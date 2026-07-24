#!/usr/bin/env python3
"""Offline Operational Support vs baseline subgraph comparison (Phase 4 scaffold).

Compares, under the same token budget:
  - keyword search neighbors
  - call/import k-hop closure
  - operational support (Core/Support/Boundaries)

This is a retrieval-quality diagnostic, not an agent evaluation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from featureliftbench.repo_graph.builder import GraphBuilder
from featureliftbench.repo_graph.query import GraphQueryEngine
from featureliftbench.repo_graph.support import build_operational_support


def _estimate_tokens(payload: dict[str, Any]) -> int:
    rendered = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return max(1, (len(rendered) + 3) // 4)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--seed", action="append", dest="seeds", required=True)
    parser.add_argument("--budget-tokens", type=int, default=8_000)
    parser.add_argument("--max-depth", type=int, default=2)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    snapshot = GraphBuilder().build(args.repo)
    engine = GraphQueryEngine(snapshot)
    support = build_operational_support(
        engine,
        args.seeds,
        budget_tokens=args.budget_tokens,
        max_depth=max(args.max_depth, 4),
    )
    keyword = _keyword_baseline(engine, args.seeds, budget_tokens=args.budget_tokens)
    khop = _khop_baseline(
        engine,
        support.get("seeds") or args.seeds,
        budget_tokens=args.budget_tokens,
        max_depth=args.max_depth,
    )
    report = {
        "schema_version": "featureliftbench.repo_graph.support_compare.v1",
        "repo": str(args.repo),
        "budget_tokens": args.budget_tokens,
        "seeds_requested": args.seeds,
        "operational_support": {
            "status": support.get("status"),
            "seeds": support.get("seeds"),
            "core": len(support.get("core") or []),
            "support": len(support.get("support") or []),
            "boundaries": len(support.get("boundaries") or []),
            "covered_categories": support.get("covered_categories"),
            "used_tokens": (support.get("budget") or {}).get("used_tokens"),
        },
        "keyword_baseline": keyword,
        "khop_baseline": khop,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if support.get("status") == "ok" else 2


def _keyword_baseline(
    engine: GraphQueryEngine, seeds: list[str], *, budget_tokens: int
) -> dict[str, Any]:
    entities: list[str] = []
    for seed in seeds:
        for match in engine.search(seed, limit=30).get("matches", []):
            stable = match.get("stable_id")
            if isinstance(stable, str) and stable not in entities:
                entities.append(stable)
    selected: list[str] = []
    used = 0
    for entity in entities:
        cost = max(8, len(entity) // 2)
        if selected and used + cost > budget_tokens:
            break
        selected.append(entity)
        used += cost
    payload = {"entities": selected}
    return {
        "entity_count": len(selected),
        "used_tokens": _estimate_tokens(payload),
        "entities": selected[:40],
    }


def _khop_baseline(
    engine: GraphQueryEngine,
    seeds: list[str],
    *,
    budget_tokens: int,
    max_depth: int,
) -> dict[str, Any]:
    try:
        closure = engine.closure(seeds, max_nodes=120, include_candidates=False)
    except ValueError as exc:
        return {"error": str(exc), "entity_count": 0, "used_tokens": 0, "entities": []}
    entities = [node.get("stable_id") for node in closure.get("nodes", []) if node.get("stable_id")]
    # Approximate depth filter via paths from first seed when available.
    if seeds and max_depth >= 0:
        kept: list[str] = []
        root = seeds[0]
        for entity in entities:
            if entity == root:
                kept.append(entity)
                continue
            found = engine.paths(root, entity, max_depth=max_depth, max_paths=1)
            if found.get("found"):
                kept.append(entity)
        entities = kept or entities
    selected: list[str] = []
    used = 0
    for entity in entities:
        cost = max(8, len(str(entity)) // 2)
        if selected and used + cost > budget_tokens:
            break
        selected.append(str(entity))
        used += cost
    payload = {"entities": selected}
    return {
        "entity_count": len(selected),
        "used_tokens": _estimate_tokens(payload),
        "entities": selected[:40],
        "truncated": bool(closure.get("truncated")),
    }


if __name__ == "__main__":
    raise SystemExit(main())
