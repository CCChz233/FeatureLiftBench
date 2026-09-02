#!/usr/bin/env python3
"""Run an eval-blind monotone CGCC repair from a prior submission.

The seed submission is copied before formal evaluation. New contracts are
synthesized only from TASK/public_spec and upstream evidence, then the agent
sees contract failures and repairs the existing implementation in place.
Benchmark public/hidden tests are mounted only after the repair is frozen.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "harness"
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

from featureliftbench.ablation import AblationOptions  # noqa: E402
from featureliftbench.agent_adapters import AgentRunConfig  # noqa: E402
from featureliftbench.agent_adapters import AgentRunContext  # noqa: E402
from featureliftbench.agent_config import load_agent_run_config  # noqa: E402
from featureliftbench.agent_docker import run_agent_in_docker  # noqa: E402
from featureliftbench.agent_runner import prepare_agent_workspace  # noqa: E402
from featureliftbench.docker_eval import evaluate_submission_docker  # noqa: E402
from featureliftbench.exec_contract import collect_upstream_runtime  # noqa: E402
from featureliftbench.exec_contract import phase1_task_appendix  # noqa: E402
from featureliftbench.exec_contract import prepare_repair_workspace  # noqa: E402
from featureliftbench.exec_contract import synthesize_contracts  # noqa: E402
from featureliftbench.exec_contract import verify_submission_contracts  # noqa: E402
from featureliftbench.metadata import load_metadata  # noqa: E402


def _resolve_seed_submission(seed_run: Path, task_id: str) -> Path:
    candidates = (
        seed_run / task_id / "submission",
        seed_run / task_id / "workspace" / "submission",
        seed_run / "submission",
        seed_run / "workspace" / "submission",
    )
    for candidate in candidates:
        if candidate.is_dir():
            return candidate.resolve()
    raise ValueError(
        f"no seed submission found under {seed_run}; checked task/output layouts"
    )


def _reset_output(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise ValueError(f"refusing to overwrite non-empty output: {path}")
    path.mkdir(parents=True, exist_ok=True)


def _agent_payload(result: Any, stdout: Path, stderr: Path) -> dict[str, Any]:
    if result is None:
        return {}
    return result.payload(stdout_log=stdout, stderr_log=stderr)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--seed-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--variant", default="cgcc_rmc", choices=("cgcc_rmc",))
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument(
        "--agent-config",
        type=Path,
        default=ROOT / "harness" / "config" / "agents.example.toml",
    )
    parser.add_argument(
        "--agent-profile",
        default="openhands_deepseek_v4_flash_exec_contract",
    )
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument(
        "--agent-image",
        default="featureliftbench-agent:latest",
    )
    parser.add_argument(
        "--eval-image",
        default="featureliftbench-eval:latest",
    )
    args = parser.parse_args()

    task_dir = (ROOT / "benchmark" / "tasks" / args.task_id).resolve()
    if not (task_dir / "metadata.json").is_file():
        raise ValueError(f"task not found: {task_dir}")
    seed_submission = _resolve_seed_submission(
        args.seed_run.resolve(),
        args.task_id,
    )
    output = args.output.resolve()
    _reset_output(output)

    workspace = output / "workspace"
    agent_dir = output / "agent_repair"
    collected = output / "submission"
    eval_dir = output / "eval"
    agent_dir.mkdir(parents=True)

    metadata = load_metadata(task_dir).data
    ablation = AblationOptions(
        exec_contract=True,
        exec_contract_variant=args.variant,
    )
    task_file = prepare_agent_workspace(
        task_dir,
        workspace,
        metadata,
        ablation=ablation,
    )
    workspace_submission = workspace / "submission"
    if workspace_submission.exists():
        shutil.rmtree(workspace_submission)
    shutil.copytree(seed_submission, workspace_submission)

    public_spec = metadata.get("public_spec")
    if not isinstance(public_spec, dict):
        raise ValueError("task public_spec is missing")
    collect_meta = collect_upstream_runtime(
        workspace,
        public_spec,
        docker_image=args.agent_image,
        use_docker=True,
    )
    synthesize_meta = synthesize_contracts(
        workspace,
        public_spec,
        collect_meta=collect_meta,
        variant=args.variant,
    )

    base_task = task_file.read_text(encoding="utf-8").rstrip()
    task_text = (
        base_task
        + "\n\n## Execution-Guided Contract\n\n"
        + phase1_task_appendix(variant=args.variant)
    )
    task_file.write_text(task_text + "\n", encoding="utf-8")
    verify_initial = verify_submission_contracts(
        workspace,
        docker_image=args.agent_image,
        use_docker=True,
    )

    agent_result = None
    stdout_log = agent_dir / "stdout.log"
    stderr_log = agent_dir / "stderr.log"
    if not verify_initial.get("ok"):
        repair_task = prepare_repair_workspace(
            workspace,
            verify_result=verify_initial,
            task_markdown=task_file.read_text(encoding="utf-8"),
        )
        loaded = load_agent_run_config(
            base_config=AgentRunConfig(
                agent="openhands-agent",
                timeout_seconds=max(1, args.timeout),
            ),
            config_path=args.agent_config,
            profile_name=args.agent_profile,
            env_file=args.env_file,
            mount_public_tests=False,
            prompt_style="standard",
            expose_source_hints=False,
            source_context="full_repository",
            td_cognition=False,
            exec_contract=True,
            exec_contract_variant=args.variant,
            self_contract=False,
        )
        repair_config = replace(
            loaded.run_config,
            timeout_seconds=max(1, args.timeout),
            env={
                **(loaded.run_config.env or {}),
                "FEATURELIFTBENCH_EXEC_CONTRACT": "1",
                "FEATURELIFTBENCH_EXEC_CONTRACT_PHASE": "warm_repair",
            },
        )
        context = AgentRunContext(
            workspace_dir=workspace,
            task_file=task_file,
            submission_dir=workspace_submission,
            agent_output_dir=agent_dir,
            task_text=repair_task,
        )
        agent_result = run_agent_in_docker(
            context,
            repair_config,
            image=args.agent_image,
            stdout_log=stdout_log,
            stderr_log=stderr_log,
        )
        agent_summary = loaded.summary
    else:
        agent_summary = {}

    verify_final = verify_submission_contracts(
        workspace,
        docker_image=args.agent_image,
        use_docker=True,
    )
    shutil.copytree(workspace_submission, collected)

    # Formal evaluation is deliberately last: its result cannot affect the
    # frozen contracts or the already-completed repair.
    eval_result = evaluate_submission_docker(
        task_dir,
        collected,
        eval_dir,
        image=args.eval_image,
        use_docker=True,
    )
    payload = {
        "schema_version": "featureliftbench.cgcc_warm_repair.v1",
        "protocol": "cgcc_monotone_delta_repair",
        "task_id": args.task_id,
        "seed_submission": str(seed_submission),
        "contract_variant": args.variant,
        "benchmark_tests_visible_to_agent": False,
        "formal_feedback_used_for_repair": False,
        "collect": collect_meta,
        "synthesize": synthesize_meta,
        "verify_initial": verify_initial,
        "agent": _agent_payload(agent_result, stdout_log, stderr_log),
        "agent_config": agent_summary,
        "verify_final": verify_final,
        "evaluation": {
            "status": eval_result.get("status"),
            "public_tests_pass": eval_result.get("public_tests_pass"),
            "hidden_tests_pass": eval_result.get("hidden_tests_pass"),
            "test_pass": eval_result.get("test_pass"),
            "final_score": (eval_result.get("scores") or {}).get("final_score"),
            "result_json": str(eval_dir / "result.json"),
        },
    }
    (output / "warm_repair_phase.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if eval_result.get("status") == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
