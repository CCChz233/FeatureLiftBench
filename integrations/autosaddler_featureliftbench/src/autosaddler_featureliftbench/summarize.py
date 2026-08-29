from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any


def summarize_run(run_dir: Path) -> dict[str, Any]:
    events = [json.loads(line) for line in (run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines() if line]
    evaluations: list[Mapping[str, Any]] = []
    task_rollouts = 0
    rollouts_by_purpose: dict[str, int] = {}
    task_input_tokens = 0
    task_output_tokens = 0
    optimizer_input_tokens = 0
    optimizer_output_tokens = 0
    for event in events:
        if event.get("event_type") == "EvaluationCompleted":
            payload = event.get("payload", {})
            evaluation = payload.get("evaluation") if isinstance(payload, Mapping) else None
            if isinstance(evaluation, Mapping):
                evaluations.append(evaluation)
        elif event.get("event_type") == "EvaluationAttemptStarted":
            payload = event.get("payload", {})
            if isinstance(payload, Mapping):
                task_rollouts += 1
                purpose = str(payload.get("evaluation_operation_id") or "unknown").rsplit(":", 1)[-1]
                rollouts_by_purpose[purpose] = rollouts_by_purpose.get(purpose, 0) + 1
        elif event.get("event_type") == "ModelUsageObserved":
            payload = event.get("payload", {})
            usage = payload.get("usage") if isinstance(payload, Mapping) else None
            if not isinstance(usage, Mapping):
                continue
            role = usage.get("role")
            input_tokens = int(usage.get("input_tokens", 0) or 0)
            output_tokens = int(usage.get("output_tokens", 0) or 0)
            if role == "task_agent":
                task_input_tokens += input_tokens
                task_output_tokens += output_tokens
            elif role == "optimizer":
                optimizer_input_tokens += input_tokens
                optimizer_output_tokens += output_tokens

    development = [item for item in evaluations if item.get("split") == "development"]
    train_before = next((item for item in evaluations if item.get("purpose") == "train_before"), None)
    train_after = next((item for item in evaluations if item.get("purpose") == "train_after"), None)
    baseline = _aggregate(development[0]) if development else None
    result_path = run_dir / "result.json"
    result = json.loads(result_path.read_text(encoding="utf-8")) if result_path.is_file() else {}
    selected = result.get("development_score") if isinstance(result, Mapping) else None
    return {
        "schema_version": "autosaddler-featureliftbench-summary/v1",
        "run_dir": str(run_dir.resolve()),
        "baseline_development_score": baseline,
        "selected_development_score": selected,
        "development_delta": (
            float(selected) - float(baseline)
            if isinstance(selected, (int, float)) and isinstance(baseline, (int, float))
            else None
        ),
        "train_before_score": _aggregate(train_before) if train_before is not None else None,
        "train_after_score": _aggregate(train_after) if train_after is not None else None,
        "task_agent_rollouts": task_rollouts,
        "task_agent_rollouts_by_purpose": dict(sorted(rollouts_by_purpose.items())),
        "task_agent_input_tokens": task_input_tokens,
        "task_agent_output_tokens": task_output_tokens,
        "task_agent_total_tokens": task_input_tokens + task_output_tokens,
        "optimizer_input_tokens": optimizer_input_tokens,
        "optimizer_output_tokens": optimizer_output_tokens,
        "optimizer_total_tokens": optimizer_input_tokens + optimizer_output_tokens,
        "total_measured_tokens": task_input_tokens + task_output_tokens + optimizer_input_tokens + optimizer_output_tokens,
    }


def _aggregate(evaluation: Mapping[str, Any]) -> float | None:
    scores = [
        observation.get("score")
        for observation in evaluation.get("observations", [])
        if isinstance(observation, Mapping)
        and observation.get("disposition") in {"success", "task_failure"}
        and isinstance(observation.get("score"), (int, float))
    ]
    return sum(float(score) for score in scores) / len(scores) if scores else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    summary = summarize_run(args.run_dir)
    text = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
