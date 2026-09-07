#!/usr/bin/env python3
"""Mechanical Python-150 analysis of freeze v2 Official Main (python200-prime-v2-main-r1).

Follows docs/paper/08_experimental_analysis_chapter.md sections 5.1–5.5.
Hard-50 is excluded. Semantic 5.3 labels are not assigned from evaluator last lines.
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
TAXONOMY = ROOT / "artifacts/research_analysis/python200_hard_task_taxonomy.csv"
TASKS_ROOT = ROOT / "benchmark/python200_hard_tasks"

SUITES = {
    "deepseek-v4-pro": {
        "label": "DeepSeek V4 Pro",
        "short": "Pro",
        "dir": ROOT / "experiments/python/openhands/deepseek-v4-pro/python150-prime-v2-main-r1",
    },
    "deepseek-v4-flash": {
        "label": "DeepSeek V4 Flash",
        "short": "DeepSeek",
        "dir": ROOT / "experiments/python/openhands/deepseek-v4-flash/python200-prime-v2-main-r1",
    },
    "gpt-5.6-luna": {
        "label": "gpt-5.6-luna (OpenLux)",
        "short": "Luna",
        "dir": ROOT / "experiments/python/openhands/gpt-5.6-luna/python200-prime-v2-main-r1",
    },
    "glm-5.3-flash": {
        "label": "GLM-5.3-Flash",
        "short": "GLM",
        "dir": ROOT / "experiments/python/openhands/glm-5.3-flash/python200-prime-v2-main-r1",
    },
    "qwen3.6-35b-a3b-fp8": {
        "label": "Qwen3.6-35B-A3B-FP8",
        "short": "Qwen",
        "dir": ROOT / "experiments/python/openhands/qwen3.6-35b-a3b-fp8/python200-prime-v2-main-r1",
    },
    "gpt-oss-120b": {
        "label": "GPT-OSS 120B",
        "short": "GPT-OSS",
        "dir": ROOT / "experiments/python/openhands/gpt-oss-120b/python200-prime-v2-main-r1",
    },
}

EXPECTED_FREEZE_V2 = "6c20ff0307762503a73cbb9ff32e9992c6446e4b17483a68373027be58cbf419"
EXPECTED_IMAGE_TAG = "python200-prime-212930ea"
STAGE_ORDER = [
    "missing_submission",
    "build_failure",
    "public_failure",
    "hidden_failure",
    "isolation_failure",
    "functional_pass",
]
GATES = ["build_pass", "public_tests_pass", "hidden_tests_pass", "isolation_pass"]


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total <= 0:
        return (0.0, 0.0)
    rate = successes / total
    denom = 1 + z * z / total
    center = (rate + z * z / (2 * total)) / denom
    margin = z * math.sqrt(rate * (1 - rate) / total + z * z / (4 * total * total)) / denom
    return (max(0.0, center - margin), min(1.0, center + margin))


def pct(n: int, d: int) -> str:
    if d == 0:
        return "—"
    return f"{100.0 * n / d:.1f}%"


def rate_blob(passed: int, total: int) -> dict[str, Any]:
    lo, hi = wilson(passed, total)
    return {
        "passed": passed,
        "total": total,
        "rate": passed / total if total else None,
        "wilson_95": [lo, hi],
        "display": f"{passed}/{total} ({pct(passed, total)})",
        "wilson_display": f"{100 * lo:.1f}–{100 * hi:.1f}%",
    }


def median(values: list[float]) -> float | None:
    clean = [float(v) for v in values if v is not None]
    return statistics.median(clean) if clean else None


def quantile(values: list[float], q: float) -> float | None:
    clean = sorted(float(v) for v in values if v is not None)
    if not clean:
        return None
    if len(clean) == 1:
        return clean[0]
    idx = q * (len(clean) - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return clean[lo]
    w = idx - lo
    return clean[lo] * (1 - w) + clean[hi] * w


def load_taxonomy() -> dict[str, dict[str, str]]:
    rows = {}
    with TAXONOMY.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows[row["task_id"]] = row
    return rows


def submission_file_count(task_dir: Path) -> int:
    sub = task_dir / "submission"
    if not sub.exists():
        return 0
    return sum(1 for p in sub.rglob("*") if p.is_file())


def _positive_int(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = int(value)
    return number if number > 0 else None


def load_agent_usage(task_dir: Path) -> dict[str, Any]:
    """Prefer canonical usage.json written by the OpenHands runner."""

    for name in ("usage.json", "openhands_usage.json"):
        path = task_dir / "agent" / name
        if not path.is_file():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            payload = dict(payload)
            payload["_usage_source"] = name
            return payload
    return {}


def classify_process(task_dir: Path, run: dict[str, Any]) -> dict[str, Any]:
    flags: set[str] = set()
    details: list[str] = []
    infra_path = task_dir / "agent" / "openhands_infrastructure_error.json"
    if infra_path.is_file():
        try:
            infra = json.loads(infra_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            infra = {}
        fc = str(infra.get("failure_class") or "")
        err = str(infra.get("error") or "")
        if fc:
            flags.add(fc)
        if infra.get("promoted_to_process_failure"):
            flags.add("promoted_process_failure")
        low = (fc + " " + err).lower()
        if "security_risk" in low or "tool_validation_error" in low:
            flags.add("tve")
        if "invalid_encrypted" in low:
            flags.add("invalid_encrypted_content")
        if "timeout" in low or "timed out" in low:
            flags.add("timeout")
        details.append(err[:240])
    blob_parts = [str(x) for x in (run.get("errors") or [])]
    usage = load_agent_usage(task_dir)
    blob_parts.append(str(usage.get("exit_status") or ""))
    blob = " ".join(blob_parts).lower()
    if "security_risk" in blob:
        flags.add("tve")
    if "invalid_encrypted" in blob:
        flags.add("invalid_encrypted_content")
    if "timeout" in blob or "timed out" in blob:
        flags.add("timeout")
    if usage.get("token_budget_exhausted"):
        flags.add("token_budget")
    context = usage.get("context_audit") if isinstance(usage.get("context_audit"), dict) else {}
    completion = _positive_int(usage.get("completion_tokens"))
    uncached = _positive_int(usage.get("effective_uncached_prompt_tokens"))
    incremental = None
    if uncached is not None:
        incremental = uncached + (completion or 0)
    return {
        "flags": sorted(flags),
        "tve": "tve" in flags or "tool_validation_error" in flags,
        "invalid_encrypted": "invalid_encrypted_content" in flags,
        "timeout": "timeout" in flags,
        "promoted_process": "promoted_process_failure" in flags,
        "context_violation": bool(context.get("context_violation")),
        "usage_unverified": bool(context.get("usage_unverified")),
        "usage_source": usage.get("_usage_source"),
        "api_calls": usage.get("api_calls"),
        "assistant_steps": usage.get("assistant_steps"),
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "total_tokens": _positive_int(usage.get("total_tokens")),
        "effective_uncached_prompt_tokens": uncached,
        "incremental_tokens": incremental,
        "prompt_cache_accounting": bool(usage.get("prompt_cache_accounting_available")),
        "duration_seconds": usage.get("duration_seconds"),
        "detail": details[0] if details else (blob_parts[0][:240] if blob_parts else ""),
    }


def first_failure_stage(result: dict[str, Any] | None, usable_submission: bool) -> str:
    if not usable_submission or result is None:
        return "missing_submission"
    scores = result.get("scores") or {}
    functional = all(result.get(k) is True for k in GATES) or float(scores.get("final_score") or 0) >= 1.0
    if functional:
        return "functional_pass"
    if not result.get("build_pass"):
        return "build_failure"
    if not result.get("public_tests_pass"):
        return "public_failure"
    if not result.get("hidden_tests_pass"):
        return "hidden_failure"
    if not result.get("isolation_pass"):
        return "isolation_failure"
    return "other"


def freeze_id(run: dict[str, Any]) -> str:
    bf = run.get("benchmark_freeze") or {}
    if isinstance(bf, dict):
        return str(bf.get("freeze_id") or bf.get("id") or "")
    return str(bf or "")


def collect_row(model_key: str, task_id: str, tax: dict[str, str], meta: dict[str, Any]) -> dict[str, Any]:
    suite_dir = SUITES[model_key]["dir"]
    task_dir = suite_dir / task_id
    run_path = task_dir / "run.json"
    result_path = task_dir / "eval" / "result.json"
    run = json.loads(run_path.read_text(encoding="utf-8")) if run_path.is_file() else {}
    result = json.loads(result_path.read_text(encoding="utf-8")) if result_path.is_file() else None
    n_files = submission_file_count(task_dir)
    usable = n_files > 0
    process = classify_process(task_dir, run)
    scores = (result or {}).get("scores") or {}
    compactness = (result or {}).get("compactness") or {}
    functional = bool(result) and all(result.get(k) is True for k in GATES)
    stage = first_failure_stage(result, usable)
    ent = (meta.get("entanglement") or {}) if isinstance(meta, dict) else {}
    return {
        "model": model_key,
        "task_id": task_id,
        "suite_split": tax.get("suite_split"),
        "construction_split": tax.get("construction_split_150"),
        "hard3": tax.get("construction_split_150") == "hard50",
        "lift_type": tax.get("lift_type") or "unknown",
        "feature_family": tax.get("feature_family_v2") or "unknown",
        "entanglement_primary": ent.get("primary") or tax.get("entanglement_primary_original") or "unknown",
        "entanglement_level": ent.get("level") or "unknown",
        "has_run_json": run_path.is_file(),
        "has_result_json": result_path.is_file(),
        "submission_file_count": n_files,
        "usable_submission": usable,
        "functional_pass": functional,
        "first_failure_stage": stage,
        "run_status": run.get("status"),
        "freeze_id": freeze_id(run),
        "agent_docker_image": run.get("agent_docker_image") or "",
        "eval_docker_image": run.get("eval_docker_image") or "",
        "build_pass": None if result is None else bool(result.get("build_pass")),
        "public_pass": None if result is None else bool(result.get("public_tests_pass")),
        "hidden_pass": None if result is None else bool(result.get("hidden_tests_pass")),
        "isolation_pass": None if result is None else bool(result.get("isolation_pass")),
        "rres": scores.get("reference_relative_loc_ratio"),
        "extraction_ratio": scores.get("extraction_ratio"),
        "copied_fraction": compactness.get("copied_fraction"),
        "copied_loc": compactness.get("copied_loc"),
        "submitted_loc": compactness.get("submitted_loc"),
        "reference_loc": compactness.get("reference_loc"),
        "compactness_class": compactness.get("compactness_class"),
        "artifact_fail": usable and (not functional),
        **{f"process_{k}": process[k] for k in (
            "tve", "invalid_encrypted", "timeout", "promoted_process",
            "context_violation", "usage_unverified", "usage_source",
            "api_calls", "assistant_steps", "prompt_tokens", "completion_tokens",
            "total_tokens", "effective_uncached_prompt_tokens", "incremental_tokens",
            "prompt_cache_accounting", "duration_seconds", "detail",
        )},
        "process_flags": process["flags"],
    }


def summarize_token_usage(model_key: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Python-150 token/step diagnostics from usage.json. Not a leaderboard metric."""

    token_rows = [r for r in rows if r.get("process_total_tokens")]
    incremental = [float(r["process_incremental_tokens"]) for r in rows if r.get("process_incremental_tokens")]
    completion = [
        float(r["process_completion_tokens"])
        for r in rows
        if _positive_int(r.get("process_completion_tokens"))
    ]
    totals = [float(r["process_total_tokens"]) for r in token_rows]
    pass_totals = [float(r["process_total_tokens"]) for r in token_rows if r["functional_pass"]]
    note = (
        "total_tokens sums provider usage across API calls; for Pro/Flash this "
        "includes cached prompt tokens. incremental_tokens is uncached prompt + "
        "completion when cache accounting exists. Luna/GLM providers returned no "
        "token usage (usage_unverified); do not impute."
    )
    if model_key in {"gpt-5.6-luna", "glm-5.3-flash"}:
        note = (
            "Provider responses had no token usage fields (context_audit.usage_unverified). "
            "API calls, steps, and duration are recorded; token totals are missing."
        )
    return {
        "model": model_key,
        "label": SUITES[model_key]["label"],
        "n_tasks": len(rows),
        "n_usage_json": sum(1 for r in rows if r.get("process_usage_source")),
        "n_tokens_positive": len(token_rows),
        "n_usage_unverified": sum(1 for r in rows if r.get("process_usage_unverified")),
        "n_cache_accounting": sum(1 for r in rows if r.get("process_prompt_cache_accounting")),
        "total_tokens_median": median(totals),
        "total_tokens_p90": quantile(totals, 0.9),
        "total_tokens_sum": sum(totals) if totals else None,
        "total_tokens_median_on_pass": median(pass_totals),
        "completion_tokens_median": median(completion),
        "incremental_tokens_median": median(incremental),
        "api_calls_median": median(
            [r["process_api_calls"] for r in rows if r.get("process_api_calls") is not None]
        ),
        "api_calls_p90": quantile(
            [float(r["process_api_calls"]) for r in rows if r.get("process_api_calls") is not None],
            0.9,
        ),
        "assistant_steps_median": median(
            [r["process_assistant_steps"] for r in rows if r.get("process_assistant_steps") is not None]
        ),
        "duration_seconds_median": median(
            [r["process_duration_seconds"] for r in rows if r.get("process_duration_seconds") is not None]
        ),
        "duration_seconds_p90": quantile(
            [float(r["process_duration_seconds"]) for r in rows if r.get("process_duration_seconds") is not None],
            0.9,
        ),
        "note": note,
    }


def grouped(rows: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[str(row.get(field) or "unknown")].append(row)
    out = []
    for key, items in sorted(buckets.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        passed = sum(1 for r in items if r["functional_pass"])
        empty = sum(1 for r in items if not r["usable_submission"])
        blob = rate_blob(passed, len(items))
        blob.update({"group": key, "empty": empty, "n_nonempty": len(items) - empty})
        out.append(blob)
    return out


def mcnemar(a_pass: list[bool], b_pass: list[bool]) -> dict[str, Any]:
    n01 = n10 = 0
    for a, b in zip(a_pass, b_pass, strict=True):
        if a and not b:
            n10 += 1
        elif b and not a:
            n01 += 1
    # exact binomial two-sided on discordant pairs
    n = n01 + n10
    if n == 0:
        p = 1.0
    else:
        # P(X<=k) + P(X>=n-k) with X~Bin(n, 0.5); k = min(n01, n10)
        k = min(n01, n10)
        p = 0.0
        for i in range(0, k + 1):
            p += math.comb(n, i)
        p = min(1.0, 2 * p / (2 ** n))
    return {"n10": n10, "n01": n01, "discordant": n, "p_exact": p}


def chi2_independence(table: list[list[int]]) -> dict[str, Any]:
    rows = len(table)
    cols = len(table[0])
    row_sum = [sum(r) for r in table]
    col_sum = [sum(table[i][j] for i in range(rows)) for j in range(cols)]
    n = sum(row_sum)
    if n == 0 or any(x == 0 for x in row_sum + col_sum):
        return {"chi2": None, "df": (rows - 1) * (cols - 1), "note": "degenerate"}
    chi2 = 0.0
    expected = []
    for i in range(rows):
        exp_row = []
        for j in range(cols):
            e = row_sum[i] * col_sum[j] / n
            exp_row.append(e)
            chi2 += (table[i][j] - e) ** 2 / e if e else 0.0
        expected.append(exp_row)
    df = (rows - 1) * (cols - 1)
    return {"chi2": chi2, "df": df, "n": n, "expected": expected}


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = fieldnames or list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            flat = dict(row)
            for key, value in list(flat.items()):
                if isinstance(value, (list, dict)):
                    flat[key] = json.dumps(value, ensure_ascii=False)
            writer.writerow(flat)


def main() -> None:
    taxonomy = load_taxonomy()
    python150 = sorted(tid for tid, row in taxonomy.items() if row.get("suite_split") == "python150")
    if len(python150) != 150:
        raise SystemExit(f"expected 150 python150 tasks, got {len(python150)}")

    metadata: dict[str, dict[str, Any]] = {}
    for tid in python150:
        path = TASKS_ROOT / tid / "metadata.json"
        metadata[tid] = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}

    all_rows: list[dict[str, Any]] = []
    by_model: dict[str, list[dict[str, Any]]] = {}
    eligibility: dict[str, Any] = {}
    for model_key in SUITES:
        rows = [collect_row(model_key, tid, taxonomy[tid], metadata[tid]) for tid in python150]
        by_model[model_key] = rows
        all_rows.extend(rows)
        freeze_counts = Counter(r["freeze_id"][:16] for r in rows)
        image_ok = sum(1 for r in rows if EXPECTED_IMAGE_TAG in str(r["agent_docker_image"]))
        eligibility[model_key] = {
            "n_tasks": len(rows),
            "has_run_json": sum(1 for r in rows if r["has_run_json"]),
            "has_result_json": sum(1 for r in rows if r["has_result_json"]),
            "freeze_prefix_counts": dict(freeze_counts),
            "agent_image_matches_212930ea": image_ok,
            "note": (
                "24 freeze-v2 ids (6c20ff03) + 126 predecessor 150 freeze (0b106842) "
                "were merged into python200-prime-v2-main-r1; GPT-OSS is 150× freeze v2."
            ),
        }

    leaderboard = []
    funnel = []
    process_rows = []
    for model_key, rows in by_model.items():
        passed = sum(1 for r in rows if r["functional_pass"])
        empty = sum(1 for r in rows if not r["usable_submission"])
        hard3 = [r for r in rows if r["hard3"]]
        core = [r for r in rows if not r["hard3"]]
        blob = rate_blob(passed, 150)
        blob.update(
            {
                "model": model_key,
                "label": SUITES[model_key]["label"],
                "empty_unusable_submission": empty,
                "empty_no_result_json": sum(1 for r in rows if not r["has_result_json"]),
                "core100": rate_blob(sum(1 for r in core if r["functional_pass"]), 100),
                "hard3": rate_blob(sum(1 for r in hard3 if r["functional_pass"]), 50),
                "pass_but_run_status_not_passed": sum(
                    1 for r in rows if r["functional_pass"] and r["run_status"] != "passed"
                ),
            }
        )
        leaderboard.append(blob)

        stage_counts = Counter(r["first_failure_stage"] for r in rows)
        funnel.append(
            {
                "model": model_key,
                "label": SUITES[model_key]["label"],
                **{stage: int(stage_counts.get(stage, 0)) for stage in STAGE_ORDER},
                "other": int(stage_counts.get("other", 0)),
            }
        )

        empty_tve = sum(
            1
            for r in rows
            if (not r["usable_submission"]) and (r["process_tve"] or r["process_invalid_encrypted"])
        )
        artifact_fail = sum(1 for r in rows if r["artifact_fail"])
        process_rows.append(
            {
                "model": model_key,
                "empty_unusable": empty,
                "empty_tve_or_encrypted": empty_tve,
                "infra_error_json_any": sum(1 for r in rows if r["process_tve"] or r["process_invalid_encrypted"]),
                "note": (
                    "infra_error_json_any includes recovered tool-schema hiccups; "
                    "only empty_unusable is a process non-delivery for 5.2.1."
                ),
                "invalid_encrypted_empty": sum(
                    1 for r in rows if (not r["usable_submission"]) and r["process_invalid_encrypted"]
                ),
                "timeout_any": sum(1 for r in rows if r["process_timeout"]),
                "context_violation": sum(1 for r in rows if r["process_context_violation"]),
                "artifact_fail_5_3_denominator": artifact_fail,
                "pass_with_nonpassed_run_status": blob["pass_but_run_status_not_passed"],
                "api_calls_median": median([r["process_api_calls"] for r in rows if r["process_api_calls"] is not None]),
                "api_calls_p90": quantile(
                    [float(r["process_api_calls"]) for r in rows if r["process_api_calls"] is not None], 0.9
                ),
                "assistant_steps_median": median(
                    [r["process_assistant_steps"] for r in rows if r["process_assistant_steps"] is not None]
                ),
                "duration_seconds_median": median(
                    [r["process_duration_seconds"] for r in rows if r["process_duration_seconds"] is not None]
                ),
            }
        )

    # pairwise McNemar
    order = list(SUITES)
    pairwise = []
    by_task_pass = {
        model: {r["task_id"]: r["functional_pass"] for r in rows} for model, rows in by_model.items()
    }
    for i, a in enumerate(order):
        for b in order[i + 1 :]:
            pa = [by_task_pass[a][tid] for tid in python150]
            pb = [by_task_pass[b][tid] for tid in python150]
            rec = mcnemar(pa, pb)
            rec.update({"a": a, "b": b})
            pairwise.append(rec)

    solve_count = Counter()
    for tid in python150:
        solve_count[sum(1 for m in order if by_task_pass[m][tid])] += 1

    # compactness among passes
    compactness_summary = []
    pass_sets = {m: {r["task_id"] for r in rows if r["functional_pass"]} for m, rows in by_model.items()}
    for model_key, rows in by_model.items():
        passes = [r for r in rows if r["functional_pass"]]
        rres = [float(r["rres"]) for r in passes if r["rres"] is not None]
        copyf = [float(r["copied_fraction"]) for r in passes if r["copied_fraction"] is not None]
        classes = Counter(r["compactness_class"] or "unknown" for r in passes)
        compactness_summary.append(
            {
                "model": model_key,
                "n_pass": len(passes),
                "n_with_rres": len(rres),
                "rres_median": median(rres),
                "rres_p25": quantile(rres, 0.25),
                "rres_p75": quantile(rres, 0.75),
                "copied_fraction_median": median(copyf),
                "compactness_class": dict(classes),
                "copy_heavy_pass": classes.get("copy_heavy_pass", 0),
                "compact_pass": classes.get("compact_pass", 0),
                "functional_mixed_footprint": classes.get("functional_mixed_footprint", 0),
            }
        )

    paired = {}
    for name, models in {
        "all6": order,
        "all5_without_glm": [m for m in order if m != "glm-5.3-flash"],
        "pro_flash": ["deepseek-v4-pro", "deepseek-v4-flash"],
        "pro_luna": ["deepseek-v4-pro", "gpt-5.6-luna"],
        "deepseek_luna": ["deepseek-v4-flash", "gpt-5.6-luna"],
        "pro_flash_luna": ["deepseek-v4-pro", "deepseek-v4-flash", "gpt-5.6-luna"],
        "glm_qwen": ["glm-5.3-flash", "qwen3.6-35b-a3b-fp8"],
        "glm_luna": ["glm-5.3-flash", "gpt-5.6-luna"],
    }.items():
        inter = set.intersection(*(pass_sets[m] for m in models))
        per_model = []
        for m in models:
            subset = [r for r in by_model[m] if r["task_id"] in inter]
            rres = [float(r["rres"]) for r in subset if r["rres"] is not None]
            copyf = [float(r["copied_fraction"]) for r in subset if r["copied_fraction"] is not None]
            classes = Counter(r["compactness_class"] or "unknown" for r in subset)
            per_model.append(
                {
                    "model": m,
                    "rres_median": median(rres),
                    "copied_fraction_median": median(copyf),
                    "copy_heavy_pass": classes.get("copy_heavy_pass", 0),
                    "compact_pass": classes.get("compact_pass", 0),
                    "functional_mixed_footprint": classes.get("functional_mixed_footprint", 0),
                }
            )
        paired[name] = {"n": len(inter), "models": per_model}

    # lift-type / hard3 chi2 on Pro and Flash (both 0 empty on Python-150)
    lift_levels = ["Direct", "Adapted", "Composite"]
    ds = by_model["deepseek-v4-flash"]
    pro_rows = by_model["deepseek-v4-pro"]

    def lift_chi2_for(rows: list[dict[str, Any]]) -> dict[str, Any]:
        table = []
        for lift in lift_levels:
            items = [r for r in rows if r["lift_type"] == lift]
            p = sum(1 for r in items if r["functional_pass"])
            table.append([p, len(items) - p])
        out = chi2_independence(table)
        out["levels"] = lift_levels
        return out

    def hard3_chi2_for(rows: list[dict[str, Any]]) -> dict[str, Any]:
        table = [
            [
                sum(1 for r in rows if (not r["hard3"]) and r["functional_pass"]),
                sum(1 for r in rows if (not r["hard3"]) and not r["functional_pass"]),
            ],
            [
                sum(1 for r in rows if r["hard3"] and r["functional_pass"]),
                sum(1 for r in rows if r["hard3"] and not r["functional_pass"]),
            ],
        ]
        out = chi2_independence(table)
        out["levels"] = ["core100", "hard3"]
        return out

    glm_rows = by_model["glm-5.3-flash"]
    lift_chi2 = lift_chi2_for(ds)
    lift_chi2_pro = lift_chi2_for(pro_rows)
    lift_chi2_glm = lift_chi2_for(glm_rows)
    hard_chi2 = hard3_chi2_for(ds)
    hard_chi2_pro = hard3_chi2_for(pro_rows)
    hard_chi2_glm = hard3_chi2_for(glm_rows)

    # extreme compactness examples
    ds_copy = sorted(
        [r for r in by_model["deepseek-v4-flash"] if r["functional_pass"] and r["rres"] is not None],
        key=lambda r: float(r["rres"]),
        reverse=True,
    )
    luna_compact = sorted(
        [r for r in by_model["gpt-5.6-luna"] if r["functional_pass"] and r["rres"] is not None],
        key=lambda r: float(r["rres"]),
    )

    # candidate cases (ids only; prose is in README)
    qwen_empty = [r for r in by_model["qwen3.6-35b-a3b-fp8"] if not r["usable_submission"]]
    ds_public = [r for r in ds if r["first_failure_stage"] == "public_failure"]
    ds_hidden = [r for r in ds if r["first_failure_stage"] == "hidden_failure"]
    ds_iso = [r for r in ds if r["first_failure_stage"] == "isolation_failure"]

    token_usage = [summarize_token_usage(model_key, rows) for model_key, rows in by_model.items()]

    summary = {
        "scope": "Python-150 only from python200-prime-v2-main-r1",
        "n": 150,
        "freeze_campaign": "python200-prime-v2-main-r1",
        "functional_pass_definition": "build ∧ public ∧ hidden ∧ isolation",
        "empty_definition": "no files under submission/ (unusable deliverable)",
        "glm_excluded": False,
        "eligibility": eligibility,
        "leaderboard": leaderboard,
        "funnel": funnel,
        "process": process_rows,
        "token_usage": token_usage,
        "pairwise_mcnemar": pairwise,
        "solve_count": {str(k): v for k, v in sorted(solve_count.items())},
        "by_lift_type": {m: grouped(rows, "lift_type") for m, rows in by_model.items()},
        "by_construction": {m: grouped(rows, "construction_split") for m, rows in by_model.items()},
        "by_entanglement_primary": {
            m: grouped(rows, "entanglement_primary") for m, rows in by_model.items()
        },
        "by_feature_family": {m: grouped(rows, "feature_family") for m, rows in by_model.items()},
        "entanglement_level_is_uniform_high": all(
            r["entanglement_level"] == "high" for r in ds
        ),
        "lift_type_chi2_deepseek": lift_chi2,
        "lift_type_chi2_pro": lift_chi2_pro,
        "lift_type_chi2_glm": lift_chi2_glm,
        "hard3_chi2_deepseek": hard_chi2,
        "hard3_chi2_pro": hard_chi2_pro,
        "hard3_chi2_glm": hard_chi2_glm,
        "compactness_among_passes": compactness_summary,
        "paired_compactness": paired,
        "section_5_3": {
            "semantic_labels_assigned": False,
            "reason": "Protocol forbids inferring primary semantic cause from evaluator last line; annotation CSV not produced in this pass.",
            "denominators": {
                m: sum(1 for r in rows if r["artifact_fail"]) for m, rows in by_model.items()
            },
            "empty_excluded_from_5_3": {
                m: sum(1 for r in rows if not r["usable_submission"]) for m, rows in by_model.items()
            },
        },
        "case_study_seeds": {
            "qwen_empty_tve_example": qwen_empty[0]["task_id"] if qwen_empty else None,
            "deepseek_public_example": ds_public[0]["task_id"] if ds_public else None,
            "deepseek_hidden_example": ds_hidden[0]["task_id"] if ds_hidden else None,
            "deepseek_isolation_example": ds_iso[0]["task_id"] if ds_iso else None,
            "pro_public_example": next(
                (r["task_id"] for r in pro_rows if r["first_failure_stage"] == "public_failure"),
                None,
            ),
            "pro_hidden_example": next(
                (r["task_id"] for r in pro_rows if r["first_failure_stage"] == "hidden_failure"),
                None,
            ),
            "deepseek_highest_rres_pass": [
                {"task_id": r["task_id"], "rres": r["rres"], "copied_fraction": r["copied_fraction"]}
                for r in ds_copy[:5]
            ],
            "luna_lowest_rres_pass": [
                {"task_id": r["task_id"], "rres": r["rres"], "copied_fraction": r["copied_fraction"]}
                for r in luna_compact[:5]
            ],
        },
    }

    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(OUT / "task_results.csv", all_rows)
    write_csv(OUT / "leaderboard.csv", [
        {
            "model": r["label"],
            "passed": r["passed"],
            "n": r["total"],
            "rate": r["rate"],
            "wilson_lo": r["wilson_95"][0],
            "wilson_hi": r["wilson_95"][1],
            "empty_unusable": r["empty_unusable_submission"],
            "empty_no_result_json": r["empty_no_result_json"],
            "core100": r["core100"]["display"],
            "hard3": r["hard3"]["display"],
            "pass_run_status_not_passed": r["pass_but_run_status_not_passed"],
        }
        for r in leaderboard
    ])
    write_csv(OUT / "funnel.csv", funnel)
    write_csv(OUT / "process.csv", process_rows)
    write_csv(OUT / "token_usage.csv", token_usage)

    lift_flat = []
    for model, groups in summary["by_lift_type"].items():
        for g in groups:
            lift_flat.append({"model": model, **g})
    write_csv(OUT / "by_lift_type.csv", lift_flat)
    cons_flat = []
    for model, groups in summary["by_construction"].items():
        for g in groups:
            cons_flat.append({"model": model, **g})
    write_csv(OUT / "by_construction.csv", cons_flat)

    print(json.dumps({
        "out": str(OUT),
        "leaderboard": [{k: r[k] for k in ("label", "display", "wilson_display", "empty_unusable_submission")} | {
            "core100": r["core100"]["display"], "hard3": r["hard3"]["display"]
        } for r in leaderboard],
        "funnel": funnel,
        "token_usage": [
            {
                k: r[k]
                for k in (
                    "label",
                    "n_tokens_positive",
                    "n_usage_unverified",
                    "total_tokens_median",
                    "incremental_tokens_median",
                    "completion_tokens_median",
                    "api_calls_median",
                    "assistant_steps_median",
                    "duration_seconds_median",
                )
            }
            for r in token_usage
        ],
        "solve_count": summary["solve_count"],
        "paired": {k: v["n"] for k, v in paired.items()},
        "compactness": compactness_summary,
        "5_3_denoms": summary["section_5_3"]["denominators"],
        "mcnemar_ds_luna": next(p for p in pairwise if p["a"] == "deepseek-v4-flash" and p["b"] == "gpt-5.6-luna"),
        "mcnemar_glm": [p for p in pairwise if "glm-5.3-flash" in (p["a"], p["b"])],
        "hard3_chi2": hard_chi2,
        "hard3_chi2_glm": hard_chi2_glm,
        "cases": summary["case_study_seeds"],
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
