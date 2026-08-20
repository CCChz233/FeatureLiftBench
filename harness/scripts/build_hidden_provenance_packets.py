#!/usr/bin/env python3
"""Build compact Hidden-provenance packets from public_spec + hidden tests + eval logs.

Does not label. Does not implement an agent method.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO / "harness"))

TASKS_ROOT = _REPO / "benchmark" / "python200_tasks"
LOCAL_SUITE = (
    _REPO
    / "experiments/python/openhands/deepseek-v4-flash"
    / "python200-deepseek-v4-flash-vllm-local-0812-001"
)
API_BASELINE = (
    _REPO
    / "experiments/FeatureLiftBench-v3-846-20260801-ready/experiments/export"
    / "FeatureLiftBench-deepseek-v4-flash-150-20260805/deepseek-v4-flash-0731"
)
API_E50 = (
    _REPO
    / "experiments/python/openhands/deepseek-v4-flash"
    / "external50-deepseek-v4-flash-0805-main-001"
)
FAILED_RE = re.compile(r"^FAILED \S+::(\S+)", re.MULTILINE)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _behaviors(public_spec: dict[str, Any]) -> list[dict[str, str]]:
    rows = []
    for item in public_spec.get("behaviors") or []:
        if isinstance(item, dict) and item.get("id") and item.get("text"):
            rows.append({"id": str(item["id"]), "text": str(item["text"])})
    iso = public_spec.get("isolation_behavior")
    if isinstance(iso, dict) and iso.get("id") and iso.get("text"):
        rows.append({"id": str(iso["id"]), "text": str(iso["text"])})
    return rows


def _api_paths(public_spec: dict[str, Any]) -> list[str]:
    paths: list[str] = []

    def walk(items: Any) -> None:
        if not isinstance(items, list):
            return
        for item in items:
            if not isinstance(item, dict):
                continue
            path = item.get("path")
            if isinstance(path, str) and path:
                paths.append(path)
            walk(item.get("members"))

    walk(public_spec.get("required_api"))
    return paths


def _hidden_tests(task_id: str) -> str:
    folder = TASKS_ROOT / task_id / "hidden_tests"
    chunks: list[str] = []
    if not folder.is_dir():
        return ""
    for path in sorted(folder.glob("*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if len(text) > 8000:
            text = text[:8000] + "\n# ... truncated ...\n"
        chunks.append(f"# FILE {path.name}\n{text}")
    return "\n\n".join(chunks)


def _eval_dir(task_id: str, prefer_local: bool) -> Path | None:
    local = LOCAL_SUITE / task_id / "eval"
    if prefer_local and (local / "result.json").is_file():
        return local
    for root in (API_E50, API_BASELINE, LOCAL_SUITE):
        cand = root / task_id / "eval"
        if (cand / "result.json").is_file():
            return cand
    return None


def _fail_names(stdout: str) -> list[str]:
    return FAILED_RE.findall(stdout or "")


def packet_for(task_id: str, *, local_hidden: bool, api_hidden: bool) -> dict[str, Any]:
    meta = _load(TASKS_ROOT / task_id / "metadata.json")
    spec = meta.get("public_spec") if isinstance(meta.get("public_spec"), dict) else {}
    eval_dir = _eval_dir(task_id, prefer_local=local_hidden)
    stdout = ""
    result: dict[str, Any] = {}
    if eval_dir is not None:
        result = _load(eval_dir / "result.json")
        hidden_log = eval_dir / "logs" / "hidden.stdout"
        if hidden_log.is_file():
            stdout = hidden_log.read_text(encoding="utf-8", errors="replace")
            if len(stdout) > 12000:
                stdout = stdout[:12000] + "\n# ... truncated ...\n"
    return {
        "task_id": task_id,
        "local_hidden_failure": local_hidden,
        "api_hidden_failure": api_hidden,
        "eval_dir": str(eval_dir) if eval_dir else None,
        "public_pass": result.get("public_tests_pass"),
        "hidden_pass": result.get("hidden_tests_pass"),
        "functional_gate": (result.get("scores") or {}).get("functional_gate")
        if isinstance(result.get("scores"), dict)
        else None,
        "behaviors": _behaviors(spec),
        "required_api": _api_paths(spec),
        "failed_hidden_tests": _fail_names(stdout),
        "hidden_stdout_excerpt": stdout,
        "hidden_tests_source": _hidden_tests(task_id),
    }


def main() -> int:
    snapshot = _load(
        _REPO
        / "artifacts/research_analysis/current_results"
        / "python200_cross_model_main_20260818.json"
    )
    local = set(
        snapshot["models"]["deepseek_local"]["python200"]["task_ids_by_primary_outcome"][
            "hidden_failure"
        ]
    )
    api = set(
        snapshot["models"]["deepseek_api"]["python200"]["task_ids_by_primary_outcome"][
            "hidden_failure"
        ]
    )
    union = sorted(local | api)
    packets = [
        packet_for(task_id, local_hidden=task_id in local, api_hidden=task_id in api)
        for task_id in union
    ]
    out = {
        "schema_version": "featureliftbench.hidden_provenance_packets.v1",
        "slice": "hidden_provenance_flash33_v1",
        "n": len(packets),
        "packets": packets,
    }
    dest = _REPO / "artifacts/research_analysis/hidden_provenance/flash33_packets.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {dest} n={len(packets)}")
    missing = [p["task_id"] for p in packets if not p["eval_dir"]]
    if missing:
        print("missing eval", missing)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
