#!/usr/bin/env python3
"""Read-only Luna RQ2-150 intake: join frozen Main and new Contract Only runs.

This produces descriptive counts, not a controlled-ablation estimate. It never
selects replacement attempts or certifies cross-campaign evaluator identity.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INVENTORY = ROOT / "docs/paper-workbench/writing/chapter2_python150_task_inventory.json"
DEFAULT_MAIN = ROOT / "reports/paper_analysis/python150_prime_v2_analysis_20260905/task_results.csv"
DEFAULT_RUNS = ROOT / "experiments/rq2_150_luna_contract_v1/runs/contract_only"
GATES = (
    ("Build", "build_pass"),
    ("Primary", "public_tests_pass"),
    ("Extended", "hidden_tests_pass"),
    ("Isolation", "isolation_pass"),
)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--main-results", type=Path, default=DEFAULT_MAIN)
    parser.add_argument("--runs", type=Path, default=DEFAULT_RUNS)
    parser.add_argument("--full-runs", type=Path, help="optional new-campaign Full Source arm for controlled 150-task pairing")
    parser.add_argument("--output", type=Path, default=ROOT / "experiments/rq2_150_luna_contract_v1/analysis")
    parser.add_argument("--preflight", action="store_true", help="validate frozen existing inputs without new runs")
    args = parser.parse_args()

    inventory = read_json(args.inventory)
    tasks = {r["task_id"]: r for r in inventory["tasks"]}
    if len(tasks) != 150 or len(inventory["tasks"]) != 150:
        raise SystemExit("inventory must contain 150 unique tasks")
    with args.main_results.open(encoding="utf-8-sig", newline="") as handle:
        main_rows = [r for r in csv.DictReader(handle) if r["model"] == "gpt-5.6-luna"]
    main_by_id = {r["task_id"]: r for r in main_rows}
    if len(main_rows) != 150 or set(main_by_id) != set(tasks):
        raise SystemExit("Main Luna and inventory must have exactly the same 150 unique task IDs")

    issues: list[dict] = []
    for tid, task in sorted(tasks.items()):
        path = ROOT / "benchmark/tasks" / tid / "metadata.json"
        if not path.is_file():
            issues.append({"task_id": tid, "kind": "missing_task_metadata", "detail": str(path)})
            continue
        current = read_json(path)
        if current.get("spec_hash") != task["spec_hash"]:
            issues.append({"task_id": tid, "kind": "spec_hash_mismatch", "detail": str(path)})
    args.output.mkdir(parents=True, exist_ok=True)
    if args.preflight:
        report = {"inventory_tasks": len(tasks), "main_luna_rows": len(main_rows),
                  "current_spec_hash_mismatches": sum(x["kind"] == "spec_hash_mismatch" for x in issues),
                  "issues": issues, "ready_for_new_runs": not issues}
        (args.output / "preflight.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({k: v for k, v in report.items() if k != "issues"}, indent=2))
        return 0 if not issues else 1

    contract_rows: list[dict] = []
    comparison_rows: list[dict] = []
    for tid, task in sorted(tasks.items()):
        main = main_by_id[tid]
        cell = args.runs / tid
        run_path = cell / "run.json"
        if not run_path.is_file():
            issues.append({"task_id": tid, "kind": "missing_run_json", "detail": str(run_path)})
            continue
        run = read_json(run_path)
        cond = run.get("experiment_conditions") or {}
        arm = run.get("ablation") or {}
        freeze = run.get("benchmark_freeze") or {}
        inventory_path = cell / "agent/agent_visible_inventory.json"
        visible = read_json(inventory_path) if inventory_path.is_file() else {}
        checks = {
            "task_id": run.get("task_id") == tid,
            "source_context": arm.get("source_context") == "contract_only",
            "agent_source_unavailable": cond.get("agent_source_available") is False,
            "repo_absent": visible.get("repo_present") is False,
            "visible_source_unavailable": visible.get("agent_source_available") is False,
            "package_mount": cond.get("agent_harness_mount") == "package",
            "supplementary_isolation": cond.get("source_ablation_isolation") is True,
            "benchmark_tests_hidden": cond.get("benchmark_tests_visible_to_agent") is False,
            "source_hints_hidden": cond.get("source_hints_visible_to_agent") is False,
            "agent_docker": run.get("agent_backend") == "docker",
            "eval_docker": run.get("eval_backend") == "docker",
            "eval_network_none": (cond.get("evaluator_runtime") or {}).get("network") == "none",
            "spec_hash": freeze.get("spec_hash") == task["spec_hash"],
        }
        failed_checks = [name for name, ok in checks.items() if not ok]
        if failed_checks:
            issues.append({"task_id": tid, "kind": "run_identity_or_visibility", "detail": ",".join(failed_checks)})
        for name in ("repo", "public_tests", "hidden_tests", "reference_solution", "evaluation"):
            if (cell / "workspace" / name).exists():
                issues.append({"task_id": tid, "kind": "forbidden_workspace_path", "detail": name})

        delivered = (run.get("submission") or {}).get("exists") is True
        eval_path = cell / "eval/result.json"
        result = read_json(eval_path) if eval_path.is_file() else None
        if delivered != (result is not None):
            issues.append({"task_id": tid, "kind": "submission_eval_mismatch", "detail": str(eval_path)})
        if result is not None and result.get("task_id") != tid:
            issues.append({"task_id": tid, "kind": "eval_task_id_mismatch", "detail": str(eval_path)})
        if result is not None:
            sandbox = result.get("sandbox") or {}
            if sandbox.get("backend") != "docker" or sandbox.get("network") != "none":
                issues.append({"task_id": tid, "kind": "eval_sandbox_mismatch", "detail": str(eval_path)})
            if not result.get("evaluation_capsule_digest"):
                issues.append({"task_id": tid, "kind": "missing_eval_capsule_digest", "detail": str(eval_path)})
        gates = {name: result.get(key) is True if result else False for name, key in GATES}
        passed = delivered and result is not None and all(gates.values())
        if result is not None and bool((result.get("scores") or {}).get("functional_gate")) != passed:
            issues.append({"task_id": tid, "kind": "gate_score_disagreement", "detail": str(eval_path)})
        first = "Missing" if not delivered else next((name for name, ok in gates.items() if not ok), "Pass")
        event_path = cell / "agent/openhands_events.jsonl"
        error_codes: set[str] = set()
        if event_path.is_file():
            for line in event_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    event = json.loads(line)
                    if event.get("kind") == "ConversationErrorEvent":
                        error_codes.add(str(event.get("code") or "unknown"))
        else:
            issues.append({"task_id": tid, "kind": "missing_events", "detail": str(event_path)})
        row = {
            "task_id": tid,
            "repository": task["source_repo_id"],
            "cohort": "earlier" if task["construction_group_150"] == "core100" else "later",
            "lift_type": task["historical_lift_type"],
            "delivered": int(delivered),
            "functional_pass": int(passed),
            "first_outcome": first,
            "first_failed_gate": first if first not in ("Pass", "Missing") else "",
            **{f"{name.lower()}_pass": int(ok) if delivered else "" for name, ok in gates.items()},
            "attempt": run.get("attempt", ""),
            "run_status": run.get("status", ""),
            "agent_exit_status": ((run.get("agent") or {}).get("usage") or {}).get("exit_status", ""),
            "assistant_steps": ((run.get("agent") or {}).get("usage") or {}).get("assistant_steps", ""),
            "api_calls": ((run.get("agent") or {}).get("usage") or {}).get("api_calls", ""),
            "agent_duration_seconds": (run.get("agent") or {}).get("duration_seconds", ""),
            "conversation_error_codes": "|".join(sorted(error_codes)),
            "new_freeze_id": freeze.get("freeze_id", ""),
            "main_freeze_id": main.get("freeze_id", ""),
            "freeze_id_matches_main": int(freeze.get("freeze_id") == main.get("freeze_id")),
            "eval_capsule_digest": result.get("evaluation_capsule_digest", "") if result else "",
            "model_id": cond.get("model", ""),
            "agent_profile": cond.get("agent_profile", ""),
            "agent_image_id": (cond.get("agent_runtime") or {}).get("image_id", ""),
            "eval_image_id": (cond.get("evaluator_runtime") or {}).get("image_id", ""),
            "timeout_seconds": cond.get("agent_timeout_seconds", ""),
            "max_steps": cond.get("agent_max_steps", ""),
            "run_json": str(run_path),
            "run_json_sha256": sha256_file(run_path),
            "eval_result_json": str(eval_path) if result else "",
            "eval_result_sha256": sha256_file(eval_path) if result else "",
        }
        contract_rows.append(row)
        comparison_rows.append({
            "task_id": tid, "repository": row["repository"], "cohort": row["cohort"],
            "lift_type": row["lift_type"], "main_full_pass": int(main["functional_pass"].lower() == "true"),
            "new_contract_pass": int(passed), "main_full_delivered": int(main["usable_submission"].lower() == "true"),
            "new_contract_delivered": int(delivered), "main_full_first_outcome": main["first_failure_stage"],
            "new_contract_first_outcome": first, "main_freeze_id": row["main_freeze_id"],
            "new_freeze_id": row["new_freeze_id"], "freeze_id_matches": row["freeze_id_matches_main"],
        })

    write_csv(args.output / "contract_task_outcomes.csv", contract_rows)
    write_csv(args.output / "main_full150_vs_new_contract150.csv", comparison_rows)
    for field in ("model_id", "agent_profile", "agent_image_id", "eval_image_id", "timeout_seconds", "max_steps"):
        values = {str(r[field]) for r in contract_rows}
        if len(values) > 1 or (values and values == {""} and field != "max_steps"):
            issues.append({"task_id": "*", "kind": "inconsistent_run_configuration", "detail": field + ": " + repr(sorted(values))})
    complete = len(contract_rows) == 150 and not issues
    counts = Counter((r["main_full_pass"], r["new_contract_pass"]) for r in comparison_rows)
    descriptive = {
        "analysis_type": "cross-campaign descriptive comparison; not controlled ablation",
        "assigned_tasks": 150, "new_contract_records": len(contract_rows),
        "main_full_pass": sum(r["main_full_pass"] for r in comparison_rows),
        "new_contract_pass": sum(r["new_contract_pass"] for r in comparison_rows),
        "both": counts[1, 1], "full_only": counts[1, 0],
        "contract_only": counts[0, 1], "neither": counts[0, 0],
        "contract_first_outcome": dict(Counter(r["first_outcome"] for r in contract_rows)),
        "contract_delivered": sum(r["delivered"] for r in contract_rows),
        "new_and_main_freeze_id_disagreements": sum(not r["freeze_id_matches_main"] for r in contract_rows),
    }
    if complete:
        descriptive["difference_pp"] = round(100 * (descriptive["main_full_pass"] - descriptive["new_contract_pass"]) / 150, 4)
        descriptive["by_lift_type"] = {}
        descriptive["by_cohort"] = {}
        for field, output_field in (("lift_type", "by_lift_type"), ("cohort", "by_cohort")):
            for value in sorted({r[field] for r in comparison_rows}):
                subset = [r for r in comparison_rows if r[field] == value]
                descriptive[output_field][value] = {
                    "n": len(subset),
                    "main_full_pass": sum(r["main_full_pass"] for r in subset),
                    "new_contract_pass": sum(r["new_contract_pass"] for r in subset),
                    "full_only": sum(r["main_full_pass"] and not r["new_contract_pass"] for r in subset),
                    "contract_only": sum(r["new_contract_pass"] and not r["main_full_pass"] for r in subset),
                }
        (args.output / "descriptive_results.json").write_text(json.dumps(descriptive, indent=2) + "\n")
    strict_summary = None
    if args.full_runs is not None:
        if not complete:
            issues.append({"task_id": "*", "kind": "contract_arm_incomplete", "detail": "strict pairing requires complete Contract Only arm"})
        else:
            strict_pairs: list[dict] = []
            contracts = {r["task_id"]: r for r in contract_rows}
            for tid, task in sorted(tasks.items()):
                cell = args.full_runs / tid
                run_path = cell / "run.json"
                inventory_path = cell / "agent/agent_visible_inventory.json"
                if not run_path.is_file() or not inventory_path.is_file():
                    issues.append({"task_id": tid, "kind": "missing_new_full_record", "detail": str(run_path)})
                    continue
                run = read_json(run_path)
                cond = run.get("experiment_conditions") or {}
                visible = read_json(inventory_path)
                freeze = run.get("benchmark_freeze") or {}
                contract = contracts[tid]
                checks = {
                    "task_id": run.get("task_id") == tid,
                    "full_source_context": (run.get("ablation") or {}).get("source_context") == "full_repository",
                    "repo_visible": visible.get("repo_present") is True and visible.get("agent_source_available") is True,
                    "package_mount": cond.get("agent_harness_mount") == "package",
                    "supplementary_isolation": cond.get("source_ablation_isolation") is True,
                    "benchmark_tests_hidden": cond.get("benchmark_tests_visible_to_agent") is False,
                    "source_hints_hidden": cond.get("source_hints_visible_to_agent") is False,
                    "agent_docker": run.get("agent_backend") == "docker",
                    "eval_docker": run.get("eval_backend") == "docker",
                    "eval_network_none": (cond.get("evaluator_runtime") or {}).get("network") == "none",
                    "spec_hash": freeze.get("spec_hash") == task["spec_hash"],
                    "source_snapshot": (run.get("source") or {}).get("source_snapshot_id") == task["source_snapshot_id"],
                }
                for source, target in (("model", "model_id"), ("agent_profile", "agent_profile"),
                                       ("agent_timeout_seconds", "timeout_seconds"), ("agent_max_steps", "max_steps")):
                    checks["paired_" + source] = str(cond.get(source, "")) == str(contract[target])
                checks["paired_agent_image"] = (cond.get("agent_runtime") or {}).get("image_id") == contract["agent_image_id"]
                checks["paired_eval_image"] = (cond.get("evaluator_runtime") or {}).get("image_id") == contract["eval_image_id"]
                failed = [name for name, ok in checks.items() if not ok]
                if failed:
                    issues.append({"task_id": tid, "kind": "paired_full_identity", "detail": ",".join(failed)})
                delivered = (run.get("submission") or {}).get("exists") is True
                result_path = cell / "eval/result.json"
                result = read_json(result_path) if result_path.is_file() else None
                if delivered != (result is not None):
                    issues.append({"task_id": tid, "kind": "paired_full_submission_eval_mismatch", "detail": str(result_path)})
                if result is not None:
                    if result.get("task_id") != tid:
                        issues.append({"task_id": tid, "kind": "paired_full_eval_task_mismatch", "detail": str(result_path)})
                    sandbox = result.get("sandbox") or {}
                    if sandbox.get("backend") != "docker" or sandbox.get("network") != "none":
                        issues.append({"task_id": tid, "kind": "paired_full_eval_sandbox", "detail": str(result_path)})
                    if not result.get("evaluation_capsule_digest"):
                        issues.append({"task_id": tid, "kind": "paired_full_missing_capsule", "detail": str(result_path)})
                    if contract["eval_capsule_digest"] and result.get("evaluation_capsule_digest") != contract["eval_capsule_digest"]:
                        issues.append({"task_id": tid, "kind": "paired_capsule_mismatch", "detail": str(result_path)})
                gates = {name: result.get(key) is True if result else False for name, key in GATES}
                passed = bool(delivered and result is not None and all(gates.values()))
                if result is not None and bool((result.get("scores") or {}).get("functional_gate")) != passed:
                    issues.append({"task_id": tid, "kind": "paired_full_gate_score_disagreement", "detail": str(result_path)})
                strict_pairs.append({
                    "task_id": tid, "repository": task["source_repo_id"],
                    "cohort": contract["cohort"], "lift_type": contract["lift_type"],
                    "new_full_pass": int(passed), "new_contract_pass": contract["functional_pass"],
                    "new_full_delivered": int(delivered), "new_contract_delivered": contract["delivered"],
                    "new_full_first_outcome": "Missing" if not delivered else next((name for name, ok in gates.items() if not ok), "Pass"),
                    "new_contract_first_outcome": contract["first_outcome"],
                    "new_full_run_json": str(run_path), "new_contract_run_json": contract["run_json"],
                })
            write_csv(args.output / "paired_150.csv", strict_pairs)
            if len(strict_pairs) == 150 and not issues:
                import numpy as np

                n = 150
                full_only = sum(r["new_full_pass"] and not r["new_contract_pass"] for r in strict_pairs)
                contract_only = sum(r["new_contract_pass"] and not r["new_full_pass"] for r in strict_pairs)
                discord = full_only + contract_only
                mcnemar_p = min(1.0, 2 * sum(math.comb(discord, i) for i in range(min(full_only, contract_only) + 1)) / 2**discord) if discord else 1.0
                delta = np.array([r["new_full_pass"] - r["new_contract_pass"] for r in strict_pairs], dtype=float)
                rng = np.random.default_rng(20260913)
                samples = np.concatenate([delta[rng.integers(0, n, size=(10000, n))].mean(axis=1) for _ in range(10)])
                repo_ids = sorted({r["repository"] for r in strict_pairs})
                repo_sums = np.array([sum(r["new_full_pass"] - r["new_contract_pass"] for r in strict_pairs if r["repository"] == repo) for repo in repo_ids])
                repo_sizes = np.array([sum(r["repository"] == repo for r in strict_pairs) for repo in repo_ids])
                cluster_samples = []
                for _ in range(10):
                    ix = rng.integers(0, len(repo_ids), size=(10000, len(repo_ids)))
                    cluster_samples.append(repo_sums[ix].sum(axis=1) / repo_sizes[ix].sum(axis=1))
                strict_summary = {
                    "analysis_type": "new-campaign controlled paired 150-task ablation",
                    "n": n, "new_full_pass": sum(r["new_full_pass"] for r in strict_pairs),
                    "new_contract_pass": sum(r["new_contract_pass"] for r in strict_pairs),
                    "both": sum(r["new_full_pass"] and r["new_contract_pass"] for r in strict_pairs),
                    "full_only": full_only, "contract_only": contract_only,
                    "neither": sum(not r["new_full_pass"] and not r["new_contract_pass"] for r in strict_pairs),
                    "delta_pp": 100 * float(delta.mean()),
                    "paired_bootstrap_95ci_pp": (100 * np.quantile(samples, [0.025, 0.975])).tolist(),
                    "repository_cluster_bootstrap_95ci_pp": (100 * np.quantile(np.concatenate(cluster_samples), [0.025, 0.975])).tolist(),
                    "mcnemar_exact_p": mcnemar_p,
                    "bootstrap_seed": 20260913, "bootstrap_resamples": 100000,
                }
                (args.output / "paired_150_stats.json").write_text(json.dumps(strict_summary, indent=2) + "\n")
    complete = complete and (args.full_runs is None or strict_summary is not None)
    report = {
        "machine_checks_complete": complete,
        "cross_campaign_identity_audit_required": True,
        "service_error_retention_review_required": True,
        "paper_ready": False,
        "note": "Paper readiness requires manual retained-attempt, task/evaluator/dependency identity, and infrastructure review. This script does not certify them.",
        "descriptive_counts": descriptive if complete else None,
        "controlled_pair_counts": strict_summary,
        "issues": issues,
    }
    (args.output / "readiness.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "issues"}, indent=2))
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
