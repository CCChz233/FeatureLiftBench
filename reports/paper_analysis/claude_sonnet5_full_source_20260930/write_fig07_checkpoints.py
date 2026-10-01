#!/usr/bin/env python3
"""Write Fig. 7 checkpoint rows once all 150 replays have metrics."""

from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIG = HERE / "fig07" / "runs" / "claude-sonnet-5"
RUNS = Path("experiments/python/openhands/claude-sonnet-5/python150-main-r1")
OUT = HERE / "fig07_checkpoints.csv"
FIELDS = [
    "task_id",
    "final_pass",
    "replay_status",
    "sufficiency_status",
    "include_checkpoint",
    "first_pass_state_index",
    "first_pass_tokens",
    "post_sufficiency_tokens",
    "post_sufficiency_fraction",
    "include_response",
    "post_responses",
    "total_primary_responses",
    "exclusion_reason",
]


def event_responses(events: list[dict]) -> dict[str, int]:
    found: dict[str, int] = {}
    for index, event in enumerate(events):
        if event.get("kind") not in ("ActionEvent", "MessageEvent"):
            continue
        response_id = event.get("llm_response_id")
        if response_id:
            found.setdefault(response_id, index)
    return found


def one(task_id: str) -> dict:
    metric = json.loads((FIG / task_id / "metrics.json").read_text())
    timeline = [
        json.loads(line)
        for line in (FIG / task_id / "artifact_timeline.jsonl").read_text().splitlines()
        if line.strip()
    ]
    evaluations = json.loads((FIG / task_id / "snapshot_evaluations.json").read_text())
    events_path = RUNS / task_id / "agent" / "openhands_events.jsonl"
    events = [
        json.loads(line)
        for line in events_path.read_text().splitlines()
        if line.strip()
    ] if events_path.exists() else []
    reasons = []
    if metric.get("identity_status") != "ok":
        reasons.append("identity")
    if metric.get("final_eval_matches") is not True:
        reasons.append("final_eval_mismatch")
    if metric.get("full_timeline_covered") is not True:
        reasons.append("incomplete_timeline")
    if metric.get("unresolved_states") not in (0, None) and metric.get("unresolved_states") != 0:
        reasons.append("unresolved_checkpoint_evaluation")
    if not metric.get("final_pass"):
        reasons.append("final_failure")
    passing = [
        state
        for state in timeline
        if evaluations.get(state["artifact_hash"], {}).get("functional_pass") is True
    ]
    primary = event_responses(events)
    post_responses = ""
    include_response = False
    if metric.get("final_pass") and not passing:
        reasons.append("no_observed_passing_checkpoint")
    elif passing:
        checkpoint = passing[0]
        matches = [index for index, event in enumerate(events) if event.get("id") == checkpoint.get("event_id")]
        if len(matches) != 1 or events[matches[0]].get("kind") != "ObservationEvent":
            reasons.append("missing_checkpoint_observation")
        else:
            cut = matches[0]
            response_id = checkpoint.get("llm_response_id")
            first = {}
            for index, event in enumerate(events):
                if event.get("llm_response_id"):
                    first.setdefault(event["llm_response_id"], index)
            if response_id not in first or first[response_id] > cut:
                reasons.append("invalid_producing_response_boundary")
            elif not reasons or reasons == ["final_failure"]:
                include_response = metric.get("final_pass") is True and "final_failure" not in reasons
                post_responses = sum(index > cut for index in primary.values())
    if not metric.get("include_psf_primary"):
        psf = metric.get("exclusion_reason_psf_primary") or metric.get("missing_reason") or "checkpoint_not_exact"
        if psf and psf not in reasons:
            reasons.append(psf)
    include_checkpoint = bool(metric.get("include_psf_primary"))
    return {
        "task_id": task_id,
        "final_pass": metric.get("final_pass"),
        "replay_status": metric.get("replay_status"),
        "sufficiency_status": metric.get("sufficiency_status"),
        "include_checkpoint": include_checkpoint,
        "first_pass_state_index": metric.get("first_pass_state_index") if passing else "",
        "first_pass_tokens": metric.get("first_pass_tokens") if include_checkpoint else "",
        "post_sufficiency_tokens": metric.get("post_sufficiency_tokens") if include_checkpoint else "",
        "post_sufficiency_fraction": metric.get("post_sufficiency_fraction") if include_checkpoint else "",
        "include_response": include_response,
        "post_responses": post_responses if include_response else "",
        "total_primary_responses": len(primary),
        "exclusion_reason": ";".join(reasons),
    }


def main() -> int:
    tasks = sorted(path.name for path in FIG.iterdir() if (path / "metrics.json").exists()) if FIG.exists() else []
    if len(tasks) != 150:
        print(f"fig07 metrics {len(tasks)}/150; checkpoint table not written", flush=True)
        return 2
    rows = [one(task_id) for task_id in tasks]
    with OUT.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    included = sum(row["include_checkpoint"] is True for row in rows)
    responses = sum(row["include_response"] is True for row in rows)
    print(f"wrote {OUT} rows={len(rows)} checkpoint_n={included} response_n={responses}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
