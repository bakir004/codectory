"""Strict, opt-in workflow continuation checkpoints.

Successful phases are immutable.  A continued invocation walks the original
workflow from phase one, restores successful agent envelopes, and re-executes
the first incomplete phase.  The manifest prevents an adw_id from being
silently continued by a different workflow/request/config/project scope.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from .utils import now_iso

MANIFEST = "continuation.json"


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def identity(*, workflow: str, prompt: str, projects: tuple[str, ...], config_path: str) -> dict[str, Any]:
    path = Path(config_path)
    config_bytes = path.read_bytes() if path.is_file() else config_path.encode()
    agents = path.with_name("agents.yaml")
    if agents.is_file():
        config_bytes += b"\0" + agents.read_bytes()
    return {
        "workflow": workflow,
        "prompt_sha256": _hash(prompt),
        "projects": list(projects),
        "config_sha256": hashlib.sha256(config_bytes).hexdigest(),
    }


def load_or_create(session_dir: Path, expected: dict[str, Any], continuing: bool) -> dict[str, Any]:
    path = session_dir / MANIFEST
    if continuing:
        if not path.is_file():
            raise RuntimeError("cannot continue this session: no continuation checkpoint exists")
        manifest = json.loads(path.read_text())
        actual = manifest.get("identity", {})
        mismatches = [key for key, value in expected.items() if actual.get(key) != value]
        if mismatches:
            raise RuntimeError("cannot continue an incompatible session; changed: " + ", ".join(mismatches))
        return manifest
    if path.exists():
        return json.loads(path.read_text())
    manifest = {"version": 1, "identity": expected, "created_at": now_iso()}
    atomic_write(path, manifest)
    return manifest


def atomic_write(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True))
    temporary.replace(path)
