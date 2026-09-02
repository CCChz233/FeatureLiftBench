#!/usr/bin/env python3
"""Exercise hardened evaluation with adversarial and compactness canaries."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "harness"
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

from featureliftbench.docker_eval import DEFAULT_EVAL_IMAGE, evaluate_submission_docker


POLICY_ID = "featureliftbench.full_repository_no_hint_main.v3"
SCHEMA_VERSION = "featureliftbench.v3_adversarial_canaries.v1"
TASK_ID = "itsdangerous__timed_serializer_core__001"
DEFAULT_OUTPUT = ROOT / "reports" / "audits" / "v3_adversarial_canaries.json"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--image", default=DEFAULT_EVAL_IMAGE)
    return parser.parse_args()


def _write_package(root: Path, source: str) -> Path:
    package = root / "featurelifted"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text(source, encoding="utf-8")
    return root


def _result_view(result: dict[str, Any]) -> dict[str, Any]:
    scores = result.get("scores") if isinstance(result.get("scores"), dict) else {}
    compactness = (
        result.get("compactness")
        if isinstance(result.get("compactness"), dict)
        else {}
    )
    isolation = (
        result.get("isolation") if isinstance(result.get("isolation"), dict) else {}
    )
    return {
        "status": result.get("status"),
        "build_pass": result.get("build_pass"),
        "public_tests_pass": result.get("public_tests_pass"),
        "hidden_tests_pass": result.get("hidden_tests_pass"),
        "isolation_pass": result.get("isolation_pass"),
        "functional_gate": scores.get("functional_gate"),
        "compactness_status": result.get("compactness_status"),
        "submitted_loc": compactness.get("submitted_loc"),
        "reference_loc": compactness.get("reference_loc"),
        "submitted_file_count": compactness.get("submitted_file_count"),
        "extraction_ratio_to_reference": compactness.get(
            "extraction_ratio_to_reference"
        ),
        "isolation": isolation,
        "errors": result.get("errors") or [],
    }


def _expectations() -> dict[str, dict[str, Any]]:
    return {
        "oracle": {"functional_gate": 1.0, "isolation_pass": True},
        "empty": {"functional_gate": 0.0},
        "stub": {"functional_gate": 0.0},
        "public_only": {
            "public_tests_pass": True,
            "hidden_tests_pass": False,
            "functional_gate": 0.0,
        },
        "upstream_import": {
            "isolation_pass": False,
            "functional_gate": 0.0,
        },
        "source_read": {
            "isolation_pass": False,
            "functional_gate": 0.0,
        },
        "subprocess": {
            "isolation_pass": False,
            "functional_gate": 0.0,
        },
        "dynamic_import": {
            "isolation_pass": False,
            "functional_gate": 0.0,
        },
        "socket": {
            "isolation_pass": False,
            "functional_gate": 0.0,
        },
        "dns": {
            "isolation_pass": False,
            "functional_gate": 0.0,
        },
        "http": {
            "isolation_pass": False,
            "functional_gate": 0.0,
        },
        "repository_scale_copy": {
            "functional_gate": 1.0,
            "isolation_pass": True,
        },
    }


def _matches(view: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(view.get(key) == value for key, value in expected.items())


def main() -> int:
    args = _parse_args()
    task_dir = ROOT / "benchmark" / "tasks" / TASK_ID
    oracle = ROOT / "benchmark" / "submissions" / TASK_ID / "oracle"
    oracle_source = (oracle / "featurelifted" / "__init__.py").read_text(
        encoding="utf-8"
    )
    public_only_source = oracle_source.replace(
        '        if max_age is not None and current - created > max_age:\n'
        '            raise SignatureExpired("signature age exceeded")\n',
        "",
    )
    source_read_source = (
        'FORBIDDEN_PROBE = "/workspace/tasks"\n'
        + oracle_source
    )
    bloat = "\n".join(
        f"def copied_repository_symbol_{index}(): return {index}"
        for index in range(3000)
    )
    cases: dict[str, tuple[str, str | None]] = {
        "oracle": ("oracle", None),
        "empty": ("empty", None),
        "stub": ("source", ""),
        "public_only": ("source", public_only_source),
        "upstream_import": (
            "source",
            "from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired\n",
        ),
        "source_read": ("source", source_read_source),
        "subprocess": (
            "source",
            "import subprocess\nsubprocess.run(['/bin/true'], check=True)\n",
        ),
        "dynamic_import": (
            "source",
            "import importlib\nimportlib.import_module('itsdangerous')\n",
        ),
        "socket": (
            "source",
            "import socket\nsocket.socket().connect(('127.0.0.1', 9))\n",
        ),
        "dns": (
            "source",
            "import socket\nsocket.getaddrinfo('example.com', 80)\n",
        ),
        "http": (
            "source",
            "from urllib.request import urlopen\nurlopen('http://example.com')\n",
        ),
        "repository_scale_copy": ("source", oracle_source + "\n" + bloat + "\n"),
    }

    records: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="flb-v3-canaries-") as tmp:
        root = Path(tmp)
        for name, (kind, source) in cases.items():
            submission = root / "submissions" / name
            if kind == "oracle":
                shutil.copytree(oracle, submission)
            elif kind == "empty":
                submission.mkdir(parents=True)
            else:
                submission.mkdir(parents=True)
                _write_package(submission, source or "")
            output = root / "outputs" / name
            result = evaluate_submission_docker(
                task_dir,
                submission,
                output,
                image=args.image,
            )
            view = _result_view(result)
            expected = _expectations()[name]
            records[name] = {
                "pass": _matches(view, expected),
                "expected": expected,
                "result": view,
            }
            print(
                f"{'PASS' if records[name]['pass'] else 'FAIL'} {name}",
                flush=True,
            )

    oracle_view = records["oracle"]["result"]
    copy_view = records["repository_scale_copy"]["result"]
    compactness_separation = (
        copy_view.get("functional_gate") == 1.0
        and copy_view.get("submitted_loc", 0) > oracle_view.get("submitted_loc", 0)
        and copy_view.get("extraction_ratio_to_reference", 0)
        > oracle_view.get("extraction_ratio_to_reference", 0)
    )
    gate_pass = all(record["pass"] for record in records.values()) and compactness_separation
    payload = {
        "schema_version": SCHEMA_VERSION,
        "policy_id": POLICY_ID,
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "task_id": TASK_ID,
        "gate_pass": gate_pass,
        "compactness_separation_pass": compactness_separation,
        "cases": records,
    }
    output_path = args.output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(
        f"Adversarial canary gate: {'PASS' if gate_pass else 'FAIL'}",
        flush=True,
    )
    return 0 if gate_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
