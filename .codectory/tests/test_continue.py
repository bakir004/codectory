from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULES = ROOT / "adws" / "adw_modules"
sys.path.insert(0, str(ROOT / "adws"))

from adw_modules import checkpoints
from adw_modules.data_types import LaunchOptions, PlanOutput


class ContinueContractTests(unittest.TestCase):
    def test_continue_requires_id_and_nonempty_instruction(self):
        with self.assertRaisesRegex(ValueError, "requires --adw-id"):
            LaunchOptions(prompt="ask", projects="adws", config_path="x", continue_instruction="go")
        with self.assertRaisesRegex(ValueError, "non-empty"):
            LaunchOptions(prompt="ask", projects="adws", config_path="x", adw_id="abc", continue_instruction="  ")

    def test_manifest_accepts_new_instruction_but_rejects_changed_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "codectory.config.yaml"
            config.write_text("defaults: {}\n")
            expected = checkpoints.identity(workflow="adw_build", prompt="original", projects=("adws",), config_path=str(config))
            checkpoints.load_or_create(root, expected, False)
            # Continue instructions are deliberately absent from identity.
            checkpoints.load_or_create(root, expected, True)
            changed = checkpoints.identity(workflow="adw_build", prompt="different", projects=("adws",), config_path=str(config))
            with self.assertRaisesRegex(RuntimeError, "prompt_sha256"):
                checkpoints.load_or_create(root, changed, True)

    def test_clarification_contract_is_typed_and_opt_in(self):
        options = LaunchOptions(prompt="ask", projects="adws", config_path="x", clarification=True)
        self.assertTrue(options.clarification)
        report = PlanOutput(status="success", clarification_questions=["Which API version?"])
        self.assertEqual(["Which API version?"], report.clarification_questions)

    def test_every_workflow_exposes_clarification_flag(self):
        for workflow in (ROOT / "adws").glob("adw_*.py"):
            self.assertIn('parser.add_argument("--clarification"', workflow.read_text(), workflow.name)

    def test_checkpoint_write_is_parseable_and_versioned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "config.yaml"
            config.write_text("agents: []\n")
            expected = checkpoints.identity(workflow="adw_plan", prompt="ask", projects=("adws",), config_path=str(config))
            manifest = checkpoints.load_or_create(root, expected, False)
            self.assertEqual(1, manifest["version"])
            self.assertEqual(manifest, checkpoints.load_or_create(root, expected, True))


if __name__ == "__main__":
    unittest.main()
