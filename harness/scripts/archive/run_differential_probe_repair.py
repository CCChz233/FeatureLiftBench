#!/usr/bin/env python3
"""Run eval-blind differential-probe repair from a frozen clean3 candidate.

The agent receives TASK, the full upstream repository, the prior submission,
the prior clean3 contracts, and an observation-only upstream/candidate diff
tool.  Benchmark evaluator tests and historical formal failures are absent.
Formal Docker evaluation runs only after the repaired submission is frozen.
"""

from __future__ import annotations

import argparse
import hashlib
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
from featureliftbench.differential_probe import load_probe_audit  # noqa: E402
from featureliftbench.differential_probe import (  # noqa: E402
    prepare_upstream_runtime_docker,
)
from featureliftbench.docker_eval import evaluate_submission_docker  # noqa: E402
from featureliftbench.exec_contract import verify_submission_contracts  # noqa: E402
from featureliftbench.metadata import load_metadata  # noqa: E402


def _resolve_seed_dir(seed_run: Path, task_id: str, name: str) -> Path:
    candidates = (
        seed_run / task_id / name,
        seed_run / task_id / "workspace" / name,
        seed_run / name,
        seed_run / "workspace" / name,
    )
    for candidate in candidates:
        if candidate.is_dir():
            return candidate.resolve()
    raise ValueError(
        f"no seed {name}/ found under {seed_run}; checked task/output layouts"
    )


def _reset_output(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise ValueError(f"refusing to overwrite non-empty output: {path}")
    path.mkdir(parents=True, exist_ok=True)


def _agent_payload(result: Any, stdout: Path, stderr: Path) -> dict[str, Any]:
    if result is None:
        return {}
    return result.payload(stdout_log=stdout, stderr_log=stderr)


def _tree_digest(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(value for value in path.rglob("*") if value.is_file()):
        digest.update(str(item.relative_to(path)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(item.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _dpr_task_appendix() -> str:
    return """\
### Paired Differential Repair (PDR)

This is a **local repair** of an existing candidate. Do not replace the whole
submission when a small correction is sufficient.

The workspace contains:

1. `submission/` — the frozen clean3 candidate to improve in place.
2. `contracts/` — the frozen clean3 regression suite. Do not edit or weaken it.
3. `repo/` — the full upstream source repository.
4. `.dpr/baseline_submission/` — the immutable pre-repair candidate.
5. `/flb/harness/scripts/flb_diff.py` — an observation-only differential runner.

Your additional dynamic-analysis capability is intentionally minimal:

```bash
mkdir -p probes
python /flb/harness/scripts/flb_diff.py probes/<name>.py
```

The probe is run three times with `FLB_DIFF_TARGET` set to `upstream`,
`baseline`, and `candidate`. Baseline and candidate use the same adapter.
Print one deterministic JSON object with exactly these conceptual sections:

```json
{"target": {"behavior_to_repair": "observed value"},
 "control": {"nearby_behavior_to_preserve": "observed value"}}
```

The target is compared with upstream. The control is compared with the
pre-repair baseline. Therefore upstream says what to add, while the baseline
says what not to break.

Rules:

- Probes are observations, not tests: no `assert`, no expected/golden values,
  and no pytest/unittest.
- `target` and `control` must each contain exactly one named observation. Do
  not bundle a behavior checklist into either section.
- Search narrowly. A probe whose target already matches may be discarded.
  The first probe showing `target_matches_upstream=false` while
  `control_preserved_from_baseline=true` is actionable; its path and content
  are then frozen by the tool.
- Before writing it, statically confirm that the chosen target operation
  exists in both upstream and candidate. Do not target task-added wrapper
  methods that have no upstream counterpart.
- First compare TASK's behavioral bullets with the candidate method bodies.
  Prefer a declared branch absent from the candidate's control flow,
  especially special/overloaded inputs and ambiguity handling, over broad
  graph combinations that the implementation already appears to cover.
- Choose one uncertain TASK-required behavior as the target and its closest
  non-target neighbor as the control.
- **Domain-complete control rule:** if the target changes dispatch on symbolic
  strings or other special values, the control must register *every special
  value named by TASK* as ordinary user data and observe lookup of the whole
  set. `None`, a missing value, or an unrelated ordinary id is not a valid
  control for symbolic dispatch. Preserve this implementation invariant:
  exact registered data is checked before symbolic fallback.
- Branch on `FLB_DIFF_TARGET == "upstream"` only for imports and constructor
  adapters; `baseline` and `candidate` must share the candidate adapter.
- Use upstream execution as the oracle only for behavior declared by TASK.
- Observe public values, ids, declared ordering, and relevant state. For
  exceptions, compare only the coarsest class/interface explicitly named by
  TASK (for example, `isinstance(error, UsageError)`). An upstream-only
  exception subtype is not an admissible target unless TASK names it.
- Do not optimize exact exception wording/casing unless TASK explicitly
  declares it.
- Do not look for benchmark public/hidden tests or reference solutions.
- Do not inspect upstream test files, delegate to subagents, or run separate
  upstream/candidate `python -c` comparisons. All cross-target behavioral
  feedback must come from the one audited `flb_diff.py` probe.
- Do not edit `.dpr/baseline_submission/`, contracts, or the probe after its
  first comparable run.
- Enter one repair episode for that frozen target. You may refine the patch
  only when the same frozen control exposes a regression; do not switch to a
  new target or probe. Finish only if `target_matches_upstream` and
  `control_preserved_from_baseline` are both true, then run:

```bash
PYTHONPATH=submission pytest contracts/ -q
```

Do not broaden the search after that one repair. Finish only after the frozen
clean3 contracts still pass.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--seed-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--max-agent-steps", type=int, default=60)
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
    parser.add_argument(
        "--no-formal",
        action="store_true",
        help="Stop after freezing the repaired submission (development only).",
    )
    args = parser.parse_args()

    task_dir = (ROOT / "benchmark" / "tasks" / args.task_id).resolve()
    if not (task_dir / "metadata.json").is_file():
        raise ValueError(f"task not found: {task_dir}")
    seed_run = args.seed_run.resolve()
    seed_submission = _resolve_seed_dir(seed_run, args.task_id, "submission")
    seed_contracts = _resolve_seed_dir(seed_run, args.task_id, "contracts")
    output = args.output.resolve()
    _reset_output(output)

    workspace = output / "workspace"
    agent_dir = output / "agent_repair"
    collected = output / "submission"
    eval_dir = output / "eval"
    agent_dir.mkdir(parents=True)

    metadata = load_metadata(task_dir).data
    task_file = prepare_agent_workspace(
        task_dir,
        workspace,
        metadata,
        ablation=AblationOptions(),
    )
    workspace_submission = workspace / "submission"
    if workspace_submission.exists():
        shutil.rmtree(workspace_submission)
    shutil.copytree(seed_submission, workspace_submission)
    shutil.copytree(seed_contracts, workspace / "contracts")
    baseline_submission = workspace / ".dpr" / "baseline_submission"
    baseline_submission.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(seed_submission, baseline_submission)
    baseline_digest_before = _tree_digest(baseline_submission)

    upstream_runtime = prepare_upstream_runtime_docker(
        workspace,
        docker_image=args.agent_image,
    )
    if not upstream_runtime.get("ok"):
        raise RuntimeError(
            "upstream runtime dependency preparation failed: "
            + str(upstream_runtime.get("stderr_tail") or "")
        )

    base_task = task_file.read_text(encoding="utf-8").rstrip()
    task_text = base_task + "\n\n## Dynamic Analysis Phase\n\n" + _dpr_task_appendix()
    task_file.write_text(task_text + "\n", encoding="utf-8")

    verify_initial = verify_submission_contracts(
        workspace,
        docker_image=args.agent_image,
        use_docker=True,
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
        exec_contract=False,
        self_contract=False,
    )
    repair_config = replace(
        loaded.run_config,
        timeout_seconds=max(1, args.timeout),
        env={
            **(loaded.run_config.env or {}),
            "FEATURELIFTBENCH_DPR": "1",
            "FEATURELIFTBENCH_EXEC_CONTRACT": "0",
            "FEATURELIFTBENCH_OPENHANDS_MAX_STEPS": str(
                max(1, args.max_agent_steps)
            ),
            "FLB_DIFF_INCLUDE_BASELINE": "1",
            "FLB_DIFF_REQUIRE_PAIRED": "1",
            "FLB_DIFF_SINGLE_PROBE": "1",
            "FLB_DIFF_MAX_CALLS": "8",
            "MSWEA_GLOBAL_CALL_LIMIT": "70",
        },
    )
    stdout_log = agent_dir / "stdout.log"
    stderr_log = agent_dir / "stderr.log"
    context = AgentRunContext(
        workspace_dir=workspace,
        task_file=task_file,
        submission_dir=workspace_submission,
        agent_output_dir=agent_dir,
        task_text=task_text,
    )
    agent_result = run_agent_in_docker(
        context,
        repair_config,
        image=args.agent_image,
        stdout_log=stdout_log,
        stderr_log=stderr_log,
    )

    baseline_digest_after = _tree_digest(baseline_submission)
    baseline_unchanged = baseline_digest_before == baseline_digest_after
    verify_final = verify_submission_contracts(
        workspace,
        docker_image=args.agent_image,
        use_docker=True,
    )
    probe_audit = load_probe_audit(workspace)
    shutil.copytree(workspace_submission, collected)

    evaluation: dict[str, Any] = {
        "run": False,
        "status": None,
        "public_tests_pass": None,
        "hidden_tests_pass": None,
        "test_pass": None,
        "final_score": None,
        "result_json": None,
    }
    eval_result: dict[str, Any] | None = None
    formal_gate = (
        bool(verify_final.get("ok"))
        and baseline_unchanged
        and bool(probe_audit.get("protocol_compliant"))
        and bool(probe_audit.get("repair_accepted"))
    )
    if not args.no_formal and formal_gate:
        # Formal evaluation is deliberately last. Its result cannot affect the
        # already-frozen probes, agent trajectory, or submission.
        eval_result = evaluate_submission_docker(
            task_dir,
            collected,
            eval_dir,
            image=args.eval_image,
            use_docker=True,
        )
        evaluation = {
            "run": True,
            "status": eval_result.get("status"),
            "public_tests_pass": eval_result.get("public_tests_pass"),
            "hidden_tests_pass": eval_result.get("hidden_tests_pass"),
            "test_pass": eval_result.get("test_pass"),
            "final_score": (eval_result.get("scores") or {}).get("final_score"),
            "result_json": str(eval_dir / "result.json"),
        }
    elif not args.no_formal:
        evaluation["status"] = "pdr_gate_failed"

    payload = {
        "schema_version": "featureliftbench.dpr_phase.v2",
        "protocol": "paired_differential_repair",
        "evidence_class": "post_hoc_development_set_mechanism_test",
        "task_id": args.task_id,
        "seed_submission": str(seed_submission),
        "seed_contracts": str(seed_contracts),
        "seed_selection": "pre_existing_best_clean3_template_candidate",
        "seed_formal_outcome_known_to_researchers": True,
        "seed_formal_outcome_visible_to_agent": False,
        "benchmark_tests_visible_to_agent": False,
        "historical_formal_feedback_used_in_prompt": False,
        "method_rule_developed_on_focus_trajectories": True,
        "focus_task_is_development_set": True,
        "formal_feedback_used_for_repair": False,
        "probe_policy": {
            "observation_only": True,
            "upstream_supplies_target_oracle": True,
            "baseline_supplies_conservation_oracle": True,
            "first_actionable_probe_is_frozen": True,
            "domain_complete_control_required": True,
            "task_semantic_admission_required": True,
            "exception_subtypes_normalized_to_task_contract": True,
            "maximum_probe_calls": 8,
            "single_repair_target": True,
            "maximum_agent_steps": max(1, args.max_agent_steps),
            "assertions_forbidden": True,
            "expected_values_forbidden_by_protocol": True,
            "uncontracted_exact_wording_forbidden": True,
        },
        "baseline": {
            "path": str(baseline_submission),
            "sha256_before": baseline_digest_before,
            "sha256_after": baseline_digest_after,
            "unchanged": baseline_unchanged,
        },
        "upstream_runtime": upstream_runtime,
        "verify_initial": verify_initial,
        "agent": _agent_payload(agent_result, stdout_log, stderr_log),
        "agent_config": loaded.summary,
        "probe_audit": probe_audit,
        "verify_final": verify_final,
        "evaluation": evaluation,
        "formal_gate": formal_gate,
    }
    (output / "dpr_phase.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))

    if args.no_formal:
        return 0 if formal_gate else 1
    if eval_result is None:
        return 1
    return 0 if eval_result.get("status") == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
