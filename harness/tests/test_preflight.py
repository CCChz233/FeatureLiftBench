from __future__ import annotations

import json
import tempfile
import unittest
import urllib.error
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

    def test_placeholder_api_key_rejects_common_placeholders(self) -> None:
        self.assertTrue(
            preflight._is_placeholder_api_key(
                "你的key",
                "https://api.deepseek.com/v1",
            )
        )
        self.assertTrue(
            preflight._is_placeholder_api_key(
                "sk-...",
                "https://api.deepseek.com/v1",
            )
        )

    def test_placeholder_api_key_allows_local_vllm_dummy_key(self) -> None:
        self.assertFalse(
            preflight._is_placeholder_api_key(
                "sk-dummy",
                "http://127.0.0.1:8008/v1",
            )
        )

    def test_local_vllm_requires_host_network_for_docker_agent(self) -> None:
        with mock.patch.dict("os.environ", {}, clear=True):
            message = preflight._check_agent_docker_network_for_api_base(
                "http://127.0.0.1:8008/v1"
            )
        self.assertIsNotNone(message)

        with mock.patch.dict(
            "os.environ",
            {"FEATURELIFTBENCH_AGENT_DOCKER_NETWORK": "host"},
            clear=True,
        ):
            message = preflight._check_agent_docker_network_for_api_base(
                "http://127.0.0.1:8008/v1"
            )
        self.assertIsNone(message)

    def test_llm_health_check_success(self) -> None:
        with mock.patch.object(
            preflight.urllib.request,
            "urlopen",
            return_value=_FakeHTTPResponse(200),
        ) as urlopen_mock:
            error = preflight._llm_health_check(
                api_base="https://api.example.test/v1",
                api_key="sk-real",
                model="openai/test",
            )
        self.assertIsNone(error)
        request = urlopen_mock.call_args.args[0]
        body = json.loads(request.data.decode("utf-8"))
        self.assertEqual(body["model"], "openai/test")

    def test_llm_health_check_normalizes_deepseek_model(self) -> None:
        captured: dict[str, str] = {}

        def _capture_request(request: object, **_kwargs: object) -> _FakeHTTPResponse:
            body = json.loads(getattr(request, "data").decode("utf-8"))
            captured["model"] = body["model"]
            return _FakeHTTPResponse(200)

        with mock.patch.object(
            preflight.urllib.request,
            "urlopen",
            side_effect=_capture_request,
        ):
            error = preflight._llm_health_check(
                api_base="https://api.deepseek.com/v1",
                api_key="sk-real",
                model="deepseek/deepseek-v4-flash",
            )
        self.assertIsNone(error)
        self.assertEqual(captured["model"], "deepseek-v4-flash")

    def test_llm_health_check_reports_http_error(self) -> None:
        error_body = b'{"error":{"message":"bad model"}}'
        with mock.patch.object(
            preflight.urllib.request,
            "urlopen",
            side_effect=urllib.error.HTTPError(
                url="https://api.example.test/v1/chat/completions",
                code=400,
                msg="Bad Request",
                hdrs={},
                fp=_BytesReader(error_body),
            ),
        ):
            error = preflight._llm_health_check(
                api_base="https://api.example.test/v1",
                api_key="sk-real",
                model="bad/model",
            )
        self.assertIsNotNone(error)
        self.assertIn("HTTP 400", error or "")
        self.assertIn("bad model", error or "")


class _FakeHTTPResponse:
    def __init__(self, status: int) -> None:
        self.status = status

    def __enter__(self) -> "_FakeHTTPResponse":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None

    def read(self) -> bytes:
        return b"{}"


class _BytesReader:
    def __init__(self, data: bytes) -> None:
        self._data = data

    def read(self, *_args: object) -> bytes:
        return self._data

    def close(self) -> None:
        return None


if __name__ == "__main__":
    unittest.main()
