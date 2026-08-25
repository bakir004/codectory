from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

TEMPLATES = Path(__file__).resolve().parents[1] / "templates" / "adws"
sys.path.insert(0, str(TEMPLATES))

from adw_modules import guidance  # noqa: E402


class GuidanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.handoff = self.root / ".handoff"
        self.handoff.mkdir()
        self.run = SimpleNamespace(
            repo_root=self.root,
            context_handoff_dir=self.handoff,
            cfg=SimpleNamespace(config_path=""),
        )

    def tearDown(self):
        self.temp.cleanup()

    def configure(self, guides: str = "guides/app"):
        (self.root / "projects.yaml").write_text(
            "projects:\n"
            "  app:\n"
            "    path: app\n"
            f"    guides: {guides}\n"
            "    checks:\n"
            "      - name: check\n"
            "        area: app\n"
            "        operation: test\n"
            "        command: [python, -c, 'pass']\n")

    def test_loads_every_markdown_guide_into_handoff_packet(self):
        (self.root / "app").mkdir()
        guide_dir = self.root / "guides" / "app"
        guide_dir.mkdir(parents=True)
        (guide_dir / "README.md").write_text("# App rules\n")
        (guide_dir / "style.md").write_text("Use four spaces.\n")
        self.configure()

        packet = guidance.load(self.run)

        self.assertIn("Project: app (app)", packet)
        self.assertIn("Use four spaces.", packet)
        self.assertEqual(packet, (self.handoff / "project_guides.md").read_text())

    def test_requires_a_markdown_readme_index(self):
        (self.root / "app").mkdir()
        (self.root / "guides" / "app").mkdir(parents=True)
        self.configure()

        with self.assertRaisesRegex(RuntimeError, "require an index"):
            guidance.load(self.run)


if __name__ == "__main__":
    unittest.main()
