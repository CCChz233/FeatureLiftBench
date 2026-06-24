from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from featureliftbench.validate import validate_task


class ValidateTaskTests(unittest.TestCase):
    def test_valid_task(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task_dir = _make_task(Path(tmp), "sample_task")

            result = validate_task(task_dir)

            self.assertTrue(result.valid, result.errors)
            self.assertEqual(result.task_id, "sample_task")

    def test_task_id_must_match_directory_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task_dir = _make_task(Path(tmp), "sample_task", metadata_task_id="other_task")

            result = validate_task(task_dir)

            self.assertFalse(result.valid)
            self.assertIn("task_id must match directory name: other_task != sample_task", result.errors)

    def test_missing_required_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task_dir = _make_task(Path(tmp), "sample_task")
            (task_dir / "hidden_tests").rmdir()

            result = validate_task(task_dir)

            self.assertFalse(result.valid)
            self.assertIn("missing required path: hidden_tests", result.errors)

    def test_allowed_and_forbidden_dependencies_cannot_overlap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task_dir = _make_task(Path(tmp), "sample_task")
            metadata = _valid_metadata("sample_task")
            metadata["environment"]["allowed_dependencies"] = ["Sample_Pkg"]
            metadata["environment"]["forbidden_dependencies"] = ["sample-pkg"]
            (task_dir / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")

            result = validate_task(task_dir)

            self.assertFalse(result.valid)
            self.assertIn(
                "dependencies cannot be both allowed and forbidden: sample-pkg",
                result.errors,
            )


def _make_task(root: Path, dirname: str, metadata_task_id: str | None = None) -> Path:
    task_dir = root / dirname
    (task_dir / "repo").mkdir(parents=True)
    (task_dir / "public_tests").mkdir()
    (task_dir / "hidden_tests").mkdir()
    (task_dir / "evaluation").mkdir()
    (task_dir / "requirements.lock").write_text("", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("sample\n", encoding="utf-8")
    (task_dir / "evaluation" / "oracle_manifest.json").write_text("{}", encoding="utf-8")
    (task_dir / "metadata.json").write_text(
        json.dumps(_valid_metadata(metadata_task_id or dirname)),
        encoding="utf-8",
    )
    return task_dir


def _valid_metadata(task_id: str) -> dict:
    return {
        "task_id": task_id,
        "language": "python",
        "source": {
            "name": "sample",
            "url": "https://example.com/sample",
            "commit": "abc123",
            "license": "MIT",
        },
        "feature": {
            "name": "sample feature",
            "description": "A sample feature.",
            "source_entrypoints": ["sample.parse"],
            "included_behaviors": ["parse input"],
            "excluded_behaviors": [],
        },
        "entanglement": {
            "level": "low",
            "types": ["implicit_dependency_coupling"],
            "description": "Sample task with a small import boundary.",
            "signals": ["single source entrypoint", "no framework runtime"],
        },
        "output": {
            "package": "featurelifted",
            "import": "from featurelifted import parse",
            "callable": "featurelifted.parse",
            "signature": "parse(text)",
        },
        "environment": {
            "python": "3.11",
            "network": False,
            "timeout_seconds": 60,
            "dependency_lock": "requirements.lock",
            "allowed_dependencies": [],
            "forbidden_dependencies": ["sample"],
            "forbidden_imports": ["sample"],
        },
        "tests": {
            "public": "public_tests/",
            "hidden": "hidden_tests/",
            "command": "pytest",
        },
        "scoring_reference": {
            "copy_all_bytes": 100,
            "copy_all_loc": 10,
            "oracle_bytes": 50,
            "oracle_loc": 5,
            "oracle_dependency_count": 0,
        },
    }


if __name__ == "__main__":
    unittest.main()
