from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

from autosaddler.v2.core.domain import JsonValue, canonical_json, sha256_digest
from autosaddler.v2.core.ports import ScenarioComponents
from autosaddler.v2.harness.component_map import ComponentMapHarnessSpace
from autosaddler.v2.plugins.api import SCENARIO_PLUGIN_API_VERSION, ScenarioPlugin
from autosaddler.v2.providers.fake import PaidWorkLedger
from autosaddler.v2.storage.local import LocalRunStore

from .config import FeatureLiftSettings
from .evaluator import FeatureLiftOpenHandsEvaluator
from .evidence import FeatureLiftEvidenceBuilder
from .harness import COMPONENT_ORDER, PromptCandidateValidator
from .prompt_pack import FeatureLiftPromptPack


def build_featureliftbench_openhands_components(
    *,
    settings: Mapping[str, JsonValue],
    base_dir: Path,
    run_dir: Path,
    store: LocalRunStore,
    ledger: PaidWorkLedger,
) -> ScenarioComponents:
    del ledger
    resolved = FeatureLiftSettings.parse(settings, base_dir=base_dir)
    if tuple(resolved.baseline) != COMPONENT_ORDER:
        raise ValueError(f"FeatureLift prompt baseline keys must be ordered exactly as {COMPONENT_ORDER}")
    forbidden = [case.case_id for case in resolved.train_cases]
    for case in resolved.train_cases:
        metadata = json.loads(
            (resolved.benchmark_root / str(case.payload["task_relpath"]) / "metadata.json").read_text(encoding="utf-8")
        )
        source = metadata.get("source") if isinstance(metadata, dict) else None
        if isinstance(source, dict) and isinstance(source.get("name"), str):
            forbidden.append(source["name"])

    validator = PromptCandidateValidator(
        component_keys=COMPONENT_ORDER,
        max_component_chars=resolved.max_component_chars,
        max_total_chars=resolved.max_total_chars,
        forbidden_identifiers=forbidden,
    )
    harness = ComponentMapHarnessSpace(
        baseline=resolved.baseline,
        store_root=run_dir / "candidates",
        materialization_root=run_dir / "materialized",
        validator=validator,
    )
    prompt_pack = FeatureLiftPromptPack(
        store=store,
        component_keys=COMPONENT_ORDER,
        max_component_chars=resolved.max_component_chars,
        fixture_target_component=resolved.fixture_target_component,
        fixture_improved_text=resolved.fixture_improved_text,
    )
    return ScenarioComponents(
        name="featureliftbench_openhands",
        version="1",
        harness_space=harness,
        evaluator=FeatureLiftOpenHandsEvaluator(settings=resolved, harness_space=harness, run_dir=run_dir),
        evidence_builder=FeatureLiftEvidenceBuilder(store),
        prompt_pack=prompt_pack,
        train_cases=resolved.train_cases,
        development_cases=resolved.development_cases,
        required_capabilities=frozenset({"read_workspace", "edit_workspace", "load_skills"}),
        evaluation_repetitions=1,
        resolved_entities={
            "resolved/sources/featureliftbench.json": {
                "schema_version": "autosaddler-featureliftbench-source/v1",
                "benchmark_root": str(resolved.benchmark_root),
                "train_manifest_sha256": resolved.manifest_digests["train"],
                "development_manifest_sha256": resolved.manifest_digests["development"],
                "test": {"state": "external_one_shot", "opened": False},
            },
            "resolved/sources/prompt_harness.json": {
                "schema_version": "autosaddler-featureliftbench-harness/v1",
                "space": "component_map",
                "components": list(COMPONENT_ORDER),
                "baseline_sha256": sha256_digest(canonical_json(resolved.baseline)),
                "max_component_chars": resolved.max_component_chars,
                "max_total_chars": resolved.max_total_chars,
            },
            "resolved/sources/evaluator.json": {
                "schema_version": "autosaddler-featureliftbench-evaluator/v1",
                "runner_mode": resolved.runner_mode,
                "agent_profile": resolved.agent_profile,
                "eval_docker": resolved.eval_docker,
                "eval_docker_image": resolved.eval_docker_image,
                "timeout_seconds": resolved.timeout_seconds,
            },
            "resolved/prompts/featureliftbench.md": (
                "# FeatureLift prompt-only optimization\n\n"
                "Use training evidence only. Produce short, generic steering components.\n"
            ),
        },
    )


PLUGIN = ScenarioPlugin(
    name="featureliftbench_openhands",
    api_version=SCENARIO_PLUGIN_API_VERSION,
    factory=build_featureliftbench_openhands_components,
)
