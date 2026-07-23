#!/usr/bin/env python3
"""Build the bounded MCP report manifest/snapshot from reviewed outputs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


HERE = Path(__file__).resolve().parent
generated_at = datetime.now(timezone.utc).isoformat()

audit = pd.read_csv(HERE / "trajectory_stage_labels_550.csv")
stages = audit[~audit.formal_pass].groupby("earliest_failure_stage", as_index=False).agg(
    failures=("run_id", "size"),
    median_tokens=("total_tokens", "median"),
    models=("model", "nunique"),
    tasks=("task_id", "nunique"),
).sort_values("failures", ascending=False)
stages["stage"] = stages["earliest_failure_stage"].str.replace("_", " ")
stages["median_tokens_m"] = (stages["median_tokens"] / 1_000_000).round(2)

dynamic = pd.read_csv(HERE / "dynamic_comparison.csv")
primary = dynamic[dynamic.group.isin(["dynamic_runtime", "relatively_static"])].copy()
primary["group_label"] = primary.group.map({"dynamic_runtime": "Dynamic runtime", "relatively_static": "Relatively static"})
dynamic_tidy = []
for _, row in primary.iterrows():
    for metric, label in [("pass_rate", "Formal pass"), ("hidden_failure_rate_given_public", "Hidden fail | public pass")]:
        dynamic_tidy.append(
            {
                "metric": label,
                "group": row["group_label"],
                "rate": float(row[metric]),
                "runs": int(row["runs"]),
                "tasks": int(row["tasks"]),
                "median_tokens": float(row["median_tokens"]),
                "repeat_read_rate": float(row["repeat_read_affected_rate"]),
                "runtime_probe_rate": float(row["runtime_probe_rate"]),
                "fresh_verify_rate": float(row["fresh_final_verification_rate"]),
            }
        )

cases = pd.read_csv(HERE / "representative_cases.csv")
priorities = pd.read_csv(HERE / "module_improvement_priorities.csv")
cold_start = pd.read_csv(HERE / "cold_start_entry_actions.csv")
priority_rows = []
for _, row in priorities.iterrows():
    priority_rows.append(
        {
            "priority": int(row["priority"]),
            "module": row["module"],
            "direct_failures": int(row["direct_failures"]),
            "share_agent_failures": float(row["share_agent_failures"]),
            "median_tokens_m": round(float(row["median_tokens"]) / 1_000_000, 2),
            "theoretical_ceiling_pp": float(row["theoretical_ceiling_pp"]),
            "twenty_percent_recovery_pp": float(row["twenty_percent_recovery_pp"]),
            "evidence_strength": row["evidence_strength"],
            "pass_value": row["pass_value"],
            "efficiency_value": row["efficiency_value"],
            "recommended_change": row["recommended_change"],
        }
    )
case_rows = []
for _, row in cases.iterrows():
    case_rows.append(
        {
            "task": row["task_id"],
            "model": row["model"].replace("openai/", "").replace("deepseek/", ""),
            "stage": row["earliest_failure_stage"].replace("_", " "),
            "subtype": row["failure_subtype"].replace("_", " "),
            "missed": str(row["missed_behavior_or_dependency"])[:180],
            "intervention": row["most_likely_intervention"],
        }
    )

audit_source = {
    "id": "trajectory_audit",
    "label": "FeatureLiftBench 550-run trajectory-stage audit",
    "path": "reports/failure_attribution_20260720/trajectory_stage_labels_550.csv",
    "query": {
        "engine": "duckdb",
        "language": "sql",
        "sql": "SELECT * FROM read_csv_auto('reports/failure_attribution_20260720/trajectory_stage_labels_550.csv', header=true);",
        "description": "Deterministic joins and rule-based stage attribution over frozen run records, trajectories, evaluator logs, metadata, oracle manifests, and taxonomy.",
        "tables_used": [
            "reports/token_efficiency_20260720/trajectory_records_550.csv",
            "artifacts/research_analysis/python150_task_taxonomy.csv",
        ],
        "filters": ["frozen_primary runs only", "550 unique model-task pairs", "infrastructure failures retained in total denominator"],
        "metric_definitions": [
            "Formal pass = run_status equals passed.",
            "Hidden fail | public pass = hidden_pass is false among runs where public_pass is true.",
            "Dynamic-runtime primary definition is outcome-blind and requires cross-boundary import/state/lifecycle/config/resource coupling.",
            "Earliest failure stage is a conservative evidence-assisted attribution, not causal ground truth.",
        ],
    },
}

manifest = {
    "version": 1,
    "surface": "report",
    "title": "FeatureLiftBench 严格失败归因：550 条 Agent 轨迹",
    "description": "竞争性瓶颈假设、阶段漏斗、动态运行时对比、代表案例与证据边界。",
    "generatedAt": generated_at,
    "sources": [audit_source],
    "cards": [
        {"id": "formal_pass", "dataset": "headline", "sourceId": "trajectory_audit", "description": "冻结 suite 的正式通过率。", "metrics": [{"label": "Formal pass", "field": "formal_pass_rate", "format": "percent"}]},
        {"id": "public_hidden", "dataset": "headline", "sourceId": "trajectory_audit", "description": "public pass 后进入 hidden fail 的条件比例。", "metrics": [{"label": "Hidden fail | public", "field": "public_hidden_fail_rate", "format": "percent"}]},
        {"id": "dynamic_gap", "dataset": "headline", "sourceId": "trajectory_audit", "description": "dynamic-runtime 与 relatively-static 的 formal-pass 差异。", "metrics": [{"label": "Dynamic pass gap", "field": "dynamic_pass_gap", "format": "percent", "signed": True}]},
        {"id": "infra", "dataset": "headline", "sourceId": "trajectory_audit", "description": "被隔离为 evaluator/dependency-install 的非 Agent 失败。", "metrics": [{"label": "Infrastructure failures", "field": "infrastructure_failures", "format": "number"}]},
        {"id": "entry_observed", "dataset": "cold_start_headline", "sourceId": "trajectory_audit", "description": "有直接证据读到正确入口文件的轨迹比例。", "metrics": [{"label": "Correct entry observed", "field": "entry_observed_rate", "format": "percent"}]},
        {"id": "entry_within_five", "dataset": "cold_start_headline", "sourceId": "trajectory_audit", "description": "在有入口证据的轨迹中，5 个 Agent 操作内读到正确入口的比例。", "metrics": [{"label": "Entry within 5 actions", "field": "entry_within_five_rate", "format": "percent"}]},
        {"id": "closure_plan", "dataset": "cold_start_headline", "sourceId": "trajectory_audit", "description": "轨迹中出现显式 closure plan 的比例。", "metrics": [{"label": "Explicit closure plan", "field": "closure_plan_rate", "format": "percent"}]},
    ],
    "charts": [
        {
            "id": "failure_stages",
            "title": "Earliest observed failure stage",
            "subtitle": "Dependency/API closure and ordinary implementation dominate agent-attributable failures.",
            "type": "horizontalBar",
            "intent": "comparison",
            "question": "Which earliest failure stages account for the most non-pass runs?",
            "rationale": "A ranked horizontal bar chart makes the long stage labels and count comparison readable.",
            "dataset": "failure_stages",
            "sourceId": "trajectory_audit",
            "encodings": {"x": {"field": "stage", "type": "nominal"}, "y": {"field": "failures", "type": "quantitative", "format": "number"}},
            "xAxisTitle": "Earliest stage",
            "yAxisTitle": "Failures",
            "valueFormat": "number",
            "layout": "full",
        },
        {
            "id": "dynamic_static",
            "title": "Dynamic-runtime and relatively-static outcomes",
            "subtitle": "Aggregate pass and post-public hidden-failure rates are nearly identical.",
            "type": "bar",
            "intent": "comparison",
            "question": "Do dynamic-runtime tasks have materially worse observed outcomes?",
            "rationale": "Grouped bars compare the two pre-outcome task groups on the same rate scale.",
            "dataset": "dynamic_comparison",
            "sourceId": "trajectory_audit",
            "encodings": {
                "x": {"field": "metric", "type": "nominal"},
                "y": {"field": "rate", "type": "quantitative", "format": "percent"},
                "color": {"field": "group", "type": "nominal"},
            },
            "valueFormat": "percent",
            "combinationRationale": "Color distinguishes the two task groups while the x-axis identifies the outcome metric.",
            "layout": "full",
        },
        {
            "id": "module_ceiling",
            "title": "Agent module addressable ceilings",
            "subtitle": "Maximum absolute pass-rate gain if every directly attributed failure were recovered; not a forecast.",
            "type": "horizontalBar",
            "intent": "comparison",
            "question": "Which Agent modules have the largest directly observed failure opportunity?",
            "rationale": "A ranked horizontal bar chart makes the long module names and percentage-point ceilings readable.",
            "dataset": "module_priorities",
            "sourceId": "trajectory_audit",
            "encodings": {
                "x": {"field": "module", "type": "nominal"},
                "y": {"field": "theoretical_ceiling_pp", "type": "quantitative", "format": "number"},
            },
            "xAxisTitle": "Agent module",
            "yAxisTitle": "Theoretical pass ceiling, percentage points",
            "valueFormat": "number",
            "layout": "full",
        },
        {
            "id": "cold_start_actions",
            "title": "Actions before the first observed correct-entry read",
            "subtitle": "523 runs with direct entry evidence; 90.8% reached the entry within five Agent actions.",
            "type": "bar",
            "intent": "distribution",
            "question": "How much early navigation work occurs before the correct entry is observed?",
            "rationale": "Discrete action bands show that entry discovery is concentrated in the first five actions.",
            "dataset": "cold_start_actions",
            "sourceId": "trajectory_audit",
            "encodings": {
                "x": {"field": "action_band", "type": "nominal"},
                "y": {"field": "runs", "type": "quantitative", "format": "number"},
            },
            "xAxisTitle": "Agent actions before/at first correct-entry evidence",
            "yAxisTitle": "Runs",
            "valueFormat": "number",
            "layout": "full",
        },
    ],
    "tables": [
        {
            "id": "stage_table",
            "title": "Failure stages and token medians",
            "subtitle": "Post-outcome attribution counts; success rate is not meaningful within these rows.",
            "dataset": "failure_stages",
            "sourceId": "trajectory_audit",
            "defaultSort": {"field": "failures", "direction": "desc"},
            "density": "dense",
            "layout": "full",
            "columns": [
                {"field": "stage", "label": "Earliest stage", "type": "text"},
                {"field": "failures", "label": "Failures", "format": "number"},
                {"field": "median_tokens_m", "label": "Median tokens, M", "format": "number"},
                {"field": "models", "label": "Models", "format": "number"},
                {"field": "tasks", "label": "Tasks", "format": "number"},
            ],
        },
        {
            "id": "case_table",
            "title": "Sixteen representative trajectory dossiers",
            "subtitle": "Deterministic stage-diverse selection; full evidence paths remain in the local dossier.",
            "dataset": "representative_cases",
            "sourceId": "trajectory_audit",
            "defaultSort": {"field": "stage", "direction": "asc"},
            "density": "dense",
            "layout": "full",
            "columns": [
                {"field": "task", "label": "Task", "type": "text"},
                {"field": "model", "label": "Model", "type": "text"},
                {"field": "stage", "label": "Earliest stage", "type": "text"},
                {"field": "subtype", "label": "Subtype", "type": "text"},
                {"field": "missed", "label": "Missed behavior/dependency", "type": "text"},
                {"field": "intervention", "label": "Most likely intervention", "type": "text"},
            ],
        },
        {
            "id": "module_table",
            "title": "Module priorities, evidence, and value",
            "subtitle": "Ceilings are non-causal upper bounds; the 20% column is a common PoC screening threshold, not a forecast.",
            "dataset": "module_priorities",
            "sourceId": "trajectory_audit",
            "defaultSort": {"field": "priority", "direction": "asc"},
            "density": "dense",
            "layout": "full",
            "columns": [
                {"field": "priority", "label": "Priority", "format": "number"},
                {"field": "module", "label": "Module", "type": "text"},
                {"field": "direct_failures", "label": "Direct failures", "format": "number"},
                {"field": "theoretical_ceiling_pp", "label": "Ceiling, pp", "format": "number"},
                {"field": "twenty_percent_recovery_pp", "label": "20% recovery, pp", "format": "number"},
                {"field": "evidence_strength", "label": "Evidence", "type": "text"},
                {"field": "pass_value", "label": "Pass value", "type": "text"},
                {"field": "efficiency_value", "label": "Efficiency value", "type": "text"},
            ],
        },
    ],
    "blocks": [
        {"id": "title", "type": "markdown", "body": "# FeatureLiftBench 严格失败归因：550 条 Agent 轨迹", "layout": "full"},
        {"id": "executive", "type": "markdown", "sourceId": "trajectory_audit", "body": "## Executive Summary\n\n**主要瓶颈发生在定位之后。** 排除 62 条 evaluator/dependency-install 失败后，263 条 Agent 可归因失败中，dependency/API closure 有 85 条，普通实现/语义错误 80 条，动态语义候选 43 条，预算/工作流终止 32 条。动态任务 formal pass 为 41.2%，相对静态任务为 39.8%；当前证据不支持把动态代码理解或 token 管理单独定为总体根因。", "layout": "full"},
        {"id": "metrics", "type": "metric-strip", "cardIds": ["formal_pass", "public_hidden", "dynamic_gap", "infra"], "layout": "full"},
        {"id": "findings", "type": "markdown", "sourceId": "trajectory_audit", "body": "## Key Findings\n\n**Closure 与实现错误排在前两位。** 95.1% 的 run 可直接观察到正确入口，72.9% public pass，但只有 41.5% hidden pass。动态候选不是一个单一机制：37 条仍是 capability-or-implementation 未决，4 条更接近 exploration policy，只有 2 条是弱 memory-state 候选。", "layout": "full"},
        {"id": "stage_chart", "type": "chart", "chartId": "failure_stages", "layout": "full"},
        {"id": "stage_table_block", "type": "table", "tableId": "stage_table", "layout": "full"},
        {"id": "module_section", "type": "markdown", "sourceId": "trajectory_audit", "body": "## Module Improvement Priorities\n\n**先做 semantic closure planner 和 implementation/repair loop。** 它们分别直接对应 85 和 80 条失败，理论绝对通过率上限为 +15.5 pp 和 +14.5 pp。Budgeted exploration scheduler 对 pass 的上限较小（+5.8 pp），但预算失败 median 为 3.41M token，效率价值很高。Targeted runtime semantics 的上限为 +7.8 pp，但证据仍不足，应按风险触发并通过随机对照验证。", "layout": "full"},
        {"id": "module_chart", "type": "chart", "chartId": "module_ceiling", "layout": "full"},
        {"id": "module_table_block", "type": "table", "tableId": "module_table", "layout": "full"},
        {"id": "cold_start_section", "type": "markdown", "sourceId": "trajectory_audit", "body": "## Cold-start Diagnosis\n\n**Navigation cold start is small; semantic-state cold start remains.** Correct entry files were directly observed in 523/550 runs. Among those runs, the median first-entry point was the third Agent action and 90.8% reached it within five actions. Only 5 failures were classified as localization. In contrast, an explicit closure plan appeared in only 62/550 runs, so every run largely reconstructs API, dependency, runtime-risk, and verification state from scratch.", "layout": "full"},
        {"id": "cold_start_metrics", "type": "metric-strip", "cardIds": ["entry_observed", "entry_within_five", "closure_plan"], "layout": "full"},
        {"id": "cold_start_chart", "type": "chart", "chartId": "cold_start_actions", "layout": "full"},
        {"id": "cold_start_caveat", "type": "markdown", "sourceId": "trajectory_audit", "body": "## Cold-start Evidence Boundary\n\nFinding the entry after more than five actions was associated with 37.5% pass versus 42.1% within five actions, but only 48 runs were in the late group and pass rates were not monotonic across action bands. This is descriptive, not evidence that navigation delay causes failure. The stronger architectural signal is the absence of a persistent semantic closure artifact, which still requires an intervention experiment to quantify.", "layout": "full"},
        {"id": "dynamic_section", "type": "markdown", "sourceId": "trajectory_audit", "body": "## Dynamic Runtime Comparison\n\n主调整模型控制 model、split、任务快照 LOC、reference LOC、public-test 数和 entanglement 数；dynamic 对成功的 OR=1.16（95% CI 0.54–2.48）。加入 condensation 与 unchanged repeated-read 后，两者也没有稳定的独立关联。由于标签、探针和 condensation 都非随机，这些结果只能解释为关联。", "layout": "full"},
        {"id": "dynamic_chart", "type": "chart", "chartId": "dynamic_static", "layout": "full"},
        {"id": "cases_section", "type": "markdown", "body": "## Representative Cases\n\n下面的 16 条覆盖 boundary、budget、dependency、dynamic、implementation 与 verification。完整档案回答 Agent 已知信息、遗漏可见性、探针机会、发现/遗忘时序和最可能干预。", "layout": "full"},
        {"id": "case_table_block", "type": "table", "tableId": "case_table", "layout": "full"},
        {"id": "limitations", "type": "markdown", "sourceId": "trajectory_audit", "body": "## Evidence Boundaries\n\n**可以确认：** outcome 漏斗、API/forbidden-import 错误、明确 step/timeout、288 条 condensation run 与 552 次 condensation。\n\n**不能确认：** dynamic coupling、high token、repeated reads 或 condensation 的因果效应；clean-install 成功率（实际执行 0/550）；64k/128k/256k 窗口效应；精确 runtime closure recall。216 条 dependency 阶段仍为 unknown，symbol/runtime-state gold 尚未完成人工双审。", "layout": "full"},
        {"id": "next_steps", "type": "markdown", "body": "## Recommended Next Experiments\n\n1. 在 dynamic/static 分层任务上比较 default 与 mandatory targeted runtime probe。\n2. 做 dependency-hint、runtime-trace、extra-token 三臂配对实验。\n3. 固定预算比较 default condenser 与 evidence-pinned memory。\n4. 同模型同任务同 seed 跑 64k/128k/256k，并加入真实 wheel/venv clean-install 门。\n5. 对 public-pass/hidden-fail 子集进行盲法双人 earliest-stage 金标。", "layout": "full"},
    ],
}

snapshot = {
    "version": 1,
    "generatedAt": generated_at,
    "status": "ready",
    "datasets": {
        "headline": [
            {
                "formal_pass_rate": 225 / 550,
                "public_hidden_fail_rate": 173 / 401,
                "dynamic_pass_gap": float(primary.loc[primary.group.eq("dynamic_runtime"), "pass_rate"].iloc[0] - primary.loc[primary.group.eq("relatively_static"), "pass_rate"].iloc[0]),
                "infrastructure_failures": 62,
            }
        ],
        "failure_stages": stages[["stage", "failures", "median_tokens", "median_tokens_m", "models", "tasks"]].to_dict("records"),
        "dynamic_comparison": dynamic_tidy,
        "module_priorities": priority_rows,
        "cold_start_headline": [
            {
                "entry_observed_rate": 523 / 550,
                "entry_within_five_rate": 475 / 523,
                "closure_plan_rate": float(audit.closure_plan_present.mean()),
            }
        ],
        "cold_start_actions": cold_start.to_dict("records"),
        "representative_cases": case_rows,
    },
}

artifact = {"surface": "report", "manifest": manifest, "snapshot": snapshot, "sources": [audit_source]}
(HERE / "artifact.json").write_text(json.dumps(artifact, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(artifact, ensure_ascii=False))
