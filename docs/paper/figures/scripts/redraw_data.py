"""Assemble the three revised figures from saved records, without evaluation."""
import csv
import hashlib
import json
import math
from collections import Counter
from statistics import median

from figure_data import ROOT, SOURCE, STATS, flag, load_results
from paper_style import BACKEND_ORDER, FIGURES_DIR
from paper_inputs import input_path

MECHANISMS = {
    "Code dependencies": {"static_transitive_dependency", "implicit_runtime_dependency", "third_party_contract"},
    "Data and state": {"data_model_invariant", "parser_state", "global_state_registry"},
    "Framework mechanisms": {"framework_lifecycle", "dynamic_import_plugin"},
    "Environment and resources": {"config_environment", "resource_packaging"},
}
LIFT_TYPES = ("Direct", "Adapted", "Composite")
FEATURE_FAMILIES = {
    "registry_plugin_dispatch": "Registry / dispatch",
    "parse_tokenize_decode": "Parsing / decoding",
    "config_resolve_discover": "Configuration / discovery",
    "validate_normalize_construct": "Validation / construction",
    "serialize_format_render": "Serialization / rendering",
    "workflow_session_orchestration": "Workflow / orchestration",
    "resource_metadata_loading": "Resources / metadata",
    "algorithm_data_structure": "Algorithms / data structures",
    "protocol_state_transition": "Protocol / state transitions",
    "cache_retry_policy": "Cache / retry policies",
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def export(name, payload, sources):
    payload["sources"] = [{"path": p.relative_to(ROOT).as_posix(),
                           "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                          for p in sorted(set(sources))]
    destination = FIGURES_DIR / "data" / f"{name}.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def task_coverage():
    taxonomy_path = input_path("mechanism_taxonomy")
    inventory_path = input_path("task_inventory")
    freeze_path = input_path("release_manifest")
    lift_path = input_path("lift_taxonomy")
    sources = [taxonomy_path, inventory_path, freeze_path, lift_path, SOURCE,
               ROOT / "docs/paper/writing/author_review_statement.json",
               ROOT / "docs/reference/research_analysis/BENCHMARK_TAXONOMY_SPEC.md",
               ROOT / "docs/reference/LIFT_TAXONOMY.md"]
    with taxonomy_path.open(encoding="utf-8-sig", newline="") as handle:
        taxonomy = list(csv.DictReader(handle))
    with lift_path.open(encoding="utf-8-sig", newline="") as handle:
        lift_records = {r["task_id"]: r for r in csv.DictReader(handle)}
    inventory_rows = read_json(inventory_path)["tasks"]
    inventory = {r["task_id"]: r for r in inventory_rows}
    freeze = read_json(freeze_path)["tasks"]
    evaluated = {t for t, record in freeze.items() if record["stratum"] == "python150"}
    assert len(inventory_rows) == len(inventory) == len(freeze) == len(lift_records) == 200
    assert set(inventory) == set(freeze) == set(lift_records)
    assert len(taxonomy) == len(evaluated) == 150
    assert {r["task_id"] for r in taxonomy} == evaluated
    complete_tasks = []
    for task_id, item in sorted(inventory.items()):
        record = lift_records[task_id]
        folder = "tasks" if task_id in evaluated else "hard50"
        metadata_path = ROOT / "benchmark" / folder / task_id / "metadata.json"
        statement_path = metadata_path.parent / "TASK.md"
        metadata = read_json(metadata_path)
        sources.extend([metadata_path, statement_path])
        public_digest = hashlib.sha256(json.dumps(metadata["public_spec"], sort_keys=True,
            separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
        statement_digest = hashlib.sha256(statement_path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
        assert public_digest == freeze[task_id]["spec_hash"], task_id
        assert statement_digest == freeze[task_id]["generated_task_hash"], task_id
        assert set(filter(None, record["entanglement_types_original"].split(";"))) == set(metadata["entanglement"]["types"]), task_id
        assert item["source_repo_id"] == freeze[task_id]["source_repo_id"], task_id
        assert item["source_snapshot_id"] == freeze[task_id]["source_snapshot_id"], task_id
        family = item["historical_feature_family"]
        lift = item["historical_lift_type"]
        assert family in FEATURE_FAMILIES and family == record["feature_family_v2"], task_id
        assert lift in LIFT_TYPES and lift == record["lift_type"], task_id
        complete_tasks.append({"task_id": task_id, "feature_family": family,
            "lift_type": lift, "source_repo_id": item["source_repo_id"],
            "source_snapshot_id": item["source_snapshot_id"],
            "common_comparison": task_id in evaluated,
            "mechanism_coverage_available": task_id in evaluated,
            "mechanisms": None,
            "annotation_source_status": record["taxonomy_coverage"]})
    lift_counts = Counter(t["lift_type"] for t in complete_tasks)
    assert lift_counts == {"Direct": 68, "Adapted": 100, "Composite": 32}
    assert len({t["source_repo_id"] for t in complete_tasks}) == 176
    assert len({t["source_snapshot_id"] for t in complete_tasks}) == 182
    families = []
    for family, label in FEATURE_FAMILIES.items():
        subset = [t for t in complete_tasks if t["feature_family"] == family]
        by_lift = Counter(t["lift_type"] for t in subset)
        families.append({"key": family, "label": label, "count": len(subset),
            "lift_counts": {lift: by_lift[lift] for lift in LIFT_TYPES}})
    assert sum(f["count"] for f in families) == 200
    assert [f["count"] for f in families] == [38, 37, 26, 22, 19, 14, 14, 11, 11, 8]
    assert all(sum(f["lift_counts"].values()) == f["count"] for f in families)
    expected_tags = set().union(*MECHANISMS.values())
    assert len(expected_tags) == sum(map(len, MECHANISMS.values())) == 10
    tasks = []
    for row in taxonomy:
        task_id = row["task_id"]
        metadata_path = ROOT / "benchmark/tasks" / task_id / "metadata.json"
        statement_path = metadata_path.parent / "TASK.md"
        sources.extend([metadata_path, statement_path])
        metadata = read_json(metadata_path)
        public_digest = hashlib.sha256(json.dumps(metadata["public_spec"], sort_keys=True,
            separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
        assert public_digest == freeze[task_id]["spec_hash"], task_id
        statement_digest = hashlib.sha256(statement_path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
        assert statement_digest == freeze[task_id]["generated_task_hash"], task_id
        original = set(filter(None, row["entanglement_types_original"].split(";")))
        assert original == set(metadata["entanglement"]["types"]), task_id
        normalized = set(filter(None, row["normalized_entanglement_types"].split(";")))
        assert normalized <= expected_tags
        lift = inventory[task_id]["historical_lift_type"]
        assert lift in LIFT_TYPES
        assert lift == lift_records[task_id]["lift_type"], task_id
        assert inventory[task_id]["historical_lift_label_status"] == lift_records[task_id]["lift_label_status"], task_id
        tasks.append({"task_id": task_id, "lift_type": lift,
            "lift_label_status": inventory[task_id]["historical_lift_label_status"],
            "normalized_mechanisms": sorted(normalized),
            "mechanisms": [name for name, tags in MECHANISMS.items() if normalized & tags],
            "historical_source_commit": row["source_commit"],
            "frozen_source_commit": freeze[task_id]["source_resolved_commit"],
            "source_identity_string_matches": row["source_commit"] == freeze[task_id]["source_resolved_commit"]})
    assert Counter(t["lift_type"] for t in tasks) == {"Direct": 56, "Adapted": 76, "Composite": 18}
    cells = []
    for lift in LIFT_TYPES:
        subset = [t for t in tasks if t["lift_type"] == lift]
        for mechanism in MECHANISMS:
            count = sum(mechanism in t["mechanisms"] for t in subset)
            cells.append({"lift_type": lift, "mechanism": mechanism,
                "count": count, "denominator": len(subset), "percent": 100 * count / len(subset)})
    assert [c["count"] for c in cells] == [52, 54, 22, 15, 69, 64, 37, 24, 18, 9, 12, 10]
    mechanisms_by_task = {t["task_id"]: t["mechanisms"] for t in tasks}
    for task in complete_tasks:
        task["mechanisms"] = mechanisms_by_task.get(task["task_id"])
    # Null/blank is deliberately distinct from an observed absence for the other 50.
    index_path = FIGURES_DIR / "data" / "figA_task_index.csv"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    columns = ["task_id", "feature_family", "lift_type", "source_repo_id",
               "source_snapshot_id", "common_comparison", "mechanism_coverage_available", *MECHANISMS]
    with index_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for task in complete_tasks:
            row = {k: task[k] for k in columns if k in task}
            row.update({m: int(m in task["mechanisms"]) if task["mechanisms"] is not None else ""
                        for m in MECHANISMS})
            writer.writerow(row)
    return export("figA_task_coverage", {"scope": "Functional families and lift types: full 200-task release; mechanism coverage: common 150-task comparison",
        "claim_scope": "Descriptive taxonomy coverage; author confirms full task review; no independent difficulty claim",
        "release_tasks": 200, "mechanism_tasks": 150,
        "panel_scopes": {"a": "Full release (n = 200)", "b": "Common comparison (n = 150)"},
        "mechanism_scope_reason": "The other 50 records are ledger-seeded and omit source-derived mechanisms. They are not pooled with the complete v2 taxonomy or counted as mechanism-negative.",
        "feature_families": families, "release_lift_counts": dict(lift_counts),
        "complete_tasks": complete_tasks,
        "author_review": read_json(ROOT / "docs/paper/writing/author_review_statement.json"),
        "lift_types": LIFT_TYPES, "mechanism_order": list(MECHANISMS),
        "mechanism_mapping": {k: sorted(v) for k, v in MECHANISMS.items()},
        "cells": cells, "tasks": tasks,
        "validation": {"task_identity_join": 200, "public_specs_match_freeze": 200,
            "task_statements_match_freeze": 200, "original_mechanism_labels_match_metadata": 200,
            "family_count_sum": 200, "lift_count_sum": 200,
            "mechanism_scope": 150, "missing_mechanism_rows_not_zero_filled": 50,
            "historical_source_identity_string_mismatches": sum(not t["source_identity_string_matches"] for t in tasks),
            "semantic_reaudit_by_this_plot_script": False}}, sources)


def functional_results():
    rows, groups, stats = load_results()
    stages = ("functional_pass", "missing_submission", "build_failure", "public_failure", "hidden_failure", "isolation_failure")
    outcomes = [{"backend": name, "assigned": 150,
                 "counts": [sum(r["first_failure_stage"] == s for r in groups[name]) for s in stages]}
                for name in BACKEND_ORDER]
    task_counts = Counter()
    for row in rows:
        task_counts[row["task_id"]] += flag(row, "functional_pass")
    bins = [{"passing_configurations": n, "task_count": sum(v == n for v in task_counts.values())} for n in range(7)]
    assert [b["task_count"] for b in bins] == [b["total"] for b in stats["spectrum6"]["bins"]]
    assert sum(b["task_count"] for b in bins) == 150
    assert sum(b["task_count"] * b["passing_configurations"] for b in bins) == sum(r["counts"][0] for r in outcomes) == 492
    assert all(sum(r["counts"]) == 150 for r in outcomes)
    return export("figB_functional_results", {"evaluated_tasks": 150, "configurations": 6,
        "first_stage_keys": stages, "first_outcomes": outcomes, "solve_frequency": bins,
        "task_outcomes": [{"task_id": t, "passing_configurations": n} for t, n in sorted(task_counts.items())]}, [SOURCE, STATS])


def footprint():
    _, groups, _ = load_results()
    reference = {r["task_id"]: r for r in groups["Pro"] if flag(r, "functional_pass")}
    comparisons = []

    def quantile(values, fraction):
        values = sorted(values)
        index = (len(values) - 1) * fraction
        lower = math.floor(index)
        upper = math.ceil(index)
        return values[lower] + (index - lower) * (values[upper] - values[lower])

    for backend in BACKEND_ORDER[1:]:
        other = {r["task_id"]: r for r in groups[backend] if flag(r, "functional_pass")}
        common = sorted(reference.keys() & other.keys())
        points = []
        for task in common:
            point = {"task_id": task}
            for metric, field in (("rres", "rres"), ("copy", "copied_fraction")):
                pro, compared = float(reference[task][field]), float(other[task][field])
                assert math.isfinite(pro) and math.isfinite(compared)
                assert min(pro, compared) > 0 if metric == "rres" else 0 <= min(pro, compared) <= max(pro, compared) <= 1
                point.update({f"pro_{metric}": pro, f"compared_{metric}": compared,
                              f"delta_{metric}": compared - pro})
            points.append(point)
        summaries = {}
        for metric in ("rres", "copy"):
            delta = [p[f"delta_{metric}"] for p in points]
            summaries[metric] = {"median": median(delta), "q1": quantile(delta, .25),
                "q3": quantile(delta, .75), "min": min(delta), "max": max(delta),
                "positive": sum(v > 0 for v in delta), "negative": sum(v < 0 for v in delta),
                "ties": sum(v == 0 for v in delta)}
            assert sum(summaries[metric][k] for k in ("positive", "negative", "ties")) == len(common)
        comparisons.append({"backend": backend, "common_passing_tasks": len(common),
                            "points": points, "summaries": summaries})
    assert [r["common_passing_tasks"] for r in comparisons] == [105, 97, 67, 63, 33]
    expected = {"rres": [(76, 22, 7), (10, 85, 2), (49, 18, 0), (31, 29, 3), (7, 25, 1)],
                "copy": [(47, 53, 5), (18, 76, 3), (17, 49, 1), (11, 50, 2), (3, 28, 2)]}
    for metric, directions in expected.items():
        assert [tuple(r["summaries"][metric][k] for k in ("positive", "negative", "ties"))
                for r in comparisons] == directions
    return export("figC_paired_footprint", {"reference_backend": "Pro",
        "reference_selection": "Most functional passes among the six evaluated configurations",
        "delta_definition": "Compared configuration minus Pro, computed within each task",
        "pairing_scope": "Each row uses that pair's common passing tasks; membership differs between rows",
        "comparisons": comparisons}, [SOURCE, STATS])
