from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import sys

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "harness"))
sys.path.insert(0, str(_REPO_ROOT / "harness" / "scripts"))

import preflight  # noqa: E402


class PreflightTests(unittest.TestCase):
    def test_bootstrap_creates_agent_config_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_dir = root / "harness" / "config"
            config_dir.mkdir(parents=True)
            example = config_dir / "agents.example.toml"
            example.write_text('profile = "default"\n\n[profiles.default]\nmodel = "openai/test"\n', encoding="utf-8")

            with mock.patch.object(preflight, "_REPO_ROOT", root), mock.patch.object(
                preflight, "DEFAULT_AGENT_CONFIG", config_dir / "agents.toml"
            ), mock.patch.object(
                preflight, "DEFAULT_AGENT_CONFIG_EXAMPLE", example
            ):
                message = preflight._ensure_agent_config(bootstrap=True)

            self.assertIsNone(message)
            self.assertTrue((config_dir / "agents.toml").is_file())

    def test_resolve_mini_bin_uses_configured_absolute_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mini_path = Path(tmp) / "mini"
            mini_path.write_text("#!/bin/sh\n", encoding="utf-8")
            mini_path.chmod(0o755)
            config_dir = Path(tmp) / "harness" / "config"
            config_dir.mkdir(parents=True)
            agents = config_dir / "agents.toml"
            agents.write_text(
                '[profiles.deepseek_v4_pro]\n'
                f'agent_bin = "{mini_path}"\n',
                encoding="utf-8",
            )

            with mock.patch.object(preflight, "DEFAULT_AGENT_CONFIG", agents):
                resolved = preflight._resolve_mini_bin(
                    mini_bin_arg="",
                    profile_name="deepseek_v4_pro",
                )

            self.assertEqual(resolved, str(mini_path))


if __name__ == "__main__":
    unittest.main()
