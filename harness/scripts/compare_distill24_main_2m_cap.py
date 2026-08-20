#!/usr/bin/env python3
"""Pair Core-12 Main+2M-cap against live API Main and Lite V1.

Diagnostic only — not a Python-200 pass-rate estimate.
Default task list is rescue_plus_core12_v1 (12 tasks).
"""

from __future__ import annotations

import json
import math
import statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
TASK_LIST = ROOT / "harness/config/experiments/rescue_plus_core12_v1.txt"
MAIN_150 = (
    ROOT
    / "experiments/FeatureLiftBench-v3-846-20260801-ready/experiments/export"
    / "FeatureLiftBench-deepseek-v4-flash-150-20260805/deepseek-v4-flash-0731"
)
MAIN_EXT50 = (
    ROOT
    / "experiments/python/openhands/deepseek-v4-flash"
    / "external50-deepseek-v4-flash-0805-main-001"
)
LITE_V1 = (
    ROOT
    / "experiments/python/openhands/deepseek-v4-flash"
    / "python200-deepseek-v4-flash-lite-v1-main-budget-0812-002"
)
DEFAULT_CAP = (
    ROOT
    / "experiments/methods/main_2m_cap"
    / "core12-deepseek-v4-flash-main-2m-cap-0817-001"
)


def _task_ids() -> list[str]:
    return [
        line.strip()
        for line in TASK_LIST.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def _load_suite(path: Path) -> dict[str, dict[str, Any]]:
    suite = json.loads((path / "suite.json").read_text(encoding="utf-8"))
    return {row["task_id"]: row for row in suite["runs"] if "task_id" in row}


def _find_main_dir(task_id: str) -> Path:
    for base in (MAIN_150, MAIN_EXT50):
        if (base / task_id / "eval" / "result.json").exists() or (
            base / task_id / "run.json"
        ).exists():
            return base
    raise FileNotFoundError(f"Main run missing for {task_id}")


def _functional_pass(suite_row: dict[str, Any], result: dict[str, Any] | None) -> bool:
    if result is not None:
        gate = (result.get("scores") or {}).get("functional_gate")
        if gate in (0, 0.0, 1, 1.0):
            return gate == 1.0
    return suite_row.get("final_score") == 1.0


def _load_result(base: Path, task_id: str) -> dict[str, Any] | None:
    path = base / task_id / "eval" / "result.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _usage(suite_row: dict[str, Any]) -> dict[str, Any]:
    usage = suite_row.get("agent_usage") or {}
    return {
        "steps": usage.get("assistant_steps"),
        "tokens": usage.get("total_tokens"),
        "prompt": usage.get("prompt_tokens"),
        "completion": usage.get("completion_tokens"),
    }


def _cap_hit(base: Path, task_id: str) -> bool:
    for rel in (
        "agent/usage.json",
        "agent/openhands_usage.json",
        "agent/context_audit.jsonl",
        "run.json",
    ):
        path = base / task_id / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if "token_budget_exhausted" in text or "featureliftbench_token_budget_exhausted" in text:
            return True
    return False


def _median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def _sum(values: list[float | int | None]) -> int:
    return int(sum(v for v in values if isinstance(v, (int, float))))


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cap-dir",
        type=Path,
        default=DEFAULT_CAP,
        help="Main+2M Distill-24 output directory",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Write JSON + markdown beside this path stem",
    )
    args = parser.parse_args()
    cap_dir: Path = args.cap_dir
    out_stem = args.out or (cap_dir / f"{cap_dir.name}-comparison")

    task_ids = _task_ids()
    cap_suite = _load_suite(cap_dir)
    lite_suite = _load_suite(LITE_V1)
    missing = [tid for tid in task_ids if tid not in cap_suite]
    if missing:
        raise SystemExit(f"Cap suite missing tasks: {missing}")

    rows: list[dict[str, Any]] = []
    for tid in task_ids:
        main_dir = _find_main_dir(tid)
        main_suite = _load_suite(main_dir)
        main_row = main_suite[tid]
        lite_row = lite_suite[tid]
        cap_row = cap_suite[tid]
        main_res = _load_result(main_dir, tid)
        lite_res = _load_result(LITE_V1, tid)
        cap_res = _load_result(cap_dir, tid)
        main_pass = _functional_pass(main_row, main_res)
        lite_pass = _functional_pass(lite_row, lite_res)
        cap_pass = _functional_pass(cap_row, cap_res)
        rows.append(
            {
                "task_id": tid,
                "main_pass": main_pass,
                "lite_pass": lite_pass,
                "cap_pass": cap_pass,
                "main_usage": _usage(main_row),
                "lite_usage": _usage(lite_row),
                "cap_usage": _usage(cap_row),
                "cap_hit": _cap_hit(cap_dir, tid),
            }
        )

    def count_pass(key: str) -> int:
        return sum(1 for row in rows if row[key])

    main_n = count_pass("main_pass")
    lite_n = count_pass("lite_pass")
    cap_n = count_pass("cap_pass")
    cap_hits = sum(1 for row in rows if row["cap_hit"])

    def token_total(key: str) -> int:
        return _sum(row[key]["tokens"] for row in rows)

    def step_median(key: str) -> float | None:
        vals = [
            float(row[key]["steps"])
            for row in rows
            if isinstance(row[key]["steps"], (int, float))
        ]
        return _median(vals)

    rescued_vs_lite = [
        row["task_id"]
        for row in rows
        if row["cap_pass"] and not row["lite_pass"]
    ]
    lost_vs_lite = [
        row["task_id"] for row in rows if row["lite_pass"] and not row["cap_pass"]
    ]
    rescued_vs_main = [
        row["task_id"]
        for row in rows
        if row["cap_pass"] and not row["main_pass"]
    ]
    lost_vs_main = [
        row["task_id"] for row in rows if row["main_pass"] and not row["cap_pass"]
    ]

    # Decision policy from the plan.
    keep_cap_kill_v1 = cap_n >= lite_n and token_total("cap_usage") < token_total(
        "main_usage"
    )
    cap_almost_free = cap_n >= main_n - 1  # near Main on this set
    checker_mattered = cap_n < lite_n - 1

    if keep_cap_kill_v1 and not checker_mattered:
        decision = "keep_cap_kill_v1_protocol"
        go_python200 = True
        rationale = (
            "Main+2M Pass ≥ current V1 and tokens stay below Main. "
            "Prefer Main+2M as the cost arm; retire V1 checker/stop/repair."
        )
    elif checker_mattered:
        decision = "checker_or_repair_may_matter"
        go_python200 = False
        rationale = (
            "Main+2M clearly worse than current V1 on Distill-24. "
            "Do not kill V1 yet; next arm is Main+2M+checker-as-linter "
            "(no stop language, no repair)."
        )
    else:
        decision = "inconclusive"
        go_python200 = False
        rationale = (
            "Pass/token pattern does not cleanly prefer Main+2M over V1. "
            "Hold Python-200; inspect per-task rows."
        )

    payload = {
        "schema_version": "featureliftbench.main_2m_cap_distill24_comparison.v1",
        "n_tasks": len(rows),
        "diagnostic_suite": "rescue_plus_core12_v1",
        "warning": (
            "Core-12 / Distill-24 are failure-enriched; do not report as "
            "Python-200 pass rate."
        ),
        "sources": {
            "cap_dir": str(cap_dir.relative_to(ROOT)),
            "main_150": str(MAIN_150.relative_to(ROOT)),
            "main_ext50": str(MAIN_EXT50.relative_to(ROOT)),
            "lite_v1": str(LITE_V1.relative_to(ROOT)),
        },
        "headline": {
            "main_pass": main_n,
            "lite_v1_pass": lite_n,
            "main_2m_pass": cap_n,
            "main_tokens": token_total("main_usage"),
            "lite_v1_tokens": token_total("lite_usage"),
            "main_2m_tokens": token_total("cap_usage"),
            "main_steps_median": step_median("main_usage"),
            "lite_v1_steps_median": step_median("lite_usage"),
            "main_2m_steps_median": step_median("cap_usage"),
            "main_2m_cap_hits": cap_hits,
        },
        "paired": {
            "cap_pass_lite_fail": rescued_vs_lite,
            "lite_pass_cap_fail": lost_vs_lite,
            "cap_pass_main_fail": rescued_vs_main,
            "main_pass_cap_fail": lost_vs_main,
            "net_vs_lite": len(rescued_vs_lite) - len(lost_vs_lite),
            "net_vs_main": len(rescued_vs_main) - len(lost_vs_main),
        },
        "decision": {
            "label": decision,
            "go_python200_cost_arm": go_python200,
            "keep_cap_kill_v1": keep_cap_kill_v1,
            "cap_almost_free_on_set": cap_almost_free,
            "checker_may_have_mattered": checker_mattered,
            "rationale": rationale,
        },
        "rows": rows,
    }

    out_stem.parent.mkdir(parents=True, exist_ok=True)
    json_path = out_stem.with_suffix(".json")
    md_path = out_stem.with_suffix(".md")
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    h = payload["headline"]
    d = payload["decision"]
    lines = [
        f"# Core-12: Main + 2M cap vs Main vs Lite V1 (n={len(rows)})",
        "",
        "> Diagnostic suite only. Not a Python-200 pass-rate estimate.",
        "",
        f"- Cap run: `{payload['sources']['cap_dir']}`",
        f"- Decision: **{d['label']}**",
        f"- Go Python-200 cost arm: **{d['go_python200_cost_arm']}**",
        "",
        d["rationale"],
        "",
        "## Headline",
        "",
        "| Arm | Functional Pass | Tokens | Median steps | Cap hits |",
        "| --- | ---: | ---: | ---: | ---: |",
        f"| API Main | {h['main_pass']}/{len(rows)} | {h['main_tokens']:,} | {h['main_steps_median']} | 0 |",
        f"| API Lite V1 | {h['lite_v1_pass']}/{len(rows)} | {h['lite_v1_tokens']:,} | {h['lite_v1_steps_median']} | — |",
        f"| Main + 2M | {h['main_2m_pass']}/{len(rows)} | {h['main_2m_tokens']:,} | {h['main_2m_steps_median']} | {h['main_2m_cap_hits']} |",
        "",
        "## Paired flips",
        "",
        f"- Cap rescued vs Lite: {len(rescued_vs_lite)} ({', '.join(rescued_vs_lite) or 'none'})",
        f"- Cap lost vs Lite: {len(lost_vs_lite)} ({', '.join(lost_vs_lite) or 'none'})",
        f"- Net vs Lite: {payload['paired']['net_vs_lite']:+d}",
        f"- Cap rescued vs Main: {len(rescued_vs_main)}",
        f"- Cap lost vs Main: {len(lost_vs_main)} ({', '.join(lost_vs_main) or 'none'})",
        f"- Net vs Main: {payload['paired']['net_vs_main']:+d}",
        "",
        "## Per-task",
        "",
        "| Task | Main | Lite V1 | Main+2M | Cap hit | Cap steps | Cap tokens |",
        "| --- | :---: | :---: | :---: | :---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| {task_id} | {m} | {l} | {c} | {hit} | {steps} | {tok} |".format(
                task_id=row["task_id"],
                m="Y" if row["main_pass"] else "N",
                l="Y" if row["lite_pass"] else "N",
                c="Y" if row["cap_pass"] else "N",
                hit="Y" if row["cap_hit"] else "N",
                steps=row["cap_usage"]["steps"],
                tok=row["cap_usage"]["tokens"],
            )
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(payload["headline"], indent=2))
    print("decision:", d["label"], "go_python200=", d["go_python200_cost_arm"])
    print("wrote", json_path)
    print("wrote", md_path)


if __name__ == "__main__":
    main()
