#!/usr/bin/env python3
"""Validate local/server environment before running agent suites."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_HARNESS_ROOT = _REPO_ROOT / "harness"
if str(_HARNESS_ROOT) not in sys.path:
    sys.path.insert(0, str(_HARNESS_ROOT))

from featureliftbench.agent_config import load_agent_run_config  # noqa: E402
from featureliftbench.agent_adapters import AgentRunConfig  # noqa: E402
from featureliftbench.dependency_install import sanity_vendor_wheels_ready  # noqa: E402
from featureliftbench.paths import DEFAULT_AGENT_CONFIG  # noqa: E402
from featureliftbench.paths import DEFAULT_AGENT_CONFIG_EXAMPLE  # noqa: E402

DEFAULT_AGENT_IMAGE = "featureliftbench-agent:latest"
DEFAULT_EVAL_IMAGE = "featureliftbench-eval:latest"


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


def _is_featurelift_agent(agent: str) -> bool:
    normalized = agent.strip().lower().replace("_", "-")
    return normalized in {"featurelift-agent", "featureliftagent", "featurelift"}


def _is_openhands_agent(agent: str) -> bool:
    normalized = agent.strip().lower().replace("_", "-")
    return normalized in {"openhands", "openhands-agent", "openhandsagent"}


def _openhands_available_locally() -> bool:
    return shutil.which("openhands") is not None


def _openhands_available_in_docker(image: str) -> bool:
    completed = subprocess.run(
        ["docker", "run", "--rm", "--entrypoint", "which", image, "openhands"],
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode == 0


def _check_vendor_wheels(*, agent: str) -> str | None:
    if not _is_featurelift_agent(agent):
        return None
    ready, missing = sanity_vendor_wheels_ready()
    if ready:
        return None
    return (
        "missing vendor wheels for sanity tasks: "
        + ", ".join(missing)
        + "; run PYTHONPATH=harness python harness/scripts/bootstrap_vendor_wheels.py"
    )


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


def _docker_image_exists(image: str) -> bool:
    completed = subprocess.run(
        ["docker", "image", "inspect", image],
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode == 0


def _list_stale_flb_containers() -> list[str]:
    completed = subprocess.run(
        [
            "docker",
            "ps",
            "-a",
            "--filter",
            "name=flb-",
            "--format",
            "{{.Names}}",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return []
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def _check_run_lock(output_dir: Path) -> str | None:
    lock_dir = output_dir / ".run.lock"
    if not lock_dir.is_dir():
        return None
    pid_path = lock_dir / "pid"
    holder = pid_path.read_text(encoding="utf-8").strip() if pid_path.is_file() else ""
    message = f"another suite run holds {lock_dir}"
    if holder:
        message += f" (pid {holder})"
    message += f"; stop that run or remove stale lock: rmdir {lock_dir}"
    return message


def _check_docker_suite(*, output_dir: Path | None) -> int:
    if shutil.which("docker") is None:
        return _fail("docker CLI not found on PATH")

    completed = subprocess.run(
        ["docker", "info"],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        return _fail(f"docker info failed: {detail or 'unknown error'}")

    for image in (DEFAULT_AGENT_IMAGE, DEFAULT_EVAL_IMAGE):
        if not _docker_image_exists(image):
            return _fail(
                f"Docker image {image} not found; build with "
                f"docker/build_agent_image.sh / docker/build_eval_image.sh"
            )

    live_trajectory = os.environ.get("FEATURELIFTBENCH_LIVE_TRAJECTORY", "1").strip().lower()
    if live_trajectory in {"0", "false", "no", "off"}:
        print(
            "preflight: warning FEATURELIFTBENCH_LIVE_TRAJECTORY=0 — "
            "suite progress may show 0 tokens",
            file=sys.stderr,
        )

    if output_dir is not None:
        output_path = output_dir.resolve()
        lock_message = _check_run_lock(output_path)
        if lock_message:
            return _fail(lock_message)

    stale = _list_stale_flb_containers()
    if stale:
        names = " ".join(stale[:10])
        suffix = f" (+{len(stale) - 10} more)" if len(stale) > 10 else ""
        print(
            f"preflight: warning stale flb-* containers: {names}{suffix}",
            file=sys.stderr,
        )
        print(
            "preflight: cleanup example: docker rm -f $(docker ps -aq --filter name=flb-)",
            file=sys.stderr,
        )

    print(
        f"preflight: docker ok images={DEFAULT_AGENT_IMAGE},{DEFAULT_EVAL_IMAGE}",
        file=sys.stderr,
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="FeatureLiftBench run preflight checks")
    parser.add_argument(
        "--agent",
        default="mini-swe-agent",
        help="agent adapter to validate (default: mini-swe-agent)",
    )
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
    parser.add_argument(
        "--docker-suite",
        action="store_true",
        help="validate Docker daemon and agent/eval images for long suite runs",
    )
    parser.add_argument(
        "--output-dir",
        default="",
        help="suite output directory (used with --docker-suite for lock checks)",
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

    for message in (
        _ensure_agent_config(bootstrap=args.bootstrap),
        _ensure_env_file(bootstrap=args.bootstrap),
        _check_vendor_wheels(agent=args.agent),
    ):
        if message:
            return _fail(message)

    featurelift_agent = _is_featurelift_agent(args.agent)
    openhands_agent = _is_openhands_agent(args.agent)
    mini_bin = ""
    if not featurelift_agent and not openhands_agent:
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
            base_config=AgentRunConfig(agent=args.agent, yolo=not featurelift_agent),
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

    if not featurelift_agent and not openhands_agent:
        agent_bin = summary.get("agent_bin") or mini_bin
        if not Path(agent_bin).is_file() and shutil.which(agent_bin) is None:
            return _fail(f"agent_bin not executable: {agent_bin}")
    elif featurelift_agent:
        extra_args = loaded.run_config.extra_args
        if "--enable-llm" not in extra_args:
            return _fail(
                f"profile {args.agent_profile} must enable featurelift LLM "
                "(featurelift_enable_llm=true or --agent-arg --enable-llm)"
            )
        if "--execute-actions" not in extra_args:
            return _fail(
                f"profile {args.agent_profile} must enable featurelift actions "
                "(featurelift_execute_actions=true or --agent-arg --execute-actions)"
            )
    elif openhands_agent:
        if not loaded.run_config.command:
            return _fail(
                f"openhands command not configured for profile {args.agent_profile}; "
                "set openhands_command in agents.toml or FEATURELIFTBENCH_OPENHANDS_COMMAND"
            )
        if args.docker_suite:
            if not _openhands_available_in_docker(DEFAULT_AGENT_IMAGE):
                return _fail(
                    f"openhands CLI not found in Docker image {DEFAULT_AGENT_IMAGE}; "
                    "rebuild with FEATURELIFTBENCH_AGENT_PYTHON_BASE=python:3.12-slim "
                    "FEATURELIFTBENCH_INSTALL_OPENHANDS=1 ./docker/build_agent_image.sh"
                )
        elif not _openhands_available_locally():
            return _fail(
                "openhands CLI not found on PATH; pip install openhands (Python 3.12+) "
                "or set FEATURELIFTBENCH_AGENT_DOCKER=1 for Docker agent runs"
            )

    if args.docker_suite:
        output_dir = Path(args.output_dir).resolve() if args.output_dir else None
        docker_status = _check_docker_suite(output_dir=output_dir)
        if docker_status != 0:
            return docker_status

    if featurelift_agent:
        print(
            "preflight: ok "
            f"agent={args.agent} "
            f"profile={args.agent_profile} "
            f"model={summary.get('model', '')}",
            file=sys.stderr,
        )
    elif openhands_agent:
        print(
            "preflight: ok "
            f"agent={args.agent} "
            f"profile={args.agent_profile} "
            f"model={summary.get('model', '')} "
            f"openhands_command={'set' if summary.get('openhands_command_configured') else 'missing'}",
            file=sys.stderr,
        )
    else:
        agent_bin = summary.get("agent_bin") or mini_bin
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
