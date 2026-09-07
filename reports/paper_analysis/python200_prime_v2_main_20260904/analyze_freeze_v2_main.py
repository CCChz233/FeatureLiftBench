#!/usr/bin/env python3
"""Mechanical analysis of freeze-v2 Python-200' OpenHands Main runs.

Follows docs/paper/08_experimental_analysis_chapter.md sections 5.1–5.2.1, 5.4, 5.5.
Does not assign semantic contract-closure labels (5.3).
"""

from __future__ import annotations

import csv
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
FREEZE_PATH = ROOT / "artifacts/research_analysis/python200_prime/current_benchmark_freeze.json"
TAXONOMY_PATH = ROOT / "artifacts/research_analysis/python200_hard_task_taxonomy.csv"
TASK_ROOT = ROOT / "benchmark/python200_hard_tasks"

RUNS = [
    {
        "key": "deepseek_v4_flash",
        "label": "DeepSeek V4 Flash",
        "table_label": "DeepSeek V4 Flash",
        "dir": ROOT / "experiments/python/openhands/deepseek-v4-flash/python200-prime-v2-main-r1",
    },
    {
        "key": "gpt_5_6_luna_openlux",
        "label": "gpt-5.6-luna (OpenLux)",
        "table_label": "gpt-5.6-luna (OpenLux)",
        "dir": ROOT / "experiments/python/openhands/gpt-5.6-luna/python200-prime-v2-main-r1",
    },
    {
        "key": "qwen3_6_35b",
        "label": "Qwen3.6-35B-A3B-FP8",
        "table_label": "Qwen3.6-35B-A3B-FP8",
        "dir": ROOT / "experiments/python/openhands/qwen3.6-35b-a3b-fp8/python200-prime-v2-main-r1",
    },
]

STAGE_ORDER = [
    "freeze_preflight_blocked",
    "missing_submission",
    "build",
    "public",
    "hidden",
    "isolation",
    "pass",
    "other",
]


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> list[float]:
    if total <= 0:
        return [0.0, 0.0]
    rate = successes / total
    denominator = 1 + z * z / total
    center = (rate + z * z / (2 * total)) / denominator
    margin = (
        z
        * math.sqrt(rate * (1 - rate) / total + z * z / (4 * total * total))
        / denominator
    )
    return [max(0.0, center - margin), min(1.0, center + margin)]


def rate_block(passed: int, total: int) -> dict[str, Any]:
    lo, hi = wilson_interval(passed, total)
    return {
        "passed": passed,
        "total": total,
        "rate": passed / total if total else None,
        "wilson_95": [lo, hi],
        "pct": round(100 * passed / total, 1) if total else None,
    }


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def freeze_blocked(run: dict[str, Any]) -> bool:
    errors = run.get("errors") or []
    return any("active benchmark freeze spec hash mismatch" in str(value) for value in errors)


def first_failure_stage(result: dict[str, Any] | None, run: dict[str, Any] | None = None) -> str:
    if run and freeze_blocked(run):
        return "freeze_preflight_blocked"
    if result is None:
        return "missing_submission"
    scores = result.get("scores") or {}
    gate = scores.get("functional_gate")
    if gate is None:
        gate = 1.0 if float(scores.get("final_score") or 0.0) >= 1.0 else 0.0
    if float(gate) >= 1.0:
        return "pass"
    if not result.get("build_pass"):
        return "build"
    if not result.get("public_tests_pass"):
        return "public"
    if not result.get("hidden_tests_pass"):
        return "hidden"
    if not result.get("isolation_pass"):
        return "isolation"
    return "other"


def process_flags(task_dir: Path, run: dict[str, Any], stage: str) -> dict[str, Any]:
    agent = run.get("agent") or {}
    rc = agent.get("returncode")
    events = task_dir / "agent" / "openhands_events.jsonl"
    infra = task_dir / "agent" / "openhands_infrastructure_error.json"
    tve_events = 0
    if events.is_file():
        tve_events = events.read_text(encoding="utf-8", errors="replace").count(
            "Error validating tool"
        )
    tve_infra = infra.is_file()
    missing = stage == "missing_submission"
    freeze = stage == "freeze_preflight_blocked"
    return {
        "returncode": rc,
        "timed_out_flag": bool(agent.get("timed_out")),
        "duration_seconds": agent.get("duration_seconds"),
        "tve_event_hits": tve_events,
        "tve_infra_file": tve_infra,
        "missing_submission": missing,
        "freeze_preflight_blocked": freeze,
        "empty_tve": missing and (rc == 86 or tve_events > 0 or tve_infra),
        "step_limited": rc == 123,
        "wall_timeout": rc == 124,
        "tve_returncode": rc == 86,
    }


def load_taxonomy(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["task_id"]: row for row in csv.DictReader(handle)}


def entanglement_level(task_id: str) -> str:
    meta_path = TASK_ROOT / task_id / "metadata.json"
    if not meta_path.is_file():
        return "unknown"
    meta = load_json(meta_path)
    level = ((meta.get("entanglement") or {}).get("level")) or "unknown"
    return str(level).strip().lower() or "unknown"


def collect_model(spec: dict[str, Any], freeze_tasks: dict[str, Any], taxonomy: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    suite_dir: Path = spec["dir"]
    rows = []
    for task_id, freeze_row in freeze_tasks.items():
        task_dir = suite_dir / task_id
        run_path = task_dir / "run.json"
        result_path = task_dir / "eval" / "result.json"
        run = load_json(run_path) if run_path.is_file() else {}
        result = load_json(result_path) if result_path.is_file() else None
        scores = (result or {}).get("scores") or {}
        compactness = (result or {}).get("compactness") or {}
        stage = first_failure_stage(result, run)
        gate = scores.get("functional_gate")
        if gate is None:
            functional_pass = stage == "pass"
        else:
            functional_pass = float(gate) >= 1.0
        tax = taxonomy.get(task_id, {})
        proc = process_flags(task_dir, run, stage)
        rres = scores.get("reference_relative_loc_ratio")
        rows.append(
            {
                "task_id": task_id,
                "model_key": spec["key"],
                "stratum": freeze_row.get("stratum") or "unknown",
                "lift_type": tax.get("lift_type") or "unknown",
                "feature_family": tax.get("feature_family_v2") or "unknown",
                "entanglement_level": entanglement_level(task_id),
                "run_status": run.get("status") or ("missing_run_json" if not run else "unknown"),
                "functional_pass": functional_pass,
                "failure_stage": stage,
                "build_pass": None if result is None else bool(result.get("build_pass")),
                "public_pass": None if result is None else bool(result.get("public_tests_pass")),
                "hidden_pass": None if result is None else bool(result.get("hidden_tests_pass")),
                "isolation_pass": None if result is None else bool(result.get("isolation_pass")),
                "rres": None if rres is None else float(rres),
                "copied_fraction": compactness.get("copied_fraction"),
                "compactness_class": compactness.get("compactness_class"),
                "submitted_loc": compactness.get("submitted_loc"),
                **proc,
            }
        )
    return rows


def median(values: list[float]) -> float | None:
    clean = [float(v) for v in values if v is not None]
    return statistics.median(clean) if clean else None


def grouped_pass(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[str(row.get(key) or "unknown")].append(row)
    out = {}
    for name, group in sorted(buckets.items()):
        passed = sum(1 for r in group if r["functional_pass"])
        out[name] = rate_block(passed, len(group))
    return out


def summarize_model(rows: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(rows)
    launched = [r for r in rows if not r["freeze_preflight_blocked"]]
    passed = [r for r in rows if r["functional_pass"]]
    artifact_fail = [
        r
        for r in rows
        if (not r["functional_pass"])
        and not r["missing_submission"]
        and not r["freeze_preflight_blocked"]
    ]
    stages = Counter(r["failure_stage"] for r in rows)
    return {
        "n": n,
        "overall": rate_block(len(passed), n),
        "eligible": rate_block(sum(1 for r in launched if r["functional_pass"]), len(launched)),
        "eligible_by_stratum": grouped_pass(launched, "stratum"),
        "strict_run_passed": sum(1 for r in rows if r["run_status"] == "passed"),
        "by_stratum": grouped_pass(rows, "stratum"),
        "by_lift_type": grouped_pass(rows, "lift_type"),
        "by_entanglement_level": grouped_pass(rows, "entanglement_level"),
        "failure_stage": {k: stages.get(k, 0) for k in STAGE_ORDER},
        "failure_stage_share": {
            k: round(stages.get(k, 0) / n, 4) if n else None for k in STAGE_ORDER
        },
        "process": {
            "freeze_preflight_blocked": sum(1 for r in rows if r["freeze_preflight_blocked"]),
            "missing_submission": sum(1 for r in rows if r["missing_submission"]),
            "empty_tve": sum(1 for r in rows if r["empty_tve"]),
            "tve_returncode_86": sum(1 for r in rows if r["tve_returncode"]),
            "tve_returncode_86_but_pass": sum(
                1 for r in rows if r["tve_returncode"] and r["functional_pass"]
            ),
            "step_limited": sum(1 for r in rows if r["step_limited"]),
            "step_limited_but_pass": sum(
                1 for r in rows if r["step_limited"] and r["functional_pass"]
            ),
            "wall_timeout": sum(1 for r in rows if r["wall_timeout"]),
            "wall_timeout_but_pass": sum(
                1 for r in rows if r["wall_timeout"] and r["functional_pass"]
            ),
            "artifact_level_failures": len(artifact_fail),
            "artifact_fail_stage": dict(Counter(r["failure_stage"] for r in artifact_fail)),
        },
        "rres_pass_only": {
            "n": len(passed),
            "median": median([r["rres"] for r in passed if r["rres"] is not None]),
            "copied_fraction_median": median(
                [r["copied_fraction"] for r in passed if r["copied_fraction"] is not None]
            ),
            "by_stratum_median": {
                stratum: median(
                    [
                        r["rres"]
                        for r in passed
                        if r["stratum"] == stratum and r["rres"] is not None
                    ]
                )
                for stratum in ("python150", "hard50")
            },
        },
    }


def pct(x: float | None) -> str:
    return "—" if x is None else f"{100 * x:.1f}%"


def fmt_ci(block: dict[str, Any]) -> str:
    lo, hi = block["wilson_95"]
    return f"{block['passed']}/{block['total']} ({block['pct']:.1f}%; {100*lo:.1f}–{100*hi:.1f})"


def write_readout(payload: dict[str, Any]) -> str:
    models = payload["models"]
    ds = models["deepseek_v4_flash"]
    luna = models["gpt_5_6_luna_openlux"]
    qwen = models["qwen3_6_35b"]
    agree = payload["cross_model"]
    lines = []
    a = lines.append
    a("# Python-200′ freeze v2 OpenHands Main — mechanical readout")
    a("")
    a("> **Status: analysis snapshot · Generated: 2026-09-04**  ")
    a("> Follows [08_experimental_analysis_chapter.md](../../../docs/paper/08_experimental_analysis_chapter.md).  ")
    a("> **5.3 semantic taxonomy is not done.** Findings 1–2 and 5 can be drafted; Finding 3 cannot.")
    a("")
    a("Freeze `" + payload["freeze_id"] + "`, candidate `212930ea`, protocol Full-Repository / No-Hint.")
    a("GLM-5.3-Flash is excluded (incomplete). Do not mix with freeze `474862c2` 132/200.")
    a("")
    a("## 5.1 Overall Capability")
    a("")
    a("We evaluate all three completed model–agent configurations on the frozen Python-200′ suite under the same Full-Repository / No-Hint protocol.")
    a("")
    a("| Model | Functional Pass@1 | Python-150 | Hard-50 | Wilson 95% CI (200) |")
    a("| --- | ---: | ---: | ---: | --- |")
    for key in ("deepseek_v4_flash", "gpt_5_6_luna_openlux", "qwen3_6_35b"):
        m = models[key]
        o = m["overall"]
        s150 = m["by_stratum"]["python150"]
        s50 = m["by_stratum"]["hard50"]
        lo, hi = o["wilson_95"]
        a(
            f"| {payload['labels'][key]} | **{o['passed']}/{o['total']} ({o['pct']:.1f}%)** "
            f"| {s150['passed']}/{s150['total']} ({s150['pct']:.1f}%) "
            f"| {s50['passed']}/{s50['total']} ({s50['pct']:.1f}%) "
            f"| {100*lo:.1f}–{100*hi:.1f} |"
        )
    a("")
    a("**Assigned-200 vs launched-176.** The same **24 Python-150** tasks never launched on any model "
      "(`active benchmark freeze spec hash mismatch`). They are infrastructure, not agent failures. "
      "Protocol still records them as non-pass in the 200-row dump. Capability among launched tasks:")
    a("")
    a("| Model | Functional Pass on launched 176 | Python-150 launched (126) | Hard-50 (50) |")
    a("| --- | ---: | ---: | ---: |")
    for key in ("deepseek_v4_flash", "gpt_5_6_luna_openlux", "qwen3_6_35b"):
        m = models[key]
        e = m["eligible"]
        e150 = m["eligible_by_stratum"]["python150"]
        e50 = m["eligible_by_stratum"]["hard50"]
        a(
            f"| {payload['labels'][key]} | **{e['passed']}/{e['total']} ({e['pct']:.1f}%)** "
            f"| {e150['passed']}/{e150['total']} ({e150['pct']:.1f}%) "
            f"| {e50['passed']}/{e50['total']} ({e50['pct']:.1f}%) |"
        )
    a("")
    a("Strict `run.status=passed` is not the paper metric: "
      f"DeepSeek {ds['strict_run_passed']}/200, Luna {luna['strict_run_passed']}/200, "
      f"Qwen {qwen['strict_run_passed']}/200.")
    a("")
    unsolved_ds = 200 - ds["overall"]["passed"]
    gap_qwen = ds["overall"]["pct"] - qwen["overall"]["pct"]
    a("**Ceiling.** On the assigned 200, DeepSeek solves "
      f"{ds['overall']['pct']:.1f}% (**{unsolved_ds}** non-passes, of which 24 never launched). "
      f"On the 176 launched tasks it reaches {ds['eligible']['pct']:.1f}%. The suite is not saturated.")
    a("")
    a("**Discrimination.** DeepSeek exceeds Qwen by "
      f"**{gap_qwen:.1f} percentage points** on assigned 200 "
      f"({ds['overall']['passed']}/200 vs {qwen['overall']['passed']}/200; "
      f"{ds['eligible']['pct']:.1f}% vs {qwen['eligible']['pct']:.1f}% on 176). "
      f"Luna (OpenLux) sits in between.")
    a("")
    a("**Hard-50 is not harder.** Even after removing the 24 Python-150 freeze blocks, "
      f"DeepSeek is {ds['eligible_by_stratum']['hard50']['pct']:.1f}% on Hard-50 vs "
      f"{ds['eligible_by_stratum']['python150']['pct']:.1f}% on launched Python-150; "
      f"Luna {luna['eligible_by_stratum']['hard50']['pct']:.1f}% vs "
      f"{luna['eligible_by_stratum']['python150']['pct']:.1f}%; "
      f"Qwen is essentially flat "
      f"({qwen['eligible_by_stratum']['hard50']['pct']:.1f}% vs "
      f"{qwen['eligible_by_stratum']['python150']['pct']:.1f}%). "
      "Do not write “all models drop on Hard-50.”")
    a("")
    a("> **Finding 1.** Current coding agents exhibit substantial but incomplete feature-lifting capability, with large performance differences across model backends. Absolute 200-row rates are pulled down by 24 shared freeze-preflight blocks.")
    a("")
    a("## 5.2 Failure Stage")
    a("")
    a("| Stage | DeepSeek | Luna (OpenLux) | Qwen |")
    a("| --- | ---: | ---: | ---: |")
    for stage in STAGE_ORDER:
        a(
            f"| {stage} | {ds['failure_stage'][stage]} | {luna['failure_stage'][stage]} | {qwen['failure_stage'][stage]} |"
        )
    a("")
    def behavioral_mass(m: dict[str, Any]) -> int:
        return m["failure_stage"]["public"] + m["failure_stage"]["hidden"]

    a(
        f"Build failures are thin for DeepSeek ({ds['failure_stage']['build']}) and Luna "
        f"({luna['failure_stage']['build']}); Qwen has {qwen['failure_stage']['build']} build fails plus "
        f"{qwen['failure_stage']['missing_submission']} post-launch empty submissions. "
        f"Isolation-only fails are rare (DeepSeek {ds['failure_stage']['isolation']}, "
        f"Luna {luna['failure_stage']['isolation']}, Qwen {qwen['failure_stage']['isolation']}). "
        f"The shared freeze_preflight_blocked row is {ds['failure_stage']['freeze_preflight_blocked']} on every model."
    )
    a("")
    ds_launched_fail = 176 - ds["eligible"]["passed"]
    a(
        f"On launched tasks, DeepSeek’s remaining fails are almost all behavioral: "
        f"public {ds['failure_stage']['public']} + hidden {ds['failure_stage']['hidden']} "
        f"(plus isolation {ds['failure_stage']['isolation']}) out of {ds_launched_fail} launched non-passes. "
        f"Luna: public {luna['failure_stage']['public']} + hidden {luna['failure_stage']['hidden']}. "
        "Qwen’s extra mass is post-launch missing_submission (TVE); interpret with §5.2.1."
    )
    a("")
    a("> **Finding 2.** For backends that reliably emit a package, functional failures concentrate at the behavioral gates (Public/Hidden) rather than Build or Isolation. Qwen’s headline distribution is not yet a behavioral-gate result until empty submissions are separated.")
    a("")
    a("## 5.2.1 Process vs capability")
    a("")
    a("| Process | DeepSeek | Luna | Qwen |")
    a("| --- | ---: | ---: | ---: |")
    a(f"| freeze spec mismatch (never launched) | {ds['process']['freeze_preflight_blocked']} | {luna['process']['freeze_preflight_blocked']} | {qwen['process']['freeze_preflight_blocked']} |")
    a(f"| missing_submission after launch | {ds['process']['missing_submission']} | {luna['process']['missing_submission']} | {qwen['process']['missing_submission']} |")
    a(f"| empty TVE (no package) | {ds['process']['empty_tve']} | {luna['process']['empty_tve']} | {qwen['process']['empty_tve']} |")
    a(f"| rc=86 TVE (any) | {ds['process']['tve_returncode_86']} | {luna['process']['tve_returncode_86']} | {qwen['process']['tve_returncode_86']} |")
    a(f"| rc=86 and Functional Pass | {ds['process']['tve_returncode_86_but_pass']} | {luna['process']['tve_returncode_86_but_pass']} | {qwen['process']['tve_returncode_86_but_pass']} |")
    a(f"| rc=123 step limit | {ds['process']['step_limited']} | {luna['process']['step_limited']} | {qwen['process']['step_limited']} |")
    a(f"| rc=123 and Pass | {ds['process']['step_limited_but_pass']} | {luna['process']['step_limited_but_pass']} | {qwen['process']['step_limited_but_pass']} |")
    a(f"| rc=124 timeout | {ds['process']['wall_timeout']} | {luna['process']['wall_timeout']} | {qwen['process']['wall_timeout']} |")
    a(f"| artifact-level fails (has package, gate=0) | {ds['process']['artifact_level_failures']} | {luna['process']['artifact_level_failures']} | {qwen['process']['artifact_level_failures']} |")
    a("")
    a(
        f"Qwen’s **{qwen['process']['missing_submission']}** post-launch empty submissions are empty-TVE "
        f"({qwen['process']['empty_tve']}/{qwen['process']['missing_submission']}). "
        f"Official assigned score remains **{qwen['overall']['passed']}/200**, not "
        f"{qwen['overall']['passed']}/{200 - qwen['process']['freeze_preflight_blocked'] - qwen['process']['missing_submission']}. "
        "The 28 TVE empties must not be cited as Hidden-semantic failures. "
        "The 24 freeze blocks are shared and are not Qwen-specific."
    )
    a("")
    a("DeepSeek records many rc=86 "
      f"({ds['process']['tve_returncode_86']}) but "
      f"**{ds['process']['tve_returncode_86_but_pass']} still Functional Pass**. "
      f"Luna post-launch missing_submission is {luna['process']['missing_submission']} "
      "(encrypted-content retry recovered empties).")
    a("")
    a("> Process failures materially affect Qwen (empty TVE) and inflate DeepSeek’s non-zero return codes, but they are analytically distinct from artifact-level feature-lifting failures.")
    a("")
    a("## 5.3 Failure Mechanism")
    a("")
    a("**Not computed.** Semantic labels require artifact/trajectory coding on the artifact-level failure sets "
      f"(DeepSeek {ds['process']['artifact_level_failures']}, Luna {luna['process']['artifact_level_failures']}, "
      f"Qwen {qwen['process']['artifact_level_failures']}). Mechanical Public/Hidden counts are not a Contract-Closure Gap.")
    a("")
    a("Artifact-level first stages (denominator = has package ∧ gate=0):")
    a("")
    a("| Stage | DeepSeek | Luna | Qwen |")
    a("| --- | ---: | ---: | ---: |")
    for stage in ("build", "public", "hidden", "isolation", "other"):
        a(
            f"| {stage} | {ds['process']['artifact_fail_stage'].get(stage, 0)} "
            f"| {luna['process']['artifact_fail_stage'].get(stage, 0)} "
            f"| {qwen['process']['artifact_fail_stage'].get(stage, 0)} |"
        )
    a("")
    a("## 5.4 Task Difficulty")
    a("")
    a("### Lift type")
    a("")
    lift_keys = sorted(
        set(ds["by_lift_type"]) | set(luna["by_lift_type"]) | set(qwen["by_lift_type"])
    )
    a("| Lift type | DeepSeek | Luna | Qwen |")
    a("| --- | ---: | ---: | ---: |")
    for name in lift_keys:
        def cell(m: dict[str, Any]) -> str:
            b = m["by_lift_type"].get(name)
            return "—" if not b else f"{b['passed']}/{b['total']} ({b['pct']:.0f}%)"
        a(f"| {name} | {cell(ds)} | {cell(luna)} | {cell(qwen)} |")
    a("")
    a("### Entanglement level (`metadata.entanglement.level`)")
    a("")
    a("All 200 frozen tasks are labeled `high`. This field currently **does not discriminate** and must not be used for Finding 4.")
    a("")
    a("Lift type: Direct > Adapted > Composite on all three models (small Composite n=32). "
      "Hard-50 is *easier* than launched Python-150 for DeepSeek/Luna (§5.1), so “calibrated expansion is harder” is **not** supported by these Main runs.")
    a("")
    a("## 5.5 Extraction Quality (pass subset only)")
    a("")
    a("| Model | n pass | Median RRES | Median copied_fraction | RRES Python-150 | RRES Hard-50 |")
    a("| --- | ---: | ---: | ---: | ---: | ---: |")
    for key in ("deepseek_v4_flash", "gpt_5_6_luna_openlux", "qwen3_6_35b"):
        m = models[key]
        r = m["rres_pass_only"]
        def md(v: float | None) -> str:
            return "—" if v is None else f"{v:.3f}"
        a(
            f"| {payload['labels'][key]} | {r['n']} | {md(r['median'])} | {md(r['copied_fraction_median'])} "
            f"| {md(r['by_stratum_median']['python150'])} | {md(r['by_stratum_median']['hard50'])} |"
        )
    paired = payload["rres_paired_triple_pass"]
    a("")
    a(
        f"Paired subset where **all three** Functional Pass: n={paired['n']}, "
        f"median RRES DeepSeek={paired['median']['deepseek_v4_flash']}, "
        f"Luna={paired['median']['gpt_5_6_luna_openlux']}, "
        f"Qwen={paired['median']['qwen3_6_35b']}."
    )
    a("")
    a("> **Finding 5 (provisional).** Correctness and compactness are distinct: Functional Pass does not imply a compact extraction. Cross-model RRES rankings use only the triple-pass subset.")
    a("")
    a("## Cross-model agreement (task-level Functional Pass)")
    a("")
    a("The 24 freeze-blocked tasks appear in `D0L0Q0`. Launched-only all-fail is "
      f"{agree['all_fail'] - 24} tasks.")
    a("")
    a("| Pattern | Tasks |")
    a("| --- | ---: |")
    for k, v in agree["counts"].items():
        a(f"| {k} | {v} |")
    a("")
    a("## 5.6 Case Studies")
    a("")
    a("Not written. Candidate IDs (mechanical shortlist) are in `case_candidates.json`.")
    a("")
    a("## Next")
    a("")
    a("1. Code semantic labels on artifact-level failures (5.3).")
    a("2. Pick 3–4 cases from `case_candidates.json`.")
    a("3. Keep GLM-Flash off the main table until complete.")
    a("")
    return "\n".join(lines) + "\n"


def main() -> None:
    freeze = load_json(FREEZE_PATH)
    freeze_tasks = freeze["tasks"]
    taxonomy = load_taxonomy(TAXONOMY_PATH)
    assert len(freeze_tasks) == 200, len(freeze_tasks)

    all_rows: dict[str, list[dict[str, Any]]] = {}
    labels = {}
    models_out = {}
    for spec in RUNS:
        rows = collect_model(spec, freeze_tasks, taxonomy)
        if len(rows) != 200:
            raise SystemExit(f"{spec['key']} expected 200 rows, got {len(rows)}")
        all_rows[spec["key"]] = rows
        labels[spec["key"]] = spec["table_label"]
        models_out[spec["key"]] = summarize_model(rows)

    ds = {r["task_id"]: r for r in all_rows["deepseek_v4_flash"]}
    luna = {r["task_id"]: r for r in all_rows["gpt_5_6_luna_openlux"]}
    qwen = {r["task_id"]: r for r in all_rows["qwen3_6_35b"]}
    patterns = Counter()
    triple_pass = []
    qwen_tve_others_pass = []
    ds_hidden = []
    ds_public = []
    ds_iso = []
    ds_copy = []
    for tid in freeze_tasks:
        d, l, q = ds[tid], luna[tid], qwen[tid]
        key = (
            f"D{'1' if d['functional_pass'] else '0'}"
            f"L{'1' if l['functional_pass'] else '0'}"
            f"Q{'1' if q['functional_pass'] else '0'}"
        )
        patterns[key] += 1
        if d["functional_pass"] and l["functional_pass"] and q["functional_pass"]:
            triple_pass.append(tid)
        if q["empty_tve"] and d["functional_pass"] and l["functional_pass"]:
            qwen_tve_others_pass.append(tid)
        if d["failure_stage"] == "hidden":
            ds_hidden.append(tid)
        if d["failure_stage"] == "public":
            ds_public.append(tid)
        if d["failure_stage"] == "isolation":
            ds_iso.append(tid)
        if d["functional_pass"] and d.get("copied_fraction") is not None:
            ds_copy.append((d["copied_fraction"], tid))

    def med_rres(key: str) -> float | None:
        vals = []
        for tid in triple_pass:
            row = {"deepseek_v4_flash": ds, "gpt_5_6_luna_openlux": luna, "qwen3_6_35b": qwen}[key][tid]
            if row["rres"] is not None:
                vals.append(row["rres"])
        return median(vals)

    ds_copy.sort(reverse=True)
    payload = {
        "freeze_id": freeze["freeze_id"],
        "labels": labels,
        "models": models_out,
        "cross_model": {
            "counts": dict(patterns),
            "all_pass": patterns.get("D1L1Q1", 0),
            "all_fail": patterns.get("D0L0Q0", 0),
        },
        "rres_paired_triple_pass": {
            "n": len(triple_pass),
            "median": {
                "deepseek_v4_flash": med_rres("deepseek_v4_flash"),
                "gpt_5_6_luna_openlux": med_rres("gpt_5_6_luna_openlux"),
                "qwen3_6_35b": med_rres("qwen3_6_35b"),
            },
        },
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    with (OUT / "tasks.jsonl").open("w", encoding="utf-8") as handle:
        for spec in RUNS:
            for row in all_rows[spec["key"]]:
                handle.write(json.dumps(row, sort_keys=True) + "\n")
    candidates = {
        "qwen_empty_tve_but_deepseek_and_luna_pass": qwen_tve_others_pass[:8],
        "deepseek_hidden_first": ds_hidden[:8],
        "deepseek_public_first": ds_public[:8],
        "deepseek_isolation_first": ds_iso[:8],
        "deepseek_pass_highest_copied_fraction": [tid for _, tid in ds_copy[:8]],
        "triple_pass_sample": triple_pass[:8],
    }
    (OUT / "case_candidates.json").write_text(json.dumps(candidates, indent=2) + "\n")
    (OUT / "readout.md").write_text(write_readout(payload), encoding="utf-8")
    print(OUT / "readout.md")
    print(json.dumps({k: models_out[k]["overall"] for k in models_out}, indent=2))


if __name__ == "__main__":
    main()
