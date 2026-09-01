#!/usr/bin/env python3
"""Build or verify the final, content-addressed Python-200-prime freeze.

The final freeze binds the pre-runtime candidate, the 200 x 3 Docker Oracle
revalidation, the compactness registry, and the exact linux/amd64 Agent and
evaluator images.  It is intentionally separate from the candidate builder so
the expensive Oracle gate does not need to be repeated unless frozen content or
runtime images actually change.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "harness"
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from build_python200_prime_candidate_freeze import verify_existing as verify_candidate  # noqa: E402
from featureliftbench.freeze import manifest_digest, sha256_file  # noqa: E402


SCHEMA_VERSION = "featureliftbench.python200_prime_benchmark_freeze.v1"
ORACLE_SCHEMA = "featureliftbench.python200_prime_oracle_revalidation.v1"
POLICY_ID = "featureliftbench.full_repository_no_hint_main.v3"
DEFAULT_CANDIDATE = (
    ROOT
    / "artifacts"
    / "research_analysis"
    / "python200_prime"
    / "current_candidate_freeze.json"
)
DEFAULT_ORACLE = ROOT / "reports" / "audits" / "python200_prime_oracle_revalidation" / "summary.json"
DEFAULT_COMPACTNESS = ROOT / "benchmark" / "references" / "python200_prime_compactness.json"
DEFAULT_OUTPUT = (
    ROOT
    / "artifacts"
    / "research_analysis"
    / "python200_prime"
    / "current_benchmark_freeze.json"
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--oracle", type=Path, default=DEFAULT_ORACLE)
    parser.add_argument("--compactness", type=Path, default=DEFAULT_COMPACTNESS)
    parser.add_argument("--agent-image", required=True)
    parser.add_argument("--evaluator-image", required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def _freeze_digest(payload: dict[str, Any]) -> str:
    normalized = dict(payload)
    normalized.pop("freeze_id", None)
    normalized.pop("generated_at", None)
    return manifest_digest(normalized)


def _run(command: list[str]) -> str:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return completed.stdout.strip()


def _last_matching_line(output: str, prefix: str) -> str:
    matches = [line.strip() for line in output.splitlines() if line.strip().startswith(prefix)]
    if not matches:
        raise ValueError(f"runtime version line missing ({prefix!r}): {output[-500:]}")
    return matches[-1]


def _inspect_image(tag: str, *, role: str, candidate_id: str) -> dict[str, Any]:
    raw = _run(["docker", "image", "inspect", tag])
    rows = json.loads(raw)
    if not isinstance(rows, list) or len(rows) != 1 or not isinstance(rows[0], dict):
        raise ValueError(f"unexpected docker inspect output for {tag}")
    image = rows[0]
    labels = ((image.get("Config") or {}).get("Labels") or {})
    if image.get("Os") != "linux" or image.get("Architecture") != "amd64":
        raise ValueError(f"{tag}: image must be linux/amd64")
    if labels.get("io.featureliftbench.benchmark-id") != candidate_id:
        raise ValueError(f"{tag}: benchmark-id label does not match candidate")
    if labels.get("io.featureliftbench.platform") != "linux/amd64":
        raise ValueError(f"{tag}: platform label is invalid")

    if role == "agent":
        output = _run(
            [
                "docker",
                "run",
                "--rm",
                "--platform",
                "linux/amd64",
                "-e",
                "OPENHANDS_SUPPRESS_BANNER=1",
                tag,
                "openhands",
                "--version",
            ]
        )
        versions = {"openhands": _last_matching_line(output, "OpenHands CLI ")}
        if versions["openhands"] != "OpenHands CLI 1.16.0":
            raise ValueError(f"{tag}: unexpected OpenHands version")
    elif role == "evaluator":
        python_output = _run(
            [
                "docker",
                "run",
                "--rm",
                "--platform",
                "linux/amd64",
                "--entrypoint",
                "python",
                tag,
                "--version",
            ]
        )
        go_output = _run(
            [
                "docker",
                "run",
                "--rm",
                "--platform",
                "linux/amd64",
                "--entrypoint",
                "go",
                tag,
                "version",
            ]
        )
        versions = {
            "python": _last_matching_line(python_output, "Python "),
            "go": _last_matching_line(go_output, "go version "),
        }
        if versions != {
            "python": "Python 3.11.14",
            "go": "go version go1.22.5 linux/amd64",
        }:
            raise ValueError(f"{tag}: unexpected evaluator runtime versions: {versions}")
    else:
        raise ValueError(f"unknown image role: {role}")

    return {
        "role": role,
        "tag": tag,
        "id": image.get("Id"),
        "repo_digests": sorted(image.get("RepoDigests") or []),
        "os": image.get("Os"),
        "architecture": image.get("Architecture"),
        "benchmark_id_label": labels.get("io.featureliftbench.benchmark-id"),
        "platform_label": labels.get("io.featureliftbench.platform"),
        "source_revision_label": labels.get("org.opencontainers.image.revision"),
        "runtime_versions": versions,
    }


def _validate_oracle(oracle: dict[str, Any], candidate_id: str) -> None:
    if oracle.get("schema_version") != ORACLE_SCHEMA:
        raise ValueError("unexpected Oracle summary schema")
    if oracle.get("policy_id") != POLICY_ID:
        raise ValueError("Oracle policy does not match Python-200-prime")
    if oracle.get("candidate_id") != candidate_id:
        raise ValueError("Oracle evidence belongs to a different candidate")
    if oracle.get("gate_pass") is not True:
        raise ValueError("Oracle gate did not pass")
    if oracle.get("failed_task_ids") or oracle.get("unstable_task_ids"):
        raise ValueError("Oracle evidence contains failed or unstable tasks")
    expected = {
        "expected_runs": 600,
        "passed_runs": 600,
        "repetitions": 3,
        "stable_tasks": 200,
        "task_count": 200,
    }
    if oracle.get("summary") != expected:
        raise ValueError(f"unexpected Oracle aggregate: {oracle.get('summary')}")
    runs = oracle.get("runs")
    if not isinstance(runs, list) or len(runs) != 600:
        raise ValueError("Oracle evidence must retain all 600 runs")
    repetitions: dict[str, list[int]] = defaultdict(list)
    fingerprints: dict[str, set[str]] = defaultdict(set)
    for run in runs:
        if not isinstance(run, dict) or run.get("passed") is not True:
            raise ValueError("Oracle evidence contains a non-passing run")
        task_id = str(run.get("task_id") or "")
        repetitions[task_id].append(int(run.get("repetition") or 0))
        fingerprints[task_id].add(str(run.get("fingerprint") or ""))
        result = run.get("result") or {}
        if (
            result.get("status") != "passed"
            or result.get("functional_gate") != 1.0
            or result.get("isolation_pass") is not True
        ):
            raise ValueError(f"{task_id}: Oracle result is not a functional isolated pass")
    if len(repetitions) != 200:
        raise ValueError("Oracle evidence does not cover 200 tasks")
    if any(sorted(values) != [1, 2, 3] for values in repetitions.values()):
        raise ValueError("each task must have exactly repetitions 1, 2, and 3")
    if any(len(values) != 1 for values in fingerprints.values()):
        raise ValueError("Oracle fingerprints are unstable across repetitions")


def build_payload(
    candidate_path: Path,
    oracle_path: Path,
    compactness_path: Path,
    agent_image: str,
    evaluator_image: str,
) -> dict[str, Any]:
    candidate = _load(candidate_path)
    verify_candidate(candidate)
    candidate_id = str(candidate.get("candidate_id") or "")
    oracle = _load(oracle_path)
    _validate_oracle(oracle, candidate_id)
    compactness = _load(compactness_path)
    if compactness.get("task_count") != 200 or len(compactness.get("tasks") or {}) != 200:
        raise ValueError("compactness registry does not cover 200 tasks")
    if set(compactness["tasks"]) != set(candidate.get("tasks") or {}):
        raise ValueError("compactness registry membership differs from candidate")

    images = {
        "agent": _inspect_image(agent_image, role="agent", candidate_id=candidate_id),
        "evaluator": _inspect_image(
            evaluator_image, role="evaluator", candidate_id=candidate_id
        ),
    }
    if (oracle.get("environment") or {}).get("id") != images["evaluator"]["id"]:
        raise ValueError("Oracle evidence was not produced by the pinned evaluator image")

    reference_counts = Counter(
        record.get("reference_kind") for record in (candidate.get("tasks") or {}).values()
    )
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "policy_id": POLICY_ID,
        "release_name": "Python-200-prime",
        "split": "python200_prime",
        "status": "frozen",
        "gate_pass": True,
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "promotion_blockers": [],
        "candidate_id": candidate_id,
        "suite_id": candidate.get("suite_id"),
        "task_count": 200,
        "strata": candidate.get("strata"),
        "task_set_sha256": candidate.get("task_set_sha256"),
        "primary_metric": candidate.get("primary_metric"),
        "functional_definition": candidate.get("functional_definition"),
        "agent_condition": candidate.get("agent_condition"),
        "evaluation_condition": candidate.get("evaluation_condition"),
        "candidate_manifest": {
            "path": _relative(candidate_path),
            "sha256": sha256_file(candidate_path),
        },
        "oracle_revalidation": {
            "path": _relative(oracle_path),
            "sha256": sha256_file(oracle_path),
            "schema_version": oracle.get("schema_version"),
            "summary": oracle.get("summary"),
            "failed_task_ids": [],
            "unstable_task_ids": [],
        },
        "compactness_registry": {
            "path": _relative(compactness_path),
            "sha256": sha256_file(compactness_path),
            "registry_id": compactness.get("registry_id"),
            "reference_composition": dict(sorted(reference_counts.items())),
        },
        "images": images,
        "gates": {
            "candidate_content_verified": True,
            "task_validation": 200,
            "source_mapping": 200,
            "hidden_contract_candidate_unresolved": 0,
            "oracle_runs": "600/600",
            "oracle_stable_tasks": "200/200",
            "docker_platform": "linux/amd64",
            "image_candidate_labels_match": True,
        },
        "tasks": candidate.get("tasks"),
    }
    payload["freeze_id"] = _freeze_digest(payload)
    return payload


def verify_existing(payload: dict[str, Any], *, agent_image: str, evaluator_image: str) -> None:
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unexpected final freeze schema")
    if payload.get("status") != "frozen" or payload.get("gate_pass") is not True:
        raise ValueError("final freeze must be a passing frozen release")
    if payload.get("task_count") != 200 or len(payload.get("tasks") or {}) != 200:
        raise ValueError("final freeze does not contain 200 tasks")
    if payload.get("freeze_id") != _freeze_digest(payload):
        raise ValueError("final freeze id is invalid")

    candidate_record = payload.get("candidate_manifest") or {}
    oracle_record = payload.get("oracle_revalidation") or {}
    compactness_record = payload.get("compactness_registry") or {}
    candidate_path = ROOT / str(candidate_record.get("path") or "")
    oracle_path = ROOT / str(oracle_record.get("path") or "")
    compactness_path = ROOT / str(compactness_record.get("path") or "")
    for path, record in (
        (candidate_path, candidate_record),
        (oracle_path, oracle_record),
        (compactness_path, compactness_record),
    ):
        if not path.is_file() or sha256_file(path) != record.get("sha256"):
            raise ValueError(f"frozen evidence drifted: {path}")

    candidate = _load(candidate_path)
    verify_candidate(candidate)
    if candidate.get("candidate_id") != payload.get("candidate_id"):
        raise ValueError("final freeze candidate id mismatch")
    if candidate.get("tasks") != payload.get("tasks"):
        raise ValueError("final freeze task records differ from candidate")
    oracle = _load(oracle_path)
    _validate_oracle(oracle, str(payload.get("candidate_id") or ""))
    compactness = _load(compactness_path)
    if compactness.get("registry_id") != compactness_record.get("registry_id"):
        raise ValueError("compactness registry id mismatch")

    current_images = {
        "agent": _inspect_image(
            agent_image, role="agent", candidate_id=str(payload.get("candidate_id") or "")
        ),
        "evaluator": _inspect_image(
            evaluator_image,
            role="evaluator",
            candidate_id=str(payload.get("candidate_id") or ""),
        ),
    }
    if current_images != payload.get("images"):
        raise ValueError("pinned Docker image identity or runtime versions drifted")
    if (oracle.get("environment") or {}).get("id") != current_images["evaluator"]["id"]:
        raise ValueError("Oracle evaluator image id mismatch")


def main() -> int:
    args = _parse_args()
    output = args.output.resolve()
    if args.check:
        payload = _load(output)
        verify_existing(
            payload, agent_image=args.agent_image, evaluator_image=args.evaluator_image
        )
        print(f"Verified Python-200-prime final freeze: {payload['freeze_id']}")
        return 0

    payload = build_payload(
        args.candidate.resolve(),
        args.oracle.resolve(),
        args.compactness.resolve(),
        args.agent_image,
        args.evaluator_image,
    )
    immutable = output.parent / "freezes" / f"{payload['freeze_id']}.json"
    immutable.parent.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    if immutable.exists():
        existing = _load(immutable)
        if _freeze_digest(existing) != payload["freeze_id"]:
            raise ValueError(f"immutable freeze collision: {immutable}")
        payload = existing
    else:
        immutable.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    shutil.copy2(immutable, output)
    verify_existing(payload, agent_image=args.agent_image, evaluator_image=args.evaluator_image)
    print(f"Wrote Python-200-prime final freeze: {payload['freeze_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
