from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from featureliftbench.agent_adapters import AgentRunConfig
from featureliftbench.agent_config import load_agent_run_config
from featureliftbench.repo_graph.policy import MODE_ENV as REPO_GRAPH_MODE_ENV


class AgentConfigTests(unittest.TestCase):
    def test_repo_graph_profile_is_opt_in_validated_and_uses_environment_precedence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_file = root / "agents.toml"
            config_file.write_text(
                "[profiles.default]\n"
                'repo_graph_mode = "static"\n'
                'repo_graph_transport = "cli"\n'
                "repo_graph_fail_fast = true\n"
                "repo_graph_bootstrap_max_nodes = 24\n"
                "repo_graph_bootstrap_max_chars = 4096\n"
                "repo_graph_query_max_chars = 9000\n",
                encoding="utf-8",
            )
            with mock.patch.dict(os.environ, {REPO_GRAPH_MODE_ENV: "closure"}, clear=False):
                loaded = load_agent_run_config(
                    base_config=AgentRunConfig(agent="mini-swe-agent"),
                    config_path=config_file,
                )

            self.assertEqual(loaded.summary["repo_graph_mode"], "closure")
            self.assertEqual(loaded.summary["repo_graph_bootstrap_max_nodes"], 24)
            self.assertEqual(loaded.summary["repo_graph_bootstrap_max_chars"], 4096)
            self.assertEqual((loaded.run_config.env or {})[REPO_GRAPH_MODE_ENV], "closure")

    def test_repo_graph_invalid_mode_and_budget_fail_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            invalid_mode = root / "invalid-mode.toml"
            invalid_mode.write_text(
                "[profiles.default]\nrepo_graph_mode = \"magic\"\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "unknown repository graph mode"):
                load_agent_run_config(
                    base_config=AgentRunConfig(agent="mini-swe-agent"),
                    config_path=invalid_mode,
                )
            invalid_budget = root / "invalid-budget.toml"
            invalid_budget.write_text(
                "[profiles.default]\n"
                'repo_graph_mode = "static"\n'
                "repo_graph_query_max_chars = 128\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "at least 512"):
                load_agent_run_config(
                    base_config=AgentRunConfig(agent="mini-swe-agent"),
                    config_path=invalid_budget,
                )
            invalid_bootstrap = root / "invalid-bootstrap.toml"
            invalid_bootstrap.write_text(
                "[profiles.default]\n"
                'repo_graph_mode = "closure"\n'
                "repo_graph_bootstrap_max_chars = 900\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "at least 1024"):
                load_agent_run_config(
                    base_config=AgentRunConfig(agent="mini-swe-agent"),
                    config_path=invalid_bootstrap,
                )

    def test_legacy_profile_keeps_repo_graph_disabled_without_forwarded_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_file = Path(tmp) / "agents.toml"
            config_file.write_text("[profiles.default]\n", encoding="utf-8")
            loaded = load_agent_run_config(
                base_config=AgentRunConfig(agent="mini-swe-agent"),
                config_path=config_file,
            )
            self.assertEqual(loaded.summary["repo_graph_mode"], "disabled")
            self.assertNotIn(REPO_GRAPH_MODE_ENV, loaded.run_config.env or {})

    def test_openhands_token_profiles_derive_expected_thresholds(self) -> None:
        cases = (
            ("ctx64k", 65536, 57344, 28672),
            ("ctx128k", 131072, 122880, 61440),
            ("ctx256k", 262144, 253952, 126976),
        )
        with tempfile.TemporaryDirectory() as tmp:
            config_file = Path(tmp) / "agents.toml"
            tables = []
            for name, total, _, _ in cases:
                tables.append(
                    f"[profiles.{name}]\n"
                    f"context_window_tokens = {total}\n"
                    "reserved_output_tokens = 8192\n"
                    'openhands_condenser_mode = "token"\n'
                    "openhands_condenser_keep_first = 4\n"
                    "openhands_condenser_max_events = 1000000\n"
                )
            config_file.write_text("\n".join(tables), encoding="utf-8")

            for name, total, trigger, target in cases:
                loaded = load_agent_run_config(
                    base_config=AgentRunConfig(agent="openhands"),
                    config_path=config_file,
                    profile_name=name,
                )
                self.assertEqual(loaded.summary["context_window_tokens"], total)
                self.assertEqual(
                    loaded.summary["openhands_condenser_trigger_tokens"], trigger
                )
                self.assertEqual(
                    loaded.summary["openhands_condenser_target_tokens"], target
                )

    def test_openhands_token_mode_rejects_invalid_or_unknown_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            invalid_window = root / "invalid-window.toml"
            invalid_window.write_text(
                "[profiles.default]\n"
                "context_window_tokens = 8192\n"
                "reserved_output_tokens = 8192\n"
                'openhands_condenser_mode = "token"\n',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "context_window_tokens >"):
                load_agent_run_config(
                    base_config=AgentRunConfig(agent="openhands"),
                    config_path=invalid_window,
                )

            unknown_mode = root / "unknown-mode.toml"
            unknown_mode.write_text(
                "[profiles.default]\n"
                'openhands_condenser_mode = "mystery"\n',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "unknown OpenHands condenser mode"):
                load_agent_run_config(
                    base_config=AgentRunConfig(agent="openhands"),
                    config_path=unknown_mode,
                )

    def test_openhands_context_environment_precedence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env_file = root / ".env"
            config_file = root / "agents.toml"
            env_file.write_text(
                "FEATURELIFTBENCH_CONTEXT_WINDOW_TOKENS=90000\n",
                encoding="utf-8",
            )
            config_file.write_text(
                "[profiles.default]\n"
                "context_window_tokens = 65536\n"
                "reserved_output_tokens = 8192\n"
                'openhands_condenser_mode = "token"\n',
                encoding="utf-8",
            )
            with mock.patch.dict(
                os.environ,
                {"FEATURELIFTBENCH_CONTEXT_WINDOW_TOKENS": "100000"},
                clear=False,
            ):
                loaded = load_agent_run_config(
                    base_config=AgentRunConfig(
                        agent="openhands",
                        env={"FEATURELIFTBENCH_CONTEXT_WINDOW_TOKENS": "110000"},
                    ),
                    config_path=config_file,
                    env_file=env_file,
                )

            self.assertEqual(loaded.summary["context_window_tokens"], 110000)
            self.assertEqual(
                (loaded.run_config.env or {})[
                    "FEATURELIFTBENCH_CONTEXT_WINDOW_TOKENS"
                ],
                "110000",
            )

    def test_legacy_openhands_profile_does_not_enable_token_condenser(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_file = Path(tmp) / "agents.toml"
            config_file.write_text(
                "[profiles.default]\n"
                "context_window_tokens = 131072\n"
                "reserved_output_tokens = 8192\n",
                encoding="utf-8",
            )
            loaded = load_agent_run_config(
                base_config=AgentRunConfig(agent="openhands"),
                config_path=config_file,
            )
            self.assertEqual(loaded.summary["openhands_condenser_mode"], "default")
            self.assertNotIn(
                "FEATURELIFTBENCH_OPENHANDS_CONDENSER_MODE",
                loaded.run_config.env or {},
            )

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

    def test_featurelift_agent_ignores_profile_mini_agent_bin(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_file = root / "agents.toml"
            config_file.write_text(
                "[profiles.default]\n"
                'model = "deepseek/deepseek-v4-flash"\n'
                'agent_bin = "/profile/bin/mini"\n',
                encoding="utf-8",
            )

            loaded = load_agent_run_config(
                base_config=AgentRunConfig(agent="featurelift-agent"),
                config_path=config_file,
            )

            self.assertEqual(loaded.run_config.model, "deepseek/deepseek-v4-flash")
            self.assertIsNone(loaded.run_config.agent_bin)

    def test_openhands_agent_ignores_profile_mini_agent_bin(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_file = root / "agents.toml"
            config_file.write_text(
                "[profiles.default]\n"
                'model = "deepseek/deepseek-v4-flash"\n'
                'agent_bin = "/profile/bin/mini"\n',
                encoding="utf-8",
            )

            loaded = load_agent_run_config(
                base_config=AgentRunConfig(agent="openhands-agent"),
                config_path=config_file,
            )

            self.assertEqual(loaded.run_config.model, "deepseek/deepseek-v4-flash")
            self.assertIsNone(loaded.run_config.agent_bin)

    def test_openhands_profile_injects_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_file = root / "agents.toml"
            config_file.write_text(
                "[profiles.openhands_deepseek_v4_flash]\n"
                'model = "deepseek/deepseek-v4-flash"\n'
                'openhands_command = "openhands --headless -f {prompt_file}"\n',
                encoding="utf-8",
            )

            loaded = load_agent_run_config(
                base_config=AgentRunConfig(agent="openhands-agent"),
                config_path=config_file,
                profile_name="openhands_deepseek_v4_flash",
            )

            self.assertEqual(
                loaded.run_config.command,
                "openhands --headless -f {prompt_file}",
            )
            self.assertTrue(loaded.summary["openhands_command_configured"])

    def test_openhands_cli_command_overrides_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_file = root / "agents.toml"
            config_file.write_text(
                "[profiles.default]\n"
                'openhands_command = "openhands profile"\n',
                encoding="utf-8",
            )

            loaded = load_agent_run_config(
                base_config=AgentRunConfig(
                    agent="openhands-agent",
                    command="openhands cli",
                ),
                config_path=config_file,
            )

            self.assertEqual(loaded.run_config.command, "openhands cli")

    def test_nex_profile_uses_siliconflow_base_not_deepseek(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env_file = root / ".env"
            config_file = root / "agents.toml"
            env_file.write_text(
                'FEATURELIFTBENCH_API_BASE="https://api.deepseek.com/v1"\n'
                'SILICONFLOW_API_BASE="https://api.siliconflow.cn/v1"\n'
                'SILICONFLOW_API_KEY="sk-sf-test"\n',
                encoding="utf-8",
            )
            config_file.write_text(
                "[profiles.nex_n2_pro]\n"
                'model = "openai/nex-agi/Nex-N2-Pro"\n'
                'api_base_env = "SILICONFLOW_API_BASE"\n'
                'api_key_env = "SILICONFLOW_API_KEY"\n',
                encoding="utf-8",
            )

            loaded = load_agent_run_config(
                base_config=AgentRunConfig(agent="mini-swe-agent"),
                config_path=config_file,
                profile_name="nex_n2_pro",
                env_file=env_file,
            )

            self.assertEqual(loaded.run_config.model, "openai/nex-agi/Nex-N2-Pro")
            self.assertEqual(loaded.summary["api_base"], "https://api.siliconflow.cn/v1")
            self.assertTrue(loaded.summary["api_key_present"])
            env = loaded.run_config.env or {}
            self.assertEqual(env["OPENAI_BASE_URL"], "https://api.siliconflow.cn/v1")
            self.assertEqual(env["OPENAI_API_KEY"], "sk-sf-test")
            self.assertEqual(env["SILICONFLOW_API_KEY"], "sk-sf-test")
            self.assertNotEqual(env["FEATURELIFTBENCH_API_BASE"], "https://api.deepseek.com/v1")

    def test_openhands_profile_does_not_forward_unselected_env_file_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env_file = root / ".env"
            config_file = root / "agents.toml"
            env_file.write_text(
                'FEATURELIFTBENCH_API_KEY="sk-deepseek"\n'
                'FEATURELIFTBENCH_API_BASE="https://api.deepseek.com/v1"\n'
                'SILICONFLOW_API_KEY="sk-siliconflow"\n'
                'SILICONFLOW_API_BASE="https://api.siliconflow.cn/v1"\n'
                "FEATURELIFTBENCH_COMMAND_OUTPUT_LIMIT_BYTES=1024\n",
                encoding="utf-8",
            )
            config_file.write_text(
                "[profiles.openhands_deepseek_v4_flash]\n"
                'model = "deepseek/deepseek-v4-flash"\n'
                'api_key_env = "FEATURELIFTBENCH_API_KEY"\n'
                'api_base_env = "FEATURELIFTBENCH_API_BASE"\n',
                encoding="utf-8",
            )

            loaded = load_agent_run_config(
                base_config=AgentRunConfig(agent="openhands-agent"),
                config_path=config_file,
                profile_name="openhands_deepseek_v4_flash",
                env_file=env_file,
            )

            env = loaded.run_config.env or {}
            self.assertEqual(env["FEATURELIFTBENCH_API_KEY"], "sk-deepseek")
            self.assertEqual(env["OPENAI_API_KEY"], "sk-deepseek")
            self.assertEqual(env["DEEPSEEK_API_KEY"], "sk-deepseek")
            self.assertEqual(env["FEATURELIFTBENCH_API_BASE"], "https://api.deepseek.com/v1")
            self.assertEqual(env["FEATURELIFTBENCH_COMMAND_OUTPUT_LIMIT_BYTES"], "1024")
            self.assertNotIn("SILICONFLOW_API_KEY", env)
            self.assertNotIn("SILICONFLOW_API_BASE", env)
            self.assertTrue(loaded.summary["api_key_present"])
            self.assertNotIn("sk-deepseek", str(loaded.summary))

    def test_featurelift_profile_injects_runtime_flags(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_file = root / "agents.toml"
            config_file.write_text(
                "[profiles.featurelift_v4_flash]\n"
                'model = "deepseek/deepseek-v4-flash"\n'
                "featurelift_enable_llm = true\n"
                "featurelift_execute_actions = true\n"
                'featurelift_llm_phases = "closure_plan,extraction_plan,final_checklist"\n'
                "featurelift_max_repair_rounds = 2\n"
                "featurelift_tool_timeout = 120\n",
                encoding="utf-8",
            )

            loaded = load_agent_run_config(
                base_config=AgentRunConfig(agent="featurelift-agent"),
                config_path=config_file,
                profile_name="featurelift_v4_flash",
            )

            self.assertIn("--enable-llm", loaded.run_config.extra_args)
            self.assertIn("--execute-actions", loaded.run_config.extra_args)
            self.assertIn("--llm-phases", loaded.run_config.extra_args)
            self.assertIn("closure_plan,extraction_plan,final_checklist", loaded.run_config.extra_args)
            self.assertIn("--max-repair-rounds", loaded.run_config.extra_args)
            self.assertIn("2", loaded.run_config.extra_args)
            self.assertIn("--tool-timeout", loaded.run_config.extra_args)
            self.assertIn("120", loaded.run_config.extra_args)


if __name__ == "__main__":
    unittest.main()
