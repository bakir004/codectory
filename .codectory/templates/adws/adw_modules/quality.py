"""Project-aware deterministic quality checks configured by ``projects.yaml``.

Commands are data, not Python: each project declares argv, operation, and timeout
in the repository's projects file.  The runner selects projects from the pinned
run baseline, executes every selected check, and returns all failures together.
"""

from __future__ import annotations

import os
import shlex
import subprocess
import time
from pathlib import Path, PurePosixPath
import yaml
from pydantic import ValidationError

from .data_types import (EventRecord, ProjectConfig, ProjectsConfig,
                         QualityCheckResult, QualityCheckSpec, QualityOperation,
                         QualityResult, QualityScope, VerifyOutput)
from .utils import now_iso, operator_env

TAIL_CHARS = 4_000


def _inside(root: Path, child: Path) -> bool:
    try:
        child.relative_to(root)
        return True
    except ValueError:
        return False


def _config_path(run, config_path: str | Path | None = None) -> Path:
    """Find projects.yaml from an explicit path, repo root, or agent config dir."""
    root = Path(run.repo_root).resolve()
    if config_path is not None:
        path = Path(config_path)
        return (root / path).resolve() if not path.is_absolute() else path.resolve()

    candidates = [root / "projects.yaml"]
    configured = getattr(run.cfg, "config_path", "")
    if configured:
        candidates.append(Path(configured).resolve().parent / "projects.yaml")
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    looked = ", ".join(str(path) for path in candidates)
    raise RuntimeError(f"projects.yaml not found (looked in: {looked})")


def load_projects(run, config_path: str | Path | None = None) -> ProjectsConfig:
    """Load and validate project/check declarations with actionable errors."""
    path = _config_path(run, config_path)
    try:
        raw = yaml.safe_load(path.read_text()) or {}
    except (OSError, yaml.YAMLError) as error:
        raise RuntimeError(f"cannot load projects config {path}: {error}") from error
    if not isinstance(raw, dict) or "projects" not in raw:
        raise RuntimeError(f"invalid projects config {path}: top-level 'projects' is required")

    declarations = raw["projects"]
    normalized: list[dict] = []
    if isinstance(declarations, dict):
        for name, value in declarations.items():
            if not isinstance(value, dict):
                raise RuntimeError(
                    f"invalid projects config {path}: project {name!r} must be a mapping")
            normalized.append({**value, "name": name})
    elif isinstance(declarations, list):
        normalized = declarations
    else:
        raise RuntimeError(
            f"invalid projects config {path}: 'projects' must be a mapping or list")

    try:
        config = ProjectsConfig(**{**raw, "projects": normalized})
    except ValidationError as error:
        raise RuntimeError(f"invalid projects config {path}:\n{error}") from error

    root = Path(run.repo_root).resolve()
    for project in config.projects:
        project_dir = (root / project.path).resolve()
        if not _inside(root, project_dir):
            # Model validation already rejects '..'; retain a filesystem-level
            # guard for symlinks that resolve outside the repository.
            raise RuntimeError(
                f"invalid projects config {path}: project {project.name!r} path "
                f"{project.path!r} resolves outside repository root {root}")
        guides_dir = (root / project.guides).resolve()
        if not _inside(root, guides_dir):
            raise RuntimeError(
                f"invalid projects config {path}: project {project.name!r} guides "
                f"path {project.guides!r} resolves outside repository root {root}")
    return config


def _git_paths(root: Path, *args: str) -> list[str]:
    completed = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=False)
    if completed.returncode != 0:
        message = completed.stderr.decode("utf-8", "replace").strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {message}")
    return [part.decode("utf-8", "surrogateescape")
            for part in completed.stdout.split(b"\0") if part]


def changed_files(run) -> list[str]:
    """Tracked baseline changes plus untracked, gitignored files excluded."""
    root = Path(run.repo_root).resolve()
    baseline = getattr(run, "baseline_commit", "")
    if not baseline:
        raise RuntimeError(
            "changed-scope quality requires run.baseline_commit to be pinned at run start")
    tracked = _git_paths(root, "diff", "--no-renames", "--name-only", "-z", baseline, "--")
    untracked = _git_paths(root, "ls-files", "--others", "--exclude-standard", "-z", "--")
    return sorted(dict.fromkeys(_normalize_git_path(path) for path in tracked + untracked))


def _normalize_git_path(path: str) -> str:
    normalized = PurePosixPath(path.replace("\\", "/"))
    if normalized.is_absolute() or ".." in normalized.parts:
        raise RuntimeError(f"git returned unsafe repository path: {path!r}")
    return normalized.as_posix().removeprefix("./")


def path_is_in_project(file_path: str, project_path: str) -> bool:
    """Component-aware matching: ``app`` never matches ``application``."""
    file = PurePosixPath(_normalize_git_path(file_path))
    project = PurePosixPath(project_path)
    if project.as_posix() == ".":
        return True
    try:
        file.relative_to(project)
        return True
    except ValueError:
        return False


def detect_changed_projects(
    run, projects: ProjectsConfig | None = None,
) -> tuple[dict[str, list[str]], list[str]]:
    """Return project -> matching files and the complete changed-file set."""
    projects = projects or load_projects(run)
    files = changed_files(run)
    matches = {
        project.name: [path for path in files if path_is_in_project(path, project.path)]
        for project in projects.projects
    }
    return {name: paths for name, paths in matches.items() if paths}, files


def _safe_directory(root: Path, *parts: str) -> Path:
    """Create artifact directories without following attacker-controlled symlinks."""
    lexical_root = Path(root)
    if lexical_root.is_symlink():
        raise RuntimeError(f"quality artifact root must not be a symlink: {lexical_root}")
    lexical_root.mkdir(parents=True, exist_ok=True)
    resolved_root = lexical_root.resolve()
    current = resolved_root
    for part in parts:
        candidate = current / part
        if candidate.is_symlink():
            raise RuntimeError(f"quality artifact path contains a symlink: {candidate}")
        if candidate.exists() and not candidate.is_dir():
            raise RuntimeError(f"quality artifact path is not a directory: {candidate}")
        candidate.mkdir(exist_ok=True)
        resolved = candidate.resolve()
        if not _inside(resolved_root, resolved):
            raise RuntimeError(
                f"quality artifact path resolves outside context handoff: {candidate}")
        current = resolved
    return current


def _check_dir(run, project: str, check: str) -> Path:
    """Allocate a unique invocation directory under project/check hierarchy."""
    check_root = _safe_directory(
        Path(run.context_handoff_dir), "quality", project, check)
    for number in range(1, 100_000):
        invocation = check_root / f"{number:03d}"
        if invocation.is_symlink():
            raise RuntimeError(f"quality artifact path contains a symlink: {invocation}")
        try:
            invocation.mkdir()
        except FileExistsError:
            if not invocation.is_dir():
                raise RuntimeError(
                    f"quality artifact path is not a directory: {invocation}")
            continue
        return invocation
    raise RuntimeError(f"quality artifact invocation limit reached: {check_root}")


def _write_log(path: Path, content: str, artifact_root: Path) -> None:
    """Create one log through a no-follow directory handle inside the handoff."""
    root = Path(artifact_root).resolve()
    parent = path.parent
    if parent.is_symlink() or not _inside(root, parent.resolve()):
        raise RuntimeError(f"quality log parent escapes context handoff: {parent}")
    directory_flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        directory_flags |= os.O_DIRECTORY
    if hasattr(os, "O_NOFOLLOW"):
        directory_flags |= os.O_NOFOLLOW
    file_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        file_flags |= os.O_NOFOLLOW
    try:
        directory_fd = os.open(parent, directory_flags)
        try:
            fd = os.open(path.name, file_flags, 0o600, dir_fd=directory_fd)
        finally:
            os.close(directory_fd)
    except OSError as error:
        raise RuntimeError(f"cannot safely create quality log {path}: {error}") from error
    with os.fdopen(fd, "w", encoding="utf-8", errors="replace") as handle:
        handle.write(content)


def _text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    return value.decode("utf-8", "replace") if isinstance(value, bytes) else value


def _run(spec: QualityCheckSpec, run) -> QualityCheckResult:
    phase = run.phases[-1]
    output_artifact = _check_dir(run, spec.project, spec.name) / "command.log"
    command = shlex.join(spec.argv)
    project_dir = (Path(run.repo_root) / spec.project_path).resolve()

    run.console.note(f"quality {spec.project}/{spec.name}: {command}")
    started_at = now_iso()
    clock = time.monotonic()
    stdout = ""
    stderr = ""
    try:
        completed = subprocess.run(
            spec.argv,
            cwd=project_dir,
            env=operator_env(),
            capture_output=True,
            text=False,
            timeout=spec.timeout_seconds,
        )
        returncode = completed.returncode
        stdout = _text(completed.stdout)
        stderr = _text(completed.stderr)
    except subprocess.TimeoutExpired as error:
        returncode = 124
        stdout = _text(error.stdout)
        stderr = _text(error.stderr) + f"\nTimed out after {spec.timeout_seconds}s."
    except OSError as error:
        returncode = 127
        stderr = str(error)

    duration = time.monotonic() - clock
    _write_log(
        output_artifact,
        f"project: {spec.project}\nproject_path: {spec.project_path}\n"
        f"changed_files: {len(spec.changed_files)}\n$ {command}\n"
        f"exit: {returncode}\nduration_seconds: {duration:.3f}\n"
        f"\n--- stdout ---\n{stdout}\n--- stderr ---\n{stderr}\n",
        Path(run.context_handoff_dir))
    passed = returncode == 0
    payload = {
        "project": spec.project,
        "project_path": spec.project_path,
        "changed_files": spec.changed_files,
        "check": spec.name,
        "area": spec.area,
        "operation": spec.operation,
        "command": command,
        "returncode": returncode,
        "passed": passed,
        "output_artifact": str(output_artifact),
    }
    run.tracer.event(EventRecord(
        adw_id=run.adw_id,
        phase_id=phase.phase_id,
        type="tool_call",
        name=f"quality:{spec.project}:{spec.name}",
        payload=payload,
        started_at=started_at,
        ended_at=now_iso(),
    ))
    run.console.note(
        f"quality {spec.project}/{spec.name}: {'passed' if passed else 'failed'} "
        f"(exit {returncode}, {duration:.1f}s)")
    return QualityCheckResult(
        project=spec.project,
        project_path=spec.project_path,
        changed_files=spec.changed_files,
        name=spec.name,
        area=spec.area,
        operation=spec.operation,
        command=command,
        returncode=returncode,
        passed=passed,
        duration_seconds=duration,
        output_artifact=str(output_artifact),
        output_tail=(stdout + stderr)[-TAIL_CHARS:],
    )


def _execute(
    run,
    scope: QualityScope,
    operations: set[QualityOperation] | None,
) -> QualityResult:
    if scope not in ("changed", "all"):
        raise ValueError("quality scope must be 'changed' or 'all'")
    config = load_projects(run)
    if scope == "changed":
        selected_files, all_changed_files = detect_changed_projects(run, config)
        selected = [p for p in config.projects if p.name in selected_files]
    else:
        all_changed_files = changed_files(run) if getattr(run, "baseline_commit", "") else []
        selected_files = {
            project.name: [path for path in all_changed_files
                           if path_is_in_project(path, project.path)]
            for project in config.projects
        }
        selected = config.projects

    specs = [
        QualityCheckSpec(
            project=project.name,
            project_path=project.path,
            changed_files=selected_files.get(project.name, []),
            name=check.name,
            area=check.area,
            operation=check.operation,
            argv=list(check.command),
            timeout_seconds=check.timeout_seconds,
        )
        for project in selected
        for check in project.checks
        if operations is None or check.operation in operations
    ]
    checks = [_run(spec, run) for spec in specs]
    failures = [
        f"{check.project}/{check.name}: `{check.command}` exited {check.returncode}\n"
        f"{check.output_tail}".rstrip()
        for check in checks if not check.passed
    ]
    changed_projects = [project.name for project in config.projects
                        if selected_files.get(project.name)]
    if scope == "changed" and not selected:
        summary = "No configured projects changed; no quality checks were run."
    elif not specs:
        kind = "test" if operations == {"test"} else "quality"
        summary = f"No configured {kind} checks matched {scope} scope."
    else:
        summary = (f"{len(checks) - len(failures)}/{len(checks)} configured check(s) passed "
                   f"across {len(selected)} project(s).")
    return QualityResult(
        passed=not failures,
        scope=scope,
        summary=summary,
        changed_projects=changed_projects,
        changed_files=all_changed_files,
        checks=checks,
        failures=failures,
        artifacts=[check.output_artifact for check in checks],
    )


def run_checks(run, scope: QualityScope = "changed") -> QualityResult:
    """Run every configured check for changed or all projects."""
    return _execute(run, scope, operations=None)


def run_tests(run, scope: QualityScope = "changed") -> QualityResult:
    """Run only checks whose projects.yaml operation is ``test``."""
    return _execute(run, scope, operations={"test"})


def run_quality(run, scope: QualityScope = "changed") -> QualityResult:
    """Compatibility alias for workflows that previously called run_quality."""
    return run_checks(run, scope=scope)


def as_envelope(result: QualityResult, what: str) -> VerifyOutput:
    """Keep deterministic failures compatible with builder repair loops."""
    return VerifyOutput(
        status="success" if result.passed else "fail",
        summary=(result.summary or
                 (f"{what}: all {len(result.checks)} check(s) passed" if result.passed
                  else f"{what}: {len(result.failures)} of {len(result.checks)} check(s) failed")),
        artifacts=result.artifacts,
        notes_for_next_agent=("" if result.passed else
                              "Fix every failure below. The output is verbatim from the "
                              "command — trust it over any summary."),
        passed=result.passed,
        failures=result.failures,
    )
