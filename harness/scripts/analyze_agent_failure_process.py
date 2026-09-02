#!/usr/bin/env python3
"""Summarize trajectory-level failure annotations for a FeatureLiftBench suite.

This script deliberately separates three questions:

1. Was the evaluator expectation supported by the task contract?
2. What did the submitted artifact do incorrectly?
3. What observable agent process led to the incomplete artifact?

The semantic answers come from a reviewed annotation CSV.  Mechanical run and
trajectory signals are extracted from the preserved suite without re-running it.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

ALIGNMENTS = {"aligned", "ambiguous", "misaligned", "not_tested"}
PROCESS_CAUSES = {
    "false_contract_closure",
    "upstream_over_task_contract",
    "step_budget_exhaustion",
    "non_delivery",
    "not_attributable",
    "unknown",
}

ALIGNMENT_LABELS = {
    "aligned": "契约对齐",
    "ambiguous": "契约含糊",
    "misaligned": "评测越界",
    "not_tested": "未进入功能评测",
}

PROCESS_LABELS = {
    "false_contract_closure": "错误的契约闭合/自测未区分",
    "upstream_over_task_contract": "上游语义优先于任务契约",
    "step_budget_exhaustion": "步数与上下文预算耗尽",
    "non_delivery": "未形成提交",
    "not_attributable": "不可归因给 Agent",
    "unknown": "过程原因未确定",
}

CLAIM_RE = re.compile(r"\b(complete|completed|implemented|ready|done|verified)\b", re.I)
TEST_COMMAND_RE = re.compile(
    r"(?:python\d*\s+-m\s+pytest|\bpytest\b|"
    r"python\d*\s+[^\n;&|]*test[^\n;&|]*\.py|"
    r"python\d*\s+-c\s+[^\n]*\bassert\b)",
    re.I,
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def relpath(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def pct(numerator: int, denominator: int) -> str:
    return "—" if denominator == 0 else f"{numerator / denominator:.1%}"


def extract_trajectory_signals(task_dir: Path) -> dict[str, Any]:
    events_path = task_dir / "agent/openhands_events.jsonl"
    terminal_actions = 0
    file_edit_actions = 0
    finish_action = False
    completion_claim = False
    verification_actions = 0
    task_mentions = 0

    if events_path.is_file():
        with events_path.open(encoding="utf-8", errors="replace") as handle:
            for line in handle:
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get("source") != "agent":
                    continue
                action = event.get("action") or {}
                kind = action.get("kind")
                command = action.get("command") or ""
                if kind == "TerminalAction":
                    terminal_actions += 1
                    if TEST_COMMAND_RE.search(command):
                        verification_actions += 1
                    if "TASK.md" in command:
                        task_mentions += 1
                elif kind == "FileEditorAction":
                    file_edit_actions += 1
                    if str(action.get("path") or "").endswith("TASK.md"):
                        task_mentions += 1
                elif kind == "FinishAction":
                    finish_action = True

                message = event.get("llm_message") or {}
                if message.get("role") == "assistant" and not action:
                    text = " ".join(
                        item.get("text", "")
                        for item in (message.get("content") or [])
                        if isinstance(item, dict)
                    )
                    if CLAIM_RE.search(text):
                        completion_claim = True

    run_path = task_dir / "run.json"
    run = read_json(run_path) if run_path.is_file() else {}
    agent = run.get("agent") or {}
    usage = agent.get("usage") or {}
    context = usage.get("context_audit") or {}
    submission_dir = task_dir / "submission"
    submission_files = (
        sum(1 for path in submission_dir.rglob("*") if path.is_file())
        if submission_dir.is_dir()
        else 0
    )
    return {
        "terminal_actions": terminal_actions,
        "file_edit_actions": file_edit_actions,
        "verification_actions": verification_actions,
        "task_read_signal": task_mentions > 0,
        "finish_action": finish_action,
        "completion_claim": completion_claim or finish_action,
        "submission_files": submission_files,
        "agent_exit_status": usage.get("exit_status") or "unknown",
        "agent_api_calls": usage.get("api_calls") or 0,
        "assistant_steps": usage.get("assistant_steps") or 0,
        "context_violation": bool(context.get("context_violation")),
        "condensation_events": context.get("condensation_events") or 0,
        "timed_out": bool(agent.get("timed_out")),
        "trajectory_path": relpath(events_path),
    }


def validate_annotations(
    failures: list[dict[str, str]], annotations: list[dict[str, str]]
) -> dict[str, dict[str, str]]:
    required = {
        "task_id",
        "contract_alignment",
        "process_cause_primary",
        "process_secondary_tags",
        "alignment_reason",
        "process_evidence_summary",
        "review_status",
        "annotator",
        "adjudicated",
    }
    if not annotations:
        raise ValueError("process annotation CSV is empty")
    missing = required - set(annotations[0])
    if missing:
        raise ValueError(f"annotation CSV is missing fields: {sorted(missing)}")

    expected_valid = {
        row["task_id"]
        for row in failures
        if row["evidence_eligibility"] == "valid_agent_evidence"
    }
    failure_by_task = {row["task_id"]: row for row in failures}
    by_task: dict[str, dict[str, str]] = {}
    for row in annotations:
        if None in row or any(value is None for value in row.values()):
            raise ValueError("malformed process annotation CSV row")
        task_id = row["task_id"].strip()
        if task_id in by_task:
            raise ValueError(f"duplicate process annotation: {task_id}")
        alignment = row["contract_alignment"].strip()
        cause = row["process_cause_primary"].strip()
        if alignment not in ALIGNMENTS:
            raise ValueError(f"{task_id}: unsupported alignment {alignment!r}")
        if cause not in PROCESS_CAUSES:
            raise ValueError(f"{task_id}: unsupported process cause {cause!r}")
        if alignment in {"ambiguous", "misaligned"} and cause != "not_attributable":
            raise ValueError(
                f"{task_id}: ambiguous/misaligned evaluator evidence is not agent-attributable"
            )
        if alignment == "not_tested" and cause != "non_delivery":
            raise ValueError(f"{task_id}: not-tested task must be a non-delivery case")
        if not row["alignment_reason"].strip():
            raise ValueError(f"{task_id}: alignment_reason is required")
        if not row["process_evidence_summary"].strip():
            raise ValueError(f"{task_id}: process_evidence_summary is required")
        if row["adjudicated"].strip().lower() not in {"true", "false"}:
            raise ValueError(f"{task_id}: adjudicated must be true or false")
        by_task[task_id] = row

    missing_tasks = sorted(expected_valid - set(by_task))
    unknown_tasks = sorted(set(by_task) - set(failure_by_task))
    invalid_extras = sorted(
        task_id
        for task_id in set(by_task) - expected_valid
        if failure_by_task[task_id]["evidence_eligibility"]
        != "benchmark_invalid_candidate"
    )
    if missing_tasks or unknown_tasks or invalid_extras:
        raise ValueError(
            "annotation coverage mismatch: "
            f"missing_valid={missing_tasks}, unknown={unknown_tasks}, "
            f"unsupported_extra={invalid_extras}"
        )
    return by_task


def build_rows(
    suite_dir: Path,
    failures: list[dict[str, str]],
    annotations: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for failure in failures:
        if failure["task_id"] not in annotations:
            continue
        task_id = failure["task_id"]
        annotation = annotations[task_id]
        signals = extract_trajectory_signals(suite_dir / task_id)
        rows.append(
            {
                "task_id": task_id,
                "first_failure_stage": failure["first_failure_stage"],
                "output_root_cause": failure["root_cause_primary"],
                "contract_alignment": annotation["contract_alignment"],
                "process_cause_primary": annotation["process_cause_primary"],
                "process_secondary_tags": annotation["process_secondary_tags"],
                "completion_claim": bool_text(signals["completion_claim"]),
                "verification_actions": signals["verification_actions"],
                "submission_files": signals["submission_files"],
                "agent_exit_status": signals["agent_exit_status"],
                "agent_api_calls": signals["agent_api_calls"],
                "assistant_steps": signals["assistant_steps"],
                "context_violation": bool_text(signals["context_violation"]),
                "condensation_events": signals["condensation_events"],
                "alignment_reason": annotation["alignment_reason"],
                "process_evidence_summary": annotation["process_evidence_summary"],
                "review_status": annotation["review_status"],
                "annotator": annotation["annotator"],
                "adjudicated": annotation["adjudicated"],
                "trajectory_path": signals["trajectory_path"],
                "evaluator_evidence_path": failure["evidence_path"],
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(map(str, row)) + " |" for row in rows)
    return "\n".join(lines)


def render_report(rows: list[dict[str, Any]], suite_dir: Path) -> str:
    total = len(rows)
    alignment = Counter(row["contract_alignment"] for row in rows)
    attributable = [
        row for row in rows if row["contract_alignment"] in {"aligned", "not_tested"}
    ]
    functional = [row for row in attributable if row["contract_alignment"] == "aligned"]
    process = Counter(row["process_cause_primary"] for row in attributable)
    output = Counter(row["output_root_cause"] for row in attributable)
    completion_claims = sum(row["completion_claim"] == "true" for row in functional)
    context_violations = sum(row["context_violation"] == "true" for row in attributable)

    lines = [
        "# Python-200′ 现有 Agent 失败的过程级分析",
        "",
        "> **Status: trajectory first pass · contract-alignment audit complete · human adjudication pending**",
        "",
        "## 核心结论",
        "",
        f"原输出侧分析中的 {total} 个候选不能全部解释为 Agent 失败。逐题对照运行时 TASK 与首败测试后，只有 **{len(attributable)} 个**可以进入 Agent 过程归因：其中 {len(functional)} 个形成了提交并发生契约对齐的功能失败，另有 {alignment['not_tested']} 个未形成提交。剩余 {alignment['ambiguous'] + alignment['misaligned']} 个首先暴露的是 benchmark 契约与 evaluator 的一致性问题。",
        "",
        f"在 {len(functional)} 个契约对齐的功能失败中，**{completion_claims}/{len(functional)}（{pct(completion_claims, len(functional))}）** 的 Agent 在轨迹末尾明确宣称实现完成或验证通过。这说明主要问题不是完全没有定位或完全没有编码，而是 Agent 在自选测试通过后过早判断契约已经闭合；自测没有区分出 evaluator 所覆盖的关键边界。",
        "",
        "## 先做公平性净化",
        "",
        markdown_table(
            ["TASK–evaluator 一致性", "任务", f"占 {total} 个候选", "处理"],
            [
                [ALIGNMENT_LABELS[key], alignment[key], pct(alignment[key], total),
                 "进入 Agent 分析" if key in {"aligned", "not_tested"} else "排除并修订题目" if key == "misaligned" else "人工裁决前排除"]
                for key in ["aligned", "not_tested", "ambiguous", "misaligned"]
            ],
        ),
        "",
        "明确越界的典型情况包括：测试调用 TASK 未声明的方法、对 TASK 只声明的状态额外检查响应正文、以及要求 TASK 未规定的返回对象相等语义。契约含糊项则是行为目标存在，但入口方法、默认常量或精确异常类型没有公开。",
        "",
        "## 可归因失败的过程原因",
        "",
        markdown_table(
            ["过程原因", "任务", f"占 {len(attributable)} 个可归因失败"],
            [
                [PROCESS_LABELS[key], count, pct(count, len(attributable))]
                for key, count in process.most_common()
            ],
        ),
        "",
        "其中“错误的契约闭合”表示 Agent 已形成提交、执行了自选验证并宣布完成，但验证集没有覆盖最终失败的已声明行为；它不是对 Agent 心理状态的推断，而是由轨迹中的测试动作、完成声明和 evaluator 反例共同支持。",
        "",
        "## 输出侧表现",
        "",
        markdown_table(
            ["输出侧结果", "任务", f"占 {len(attributable)} 个可归因失败"],
            [[key, count, pct(count, len(attributable))] for key, count in output.most_common()],
        ),
        "",
        "输出侧以行为语义漂移为主；过程侧则以验证闭合错误为主。二者共同说明：Agent 往往能够找到相关模块并生成大体可运行的实现，但没有把 TASK 中分散的 API、状态、边界、异常和适配语义转化为一组具有区分力的验收检查。",
        "",
        "## 上下文与运行预算",
        "",
        f"可归因失败中有 **{context_violations}/{len(attributable)}** 个存在 context-window 违规。两道以 step limit 结束的有效题同时存在 context 违规，因此预算耗尽对这两题有直接证据；其他违规题仍形成提交并宣称完成，不能仅凭违规标记把其语义错误归因于上下文。",
        "",
        "运行器普遍出现的 `tool_validation_error` 也不能直接当作功能根因：不少任务虽然 Agent 容器返回 86，但提交已生成且 evaluator 正常执行。报告以提交和 evaluator 结果为准，运行器状态只作为过程辅助证据。",
        "",
        "## 代表性案例",
        "",
        "- **Alembic：自测数量多但区分力不足。** Agent 声称 130 个上游测试和 51 个契约测试通过，最终提交仍在 merge graph 中丢失 base revision。问题不是没有测试，而是自测没有覆盖任务特定的合并后索引不变量。",
        "- **Decorator：上游语义压过任务契约。** Agent 的自写场景已经观察到调用参数形状不一致，随后用上游 `decorator` 的默认行为解释该差异并宣布完成；evaluator 正好在任务要求的调用形状上失败。",
        "- **Pylint / Typer：预算耗尽导致不完整交付。** 两条轨迹都以 `step_limit_exceeded` 结束，且缺失 TASK 明确声明的公开导出或子模块。这类失败与“自测后误判完成”不同。",
        "- **Click / Pluggy：不是 Agent 契约遗漏。** evaluator 分别调用了 TASK 未声明的 `invoke` 和 `call_historic`；这两题必须先修订 TASK 或测试，不能作为 Agent 失败案例。",
        "",
        "## 对论文的可用结论",
        "",
        "当前证据支持的最稳妥表述是：**现有 Agent 的主要失败不是无法生成代码，而是无法可靠地确认一个跨模块功能的完整可观察契约已经闭合；它们常用大量但非区分性的自测建立错误完成信心。**",
        "",
        "同时，这轮分析也给 benchmark 本身提出了硬要求：主表前必须逐题证明 evaluator 的每个可观察断言都能映射到 TASK 的稳定 clause。否则，隐藏契约会把 benchmark 缺陷错误地计入 Agent 缺陷。",
        "",
        "## 证据与限制",
        "",
        f"- 原始 suite：`{relpath(suite_dir)}`",
        "- 逐任务过程表：`failure_process_analysis.csv`",
        "- 标注源：`failure_process_annotations.csv`",
        "- 本轮为单 reviewer 的 trajectory first pass；论文定稿前需对 6 个含糊项和全部 Hidden-only 失败进行第二 reviewer 裁决。",
        "- 没有重新运行实验；所有数字来自保留的 TASK、提交、evaluator 日志、run.json 和 OpenHands events。",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("suite_dir", type=Path)
    parser.add_argument("failure_analysis", type=Path)
    parser.add_argument("annotations", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()

    failures = read_csv(args.failure_analysis)
    annotations = validate_annotations(failures, read_csv(args.annotations))
    rows = build_rows(args.suite_dir, failures, annotations)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "failure_process_analysis.csv", rows)
    payload = {
        "suite": relpath(args.suite_dir),
        "task_count": len(rows),
        "contract_alignment": dict(Counter(row["contract_alignment"] for row in rows)),
        "process_causes": dict(Counter(row["process_cause_primary"] for row in rows)),
        "rows": rows,
    }
    (args.output_dir / "failure_process_analysis.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "failure_process_analysis.md").write_text(
        render_report(rows, args.suite_dir), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
