"""Generate candidate packages, preserving the existing published benchmark."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT / "harness"), str(ROOT / "scripts")]
from featureliftbench.task_render import render_public_task
from featureliftbench.task_spec import sync_spec_hashes
from build_source_registry import build_registry, validate_registry
from definitions import TASKS
from lift_references import build_pip, build_dbt, build_sqlglot, write


def materialize(definition, source):
    task = ROOT / "benchmark/staging" / definition["task_id"]
    task.mkdir(parents=True, exist_ok=True)
    fixtures = json.loads((HERE / "fixtures" / (definition["source"] + ".json")).read_text(encoding="utf-8"))
    spec = dict(title=definition["title"], summary=definition["summary"], required_api=[dict(path="featurelifted." + definition["api"], kind="function", signature=definition["signature"])], optional_api=[], behaviors=[dict(id=i, text=t) for i, t in definition["behaviors"]], exclusions=definition["exclusions"], forbidden=dict(imports=definition["forbidden"], paths=["repo/"]))
    evaluation = dict(public_clauses=[dict(behavior_id=i, clause_kind="included_behavior", text=t) for i, t in definition["behaviors"]], public_test_mappings=[], hidden_test_mappings=[], required_api_coverage=[dict(path="featurelifted." + definition["api"], covered_by_tests=["hidden_tests/test_contract.py::test_contract"])], manual_review=dict(reviewer="Codex", reviewer_type="ai_assisted", reviewed_at="2026-09-12", checklist_passed=True, notes="Author reviewed declared inputs, exclusions, upstream adapter, fixture coverage and generated contract. Not independent human review; executable gate results are recorded separately."))
    for tier in ["public", "hidden"]:
        selected = [f for f in fixtures if f["tier"] == tier]
        folder = task / (tier + "_tests")
        write(folder / "cases.json", json.dumps(selected, indent=2, ensure_ascii=False) + "\n")
        script = '''from copy import deepcopy
import json
from pathlib import Path
import pytest
import featurelifted

CASES = json.loads(Path(__file__).with_name("cases.json").read_text(encoding="utf-8"))

@pytest.mark.parametrize("case", CASES, ids=lambda c: c["name"])
def test_contract(case):
    original = deepcopy(case["args"])
    arguments = deepcopy(original)
    if case["error"]:
        with pytest.raises(ValueError):
            featurelifted.API(**arguments)
    else:
        assert featurelifted.API(**arguments) == case["expected"]
    assert arguments == original

def test_repeated_calls_are_independent():
    normal = [c for c in CASES if not c["error"]]
    for case in normal + list(reversed(normal)):
        assert featurelifted.API(**deepcopy(case["args"])) == case["expected"]
'''.replace("featurelifted.API", "featurelifted." + definition["api"])
        write(folder / "test_contract.py", script)
        ids = sorted({i for f in selected for i in f["behavior_ids"]})
        evaluation[tier + "_test_mappings"] = [dict(nodeid=f"{tier}_tests/test_contract.py::test_contract", behavior_ids=ids, mapping_method="authored_scenarios_with_pinned_upstream_expectations"), dict(nodeid=f"{tier}_tests/test_contract.py::test_repeated_calls_are_independent", behavior_ids=["B001"], mapping_method="explicit_state_independence")]
    metadata = dict(task_id=definition["task_id"], language="python", difficulty="hard", status="materialized_candidate", task_revision=definition.get("revision", 1), tags=["workflow-pilot-20260912", "difficulty_uncalibrated"], source=dict(name=source["name"], url=source["url"], commit=source["commit"], license=source["license"]), feature=dict(name=definition["title"], description=definition["consumer"], included_behaviors=[t for _, t in definition["behaviors"]], excluded_behaviors=definition["exclusions"]), output=dict(package="featurelifted", **{"import": "from featurelifted import " + definition["api"]}, callable=definition["api"], signature=definition["signature"]), environment=dict(python="3.12", network=False, timeout_seconds=120, dependency_lock="requirements.lock", allowed_dependencies=definition["dependencies"], forbidden_dependencies=definition["forbidden"], forbidden_imports=definition["forbidden"], forbidden_paths=["repo/"]), tests=dict(public="public_tests/", hidden="hidden_tests/", command="pytest"), spec_status="compliant", public_spec=spec, evaluation_spec=evaluation, entanglement=dict(level="high", primary="data_model_coupling", types=["data_model_coupling", "framework_coupling"], description="Design hypothesis only; empirical difficulty pending."), difficulty_evidence=dict(status="uncalibrated", source_overlap_with_retired_external50=source["legacy_overlap"]))
    # Required historical fields remain private; the Main workspace redactor
    # removes feature.source_entrypoints and entanglement entirely.
    metadata["feature"]["source_entrypoints"] = definition["source_files"]
    metadata["entanglement"].update(primary="data_model_coupling", types=["data_model_coupling", "framework_coupling"], signals=["cross-module observable behavior", "host data model adaptation"])
    markdown = render_public_task(metadata)
    metadata = sync_spec_hashes(metadata, markdown)
    write(task / "metadata.json", json.dumps(metadata, indent=2, ensure_ascii=False) + "\n")
    write(task / "TASK.md", markdown)
    write(task / "requirements.lock", "\n".join(definition["dependencies"]) + "\n")
    write(task / "evaluation/forbidden_imports.txt", "\n".join(definition["forbidden"]) + "\n")
    provenance = dict(source_commit=source["commit"], source_files=definition["source_files"], required_files=definition["source_files"], upstream_test_evidence=definition["upstream_tests"], semantic_delta=definition["reference_note"], source_tree_sha256=source["source_tree_sha256"], oracle_basis="pinned_upstream_definitions_and_explicit_record_adapter", independent_upstream_probe="benchmark/selection/workflow_hard_pilot_20260912/upstream_probe.py")
    write(task / "evaluation/oracle_manifest.json", json.dumps(provenance, indent=2) + "\n")
    reference = task / "reference_solution/featurelifted"
    reference.mkdir(parents=True, exist_ok=True)
    {"pip": build_pip, "dbt-core": build_dbt, "sqlglot": build_sqlglot}[definition["source"]](reference)
    shutil.copyfile(ROOT / source["tree_path"] / source["license_path"], reference / "UPSTREAM_LICENSE.txt")
    write(reference / "NOTICE.txt", f"Derived from {source['url']} at {source['commit']}.\nChanges: selected definitions, import/host-boundary adaptation, namespace rewriting as described in private provenance.\n")
    # Staging provenance is a full source tree too; official runs use the archive.
    shutil.copytree(ROOT / source["tree_path"], task / "repo", dirs_exist_ok=True)
    return task


def main():
    sources = {s["name"]: s for s in json.loads((HERE / "source_evidence.json").read_text())}
    paths = [materialize(d, sources[d["source"]]) for d in TASKS]
    registry = build_registry(ROOT / "benchmark/staging")
    for snapshot in registry["snapshots"]:
        definition = next(d for d in TASKS if d["task_id"] in snapshot["task_ids"])
        source = sources[definition["source"]]
        snapshot.update({k: source[k] for k in ["archive_path", "archive_sha256", "source_tree_sha256", "tracked_file_count", "python_file_count", "python_loc", "total_bytes", "max_path_depth"]})
        snapshot.update(resolved_commit=source["commit"], acquisition_method="git_checkout", current_snapshot_scope="full_tracked_tree", status="ready", license_text_path=source["license_path"])
    registry["summary"]["ready_snapshot_count"] = len(registry["snapshots"])
    registry["summary"]["pending_snapshot_count"] = 0
    errors = validate_registry(registry)
    if errors:
        raise ValueError(errors)
    write(ROOT / "benchmark/sources/workflow_hard_pilot_registry.json", json.dumps(registry, indent=2, sort_keys=True) + "\n")
    print(json.dumps(dict(tasks=[p.relative_to(ROOT).as_posix() for p in paths], source_registry="benchmark/sources/workflow_hard_pilot_registry.json"), indent=2))


if __name__ == "__main__":
    main()
