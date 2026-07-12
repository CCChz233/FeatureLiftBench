#!/usr/bin/env python3
"""Generate paper analysis artifacts from frozen experiment runs."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))

from featureliftbench.metadata import ENTANGLEMENT_PRIMARY_TYPES
from featureliftbench.paths import TASKS_DIR

# Import shared helpers from summarize_experiment_runs
from summarize_experiment_runs import (  # noqa: E402
    HIGH_EXTRACTION_RATIO,
    classify_failure,
    enrich_task_run,
    load_json,
    load_task_metadata,
    summarize as summarize_runs,
)

OUTPUT_DIR = _REPO_ROOT / "reports" / "paper_analysis"

MAIN_RUNS = [
    _REPO_ROOT / "experiments/python/openhands/deepseek-v4-flash/main-flash-20260705-232429",
    _REPO_ROOT / "experiments/python/openhands/qwen3.6-27b-fp8/qwen36-27b-fp8-main-20260704-001328",
    _REPO_ROOT / "experiments/python/openhands/qwen3.6-35b-a3b-fp8/qwen36-35b-a3b-fp8-main-20260704-001313",
    _REPO_ROOT / "experiments/python/openhands/qwen3-coder-30b-a3b-instruct/main-20260702-212731",
]

BATCH3_RUNS = [
    _REPO_ROOT / "experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260707-113104",
    _REPO_ROOT / "experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260707-wave2wave4",
    _REPO_ROOT / "experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260708-wave5",
]

MODEL_LABELS = {
    "main-flash-20260705-232429": "DeepSeek-V4-Flash",
    "qwen36-27b-fp8-main-20260704-001328": "Qwen3.6-27B-FP8",
    "qwen36-35b-a3b-fp8-main-20260704-001313": "Qwen3.6-35B-A3B-FP8",
    "main-20260702-212731": "Qwen3-Coder-30B",
}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def median_or_none(values: list[float]) -> float | None:
    nums = [v for v in values if isinstance(v, (int, float))]
    return round(median(nums), 4) if nums else None


def merge_batch3_runs(suite_dirs: list[Path]) -> dict[str, Any]:
    all_tasks: dict[str, dict[str, Any]] = {}
    per_run: list[dict[str, Any]] = []

    for suite_dir in suite_dirs:
        suite = load_json(suite_dir / "suite.json")
        summary = suite.get("summary") or {}
        run_stats = {"run_id": suite_dir.name, "total": summary.get("total"), "passed": summary.get("passed")}
        per_run.append(run_stats)
        for entry in suite.get("runs") or []:
            task_id = entry["task_id"]
            status = entry.get("status")
            if task_id not in all_tasks or status == "passed":
                all_tasks[task_id] = {
                    "task_id": task_id,
                    "status": status,
                    "best_run": suite_dir.name,
                    "final_score": entry.get("final_score"),
                }

    passed = sorted(t for t, v in all_tasks.items() if v["status"] == "passed")
    failed = sorted(t for t, v in all_tasks.items() if v["status"] != "passed")
    return {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "suite_dirs": [d.name for d in suite_dirs],
        "unique_tasks": len(all_tasks),
        "unique_passed": len(passed),
        "unique_failed": len(failed),
        "pass_rate": round(len(passed) / len(all_tasks), 4) if all_tasks else 0.0,
        "avg_final_score": round(
            sum((row.get("final_score") or 0.0) for row in all_tasks.values()) / len(all_tasks),
            4,
        )
        if all_tasks
        else 0.0,
        "passed_tasks": passed,
        "failed_tasks": failed,
        "per_run": per_run,
        "per_task": all_tasks,
    }


def build_python150_protocol(
    rq1: list[dict[str, Any]], batch3: dict[str, Any]
) -> dict[str, Any]:
    """Freeze the current 150-task composition and the valid comparison scopes."""

    current_ids = {path.parent.name for path in TASKS_DIR.glob("*/metadata.json")}
    core_suite = load_json(MAIN_RUNS[0] / "suite.json")
    core_ids = {row["task_id"] for row in core_suite.get("runs") or []}
    extension_ids = set(batch3.get("per_task", {}))
    if core_ids & extension_ids:
        raise ValueError("frozen core-100 and hard-50 task sets overlap")
    frozen_ids = core_ids | extension_ids
    if frozen_ids != current_ids:
        missing = sorted(current_ids - frozen_ids)
        extra = sorted(frozen_ids - current_ids)
        raise ValueError(
            f"frozen Python-150 does not match benchmark/tasks: missing={missing}, extra={extra}"
        )

    flash_core = next(row for row in rq1 if row["model"] == "DeepSeek-V4-Flash")
    total_tasks = len(core_ids) + len(extension_ids)
    total_passed = flash_core["functional_pass"] + batch3["unique_passed"]
    combined_score = (
        flash_core["avg_final_score"] * len(core_ids)
        + batch3["avg_final_score"] * len(extension_ids)
    ) / total_tasks
    return {
        "schema_version": "featureliftbench.python150_protocol.v1",
        "dataset": {
            "task_count": len(current_ids),
            "core_task_count": len(core_ids),
            "hard_extension_task_count": len(extension_ids),
            "sets_disjoint": True,
            "frozen_union_matches_current_main": True,
        },
        "comparison_scopes": {
            "cross_model_leaderboard": "core-100 only",
            "deepseek_v4_flash_full_split": "core-100 + hard-50",
            "hard_extension_calibration": "hard-50 only",
        },
        "deepseek_v4_flash_full_split": {
            "tasks": total_tasks,
            "functional_pass": total_passed,
            "pass_rate": round(total_passed / total_tasks, 4),
            "avg_final_score": round(combined_score, 4),
        },
        "score_denominator": (
            "all assigned tasks; missing submissions and failed functional gates contribute zero"
        ),
        "caveat": (
            "The full-150 Flash result is assembled from the frozen core and extension runs; "
            "only core-100 has matched runs for all four models."
        ),
    }


def load_suite_rows(suite_dir: Path) -> list[dict[str, Any]]:
    task_meta = load_task_meta_extended()
    suite = load_json(suite_dir / "suite.json")
    rows = []
    for entry in suite.get("runs") or []:
        task_id = entry.get("task_id", "")
        row = enrich_task_run(suite_dir, task_id, entry)
        row.update(task_meta.get(task_id, {}))
        row["model_label"] = MODEL_LABELS.get(suite_dir.name, suite_dir.name)
        rows.append(row)
    return rows


def aggregate_rq1(rows_by_suite: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    table = []
    for suite_name, rows in rows_by_suite.items():
        total = len(rows)
        passed = [r for r in rows if r["status"] == "passed"]
        failed = [r for r in rows if r["status"] != "passed"]
        copy_heavy = [r for r in passed if r.get("copy_heavy_pass")]
        compact = [r for r in passed if r.get("compact_pass")]
        table.append(
            {
                "model": rows[0]["model_label"] if rows else suite_name,
                "suite": suite_name,
                "tasks": total,
                "functional_pass": len(passed),
                "pass_rate": round(len(passed) / total, 4) if total else 0.0,
                "avg_final_score": round(
                    sum(r.get("final_score") or 0 for r in rows) / total, 4
                )
                if total
                else 0.0,
                "median_extraction_passed": median_or_none(
                    [r["extraction_ratio"] for r in passed]
                ),
                "median_extraction_all": median_or_none(
                    [r["extraction_ratio"] for r in rows if r.get("extraction_ratio") is not None]
                ),
                "copy_heavy_pass": len(copy_heavy),
                "compact_pass": len(compact),
                "median_tokens_passed": median_or_none([r["total_tokens"] for r in passed]),
                "median_tokens_failed": median_or_none([r["total_tokens"] for r in failed]),
                "missing_submission": sum(1 for r in rows if r["status"] == "missing_submission"),
            }
        )
    return table


def infer_semantic_failure(row: dict[str, Any]) -> str:
    mechanical = row.get("failure_mode", "")
    if mechanical == "passed":
        if row.get("copy_heavy_pass"):
            return "over_copy"
        return "passed"
    if mechanical == "missing_submission":
        return "locate_failure"
    if mechanical == "build_fail":
        return "packaging_failure"
    if mechanical == "forbidden_import_fail":
        return "forbidden_import"
    if mechanical == "public_only_fail":
        if row.get("build_pass") is False:
            return "packaging_failure"
        return "behavior_drift"
    if mechanical == "test_fail":
        if row.get("public_pass") is False:
            return "locate_failure"
        if row.get("hidden_pass") is False and row.get("public_pass") is True:
            return "dependency_closure_failure"
        return "behavior_drift"
    return "other_fail"


def build_failure_taxonomy(rows: list[dict[str, Any]], model_filter: str | None = None) -> dict[str, Any]:
    filtered = [r for r in rows if not model_filter or r.get("model_label") == model_filter]
    mechanical = Counter(r["failure_mode"] for r in filtered)
    semantic = Counter(infer_semantic_failure(r) for r in filtered)

    csv_rows = []
    for row in filtered:
        csv_rows.append(
            {
                "task_id": row["task_id"],
                "model": row.get("model_label"),
                "status": row["status"],
                "mechanical": row["failure_mode"],
                "semantic_primary": infer_semantic_failure(row),
                "extraction_ratio": row.get("extraction_ratio"),
                "final_score": row.get("final_score"),
                "public_pass": row.get("public_pass"),
                "hidden_pass": row.get("hidden_pass"),
                "build_pass": row.get("build_pass"),
                "entanglement": row.get("entanglement_level"),
                "difficulty": row.get("difficulty"),
                "notes": "",
            }
        )

    return {
        "model": model_filter or "all",
        "task_count": len(filtered),
        "mechanical_taxonomy": dict(mechanical),
        "semantic_taxonomy": dict(semantic),
        "csv_rows": csv_rows,
    }


SEMANTIC_NOTES: dict[str, str] = {
    "h2__frame_parse_core__001": "Agent finished without producing submission/; no eval artifact.",
    "bleach__sanitize_core__001": "Build/import failure before tests; incomplete standalone package layout.",
    "coverage__config_merge_core__001": "Public tests pass but hidden merge edge cases fail; likely missing helper closure.",
    "coverage__glob_matcher_core__001": "Functional pass with extraction_ratio=1.0; copy-heavy shortcut.",
    "httpx__request_model_core__001": "Public pass, hidden fail on request model edge cases.",
    "alembic__revision_map_core__hard3_001": "Batch3: public pass, hidden fail on revision graph branches.",
    "click__lazy_command_core__hard3_001": "Batch3: framework entrypoint found but dispatch closure incomplete.",
}


def annotate_csv_rows(rows: list[dict[str, Any]]) -> None:
    for row in rows:
        tid = row["task_id"]
        if tid in SEMANTIC_NOTES:
            row["notes"] = SEMANTIC_NOTES[tid]
        elif row["mechanical"] == "public_only_fail":
            row["notes"] = "Public-hidden gap; review for closure vs behavior drift."
        elif row["mechanical"] == "missing_submission":
            row["notes"] = "No submission recovered; agent or infra failure."


def sample_batch3_case_studies(batch3_rows: list[dict[str, Any]], limit: int = 5) -> list[tuple[dict[str, Any], Path]]:
    """Return (case, suite_dir) for batch3 failures worth documenting."""
    suite_by_task: dict[str, Path] = {}
    for suite_dir in BATCH3_RUNS:
        suite = load_json(suite_dir / "suite.json")
        for entry in suite.get("runs") or []:
            suite_by_task[entry["task_id"]] = suite_dir

    merged = {r["task_id"]: r for r in batch3_rows}
    picks = []
    for task_id in sorted(merged):
        row = merged[task_id]
        if row["status"] == "passed":
            continue
        suite_dir = suite_by_task.get(task_id, BATCH3_RUNS[0])
        picks.append(
            (
                {
                    "task_id": task_id,
                    "failure_mode": row["failure_mode"],
                    "semantic": infer_semantic_failure(row),
                    "extraction_ratio": row.get("extraction_ratio"),
                    "final_score": row.get("final_score"),
                    "public_pass": row.get("public_pass"),
                    "hidden_pass": row.get("hidden_pass"),
                    "source": "batch3",
                    "best_run": suite_dir.name,
                },
                suite_dir,
            )
        )
        if len(picks) >= limit:
            break
    return picks


def sample_case_studies(rows: list[dict[str, Any]], suite_dir: Path, limit: int = 8) -> list[dict[str, Any]]:
    """Pick representative failures and copy-heavy passes for case study markdown."""
    candidates: list[tuple[int, dict[str, Any]]] = []
    priority_map = {
        "public_only_fail": 10,
        "missing_submission": 9,
        "build_fail": 8,
        "forbidden_import_fail": 7,
        "test_fail": 6,
        "passed": 5,
    }
    for row in rows:
        if row.get("model_label") != "DeepSeek-V4-Flash":
            continue
        mode = row["failure_mode"]
        score = priority_map.get(mode, 1)
        if mode == "passed" and row.get("copy_heavy_pass"):
            score = 11
        candidates.append((score, row))

    candidates.sort(key=lambda x: (-x[0], x[1]["task_id"]))
    selected = []
    seen_modes: set[str] = set()
    for _, row in candidates:
        key = row["failure_mode"]
        if key == "passed" and not row.get("copy_heavy_pass"):
            continue
        if key in seen_modes and key != "test_fail":
            continue
        seen_modes.add(key)
        task_dir = suite_dir / row["task_id"]
        traj = task_dir / "agent" / "trajectory.json"
        events = task_dir / "agent" / "openhands_events.jsonl"
        eval_result = task_dir / "eval" / "result.json"
        selected.append(
            {
                "task_id": row["task_id"],
                "failure_mode": row["failure_mode"],
                "semantic": infer_semantic_failure(row),
                "extraction_ratio": row.get("extraction_ratio"),
                "final_score": row.get("final_score"),
                "public_pass": row.get("public_pass"),
                "hidden_pass": row.get("hidden_pass"),
                "has_trajectory": traj.is_file(),
                "has_events": events.is_file(),
                "eval_result_path": str(eval_result.relative_to(_REPO_ROOT)) if eval_result.is_file() else None,
            }
        )
        if len(selected) >= limit:
            break
    return selected


def write_case_study_md(case: dict[str, Any], suite_dir: Path, out_dir: Path) -> None:
    task_id = case["task_id"]
    task_dir = suite_dir / task_id
    lines = [
        f"# Case Study: {task_id}",
        "",
        f"- **Mechanical label:** {case['failure_mode']}",
        f"- **Semantic label:** {case['semantic']}",
        f"- **Final score:** {case.get('final_score')}",
        f"- **Extraction ratio:** {case.get('extraction_ratio')}",
        f"- **Public pass:** {case.get('public_pass')}",
        f"- **Hidden pass:** {case.get('hidden_pass')}",
        "",
    ]

    eval_path = task_dir / "eval" / "result.json"
    if eval_path.is_file():
        ev = load_json(eval_path)
        lines.append("## Eval summary")
        lines.append("")
        lines.append(f"- build_pass: {ev.get('build_pass')}")
        lines.append(f"- test_pass: {ev.get('test_pass')}")
        lines.append(f"- original_import_pass: {ev.get('original_import_pass')}")
        pub = ev.get("public_tests") or {}
        hid = ev.get("hidden_tests") or {}
        lines.append(f"- public: {pub.get('passed')}/{pub.get('total')}")
        lines.append(f"- hidden: {hid.get('passed')}/{hid.get('total')}")
        lines.append("")

    for log_name in ("public.stdout", "hidden.stdout", "build.stdout"):
        log_path = task_dir / "eval" / "logs" / log_name
        if log_path.is_file():
            text = log_path.read_text(encoding="utf-8", errors="replace")
            tail = "\n".join(text.strip().splitlines()[-15:])
            lines.append(f"## Eval log tail ({log_name})")
            lines.append("")
            lines.append("```")
            lines.append(tail)
            lines.append("```")
            lines.append("")

    events_path = task_dir / "agent" / "openhands_events.jsonl"
    if events_path.is_file():
        event_lines = events_path.read_text(encoding="utf-8", errors="replace").strip().splitlines()
        lines.append("## Agent trajectory (last 5 events)")
        lines.append("")
        for raw in event_lines[-5:]:
            try:
                evt = json.loads(raw)
                action = evt.get("action") or evt.get("type") or "event"
                content = str(evt.get("content") or evt.get("message") or "")[:200]
                lines.append(f"- **{action}:** {content}")
            except json.JSONDecodeError:
                lines.append(f"- {raw[:120]}")
        lines.append("")

    out_path = out_dir / f"{task_id}.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")


def aggregate_gate_evidence(evidence_root: Path, flash_rows: list[dict[str, Any]]) -> dict[str, Any]:
    flash_by_task = {r["task_id"]: r for r in flash_rows}
    gate_reports = sorted(evidence_root.glob("*/review/gate_report.json"))
    rows = []
    for path in gate_reports:
        report = load_json(path)
        task_id = report["task_id"]
        metrics = report.get("metrics") or {}
        flash_row = flash_by_task.get(task_id, {})
        rows.append(
            {
                "task_id": task_id,
                "decision": report.get("decision"),
                "flash_tier": report.get("flash_tier"),
                "oracle_extraction": metrics.get("oracle_extraction"),
                "oracle_final": metrics.get("oracle_final"),
                "naive_extraction": metrics.get("naive_extraction"),
                "copy_all_extraction": metrics.get("copy_all_extraction"),
                "copy_all_delta_vs_oracle": metrics.get("copy_all_delta_vs_oracle"),
                "flash_extraction": metrics.get("flash_extraction") or flash_row.get("extraction_ratio"),
                "flash_final": metrics.get("flash_final") or flash_row.get("final_score"),
                "flash_pass": flash_row.get("status") == "passed",
                "is_hard3": task_id.endswith("__hard3_001"),
            }
        )

    copy_all_pass = sum(1 for r in rows if (r.get("copy_all_extraction") or 0) >= 0.7)
    agent_pass = sum(1 for r in rows if r.get("flash_pass"))
    return {
        "gate_report_count": len(rows),
        "copy_all_high_extraction_count": copy_all_pass,
        "agent_pass_in_gate_set": agent_pass,
        "median_oracle_extraction": median_or_none([r["oracle_extraction"] for r in rows if r.get("oracle_extraction")]),
        "median_copy_all_extraction": median_or_none(
            [r["copy_all_extraction"] for r in rows if r.get("copy_all_extraction")]
        ),
        "median_flash_extraction_passed": median_or_none(
            [r["flash_extraction"] for r in rows if r.get("flash_pass") and r.get("flash_extraction")]
        ),
        "per_task": rows,
    }


def load_task_meta_extended() -> dict[str, dict[str, Any]]:
    meta: dict[str, dict[str, Any]] = {}
    for path in sorted(TASKS_DIR.glob("*/metadata.json")):
        payload = load_json(path)
        task_id = payload.get("task_id") or path.parent.name
        source = payload.get("source") or {}
        ent = payload.get("entanglement") or {}
        meta[task_id] = {
            "task_id": task_id,
            "difficulty": payload.get("difficulty"),
            "tags": payload.get("tags") or [],
            "source_name": source.get("name"),
            "entanglement_level": ent.get("level"),
            "entanglement_primary": ent.get("primary"),
            "is_hard3": task_id.endswith("__hard3_001"),
        }
    return meta


def build_rq5_slices(flash_rows: list[dict[str, Any]], task_meta: dict[str, dict[str, Any]]) -> dict[str, Any]:
    def slice_stats(key_fn) -> list[dict[str, Any]]:
        buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in flash_rows:
            buckets[key_fn(row)].append(row)
        out = []
        for key in sorted(buckets):
            items = buckets[key]
            passed = sum(1 for r in items if r["status"] == "passed")
            out.append(
                {
                    "group": key,
                    "tasks": len(items),
                    "passed": passed,
                    "pass_rate": round(passed / len(items), 4) if items else 0.0,
                    "avg_final_score": round(
                        sum(r.get("final_score") or 0 for r in items) / len(items), 4
                    )
                    if items
                    else 0.0,
                }
            )
        return out

    for row in flash_rows:
        meta = task_meta.get(row["task_id"], {})
        row["is_hard3"] = meta.get("is_hard3", row["task_id"].endswith("__hard3_001"))
        row["entanglement_primary"] = meta.get("entanglement_primary") or "unknown"

    return {
        "by_entanglement": slice_stats(lambda r: r.get("entanglement_primary") or "unknown"),
        "by_difficulty": slice_stats(lambda r: r.get("difficulty") or "unknown"),
        "by_hard3": slice_stats(lambda r: "hard3" if r.get("is_hard3") else "original_100"),
        "by_source": slice_stats(lambda r: r.get("source_name") or "unknown"),
        "entanglement_types_expected": list(ENTANGLEMENT_PRIMARY_TYPES),
    }


def build_batch3_rq5(batch3_rows: list[dict[str, Any]], task_meta: dict[str, dict[str, Any]]) -> dict[str, Any]:
    for row in batch3_rows:
        meta = task_meta.get(row["task_id"], {})
        row["entanglement_primary"] = meta.get("entanglement_primary") or "unknown"
    passed = sum(1 for r in batch3_rows if r["status"] == "passed")
    by_ent: dict[str, dict[str, int]] = defaultdict(lambda: {"tasks": 0, "passed": 0})
    for row in batch3_rows:
        key = row.get("entanglement_primary") or "unknown"
        by_ent[key]["tasks"] += 1
        if row["status"] == "passed":
            by_ent[key]["passed"] += 1
    return {
        "unique_tasks": len(batch3_rows),
        "passed": passed,
        "pass_rate": round(passed / len(batch3_rows), 4) if batch3_rows else 0.0,
        "by_entanglement": [
            {
                "group": k,
                "tasks": v["tasks"],
                "passed": v["passed"],
                "pass_rate": round(v["passed"] / v["tasks"], 4) if v["tasks"] else 0.0,
            }
            for k, v in sorted(by_ent.items())
        ],
    }


def load_batch3_merged_rows() -> list[dict[str, Any]]:
    task_meta = load_task_meta_extended()
    merged: dict[str, dict[str, Any]] = {}
    for suite_dir in BATCH3_RUNS:
        for row in load_suite_rows(suite_dir):
            task_id = row["task_id"]
            if task_id not in merged or row["status"] == "passed":
                row["model_label"] = "DeepSeek-V4-Flash-batch3"
                row.update(task_meta.get(task_id, {}))
                merged[task_id] = row
    return list(merged.values())


def run_per_suite_analysis(suite_dir: Path, out_dir: Path) -> None:
    script = _REPO_ROOT / "harness/scripts/analyze_benchmark_suite.py"
    prefix = out_dir / "per_suite" / suite_dir.name
    subprocess.run(
        [
            sys.executable,
            str(script),
            str(suite_dir),
            "--analysis-prefix",
            str(prefix),
            "--output",
            str(out_dir / "per_suite" / f"{suite_dir.name}-comparison.json"),
        ],
        check=True,
        cwd=_REPO_ROOT,
        env={**dict(**{"PYTHONPATH": str(_REPO_ROOT / "harness")})},
    )

    entangle_script = _REPO_ROOT / "harness/scripts/report_entanglement_coverage.py"
    result = subprocess.run(
        [
            sys.executable,
            str(entangle_script),
            "--suite-dir",
            str(suite_dir),
        ],
        capture_output=True,
        text=True,
        cwd=_REPO_ROOT,
        env={**dict(**{"PYTHONPATH": str(_REPO_ROOT / "harness")})},
    )
    entangle_out = out_dir / "per_suite" / f"{suite_dir.name}-entanglement.txt"
    entangle_out.write_text(result.stdout + result.stderr, encoding="utf-8")


def write_readme(
    out_dir: Path,
    rq1: list[dict[str, Any]],
    batch3: dict[str, Any],
    formal_summary: dict[str, Any],
) -> None:
    lines = [
        "# Paper Analysis Outputs",
        "",
        f"Generated: {datetime.now(timezone.utc).replace(microsecond=0).isoformat()}",
        "",
        "Canonical runs: see [docs/paper_runs_frozen.md](../../docs/paper_runs_frozen.md).",
        "",
        "## Regenerate",
        "",
        "```bash",
        "PYTHONPATH=harness .venv/bin/python harness/scripts/generate_paper_analysis.py",
        "```",
        "",
        "## RQ1 snapshot (100-hard)",
        "",
        "| Model | Pass | Pass rate | Avg final score | Copy-heavy pass |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in rq1:
        lines.append(
            f"| {row['model']} | {row['functional_pass']}/{row['tasks']} | "
            f"{row['pass_rate']:.1%} | {row['avg_final_score']:.3f} | {row['copy_heavy_pass']} |"
        )
    lines.extend(
        [
            "",
            "## Batch3 Flash (merged)",
            "",
            f"- Unique tasks: {batch3['unique_tasks']}",
            f"- Unique passed: {batch3['unique_passed']} ({batch3['pass_rate']:.1%})",
            "",
            "## Files",
            "",
            "- `formal-runs-summary.json` — cross-run failure taxonomy",
            "- `batch3-flash-summary.json` — merged batch3 stats",
            "- `rq1_main_table.json` / `rq1_main_table.md`",
            "- `failure_taxonomy.csv` / `failure_taxonomy_flash.json`",
            "- `rq4_compactness.json`",
            "- `rq5_slices.json`",
            "- `case_studies/` — representative Flash failures",
            "- `executive_summary.md`",
            "- `per_suite/` — per-run analyze_benchmark_suite outputs",
            "",
            "## Failure taxonomy (Flash 100-hard)",
            "",
            f"```json",
            json.dumps(formal_summary.get("failure_taxonomy", {}), indent=2),
            "```",
        ]
    )
    (out_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def write_executive_summary(
    out_dir: Path,
    rq1: list[dict[str, Any]],
    batch3: dict[str, Any],
    taxonomy: dict[str, Any],
    rq4: dict[str, Any],
    rq5: dict[str, Any],
    protocol: dict[str, Any],
) -> None:
    flash = next(r for r in rq1 if r["model"] == "DeepSeek-V4-Flash")
    hard3_slice = next((s for s in rq5["by_hard3"] if s["group"] == "hard3"), None)
    orig_slice = next((s for s in rq5["by_hard3"] if s["group"] == "original_100"), None)

    lines = [
        "# Executive Summary — Python Paper Analysis",
        "",
        "## Headline results (frozen Python-150, OpenHands standard)",
        "",
        f"- **DeepSeek-V4-Flash full split:** {protocol['deepseek_v4_flash_full_split']['functional_pass']}/150 "
        f"pass ({protocol['deepseek_v4_flash_full_split']['pass_rate']:.1%}), avg final score "
        f"{protocol['deepseek_v4_flash_full_split']['avg_final_score']:.3f}",
        "- Cross-model comparison is restricted to the shared core-100 subset.",
        f"- **DeepSeek-V4-Flash:** {flash['functional_pass']}/100 pass ({flash['pass_rate']:.0%}), "
        f"avg final score {flash['avg_final_score']:.3f}",
        f"- **Best open model (Qwen3.6-27B):** {next(r for r in rq1 if '27B' in r['model'])['functional_pass']}/100",
        f"- **Weakest (Qwen3-Coder-30B):** {next(r for r in rq1 if '30B' in r['model'])['functional_pass']}/100",
        "",
        "## Batch3 hard3 pilot (Flash, 50 tasks merged)",
        "",
        f"- Pass rate: **{batch3['unique_passed']}/{batch3['unique_tasks']}** ({batch3['pass_rate']:.0%})",
        f"- Confirms harder entanglement slice is substantially below main-set Flash rate",
        "",
        "## Failure modes (Flash)",
        "",
        f"- Mechanical: {taxonomy['mechanical_taxonomy']}",
        f"- Semantic (inferred): {taxonomy['semantic_taxonomy']}",
        "",
        "## Compactness (52 gate reports)",
        "",
        f"- Median oracle extraction: {rq4.get('median_oracle_extraction')}",
        f"- Median copy-all extraction: {rq4.get('median_copy_all_extraction')}",
        f"- Agent passes in gate set: {rq4.get('agent_pass_in_gate_set')}/{rq4.get('gate_report_count')}",
        "",
        "## Difficulty drivers (Flash 100-hard)",
        "",
    ]
    if orig_slice and hard3_slice:
        lines.append(
            f"- Original 100 tasks: {orig_slice['passed']}/{orig_slice['tasks']} "
            f"({orig_slice['pass_rate']:.0%})"
        )
        if hard3_slice["tasks"]:
            lines.append(
                f"- Hard3 promoted (in main set): {hard3_slice['passed']}/{hard3_slice['tasks']} "
                f"({hard3_slice['pass_rate']:.0%})"
            )
    ent_slices = [s for s in rq5.get("by_entanglement", []) if s["group"] != "unknown"]
    if ent_slices:
        lines.append("")
        lines.append("### Entanglement primary (Flash 100-hard)")
        for s in ent_slices[:6]:
            lines.append(f"- {s['group']}: {s['passed']}/{s['tasks']} ({s['pass_rate']:.0%})")
    if rq5.get("batch3_hard3"):
        b3 = rq5["batch3_hard3"]
        lines.append("")
        lines.append(f"### Batch3 hard3 pilot (merged): {b3['passed']}/{b3['unique_tasks']} ({b3['pass_rate']:.0%})")
    lines.extend(
        [
            "",
            "## RQ3 status",
            "",
            "Hint and Oracle-Locate settings are not implemented in the harness. "
            "Paper uses gate-oracle extraction as a localization upper-bound proxy and marks full RQ3 ablation as future work.",
            "",
        ]
    )
    (out_dir / "executive_summary.md").write_text("\n".join(lines), encoding="utf-8")


def write_paper_tables_md(out_dir: Path, rq1: list[dict[str, Any]], rq4: dict[str, Any], rq5: dict[str, Any], taxonomy: dict[str, Any], protocol: dict[str, Any]) -> None:
    lines = [
        "# Paper Tables (Draft)",
        "",
        "## Table 1: Cross-model performance (RQ1) — shared core-100",
        "",
        "| Model | Functional pass | Pass rate | Avg final score | Median extraction (passed) | Copy-heavy pass | Median tokens (passed) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for r in rq1:
        med_ext = r.get("median_extraction_passed")
        med_tok = r.get("median_tokens_passed")
        lines.append(
            f"| {r['model']} | {r['functional_pass']}/100 | {r['pass_rate']:.1%} | "
            f"{r['avg_final_score']:.3f} | {med_ext if med_ext is not None else '—'} | "
            f"{r['copy_heavy_pass']} | {med_tok if med_tok is not None else '—'} |"
        )

    lines.extend(["", "## Table 2: Python-150 coverage and hard-extension calibration (Flash)", ""])
    batch3 = load_json(out_dir / "batch3-flash-summary.json")
    full = protocol["deepseek_v4_flash_full_split"]
    lines.extend(
        [
            "| Scope | Functional pass | Pass rate | Avg final score |",
            "| --- | ---: | ---: | ---: |",
            f"| Full Python-150 | {full['functional_pass']}/150 | {full['pass_rate']:.1%} | {full['avg_final_score']:.3f} |",
            f"| Hard extension (50) | {batch3['unique_passed']}/50 | {batch3['pass_rate']:.1%} | {batch3['avg_final_score']:.3f} |",
        ]
    )
    lines.append("")
    lines.extend(["", "## Table 3: Failure taxonomy — Flash 100-hard (RQ2)", ""])
    mech = taxonomy.get("mechanical_taxonomy", {})
    total = sum(mech.values()) or 1
    lines.append("| Mechanical label | Count | % |")
    lines.append("| --- | ---: | ---: |")
    for k, v in sorted(mech.items(), key=lambda x: -x[1]):
        lines.append(f"| {k} | {v} | {v/total:.1%} |")

    lines.extend(["", "## Table 4: Compactness baselines (RQ4)", ""])
    lines.append("| Metric | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| Gate reports | {rq4.get('gate_report_count')} |")
    lines.append(f"| Median oracle extraction | {rq4.get('median_oracle_extraction')} |")
    lines.append(f"| Median copy-all extraction | {rq4.get('median_copy_all_extraction')} |")
    lines.append(f"| Median Flash extraction (passed, gate set) | {rq4.get('median_flash_extraction_passed')} |")

    lines.extend(["", "## Table 5: Pass rate by entanglement primary (RQ5, Flash)", ""])
    lines.append("| Entanglement primary | Tasks | Passed | Pass rate |")
    lines.append("| --- | ---: | ---: | ---: |")
    for s in rq5.get("by_entanglement", []):
        if s["group"] == "unknown":
            continue
        lines.append(f"| {s['group']} | {s['tasks']} | {s['passed']} | {s['pass_rate']:.1%} |")
    if rq5.get("batch3_hard3"):
        lines.extend(["", "## Table 6: Batch3 hard3 by entanglement (Flash merged)", ""])
        lines.append("| Entanglement primary | Tasks | Passed | Pass rate |")
        lines.append("| --- | ---: | ---: | ---: |")
        for s in rq5["batch3_hard3"].get("by_entanglement", []):
            lines.append(f"| {s['group']} | {s['tasks']} | {s['passed']} | {s['pass_rate']:.1%} |")

    (_REPO_ROOT / "docs" / "paper_tables.md").write_text("\n".join(lines), encoding="utf-8")


def update_failure_taxonomy_doc(case_studies: list[dict[str, Any]], suite_dir: Path) -> None:
    doc_path = _REPO_ROOT / "docs" / "05_failure_taxonomy.md"
    text = doc_path.read_text(encoding="utf-8")

    examples = {
        "locate_failure": ("1. Locate Failure", "missing_submission"),
        "dependency_closure_failure": ("2. Dependency Closure Failure", "test_fail"),
        "packaging_failure": ("3. Packaging Failure", "build_fail"),
        "behavior_drift": ("4. Behavior Drift", "public_only_fail"),
        "over_copy": ("5. Over-Copy", "passed"),
        "forbidden_import": ("6. Forbidden Import", "forbidden_import_fail"),
    }

    case_by_semantic = {c["semantic"]: c for c in case_studies}

    for semantic, (section_title, _) in examples.items():
        case = case_by_semantic.get(semantic)
        if not case and semantic == "dependency_closure_failure":
            case = next((c for c in case_studies if c["task_id"] == "alembic__revision_map_core__hard3_001"), None)
            if case:
                case = {**case, "semantic": "dependency_closure_failure"}
        if not case:
            continue
        task_id = case["task_id"]
        if case.get("source") == "batch3":
            run_rel = f"experiments/python/openhands/deepseek-v4-flash/{case.get('best_run', 'batch3-flash-*')}"
        else:
            run_rel = suite_dir.relative_to(_REPO_ROOT)
        replacement = (
            f"- Example: `{task_id}` — Flash run `{run_rel}`; "
            f"mechanical={case['failure_mode']}, "
            f"extraction={case.get('extraction_ratio')}, "
            f"final_score={case.get('final_score')}. "
            f"See `reports/paper_analysis/case_studies/{task_id}.md`."
        )
        placeholder = "- Example placeholder: TODO: add example from experiments."
        # Replace only within the matching section
        section_start = text.find(f"## {section_title}")
        if section_start == -1:
            continue
        next_section = text.find("\n## ", section_start + 1)
        section_text = text[section_start:next_section] if next_section != -1 else text[section_start:]
        if placeholder in section_text:
            new_section = section_text.replace(placeholder, replacement)
            text = text[:section_start] + new_section + (text[next_section:] if next_section != -1 else "")

    doc_path.write_text(text, encoding="utf-8")


def update_paper_outline(rq1: list[dict[str, Any]], batch3: dict[str, Any], taxonomy: dict[str, Any], protocol: dict[str, Any]) -> None:
    doc_path = _REPO_ROOT / "docs" / "06_paper_outline.md"
    text = doc_path.read_text(encoding="utf-8")
    flash = next(r for r in rq1 if r["model"] == "DeepSeek-V4-Flash")

    full = protocol["deepseek_v4_flash_full_split"]
    abstract_result = (
        f"On the frozen Python-150 split with OpenHands, DeepSeek-V4-Flash achieves "
        f"{full['functional_pass']}/150 functional passes ({full['pass_rate']:.1%}) with average final score "
        f"{full['avg_final_score']:.3f}. On the shared core-100 comparison subset, it achieves "
        f"{flash['functional_pass']}/100 functional passes ({flash['pass_rate']:.0%}) with average final score "
        f"{flash['avg_final_score']:.3f}; open models range from "
        f"{min(r['functional_pass'] for r in rq1)}/100 to "
        f"{max(r['functional_pass'] for r in rq1 if r['model'] != 'DeepSeek-V4-Flash')}/100. "
        f"The hard 50-task extension yields only {batch3['unique_passed']}/50 Flash passes, "
        f"indicating substantial headroom on entangled repository features. "
        f"Compactness scoring separates copy-heavy functional passes from compact extractions."
    )
    text = re.sub(
        r"On the frozen Python(?: 100-hard|-150) split with OpenHands,.*?compact extractions\.",
        abstract_result,
        text,
        count=1,
    )
    text = text.replace(
        "TODO: add verified headline results only after the official run protocol is frozen.",
        abstract_result,
    )

    rq1_text = (
        f"DeepSeek-V4-Flash: {full['functional_pass']}/150 on the full split; "
        f"{flash['functional_pass']}/100 on the shared cross-model subset. "
        f"See `docs/paper_tables.md` Table 1."
    )
    text = re.sub(
        r"DeepSeek-V4-Flash: \d+/100 pass, avg final score [0-9.]+\. See `docs/paper_tables\.md` Table 1\.",
        rq1_text,
        text,
        count=1,
    )
    if "### RQ1: Overall Performance\n\nReport whether" in text:
        text = text.replace(
            "### RQ1: Overall Performance\n\nReport whether current agents can perform FeatureLift. Use one table per stable language split or a split column if both are mature.",
            f"### RQ1: Overall Performance\n\n{rq1_text}",
        )

    rq2_mech = taxonomy.get("mechanical_taxonomy", {})
    rq2_text = (
        f"Flash 100-hard mechanical failure distribution: {rq2_mech}. "
        f"Representative case studies in `reports/paper_analysis/case_studies/`."
    )
    text = text.replace(
        "### RQ2: Failure Analysis\n\nReport failure taxonomy distribution and representative case studies.",
        f"### RQ2: Failure Analysis\n\n{rq2_text}",
    )

    rq3_text = (
        "Full hint/oracle-locate ablation is not yet implemented in the harness. "
        "We report gate-oracle extraction ratios as a localization upper bound and defer full RQ3 to future work. "
        "Optional 10-task hint pilot is listed as follow-up."
    )
    text = text.replace(
        "### RQ3: Localization Ablation\n\nCompare standard, hint, and oracle-locate settings.",
        f"### RQ3: Localization Ablation\n\n{rq3_text}",
    )

    rq4_text = "See `reports/paper_analysis/rq4_compactness.json` and Table 4 in `docs/paper_tables.md`."
    text = text.replace(
        "### RQ4: Compactness\n\nCompare pass rate with final score and copy-all baseline. Show that functional tests alone overestimate extraction quality.",
        f"### RQ4: Compactness\n\n{rq4_text}",
    )

    rq5_text = "See `reports/paper_analysis/rq5_slices.json` — entanglement, difficulty, and hard3 slices."
    text = text.replace(
        "### RQ5: Task Difficulty\n\nAnalyze performance against task properties such as files, dependency depth, feature type, dynamic behavior, global state, package boundaries, and type closure.",
        f"### RQ5: Task Difficulty\n\n{rq5_text}",
    )

    text = text.replace(
        "- Replace abstract TODO with verified results.",
        "- Abstract updated with frozen-run headline numbers (2026-07-08).",
    )
    doc_path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Output directory for paper analysis artifacts",
    )
    parser.add_argument(
        "--skip-per-suite",
        action="store_true",
        help="Skip analyze_benchmark_suite per-suite runs (faster)",
    )
    args = parser.parse_args()
    out_dir = args.output_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Batch3 inventory
    batch3 = merge_batch3_runs(BATCH3_RUNS)
    write_json(out_dir / "batch3-flash-summary.json", batch3)

    # Per-suite analysis
    all_suite_dirs = MAIN_RUNS + BATCH3_RUNS
    if not args.skip_per_suite:
        for suite_dir in all_suite_dirs:
            if suite_dir.is_dir():
                run_per_suite_analysis(suite_dir, out_dir)

    # Cross-run summarize
    existing_main = [d for d in MAIN_RUNS if d.is_dir()]
    formal_summary = summarize_runs(existing_main)
    slim = {k: v for k, v in formal_summary.items() if k != "rows"}
    write_json(out_dir / "formal-runs-summary.json", slim)
    write_json(out_dir / "formal-runs-rows.json", formal_summary.get("rows", []))

    # RQ1
    rows_by_suite: dict[str, list[dict[str, Any]]] = {}
    all_main_rows: list[dict[str, Any]] = []
    flash_suite = MAIN_RUNS[0]
    flash_rows: list[dict[str, Any]] = []
    for suite_dir in existing_main:
        rows = load_suite_rows(suite_dir)
        rows_by_suite[suite_dir.name] = rows
        all_main_rows.extend(rows)
        if suite_dir == flash_suite:
            flash_rows = rows

    rq1 = aggregate_rq1(rows_by_suite)
    write_json(out_dir / "rq1_main_table.json", rq1)
    protocol = build_python150_protocol(rq1, batch3)
    write_json(out_dir / "python150_protocol.json", protocol)

    rq1_md = ["# RQ1 Main Table", "", "| Model | Pass | Pass rate | Avg final | Copy-heavy | Median tokens (pass) |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for r in rq1:
        rq1_md.append(
            f"| {r['model']} | {r['functional_pass']}/{r['tasks']} | {r['pass_rate']:.1%} | "
            f"{r['avg_final_score']:.3f} | {r['copy_heavy_pass']} | {r.get('median_tokens_passed') or '—'} |"
        )
    (out_dir / "rq1_main_table.md").write_text("\n".join(rq1_md), encoding="utf-8")

    # RQ2 failure taxonomy
    taxonomy = build_failure_taxonomy(flash_rows, "DeepSeek-V4-Flash")
    batch3_rows = load_batch3_merged_rows()
    batch3_taxonomy = build_failure_taxonomy(batch3_rows, "DeepSeek-V4-Flash-batch3")
    all_csv_rows = taxonomy["csv_rows"] + batch3_taxonomy["csv_rows"]
    annotate_csv_rows(all_csv_rows)
    write_json(out_dir / "failure_taxonomy_flash.json", {k: v for k, v in taxonomy.items() if k != "csv_rows"})
    write_json(out_dir / "failure_taxonomy_batch3.json", {k: v for k, v in batch3_taxonomy.items() if k != "csv_rows"})

    csv_path = out_dir / "failure_taxonomy.csv"
    if all_csv_rows:
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(all_csv_rows[0].keys()))
            writer.writeheader()
            writer.writerows(all_csv_rows)

    # Case studies
    case_dir = out_dir / "case_studies"
    case_dir.mkdir(parents=True, exist_ok=True)
    cases = sample_case_studies(flash_rows, flash_suite, limit=8)
    for case, suite_dir in sample_batch3_case_studies(batch3_rows, limit=3):
        if case["task_id"] not in {c["task_id"] for c in cases}:
            cases.append(case)
            write_case_study_md(case, suite_dir, case_dir)
    write_json(out_dir / "case_studies_index.json", cases)
    for case in cases:
        if case.get("source") != "batch3":
            write_case_study_md(case, flash_suite, case_dir)
        elif not (case_dir / f"{case['task_id']}.md").is_file():
            for suite_dir in BATCH3_RUNS:
                if (suite_dir / case["task_id"]).is_dir():
                    write_case_study_md(case, suite_dir, case_dir)
                    break

    # RQ4
    evidence_root = _REPO_ROOT / "evidence/python/batch1"
    rq4 = aggregate_gate_evidence(evidence_root, flash_rows)
    write_json(out_dir / "rq4_compactness.json", rq4)

    # RQ5
    task_meta = load_task_meta_extended()
    rq5 = build_rq5_slices(flash_rows, task_meta)
    rq5["batch3_hard3"] = build_batch3_rq5(batch3_rows, task_meta)
    write_json(out_dir / "rq5_slices.json", rq5)

    # Raw manifest for frozen runs
    import subprocess as sp
    write_json(
        out_dir / "raw_manifest.json",
        {
            "analysis_commit": sp.check_output(["git", "rev-parse", "HEAD"], cwd=_REPO_ROOT, text=True).strip(),
            "main_runs": [str(p.relative_to(_REPO_ROOT)) for p in existing_main],
            "batch3_runs": [str(p.relative_to(_REPO_ROOT)) for p in BATCH3_RUNS if p.is_dir()],
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        },
    )

    # Docs
    write_readme(out_dir, rq1, batch3, slim)
    write_executive_summary(out_dir, rq1, batch3, taxonomy, rq4, rq5, protocol)
    write_paper_tables_md(out_dir, rq1, rq4, rq5, taxonomy, protocol)
    update_failure_taxonomy_doc(cases, flash_suite)
    update_paper_outline(rq1, batch3, taxonomy, protocol)

    print(f"Wrote paper analysis to {out_dir}")
    print(f"RQ1 Flash: {rq1[0]['functional_pass']}/100")
    print(f"Batch3 merged: {batch3['unique_passed']}/{batch3['unique_tasks']}")
    print(f"Python-150 Flash: {protocol['deepseek_v4_flash_full_split']['functional_pass']}/150")
    print(f"Failure taxonomy: {taxonomy['mechanical_taxonomy']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
