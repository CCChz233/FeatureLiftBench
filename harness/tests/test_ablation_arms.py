"""Tests for test-blind Main / Public-feedback / Short-prompt ablation arms."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from featureliftbench.ablation import AblationOptions
from featureliftbench.ablation import resolve_ablation_options
from featureliftbench.agent_runner import build_task_prompt
from featureliftbench.agent_runner import prepare_agent_workspace
from featureliftbench.metadata import load_metadata
from featureliftbench.openhands_runner import OpenHandsRunnerConfig
from featureliftbench.openhands_runner import _build_openhands_prompt


class AblationOptionsTests(unittest.TestCase):
    def test_arm_names(self) -> None:
        self.assertEqual(AblationOptions().ablation_arm, "main")
        self.assertEqual(
            AblationOptions(mount_public_tests=True).ablation_arm,
            "public_feedback",
        )
        self.assertEqual(
            AblationOptions(prompt_style="short").ablation_arm,
            "short_prompt",
        )
        self.assertEqual(
            AblationOptions(mount_public_tests=True, prompt_style="short").ablation_arm,
            "public_feedback_short",
        )

    def test_cli_overrides_profile(self) -> None:
        options = resolve_ablation_options(
            profile={"mount_public_tests": True, "prompt_style": "standard"},
            mount_public_tests=False,
            prompt_style="short",
        )
        self.assertEqual(options.ablation_arm, "short_prompt")


class AblationWorkspaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task_dir = (
            Path(__file__).resolve().parents[2]
            / "benchmark"
            / "sanity"
            / "iniconfig__parse_config__001"
        )
        self.metadata = load_metadata(self.task_dir).data

    def test_main_hides_evaluator_tests_and_keeps_upstream_tests(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "ws"
            prepare_agent_workspace(
                self.task_dir,
                workspace,
                self.metadata,
                ablation=AblationOptions(),
            )
            self.assertFalse((workspace / "public_tests").exists())
            self.assertTrue((workspace / "repo" / "testing" / "test_iniconfig.py").is_file())
            prompt = (workspace / "TASK.md").read_text(encoding="utf-8")
            self.assertIn("## How to work", prompt)
            self.assertIn("## Closure Discipline", prompt)
            self.assertIn("Benchmark evaluator tests", prompt)
            self.assertNotIn("Run `pytest public_tests/`", prompt)

    def test_public_feedback_mounts_public_and_mentions_pytest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "ws"
            prepare_agent_workspace(
                self.task_dir,
                workspace,
                self.metadata,
                ablation=AblationOptions(mount_public_tests=True),
            )
            self.assertTrue((workspace / "public_tests").is_dir())
            prompt = (workspace / "TASK.md").read_text(encoding="utf-8")
            self.assertIn("Run `pytest public_tests/`", prompt)
            self.assertIn("Required Output API", prompt)

    def test_short_prompt_drops_closure_keeps_api(self) -> None:
        prompt = build_task_prompt(
            self.metadata,
            ablation=AblationOptions(prompt_style="short"),
        )
        self.assertNotIn("## Closure Discipline", prompt)
        self.assertNotIn("## Entanglement Context", prompt)
        self.assertIn("## Required Output API", prompt)
        self.assertIn("## Target Feature", prompt)
        self.assertNotIn("Run `pytest public_tests/`", prompt)
        self.assertIn("Forbidden imports", prompt)

    def test_openhands_wrapper_respects_test_blind_main(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = root / "TASK.md"
            task.write_text("# task\n", encoding="utf-8")
            config = OpenHandsRunnerConfig(
                workspace_dir=root,
                task_file=task,
                submission_dir=root / "submission",
                agent_output_dir=root / "agent",
                model="test-model",
            )
            with mock.patch.dict(
                "os.environ",
                {"FEATURELIFTBENCH_MOUNT_PUBLIC_TESTS": "0"},
                clear=False,
            ):
                text = _build_openhands_prompt(config)
            self.assertIn("not mounted", text)
            self.assertIn("upstream tests", text)
            self.assertNotIn("PYTHONPATH=submission pytest public_tests/", text)


if __name__ == "__main__":
    unittest.main()
