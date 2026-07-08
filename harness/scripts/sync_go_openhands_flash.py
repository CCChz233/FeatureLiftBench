#!/usr/bin/env python3
"""Copy OpenHands run summary into go-pilot flash evidence."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def sync_flash(task_id: str, run_dir: Path) -> Path:
    run_dir = run_dir.resolve()
    run_json = run_dir / "run.json"
    if not run_json.is_file():
        raise SystemExit(f"missing {run_json}")
    data = json.loads(run_json.read_text(encoding="utf-8"))
    evaluation = data.get("evaluation") or {}
    scores = evaluation.get("scores") or {}
    public = evaluation.get("public_tests") or {}
    hidden = evaluation.get("hidden_tests") or {}
    eval_result_path = run_dir / "eval" / "result.json"
    if eval_result_path.is_file():
        eval_data = json.loads(eval_result_path.read_text(encoding="utf-8"))
        scores = eval_data.get("scores") or scores
        public = eval_data.get("public_tests") or public
        hidden = eval_data.get("hidden_tests") or hidden
    agent = data.get("agent") or {}

    flash = {
        "task_id": task_id,
        "model": "deepseek/deepseek-v4-flash",
        "agent": "openhands",
        "status": data.get("status", "unknown"),
        "evaluation": {
            "scores": {
                "functional_gate": scores.get("functional_gate"),
                "extraction_ratio": scores.get("extraction_ratio"),
                "final_score": scores.get("final_score"),
            },
            "public_tests": {"passed": public.get("passed")},
            "hidden_tests": {"passed": hidden.get("passed")},
            "result_json": str(eval_result_path.as_posix()),
        },
        "agent_run": {
            "passed": agent.get("passed"),
            "duration_seconds": agent.get("duration_seconds"),
        },
        "source_run": str(run_dir.relative_to(REPO).as_posix()),
    }

    out_dir = REPO / "evidence" / "go" / "go-pilot" / task_id / "review" / "flash"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "run.json"
    out_path.write_text(json.dumps(flash, indent=2) + "\n", encoding="utf-8")

    agent_src = run_dir / "agent"
    if agent_src.is_dir():
        dest = out_dir / "agent_logs"
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(agent_src, dest)

    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_id")
    parser.add_argument("run_dir", type=Path, help="experiments/GO/openhands/<model>/<run_id>")
    args = parser.parse_args()
    run_dir = args.run_dir if args.run_dir.is_absolute() else REPO / args.run_dir
    out = sync_flash(args.task_id, run_dir.resolve())
    print(f"synced flash evidence: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
