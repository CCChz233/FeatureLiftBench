from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def _load_refresh_suite():
    path = Path(__file__).resolve().parents[1] / "scripts" / "refresh_suite_from_task_runs.py"
    spec = importlib.util.spec_from_file_location("refresh_suite_from_task_runs", path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_refresh_suite_rebuilds_summary_from_task_run_json(tmp_path: Path) -> None:
    refresh = _load_refresh_suite()
    suite_dir = tmp_path / "suite"
    task_dir = suite_dir / "semver__version_parse_core__001"
    task_dir.mkdir(parents=True)
    (suite_dir / "suite.json").write_text(
        json.dumps(
            {
                "runs": [
                    {
                        "task_id": "semver__version_parse_core__001",
                        "status": "failed",
                    }
                ],
                "summary": {"passed": 0, "failed": 1, "total": 1},
            }
        ),
        encoding="utf-8",
    )
    (task_dir / "run.json").write_text(
        json.dumps(
            {
                "task_id": "semver__version_parse_core__001",
                "status": "passed",
                "agent": {"usage": {"available": True, "api_calls": 3}},
                "evaluation": {"scores": {"final_score": 0.42}},
            }
        ),
        encoding="utf-8",
    )

    suite = refresh.refresh_suite(suite_dir)

    assert suite["summary"]["passed"] == 1
    assert suite["summary"]["failed"] == 0
    assert suite["runs"][0]["status"] == "passed"
    assert suite["agent_usage_totals"]["api_calls"] == 3
