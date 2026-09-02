#!/usr/bin/env python3
"""Validate and summarize a FeatureLiftBench failure-root-cause annotation pass."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]

INFRASTRUCTURE_CLASSES = {
    "freeze_preflight_blocked",
    "dependency_install_infrastructure",
}

AUDIT_CLASS_TO_STAGE = {
    "freeze_preflight_blocked": "preflight_blocked",
    "dependency_install_infrastructure": "build_failure",
    "agent_no_submission": "missing_submission",
    "submission_build": "build_failure",
    "public_behavior": "public_failure",
    "hidden_only_behavior": "hidden_failure",
    "isolation": "isolation_failure",
    "other": "stage_evidence_unavailable",
}

VALID_ANNOTATION_CAUSES = {
    "agent_process_non_delivery",
    "localization",
    "contract_api_completion",
    "dependency_closure",
    "behavior_drift",
    "packaging_modularization",
    "test_gaming_narrow",
    "task_or_evaluator_defect",
    "unknown",
}

VALIDITY_OVERRIDES = {
    "",
    "benchmark_invalid_candidate",
    "evidence_unavailable",
}

ROOT_CAUSE_LABELS = {
    "agent_process_non_delivery": "Agent 未形成提交",
    "localization": "定位错误",
    "contract_api_completion": "契约/API 完整性不足",
    "dependency_closure": "依赖闭包不足",
    "behavior_drift": "行为语义漂移",
    "packaging_modularization": "打包/模块化失败",
    "test_gaming_narrow": "窄化实现或测试投机",
    "task_or_evaluator_defect": "题目或评测器缺陷",
    "unknown": "原因未确定",
    "infrastructure": "基础设施",
}

STAGE_LABELS = {
    "preflight_blocked": "Preflight",
    "missing_submission": "未提交",
    "build_failure": "Build",
    "public_failure": "Public",
    "hidden_failure": "Hidden",
    "isolation_failure": "Isolation",
    "stage_evidence_unavailable": "证据不足",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def bool_value(value: Any) -> bool | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    lowered = str(value).strip().lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    raise ValueError(f"invalid boolean value: {value!r}")


def relpath(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def pct(numerator: int, denominator: int) -> str:
    return "—" if denominator == 0 else f"{numerator / denominator:.1%}"


def markdown_table(headers: list[str], rows: Iterable[Iterable[Any]]) -> list[str]:
    result = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        result.append("| " + " | ".join(str(value) for value in row) + " |")
    return result


def evidence_path(suite_dir: Path, task_id: str, audit_class: str) -> Path:
    task_dir = suite_dir / task_id
    if audit_class in {"freeze_preflight_blocked", "agent_no_submission"}:
        return task_dir / "run.json"
    if audit_class == "dependency_install_infrastructure":
        return task_dir / "eval/logs/dependency_install.stderr"
    if audit_class == "public_behavior":
        return task_dir / "eval/logs/public.stdout"
    if audit_class == "hidden_only_behavior":
        return task_dir / "eval/logs/hidden.stdout"
    return task_dir / "eval/result.json"


def validate_annotations(
    failures: list[dict[str, str]], annotations: list[dict[str, str]]
) -> dict[str, dict[str, str]]:
    required_fields = {
        "task_id",
        "root_cause_primary",
        "secondary_tags",
        "contract_clause_ids",
        "validity_override",
        "validity_reason",
        "review_status",
        "evidence_summary",
    }
    if annotations:
        missing_fields = required_fields - set(annotations[0])
        if missing_fields:
            raise ValueError(f"annotation CSV is missing fields: {sorted(missing_fields)}")

    failure_by_task = {row["task_id"]: row for row in failures}
    by_task: dict[str, dict[str, str]] = {}
    duplicates: list[str] = []
    for row in annotations:
        task_id = row["task_id"].strip()
        if task_id in by_task:
            duplicates.append(task_id)
        by_task[task_id] = row
        cause = row["root_cause_primary"].strip()
        if cause not in VALID_ANNOTATION_CAUSES:
            raise ValueError(f"{task_id}: unsupported root cause {cause!r}")
        override = row["validity_override"].strip()
        if override not in VALIDITY_OVERRIDES:
            raise ValueError(f"{task_id}: unsupported validity override {override!r}")
        if override and not row["validity_reason"].strip():
            raise ValueError(f"{task_id}: validity override requires a reason")
        if cause == "task_or_evaluator_defect" and override != "benchmark_invalid_candidate":
            raise ValueError(
                f"{task_id}: task/evaluator defect requires benchmark_invalid_candidate"
            )
        if override == "benchmark_invalid_candidate" and cause != "task_or_evaluator_defect":
            raise ValueError(
                f"{task_id}: benchmark-invalid candidate requires task/evaluator defect cause"
            )
        audit_class = failure_by_task.get(task_id, {}).get("audit_failure_class")
        if audit_class == "agent_no_submission" and cause != "agent_process_non_delivery":
            raise ValueError(f"{task_id}: no-submission outcome requires non-delivery cause")
        if cause == "agent_process_non_delivery" and audit_class != "agent_no_submission":
            raise ValueError(f"{task_id}: non-delivery cause requires no-submission outcome")
        clause_ids = row["contract_clause_ids"].strip()
        if clause_ids and any(
            re.fullmatch(r"B[0-9]{3}", value) is None
            for value in clause_ids.split(";")
        ):
            raise ValueError(f"{task_id}: invalid contract clause list {clause_ids!r}")
        public_text = " ".join(
            [
                row["evidence_summary"],
                row["validity_reason"],
                row["secondary_tags"],
            ]
        )
        if re.search(r"hidden_tests/|test_hidden|::test_", public_text):
            raise ValueError(f"{task_id}: annotation exposes a private test identifier")
        if not row["review_status"].strip():
            raise ValueError(f"{task_id}: review_status is required")
        if not row["evidence_summary"].strip():
            raise ValueError(f"{task_id}: evidence_summary is required")
    if duplicates:
        raise ValueError(f"duplicate annotation task IDs: {sorted(set(duplicates))}")

    expected = {
        row["task_id"]
        for row in failures
        if row["audit_failure_class"] not in INFRASTRUCTURE_CLASSES
    }
    actual = set(by_task)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing or extra:
        raise ValueError(
            "annotation coverage mismatch: "
            f"missing={missing or 'none'}, extra={extra or 'none'}"
        )
    return by_task


def build_rows(
    suite_dir: Path,
    suite: dict[str, Any],
    failures: list[dict[str, str]],
    annotations: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    model = (suite.get("agent_config") or {}).get("model") or "unknown"
    for failure in failures:
        task_id = failure["task_id"]
        audit_class = failure["audit_failure_class"]
        context_violation = bool_value(failure.get("context_violation"))
        path = evidence_path(suite_dir, task_id, audit_class)
        if audit_class in INFRASTRUCTURE_CLASSES:
            eligibility = "infrastructure_invalid"
            cause = "infrastructure"
            secondary_tags = audit_class
            clause_ids = ""
            review_status = "automatic"
            annotator = "rule_based"
            adjudicated = False
            summary = failure.get("evidence", "").strip() or audit_class.replace("_", " ")
            validity_reason = summary
        else:
            annotation = annotations[task_id]
            eligibility = annotation["validity_override"].strip() or "valid_agent_evidence"
            cause = annotation["root_cause_primary"].strip()
            secondary_tags = annotation["secondary_tags"].strip()
            clause_ids = annotation["contract_clause_ids"].strip()
            review_status = annotation["review_status"].strip()
            annotator = (annotation.get("annotator") or "").strip()
            if not annotator and review_status == "assistant_first_pass":
                annotator = "codex_assistant"
            annotator = annotator or "unspecified"
            adjudicated = bool_value(annotation.get("adjudicated")) is True
            summary = annotation["evidence_summary"].strip()
            validity_reason = annotation["validity_reason"].strip()
        if not path.is_file() and eligibility != "evidence_unavailable":
            raise FileNotFoundError(f"{task_id}: evidence path does not exist: {path}")
        rows.append(
            {
                "suite_id": suite_dir.name,
                "task_id": task_id,
                "model": model,
                "suite_split": failure.get("suite_split", "unknown"),
                "lift_type": failure.get("lift_type", "unknown"),
                "feature_family": failure.get("feature_family", "unknown"),
                "evidence_eligibility": eligibility,
                "functional_pass": False,
                "first_failure_stage": AUDIT_CLASS_TO_STAGE.get(
                    audit_class, "stage_evidence_unavailable"
                ),
                "audit_failure_class": audit_class,
                "root_cause_primary": cause,
                "secondary_tags": secondary_tags,
                "contract_clause_ids": clause_ids,
                "context_violation": context_violation,
                "review_status": review_status,
                "annotator": annotator,
                "adjudicated": adjudicated,
                "evidence_summary": summary,
                "evidence_path": relpath(path),
                "validity_reason": validity_reason,
            }
        )
    return sorted(rows, key=lambda row: (str(row["evidence_eligibility"]), str(row["task_id"])))


def counter_dict(values: Iterable[Any]) -> dict[str, int]:
    return dict(sorted(Counter(str(value) for value in values).items()))


def make_summary(
    suite: dict[str, Any],
    rows: list[dict[str, Any]],
    suite_dir: Path,
    failure_audit: Path,
    annotations: Path,
) -> dict[str, Any]:
    valid = [row for row in rows if row["evidence_eligibility"] == "valid_agent_evidence"]
    by_split: dict[str, Counter[str]] = defaultdict(Counter)
    for row in valid:
        by_split[str(row["suite_split"])][str(row["root_cause_primary"])] += 1
    return {
        "schema_version": "featureliftbench.failure_analysis.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "suite": suite_dir.name,
        "model": (suite.get("agent_config") or {}).get("model"),
        "profile": (suite.get("agent_config") or {}).get("profile"),
        "sources": {
            "suite": relpath(suite_dir / "suite.json"),
            "failure_audit": relpath(failure_audit),
            "annotations": relpath(annotations),
        },
        "nonpasses": len(rows),
        "eligibility_counts": counter_dict(row["evidence_eligibility"] for row in rows),
        "first_failure_stage_all": counter_dict(row["first_failure_stage"] for row in rows),
        "first_failure_stage_valid_agent": counter_dict(
            row["first_failure_stage"] for row in valid
        ),
        "root_cause_valid_agent": counter_dict(row["root_cause_primary"] for row in valid),
        "root_cause_valid_agent_by_split": {
            split: dict(sorted(counts.items())) for split, counts in sorted(by_split.items())
        },
        "valid_agent_failures": len(valid),
        "valid_agent_context_violations": sum(
            row["context_violation"] is True for row in valid
        ),
        "review_status_counts": counter_dict(row["review_status"] for row in rows),
        "human_adjudication": {
            "status": "pending",
            "note": (
                "Semantic causes are an assistant first pass. Hidden-only failures, unknowns, "
                "and benchmark-invalid candidates require independent human review before "
                "paper-level causal claims."
            ),
        },
    }


def validate_output(summary: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    task_ids = [str(row["task_id"]) for row in rows]
    checks = {
        "unique_failure_task_ids": len(task_ids) == len(set(task_ids)),
        "eligibility_partition_complete": (
            sum(int(value) for value in summary["eligibility_counts"].values())
            == len(rows)
        ),
        "valid_stage_partition_complete": (
            sum(int(value) for value in summary["first_failure_stage_valid_agent"].values())
            == int(summary["valid_agent_failures"])
        ),
        "valid_root_cause_partition_complete": (
            sum(int(value) for value in summary["root_cause_valid_agent"].values())
            == int(summary["valid_agent_failures"])
        ),
        "all_rows_have_evidence_summary": all(
            bool(str(row["evidence_summary"]).strip()) for row in rows
        ),
        "all_rows_have_review_provenance": all(
            bool(str(row["review_status"]).strip())
            and bool(str(row["annotator"]).strip())
            for row in rows
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    summary["validation"] = {
        "status": "pass" if not failed else "fail",
        "checks": checks,
    }
    if failed:
        raise ValueError(f"failure analysis validation failed: {failed}")


def make_markdown(summary: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    eligibility = summary["eligibility_counts"]
    valid_total = int(summary["valid_agent_failures"])
    infra = int(eligibility.get("infrastructure_invalid", 0))
    benchmark_candidates = int(eligibility.get("benchmark_invalid_candidate", 0))
    root_causes = summary["root_cause_valid_agent"]
    stages = summary["first_failure_stage_valid_agent"]
    invalid_candidates = [
        row for row in rows if row["evidence_eligibility"] == "benchmark_invalid_candidate"
    ]
    lines = [
        "# Python-200′ 当前候选结果的具体失败归类",
        "",
        "> **Status: evidence audit complete · semantic labels are an assistant first pass · "
        "human adjudication pending**",
        "",
        "## 结论",
        "",
        f"收到的 suite 有 **{summary['nonpasses']} 个表面未通过结果**。其中 "
        f"**{infra} 个是基础设施结果**，另有 **{benchmark_candidates} 个题目/评测缺陷候选**；"
        f"当前可进入 Agent 根因分母的是 **{valid_total} 个失败**。根因统计不使用 68 作为分母，"
        "也不把上下文违规改写为功能失败原因。",
        "",
        f"在这 {valid_total} 个有效 Agent 失败的一轮输出侧审查中，主要现象是行为已经实现但语义发生漂移，"
        "其次是契约/API 完整性不足。该结论描述提交的外部表现；在完成 trajectory 双审前，"
        "不能进一步声称这些错误由搜索、记忆或预算中的某一个过程机制导致。",
        "",
        "## 证据有效性",
        "",
    ]
    lines.extend(
        markdown_table(
            ["类别", "任务", "占 68 个未通过", "处理"],
            [
                (
                    "有效 Agent 失败",
                    valid_total,
                    pct(valid_total, summary["nonpasses"]),
                    "进入根因分母",
                ),
                (
                    "基础设施无效",
                    infra,
                    pct(infra, summary["nonpasses"]),
                    "修复后重跑",
                ),
                (
                    "题目/评测缺陷候选",
                    benchmark_candidates,
                    pct(benchmark_candidates, summary["nonpasses"]),
                    "人工裁决，裁决前排除",
                ),
            ],
        )
    )
    lines.extend(["", "## 有效 Agent 失败的首败阶段", ""])
    stage_order = [
        "missing_submission",
        "build_failure",
        "public_failure",
        "hidden_failure",
        "isolation_failure",
        "stage_evidence_unavailable",
    ]
    lines.extend(
        markdown_table(
            ["首败阶段", "任务", f"占 {valid_total} 个有效失败"],
            [
                (STAGE_LABELS[stage], stages.get(stage, 0), pct(stages.get(stage, 0), valid_total))
                for stage in stage_order
                if stages.get(stage, 0)
            ],
        )
    )
    lines.extend(["", "## 有效 Agent 失败的输出侧根因", ""])
    root_order = [
        "behavior_drift",
        "contract_api_completion",
        "agent_process_non_delivery",
        "dependency_closure",
        "packaging_modularization",
        "localization",
        "test_gaming_narrow",
        "unknown",
    ]
    lines.extend(
        markdown_table(
            ["Primary cause", "任务", f"占 {valid_total} 个有效失败", "解释"],
            [
                (
                    ROOT_CAUSE_LABELS[cause],
                    root_causes.get(cause, 0),
                    pct(root_causes.get(cause, 0), valid_total),
                    {
                        "behavior_drift": "API 已存在，但返回、顺序、状态、解析或异常语义不同",
                        "contract_api_completion": "缺少模块、成员、导出、签名或必要行为分支",
                        "agent_process_non_delivery": "正常启动但未形成可评测提交",
                        "dependency_closure": "内部 helper、资源或传递依赖未闭合",
                        "packaging_modularization": "实现存在但独立包无法正确暴露",
                        "localization": "直接证据显示定位到错误区域",
                        "test_gaming_narrow": "直接证据显示硬编码或窄化实现",
                        "unknown": "证据不足",
                    }[cause],
                )
                for cause in root_order
                if root_causes.get(cause, 0)
            ],
        )
    )
    lines.extend(
        [
            "",
            "本轮没有把任何任务归为 localization、dependency closure 或 packaging failure。"
            "这不等于证明 Agent 在这些方面没有问题；它只表示当前 evaluator 日志和提交没有提供足够直接证据。",
            "",
            "## 协议合规性",
            "",
            f"有效 Agent 失败中有 **{summary['valid_agent_context_violations']}/{valid_total}** 个同时存在 "
            "context-window 违规。它们可以用于内部行为诊断，但在严格 Python-200′ 主表中仍属于冻结替换集，"
            "不能直接进入最终分数。",
            "",
        ]
    )
    if invalid_candidates:
        lines.extend(["## 新发现的题目/评测缺陷候选", ""])
        for row in invalid_candidates:
            lines.append(
                f"- `{row['task_id']}`：{row['evidence_summary']}。"
                f"处理：{row['validity_reason']}"
            )
        lines.extend(
            [
                "",
                "该修正不回写收到的原始 suite，也不静默修改旧 `failure_audit.csv`；"
                "它作为语义审查层的 validity override 单独保留。",
                "",
            ]
        )
    lines.extend(
        [
            "## 当前证据可以支持什么",
            "",
            "- 68 个未通过结果的证据有效性、首败阶段和逐任务证据路径；",
            f"- {valid_total} 个有效 Agent 失败的一轮输出侧语义归类；",
            "- 基础设施、协议违规和题目缺陷候选与 Agent 行为的分离；",
            "- 以 Public/Hidden 和稳定 clause ID 为单位选择代表性案例。",
            "",
            "当前还不能支持：",
            "",
            "- 将 assistant first-pass 标签当成人工金标；",
            "- 从输出错误直接推出搜索、记忆、上下文压缩或动态分析能力的因果机制；",
            "- 在 84 个严格替换任务完成前把 132/200 写入最终主表；",
            "- 在 Hidden-only 契约完成人工双审前声称全部隐藏失败都公平且无争议。",
            "",
            "## 下一轮人工复核",
            "",
            "1. 双审全部 8 个 Hidden-only 失败及其公开 clause 映射；",
            "2. 裁决题目/评测缺陷候选；",
            f"3. 对 {root_causes.get('contract_api_completion', 0)} 个 contract/API completion "
            "和分层抽样的 behavior drift 阅读 trajectory；",
            "4. 记录第二 reviewer 标签、分歧和最终 adjudication；",
            "5. 完成人工一致性后再生成论文级根因比例和代表性案例。",
            "",
            "逐任务记录见 `failure_analysis.csv`，机器可读汇总见 `failure_analysis.json`，"
            "标注源见 `failure_root_cause_annotations.csv`。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suite_dir", type=Path)
    parser.add_argument("--failure-audit", type=Path, required=True)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    suite_dir = args.suite_dir.resolve()
    failure_audit = args.failure_audit.resolve()
    annotations_path = args.annotations.resolve()
    output_dir = args.output_dir.resolve()
    suite = read_json(suite_dir / "suite.json")
    failures = read_csv(failure_audit)
    raw_annotations = read_csv(annotations_path)
    annotations = validate_annotations(failures, raw_annotations)
    rows = build_rows(suite_dir, suite, failures, annotations)
    summary = make_summary(
        suite, rows, suite_dir, failure_audit, annotations_path
    )
    validate_output(summary, rows)

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "failure_analysis.csv", rows)
    (output_dir / "failure_analysis.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (output_dir / "failure_analysis.md").write_text(
        make_markdown(summary, rows), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
