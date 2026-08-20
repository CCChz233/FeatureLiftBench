#!/usr/bin/env python3
"""Compare Core-12 V2 Adaptive Budget vs live API Main and V1 (Main+2M).

Diagnostic only — not a Python-200 pass-rate estimate.
Does not write FINDINGS Python-200 tables.
"""

from __future__ import annotations

import json
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
DEFAULT_V1 = (
    ROOT
    / "experiments/methods/main_2m_cap"
    / "core12-deepseek-v4-flash-main-2m-cap-0817-001"
)
DEFAULT_V2 = (
    ROOT
    / "experiments/methods/adaptive_budget_v2"
    / "core12-deepseek-v4-flash-v2-0817-001"
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


def _checkpoint(base: Path, task_id: str) -> dict[str, Any]:
    path = base / task_id / "agent" / "v2_checkpoint.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def _sum(values: list[float | int | None]) -> int:
    return int(sum(v for v in values if isinstance(v, (int, float))))


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--v2-dir", type=Path, default=DEFAULT_V2)
    parser.add_argument("--v1-dir", type=Path, default=DEFAULT_V1)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    v2_dir: Path = args.v2_dir
    v1_dir: Path = args.v1_dir
    out_stem = args.out or (v2_dir / f"{v2_dir.name}-comparison")

    if not (v2_dir / "suite.json").exists():
        raise SystemExit(f"V2 suite missing: {v2_dir / 'suite.json'}")
    if not (v1_dir / "suite.json").exists():
        raise SystemExit(f"V1 suite missing: {v1_dir / 'suite.json'}")

    task_ids = _task_ids()
    v2_suite = _load_suite(v2_dir)
    v1_suite = _load_suite(v1_dir)
    missing = [tid for tid in task_ids if tid not in v2_suite]
    if missing:
        raise SystemExit(f"V2 suite missing tasks: {missing}")

    rows: list[dict[str, Any]] = []
    for tid in task_ids:
        main_dir = _find_main_dir(tid)
        main_suite = _load_suite(main_dir)
        main_row = main_suite[tid]
        v1_row = v1_suite[tid]
        v2_row = v2_suite[tid]
        main_res = _load_result(main_dir, tid)
        v1_res = _load_result(v1_dir, tid)
        v2_res = _load_result(v2_dir, tid)
        ckpt = _checkpoint(v2_dir, tid)
        rows.append(
            {
                "task_id": tid,
                "main_pass": _functional_pass(main_row, main_res),
                "v1_pass": _functional_pass(v1_row, v1_res),
                "v2_pass": _functional_pass(v2_row, v2_res),
                "main_usage": _usage(main_row),
                "v1_usage": _usage(v1_row),
                "v2_usage": _usage(v2_row),
                "extra_granted": bool(ckpt.get("granted_extra")),
                "checkpoint_decision": ckpt.get("decision"),
                "checkpoint_reason": ckpt.get("reason"),
            }
        )

    def token_total(key: str) -> int:
        return _sum([row[key].get("tokens") for row in rows])

    def step_median(key: str) -> float | None:
        vals = [
            float(row[key]["steps"])
            for row in rows
            if isinstance(row[key].get("steps"), (int, float))
        ]
        return _median(vals)

    main_n = sum(1 for row in rows if row["main_pass"])
    v1_n = sum(1 for row in rows if row["v1_pass"])
    v2_n = sum(1 for row in rows if row["v2_pass"])
    extra_n = sum(1 for row in rows if row["extra_granted"])
    extra_to_pass = sum(
        1 for row in rows if row["extra_granted"] and row["v2_pass"] and not row["v1_pass"]
    )

    # Go / no-go (diagnostic): tokens < V1 and Pass >= V1 - 1 → keep as cost arm.
    tokens_ok = token_total("v2_usage") < token_total("v1_usage")
    pass_ok = v2_n >= max(0, v1_n - 1)
    pass_much_worse = v2_n <= max(0, v1_n - 3)
    tokens_similar = abs(token_total("v2_usage") - token_total("v1_usage")) < max(
        1, int(0.05 * token_total("v1_usage"))
    )
    if pass_much_worse:
        decision = "loosen_or_raise_B_base"
        decision_note = (
            "Pass ≪ V1: early-stop may be killing converters; loosen checkpoint "
            "or raise B_base before any 200-run."
        )
    elif tokens_ok and pass_ok:
        decision = "keep_v2_cost_efficiency"
        decision_note = (
            "Token total < V1 and Pass ≥ V1 − 1: keep V2 as cost-efficiency arm; "
            "consider Python-200 later."
        )
    elif v2_n == v1_n and tokens_similar:
        decision = "stop_checkpoint_not_separating"
        decision_note = (
            "Pass ≈ V1 and tokens ≈ V1: checkpoint is not separating trajectories; "
            "stop, do not scale."
        )
    else:
        decision = "review_manually"
        decision_note = "Mixed Pass/token pattern; review per-task flips before scaling."

    headline = {
        "main_pass": main_n,
        "v1_pass": v1_n,
        "v2_pass": v2_n,
        "main_tokens": token_total("main_usage"),
        "v1_tokens": token_total("v1_usage"),
        "v2_tokens": token_total("v2_usage"),
        "main_steps_median": step_median("main_usage"),
        "v1_steps_median": step_median("v1_usage"),
        "v2_steps_median": step_median("v2_usage"),
        "extra_granted": extra_n,
        "extra_to_pass_vs_v1": extra_to_pass,
    }

    rescued_vs_v1 = [
        row["task_id"]
        for row in rows
        if row["v2_pass"] and not row["v1_pass"]
    ]
    lost_vs_v1 = [
        row["task_id"]
        for row in rows
        if row["v1_pass"] and not row["v2_pass"]
    ]

    payload = {
        "schema_version": "featureliftbench.adaptive_budget_v2_core12_comparison.v1",
        "diagnostic_suite": "rescue_plus_core12_v1",
        "n": len(rows),
        "v2_dir": str(v2_dir),
        "v1_dir": str(v1_dir),
        "decision": decision,
        "decision_note": decision_note,
        "headline": headline,
        "flips": {
            "v2_rescued_vs_v1": rescued_vs_v1,
            "v2_lost_vs_v1": lost_vs_v1,
            "net_vs_v1": len(rescued_vs_v1) - len(lost_vs_v1),
        },
        "rows": rows,
    }

    out_stem.parent.mkdir(parents=True, exist_ok=True)
    json_path = Path(str(out_stem) + ".json")
    md_path = Path(str(out_stem) + ".md")
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    h = headline
    lines = [
        f"# Core-12: V2 Adaptive Budget vs Main vs V1 (n={len(rows)})",
        "",
        "> Diagnostic suite only. Not a Python-200 pass-rate estimate.",
        "",
        f"- V2 run: `{v2_dir}`",
        f"- V1 (Main+2M) run: `{v1_dir}`",
        f"- Decision: **{decision}**",
        "",
        decision_note,
        "",
        "## Headline",
        "",
        "| Arm | Functional Pass | Tokens | Median steps | Extra granted | Extra→pass vs V1 |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
        f"| API Main | {h['main_pass']}/{len(rows)} | {h['main_tokens']:,} | {h['main_steps_median']} | — | — |",
        f"| V1 (Main+2M) | {h['v1_pass']}/{len(rows)} | {h['v1_tokens']:,} | {h['v1_steps_median']} | — | — |",
        f"| V2 Adaptive | {h['v2_pass']}/{len(rows)} | {h['v2_tokens']:,} | {h['v2_steps_median']} | {h['extra_granted']} | {h['extra_to_pass_vs_v1']} |",
        "",
        "## Paired flips vs V1",
        "",
        f"- V2 rescued vs V1: {len(rescued_vs_v1)}"
        + (f" ({', '.join(rescued_vs_v1)})" if rescued_vs_v1 else ""),
        f"- V2 lost vs V1: {len(lost_vs_v1)}"
        + (f" ({', '.join(lost_vs_v1)})" if lost_vs_v1 else ""),
        f"- Net vs V1: {len(rescued_vs_v1) - len(lost_vs_v1):+d}",
        "",
        "## Per-task",
        "",
        "| Task | Main | V1 | V2 | Extra | Decision | V2 tokens |",
        "| --- | :---: | :---: | :---: | :---: | --- | ---: |",
    ]
    for row in rows:
        lines.append(
            "| {task} | {main} | {v1} | {v2} | {extra} | {dec} | {tok} |".format(
                task=row["task_id"],
                main="Y" if row["main_pass"] else "N",
                v1="Y" if row["v1_pass"] else "N",
                v2="Y" if row["v2_pass"] else "N",
                extra="Y" if row["extra_granted"] else "N",
                dec=row.get("checkpoint_decision") or "—",
                tok=row["v2_usage"].get("tokens") or "—",
            )
        )
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"json": str(json_path), "md": str(md_path), "decision": decision}, indent=2))


if __name__ == "__main__":
    main()
