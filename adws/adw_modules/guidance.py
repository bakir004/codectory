"""Project guide loading and prompt injection for every CODECTORY agent call.

Guides are repository-owned Markdown instructions for how work is done. They
are loaded once per Run, written into the shared handoff directory, and added
to every agent prompt by agents.execute(). The engineer's request always wins
when it conflicts with a guide.
"""

from __future__ import annotations

from pathlib import Path

from . import quality


def load(run) -> str:
    """Validate every configured guide set and return its immutable prompt packet."""
    config = quality.load_projects(run)
    root = Path(run.repo_root).resolve()
    configured = {project.name: project for project in config.projects}
    unknown = sorted(set(run.project_scope) - configured.keys())
    if unknown:
        raise RuntimeError(
            f"CODECTORY_PROJECTS names unknown project(s): {', '.join(unknown)}; "
            f"configured: {', '.join(sorted(configured))}")
    projects = [configured[name] for name in run.project_scope]
    paths: list[str] = []
    sections: list[str] = [
        "## Project guides (factory-provided)",
        "These Markdown guides define the repository's architecture, style, testing, "
        "and documentation rules. Follow every applicable rule. If a guide conflicts "
        "with the engineer's request, the engineer's request wins; state that override "
        "explicitly in your report rather than silently ignoring the guide.",
    ]

    for project in projects:
        guide_dir = (root / project.guides).resolve()
        if not guide_dir.is_dir():
            raise RuntimeError(
                f"project {project.name!r} guide directory is required but missing: "
                f"{project.guides}")
        index = guide_dir / "README.md"
        if not index.is_file():
            raise RuntimeError(
                f"project {project.name!r} guides require an index: "
                f"{index.relative_to(root)}")
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
    run.project_guides_scope = tuple(project.name for project in projects)
    packet = "\n".join(sections).rstrip() + "\n"
    (run.context_handoff_dir / "project_guides.md").write_text(packet)
    return packet
