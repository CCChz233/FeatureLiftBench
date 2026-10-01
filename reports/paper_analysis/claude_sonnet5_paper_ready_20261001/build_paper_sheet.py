#!/usr/bin/env python3
"""Assemble Claude numbers in the paper's table units."""

from __future__ import annotations

import csv
import json
import math
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ANALYSIS = ROOT / "reports/paper_analysis/claude_sonnet5_full_source_20260930"
PAIRED = ROOT / "reports/paper_analysis/claude_sonnet5_paired_20261001"
OFFICIAL_EXPOSURE = ROOT / "reports/paper_analysis/source_exposure/diagnosis/run_exposure.csv"
TAXONOMY = ROOT / "artifacts/research_analysis/python150_task_taxonomy.csv"

MECHANISMS = {
    "Code dependencies": {"static_transitive_dependency", "implicit_runtime_dependency", "third_party_contract"},
    "Data and state": {"data_model_invariant", "parser_state", "global_state_registry"},
    "Framework mechanisms": {"framework_lifecycle", "dynamic_import_plugin"},
    "Environment and resources": {"config_environment", "resource_packaging"},
}
EXPOSURE_GROUPS = (
    ("Pass", {"functional_pass"}),
    ("Behavioral failure", {"public_failure", "hidden_failure"}),
    ("No submission or Build-first", {"missing_submission", "build_failure"}),
    ("Isolation-first", {"isolation_failure"}),
)


def quantile(values: list[float], q: float) -> float:
    values = sorted(values)
    at = q * (len(values) - 1)
    lo, hi = math.floor(at), math.ceil(at)
    if lo == hi:
        return values[lo]
    return values[lo] * (hi - at) + values[hi] * (at - lo)


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def fmt_iqr(median_value: float, q1: float, q3: float, digits: int = 2) -> str:
    return f"{median_value:.{digits}f} [{q1:.{digits}f}, {q3:.{digits}f}]"


def exposure_rows(rows: list[dict]) -> list[dict]:
    out = []
    for label, outcomes in EXPOSURE_GROUPS:
        group = [row for row in rows if row["outcome"] in outcomes]
        exposed = [row for row in group if row["entrypoint_explicit_read"] == "1"]
        steps = [float(row["first_explicit_read_action_step"]) for row in exposed]
        out.append(
            {
                "outcome": label,
                "runs": len(group),
                "exposed": len(exposed),
                "exposed_percent": (100 * len(exposed) / len(group)) if group else "",
                "median_first_read": statistics.median(steps) if steps else "",
            }
        )
    return out


def main() -> None:
    tasks = read_csv(ANALYSIS / "task_results.csv")
    artifacts = read_csv(ANALYSIS / "fig08_artifacts.csv")
    checkpoints = read_csv(ANALYSIS / "fig07_checkpoints.csv")
    paired = json.loads((PAIRED / "paired_claude_150_stats.json").read_text())
    exposure = read_csv(ANALYSIS / "source_exposure" / "summary_by_model_outcome.csv")
    qualitative = read_csv(ANALYSIS / "qualitative_claude_6.csv")
    fig08 = read_csv(ANALYSIS / "fig08_seven" / "fig08_seven_task_bootstrap.csv")
    assert len(tasks) == 150 and len(artifacts) == 89 and len(checkpoints) == 150

    passed = [row for row in tasks if row["functional_pass"] == "1"]
    steps = [float(row["assistant_steps"]) for row in tasks]
    tokens = [float(row["total_tokens"]) for row in tasks if row["usage_unverified"] == "False"]
    assert len(passed) == 89 and len(steps) == 150 and len(tokens) == 150
    rres = [float(row["rres"]) for row in artifacts]
    copy = [float(row["copied_fraction"]) for row in artifacts]
    main = {
        "configuration": "Claude Sonnet 5",
        "pass_n": 89,
        "pass_percent": 100 * 89 / 150,
        "pass_cell": "89 (59.3)",
        "rres_median_iqr": fmt_iqr(statistics.median(rres), quantile(rres, 0.25), quantile(rres, 0.75)),
        "copy_median_iqr": fmt_iqr(statistics.median(copy), quantile(copy, 0.25), quantile(copy, 0.75)),
        "steps_median": f"{statistics.median(steps):.1f}",
        "steps_p90": f"{quantile(steps, 0.9):.1f}",
        "tokens_median_millions": f"{statistics.median(tokens) / 1e6:.2f}",
        "tokens_p90_millions": f"{quantile(tokens, 0.9) / 1e6:.2f}",
    }
    write_csv(HERE / "table_main_claude.csv", [main])

    labels = {}
    for row in read_csv(TAXONOMY):
        labels[row["task_id"]] = set(filter(None, row["normalized_entanglement_types"].split(";")))
    assert set(labels) >= {row["task_id"] for row in tasks}
    structure = []
    for lift in ("Direct", "Adapted", "Composite"):
        subset = [row for row in tasks if row["lift_type"] == lift]
        structure.append(
            {
                "task_structure": lift,
                "n": len(subset),
                "pass": sum(row["functional_pass"] == "1" for row in subset),
                "pass_percent": f"{100 * sum(row['functional_pass'] == '1' for row in subset) / len(subset):.1f}",
            }
        )
    for name, tags in MECHANISMS.items():
        subset = [row for row in tasks if labels[row["task_id"]] & tags]
        structure.append(
            {
                "task_structure": name,
                "n": len(subset),
                "pass": sum(row["functional_pass"] == "1" for row in subset),
                "pass_percent": f"{100 * sum(row['functional_pass'] == '1' for row in subset) / len(subset):.1f}",
            }
        )
    write_csv(HERE / "table_structure_claude.csv", structure)

    official = exposure_rows(read_csv(OFFICIAL_EXPOSURE))
    expected = {
        "Pass": (492, 363, 5),
        "Behavioral failure": (303, 241, 5),
        "No submission or Build-first": (101, 51, 5),
        "Isolation-first": (4, 4, 10.5),
    }
    for row in official:
        runs, exposed, step = expected[row["outcome"]]
        if (row["runs"], row["exposed"], row["median_first_read"]) != (runs, exposed, step):
            raise SystemExit(f"official exposure median drifted: {row}")
    claude_exposure = read_csv(ANALYSIS / "source_exposure" / "run_exposure.csv")
    combined = exposure_rows(read_csv(OFFICIAL_EXPOSURE) + claude_exposure)
    for row in combined:
        row["exposed_cell"] = (
            f"{row['exposed']}/{row['runs']} ({row['exposed_percent']:.1f})" if row["runs"] else ""
        )
        row["median_first_read"] = (
            f"{row['median_first_read']:g}" if row["median_first_read"] != "" else ""
        )
    write_csv(HERE / "table_exposure_1050.csv", combined)

    token_rows = [row for row in checkpoints if row["include_checkpoint"] == "True"]
    response_rows = [row for row in checkpoints if row["include_response"] == "True"]
    token_values = [100 * float(row["post_sufficiency_fraction"]) for row in token_rows]
    response_values = [int(row["post_responses"]) for row in response_rows]
    fig07 = [
        {
            "panel": "post_pass_tokens_percent",
            "n": len(token_values),
            "median_iqr": fmt_iqr(statistics.median(token_values), quantile(token_values, 0.25), quantile(token_values, 0.75), 1)
            if token_values
            else "",
        },
        {
            "panel": "post_pass_responses",
            "n": len(response_values),
            "median_iqr": fmt_iqr(
                float(statistics.median(response_values)),
                quantile([float(v) for v in response_values], 0.25),
                quantile([float(v) for v in response_values], 0.75),
                1,
            )
            if response_values
            else "",
        },
    ]
    write_csv(HERE / "fig07_claude_summary.csv", fig07)

    stages = Counter(row["first_failure_stage"] for row in tasks)
    claude = paired["claude"]
    ci = claude["paired_bootstrap_95ci_pp"]
    holm_lines = []
    for row in sorted(paired["holm_four_configurations"], key=lambda item: item["mcnemar_exact_p"]):
        holm_lines.append(
            f"| {row['configuration']} | {row['full_only']} | {row['contract_only']} | {row['mcnemar_exact_p']:.2e} | {row['holm_p']:.2e} |"
        )
    behavior_exposed = next(
        row
        for row in exposure
        if row["model"] == "openai/claude-sonnet-5" and row["outcome_group"] == "Behavioral-first failure"
    )
    themes = Counter(row["theme"] for row in qualitative)
    text = f"""# Claude Sonnet 5，可直接写入论文的数字

功能通过 = Build ∧ Primary ∧ Extended ∧ Isolation。空提交留在分母里。`run.status` 不作为分数。Token 用 prompt + completion，含缓存输入，表内单位是百万。RRES 和 Copy 只在 89 个成功产物上计算。分位数是论文里的线性插值。

原始逐题表仍在 `reports/paper_analysis/claude_sonnet5_full_source_20260930/` 和 `reports/paper_analysis/claude_sonnet5_paired_20261001/`。

## 排名

按 Full Source 通过数：OSS 36，Qwen 63，GLM 68，Claude 89，Luna 102，Flash 108，Pro 115。

## 主表一行

| Configuration | Pass n (%) | RRES Median [IQR] | Copy Median [IQR] | Steps Median | Steps P90 | Tokens (M) Median | Tokens (M) P90 |
| --- | --- | --- | --- | --- | --- | ---: | ---: |
| Claude Sonnet 5 | {main['pass_cell']} | {main['rres_median_iqr']} | {main['copy_median_iqr']} | {main['steps_median']} | {main['steps_p90']} | {main['tokens_median_millions']} | {main['tokens_p90_millions']} |

成功产物 89。步数和 token 的分母都是 150，且 150 题 token 都已核对。

按构造组：core100 78/100（78.0%），hard50 11/50（22.0%）。

## 结构表，Claude 列

Lift type 互斥。四个机制重叠，一组任务可以同时计入多行。分母与现有表相同。

| Task structure | n | Claude pass | Claude % |
| --- | ---: | ---: | ---: |
{chr(10).join(f"| {row['task_structure']} | {row['n']} | {row['pass']} | {row['pass_percent']} |" for row in structure)}

## RQ2 配对

Full 89/150，Contract 53/150。都过 40，只 Full 49，只 Contract 13，都不过 48。

Δ = {claude['delta_pp']:.1f} pp，95% 配对任务 bootstrap [{ci[0]:.1f}, {ci[1]:.1f}]。仓库聚类区间 [{claude['repository_cluster_bootstrap_95ci_pp'][0]:.1f}, {claude['repository_cluster_bootstrap_95ci_pp'][1]:.1f}]，表内用任务 bootstrap。

两臂评测胶囊摘要不一致的题：0。

Holm 是四个配置一起校正。Luna、Pro、Qwen 的原始 p 不变，校正后的 p 比现在正文里的三配置 Holm 更大。

| Configuration | Only Full | Only Contract | Raw p | Holm p |
| --- | ---: | ---: | ---: | ---: |
{chr(10).join(holm_lines)}

| Lift | n | Full | Contract | Both | Only Full | Only Contract | Neither |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(f"| {row['lift_type']} | {row['n']} | {row['full_pass']} | {row['contract_pass']} | {row['both']} | {row['full_only']} | {row['contract_only']} | {row['neither']} |" for row in paired['by_lift_type'])}

逐题分类：`paired_claude_150.csv` 的 `pair_class`。

## RQ3 第一失败关和源码暴露

Full Source 第一失败关：通过 89，Primary 39，Extended 20，Build 2。没有缺交，没有 Isolation-first。行为失败 59。

Claude 行为失败中确认读过入口关联源码：{behavior_exposed['confirmed_explicit_read_runs']}/{behavior_exposed['all_runs']}（{float(behavior_exposed['confirmed_explicit_read_percent']):.1f}%），首次阅读步数中位 {float(behavior_exposed['median_first_explicit_read_action_step']):g}。

下面是六配置加 Claude 的 1050 行。中位数用确认阅读的那些 run 重算，不是把两组中位数平均。

| Outcome | Runs | Source-exposed | Median first read |
| --- | ---: | --- | ---: |
{chr(10).join(f"| {row['outcome']} | {row['runs']} | {row['exposed_cell']} | {row['median_first_read']} |" for row in combined)}

行为失败因此是 {combined[1]['exposed']}/{combined[1]['runs']}（{combined[1]['exposed_percent']:.1f}%）。原来的 241/303 不要再单独当总分母。

## Fig. 7

两块面板样本不同。未纳入的行不要填 0，原因在 `fig07_checkpoints.csv` 的 `exclusion_reason`。

| Panel | Eligible n | Median [IQR] |
| --- | ---: | --- |
| Post-pass tokens (%) | {fig07[0]['n']} | {fig07[0]['median_iqr']} |
| Subsequent responses | {fig07[1]['n']} | {fig07[1]['median_iqr']} |

点值：token 用 `include_checkpoint=True` 的 `post_sufficiency_fraction`（乘 100 得到百分数）；回复用 `include_response=True` 的 `post_responses`。

## Fig. 8

成功产物逐题值：`fig08_artifacts.csv`，89 行。失败题没有足迹。

七配置任务固定效应，10,000 次任务聚类 bootstrap，和为零中心。样本 116 题、574 个产物、98 个仓库。这不是原来六配置表上的系数。

| Configuration | Included n | RRES ratio [95% CI] | Copy pp [95% CI] |
| --- | ---: | --- | --- |
{chr(10).join(f"| {row['configuration']} | {row['included_success_n']} | {float(row['rres_ratio']):.3f} [{float(row['rres_ci_low']):.3f}, {float(row['rres_ci_high']):.3f}] | {float(row['copy_pp']):+.2f} [{float(row['copy_ci_low']):+.2f}, {float(row['copy_ci_high']):+.2f}] |" for row in fig08)}

任务等权和仓库聚类在 `fig08_seven/fig08_seven_results.md`。方向一致。没有不连通的抽样被丢弃。

## 定性 46 例

旧 40 例不动。新增 6 例，助手编码，没有独立人工复核。主题计数：C {themes['C']}，B {themes['B']}，其他 {themes['O']}，A 0。没有新的主题类别。

| Case | Task | Theme |
| --- | --- | --- |
{chr(10).join(f"| {row['case_id']} | {row['task_id']} | {row['theme']} |" for row in qualitative)}

选择规则和依据在 `qualitative_claude_6.csv`。
"""
    (HERE / "PAPER_NUMBERS.md").write_text(text)
    print(HERE / "PAPER_NUMBERS.md")


if __name__ == "__main__":
    main()
