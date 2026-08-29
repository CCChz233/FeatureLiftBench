from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from autosaddler.v2.core.domain import Case, JsonValue, Split, sha256_digest
from featureliftbench.ablation import AblationOptions
from featureliftbench.agent_runner import build_task_prompt, redact_task_metadata
from featureliftbench.task_render import render_agent_workspace_task
from featureliftbench.task_spec import SPEC_STATUS_COMPLIANT, get_spec_status

_SETTING_KEYS = {
    "agent_config",
    "agent_profile",
    "baseline",
    "benchmark_root",
    "development_manifest",
    "env_file",
    "eval_docker",
    "eval_docker_image",
    "fixture_improved_text",
    "fixture_target_component",
    "max_component_chars",
    "max_evidence_chars",
    "max_evidence_events",
    "max_infrastructure_retries",
    "max_total_chars",
    "runner_mode",
    "timeout_seconds",
    "train_manifest",
}


@dataclass(frozen=True, slots=True)
class FeatureLiftSettings:
    benchmark_root: Path
    train_manifest: Path
    development_manifest: Path
    agent_config: Path
    agent_profile: str
    env_file: Path
    eval_docker: bool
    eval_docker_image: str
    timeout_seconds: int
    max_infrastructure_retries: int
    max_component_chars: int
    max_total_chars: int
    max_evidence_events: int
    max_evidence_chars: int
    runner_mode: str
    baseline: Mapping[str, str]
    fixture_target_component: str
    fixture_improved_text: str
    train_cases: tuple[Case, ...]
    development_cases: tuple[Case, ...]
    train_repo_keys: tuple[str, ...]
    manifest_digests: Mapping[str, str]

    @classmethod
    def parse(cls, value: Mapping[str, JsonValue], *, base_dir: Path) -> FeatureLiftSettings:
        missing = sorted(_SETTING_KEYS - value.keys())
        extra = sorted(value.keys() - _SETTING_KEYS)
        if missing or extra:
            raise ValueError(f"Invalid FeatureLift scenario settings: missing={missing}, extra={extra}")

        benchmark_root = _directory(value["benchmark_root"], base_dir, "benchmark_root")
        train_manifest = _file(value["train_manifest"], base_dir, "train_manifest")
        development_manifest = _file(value["development_manifest"], base_dir, "development_manifest")
        agent_config = _file(value["agent_config"], base_dir, "agent_config")
        env_file = _file(value["env_file"], base_dir, "env_file")
        runner_mode = _choice(value["runner_mode"], {"fixture", "openhands"}, "runner_mode")
        baseline = _string_mapping(value["baseline"], "baseline")
        if not baseline:
            raise ValueError("scenario.settings.baseline must not be empty")

        max_component_chars = _positive_int(value["max_component_chars"], "max_component_chars")
        max_total_chars = _positive_int(value["max_total_chars"], "max_total_chars")
        if max_total_chars < max_component_chars:
            raise ValueError("max_total_chars must be at least max_component_chars")

        fixture_target = _string(value["fixture_target_component"], "fixture_target_component", allow_empty=True)
        fixture_improved = _string(value["fixture_improved_text"], "fixture_improved_text", allow_empty=True)
        if runner_mode == "fixture":
            if fixture_target not in baseline:
                raise ValueError("fixture_target_component must name a baseline component")
            if not fixture_improved:
                raise ValueError("fixture_improved_text is required in fixture mode")

        train_cases, train_repos = _load_manifest(train_manifest, benchmark_root, split="train")
        development_cases, development_repos = _load_manifest(
            development_manifest,
            benchmark_root,
            split="development",
        )
        overlap = sorted(set(train_repos) & set(development_repos))
        if overlap:
            raise ValueError(f"FeatureLift train/development repositories must be disjoint: {overlap}")

        return cls(
            benchmark_root=benchmark_root,
            train_manifest=train_manifest,
            development_manifest=development_manifest,
            agent_config=agent_config,
            agent_profile=_string(value["agent_profile"], "agent_profile"),
            env_file=env_file,
            eval_docker=_boolean(value["eval_docker"], "eval_docker"),
            eval_docker_image=_string(value["eval_docker_image"], "eval_docker_image"),
            timeout_seconds=_positive_int(value["timeout_seconds"], "timeout_seconds"),
            max_infrastructure_retries=_nonnegative_int(
                value["max_infrastructure_retries"],
                "max_infrastructure_retries",
            ),
            max_component_chars=max_component_chars,
            max_total_chars=max_total_chars,
            max_evidence_events=_positive_int(value["max_evidence_events"], "max_evidence_events"),
            max_evidence_chars=_positive_int(value["max_evidence_chars"], "max_evidence_chars"),
            runner_mode=runner_mode,
            baseline=baseline,
            fixture_target_component=fixture_target,
            fixture_improved_text=fixture_improved,
            train_cases=train_cases,
            development_cases=development_cases,
            train_repo_keys=tuple(sorted(train_repos)),
            manifest_digests={
                "train": sha256_digest(train_manifest.read_bytes()),
                "development": sha256_digest(development_manifest.read_bytes()),
            },
        )


def _load_manifest(path: Path, benchmark_root: Path, *, split: str) -> tuple[tuple[Case, ...], tuple[str, ...]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("schema_version") != "autosaddler-flb-split/v1":
        raise ValueError(f"Invalid FeatureLift split manifest schema: {path}")
    entries = raw.get("cases")
    if not isinstance(entries, list) or not entries:
        raise ValueError(f"FeatureLift split manifest must contain cases: {path}")
    cases: list[Case] = []
    repo_keys: list[str] = []
    seen: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or set(entry) != {"task_id"}:
            raise ValueError(f"Invalid case {index} in {path}; expected only task_id")
        task_id = entry.get("task_id")
        if not isinstance(task_id, str) or not task_id or "/" in task_id or ".." in task_id:
            raise ValueError(f"Invalid task_id at {path}:{index}")
        if task_id in seen:
            raise ValueError(f"Duplicate task_id in {path}: {task_id}")
        seen.add(task_id)
        task_dir = (benchmark_root / task_id).resolve()
        if task_dir.parent != benchmark_root or not task_dir.is_dir():
            raise FileNotFoundError(f"FeatureLift task directory is missing: {task_dir}")
        metadata_path = task_dir / "metadata.json"
        if not metadata_path.is_file():
            raise FileNotFoundError(f"FeatureLift task is incomplete: {task_dir}")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if not isinstance(metadata, dict) or metadata.get("task_id") != task_id:
            raise ValueError(f"FeatureLift metadata task_id mismatch: {metadata_path}")
        source = metadata.get("source")
        if not isinstance(source, dict):
            raise TypeError(f"FeatureLift metadata source is missing: {metadata_path}")
        repo_key = str(source.get("url") or source.get("name") or "").strip().lower()
        if not repo_key:
            raise ValueError(f"FeatureLift metadata source identity is missing: {metadata_path}")
        repo_keys.append(repo_key)
        task_text = public_task_text(task_dir, metadata=metadata)
        cases.append(
            Case(
                case_id=task_id,
                split=cast(Split, split),
                payload={
                    "task_relpath": task_id,
                    "task_sha256": sha256_digest(task_text),
                    "metadata_sha256": sha256_digest(metadata_path.read_bytes()),
                    "repo_key_sha256": sha256_digest(repo_key),
                },
            )
        )
    return tuple(cases), tuple(repo_keys)


def public_task_text(task_dir: Path, *, metadata: Mapping[str, object] | None = None) -> str:
    value = metadata
    if value is None:
        loaded = json.loads((task_dir / "metadata.json").read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise TypeError(f"FeatureLift metadata must be an object: {task_dir / 'metadata.json'}")
        value = loaded
    materialized = dict(value)
    if get_spec_status(materialized) == SPEC_STATUS_COMPLIANT:
        return render_agent_workspace_task(
            materialized,
            mount_public_tests=False,
            source_entrypoints=None,
        )
    redacted = redact_task_metadata(materialized, expose_source_hints=False)
    return build_task_prompt(redacted, ablation=AblationOptions())


def _resolve(value: JsonValue, base_dir: Path, name: str) -> Path:
    text = _string(value, name)
    path = Path(text)
    return (path if path.is_absolute() else base_dir / path).resolve()


def _directory(value: JsonValue, base_dir: Path, name: str) -> Path:
    path = _resolve(value, base_dir, name)
    if not path.is_dir():
        raise FileNotFoundError(f"scenario.settings.{name} is not a directory: {path}")
    return path


def _file(value: JsonValue, base_dir: Path, name: str) -> Path:
    path = _resolve(value, base_dir, name)
    if not path.is_file():
        raise FileNotFoundError(f"scenario.settings.{name} is not a file: {path}")
    return path


def _string(value: JsonValue, name: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise TypeError(f"scenario.settings.{name} must be a {'string' if allow_empty else 'non-empty string'}")
    return value.strip()


def _choice(value: JsonValue, choices: set[str], name: str) -> str:
    text = _string(value, name)
    if text not in choices:
        raise ValueError(f"scenario.settings.{name} must be one of {sorted(choices)}")
    return text


def _boolean(value: JsonValue, name: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"scenario.settings.{name} must be a boolean")
    return value


def _positive_int(value: JsonValue, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise TypeError(f"scenario.settings.{name} must be a positive integer")
    return value


def _nonnegative_int(value: JsonValue, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise TypeError(f"scenario.settings.{name} must be a nonnegative integer")
    return value


def _string_mapping(value: JsonValue, name: str) -> Mapping[str, str]:
    if not isinstance(value, Mapping) or any(
        not isinstance(key, str) or not key or not isinstance(item, str) for key, item in value.items()
    ):
        raise TypeError(f"scenario.settings.{name} must map non-empty strings to strings")
    return dict(cast(Mapping[str, str], value))
