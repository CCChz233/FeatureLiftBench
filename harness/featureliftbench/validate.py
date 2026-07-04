"""Task directory validation."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .metadata import MetadataError, load_metadata, validate_metadata_shape


@dataclass(frozen=True)
class ValidationResult:
    """Result of validating one task directory."""

    task_dir: Path
    task_id: str
    errors: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.errors


PYTHON_REQUIRED_PATHS = (
    "metadata.json",
    "requirements.lock",
    "repo",
    "public_tests",
    "hidden_tests",
    "evaluation",
    "evaluation/forbidden_imports.txt",
    "evaluation/oracle_manifest.json",
)

GO_REQUIRED_PATHS = (
    "metadata.json",
    "repo",
    "public_tests",
    "hidden_tests",
    "evaluation",
    "evaluation/forbidden_imports.txt",
    "environment",
    "environment/go.mod",
)


def validate_task(task_dir: str | Path) -> ValidationResult:
    """Validate a benchmark task directory."""

    root = Path(task_dir)
    errors: list[str] = []

    if not root.exists():
        return ValidationResult(task_dir=root, task_id="", errors=[f"task dir not found: {root}"])
    if not root.is_dir():
        return ValidationResult(task_dir=root, task_id="", errors=[f"task path is not a directory: {root}"])

    metadata = None
    language = "python"
    try:
        metadata = load_metadata(root)
        language = str(metadata.data.get("language", "python"))
    except MetadataError as exc:
        errors.append(str(exc))

    required_paths = GO_REQUIRED_PATHS if language == "go" else PYTHON_REQUIRED_PATHS
    for relative_path in required_paths:
        path = root / relative_path
        if not path.exists():
            errors.append(f"missing required path: {relative_path}")

    task_id = ""
    if metadata is not None:
        task_id = metadata.task_id
        errors.extend(validate_metadata_shape(metadata.data))

        if task_id and task_id != root.name:
            errors.append(f"task_id must match directory name: {task_id} != {root.name}")

        if language == "go":
            errors.extend(_validate_go_tests(root))
            errors.extend(_validate_go_environment(metadata.data, root))
        else:
            errors.extend(_validate_dependency_sets(metadata.data))
            errors.extend(_validate_lock_file_name(metadata.data, root))

    if language != "go":
        oracle_manifest = root / "evaluation" / "oracle_manifest.json"
        if oracle_manifest.exists():
            try:
                json.loads(oracle_manifest.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"invalid JSON: evaluation/oracle_manifest.json: {exc}")
            except OSError as exc:
                errors.append(f"cannot read evaluation/oracle_manifest.json: {exc}")

    return ValidationResult(task_dir=root, task_id=task_id, errors=errors)


def _validate_go_tests(root: Path) -> list[str]:
    errors: list[str] = []
    for label, rel in (("public", "public_tests"), ("hidden", "hidden_tests")):
        test_dir = root / rel
        if not test_dir.is_dir():
            continue
        go_tests = list(test_dir.glob("*_test.go"))
        if not go_tests:
            errors.append(f"{label} tests must include at least one *_test.go file under {rel}/")
    return errors


def _validate_go_environment(metadata: dict, task_dir: Path) -> list[str]:
    environment = metadata.get("environment")
    if not isinstance(environment, dict):
        return []

    go_mod = task_dir / "environment" / "go.mod"
    if go_mod.is_file():
        text = go_mod.read_text(encoding="utf-8")
        if "module " not in text:
            errors.append("environment/go.mod must declare a module path")

    cgo = environment.get("cgo_enabled", False)
    if cgo is True:
        errors.append("Go tasks must set environment.cgo_enabled to false for pilot track")

    return []


def _validate_dependency_sets(metadata: dict) -> list[str]:
    environment = metadata.get("environment")
    if not isinstance(environment, dict):
        return []

    allowed = environment.get("allowed_dependencies", [])
    forbidden = environment.get("forbidden_dependencies", [])
    if not isinstance(allowed, list) or not isinstance(forbidden, list):
        return []

    allowed_names = {_normalize_distribution_name(item) for item in allowed if isinstance(item, str)}
    forbidden_names = {_normalize_distribution_name(item) for item in forbidden if isinstance(item, str)}
    conflicts = sorted(allowed_names & forbidden_names)
    if not conflicts:
        return []

    return [f"dependencies cannot be both allowed and forbidden: {', '.join(conflicts)}"]


def _validate_lock_file_name(metadata: dict, task_dir: Path) -> list[str]:
    environment = metadata.get("environment")
    if not isinstance(environment, dict):
        return []

    lock_file = environment.get("dependency_lock")
    if not isinstance(lock_file, str):
        return []

    if Path(lock_file).is_absolute() or ".." in Path(lock_file).parts:
        return ["environment.dependency_lock must be a relative file inside the task directory"]

    if not (task_dir / lock_file).exists():
        return [f"dependency lock file not found: {lock_file}"]

    return []


def _normalize_distribution_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()
