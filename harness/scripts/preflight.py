#!/usr/bin/env python3
"""Validate local/server environment before running agent suites."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_HARNESS_ROOT = _REPO_ROOT / "harness"
if str(_HARNESS_ROOT) not in sys.path:
    sys.path.insert(0, str(_HARNESS_ROOT))

from featureliftbench.agent_config import load_agent_run_config  # noqa: E402
from featureliftbench.agent_adapters import AgentRunConfig  # noqa: E402
from featureliftbench.paths import DEFAULT_AGENT_CONFIG  # noqa: E402
from featureliftbench.paths import DEFAULT_AGENT_CONFIG_EXAMPLE  # noqa: E402


def _fail(message: str) -> int:
    print(f"preflight: {message}", file=sys.stderr)
    return 1


def _ensure_agent_config(*, bootstrap: bool) -> str | None:
    if DEFAULT_AGENT_CONFIG.is_file():
        return None
    if not DEFAULT_AGENT_CONFIG_EXAMPLE.is_file():
        return f"missing {DEFAULT_AGENT_CONFIG} and {DEFAULT_AGENT_CONFIG_EXAMPLE}"
    if not bootstrap:
        return (
            f"missing {DEFAULT_AGENT_CONFIG}; run ./setup.sh or "
            f"cp {DEFAULT_AGENT_CONFIG_EXAMPLE} {DEFAULT_AGENT_CONFIG}"
        )
    DEFAULT_AGENT_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_AGENT_CONFIG.write_text(
        DEFAULT_AGENT_CONFIG_EXAMPLE.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    print(f"preflight: created {DEFAULT_AGENT_CONFIG} from example", file=sys.stderr)
    return None


def _ensure_env_file(*, bootstrap: bool) -> str | None:
    env_path = _REPO_ROOT / ".env"
    example_path = _REPO_ROOT / ".env.example"
    if env_path.is_file():
        return None
    if not bootstrap:
        return f"missing {env_path}; copy from {example_path} and add API keys"
    if not example_path.is_file():
        return f"missing {env_path} and {example_path}"
    env_path.write_text(example_path.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"preflight: created {env_path} from example — add API keys before running", file=sys.stderr)
    return None


def _read_configured_mini_bin(profile_name: str) -> str:
    if not DEFAULT_AGENT_CONFIG.is_file():
        return ""
    try:
        import tomllib

        data = tomllib.loads(DEFAULT_AGENT_CONFIG.read_text(encoding="utf-8"))
    except Exception:
        return ""
    profiles = data.get("profiles")
    if not isinstance(profiles, dict):
        return ""
    profile = profiles.get(profile_name, {})
    if not isinstance(profile, dict):
        return ""
    agent_bin = profile.get("agent_bin")
    return agent_bin if isinstance(agent_bin, str) and agent_bin else ""


def _resolve_mini_bin(*, mini_bin_arg: str, profile_name: str) -> str:
    if mini_bin_arg:
        return mini_bin_arg
    configured = _read_configured_mini_bin(profile_name)
    if configured:
        if Path(configured).is_file() or shutil.which(configured):
            return configured
    return shutil.which("mini") or ""


def _patch_agent_bin(mini_bin: str) -> None:
    import re

    path = DEFAULT_AGENT_CONFIG
    text = path.read_text(encoding="utf-8")
    patched = re.sub(
        r'^agent_bin\s*=\s*".*"$',
        f'agent_bin = "{mini_bin}"',
        text,
        flags=re.MULTILINE,
    )
    if 'agent_bin = "' not in patched:
        patched = re.sub(
            r'^#\s*agent_bin\s*=\s*".*"$',
            f'agent_bin = "{mini_bin}"',
            patched,
            flags=re.MULTILINE,
        )
    path.write_text(patched, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="FeatureLiftBench run preflight checks")
    parser.add_argument(
        "--agent-profile",
        default="deepseek_v4_pro",
        help="profile to validate (default: deepseek_v4_pro)",
    )
    parser.add_argument(
        "--bootstrap",
        action="store_true",
        help="create agents.toml / .env from examples when missing",
    )
    parser.add_argument(
        "--mini-bin",
        default="",
        help="expected mini executable path (default: shutil.which('mini'))",
    )
    args = parser.parse_args(argv)

    if sys.version_info < (3, 11):
        return _fail(f"Python 3.11+ required, got {sys.version.split()[0]}")

    for message in (
        _ensure_agent_config(bootstrap=args.bootstrap),
        _ensure_env_file(bootstrap=args.bootstrap),
    ):
        if message:
            return _fail(message)

    mini_bin = _resolve_mini_bin(mini_bin_arg=args.mini_bin, profile_name=args.agent_profile)
    if mini_bin:
        _patch_agent_bin(mini_bin)
    else:
        return _fail(
            "mini-swe-agent CLI not found on PATH; run ./setup.sh or "
            "pip install mini-swe-agent into .venv"
        )

    if shutil.which("pytest") is None:
        return _fail("pytest not found; run ./setup.sh")

    try:
        loaded = load_agent_run_config(
            base_config=AgentRunConfig(agent="mini-swe-agent", yolo=True),
            config_path=DEFAULT_AGENT_CONFIG,
            profile_name=args.agent_profile,
            env_file=_REPO_ROOT / ".env",
        )
    except ValueError as exc:
        return _fail(str(exc))

    summary = loaded.summary
    if not summary.get("api_key_present"):
        key_env = summary.get("api_key_env", "FEATURELIFTBENCH_API_KEY")
        return _fail(
            f"{key_env} is empty in .env for profile {args.agent_profile}; "
            "add your API key before running suites"
        )
    if not summary.get("api_base"):
        return _fail(f"API base URL missing for profile {args.agent_profile}")

    agent_bin = summary.get("agent_bin") or mini_bin
    if not Path(agent_bin).is_file() and shutil.which(agent_bin) is None:
        return _fail(f"agent_bin not executable: {agent_bin}")

    print(
        "preflight: ok "
        f"profile={args.agent_profile} "
        f"model={summary.get('model', '')} "
        f"mini={agent_bin}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
