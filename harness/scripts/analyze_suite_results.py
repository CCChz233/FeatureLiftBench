from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HIGH_EXTRACTION_RATIO = 0.8
LOW_EXTRACTION_RATIO = 0.25


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fmt_float(value: Any, digits: int = 3) -> str:
    if isinstance(value, (int, float)):
        return f"{value:.{digits}f}"
    return ""


def fmt_int(value: Any) -> str:
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, float):
        return f"{int(value):,}"
    return ""


def fmt_seconds(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value:.1f}s"
    return ""


def summarize_suite(name: str, suite: dict[str, Any]) -> dict[str, Any]:
    summary = suite.get("summary") or {}
    totals = suite.get("agent_usage_totals") or {}
    return {
        "suite": name,
        "model": suite.get("model"),
        "profile": suite.get("profile"),
        "api_base": suite.get("api_base"),
        "passed": summary.get("passed"),
        "failed": summary.get("failed"),
        "total": summary.get("total"),
        "average_final_score": summary.get("average_final_score"),
        "assistant_steps": totals.get("assistant_steps"),
        "api_calls": totals.get("api_calls"),
        "prompt_tokens": totals.get("prompt_tokens"),
        "completion_tokens": totals.get("completion_tokens"),
        "total_tokens": totals.get("total_tokens"),
        "agent_duration_seconds": totals.get("agent_duration_seconds"),
    }


def collect_runs(suites: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for suite_name, suite in sorted(suites.items()):
        for run in suite.get("runs") or []:
            rows.append(
                {
                    "suite": suite_name,
                    "model": suite.get("model"),
                    "task_id": run.get("task_id"),
                    "status": run.get("status"),
                    "functional_gate": run.get("functional_gate"),
                    "test_pass": run.get("test_pass"),
                    "build_pass": run.get("build_pass"),
                    "final_score": run.get("final_score"),
                    "extraction_ratio": run.get("extraction_ratio"),
                    "submission_loc": run.get("submission_loc"),
                    "source_loc": run.get("source_loc"),
                    "assistant_steps": run.get("assistant_steps"),
                    "total_tokens": run.get("total_tokens"),
                    "agent_duration_seconds": run.get("agent_duration_seconds"),
                    "trajectory_json": run.get("trajectory_json"),
                }
            )
    return rows


def build_task_matrix(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    task_ids = sorted({row["task_id"] for row in rows if row.get("task_id")})
    suites = sorted({row["suite"] for row in rows if row.get("suite")})
    by_key = {(row["task_id"], row["suite"]): row for row in rows}

    matrix = []
    for task_id in task_ids:
        task_row: dict[str, Any] = {"task_id": task_id, "suites": {}}
        for suite in suites:
            run = by_key.get((task_id, suite))
            if not run:
                task_row["suites"][suite] = {"status": "missing"}
                continue
            task_row["suites"][suite] = {
                "status": run.get("status"),
                "functional_gate": run.get("functional_gate"),
                "extraction_ratio": run.get("extraction_ratio"),
                "final_score": run.get("final_score"),
                "total_tokens": run.get("total_tokens"),
                "assistant_steps": run.get("assistant_steps"),
                "submission_loc": run.get("submission_loc"),
                "source_loc": run.get("source_loc"),
            }
        matrix.append(task_row)
    return matrix


def classify_runs(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    failures = [
        row
        for row in rows
        if row.get("status") != "passed" or row.get("functional_gate") != 1.0
    ]
    high_ratio_passes = [
        row
        for row in rows
        if row.get("status") == "passed"
        and isinstance(row.get("extraction_ratio"), (int, float))
        and row["extraction_ratio"] >= HIGH_EXTRACTION_RATIO
    ]
    compact_passes = [
        row
        for row in rows
        if row.get("status") == "passed"
        and isinstance(row.get("extraction_ratio"), (int, float))
        and row["extraction_ratio"] <= LOW_EXTRACTION_RATIO
    ]
    token_outliers = sorted(
        [row for row in rows if isinstance(row.get("total_tokens"), (int, float))],
        key=lambda row: row["total_tokens"],
        reverse=True,
    )[:5]

    high_ratio_passes.sort(
        key=lambda row: (row.get("extraction_ratio") or 0, row.get("suite") or ""),
        reverse=True,
    )
    compact_passes.sort(key=lambda row: (row.get("extraction_ratio") or 0))

    return {
        "failures": failures,
        "high_extraction_ratio_passes": high_ratio_passes,
        "compact_passes": compact_passes,
        "token_outliers": token_outliers,
    }


def build_findings(
    suite_summaries: list[dict[str, Any]], classifications: dict[str, list[dict[str, Any]]]
) -> list[str]:
    findings: list[str] = []
    for suite in suite_summaries:
        passed = suite.get("passed")
        total = suite.get("total")
        model = suite.get("model") or suite["suite"]
        findings.append(f"{model}: {passed}/{total} tasks passed.")

    failures = classifications["failures"]
    if failures:
        failed_tasks = ", ".join(
            f"{row['suite']}::{row['task_id']}" for row in failures
        )
        findings.append(f"Observed failed runs: {failed_tasks}.")
    else:
        findings.append("No failed runs were observed.")

    high_ratio_tasks = sorted(
        {
            row["task_id"]
            for row in classifications["high_extraction_ratio_passes"]
            if row.get("task_id")
        }
    )
    if high_ratio_tasks:
        findings.append(
            "High extraction-ratio passes indicate copy-heavy solutions on: "
            + ", ".join(high_ratio_tasks)
            + "."
        )

    token_outliers = classifications["token_outliers"]
    if token_outliers:
        top = token_outliers[0]
        findings.append(
            "Largest token outlier: "
            f"{top['suite']}::{top['task_id']} used {fmt_int(top.get('total_tokens'))} tokens."
        )

    findings.append(
        "Pro and Flash used different endpoints, so this is a pilot comparison rather than a controlled model benchmark."
    )
    return findings


def build_recommendations() -> list[str]:
    return [
        "Inspect high extraction-ratio passes first: click, markdown_it, pluggy, and pyyaml are functional but copy-heavy.",
        "Use the Flash jsonschema hidden-test failure as the first concrete failure-mode case study.",
        "Add property-style or migrated edge tests only after confirming each high-ratio task is passing by broad copying rather than legitimate large closure.",
        "Move trajectory step/token aggregation into run-agent output once the current analysis format looks right.",
    ]


def render_md(analysis: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Mini-SWE-Agent Suite Analysis")
    lines.append("")
    lines.append(f"Generated at: {analysis['generated_at']}")
    lines.append(f"Source: `{analysis['source']}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| suite | model | endpoint | passed | avg final_score | steps | tokens | agent wall time |")
    lines.append("| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |")
    for suite in analysis["suite_summaries"]:
        passed = f"{suite.get('passed')}/{suite.get('total')}"
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{suite['suite']}`",
                    f"`{suite.get('model') or ''}`",
                    f"`{suite.get('api_base') or ''}`",
                    passed,
                    fmt_float(suite.get("average_final_score"), 6),
                    fmt_int(suite.get("assistant_steps")),
                    fmt_int(suite.get("total_tokens")),
                    fmt_seconds(suite.get("agent_duration_seconds")),
                ]
            )
            + " |"
        )

    lines.append("")
    lines.append("## Findings")
    lines.append("")
    for finding in analysis["findings"]:
        lines.append(f"- {finding}")

    lines.append("")
    lines.append("## Per-Task Matrix")
    lines.append("")
    suite_names = [suite["suite"] for suite in analysis["suite_summaries"]]
    header = ["task"]
    for suite_name in suite_names:
        header.extend([f"{suite_name} status", "ratio", "score", "tokens"])
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(["---"] + ["---:", "---:", "---:", "---:"] * len(suite_names)) + " |")

    for task in analysis["task_matrix"]:
        row = [f"`{task['task_id']}`"]
        for suite_name in suite_names:
            run = task["suites"].get(suite_name) or {}
            row.extend(
                [
                    str(run.get("status") or ""),
                    fmt_float(run.get("extraction_ratio"), 6),
                    fmt_float(run.get("final_score"), 6),
                    fmt_int(run.get("total_tokens")),
                ]
            )
        lines.append("| " + " | ".join(row) + " |")

    lines.append("")
    lines.append("## High Extraction-Ratio Passes")
    lines.append("")
    lines.append(
        f"Threshold: `extraction_ratio >= {HIGH_EXTRACTION_RATIO}` and functional pass."
    )
    lines.append("")
    lines.append("| suite | task | ratio | final_score | submission_loc | source_loc |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: |")
    for row in analysis["classifications"]["high_extraction_ratio_passes"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['suite']}`",
                    f"`{row['task_id']}`",
                    fmt_float(row.get("extraction_ratio"), 6),
                    fmt_float(row.get("final_score"), 6),
                    fmt_int(row.get("submission_loc")),
                    fmt_int(row.get("source_loc")),
                ]
            )
            + " |"
        )

    lines.append("")
    lines.append("## Compact Functional Passes")
    lines.append("")
    lines.append(
        f"Threshold: `extraction_ratio <= {LOW_EXTRACTION_RATIO}` and functional pass."
    )
    lines.append("")
    lines.append("| suite | task | ratio | final_score | submission_loc | source_loc |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: |")
    for row in analysis["classifications"]["compact_passes"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['suite']}`",
                    f"`{row['task_id']}`",
                    fmt_float(row.get("extraction_ratio"), 6),
                    fmt_float(row.get("final_score"), 6),
                    fmt_int(row.get("submission_loc")),
                    fmt_int(row.get("source_loc")),
                ]
            )
            + " |"
        )

    lines.append("")
    lines.append("## Token Outliers")
    lines.append("")
    lines.append("| suite | task | tokens | steps | agent wall time |")
    lines.append("| --- | --- | ---: | ---: | ---: |")
    for row in analysis["classifications"]["token_outliers"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['suite']}`",
                    f"`{row['task_id']}`",
                    fmt_int(row.get("total_tokens")),
                    fmt_int(row.get("assistant_steps")),
                    fmt_seconds(row.get("agent_duration_seconds")),
                ]
            )
            + " |"
        )

    failures = analysis["classifications"]["failures"]
    lines.append("")
    lines.append("## Failures")
    lines.append("")
    if not failures:
        lines.append("No failed runs in the analyzed suites.")
    else:
        lines.append("| suite | task | status | functional_gate | test_pass | trajectory |")
        lines.append("| --- | --- | --- | ---: | --- | --- |")
        for row in failures:
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{row['suite']}`",
                        f"`{row['task_id']}`",
                        str(row.get("status") or ""),
                        fmt_float(row.get("functional_gate"), 1),
                        str(row.get("test_pass")),
                        f"`{row.get('trajectory_json') or ''}`",
                    ]
                )
                + " |"
            )

    lines.append("")
    lines.append("## Recommendations")
    lines.append("")
    for recommendation in analysis["recommendations"]:
        lines.append(f"- {recommendation}")

    lines.append("")
    return "\n".join(lines)


def build_analysis(source: Path) -> dict[str, Any]:
    payload = load_json(source)
    suites = payload.get("suites") or {}
    suite_summaries = [summarize_suite(name, suite) for name, suite in sorted(suites.items())]
    rows = collect_runs(suites)
    classifications = classify_runs(rows)
    analysis = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source": str(source),
        "suite_summaries": suite_summaries,
        "task_matrix": build_task_matrix(rows),
        "classifications": classifications,
        "findings": build_findings(suite_summaries, classifications),
        "recommendations": build_recommendations(),
    }
    return analysis


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze FeatureLiftBench mini-swe-agent suite comparison outputs."
    )
    parser.add_argument(
        "--input",
        default="experiments/mini-swe-agent/suite-comparison.json",
        help="Path to suite-comparison.json.",
    )
    parser.add_argument(
        "--output-prefix",
        default="experiments/mini-swe-agent/suite-analysis",
        help="Output path prefix. Writes .json and .md.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = Path(args.input)
    output_prefix = Path(args.output_prefix)
    analysis = build_analysis(source)
    write_json(output_prefix.with_suffix(".json"), analysis)
    write_text(output_prefix.with_suffix(".md"), render_md(analysis))
    print(f"Wrote {output_prefix.with_suffix('.json')}")
    print(f"Wrote {output_prefix.with_suffix('.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
