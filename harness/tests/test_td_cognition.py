"""Tests for TD-Cognition two-phase protocol."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from featureliftbench.ablation import AblationOptions
from featureliftbench.ablation import resolve_ablation_options
from featureliftbench.agent_runner import prepare_agent_workspace
from featureliftbench.metadata import load_metadata
from featureliftbench.td_cognition import evaluate_phase1_artifacts
from featureliftbench.td_cognition import prepare_phase2_workspace
from featureliftbench.td_cognition import validate_cognition_scaffold


class TdCognitionAblationTests(unittest.TestCase):
    def test_arm_name(self) -> None:
        self.assertEqual(AblationOptions(td_cognition=True).ablation_arm, "td_cognition")

    def test_resolve_from_profile(self) -> None:
        options = resolve_ablation_options(profile={"td_cognition": True})
        self.assertTrue(options.td_cognition)
        self.assertEqual(options.ablation_arm, "td_cognition")


class TdCognitionTwoPhaseWorkspaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task_dir = (
            Path(__file__).resolve().parents[2]
            / "benchmark"
            / "sanity"
            / "iniconfig__parse_config__001"
        )
        self.metadata = load_metadata(self.task_dir).data

    def test_phase1_keeps_writable_submission_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "ws"
            prepare_agent_workspace(
                self.task_dir,
                workspace,
                self.metadata,
                ablation=AblationOptions(td_cognition=True),
            )
            submission = workspace / "submission"
            self.assertTrue(submission.is_dir())
            self.assertTrue((workspace / "COGNITION.md").is_file())
            self.assertTrue((workspace / "probes").is_dir())
            task = (workspace / "TASK.md").read_text(encoding="utf-8")
            self.assertIn("Phase 1", task)
            self.assertIn("Do not", task)

            blocked = evaluate_phase1_artifacts(workspace, run_pytest=False)
            self.assertFalse(blocked.ok)

            (workspace / "COGNITION.md").write_text(
                "# Cognition\n\n"
                "## Critical Use Cases\n\n"
                "1. Parse empty config returns empty mapping\n"
                "2. Duplicate keys follow documented precedence\n"
                "3. Invalid syntax raises a clear error\n\n"
                "## Required Surface\n\n"
                "- parse API\n\n"
                "## Support Set Hypothesis\n\n"
                "- iniconfig core modules\n\n"
                "## Exclusions\n\n"
                "- unrelated packaging helpers\n\n"
                "## Probes\n\n"
                "- probes/test_contract_smoke.py\n",
                encoding="utf-8",
            )
            self.assertTrue(validate_cognition_scaffold(workspace).ok)
            (workspace / "probes" / "test_contract_smoke.py").write_text(
                "def test_truth() -> None:\n    assert True\n",
                encoding="utf-8",
            )
            ok = evaluate_phase1_artifacts(workspace, run_pytest=True)
            self.assertTrue(ok.ok, ok.errors)

            phase2 = prepare_phase2_workspace(
                workspace,
                (workspace / "TASK.md").read_text(encoding="utf-8"),
            )
            self.assertIn("Phase 2", phase2)
            self.assertIn("Parse empty config", phase2)
            self.assertTrue((workspace / "submission").is_dir())
            self.assertFalse(any((workspace / "submission").iterdir()))


if __name__ == "__main__":
    unittest.main()
