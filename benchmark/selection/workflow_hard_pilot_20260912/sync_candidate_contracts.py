"""Apply an explicit pre-calibration contract repair to existing pilot assets.

Does not acquire/read full source trees or claim a fresh upstream probe. SQLGlot
expectations are a canonical reorder of already recorded upstream graph nodes.
"""
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "harness"))
from featureliftbench.task_render import render_public_task
from featureliftbench.task_spec import sync_spec_hashes
from definitions import TASKS


def canonicalize(node):
    children = [canonicalize(child) for child in node["downstream"]]
    return {**node, "downstream": sorted(children, key=lambda child: json.dumps(child, sort_keys=True, ensure_ascii=True))}


def main():
    for definition in TASKS:
        task = ROOT / "benchmark/staging" / definition["task_id"]
        if definition["source"] == "sqlglot":
            fixture_path = HERE / "fixtures/sqlglot.json"
            fixtures = json.loads(fixture_path.read_text(encoding="utf-8"))
            for case in fixtures:
                if not case["error"]:
                    case["expected"] = canonicalize(case["expected"])
            fixture_path.write_text(json.dumps(fixtures, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            for tier in ("public", "hidden"):
                cases = [case for case in fixtures if case["tier"] == tier]
                (task / (tier + "_tests/cases.json")).write_text(json.dumps(cases, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            shutil.copyfile(HERE / "adapters/sqlglot.py", task / "reference_solution/featurelifted/__init__.py")
            revision = dict(task_revision=2, reason="Pre-calibration determinism repair", transformation="Recursively sort recorded downstream nodes by canonical JSON key; preserve all node values and duplicates.", fresh_upstream_probe=False, original_probe="upstream_probe.py / pinned source_evidence.json", calibration_runs_before_change=0)
            (task / "evaluation/contract_revision.json").write_text(json.dumps(revision, indent=2) + "\n", encoding="utf-8")
        metadata = json.loads((task / "metadata.json").read_text(encoding="utf-8"))
        metadata["task_revision"] = definition.get("revision", 1)
        metadata["feature"]["source_entrypoints"] = definition["source_files"]
        metadata["feature"]["included_behaviors"] = [text for _, text in definition["behaviors"]]
        metadata["public_spec"]["behaviors"] = [dict(id=i, text=t) for i, t in definition["behaviors"]]
        metadata["evaluation_spec"]["public_clauses"] = [dict(behavior_id=i, clause_kind="included_behavior", text=t) for i, t in definition["behaviors"]]
        markdown = render_public_task(metadata)
        metadata = sync_spec_hashes(metadata, markdown)
        (task / "TASK.md").write_text(markdown, encoding="utf-8")
        (task / "metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
