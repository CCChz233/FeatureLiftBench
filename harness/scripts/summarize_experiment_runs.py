#!/usr/bin/env python3
"""Join suite runs with task metadata; emit cross-run failure taxonomy and grouping stats."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))

from featureliftbench.paths import TASKS_DIR

HIGH_EXTRACTION_RATIO = 0.8
LOW_EXTRACTION_RATIO = 0.25


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_task_metadata() -> dict[str, dict[str, Any]]:
    meta: dict[str, dict[str, Any]] = {}
    for path in sorted(TASKS_DIR.glob("*/metadata.json")):
        payload = load_json(path)
        task_id = payload.get("task_id") or path.parent.name
        source = payload.get("source") or {}
        meta[task_id] = {
            "task_id": task_id,
            "difficulty": payload.get("difficulty"),
            "tags": payload.get("tags") or [],
            "source_name": source.get("name"),
            "entanglement_level": (payload.get("entanglement") or {}).get("level"),
        }
    return meta


def classify_failure(
    status: str,
    build_pass: bool | None,
    test_pass: bool | None,
    original_import_pass: bool | None,
    public_pass: bool | None,
    hidden_pass: bool | None,
) -> str:
    if status == "missing_submission":
        return "missing_submission"
    if status == "passed":
        return "passed"
    if build_pass is False:
        return "build_fail"
    if public_pass is True and hidden_pass is False:
        return "public_only_fail"
    if test_pass is False:
        return "test_fail"
    if original_import_pass is False:
        return "forbidden_import_fail"
    return "other_fail"


def enrich_task_run(suite_dir: Path, task_id: str, suite_entry: dict[str, Any]) -> dict[str, Any]:
    run_json = Path(suite_entry.get("run_json") or suite_dir / task_id / "run.json")
    detail = load_json(run_json) if run_json.is_file() else {}
    eval_path = Path(
        (detail.get("evaluation") or {}).get("result_json")
        or suite_dir / task_id / "eval" / "result.json"
    )
    eval_detail = load_json(eval_path) if eval_path.is_file() else {}

    scores = eval_detail.get("scores") or (detail.get("evaluation") or {}).get("scores") or {}
    metrics = eval_detail.get("metrics") or {}
    build_pass = eval_detail.get("build_pass", (detail.get("evaluation") or {}).get("build_pass"))
    test_pass = eval_detail.get("test_pass", (detail.get("evaluation") or {}).get("test_pass"))
    original_import_pass = eval_detail.get("original_import_pass")
    public_pass = (eval_detail.get("public_tests") or {}).get("passed")
    hidden_pass = (eval_detail.get("hidden_tests") or {}).get("passed")
    status = suite_entry.get("status") or detail.get("status")

    extraction_ratio = scores.get("extraction_ratio")
    functional_gate = scores.get("functional_gate")
    failure_mode = classify_failure(
        status, build_pass, test_pass, original_import_pass, public_pass, hidden_pass
    )

    usage = (detail.get("agent") or {}).get("usage") or suite_entry.get("agent_usage") or {}
    copy_heavy_pass = (
        status == "passed"
        and isinstance(extraction_ratio, (int, float))
        and extraction_ratio >= HIGH_EXTRACTION_RATIO
    )
    compact_pass = (
        status == "passed"
        and isinstance(extraction_ratio, (int, float))
        and extraction_ratio <= LOW_EXTRACTION_RATIO
    )

    return {
        "task_id": task_id,
        "suite_dir": suite_dir.name,
        "model_family": _model_family(suite_dir.name),
        "status": status,
        "failure_mode": failure_mode,
        "build_pass": build_pass,
        "test_pass": test_pass,
        "public_pass": public_pass,
        "hidden_pass": hidden_pass,
        "original_import_pass": original_import_pass,
        "functional_gate": functional_gate,
        "extraction_ratio": extraction_ratio,
        "final_score": scores.get("final_score", suite_entry.get("final_score")),
        "submission_loc": metrics.get("loc"),
        "source_loc": metrics.get("source_loc"),
        "copy_heavy_pass": copy_heavy_pass,
        "compact_pass": compact_pass,
        "total_tokens": usage.get("total_tokens"),
        "assistant_steps": usage.get("assistant_steps"),
        "agent_duration_seconds": (detail.get("agent") or {}).get("duration_seconds"),
    }


def _model_family(suite_name: str) -> str:
    if "gpt-oss" in suite_name:
        return "GPT-OSS-120B"
    if "qwen" in suite_name:
        return "Qwen3-Coder-30B"
    return "unknown"


def _rate(n: int, d: int) -> float:
    return round(n / d, 4) if d else 0.0


def _group_stats(rows: list[dict[str, Any]], key_fn) -> list[dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[key_fn(row)].append(row)
    out = []
    for key in sorted(buckets):
        items = buckets[key]
        total = len(items)
        passed = sum(1 for r in items if r["status"] == "passed")
        out.append(
            {
                "group": key,
                "attempts": total,
                "passed": passed,
                "pass_rate": _rate(passed, total),
                "failure_modes": dict(Counter(r["failure_mode"] for r in items)),
            }
        )
    return out


def _task_stability(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_task[row["task_id"]].append(row)

    result = []
    for task_id in sorted(by_task):
        items = by_task[task_id]
        statuses = [r["status"] for r in items]
        pass_count = statuses.count("passed")
        result.append(
            {
                "task_id": task_id,
                "attempts": len(items),
                "pass_count": pass_count,
                "pass_rate": _rate(pass_count, len(items)),
                "never_passed": pass_count == 0,
                "always_passed": pass_count == len(items) and len(items) >= 3,
                "by_model": {
                    model: sum(1 for r in items if r["model_family"] == model and r["status"] == "passed")
                    for model in sorted({r["model_family"] for r in items})
                },
            }
        )
    return result


def summarize(suite_dirs: list[Path]) -> dict[str, Any]:
    task_meta = load_task_metadata()
    rows: list[dict[str, Any]] = []

    for suite_dir in suite_dirs:
        suite_path = suite_dir / "suite.json"
        if not suite_path.is_file():
            raise FileNotFoundError(f"missing suite.json: {suite_path}")
        suite = load_json(suite_path)
        for entry in suite.get("runs") or []:
            task_id = entry.get("task_id", "")
            row = enrich_task_run(suite_dir, task_id, entry)
            row.update(task_meta.get(task_id, {}))
            rows.append(row)

    failure_taxonomy = dict(Counter(r["failure_mode"] for r in rows))
    by_model = _group_stats(rows, lambda r: r["model_family"])
    by_source = _group_stats(rows, lambda r: r.get("source_name") or "unknown")
    by_difficulty = _group_stats(rows, lambda r: r.get("difficulty") or "unknown")
    by_entanglement = _group_stats(rows, lambda r: r.get("entanglement_level") or "unknown")

    passed_rows = [r for r in rows if r["status"] == "passed"]
    copy_heavy = [r for r in passed_rows if r["copy_heavy_pass"]]
    compact = [r for r in passed_rows if r["compact_pass"]]
    public_only = [r for r in rows if r["failure_mode"] == "public_only_fail"]

    passed_tokens = sorted(r["total_tokens"] for r in passed_rows if isinstance(r["total_tokens"], (int, float)))
    failed_tokens = sorted(
        r["total_tokens"]
        for r in rows
        if r["status"] != "passed" and isinstance(r["total_tokens"], (int, float))
    )

    def median(values: list[int | float]) -> int | None:
        if not values:
            return None
        return values[len(values) // 2]

    stability = _task_stability(rows)
    never_passed = [t["task_id"] for t in stability if t["never_passed"]]
    always_passed_3plus = [t["task_id"] for t in stability if t["always_passed"]]
    unstable = [
        t["task_id"]
        for t in stability
        if 0 < t["pass_count"] < t["attempts"] and t["attempts"] >= 3
    ]

    both_models_pass_any = []
    task_by_id = {t["task_id"]: t for t in stability}
    for task_id, task in task_by_id.items():
        gpt = task["by_model"].get("GPT-OSS-120B", 0)
        qwen = task["by_model"].get("Qwen3-Coder-30B", 0)
        if gpt > 0 and qwen > 0:
            both_models_pass_any.append(task_id)

    return {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "suite_count": len(suite_dirs),
        "task_attempts": len(rows),
        "failure_taxonomy": failure_taxonomy,
        "failure_taxonomy_pct": {
            k: round(v / len(rows) * 100, 1) for k, v in failure_taxonomy.items()
        },
        "by_model": by_model,
        "by_source": by_source,
        "by_difficulty": by_difficulty,
        "by_entanglement": by_entanglement,
        "quality_breakdown": {
            "functional_passes": len(passed_rows),
            "copy_heavy_passes": len(copy_heavy),
            "compact_passes": len(compact),
            "public_only_failures": len(public_only),
            "copy_heavy_tasks": sorted({r["task_id"] for r in copy_heavy}),
            "compact_tasks": sorted({r["task_id"] for r in compact}),
        },
        "token_stats": {
            "passed_median": median(passed_tokens),
            "failed_median": median(failed_tokens),
        },
        "task_stability": {
            "never_passed": never_passed,
            "always_passed_3plus": always_passed_3plus,
            "unstable_3plus": unstable,
            "both_models_pass_any": sorted(both_models_pass_any),
            "per_task": stability,
        },
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suite_dirs", nargs="+", type=Path, help="Suite directories with suite.json")
    parser.add_argument(
        "--output",
        type=Path,
        default=_REPO_ROOT / "experiments" / "mini-swe-agent" / "formal-runs-summary.json",
        help="Output JSON path",
    )
    args = parser.parse_args()
    payload = summarize([path.resolve() for path in args.suite_dirs])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    slim = {k: v for k, v in payload.items() if k != "rows"}
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(slim, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(f"Wrote {args.output}")
    print("failure_taxonomy:", payload["failure_taxonomy"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
