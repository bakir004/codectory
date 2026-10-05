"""Optional project-guide loading and prompt injection for CODECTORY agent calls.

Projects may opt into repository-owned Markdown instructions with a ``guides``
path in ``projects.yaml``. Configured guides are loaded once per Run, written
into the shared handoff directory, and added to every agent prompt. Projects
without ``guides`` run normally without guide injection.
"""

from __future__ import annotations

from pathlib import Path

from . import quality


def load(run) -> str:
    """Validate configured guide sets and return their immutable prompt packet."""
    config = quality.load_projects(run)
    root = Path(run.repo_root).resolve()
    configured = {project.name: project for project in config.projects}
    unknown = sorted(set(run.project_scope) - configured.keys())
    if unknown:
        raise RuntimeError(
            f"--projects names unknown project(s): {', '.join(unknown)}; "
            f"configured: {', '.join(sorted(configured))}")
    projects = [configured[name] for name in run.project_scope]
    paths: list[str] = []
    sections: list[str] = []

    for project in projects:
        if project.guides is None:
            continue
        guide_dir = (root / project.guides).resolve()
        if not guide_dir.is_dir():
            raise RuntimeError(
                f"project {project.name!r} configured guide directory is missing: "
                f"{project.guides}")
        files = sorted(path for path in guide_dir.rglob("*.md") if path.is_file())
        if not files:
            raise RuntimeError(f"project {project.name!r} has no Markdown guides: {project.guides}")

        sections.append(f"\n### Project: {project.name} ({project.path})")
        for path in files:
            resolved = path.resolve()
            try:
                relative = resolved.relative_to(root)
            except ValueError as error:
                raise RuntimeError(
                    f"project {project.name!r} guide escapes repository: {path}") from error
            paths.append(relative.as_posix())
            sections.append(f"\n#### {relative}\n\n{resolved.read_text()}")

    run.project_guide_paths = frozenset(paths)
    run.project_guides_scope = tuple(project.name for project in projects if project.guides is not None)
    if not sections:
        return ""

    header = [
        "## Project guides (factory-provided)",
        "These optional Markdown guides define repository conventions. Follow every "
        "applicable rule. If a guide conflicts with the engineer's request, the request "
        "wins; state that override explicitly in your report.",
    ]
    packet = "\n".join([*header, *sections]).rstrip() + "\n"
    (run.context_handoff_dir / "project_guides.md").write_text(packet)
    return packet
