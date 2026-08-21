"""Pinned third-party coding runtimes treated as OpenHands-level agents.

These adapters are a runtime ablation, not Official Main. Do not merge their
Functional Pass numbers into the OpenHands Python-200 leaderboard.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .agent_adapters import AgentRunConfig
from .agent_adapters import AgentRunContext


RUNTIME_TASK_FILENAME = "FEATURELIFT_AGENT_TASK.md"
PINS_PATH = Path(__file__).resolve().parents[1] / "config" / "runtime_pins.json"

DSH_SHORT_PROMPT = (
    "Follow FEATURELIFT_AGENT_TASK.md in the current directory exactly. "
    "Extract the feature into submission/featurelifted/ and finish."
)
CODEX_SHORT_PROMPT = DSH_SHORT_PROMPT


def load_runtime_pins(path: str | Path | None = None) -> dict[str, Any]:
    pins_path = Path(path) if path is not None else PINS_PATH
    return json.loads(pins_path.read_text(encoding="utf-8"))


def runtime_task_prompt(*, task_text: str) -> str:
    """Main-protocol instructions shared by DeepSeek Harness and Codex."""

    return (
        "# FeatureLiftBench Runtime Task\n\n"
        "You are a coding agent extracting one feature from a pinned upstream "
        "repository into an independent Python package.\n\n"
        "## Information Boundary\n\n"
        "- Read `TASK.md` (authoritative public contract) and search `repo/`.\n"
        "- Benchmark-authored evaluator tests are **not mounted**. Do not look "
        "for `hidden_tests/`, `public_tests/`, `evaluation/`, or reference solutions.\n"
        "- Upstream tests, docs, and examples already present under `repo/` may "
        "be used as source context.\n"
        "- Do not access parent directories of this workspace.\n\n"
        "## Required Finish State\n\n"
        "Write the extracted package here:\n\n"
        "```text\n"
        "submission/\n"
        "  featurelifted/\n"
        "    __init__.py\n"
        "    ...\n"
        "```\n\n"
        "The evaluator installs only `submission/` after you finish. Leaving "
        "code only under `repo/` is a missing submission.\n\n"
        "## Public Contract (from TASK.md)\n\n"
        f"{task_text.rstrip()}\n"
    )


def write_runtime_task_file(context: AgentRunContext) -> Path:
    destination = context.workspace_dir / RUNTIME_TASK_FILENAME
    destination.write_text(
        runtime_task_prompt(task_text=context.task_text),
        encoding="utf-8",
    )
    return destination


def _resolve_bin(config: AgentRunConfig, *, env_name: str, default: str) -> str:
    if config.agent_bin:
        return config.agent_bin
    env = config.env or {}
    return str(env.get(env_name) or default)


def build_deepseek_harness_command(
    context: AgentRunContext,
    config: AgentRunConfig,
) -> list[str]:
    del context
    binary = _resolve_bin(
        config,
        env_name="FEATURELIFTBENCH_DSH_BIN",
        default="dsh",
    )
    command = [binary, "--profile", "headless"]
    command.extend(config.extra_args)
    command.append(DSH_SHORT_PROMPT)
    return command


def build_codex_command(
    context: AgentRunContext,
    config: AgentRunConfig,
) -> list[str]:
    del context
    binary = _resolve_bin(
        config,
        env_name="FEATURELIFTBENCH_CODEX_BIN",
        default="codex",
    )
    command = [
        binary,
        "exec",
        "--approve-for-me",
        "--skip-git-repo-check",
        "--json",
    ]
    if config.model:
        command.extend(["--model", config.model])
    command.extend(config.extra_args)
    command.append(CODEX_SHORT_PROMPT)
    return command
