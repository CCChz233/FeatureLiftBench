from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from featureliftbench.agent_adapters import AgentRunConfig
from featureliftbench.agent_config import load_agent_run_config


class AgentConfigTests(unittest.TestCase):
    def test_load_agent_run_config_maps_shared_key_to_common_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env_file = root / ".env"
            config_file = root / "agents.toml"
            env_file.write_text(
                'FEATURELIFTBENCH_API_KEY="sk-test"\n'
                "FEATURELIFTBENCH_API_BASE=https://api.example.test/v1\n",
                encoding="utf-8",
            )
            config_file.write_text(
                'profile = "default"\n'
                f'env_file = "{env_file}"\n\n'
                "[profiles.default]\n"
                'model = "openai/example-model"\n'
                'agent_bin = "/opt/miniswe/bin/mini"\n'
                'cost_limit = "1.00"\n',
                encoding="utf-8",
            )

            loaded = load_agent_run_config(
                base_config=AgentRunConfig(agent="mini-swe-agent"),
                config_path=config_file,
            )

            env = loaded.run_config.env or {}
            self.assertEqual(loaded.run_config.model, "openai/example-model")
            self.assertEqual(loaded.run_config.agent_bin, "/opt/miniswe/bin/mini")
            self.assertEqual(env["FEATURELIFTBENCH_API_KEY"], "sk-test")
            self.assertEqual(env["OPENAI_API_KEY"], "sk-test")
            self.assertEqual(env["LITELLM_API_KEY"], "sk-test")
            self.assertEqual(env["OPENAI_BASE_URL"], "https://api.example.test/v1")
            self.assertEqual(env["OPENAI_API_BASE"], "https://api.example.test/v1")
            self.assertEqual(env["MSWEA_MODEL_NAME"], "openai/example-model")
            self.assertEqual(env["MSWEA_GLOBAL_COST_LIMIT"], "1.00")
            self.assertTrue(loaded.summary["api_key_present"])
            self.assertNotIn("sk-test", str(loaded.summary))

    def test_cli_model_overrides_profile_model(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_file = root / "agents.toml"
            config_file.write_text(
                "[profiles.default]\n"
                'model = "openai/profile-model"\n',
                encoding="utf-8",
            )

            loaded = load_agent_run_config(
                base_config=AgentRunConfig(
                    agent="mini-swe-agent",
                    model="openai/cli-model",
                ),
                config_path=config_file,
            )

            self.assertEqual(loaded.run_config.model, "openai/cli-model")

    def test_cli_agent_bin_overrides_profile_agent_bin(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_file = root / "agents.toml"
            config_file.write_text(
                "[profiles.default]\n"
                'agent_bin = "/profile/bin/mini"\n',
                encoding="utf-8",
            )

            loaded = load_agent_run_config(
                base_config=AgentRunConfig(
                    agent="mini-swe-agent",
                    agent_bin="/cli/bin/mini",
                ),
                config_path=config_file,
            )

            self.assertEqual(loaded.run_config.agent_bin, "/cli/bin/mini")


if __name__ == "__main__":
    unittest.main()
