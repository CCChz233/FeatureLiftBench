"""Task directory validation."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .dependency_audit import validate_lock_allowed_consistency
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
    "evaluation/forbidden_modules.txt",
    "evaluation/allowed_modules.txt",
    "evaluation/oracle_manifest.json",
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
    try:
        metadata = load_metadata(root)
    except MetadataError as exc:
        errors.append(str(exc))

    task_id = ""
    language = "python"
    if metadata is not None:
        task_id = metadata.task_id
        raw_language = metadata.data.get("language")
        if isinstance(raw_language, str):
            language = raw_language

    for relative_path in _required_paths_for_language(language):
        path = root / relative_path
        if not path.exists():
            errors.append(f"missing required path: {relative_path}")

    if metadata is not None:
        errors.extend(validate_metadata_shape(metadata.data))

        if task_id and task_id != root.name:
            errors.append(f"task_id must match directory name: {task_id} != {root.name}")

        errors.extend(_validate_dependency_sets(metadata.data))
        errors.extend(_validate_lock_file_name(metadata.data, root))
        errors.extend(validate_lock_allowed_consistency(metadata.data, root))

    oracle_manifest = root / "evaluation" / "oracle_manifest.json"
    if oracle_manifest.exists():
        try:
            json.loads(oracle_manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON: evaluation/oracle_manifest.json: {exc}")
        except OSError as exc:
            errors.append(f"cannot read evaluation/oracle_manifest.json: {exc}")

    return ValidationResult(task_dir=root, task_id=task_id, errors=errors)


def _validate_dependency_sets(metadata: dict) -> list[str]:
    environment = metadata.get("environment")
    if not isinstance(environment, dict):
        return []

    if metadata.get("language") == "go":
        allowed = environment.get("allowed_modules", [])
        forbidden = environment.get("forbidden_modules", [])
    else:
        allowed = environment.get("allowed_dependencies", [])
        forbidden = environment.get("forbidden_dependencies", [])
    if not isinstance(allowed, list) or not isinstance(forbidden, list):
        return []

    normalizer = _normalize_go_module if metadata.get("language") == "go" else _normalize_distribution_name
    allowed_names = {normalizer(item) for item in allowed if isinstance(item, str)}
    forbidden_names = {normalizer(item) for item in forbidden if isinstance(item, str)}
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


def _normalize_go_module(name: str) -> str:
    return name.strip().rstrip("/").lower()


def _required_paths_for_language(language: str) -> tuple[str, ...]:
    if language == "go":
        return GO_REQUIRED_PATHS
    return PYTHON_REQUIRED_PATHS
