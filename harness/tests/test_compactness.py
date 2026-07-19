from __future__ import annotations

import json
from pathlib import Path

from harness.featureliftbench.compactness import analyze_submission_footprint


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_compactness_vector_does_not_invent_excess_copy_without_complete_gold(tmp_path: Path) -> None:
    task = tmp_path / "benchmark/tasks/demo"
    submission = tmp_path / "benchmark/submissions/demo/candidate"
    reference = tmp_path / "benchmark/submissions/demo/oracle"
    metadata = {
        "source": {"name": "upstream"},
        "environment": {"allowed_dependencies": []},
    }
    _write(task / "metadata.json", json.dumps(metadata))
    _write(task / "repo/upstream/core.py", "def f(x):\n    y = x + 1\n    return y\n")
    _write(submission / "featurelifted/core.py", "def f(x):\n    y = x + 1\n    return y\n")
    _write(reference / "featurelifted/core.py", "def f(x):\n    y = x + 1\n    return y\n")

    metrics = analyze_submission_footprint(
        task, submission, reference_path=reference, functional_pass=True
    )

    assert metrics["copied_loc"] == 3
    assert metrics["excess_copied_loc"] is None
    assert metrics["closure_gold_file_completeness"] == "unresolved"
    assert metrics["compactness_class"] == "copy_heavy_pass"


def test_compactness_detects_unapproved_external_import(tmp_path: Path) -> None:
    task = tmp_path / "benchmark/tasks/demo"
    submission = tmp_path / "benchmark/submissions/demo/candidate"
    reference = tmp_path / "benchmark/submissions/demo/oracle"
    metadata = {
        "source": {"name": "upstream"},
        "environment": {"allowed_dependencies": ["approved-lib"]},
    }
    _write(task / "metadata.json", json.dumps(metadata))
    _write(task / "repo/upstream/core.py", "VALUE = 1\n")
    _write(submission / "featurelifted/core.py", "import requests\nimport approved_lib\n")
    _write(reference / "featurelifted/core.py", "VALUE = 1\n")

    metrics = analyze_submission_footprint(
        task, submission, reference_path=reference, functional_pass=False
    )

    assert metrics["external_dependencies"] == ["approved_lib", "requests"]
    assert metrics["unapproved_external_dependencies"] == ["requests"]
    assert metrics["compactness_class"] == "non_functional"
