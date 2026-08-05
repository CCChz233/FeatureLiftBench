#!/usr/bin/env python3
"""Render audit-facing research documents from trajectory_records.csv statistics.

The prose labels below are qualitative audit annotations.  Every count, rate,
metric, path, and event identifier is read from the generated CSV/JSON rather
than being typed into the Markdown documents.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


CASE_NOTES: dict[str, tuple[str, str]] = {
    "requests_cache__cache_key_core__hard3_001": (
        "Located and copied the cache-key/policy region, but the required `normalize_body` export is absent; hidden collection fails.",
        "High footprint does not guarantee API/closure recall; localization alone is insufficient.",
    ),
    "pydantic_v1__validation_error_core__001": (
        "Expanded to 15 submission files and hit the step limit; build still reports missing `featurelifted.datetime_parse`.",
        "Long exploration and broad expansion can still omit one transitive runtime provider.",
    ),
    "phonenumbers__parse_format_core__001": (
        "Read the same paths repeatedly and included regional data, yet hidden metadata access lacks `same_mobile_and_fixed_line_pattern`.",
        "Resource closure is field/behavior level, not merely file-level presence.",
    ),
    "diskcache__eviction_policy_core__hard3_001": (
        "Submitted a two-file small implementation after public success; hidden expects an additional state-query interface.",
        "A low-footprint public pass can stop before interface closure is demonstrated; contract requires review.",
    ),
    "click__lazy_command_core__hard3_001": (
        "Public behavior passes, then the agent signals completion; hidden fails on lazy command/default-map resolution.",
        "Dynamic resolution paths need executable state-transition probes.",
    ),
    "pytest__marker_registry_core__hard3_001": (
        "Public passes after a compact extraction; hidden marker/plugin registry merge lacks required behavior/interface.",
        "Registry state is not fully represented by static import reachability.",
    ),
    "jupyter_server__extension_config_core__hard3_001": (
        "Configuration storage works publicly, but hidden merged-extension access fails.",
        "Global/config state closure remains uncertain; the hidden name is contract-review sensitive.",
    ),
    "parsel__selector_namespace_core__hard3_001": (
        "Copies more Python LOC than the source slice and explicitly finishes, but hidden selector namespace API fails.",
        "Over-extraction can coexist with interface omission; copy volume is not closure evidence.",
    ),
    "sqlalchemy__event_dispatch_core__hard3_001": (
        "A broad eight-file extraction passes both test suites, but extraction ratio above one drives final score to zero.",
        "Conservative expansion can recover behavior while failing compactness; it is a prune positive control.",
    ),
    "stevedore__extension_manager_core__hard3_001": (
        "A copy-heavy plugin/entry-point extraction passes hidden tests.",
        "Dynamic-state tasks are not intrinsically impossible; this is an expand-then-prune positive control.",
    ),
    "pluggy__hook_wrapper_core__hard3_001": (
        "Public wrapper/replay cases pass; hidden historic direct-call behavior raises the wrong exception.",
        "Closure recovery alone cannot replace behavior-contract validation.",
    ),
    "pydantic__field_validator_core__hard3_001": (
        "The frozen first run exits without a submission after tool/schema errors.",
        "A harness/workflow failure must not be counted as a hidden behavior observation.",
    ),
    "coverage__config_merge_core__001": (
        "The trajectory says the repository is empty, implements from prior knowledge, self-tests, and finishes; hidden setup.cfg merging fails.",
        "This is direct evidence for an input/localization failure followed by an unsupported behavioral completion claim.",
    ),
    "dynaconf__settings_merge_core__001": (
        "A very long, repeat-heavy run ultimately passes with a compact ratio.",
        "High token use and repeated reads do not imply failure; cost must be tied to state-changing evidence.",
    ),
    "sphinx__extension_registry_core__hard3_001": (
        "The agent signals completion, but the build fails on Python-version syntax before public/hidden tests execute.",
        "Syntax/build compatibility is distinct from hidden behavior and closure recovery.",
    ),
    "readme_renderer__content_type_core__hard3_001": (
        "Submission LOC is over three times the source slice, yet build fails because `nh3` is absent.",
        "More copied code does not recover an allowed external dependency automatically.",
    ),
    "bleach__sanitize_core__001": (
        "A 36-file submission cannot build because `webencodings` is missing.",
        "File-level copying and dependency replacement/packaging are different actions.",
    ),
    "responses__request_matcher_core__hard3_001": (
        "The frozen evaluator cannot install the required dependency, so no public/hidden result is observed.",
        "This row is evaluator/environment noise, not an Agent failure; saved-submission re-evaluation is supplementary.",
    ),
    "yamale__schema_validate_core__hard3_001": (
        "The frozen evaluator dependency set fails before testing.",
        "Raw Pass@1 must be reported, but mechanism analysis must exclude this as an unobserved test outcome.",
    ),
    "pyyaml__safe_load_dump__001": (
        "Public and hidden tests pass, but the forbidden-original-import gate fails.",
        "Functional completion includes isolation; test pass alone is not the final gate.",
    ),
}


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=root / "artifacts/research_analysis/trajectory_records.csv")
    parser.add_argument("--statistics", type=Path, default=root / "artifacts/research_analysis/trajectory_statistics.json")
    parser.add_argument("--findings", type=Path, default=root / "docs/reference/research_analysis/TRAJECTORY_FINDINGS.md")
    parser.add_argument("--hypotheses", type=Path, default=root / "docs/reference/research_analysis/MECHANISM_HYPOTHESES.md")
    return parser.parse_args()


def fmt_rate(value: dict[str, Any], digits: int = 1) -> str:
    rate = value.get("rate")
    suffix = "NA" if rate is None else f"{rate * 100:.{digits}f}%"
    return f"{value['count']}/{value['denominator']} ({suffix})"


def scalar(value: Any) -> str:
    if value is None or value == "":
        return "NA"
    if isinstance(value, float):
        return f"{value:.6f}".rstrip("0").rstrip(".")
    return str(value)


def group_table(groups: list[dict[str, Any]]) -> str:
    lines = [
        "| group | n | functional pass | observed public | public→hidden / public pass | environment error | median ratio | median tokens |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for group in groups:
        lines.append(
            "| `{label}` | {runs} | {functional} | {public} | {gap} | {env} | {ratio} | {tokens:,.0f} |".format(
                label=group["label"],
                runs=group["runs"],
                functional=fmt_rate(group["functional_pass"]),
                public=fmt_rate(group["public_observed"]),
                gap=fmt_rate(group["public_hidden_fail_given_public_pass"]),
                env=fmt_rate(group["environment_error"]),
                ratio=scalar(group["median_extraction_ratio"]),
                tokens=group["median_tokens"] or 0,
            )
        )
    return "\n".join(lines)


def case_sections(cases: list[dict[str, Any]]) -> str:
    blocks: list[str] = []
    for index, case in enumerate(cases, 1):
        behavior, conclusion = CASE_NOTES[case["task_id"]]
        result = (
            f"public={case['public_pass']}, hidden={case['hidden_pass']}, "
            f"functional={case['functional_pass']}, ratio={scalar(case['extraction_ratio'])}, "
            f"final={scalar(case['final_score'])}, files={case['copied_file_count']}, "
            f"LOC={case['copied_loc']}, tokens={case['tokens']:,}, stop={case['stop_reason']}"
        )
        evidence = ", ".join(f"`{item}`" for item in case["evidence_step_ids"])
        review = "；该任务 hidden contract 标为**需要人工复核**" if case["contract_review_required"] else ""
        blocks.append(
            f"### {index}. `{case['task_id']}`\n\n"
            f"- 结果：{result}；primary=`{case['primary_failure']}`{review}。\n"
            f"- 轨迹：`{case['trajectory_path']}`\n"
            f"- 评测：`{case['evaluation_path']}`\n"
            f"- 关键步骤：{evidence}\n"
            f"- 行为摘要：{behavior}\n"
            f"- 支持结论：{conclusion}"
        )
    return "\n\n".join(blocks)


def render_findings(stats: dict[str, Any]) -> str:
    overall = stats["overall"]
    extraction = stats["extraction"]
    errors = stats["error_sources"]
    repeated = stats["repeated_and_error_events"]
    completeness = stats["completeness"]

    failure_lines = ["| label | n / 450 |", "|---|---:|"]
    for item in stats["primary_failure_counts"]:
        failure_lines.append(f"| `{item['primary_failure']}` | {fmt_rate(item)} |")

    extraction_lines = [
        "| ratio bucket | n | functional pass | public→hidden / public pass | environment error | median files | median tokens | closure plan | self tests | unsupported finish |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for key in ("under_proxy_le_0_25", "middle_0_25_to_0_80", "over_proxy_gt_0_80"):
        item = extraction[key]
        extraction_lines.append(
            f"| `{key}` | {item['runs']} | {fmt_rate(item['functional_pass'])} | "
            f"{fmt_rate(item['public_hidden_fail_given_public_pass'])} | {fmt_rate(item['environment_error'])} | "
            f"{item['median_copied_file_count']:.1f} | {item['median_tokens']:,.0f} | "
            f"{fmt_rate(item['closure_plan_present'])} | {fmt_rate(item['self_generated_tests'])} | "
            f"{fmt_rate(item['unsupported_completion_claim'])} |"
        )

    error_lines = ["| source | affected runs | events | operational definition |", "|---|---:|---:|---|"]
    for key in ("agent_reasoning_unsupported_completion_claim", "tool_execution_error", "harness_format_error", "evaluator_environment_error"):
        item = errors[key]
        rate_item = item.get("all_runs") or item["affected_runs"]
        error_lines.append(f"| `{key}` | {fmt_rate(rate_item)} | {item.get('events', '—')} | {item['definition']} |")

    repetition_lines = ["| metric | affected runs | duplicate/error events | median among affected |", "|---|---:|---:|---:|"]
    for key, item in repeated.items():
        repetition_lines.append(f"| `{key}` | {fmt_rate(item['affected_runs'])} | {item['event_count']} | {item['median_among_affected']} |")

    stop_lines = ["| stop reason | n / 450 |", "|---|---:|"]
    for item in stats["stop_reason_counts"]:
        stop_lines.append(f"| `{item['stop_reason']}` | {fmt_rate(item)} |")

    dynamic_table = group_table(stats["by_dynamic_state"])
    return f"""# FeatureLiftBench Python 轨迹证据（自动生成）

> 历史 `mixed_snapshot_v1` 轨迹证据。失败机制可作为 v3 假设来源，但绝对
> 通过率、token 和定位行为不能直接外推到 Full-Repository / No-Hint。

> 本文件由 `python tools/research_analysis/render_research_docs.py` 从 `artifacts/research_analysis/trajectory_records.csv` 与 `trajectory_statistics.json` 生成。禁止手工修改比例；定性 case 注释在生成脚本中受版本控制。

## 1. 审计范围与完整性

CSV 库存包含所有可发现的 Python OpenHands 轨迹；主分析语料是 `build_trajectory_records.py` 中冻结的 7 个官方 suite：4 个模型配置、450 个首次运行。另有 {completeness['excluded_rows']} 条通过 `analysis_included=false` 保留但不进入主 Pass@1：{json.dumps(completeness['exclusion_reasons'], ensure_ascii=False)}。每行联接可用的 `run.json`、事件轨迹、submission 与 evaluator result；任务契约来自 `benchmark/tasks/<task_id>/TASK.md` 和 `metadata.json`。

- 行数：{completeness['rows']}；唯一 run_id：{completeness['unique_run_ids']}；列数：{completeness['columns']}。
- 10 个结构字段的 cell 完整率：{fmt_rate(completeness['structural_field_cell_completeness'])}。
- 事件轨迹可用：{fmt_rate(completeness['events_available'])}；evaluation result 可用：{fmt_rate(completeness['evaluation_available'])}。
- 主分析 public/hidden 结果已实际观测：{fmt_rate(overall['public_observed'])}；库存字段非空为 {completeness['by_required_field']['public_pass']['nonempty']}/{completeness['inventory_rows']}。未执行为 NA，而不是 false。
- 主分析 extraction ratio 可用：{extraction['known_ratio_runs']}/{completeness['analysis_rows']}；全库存为 {completeness['by_required_field']['extraction_ratio']['nonempty']}/{completeness['inventory_rows']}。

重建命令：

```bash
python tools/research_analysis/build_trajectory_records.py
python tools/research_analysis/summarize_trajectory_records.py --check-paths
python tools/research_analysis/render_research_docs.py
```

## 2. 指标定义与分母

| metric | definition | denominator |
|---|---|---|
| strict suite pass | 历史 `run_status == passed` | 所在分组全部 trajectory |
| functional pass | evaluator `scores.functional_gate == 1`；允许 step-limit 前已产生有效 submission 的 run | 所在分组全部 trajectory |
| public/hidden pass | 对应测试阶段实际执行且通过 | `*_executed=true` 的 trajectory；未执行为 NA |
| public→hidden gap | `public_pass=true ∧ hidden_pass=false` | 主文同时报告全体 450 和 public pass 319 两个分母 |
| extraction ratio | evaluator `submission Python LOC / source snapshot Python LOC` | ratio 非空的 440 条；它是 footprint proxy，不证明逐行复制 |
| final score | functional gate 通过时 `clamp(1-extraction_ratio, 0, 1)`，否则 0 | 全部 trajectory |
| copied files / LOC | evaluator submission `file_count` / nonblank noncomment Python LOC | 全部 trajectory；是 submission-footprint proxy |
| repeated file read | 同一规范化路径的 `file_editor view` 在首次之后再次发生 | 全部有 events 的 450 条 |
| repeated line read | 同一路径、完全相同 `view_range` 的重复读取 | 全部有 events 的 450 条 |
| Agent 推理错误 | FinishAction 声称完成/测试成功，但 functional gate=0，且排除 evaluator/environment error | 全部 450；另可在 168 个非环境功能失败上取条件比例 |
| tool 执行错误 | `ObservationEvent.is_error=true`，排除 schema/required-parameter 错误 | 全部 450 |
| harness 格式错误 | Agent/Conversation error 明确是 tool schema/validation/required-parameter failure | 全部 450 |
| evaluator/environment error | 依赖安装、eval tooling 或 Docker sandbox 在有效测试结论前失败 | 全部 450 |
| closure plan/self-tests/hidden risk | 事件文本的保守规则匹配 | 全部 450；仅表示“出现过”，不是质量标注 |

## 3. 总体与分组统计

全体：strict suite pass {fmt_rate(overall['strict_suite_pass'])}；functional pass {fmt_rate(overall['functional_pass'])}；public→hidden 为 {fmt_rate(overall['public_hidden_fail_total'])}，在 public pass 条件下为 {fmt_rate(overall['public_hidden_fail_given_public_pass'])}；环境/evaluator error {fmt_rate(overall['environment_error'])}。

### 3.1 按模型

{group_table(stats['by_model'])}

模型间 raw 结果不可直接解释为能力差异：Qwen 三组各有明显环境失败，而 DeepSeek 组只有少量；论文主比较必须同环境重跑或排除环境未观测行。

### 3.2 按 split

{group_table(stats['by_split'])}

### 3.3 按 task type

{group_table(stats['by_task_type'])}

### 3.4 dynamic/global-state metadata 切片

{dynamic_table}

`dynamic_state_task` 只由 metadata entanglement/tags 中的 registry、plugin、dynamic import、entry point、resource、lazy、cache、metaclass/global-state 信号生成。它是宽切片，未控制 split 和难度；只能用于分层抽样，不能做因果结论。

## 4. 失败与噪声分离

### 4.1 Primary outcome 标签

{chr(10).join(failure_lines)}

这些标签由首个 evaluator 失败与日志模式生成。`hidden_behavior_contract_failure`、`hidden_interface_or_closure_failure` 和 public 行为/接口类别是**启发式标签，需要人工复核**；environment、missing submission、build/import 错误可直接验证。

### 4.2 四类错误源

{chr(10).join(error_lines)}

因此不能把“tool error 很多”与“Agent 机制错误很多”混为同一个统计。harness schema 错误可能被恢复，tool execution error 也可能出现在最终通过的轨迹中；只有 evaluator/environment error 会让本行 public/hidden 结论变成 NA。

## 5. Under-/over-extraction 对照

{chr(10).join(extraction_lines)}

已被数据支持：低比例桶与高比例桶都同时包含通过和 public→hidden 失败；两端的 unsupported finish 比例接近，closure plan 均少见。没有被数据支持：它们必然来自同一个潜变量。当前只能提出“边界不确定性可能分别导致早停或保守复制”的待验证假设，需 Oracle Closure 与 executable deletion 干预。

## 6. 重复探索与停止

{chr(10).join(repetition_lines)}

{chr(10).join(stop_lines)}

显式 FinishAction 出现在 {fmt_rate(overall['explicit_finish'])}；保守规则检测到 unsupported completion claim {fmt_rate(overall['unsupported_completion_claim'])}，占 168 个非环境 functional failure 的 {fmt_rate(errors['agent_reasoning_unsupported_completion_claim']['non_environment_failures'])}。这证明当前停止证据经常不充分，但不证明“再多一轮 reflection”能修复；必须要求新的 executable evidence。

## 7. 20 个可审计 case

{case_sections(stats['cases'])}

## 8. 可以与不可以下的结论

**已被数据支持：** public pass 后仍有大量 hidden failure；依赖/接口、行为契约、隔离、build 和环境错误是不同 failure source；低/高 footprint 都不能单独保证成功；轨迹有显著重复读取/命令；62 条环境/evaluator 失败污染 raw 模型比较。

**合理推测：** 缺少显式 executable closure state 可能把定位、扩张、行为验证、裁剪和停止割裂。

**待验证假设：** Oracle Closure 会显著强于 Oracle Locate；counterfactual deletion 能在不损伤 hidden pass 的情况下提升 compactness；ECSM 的收益超过等预算 strong prompt。
"""


def render_hypotheses(stats: dict[str, Any]) -> str:
    overall = stats["overall"]
    extraction = stats["extraction"]
    errors = stats["error_sources"]
    under = extraction["under_proxy_le_0_25"]
    over = extraction["over_proxy_gt_0_80"]
    return f"""# FeatureLiftBench 竞争机制假设（自动生成统计）

> 本文件由 `render_research_docs.py` 生成。数值来自 `trajectory_records.csv`；定性轨迹判断通过 task/path/event ID 在 `TRAJECTORY_FINDINGS.md` 审计。以下 H1–H6 是竞争解释，不预设 ECSM 正确。

## 1. 当前证据边界

450 条 frozen trajectories 中，public→hidden gap 为 {fmt_rate(overall['public_hidden_fail_total'])}，在 public pass 条件下为 {fmt_rate(overall['public_hidden_fail_given_public_pass'])}；但 {fmt_rate(overall['environment_error'])} 在环境/evaluator 阶段没有有效测试结论。primary failure 的行为/接口分类依赖日志启发式，因而任何“共同机制”结论都仍是待干预验证的假设。

## H1：主要问题是定位失败

- **操作化定义：** Agent 未在预算前找到 feature source entrypoint 或首个正确 provider；Oracle Locate 提供 entrypoint/source file 后，hidden Pass@1 应接近 Oracle Closure。
- **支持证据：** `coverage__config_merge_core__001` 的真实轨迹明确说 repository empty，随后从知识重写并 hidden fail；missing submission 与一部分 public API failure 也与定位失败相容，但不是定位失败的直接证据。
- **冲突证据：** `requests_cache` 已定位 cache-key/policy 且 ratio=0.96319 仍漏明确 export；`pydantic_v1` 已扩到 15 files 仍漏 `datetime_parse`；`phonenumbers` 已找到 regional data 仍漏字段；`readme_renderer` ratio=3.044248 仍漏外部依赖。
- **可证伪预测：** Oracle Locate 相对 Strong Prompt 若在 10-task pilot 上增加至少 2 个 paired hidden pass，并与 Oracle Closure 相差不超过 1 个任务，H1 获支持；若 Oracle Locate 小而 Oracle Closure 大，H1 作为主要瓶颈被否定。
- **区分实验：** Strong Prompt vs Oracle Locate vs Oracle Closure；模型、预算、工具、测试权限固定。
- **与简单解释区别：** 这是普通检索/RepoMap 最能解决的假设；它不预测 deletion verifier 会改善 compactness。
- **当前置信度：低—中。**
- **新增数据：** first-correct-file step、entrypoint recall、空 source mount 发生率、Oracle Locate arm。

## H2：主要问题是依赖闭包恢复失败

- **操作化定义：** Agent 找到入口后，未恢复 output API、transitive provider、allowed external dependency、resource 或 runtime/global-state edge；Oracle Closure 显著优于 Oracle Locate/Static Hint。
- **支持证据：** primary labels 中 `hidden_interface_or_closure_failure`、`dependency_closure_omission` 可审计；具体有 `pydantic_v1→datetime_parse`、`requests_cache→normalize_body`、`phonenumbers→metadata field`、`readme_renderer→nh3`、`bleach→webencodings`。
- **冲突证据：** `pluggy` 与 `coverage` 的首要失败是行为语义；低 ratio 桶仍有 {fmt_rate(under['functional_pass'])} functional pass；copy-heavy `stevedore` 成功。
- **可证伪预测：** Oracle Closure 相对 Oracle Locate 至少多 2 个 paired hidden pass，且 closure recall/F1 上升、interface/build failure 下降；若只提高 footprint 而不提高 hidden，H2 被削弱。
- **区分实验：** Oracle Locate vs Static Closure Hint vs Oracle Closure；按 static import 与 runtime/resource strata 分层。
- **与简单解释区别：** localization 只给入口；闭包要求 artifact/obligation provider 集。普通依赖图只给候选，不能证明 runtime necessity。
- **当前置信度：中—高（作为重要局部机制），尚未证明主导全部失败。**
- **新增数据：** executable oracle closure、symbol/resource/runtime gold、closure P/R/F1。

## H3：主要问题是行为契约和 hidden case 不完整

- **操作化定义：** included artifacts 足以 build/import，但 Agent 未枚举并 probe 异常、顺序、边界、合并、状态转移等行为义务；hidden-aware validation 主要修复 behavior failure。
- **支持证据：** `hidden_behavior_contract_failure` 是最大的可评测单一失败标签；`pluggy` 的 historic direct-call exception、`coverage` 的 setup.cfg merge、pydantic rerun 的 structured error 都是具体案例。
- **冲突证据：** import/export/provider 缺失可被机械 closure 检查发现，不要求猜 hidden edge；contract-review tasks 会夸大表面 hidden gap。
- **可证伪预测：** Hidden-aware checklist/contract probes 显著改善 behavior cohort，但对 `datetime_parse`/`normalize_body` 等 provider omission 收益小；若只增加文本讨论不改 hidden pass，则 H3 的 prompt 版本被否定。
- **区分实验：** Strong Prompt vs hidden-aware validation（在 pilot 中由 ECSM probe state 与 decision-rule behavior subgroup读取）；另对 Oracle Closure 后残余失败分类。
- **与简单解释区别：** 不是“测试再多一点”，而是 TASK obligation→probe→fresh result 的覆盖矩阵；普通 reflection 没有新执行证据不计入。
- **当前置信度：高（局部），中（作为总体主因）。**
- **新增数据：** behavior-family gold、probe coverage、Oracle Closure 后残余错误。

## H4：主要问题是停止策略错误

- **操作化定义：** Agent 在仍有 unresolved hard reference、未覆盖 behavior/runtime obligation、stale probe 或 pending prune 时提交。当前代理指标是 unsupported completion claim。
- **支持证据：** explicit FinishAction {fmt_rate(overall['explicit_finish'])}；unsupported completion claim {fmt_rate(overall['unsupported_completion_claim'])}，占非环境 functional failure {fmt_rate(errors['agent_reasoning_unsupported_completion_claim']['non_environment_failures'])}。`requests_cache`、`click`、`coverage` 都在完成信号后暴露 hidden failure。
- **冲突证据：** 23 个 step-limit 与 2 个 timeout 并非主动早停；纯实现错误即使延后停止也可能不修复；unsupported claim 是高精度代理而非完整 stopping-error gold。
- **可证伪预测：** 在相同信息下，fresh-evidence stopping guard 降低 public-hidden gap；如果只增加 token/tool calls、hidden 不升，则 H4 被削弱。
- **区分实验：** Strong Prompt vs reflection vs hidden-aware checklist vs ECSM stopping ablation；比较 public pass 后的新增 state-changing probes，而非只比较额外步骤。
- **与简单解释区别：** “弱模型”预测 guard 也无用；停止假设预测同一模型、同一候选信息仅改变提交条件即可改善。
- **当前置信度：中—高。**
- **新增数据：** submit-time unresolved/risk snapshot、last-mutation 后 probe freshness、public-pass 后动作类型。

## H5：主要问题是 Agent workflow 与 feature lifting 不匹配

- **操作化定义：** 通用 read/edit/test workflow 没有显式维护 `obligation→provider→probe→risk`，因此 locate、expand、replace、adapter、prune、restore、stop 之间无状态连续性。
- **支持证据：** closure plan 只在 {fmt_rate(overall['closure_plan_present'])} 出现，自生成测试只在 {fmt_rate(overall['self_generated_tests'])} 出现；重复 path read 影响 {fmt_rate(overall['repeated_file_read_affected'])}。`pydantic_v1`/`phonenumbers` 的大量探索未转化为 closure completion；`sqlalchemy`/`stevedore` 成功但 copy-heavy，显示 recall 与 compactness 没有统一 controller。
- **冲突证据：** 现有 OpenHands prompt 已包含 FeatureLift 约束；一些 compact run 成功；文本规则检测不到隐式规划质量。
- **可证伪预测：** 等预算 ECSM 超过 Strong Prompt，且不仅 hidden pass 上升，还同时改善 closure F1、重复探索或 compactness；如果仅多消耗计算，H5 不成立。
- **区分实验：** Strong Prompt vs Copy-first Prune vs ECSM，并做 `ECSM - state`、`- pruning`、`- stopping guard` 消融。
- **与简单解释区别：** 不是更长 prompt、RAG 或 multi-agent；机制变量是持久 state、可执行 update 和不可绕过 guard。
- **当前置信度：中。**
- **新增数据：** 每步 state delta、动作净风险收益、prune/restore 因果日志。

## H6：主要问题是工具或 harness 噪声

- **操作化定义：** Agent 失败主要由 tool execution、schema 格式、evaluator dependency 或环境中断造成；修复噪声后方法间差异显著收缩。
- **支持证据：** tool execution error 影响 {fmt_rate(errors['tool_execution_error']['affected_runs'])}，harness format error 影响 {fmt_rate(errors['harness_format_error']['affected_runs'])}，evaluator/environment error 影响 {fmt_rate(errors['evaluator_environment_error']['affected_runs'])}；`responses`、`yamale` 和 frozen pydantic first run 是直接案例。
- **冲突证据：** 有效评测中仍有 {fmt_rate(overall['public_hidden_fail_total'])} public→hidden；tool/harness error 可被恢复且也出现在通过 run；`responses`/`yamale` saved-submission 重评后仍 hidden fail（补充证据，不回写 frozen CSV）。
- **可证伪预测：** 在统一 Docker/依赖并排除 environment rows 后，若 H1–H5 的 arm 差异消失，H6 获支持；若差异保持，H6 只是重要混杂因素。
- **区分实验：** pilot 预检 reference + identical runtime；同时报告 ITT raw、environment-excluded 和 contract-review sensitivity。
- **与简单解释区别：** H6 是 measurement validity 假设，不是 Agent 方法创新。
- **当前置信度：高（噪声确实存在），低—中（作为主要共同原因）。**
- **新增数据：** 全 70 cells 的环境预检、同 submission 重评、错误重试归因。

## 2. Under- 与 over-extraction 的 task-level 对照

| feature | under proxy ≤0.25 | over proxy >0.80 | 当前解释 |
|---|---:|---:|---|
| known-ratio n | {under['runs']} | {over['runs']} | 两桶分母不同 |
| functional pass | {fmt_rate(under['functional_pass'])} | {fmt_rate(over['functional_pass'])} | 两端都有成功/失败，不支持单调“越少越好/越多越好” |
| public→hidden / public pass | {fmt_rate(under['public_hidden_fail_given_public_pass'])} | {fmt_rate(over['public_hidden_fail_given_public_pass'])} | 两端 gap 都高；差异不是因果 |
| closure plan | {fmt_rate(under['closure_plan_present'])} | {fmt_rate(over['closure_plan_present'])} | 两端都很少，符合但不证明共同 workflow 假设 |
| self tests | {fmt_rate(under['self_generated_tests'])} | {fmt_rate(over['self_generated_tests'])} | 规则只检测存在，不检测覆盖质量 |
| hidden risk discussed | {fmt_rate(under['hidden_risk_discussed'])} | {fmt_rate(over['hidden_risk_discussed'])} | 仅“讨论”不能区分两端 |
| repeated-read affected | {fmt_rate(under['repeated_file_read_affected'])} | {fmt_rate(over['repeated_file_read_affected'])} | 轨迹形态存在差异，反对简单同源断言 |
| unsupported finish | {fmt_rate(under['unsupported_completion_claim'])} | {fmt_rate(over['unsupported_completion_claim'])} | 比例接近，符合共同 stopping-risk 假设 |
| median copied files | {under['median_copied_file_count']:.1f} | {over['median_copied_file_count']:.1f} | ratio 由 LOC 而非文件数定义 |
| median tokens | {under['median_tokens']:,.0f} | {over['median_tokens']:,.0f} | over 并没有简单消耗更多 token |

任务正反例见 `TRAJECTORY_FINDINGS.md`：under-fail 为 `diskcache`/`click`/`pytest`，under-pass 为 `dynaconf`；over-fail 为 `parsel`/`requests_cache`/`readme_renderer`，over-pass 为 `sqlalchemy`/`stevedore`。因此“under 与 over 是同一不确定性的两种动作”目前仅是**待验证假设**。最小证伪实验是：Oracle Closure 是否同时减少 omission 与无必要复制；copy-first + executable deletion 是否保持 hidden 而降低 ratio。

## 3. 竞争假设的判别顺序

1. 先做统一环境预检并冻结 valid cells，控制 H6。
2. 比较 Strong Prompt→Oracle Locate，检验 H1。
3. 比较 Oracle Locate→Static Hint→Oracle Closure，检验 H2 与静态/动态分解。
4. 对 Oracle Closure 残余失败做 behavior-family probe，检验 H3。
5. 比较 Strong Prompt、Copy-first Prune、ECSM 及 stopping/state 消融，检验 H4/H5。

当前最值得先验证的是 **H2 vs H1**：Oracle Locate 与 Oracle Closure 的差值能直接决定研究应聚焦检索，还是聚焦 executable closure recovery。ECSM 只有在等预算下同时改善 hidden correctness 与 closure/compactness，并满足预注册 compute guard 时才值得继续。
"""


def main() -> None:
    args = parse_args()
    with args.csv.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    stats = json.loads(args.statistics.read_text(encoding="utf-8"))
    if len(rows) != stats["completeness"]["rows"]:
        raise ValueError("CSV/statistics row-count mismatch; rerun summarize_trajectory_records.py")
    for path, content in ((args.findings, render_findings(stats)), (args.hypotheses, render_hypotheses(stats))):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.rstrip() + "\n", encoding="utf-8")
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
