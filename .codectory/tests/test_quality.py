from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import yaml

TEMPLATES = Path(__file__).resolve().parents[1] / "templates" / "adws"
sys.path.insert(0, str(TEMPLATES))

from adw_modules import quality  # noqa: E402


class _Tracer:
    def __init__(self):
        self.events = []

    def event(self, record):
        self.events.append(record)


class _Console:
    def __init__(self):
        self.notes = []

    def note(self, message):
        self.notes.append(message)


class _Run:
    def __init__(self, root: Path, baseline: str):
        self.repo_root = root
        self.baseline_commit = baseline
        self.context_handoff_dir = root / ".handoff"
        self.context_handoff_dir.mkdir(exist_ok=True)
        self.cfg = SimpleNamespace(config_path="")
        self.adw_id = "test-run"
        self.phases = [SimpleNamespace(phase_id="phase-1")]
        self.tracer = _Tracer()
        self.console = _Console()


class QualityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.email", "quality@example.test")
        self.git("config", "user.name", "Quality Test")
        (self.root / "app").mkdir()
        (self.root / "application").mkdir()
        (self.root / "other").mkdir()
        (self.root / "app" / "tracked.txt").write_text("before")
        (self.root / "application" / "tracked.txt").write_text("before")
        self.git("add", ".")
        self.git("commit", "-qm", "baseline")
        self.baseline = self.git("rev-parse", "HEAD").strip()

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(self.root), *args], capture_output=True, text=True, check=True)
        return result.stdout

    def configure(self, projects: dict) -> None:
        (self.root / "projects.yaml").write_text(yaml.safe_dump({"projects": projects}))

    def make_run(self) -> _Run:
        return _Run(self.root, self.baseline)

    def test_changed_projects_include_tracked_and_untracked_without_prefix_bug(self):
        self.configure({"app": {"path": "app", "guides": "guides", "checks": [{
            "name": "detect-only", "area": "backend", "operation": "build",
            "command": [sys.executable, "-c", "raise SystemExit(0)"],
        }]}})
        (self.root / "app" / "tracked.txt").write_text("after")
        (self.root / "app" / "new.txt").write_text("new")
        (self.root / "application" / "new.txt").write_text("not app")

        projects, files = quality.detect_changed_projects(self.make_run())

        self.assertEqual(projects, {"app": ["app/new.txt", "app/tracked.txt"]})
        self.assertIn("application/new.txt", files)
        self.assertFalse(quality.path_is_in_project("application/x.py", "app"))
        self.assertTrue(quality.path_is_in_project("app/x.py", "app"))

    def test_command_runs_from_project_directory_and_records_payload(self):
        command = [
            sys.executable,
            "-c",
            "from pathlib import Path; Path('cwd.txt').write_text(Path.cwd().name)",
        ]
        self.configure({
            "app": {"path": "app", "guides": "guides", "checks": [{
                "name": "cwd", "area": "backend", "operation": "test",
                "command": command, "timeout_seconds": 10,
            }]},
        })

        run = self.make_run()
        result = quality.run_tests(run, scope="all")

        self.assertTrue(result.passed)
        self.assertEqual((self.root / "app" / "cwd.txt").read_text(), "app")
        self.assertEqual(result.checks[0].project, "app")
        self.assertTrue(Path(result.checks[0].output_artifact).is_file())
        payload = run.tracer.events[0].payload
        self.assertEqual(payload["project"], "app")
        self.assertEqual(payload["operation"], "test")
        self.assertIn("changed_files", payload)

    def test_empty_changed_scope_is_successful(self):
        self.configure({"app": {"path": "app", "guides": "guides", "checks": [{
            "name": "never", "area": "backend", "operation": "build",
            "command": [sys.executable, "-c", "raise SystemExit(1)"],
        }]}})

        result = quality.run_checks(self.make_run(), scope="changed")

        self.assertTrue(result.passed)
        self.assertEqual(result.checks, [])
        self.assertIn("No configured projects changed", result.summary)

    def test_multiple_failures_are_aggregated_and_later_checks_run(self):
        marker = self.root / "app" / "last-ran"
        self.configure({"app": {"path": "app", "guides": "guides", "checks": [
            {"name": "first", "area": "backend", "operation": "lint",
             "command": [sys.executable, "-c", "raise SystemExit(3)"]},
            {"name": "second", "area": "backend", "operation": "typecheck",
             "command": [sys.executable, "-c", "raise SystemExit(4)"]},
            {"name": "last", "area": "backend", "operation": "build",
             "command": [sys.executable, "-c", "from pathlib import Path; Path('last-ran').touch()"]},
        ]}})

        run = self.make_run()
        result = quality.run_checks(run, scope="all")

        self.assertFalse(result.passed)
        self.assertEqual(len(result.checks), 3)
        self.assertEqual(len(result.failures), 2)
        self.assertTrue(marker.exists())
        self.assertEqual(len(run.tracer.events), 3)

    def test_malformed_check_has_clear_project_context(self):
        self.configure({"app": {"path": "app", "checks": [{
            "name": "bad", "area": "backend", "operation": "deploy", "command": "echo bad"
        }]}})
        with self.assertRaisesRegex(RuntimeError, "invalid projects config"):
            quality.load_projects(self.make_run())

    def test_unknown_fields_and_empty_checks_are_rejected(self):
        valid = {"name": "ok", "area": "backend", "operation": "build",
                 "command": [sys.executable, "-c", "pass"]}
        malformed = [
            {"projects": {"app": {"path": "app", "checks": [valid], "typo": True}}},
            {"projects": {"app": {"path": "app", "checks": [{**valid, "typo": True}]}}},
            {"projects": {"app": {"path": "app", "checks": []}}},
            {"projects": {"app": {"path": "app", "checks": [
                {**valid, "command": ["   "]}]}}},
            {"projects": {}, "typo": True},
        ]
        for raw in malformed:
            with self.subTest(raw=raw):
                (self.root / "projects.yaml").write_text(yaml.safe_dump(raw))
                with self.assertRaisesRegex(RuntimeError, "invalid projects config"):
                    quality.load_projects(self.make_run())

    def test_resolved_guides_path_cannot_escape_repository(self):
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        (self.root / "guides-link").symlink_to(Path(outside.name), target_is_directory=True)
        self.configure({"app": {"path": "app", "guides": "guides-link", "checks": [{
            "name": "ok", "area": "backend", "operation": "build",
            "command": [sys.executable, "-c", "pass"],
        }]}})
        with self.assertRaisesRegex(RuntimeError, "guides path.*outside"):
            quality.load_projects(self.make_run())

    def test_non_utf8_output_is_captured_and_does_not_abort_aggregation(self):
        marker = self.root / "app" / "decoded-next"
        self.configure({"app": {"path": "app", "checks": [
            {"name": "binary", "area": "backend", "operation": "lint",
             "command": [sys.executable, "-c",
                         "import os; os.write(1, b'\\xff'); raise SystemExit(2)"]},
            {"name": "next", "area": "backend", "operation": "build",
             "command": [sys.executable, "-c",
                         "from pathlib import Path; Path('decoded-next').touch()"]},
        ]}})
        result = quality.run_checks(self.make_run(), scope="all")
        self.assertFalse(result.passed)
        self.assertEqual(len(result.checks), 2)
        self.assertIn("\ufffd", result.checks[0].output_tail)
        self.assertTrue(marker.exists())

    def test_repeated_checks_get_distinct_logs(self):
        self.configure({"app": {"path": "app", "checks": [{
            "name": "repeat", "area": "backend", "operation": "build",
            "command": [sys.executable, "-c", "print('ok')"],
        }]}})
        run = self.make_run()
        first = quality.run_checks(run, scope="all")
        second = quality.run_checks(run, scope="all")
        first_log = Path(first.checks[0].output_artifact)
        second_log = Path(second.checks[0].output_artifact)
        self.assertNotEqual(first_log, second_log)
        self.assertEqual(first_log.parts[-5:-2], ("quality", "app", "repeat"))
        self.assertTrue(first_log.is_file())
        self.assertTrue(second_log.is_file())

    def test_artifact_directory_symlink_is_rejected(self):
        self.configure({"app": {"path": "app", "checks": [{
            "name": "safe", "area": "backend", "operation": "build",
            "command": [sys.executable, "-c", "pass"],
        }]}})
        run = self.make_run()
        (run.context_handoff_dir / "quality").symlink_to(
            self.root / "other", target_is_directory=True)
        with self.assertRaisesRegex(RuntimeError, "artifact path contains a symlink"):
            quality.run_checks(run, scope="all")
        self.assertEqual(list((self.root / "other").iterdir()), [])


class WorkflowQualityLoopTests(unittest.TestCase):
    def test_every_repair_loop_has_a_final_quality_rerun(self):
        for name in ("adw_build_test.py", "adw_plan_build_test.py",
                     "adw_plan_build_test_quality.py"):
            source = (TEMPLATES / name).read_text()
            with self.subTest(workflow=name):
                self.assertIn("range(1, MAX_FIX_LOOPS + 2)", source)
                self.assertIn("i > MAX_FIX_LOOPS", source)

    def test_simple_sdlc_repairs_post_review_quality_failures(self):
        source = (TEMPLATES / "adw_simple_sdlc.py").read_text()
        self.assertIn("range(1, MAX_FIX_LOOPS + 2)", source)
        self.assertIn('repair_quality("review_quality", build)', source)


if __name__ == "__main__":
    unittest.main()
