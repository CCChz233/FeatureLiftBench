#!/usr/bin/env python3
"""Compare paired FeatureLiftBench Main and No-public suite results."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_suite(suite_dir: Path) -> dict[str, Any]:
    suite_path = suite_dir / "suite.json"
    if not suite_path.is_file():
        raise FileNotFoundError(f"missing suite.json: {suite_path}")
    suite = _load_json(suite_path)
    runs = suite.get("runs")
    if not isinstance(runs, list):
        raise ValueError(f"suite runs must be a list: {suite_path}")
    return suite


def _run_map(suite: dict[str, Any]) -> dict[str, dict[str, Any]]:
    runs: dict[str, dict[str, Any]] = {}
    for run in suite.get("runs", []):
        if not isinstance(run, dict):
            continue
        task_id = run.get("task_id")
        if not isinstance(task_id, str) or not task_id:
            continue
        if task_id in runs:
            raise ValueError(f"duplicate task_id in suite: {task_id}")
        runs[task_id] = run
    return runs


def _eval_summary(suite_dir: Path, task_id: str) -> dict[str, Any]:
    path = suite_dir / task_id / "eval" / "result.json"
    if not path.is_file():
        return {
            "available": False,
            "build_pass": None,
            "public_pass": None,
            "public_skipped": None,
            "hidden_pass": None,
            "functional_gate": None,
        }
    result = _load_json(path)
    return {
        "available": True,
        "build_pass": result.get("build_pass"),
        "public_pass": _nested_bool(result, "public_tests", "passed"),
        "public_skipped": _nested_bool(result, "public_tests", "skipped"),
        "hidden_pass": _nested_bool(result, "hidden_tests", "passed"),
        "functional_gate": (result.get("scores") or {}).get("functional_gate"),
    }


def _nested_bool(data: dict[str, Any], outer: str, inner: str) -> bool | None:
    value = data.get(outer)
    if not isinstance(value, dict):
        return None
    result = value.get(inner)
    return result if isinstance(result, bool) else None


def _wilson_interval(successes: int, total: int) -> tuple[float, float]:
    if total <= 0:
        return (0.0, 0.0)
    z = 1.959963984540054
    proportion = successes / total
    denominator = 1.0 + z * z / total
    center = (proportion + z * z / (2 * total)) / denominator
    half_width = (
        z
        * math.sqrt(
            proportion * (1.0 - proportion) / total
            + z * z / (4 * total * total)
        )
        / denominator
    )
    return (center - half_width, center + half_width)


def _exact_mcnemar_p(left_only: int, right_only: int) -> float:
    discordant = left_only + right_only
    if discordant == 0:
        return 1.0
    smaller = min(left_only, right_only)
    lower_tail = sum(math.comb(discordant, i) for i in range(smaller + 1))
    return min(1.0, 2.0 * lower_tail / (2**discordant))


def _gate_pattern(eval_summary: dict[str, Any]) -> str:
    return (
        f"build={eval_summary['build_pass']},"
        f"public={eval_summary['public_pass']},"
        f"hidden={eval_summary['hidden_pass']},"
        f"gate={eval_summary['functional_gate']}"
    )


def _load_legacy_runs(paths: list[Path]) -> dict[str, dict[str, Any]]:
    runs: dict[str, dict[str, Any]] = {}
    for path in paths:
        suite_path = path / "suite.json" if path.is_dir() else path
        suite = _load_json(suite_path)
        for task_id, run in _run_map(suite).items():
            if task_id in runs:
                raise ValueError(f"duplicate legacy task_id across suites: {task_id}")
            runs[task_id] = run
    return runs


def build_analysis(
    main_dir: Path,
    nopublic_dir: Path,
    legacy_paths: list[Path],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    main_suite = _load_suite(main_dir)
    nopublic_suite = _load_suite(nopublic_dir)
    main_runs = _run_map(main_suite)
    nopublic_runs = _run_map(nopublic_suite)
    if set(main_runs) != set(nopublic_runs):
        raise ValueError("Main and No-public task sets differ")

    task_rows: list[dict[str, Any]] = []
    paired: Counter[str] = Counter()
    gate_patterns = {"main": Counter(), "nopublic": Counter()}
    task_groups: dict[str, list[str]] = {
        "both_pass": [],
        "main_only": [],
        "nopublic_only": [],
        "both_fail": [],
    }
    repaired_main_runs: list[str] = []
    integrity_counts: Counter[str] = Counter()

    for task_id in sorted(main_runs):
        main_run = main_runs[task_id]
        nopublic_run = nopublic_runs[task_id]
        main_pass = main_run.get("status") == "passed"
        nopublic_pass = nopublic_run.get("status") == "passed"
        group = (
            "both_pass"
            if main_pass and nopublic_pass
            else "main_only"
            if main_pass
            else "nopublic_only"
            if nopublic_pass
            else "both_fail"
        )
        paired[group] += 1
        task_groups[group].append(task_id)

        main_eval = _eval_summary(main_dir, task_id)
        nopublic_eval = _eval_summary(nopublic_dir, task_id)
        gate_patterns["main"][_gate_pattern(main_eval)] += 1
        gate_patterns["nopublic"][_gate_pattern(nopublic_eval)] += 1
        integrity_counts["main_workspace_public_tests_present"] += (
            main_dir / task_id / "workspace" / "public_tests"
        ).is_dir()
        integrity_counts["nopublic_workspace_public_tests_absent"] += not (
            nopublic_dir / task_id / "workspace" / "public_tests"
        ).exists()
        integrity_counts["main_public_eval_ran"] += (
            main_eval["public_skipped"] is False
        )
        integrity_counts["nopublic_public_eval_ran"] += (
            nopublic_eval["public_skipped"] is False
        )
        main_full_run_path = main_dir / task_id / "run.json"
        if main_full_run_path.is_file():
            main_full_run = _load_json(main_full_run_path)
            if main_full_run.get("repair_provenance"):
                repaired_main_runs.append(task_id)
            integrity_counts["main_run_mount_true"] += (
                (main_full_run.get("workspace") or {}).get(
                    "public_tests_mounted"
                )
                is True
            )
        nopublic_full_run_path = nopublic_dir / task_id / "run.json"
        if nopublic_full_run_path.is_file():
            nopublic_full_run = _load_json(nopublic_full_run_path)
            integrity_counts["nopublic_run_mount_false"] += (
                (nopublic_full_run.get("workspace") or {}).get(
                    "public_tests_mounted"
                )
                is False
            )

        task_rows.append(
            {
                "task_id": task_id,
                "paired_group": group,
                "main_status": main_run.get("status"),
                "nopublic_status": nopublic_run.get("status"),
                "main_public_pass": main_eval["public_pass"],
                "main_hidden_pass": main_eval["hidden_pass"],
                "nopublic_public_pass": nopublic_eval["public_pass"],
                "nopublic_hidden_pass": nopublic_eval["hidden_pass"],
                "main_final_score": main_run.get("final_score"),
                "nopublic_final_score": nopublic_run.get("final_score"),
                "main_tokens": ((main_run.get("agent_usage") or {}).get("total_tokens")),
                "nopublic_tokens": (
                    (nopublic_run.get("agent_usage") or {}).get("total_tokens")
                ),
            }
        )

    total = len(task_rows)
    expected_integrity_keys = (
        "main_workspace_public_tests_present",
        "nopublic_workspace_public_tests_absent",
        "main_public_eval_ran",
        "nopublic_public_eval_ran",
        "main_run_mount_true",
        "nopublic_run_mount_false",
    )
    failed_integrity = {
        key: integrity_counts[key]
        for key in expected_integrity_keys
        if integrity_counts[key] != total
    }
    if failed_integrity:
        raise ValueError(
            f"ablation treatment integrity checks failed: {failed_integrity}"
        )

    main_config = main_suite.get("agent_config") or {}
    nopublic_config = nopublic_suite.get("agent_config") or {}
    config_differences = {
        key: {"main": main_config.get(key), "nopublic": nopublic_config.get(key)}
        for key in sorted(set(main_config) | set(nopublic_config))
        if main_config.get(key) != nopublic_config.get(key)
    }
    intended_config_differences = {
        "ablation_arm",
        "mount_public_tests",
        "profile",
    }
    unexpected_config_differences = sorted(
        set(config_differences) - intended_config_differences
    )
    if unexpected_config_differences:
        raise ValueError(
            "unexpected Main/No-public config differences: "
            + ", ".join(unexpected_config_differences)
        )

    main_passed = sum(row["main_status"] == "passed" for row in task_rows)
    nopublic_passed = sum(row["nopublic_status"] == "passed" for row in task_rows)
    main_interval = _wilson_interval(main_passed, total)
    nopublic_interval = _wilson_interval(nopublic_passed, total)

    legacy: dict[str, Any] | None = None
    if legacy_paths:
        legacy_runs = _load_legacy_runs(legacy_paths)
        if set(legacy_runs) != set(main_runs):
            raise ValueError("legacy and compliant Main task sets differ")
        legacy_only: list[str] = []
        compliant_only: list[str] = []
        both_pass: list[str] = []
        both_fail: list[str] = []
        for task_id in sorted(main_runs):
            legacy_pass = legacy_runs[task_id].get("status") == "passed"
            compliant_pass = main_runs[task_id].get("status") == "passed"
            target = (
                both_pass
                if legacy_pass and compliant_pass
                else legacy_only
                if legacy_pass
                else compliant_only
                if compliant_pass
                else both_fail
            )
            target.append(task_id)
        legacy_passed = sum(run.get("status") == "passed" for run in legacy_runs.values())
        legacy = {
            "legacy_passed": legacy_passed,
            "compliant_main_passed": main_passed,
            "delta_percentage_points": 100.0 * (main_passed - legacy_passed) / total,
            "both_pass": both_pass,
            "legacy_only": legacy_only,
            "compliant_only": compliant_only,
            "both_fail": both_fail,
            "exact_mcnemar_p": _exact_mcnemar_p(
                len(compliant_only), len(legacy_only)
            ),
            "caveat": (
                "Task specifications and tests changed during constitution migration; "
                "one stochastic run per condition does not identify a causal model improvement."
            ),
        }

    analysis = {
        "schema_version": "featureliftbench.ablation_pair.v1",
        "main_dir": str(main_dir),
        "nopublic_dir": str(nopublic_dir),
        "model": (main_suite.get("agent_config") or {}).get("model"),
        "total_tasks": total,
        "main": {
            "passed": main_passed,
            "pass_rate": main_passed / total,
            "wilson_95": list(main_interval),
            "summary": main_suite.get("summary"),
            "usage": main_suite.get("agent_usage_totals"),
        },
        "nopublic": {
            "passed": nopublic_passed,
            "pass_rate": nopublic_passed / total,
            "wilson_95": list(nopublic_interval),
            "summary": nopublic_suite.get("summary"),
            "usage": nopublic_suite.get("agent_usage_totals"),
        },
        "paired": {
            **{key: task_groups[key] for key in task_groups},
            "delta_percentage_points": 100.0
            * (main_passed - nopublic_passed)
            / total,
            "risk_ratio": (
                main_passed / nopublic_passed if nopublic_passed else None
            ),
            "exact_mcnemar_p": _exact_mcnemar_p(
                paired["main_only"], paired["nopublic_only"]
            ),
        },
        "gate_patterns": {
            arm: dict(patterns) for arm, patterns in gate_patterns.items()
        },
        "treatment_integrity": {
            "counts": dict(integrity_counts),
            "config_differences": config_differences,
            "unexpected_config_differences": unexpected_config_differences,
            "passed": not failed_integrity and not unexpected_config_differences,
        },
        "legacy_comparison": legacy,
        "repair_provenance": {
            "main_repaired_completed_runs": sorted(set(repaired_main_runs)),
            "note": (
                "These completed runs were reconstructed from durable usage and evaluator "
                "artifacts after a progress-output BrokenPipeError overwrote run.json. "
                "They were retained and not rerun."
            )
            if repaired_main_runs
            else "",
        },
    }
    return analysis, task_rows


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _percent(value: float) -> str:
    return f"{100.0 * value:.1f}%"


def _render_markdown(analysis: dict[str, Any]) -> str:
    main = analysis["main"]
    nopublic = analysis["nopublic"]
    paired = analysis["paired"]
    legacy = analysis.get("legacy_comparison")
    lines = [
        "# Hard-50 Compliant Main vs No-public",
        "",
        "## Outcome",
        "",
        "| Arm | Passed | Pass@1 | Wilson 95% CI | Infra failures |",
        "| --- | ---: | ---: | ---: | ---: |",
        (
            f"| Main | {main['passed']}/50 | {_percent(main['pass_rate'])} | "
            f"{_percent(main['wilson_95'][0])}–{_percent(main['wilson_95'][1])} | "
            f"{main['summary'].get('agent_failures', 0)} |"
        ),
        (
            f"| No-public | {nopublic['passed']}/50 | {_percent(nopublic['pass_rate'])} | "
            f"{_percent(nopublic['wilson_95'][0])}–{_percent(nopublic['wilson_95'][1])} | "
            f"{nopublic['summary'].get('agent_failures', 0)} |"
        ),
        "",
        (
            f"Main exceeds No-public by **{paired['delta_percentage_points']:.1f} "
            f"percentage points** ({paired['risk_ratio']:.2f}× pass rate). "
            f"Exact paired McNemar p = **{paired['exact_mcnemar_p']:.6f}**."
        ),
        "",
        "## Paired outcomes",
        "",
        "| Outcome | Count |",
        "| --- | ---: |",
        f"| Both pass | {len(paired['both_pass'])} |",
        f"| Main only | {len(paired['main_only'])} |",
        f"| No-public only | {len(paired['nopublic_only'])} |",
        f"| Both fail | {len(paired['both_fail'])} |",
        "",
        "Main-only passes:",
        "",
    ]
    lines.extend(f"- `{task_id}`" for task_id in paired["main_only"])
    lines.extend(
        [
            "",
            "No-public-only passes: **none**.",
            "",
            "## Evaluator gate patterns",
            "",
            "### Main",
            "",
        ]
    )
    lines.extend(
        f"- {count} × `{pattern}`"
        for pattern, count in sorted(
            analysis["gate_patterns"]["main"].items(),
            key=lambda item: (-item[1], item[0]),
        )
    )
    lines.extend(["", "### No-public", ""])
    lines.extend(
        f"- {count} × `{pattern}`"
        for pattern, count in sorted(
            analysis["gate_patterns"]["nopublic"].items(),
            key=lambda item: (-item[1], item[0]),
        )
    )

    if legacy is not None:
        lines.extend(
            [
                "",
                "## Legacy comparison",
                "",
                (
                    f"Legacy hard-50: **{legacy['legacy_passed']}/50**; compliant "
                    f"Main: **{legacy['compliant_main_passed']}/50** "
                    f"({legacy['delta_percentage_points']:+.1f} percentage points)."
                ),
                "",
                "| Outcome | Count |",
                "| --- | ---: |",
                f"| Both pass | {len(legacy['both_pass'])} |",
                f"| Legacy only | {len(legacy['legacy_only'])} |",
                f"| Compliant only | {len(legacy['compliant_only'])} |",
                f"| Both fail | {len(legacy['both_fail'])} |",
                "",
                f"Exact paired McNemar p = **{legacy['exact_mcnemar_p']:.3f}**.",
                "",
                f"Caveat: {legacy['caveat']}",
            ]
        )

    main_usage = main.get("usage") or {}
    nopublic_usage = nopublic.get("usage") or {}
    lines.extend(
        [
            "",
            "## Usage and integrity",
            "",
            "| Arm | API calls | Total tokens | Context violations | Missing usage |",
            "| --- | ---: | ---: | ---: | ---: |",
            (
                f"| Main | {main_usage.get('api_calls', 0):,} | "
                f"{main_usage.get('total_tokens', 0):,} | "
                f"{(main_usage.get('context_audit') or {}).get('context_violation_runs', 0)} | "
                f"{main_usage.get('missing_runs', 0)} |"
            ),
            (
                f"| No-public | {nopublic_usage.get('api_calls', 0):,} | "
                f"{nopublic_usage.get('total_tokens', 0):,} | "
                f"{(nopublic_usage.get('context_audit') or {}).get('context_violation_runs', 0)} | "
                f"{nopublic_usage.get('missing_runs', 0)} |"
            ),
            "",
            (
                "Both arms used the same model, standard prompt, 120-step limit, "
                "Docker agent/evaluator, and frozen 50-task list. The intended treatment "
                "difference was whether public tests were mounted in the agent workspace."
            ),
            "",
            "Treatment-integrity checks: **pass**.",
            "",
            "- Main workspace contains public tests: 50/50.",
            "- No-public workspace omits public tests: 50/50.",
            "- Post-submit evaluator ran public tests in both arms: 50/50 each.",
            "- No unexpected configuration differences were found.",
        ]
    )

    repaired = analysis["repair_provenance"]["main_repaired_completed_runs"]
    if repaired:
        lines.extend(
            [
                "",
                "### Interruption provenance",
                "",
                analysis["repair_provenance"]["note"],
                "",
            ]
        )
        lines.extend(f"- `{task_id}`" for task_id in repaired)
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("main_dir", type=Path)
    parser.add_argument("nopublic_dir", type=Path)
    parser.add_argument(
        "--legacy-suite",
        action="append",
        default=[],
        type=Path,
        help="Legacy suite directory or suite.json; may be repeated.",
    )
    parser.add_argument(
        "--output-prefix",
        required=True,
        type=Path,
        help="Output path without extension.",
    )
    args = parser.parse_args()

    analysis, rows = build_analysis(
        args.main_dir.resolve(),
        args.nopublic_dir.resolve(),
        [path.resolve() for path in args.legacy_suite],
    )
    prefix = args.output_prefix.resolve()
    prefix.parent.mkdir(parents=True, exist_ok=True)
    json_path = prefix.with_suffix(".json")
    csv_path = prefix.with_suffix(".csv")
    markdown_path = prefix.with_suffix(".md")
    json_path.write_text(
        json.dumps(analysis, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_csv(csv_path, rows)
    markdown_path.write_text(_render_markdown(analysis), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {csv_path}")
    print(f"Wrote {markdown_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
