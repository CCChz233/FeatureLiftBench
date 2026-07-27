#!/usr/bin/env python3
"""Build the preregistered 21-repository queue for replacing Curated-7."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "benchmark" / "selection" / "external150_replacement_20260727.json"
SNAPSHOT_SHA256 = "c40ccdde2a07d48c25c31a9d9d8fcbfe8c166987b1b43aa47e02b695a01c71f1"
SEED = "featureliftbench-external150-20260727-v1"

CANDIDATES = (
    ("filelock", "https://github.com/tox-dev/filelock", "Unlicense", "selected", "filesystem_resource", "resource_coupling"),
    ("decorator", "https://github.com/micheles/decorator", "BSD-2-Clause", "selected", "language_runtime", "reflection_signature_coupling"),
    ("itsdangerous", "https://github.com/pallets/itsdangerous", "BSD-3-Clause", "selected", "application_service", "serialization_crypto_coupling"),
    ("flask", "https://github.com/pallets/flask", "BSD-3-Clause", "selected", "application_service", "framework_coupling"),
    ("blinker", "https://github.com/pallets-eco/blinker", "MIT", "selected", "plugin_registry", "registry_state_coupling"),
    ("parse", "https://github.com/r1chardj0n3s/parse", "MIT", "selected", "parser", "parser_state_coupling"),
    ("python-decouple", "https://github.com/HBNetwork/python-decouple", "MIT", "selected", "configuration", "config_resource_coupling"),
    ("more-itertools", "https://github.com/more-itertools/more-itertools", "MIT", "backup", "data_processing", "iterator_state_coupling"),
    ("dill", "https://github.com/uqfoundation/dill", "BSD-3-Clause", "backup", "serialization", "serialization_runtime_coupling"),
    ("python-json-logger", "https://github.com/nhairs/python-json-logger", "BSD-2-Clause", "backup", "configuration", "config_environment_coupling"),
    ("cachecontrol", "https://github.com/psf/cachecontrol", "Apache-2.0", "backup", "application_service", "protocol_state_coupling"),
    ("watchdog", "https://github.com/gorakhargosh/watchdog", "Apache-2.0", "backup", "filesystem_resource", "resource_coupling"),
    ("structlog", "https://github.com/hynek/structlog", "MIT OR Apache-2.0", "backup", "observability", "processor_pipeline_coupling"),
    ("flask-cors", "https://github.com/corydolphin/flask-cors", "MIT", "backup", "application_service", "framework_coupling"),
    ("toolz", "https://github.com/pytoolz/toolz", "BSD-3-Clause", "backup", "data_processing", "functional_composition_coupling"),
    ("omegaconf", "https://github.com/omry/omegaconf", "BSD-3-Clause", "backup", "configuration", "config_resource_coupling"),
    ("dateparser", "https://github.com/scrapinghub/dateparser", "BSD-3-Clause", "backup", "parser", "parser_resource_coupling"),
    ("flask-login", "https://github.com/maxcountryman/flask-login", "MIT", "backup", "application_service", "framework_state_coupling"),
    ("jsonpickle", "https://github.com/jsonpickle/jsonpickle", "BSD-3-Clause", "backup", "serialization", "serialization_object_graph_coupling"),
    ("ciso8601", "https://github.com/closeio/ciso8601", "MIT", "excluded_native_extension", "parser", "native_extension_coupling"),
    ("wrapt", "https://github.com/GrahamDumpleton/wrapt", "BSD-2-Clause", "excluded_native_extension", "language_runtime", "native_extension_coupling"),
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    snapshot_bytes = args.snapshot.read_bytes()
    actual_sha = hashlib.sha256(snapshot_bytes).hexdigest()
    if actual_sha != SNAPSHOT_SHA256:
        raise SystemExit(f"ranking snapshot digest mismatch: {actual_sha}")
    snapshot = json.loads(snapshot_bytes)
    ranks = {
        str(row["project"]).lower(): (index, int(row["download_count"]))
        for index, row in enumerate(snapshot["rows"], 1)
    }

    seen: set[str] = set()
    rows = []
    for package, url, license_id, disposition, domain, entanglement in CANDIDATES:
        normalized = package.lower()
        rank, downloads = ranks[normalized]
        duplicate = normalized in seen
        seen.add(normalized)
        effective_disposition = "excluded_duplicate_candidate" if duplicate else disposition
        rows.append(
            {
                "package": package,
                "pypi_rank_30d": rank,
                "downloads_30d": downloads,
                "popularity_stratum": (
                    "popular" if rank <= 300 else "middle" if rank <= 1000 else "long_tail"
                ),
                "repository_url": url,
                "license": license_id,
                "domain": domain,
                "primary_entanglement": entanglement,
                "selection_key": hashlib.sha256(
                    f"{SEED}\0{normalized}".encode("utf-8")
                ).hexdigest(),
                "disposition": effective_disposition,
                "reason": (
                    "selected before model execution under rubric and portfolio constraints"
                    if effective_disposition == "selected"
                    else "eligible reserve after seven preregistered slots were filled"
                    if effective_disposition == "backup"
                    else "excluded before task construction because its core path requires a native extension"
                ),
            }
        )

    payload = {
        "schema_version": "featureliftbench.repository_selection.v1",
        "selection_id": "external150-replacement-20260727-v1",
        "selection_date": "2026-07-27",
        "model_results_consulted": False,
        "ranking_snapshot": {
            "url": "https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.min.json",
            "sha256": SNAPSHOT_SHA256,
            "last_update": snapshot.get("last_update"),
            "source": snapshot.get("source"),
            "row_count": len(snapshot["rows"]),
        },
        "hash_seed": SEED,
        "selection_protocol": {
            "candidate_rows": 21,
            "unique_candidate_repositories": 21,
            "selected_repositories": 7,
            "rubric": [
                "real reuse scenario",
                "non-trivial implementation closure",
                "offline deterministic evaluation",
                "complete public contract can be written",
                "hidden tests distinguish shallow implementations",
                "copy-all is materially larger than the target feature",
            ],
            "portfolio_constraints": {
                "max_tasks_per_repository": 1,
                "max_selected_per_domain": 2,
                "max_selected_per_primary_entanglement": 2,
                "required_coverage": [
                    "application_service",
                    "parser",
                    "configuration_or_resource",
                    "plugin_or_registry",
                ],
            },
        },
        "rows": rows,
        "summary": {
            "selected": sum(row["disposition"] == "selected" for row in rows),
            "eligible_backups": sum(row["disposition"] == "backup" for row in rows),
            "excluded": sum(row["disposition"].startswith("excluded") for row in rows),
        },
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("selection ledger is stale")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered, encoding="utf-8")
    print(
        f"selection ledger: {payload['summary']['selected']} selected, "
        f"{payload['summary']['eligible_backups']} backups"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
