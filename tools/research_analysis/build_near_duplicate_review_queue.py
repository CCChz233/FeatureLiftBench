#!/usr/bin/env python3
"""Materialize the eight conservative near-duplicate candidate clusters for human review."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools/research_analysis"
sys.path.insert(0, str(TOOLS))

from build_benchmark_taxonomy import near_duplicate_candidates  # noqa: E402


TAXONOMY = ROOT / "artifacts/research_analysis/python150_task_taxonomy.csv"
OUTPUT = ROOT / "artifacts/research_analysis/v1_1/near_duplicate_review_queue.csv"
FIELDS = [
    "candidate_cluster", "task_ids", "warning_basis", "semantic_relation",
    "main_stat_policy", "reviewer", "reviewer_type", "review_status",
    "formal_human_review_pending", "evidence_paths",
]

AI_ASSISTED_DECISIONS = {
    "coveragepy / config_resolve_discover": (
        "shared utilities and configuration vocabulary, but four distinct entrypoint/behavior contracts",
        "retain tasks; source-group macro and clustered bootstrap; report cluster-collapsed sensitivity",
    ),
    "jinja2 / serialize_format_render": (
        "partially nested rendering variants: filter/test dispatch shares Environment/runtime with the broader compile/render task",
        "retain diagnostic tasks; cluster by source group; collapse to one task in independence sensitivity analysis",
    ),
    "pluggy / registry_plugin_dispatch": (
        "partially nested feature variants over the same hook engine; specs and wrapper tasks overlap the broad call-order task",
        "retain diagnostic tasks; cluster by source group; collapse to one task in independence sensitivity analysis",
    ),
    "pydantic / validate_normalize_construct": (
        "related validation concepts but different major APIs and non-equivalent behavior contracts",
        "retain tasks; cluster by source group and report version/API distinction",
    ),
    "pytest / registry_plugin_dispatch": (
        "same framework repository but fixture closure and marker registration are different subsystems",
        "retain tasks; cluster by source group in uncertainty estimates",
    ),
    "sqlparse / parse_tokenize_decode": (
        "hierarchical overlap: parse_split and token_tree are strict subsets of the broad parse_format surface",
        "retain task-level results; cluster by source group; use one representative in independence sensitivity analysis",
    ),
    "vibe_app / workflow_session_orchestration": (
        "coarse-family false positive: CSV transformation and session registry share no target entrypoints or behavior",
        "retain tasks; source-group macro still prevents curated-repository overweighting",
    ),
    "vibe_app / cache_retry_policy": (
        "coarse-family false positive: pricing calculation and generic rules evaluation are separate features",
        "retain tasks; source-group macro still prevents curated-repository overweighting",
    ),
}


def main() -> int:
    with TAXONOMY.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    candidates = near_duplicate_candidates(rows)
    output_rows = []
    for cluster, task_ids in candidates:
        evidence = []
        for task_id in task_ids:
            evidence.extend([
                f"benchmark/tasks/{task_id}/metadata.json",
                f"benchmark/tasks/{task_id}/TASK.md",
                f"benchmark/tasks/{task_id}/public_tests",
                f"benchmark/tasks/{task_id}/hidden_tests",
            ])
        semantic_relation, main_stat_policy = AI_ASSISTED_DECISIONS[cluster]
        output_rows.append({
            "candidate_cluster": cluster,
            "task_ids": ";".join(task_ids),
            "warning_basis": "same source_repo and feature_family_primary; Jaccard is warning-only",
            "semantic_relation": semantic_relation,
            "main_stat_policy": main_stat_policy,
            "reviewer": "codex_near_duplicate_semantic_pass",
            "reviewer_type": "ai_assisted_author",
            "review_status": "ai_assisted_adjudicated",
            "formal_human_review_pending": "true",
            "evidence_paths": ";".join(evidence),
        })
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"wrote {OUTPUT.relative_to(ROOT)}: candidate_clusters={len(output_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
