#!/usr/bin/env python3
"""Union frozen Python-150 Main with External-50 Main into Python-200 analysis.

Reads per-task ``eval/result.json`` for Functional Pass, primary failure stage,
and pass-conditioned RRES. Workflow ``run.status`` / ``summary.passed`` are
operational only.

This is analysis-only: it does not copy raw experiment archives.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
SUITE_PATH = REPO_ROOT / "benchmark/selection/python200_suite.json"
EXTERNAL_ROOT = REPO_ROOT / "benchmark/external50"
DEFAULT_OUTPUT = (
    REPO_ROOT
    / "artifacts/research_analysis/current_results/python200_cross_model_main_20260818.json"
)

AGENT_IMAGE = "sha256:f328e2ceb9d68afca405e1b0be0bb7d8ef24a05e7dab3242b05cf574867132fd"
EVAL_IMAGE = "sha256:a491d620df49638e6a9faee6701133a9351055d4783390f86ed345dd73ae92c2"

MODELS: dict[str, dict[str, Any]] = {
    "deepseek_api": {
        "label": "DeepSeek V4 Flash API",
        "endpoint": "api",
        "model": "deepseek/deepseek-v4-flash",
        "profile": "openhands_deepseek_v4_flash",
        "baseline_dirs": [
            REPO_ROOT
            / "experiments/FeatureLiftBench-v3-846-20260801-ready/experiments/export"
            / "FeatureLiftBench-deepseek-v4-flash-150-20260805/deepseek-v4-flash-0731"
        ],
        "extension_dirs": [
            REPO_ROOT
            / "experiments/python/openhands/deepseek-v4-flash"
            / "external50-deepseek-v4-flash-0805-main-001"
        ],
        "full200_dir": None,
    },
    "deepseek_local": {
        "label": "DeepSeek V4 Flash local vLLM",
        "endpoint": "local_vllm",
        "model": "openai/DeepSeek-V4-Flash",
        "profile": "openhands_deepseek_v4_flash_vllm_local",
        "baseline_dirs": [],
        "extension_dirs": [],
        "full200_dir": (
            REPO_ROOT
            / "experiments/python/openhands/deepseek-v4-flash"
            / "python200-deepseek-v4-flash-vllm-local-0812-001"
        ),
    },
    "qwen3_5_122b": {
        "label": "Qwen3.5 122B local vLLM",
        "endpoint": "local_vllm",
        "model": "openai/Qwen3.5-122B-A10B-FP8",
        "profile": "openhands_qwen3_5_122b_a10b_fp8_paper",
        "baseline_dirs": [
            REPO_ROOT
            / "experiments/FeatureLiftBench-v3-846-20260801-ready/experiments/python/openhands"
            / "qwen3.5-122b-a10b-fp8/compliant150-qwen122b-main-002-20260801-151040"
        ],
        "extension_dirs": [
            REPO_ROOT
            / "experiments/python/openhands/qwen3.5-122b-a10b-fp8"
            / "external50-qwen3.5-122b-a10b-fp8-0817-main-001"
        ],
        "full200_dir": None,
    },
    "qwen3_6_35b": {
        "label": "Qwen3.6 35B local vLLM",
        "endpoint": "local_vllm",
        "model": "openai/Qwen3.6-35B-A3B-FP8",
        "profile": "openhands_qwen3_6_35b_a3b_fp8_paper",
        "baseline_dirs": [
            REPO_ROOT
            / "experiments/FeatureLiftBench-v3-846-20260801-ready/experiments/python/openhands"
            / "qwen3.6-35b-a3b-fp8/compliant150-qwen35b-shard1-p8008-20260801-173847",
            REPO_ROOT
            / "experiments/FeatureLiftBench-v3-846-20260801-ready/experiments/python/openhands"
            / "qwen3.6-35b-a3b-fp8/compliant150-qwen35b-shard2-p8020-20260801-173847",
            REPO_ROOT
            / "experiments/FeatureLiftBench-v3-846-20260801-ready/experiments/python/openhands"
            / "qwen3.6-35b-a3b-fp8/compliant150-qwen35b-shard3-p8021-20260801-173847",
        ],
        "extension_dirs": [
            REPO_ROOT
            / "experiments/python/openhands/qwen3.6-35b-a3b-fp8"
            / "external50-qwen3.6-35b-a3b-fp8-0817-main-001"
        ],
        "full200_dir": None,
    },
    "gpt_oss_120b": {
        "label": "GPT-OSS 120B local vLLM",
        "endpoint": "local_vllm",
        "model": "openai/gpt-oss-120b",
        "profile": "openhands_gpt_oss_120b_paper",
        "baseline_dirs": [
            REPO_ROOT
            / "experiments/FeatureLiftBench-v3-846-20260801-ready/experiments/python/openhands"
            / "gpt-oss-120b/compliant150-gptoss120b-main-003-20260801-151040"
        ],
        "extension_dirs": [
            REPO_ROOT
            / "experiments/python/openhands/gpt-oss-120b"
            / "external50-gpt-oss-120b-0817-main-001"
        ],
        "full200_dir": None,
    },
}


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def _rel(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPO_ROOT))
    except ValueError:
        return str(resolved)


def _gate_value(result: dict[str, Any], direct: str, nested: str) -> bool | None:
    value = result.get(direct)
    if isinstance(value, bool):
        return value
    value = result.get(nested)
    if isinstance(value, dict) and isinstance(value.get("passed"), bool):
        return value["passed"]
    return None


def _primary_failure_stage(result: dict[str, Any] | None, run_status: str | None) -> str:
    if result is None:
        if run_status == "missing_submission":
            return "missing_submission"
        return "stage_evidence_unavailable"
    build = _gate_value(result, "build_pass", "build")
    public = _gate_value(result, "public_tests_pass", "public_tests")
    hidden = _gate_value(result, "hidden_tests_pass", "hidden_tests")
    isolation = _gate_value(result, "isolation_pass", "isolation")
    score = (result.get("scores") or {}).get("functional_gate")
    eval_tooling = result.get("eval_tooling") or {}
    sandbox = result.get("sandbox") or {}
    if eval_tooling.get("passed") is False or sandbox.get("docker_sandbox_error") is True:
        return "evaluator_infra"
    if build is False:
        return "build_failure"
    if public is False:
        return "public_failure"
    if hidden is False:
        return "hidden_failure"
    if isolation is False:
        return "isolation_failure"
    if score in {1, 1.0}:
        return "functional_pass"
    if run_status == "missing_submission":
        return "missing_submission"
    return "unknown"


def _quantile(values: list[float], probability: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def _wilson(k: int, n: int, z: float = 1.96) -> dict[str, float]:
    if n <= 0:
        return {"low": 0.0, "high": 0.0}
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    margin = z * math.sqrt((p * (1.0 - p) + z * z / (4.0 * n)) / n) / denom
    return {"low": round(center - margin, 6), "high": round(center + margin, 6)}


def _rres_summary(values: list[float], functional_passed: int) -> dict[str, Any]:
    return {
        "metric": "reference_relative_extraction_size",
        "direction": "lower_is_better",
        "eligible_functional_passes": functional_passed,
        "available": len(values),
        "coverage": round(len(values) / functional_passed, 6) if functional_passed else 0.0,
        "median": round(statistics.median(values), 6) if values else None,
        "q1": round(_quantile(values, 0.25), 6) if values else None,
        "q3": round(_quantile(values, 0.75), 6) if values else None,
        "minimum": round(min(values), 6) if values else None,
        "maximum": round(max(values), 6) if values else None,
    }


def _add_usage(totals: dict[str, float], usage: MappingLike) -> None:
    if not isinstance(usage, dict):
        return
    for key in (
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "api_calls",
        "assistant_steps",
    ):
        value = usage.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            totals[key] = totals.get(key, 0.0) + float(value)


MappingLike = dict[str, Any]


def _collect_tasks(suite_dirs: list[Path]) -> dict[str, dict[str, Any]]:
    collected: dict[str, dict[str, Any]] = {}
    for suite_dir in suite_dirs:
        suite_path = suite_dir / "suite.json"
        if not suite_path.is_file():
            raise FileNotFoundError(f"missing suite.json: {suite_path}")
        suite = _load_json(suite_path)
        for entry in suite.get("runs") or []:
            if not isinstance(entry, dict) or not isinstance(entry.get("task_id"), str):
                raise TypeError(f"invalid suite row in {suite_path}")
            task_id = entry["task_id"]
            if task_id in collected:
                raise ValueError(f"duplicate task_id {task_id} while reading {suite_dir}")
            run_path = suite_dir / task_id / "run.json"
            eval_path = suite_dir / task_id / "eval/result.json"
            run = _load_json(run_path) if run_path.is_file() else {}
            result = _load_json(eval_path) if eval_path.is_file() else None
            conditions = run.get("experiment_conditions") if isinstance(run, dict) else {}
            if not isinstance(conditions, dict):
                conditions = {}
            agent = run.get("agent") if isinstance(run.get("agent"), dict) else {}
            collected[task_id] = {
                "task_id": task_id,
                "suite_dir": _rel(suite_dir),
                "run_status": run.get("status") or entry.get("status"),
                "suite_final_score": entry.get("final_score"),
                "eval_result": result,
                "agent_runtime": conditions.get("agent_runtime"),
                "evaluator_runtime": conditions.get("evaluator_runtime"),
                "agent_profile": conditions.get("agent_profile"),
                "model": conditions.get("model"),
                "agent_max_steps": conditions.get("agent_max_steps"),
                "ablation_arm": (conditions.get("ablation") or {}).get("ablation_arm")
                if isinstance(conditions.get("ablation"), dict)
                else None,
                "usage": agent.get("usage") if isinstance(agent.get("usage"), dict) else {},
            }
    return collected


def _functional_pass(task: dict[str, Any]) -> bool:
    result = task.get("eval_result")
    if isinstance(result, dict):
        gate = (result.get("scores") or {}).get("functional_gate")
        if gate in {1, 1.0}:
            return True
        if gate in {0, 0.0}:
            return False
    score = task.get("suite_final_score")
    return score in {1, 1.0}


def _summarize_split(
    tasks: dict[str, dict[str, Any]],
    expected_ids: list[str],
    split: str,
) -> dict[str, Any]:
    missing = [task_id for task_id in expected_ids if task_id not in tasks]
    extra = sorted(set(tasks) - set(expected_ids))
    if missing or extra:
        raise ValueError(
            f"{split} coverage error: missing={len(missing)} extra={len(extra)} "
            f"missing_sample={missing[:5]} extra_sample={extra[:5]}"
        )
    outcomes: Counter[str] = Counter()
    task_ids_by_outcome: dict[str, list[str]] = {}
    rres_values: list[float] = []
    image_ids: set[tuple[str | None, str | None]] = set()
    profiles: set[str] = set()
    models: set[str] = set()
    steps: set[Any] = set()
    arms: set[str] = set()
    usage_totals: dict[str, float] = {}
    eval_coverage = 0
    run_status_passed = 0
    for task_id in expected_ids:
        task = tasks[task_id]
        result = task.get("eval_result") if isinstance(task.get("eval_result"), dict) else None
        if result is not None:
            eval_coverage += 1
        passed = _functional_pass(task)
        if result is not None:
            result_gate = (result.get("scores") or {}).get("functional_gate")
            suite_score = task.get("suite_final_score")
            if result_gate in {0, 0.0, 1, 1.0} and suite_score in {0, 0.0, 1, 1.0}:
                if float(result_gate) != float(suite_score):
                    raise ValueError(
                        f"suite/evaluator functional mismatch for {task_id}: "
                        f"{suite_score} vs {result_gate}"
                    )
        outcome = (
            "functional_pass"
            if passed
            else _primary_failure_stage(result, task.get("run_status"))
        )
        if passed:
            outcome = "functional_pass"
            if result is not None:
                ratio = (result.get("scores") or {}).get("reference_relative_loc_ratio")
                if isinstance(ratio, (int, float)) and not isinstance(ratio, bool):
                    rres_values.append(float(ratio))
        outcomes[outcome] += 1
        task_ids_by_outcome.setdefault(outcome, []).append(task_id)
        if task.get("run_status") == "passed":
            run_status_passed += 1
        agent_rt = task.get("agent_runtime") if isinstance(task.get("agent_runtime"), dict) else {}
        eval_rt = (
            task.get("evaluator_runtime")
            if isinstance(task.get("evaluator_runtime"), dict)
            else {}
        )
        image_ids.add((agent_rt.get("image_id"), eval_rt.get("image_id")))
        if isinstance(task.get("agent_profile"), str):
            profiles.add(task["agent_profile"])
        if isinstance(task.get("model"), str):
            models.add(task["model"])
        steps.add(task.get("agent_max_steps"))
        if isinstance(task.get("ablation_arm"), str):
            arms.add(task["ablation_arm"])
        _add_usage(usage_totals, task.get("usage") or {})
    for values in task_ids_by_outcome.values():
        values.sort()
    assigned = len(expected_ids)
    functional_passed = outcomes.get("functional_pass", 0)
    return {
        "split": split,
        "assigned": assigned,
        "functional_passed": functional_passed,
        "functional_pass_rate": round(functional_passed / assigned, 6) if assigned else 0.0,
        "wilson95": _wilson(functional_passed, assigned),
        "run_status_passed": run_status_passed,
        "eval_result_coverage": eval_coverage,
        "primary_outcomes": dict(sorted(outcomes.items())),
        "task_ids_by_primary_outcome": dict(sorted(task_ids_by_outcome.items())),
        "rres": _rres_summary(rres_values, functional_passed),
        "usage_totals": {key: int(value) for key, value in sorted(usage_totals.items())},
        "attestation": {
            "image_id_pairs": [
                {"agent_image_id": agent, "eval_image_id": eval_id}
                for agent, eval_id in sorted(image_ids, key=lambda item: (item[0] or "", item[1] or ""))
            ],
            "profiles": sorted(profiles),
            "models": sorted(models),
            "agent_max_steps": sorted(steps, key=lambda value: str(value)),
            "ablation_arms": sorted(arms),
            "expected_agent_image_id": AGENT_IMAGE,
            "expected_eval_image_id": EVAL_IMAGE,
            "images_match_expected": image_ids <= {(AGENT_IMAGE, EVAL_IMAGE)},
        },
    }


def _merge_model(
    spec: dict[str, Any],
    baseline_ids: list[str],
    external_ids: list[str],
    all_ids: list[str],
) -> dict[str, Any]:
    full200_dir = spec.get("full200_dir")
    if full200_dir:
        tasks = _collect_tasks([Path(full200_dir)])
        sources = {"full200": [_rel(Path(full200_dir))]}
    else:
        baseline_tasks = _collect_tasks([Path(path) for path in spec["baseline_dirs"]])
        extension_tasks = _collect_tasks([Path(path) for path in spec["extension_dirs"]])
        overlap = set(baseline_tasks) & set(extension_tasks)
        if overlap:
            raise ValueError(f"baseline/extension overlap: {sorted(overlap)[:5]}")
        tasks = {**baseline_tasks, **extension_tasks}
        sources = {
            "baseline": [_rel(Path(path)) for path in spec["baseline_dirs"]],
            "extension": [_rel(Path(path)) for path in spec["extension_dirs"]],
        }
    python150 = _summarize_split(
        {task_id: tasks[task_id] for task_id in baseline_ids},
        baseline_ids,
        "python150",
    )
    external50 = _summarize_split(
        {task_id: tasks[task_id] for task_id in external_ids},
        external_ids,
        "external50",
    )
    python200 = _summarize_split(tasks, all_ids, "python200")
    return {
        "label": spec["label"],
        "endpoint": spec["endpoint"],
        "expected_model": spec["model"],
        "expected_profile": spec["profile"],
        "sources": sources,
        "python150": python150,
        "external50": external50,
        "python200": python200,
    }


def build_payload() -> dict[str, Any]:
    suite = _load_json(SUITE_PATH)
    all_ids = list(suite["task_ids"])
    external_ids = [task_id for task_id in all_ids if (EXTERNAL_ROOT / task_id).is_dir()]
    baseline_ids = [task_id for task_id in all_ids if task_id not in set(external_ids)]
    if len(all_ids) != 200 or len(baseline_ids) != 150 or len(external_ids) != 50:
        raise ValueError(
            f"unexpected suite split: total={len(all_ids)} "
            f"baseline={len(baseline_ids)} external={len(external_ids)}"
        )
    models = {
        key: _merge_model(spec, baseline_ids, external_ids, all_ids)
        for key, spec in MODELS.items()
    }
    leaderboard = []
    for key, payload in models.items():
        row = payload["python200"]
        leaderboard.append(
            {
                "model_key": key,
                "label": payload["label"],
                "endpoint": payload["endpoint"],
                "functional_passed": row["functional_passed"],
                "assigned": row["assigned"],
                "functional_pass_rate": row["functional_pass_rate"],
                "wilson95": row["wilson95"],
                "rres_median": row["rres"]["median"],
                "images_match_expected": row["attestation"]["images_match_expected"],
            }
        )
    leaderboard.sort(key=lambda item: (-item["functional_passed"], item["label"]))
    return {
        "schema_version": "featureliftbench.python200_cross_model_main.v1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "suite_id": suite["suite_id"],
        "task_set_sha256": suite["task_set_sha256"],
        "arm": "main",
        "information_condition": "full_repository_no_hint",
        "metric_contract": {
            "primary": "functional_pass_rate",
            "secondary": "reference_relative_extraction_size",
            "workflow_passed_is_not_functional": True,
        },
        "leaderboard": leaderboard,
        "models": models,
    }


def _fmt_pct(rate: float) -> str:
    return f"{rate * 100:.1f}%"


def _fmt_rres(rres: dict[str, Any]) -> str:
    if not rres.get("available"):
        return "n/a"
    return (
        f"{rres['available']}/{rres['eligible_functional_passes']}, "
        f"median {rres['median']:.3f} [{rres['q1']:.3f}, {rres['q3']:.3f}]"
    )


def _outcome_row(outcomes: dict[str, int]) -> str:
    keys = (
        "functional_pass",
        "missing_submission",
        "build_failure",
        "public_failure",
        "hidden_failure",
        "isolation_failure",
        "evaluator_infra",
        "stage_evidence_unavailable",
        "unknown",
    )
    return " | ".join(str(outcomes.get(key, 0)) for key in keys)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Python-200 Main 跨模型结果",
        "",
        f"> **Status: current · Generated: {payload['generated_at']}**",
        "> 条件：Full-Repository / No-Hint Main，120 步，每题一次。",
        "> 指标：evaluator `functional_gate`；`summary.passed` / `run.status` 只作运行诊断。",
        "> 这不是 V1（Main+2M cap），也不是旧 Lite V1 checker/repair 协议。",
        "",
        f"Suite: `{payload['suite_id']}`  ",
        f"Task set: `{payload['task_set_sha256']}`",
        "",
        "## Leaderboard",
        "",
        "| 模型 | 端点 | Functional Pass | Pass Rate | Wilson 95% | RRES median [Q1, Q3] |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    for row in payload["leaderboard"]:
        model = payload["models"][row["model_key"]]
        rres = model["python200"]["rres"]
        ci = row["wilson95"]
        lines.append(
            "| {label} | {endpoint} | **{passed}/200** | **{rate}** | {low:.1%}–{high:.1%} | {rres} |".format(
                label=row["label"],
                endpoint=row["endpoint"],
                passed=row["functional_passed"],
                rate=_fmt_pct(row["functional_pass_rate"]),
                low=ci["low"],
                high=ci["high"],
                rres=_fmt_rres(rres),
            )
        )
    lines.extend(
        [
            "",
            "## 150 / External-50 / 200 分解",
            "",
            "| 模型 | Python-150 | External-50 | Python-200 |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for key, model in payload["models"].items():
        lines.append(
            "| {label} | {a}/{n150} ({ra}) | {b}/{n50} ({rb}) | **{c}/200 ({rc})** |".format(
                label=model["label"],
                a=model["python150"]["functional_passed"],
                n150=model["python150"]["assigned"],
                ra=_fmt_pct(model["python150"]["functional_pass_rate"]),
                b=model["external50"]["functional_passed"],
                n50=model["external50"]["assigned"],
                rb=_fmt_pct(model["external50"]["functional_pass_rate"]),
                c=model["python200"]["functional_passed"],
                rc=_fmt_pct(model["python200"]["functional_pass_rate"]),
            )
        )
    lines.extend(
        [
            "",
            "## 失败阶段（Python-200，互斥首败）",
            "",
            "| 模型 | Pass | 未交付 | Build | Public | Hidden | Isolation | Infra | 缺证据 | Unknown |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for model in payload["models"].values():
        lines.append(
            f"| {model['label']} | {_outcome_row(model['python200']['primary_outcomes'])} |"
        )
    lines.extend(
        [
            "",
            "## 口径与资格",
            "",
            "- Qwen3.5 / GPT-OSS：冻结 Python-150 整包 + 2026-08-17 External-50。",
            "- Qwen3.6-35B：冻结 Python-150 三片（p8008/p8020/p8021）并集 + 同日 External-50。",
            "- DeepSeek API：既有 150 + External-50；DeepSeek 本地：一次跑满 200。",
            "- Agent/evaluator image 均钉在 `sha256:f328e2ce…` / `sha256:a491d620…`。",
            "- Qwen3.6-35B External-50 的 `run.status` 大量失败，但 evaluator Functional 仍按 `functional_gate` 计；不得用 `summary.passed`。",
            "- 未与当前 V1（Main+2M）混表。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown_path = output.with_suffix(".md")
    markdown_path.write_text(render_markdown(payload), encoding="utf-8")
    print(f"Wrote {output}")
    print(f"Wrote {markdown_path}")
    for row in payload["leaderboard"]:
        print(
            f"{row['label']}: {row['functional_passed']}/200 "
            f"({row['functional_pass_rate']:.1%}) images_ok={row['images_match_expected']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
