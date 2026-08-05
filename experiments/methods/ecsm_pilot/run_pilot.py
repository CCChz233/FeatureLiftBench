#!/usr/bin/env python3
"""Plan or execute the preregistered ECSM pilot.

Dry-run is the default.  Pass ``--execute`` to launch cells.  Each condition
uses the same OpenHands profile, model, token/step limits, tools, evaluator, and
submission protocol; only the registered condition appendix/hints differ.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import os
import random
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
HARNESS_ROOT = REPO_ROOT / "harness"
if str(HARNESS_ROOT) not in sys.path:
    sys.path.insert(0, str(HARNESS_ROOT))

from featureliftbench.closure_gold import load_closure_gold  # noqa: E402
from pilot_freeze import verify_pilot_freeze  # noqa: E402

PROMPT_APPEND_ENV = "FEATURELIFTBENCH_OPENHANDS_PROMPT_APPEND_FILE"
TOKEN_LIMIT_ENV = "FEATURELIFTBENCH_OPENHANDS_TOTAL_TOKEN_LIMIT"
MAX_STEPS_ENV = "FEATURELIFTBENCH_OPENHANDS_MAX_STEPS"


@dataclass(frozen=True)
class Cell:
    arm_id: str
    arm_label: str
    strategy: str
    task_id: str
    task_dir: Path
    seed: int

    @property
    def key(self) -> str:
        return f"{self.arm_id}::{self.task_id}::seed-{self.seed}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path(__file__).with_name("pilot_manifest.yaml"),
    )
    parser.add_argument("--execute", action="store_true", help="execute instead of dry-run")
    parser.add_argument("--resume", action="store_true", help="skip cells with an existing run.json")
    parser.add_argument("--arm", action="append", default=[], help="limit to arm id; repeatable")
    parser.add_argument("--task-id", action="append", default=[], help="limit to task id; repeatable")
    parser.add_argument("--seed", action="append", type=int, default=[], help="limit to seed; repeatable")
    parser.add_argument("--limit", type=int, default=0, help="limit planned cells after blocking/order")
    parser.add_argument("--output-root", type=Path, default=None)
    parser.add_argument("--print-prompts", action="store_true")
    parser.add_argument("--stage", choices=["A", "B", "C"], help="run a preregistered stage")
    return parser.parse_args()


def load_manifest(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("pilot manifest must be a YAML mapping")
    return payload


def required_mapping(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"manifest.{key} must be a mapping")
    return value


def required_list(payload: dict[str, Any], key: str) -> list[Any]:
    value = payload.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"manifest.{key} must be a non-empty list")
    return value


def validate_manifest(manifest: dict[str, Any]) -> None:
    controls = required_mapping(manifest, "controls")
    arms = required_list(manifest, "arms")
    tasks = required_list(manifest, "tasks")
    required_controls = {
        "model",
        "agent",
        "agent_profile",
        "agent_config",
        "env_file",
        "eval_docker_image",
        "context_window_tokens",
        "reserved_output_tokens",
        "per_instance_total_token_budget",
        "max_steps",
        "timeout_seconds",
        "temperature",
        "tools",
        "test_permissions",
        "submission_protocol",
    }
    missing_controls = sorted(required_controls - set(controls))
    if missing_controls:
        raise ValueError(f"manifest.controls missing: {missing_controls}")
    if controls.get("test_permissions") != "public_tests_only":
        raise ValueError("pilot must keep agent test permissions at public_tests_only")
    if controls.get("submission_protocol") != "submission/featurelifted":
        raise ValueError("unsupported submission protocol")
    arm_ids = [str(arm.get("id") or "") for arm in arms if isinstance(arm, dict)]
    if len(arm_ids) != len(set(arm_ids)) or any(not value for value in arm_ids):
        raise ValueError("arm ids must be non-empty and unique")
    expected_arms = {
        "standard",
        "strong_prompt",
        "oracle_locate",
        "static_closure_hint",
        "oracle_closure",
        "copy_first_then_prune",
        "ecsm",
    }
    if set(arm_ids) != expected_arms:
        raise ValueError(f"manifest arms must be exactly {sorted(expected_arms)}")
    task_ids = [str(task.get("task_id") or "") for task in tasks if isinstance(task, dict)]
    if not 8 <= len(task_ids) <= 12:
        raise ValueError("pilot must contain 8-12 tasks")
    if len(task_ids) != len(set(task_ids)) or any(not value for value in task_ids):
        raise ValueError("task ids must be non-empty and unique")
    for task in tasks:
        if not isinstance(task, dict):
            raise ValueError("every task entry must be a mapping")
        task_dir = REPO_ROOT / str(task.get("task_dir") or "")
        if not (task_dir / "metadata.json").is_file():
            raise FileNotFoundError(f"task metadata missing: {task_dir}")
        closure = load_closure_gold(task_dir)
        if not closure.available:
            raise FileNotFoundError(f"closure hint source missing: {task_dir}: {closure.errors}")
    validate_taxonomy_selection(manifest, tasks)


def validate_taxonomy_selection(manifest: dict[str, Any], tasks: list[Any]) -> None:
    selection = manifest.get("task_selection")
    if not isinstance(selection, dict):
        return
    if selection.get("outcome_fields_used") is not False:
        raise ValueError("pilot taxonomy selection must declare outcome_fields_used: false")
    taxonomy_path = REPO_ROOT / str(selection.get("source") or "")
    if not taxonomy_path.is_file():
        raise FileNotFoundError(f"pilot taxonomy CSV missing: {taxonomy_path}")
    with taxonomy_path.open("r", encoding="utf-8", newline="") as handle:
        taxonomy = {row["task_id"]: row for row in csv.DictReader(handle)}
    expected_version = str(manifest.get("taxonomy_version") or "")
    policy = selection.get("policy") if isinstance(selection.get("policy"), dict) else {}
    roles: dict[str, int] = {}
    bins: set[str] = set()
    sources: set[str] = set()
    families: set[str] = set()
    parser_primary = 0
    curated_vibe = 0
    for task in tasks:
        task_id = str(task["task_id"])
        row = taxonomy.get(task_id)
        if row is None:
            raise ValueError(f"pilot task missing from taxonomy: {task_id}")
        if row.get("taxonomy_version") != expected_version:
            raise ValueError(f"pilot taxonomy version mismatch for {task_id}")
        if row.get("review_status") == "needs_review":
            raise ValueError(f"pilot task still needs taxonomy review: {task_id}")
        if policy.get("require_reference_closure_for_all") is True:
            reference_count = str(row.get("reference_file_count") or "")
            if reference_count == "NA" or not reference_count or int(reference_count) <= 0:
                raise ValueError(f"pilot task lacks measurable oracle reference closure: {task_id}")
        expected_fields = {
            "source_repo": row.get("source_repo"),
            "feature_family": row.get("feature_family_primary"),
            "feature_statefulness": row.get("feature_statefulness"),
            "closure_depth": row.get("static_file_closure_depth"),
        }
        for key, expected in expected_fields.items():
            if str(task.get(key)) != str(expected):
                raise ValueError(
                    f"pilot task {task_id} has stale {key}: {task.get(key)!r} != {expected!r}"
                )
        task_mechanisms = {str(value) for value in task.get("mechanisms") or []}
        row_mechanisms = {value for value in str(row.get("normalized_entanglement_types") or "").split(";") if value}
        if task_mechanisms != row_mechanisms:
            raise ValueError(f"pilot task {task_id} has stale mechanism labels")
        for role in task.get("selection_roles") or []:
            roles[str(role)] = roles.get(str(role), 0) + 1
        bins.add(str(task.get("closure_depth_bin") or ""))
        sources.add(str(row.get("source_group_id") or ""))
        families.add(str(row.get("feature_family_primary") or ""))
        parser_primary += row.get("feature_family_primary") == "parse_tokenize_decode"
        curated_vibe += row.get("repo_provenance") == "curated_vibe"

    if len(tasks) != int(policy.get("task_count") or len(tasks)):
        raise ValueError("pilot task count violates taxonomy selection policy")
    if len(sources) < int(policy.get("minimum_unique_source_repos") or 0):
        raise ValueError("pilot has too few unique source repositories")
    if len(families) < int(policy.get("minimum_feature_families") or 0):
        raise ValueError("pilot has too few feature families")
    role_thresholds = {
        "static_cross_file_closure": "minimum_static_cross_file_closure",
        "framework_lifecycle": "minimum_framework_lifecycle",
        "global_state_registry": "minimum_global_state_registry",
        "parser_stateful": "minimum_parser_stateful",
        "simple_control": "simple_controls",
    }
    for role, key in role_thresholds.items():
        if roles.get(role, 0) < int(policy.get(key) or 0):
            raise ValueError(f"pilot lacks required {role} coverage")
    config_resource = roles.get("config_environment", 0) + roles.get("resource_packaging", 0)
    if config_resource < int(policy.get("minimum_config_environment_or_resource") or 0):
        raise ValueError("pilot lacks config/environment/resource coverage")
    required_bins = {str(value) for value in policy.get("closure_depth_bins_required") or []}
    if not required_bins <= bins:
        raise ValueError(f"pilot lacks closure depth bins: {sorted(required_bins - bins)}")
    if parser_primary / len(tasks) > float(policy.get("maximum_parser_primary_share") or 1.0):
        raise ValueError("pilot parser-primary share exceeds policy")
    if curated_vibe > int(policy.get("maximum_curated_vibe_tasks") or len(tasks)):
        raise ValueError("pilot curated-vibe share exceeds policy")


def build_cells(manifest: dict[str, Any], args: argparse.Namespace) -> list[Cell]:
    controls = required_mapping(manifest, "controls")
    execution = required_mapping(manifest, "execution")
    seeds = args.seed or [int(value) for value in required_list(controls, "seeds")]
    arm_filter = set(args.arm)
    task_filter = set(args.task_id)
    arms = [arm for arm in required_list(manifest, "arms") if not arm_filter or arm["id"] in arm_filter]
    tasks = [
        task for task in required_list(manifest, "tasks") if not task_filter or task["task_id"] in task_filter
    ]
    if arm_filter - {arm["id"] for arm in arms}:
        raise ValueError(f"unknown --arm values: {sorted(arm_filter - {arm['id'] for arm in arms})}")
    if task_filter - {task["task_id"] for task in tasks}:
        raise ValueError(f"unknown --task-id values: {sorted(task_filter - {task['task_id'] for task in tasks})}")

    cells: list[Cell] = []
    base_seed = int(execution.get("random_seed") or 0)
    for task_index, task in enumerate(tasks):
        ordered_arms = list(arms)
        random.Random(base_seed + task_index).shuffle(ordered_arms)
        for seed in seeds:
            for arm in ordered_arms:
                cells.append(
                    Cell(
                        arm_id=str(arm["id"]),
                        arm_label=str(arm.get("label") or arm["id"]),
                        strategy=str(arm.get("strategy") or arm["id"]),
                        task_id=str(task["task_id"]),
                        task_dir=REPO_ROOT / str(task["task_dir"]),
                        seed=int(seed),
                    )
                )
    if args.stage:
        stages = required_mapping(manifest, "stages")
        stage = required_mapping(stages, args.stage)
        if args.stage in {"A", "B"}:
            stage_tasks = {str(value) for value in stage.get("task_ids") or []}
            stage_arms = {str(value) for value in stage.get("arm_ids") or []}
            cells = [cell for cell in cells if cell.task_id in stage_tasks and cell.arm_id in stage_arms]
        else:
            prior_keys: set[tuple[str, str]] = set()
            for prior_name in ("A", "B"):
                prior = required_mapping(stages, prior_name)
                prior_keys.update(
                    (str(task_id), str(arm_id))
                    for task_id in prior.get("task_ids") or []
                    for arm_id in prior.get("arm_ids") or []
                )
            cells = [cell for cell in cells if (cell.task_id, cell.arm_id) not in prior_keys]
        expected = int(stage.get("expected_cells") or 0)
        if not args.arm and not args.task_id and not args.seed and len(cells) != expected:
            raise ValueError(
                f"stage {args.stage} expected {expected} cells but selected {len(cells)}"
            )
    return cells[: args.limit] if args.limit > 0 else cells


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def source_entrypoints(metadata: dict[str, Any]) -> list[str]:
    feature = metadata.get("feature") if isinstance(metadata.get("feature"), dict) else {}
    values = feature.get("source_entrypoints")
    return [str(value) for value in values if isinstance(value, str)] if isinstance(values, list) else []


def python_files(repo_dir: Path) -> list[Path]:
    return [path for path in sorted(repo_dir.rglob("*.py")) if ".git" not in path.parts]


def module_variants(path: Path, repo_dir: Path) -> set[str]:
    rel = path.relative_to(repo_dir).with_suffix("")
    parts = list(rel.parts)
    variants: set[str] = set()
    starts = [0]
    for marker in ("src", "lib", "python"):
        if marker in parts:
            starts.append(parts.index(marker) + 1)
    for start in starts:
        selected = parts[start:]
        if selected and selected[-1] == "__init__":
            selected = selected[:-1]
        if selected:
            variants.add(".".join(selected))
    return variants


def build_module_index(repo_dir: Path) -> dict[str, Path]:
    index: dict[str, Path] = {}
    for path in python_files(repo_dir):
        for module in module_variants(path, repo_dir):
            index.setdefault(module, path)
    return index


def locate_entrypoint_files(task_dir: Path, metadata: dict[str, Any]) -> list[dict[str, str]]:
    repo_dir = task_dir / "repo"
    files = python_files(repo_dir)
    module_index = build_module_index(repo_dir)
    output: list[dict[str, str]] = []
    seen: set[Path] = set()
    for entrypoint in source_entrypoints(metadata):
        parts = entrypoint.split(".")
        candidates: list[Path] = []
        for end in range(len(parts), 0, -1):
            module = ".".join(parts[:end])
            if module in module_index:
                candidates.append(module_index[module])
                break
        symbol = parts[-1]
        definition = re.compile(rf"^\s*(?:async\s+def|def|class)\s+{re.escape(symbol)}\b|^\s*{re.escape(symbol)}\s*=", re.MULTILINE)
        for path in files:
            if len(candidates) >= 3:
                break
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if definition.search(text):
                candidates.append(path)
        for path in candidates:
            if path in seen:
                continue
            seen.add(path)
            output.append(
                {
                    "entrypoint": entrypoint,
                    "path": path.relative_to(task_dir).as_posix(),
                }
            )
    return output


def resolve_import_candidates(
    path: Path,
    repo_dir: Path,
    module_index: dict[str, Path],
) -> set[Path]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError):
        return set()
    current_modules = sorted(module_variants(path, repo_dir), key=len)
    current = current_modules[0] if current_modules else ""
    package_parts = current.split(".")[:-1]
    found: set[Path] = set()
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base_parts = package_parts[:]
            if node.level:
                trim = max(node.level - 1, 0)
                if trim:
                    base_parts = base_parts[:-trim]
            module = node.module or ""
            base = ".".join(base_parts + ([module] if module else []))
            names.append(base)
            names.extend(".".join(part for part in (base, alias.name) if part) for alias in node.names)
        for name in names:
            candidate = name
            while candidate:
                resolved = module_index.get(candidate)
                if resolved is not None:
                    found.add(resolved)
                    break
                candidate = candidate.rsplit(".", 1)[0] if "." in candidate else ""
    return found


def static_closure_candidates(task_dir: Path, located: list[dict[str, str]], depth: int = 2) -> list[str]:
    repo_dir = task_dir / "repo"
    module_index = build_module_index(repo_dir)
    frontier = {
        task_dir / item["path"]
        for item in located
        if (task_dir / item["path"]).is_file()
    }
    visited = set(frontier)
    for _ in range(depth):
        next_frontier: set[Path] = set()
        for path in frontier:
            next_frontier.update(resolve_import_candidates(path, repo_dir, module_index))
        next_frontier -= visited
        visited.update(next_frontier)
        frontier = next_frontier
        if not frontier:
            break
    return sorted(path.relative_to(task_dir).as_posix() for path in visited)


def oracle_manifest(task_dir: Path) -> dict[str, Any]:
    return load_json(task_dir / "evaluation" / "oracle_manifest.json")


def strong_prompt_text() -> str:
    return """### Condition: FeatureLift-specific strong prompt

Before editing, enumerate every required public symbol and behavior from TASK.md.
For every included behavior, identify source evidence, direct/transitive runtime
dependencies, resources, global/registry state, and an executable probe. Do not
equate public-test success with completion. Before submitting, run import/API,
public, isolation, and edge-behavior checks, then justify every retained file.
This is a checklist condition; it does not provide oracle files or hidden tests.
"""


def copy_first_prompt_text() -> str:
    return """### Condition: Copy-first then executable prune

Start with a conservative behavior-complete source closure around the located
entrypoints, including resources and runtime registration code. Make it importable
and pass the public/API probes before optimizing size. Then prune one candidate
file, symbol, adapter, or resource at a time in a reversible sandbox: delete,
rerun import + public + self-generated contract probes, keep the deletion only
when all probes remain green, otherwise restore it. Record each deletion decision
in `workspace/prune_evidence.jsonl`. Do not inspect hidden tests.
"""


def ecsm_prompt_text() -> str:
    return """### Condition: ECSM-Prompt executable closure-state protocol

Maintain `ecsm_state.json` at the workspace root. Update it after every source
read, static expansion, code change, probe, deletion, and restore. Its top-level
keys must be:

`included_symbols`, `included_files`, `unresolved_references`,
`transitive_dependency_candidates`, `runtime_global_state_dependencies`,
`observed_behavior_evidence`, `failed_probes`, `redundancy_estimates`,
`omission_risk_estimates`, `action_history`, `included_source_files`.

Choose only these controller actions and append each to `action_history`:
`locate`, `expand_dependency`, `replace_dependency`, `create_adapter`,
`execute_probe`, `prune_dependency`, `restore_dependency`, `finalize`.

Loop: locate entrypoints; expand the highest omission-risk unresolved item;
execute import/API/public and behavior probes; when probes pass, run reversible
counterfactual deletion tests on high-redundancy candidates; compare the expected
omission risk of stopping with the expected redundancy cost of continuing.

You may finalize only when: every TASK symbol maps to an included artifact and a
successful import probe; unresolved high-risk references are empty; public tests
pass; at least one non-public contract probe exists for every behavior family;
runtime/global-state candidates have been exercised or explicitly replaced;
every attempted prune has keep/restore evidence; isolation checks pass; and the
remaining omission-risk estimate is below 0.15. Public tests alone are never a
valid stopping condition. Do not inspect hidden tests.
"""


def condition_text(cell: Cell) -> tuple[str, dict[str, Any]]:
    metadata = load_json(cell.task_dir / "metadata.json")
    payload: dict[str, Any] = {
        "schema_version": "featureliftbench.pilot_condition.v1",
        "arm_id": cell.arm_id,
        "strategy": cell.strategy,
        "task_id": cell.task_id,
        "seed": cell.seed,
        "source": [],
    }
    if cell.strategy == "standard":
        return "", payload
    if cell.strategy == "strong_prompt":
        return strong_prompt_text(), payload
    if cell.strategy == "oracle_locate":
        located = locate_entrypoint_files(cell.task_dir, metadata)
        payload["source"] = ["metadata.feature.source_entrypoints", "public source snapshot"]
        payload["located"] = located
        text = (
            "### Condition: Oracle Locate\n\n"
            "The following locations are supplied by an oracle locator. They do not describe the transitive closure.\n\n"
            + "\n".join(f"- `{item['entrypoint']}` → `{item['path']}`" for item in located)
            + "\n\nRecover and validate the remaining closure yourself; do not inspect hidden tests.\n"
        )
        return text, payload
    if cell.strategy == "static_closure_hint":
        located = locate_entrypoint_files(cell.task_dir, metadata)
        candidates = static_closure_candidates(cell.task_dir, located)
        payload["source"] = ["metadata.feature.source_entrypoints", "AST imports depth<=2"]
        payload["located"] = located
        payload["static_candidates"] = candidates
        text = (
            "### Condition: Static Closure Hint\n\n"
            "A bounded AST import walk from automatically located entrypoints produced these candidates. "
            "The list can contain false positives and cannot observe registries, resources, or dynamic imports.\n\n"
            + "\n".join(f"- `{path}`" for path in candidates)
            + "\n\nVerify necessity and add missing runtime/dynamic dependencies yourself.\n"
        )
        return text, payload
    if cell.strategy == "oracle_closure":
        oracle = oracle_manifest(cell.task_dir)
        closure = load_closure_gold(cell.task_dir)
        files = sorted(closure.approved_artifact_values("file"))
        api = [str(value) for value in oracle.get("target_api") or []]
        payload["source"] = [str(closure.path.relative_to(cell.task_dir))] if closure.path else []
        payload["required_source_files"] = files
        payload["target_api"] = api
        payload["closure_annotation_status"] = closure.annotation_status
        payload["file_gold_completeness"] = closure.completeness_for("file")
        text = (
            "### Condition: Oracle Closure\n\n"
            "The benchmark oracle manifest supplies the intended source-file closure and target API. "
            "It supplies no hidden tests, assertions, or expected outputs.\n\n"
            "Required source files:\n"
            + "\n".join(f"- `{value}`" for value in files)
            + "\n\nTarget API:\n"
            + "\n".join(f"- `{value}`" for value in api)
            + "\n\nAdapt this closure into a standalone submission and validate behavior.\n"
        )
        return text, payload
    if cell.strategy == "copy_first_then_prune":
        return copy_first_prompt_text(), payload
    if cell.strategy == "ecsm":
        return ecsm_prompt_text(), payload
    raise ValueError(f"unknown strategy: {cell.strategy}")


def manifest_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def output_root(manifest: dict[str, Any], args: argparse.Namespace) -> Path:
    if args.output_root is not None:
        return args.output_root if args.output_root.is_absolute() else REPO_ROOT / args.output_root
    execution = required_mapping(manifest, "execution")
    root = REPO_ROOT / str(execution.get("output_root") or "experiments/methods/ecsm_pilot/runs")
    return root / str(manifest.get("pilot_id") or "ecsm-pilot")


def cell_dir(root: Path, cell: Cell) -> Path:
    return root / cell.arm_id / cell.task_id / f"seed-{cell.seed}"


def command_for(cell: Cell, cell_output: Path, controls: dict[str, Any]) -> list[str]:
    command = [
        sys.executable,
        "-m",
        "featureliftbench.cli",
        "run-agent",
        str(cell.task_dir),
        "--output",
        str(cell_output),
        "--agent",
        str(controls["agent"]),
        "--model",
        str(controls["model"]),
        "--agent-config",
        str(REPO_ROOT / str(controls["agent_config"])),
        "--agent-profile",
        str(controls["agent_profile"]),
        "--env-file",
        str(REPO_ROOT / str(controls["env_file"])),
        "--timeout-seconds",
        str(int(controls["timeout_seconds"])),
        "--eval-docker",
        "--eval-docker-image",
        str(controls["eval_docker_image"]),
        "--no-progress",
    ]
    if str(controls.get("agent_backend")) == "docker":
        command.append("--agent-docker")
    return command


def child_env(cell: Cell, condition_path: Path | None, controls: dict[str, Any]) -> dict[str, str]:
    env = os.environ.copy()
    current_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = os.pathsep.join(
        value for value in (str(REPO_ROOT / "harness"), current_pythonpath) if value
    )
    env[MAX_STEPS_ENV] = str(int(controls["max_steps"]))
    env[TOKEN_LIMIT_ENV] = str(int(controls["per_instance_total_token_budget"]))
    env["FEATURELIFTBENCH_CONTEXT_WINDOW_TOKENS"] = str(int(controls["context_window_tokens"]))
    env["FEATURELIFTBENCH_RESERVED_OUTPUT_TOKENS"] = str(int(controls["reserved_output_tokens"]))
    env["LLM_TEMPERATURE"] = str(controls["temperature"])
    env["FEATURELIFTBENCH_PILOT_ARM"] = cell.arm_id
    env["FEATURELIFTBENCH_PILOT_SEED"] = str(cell.seed)
    if condition_path is not None:
        env[PROMPT_APPEND_ENV] = str(condition_path)
    else:
        env.pop(PROMPT_APPEND_ENV, None)
    return env


def plan_payload(
    manifest_path: Path,
    manifest: dict[str, Any],
    root: Path,
    cells: list[Cell],
    controls: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "featureliftbench.ecsm_pilot_plan.v1",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "manifest": str(manifest_path.resolve()),
        "manifest_sha256": manifest_hash(manifest_path),
        "pilot_id": manifest.get("pilot_id"),
        "output_root": str(root),
        "controls": controls,
        "cell_count": len(cells),
        "cells": [
            {
                "key": cell.key,
                "arm_id": cell.arm_id,
                "task_id": cell.task_id,
                "seed": cell.seed,
                "output_dir": str(cell_dir(root, cell)),
            }
            for cell in cells
        ],
    }


def run_cell(
    cell: Cell,
    root: Path,
    controls: dict[str, Any],
    *,
    execute: bool,
    resume: bool,
    print_prompts: bool,
) -> dict[str, Any]:
    output = cell_dir(root, cell)
    run_path = output / "run.json"
    if resume and run_path.is_file():
        return {"key": cell.key, "status": "skipped_existing", "output_dir": str(output)}

    text, condition_payload = condition_text(cell)
    condition_path: Path | None = None
    if text:
        condition_path = output / "condition.md"
    command = command_for(cell, output, controls)
    record: dict[str, Any] = {
        "key": cell.key,
        "arm_id": cell.arm_id,
        "task_id": cell.task_id,
        "seed": cell.seed,
        "output_dir": str(output),
        "command": command,
        "condition_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "status": "planned",
    }
    if print_prompts and text:
        print(f"\n### {cell.key}\n{text}")
    if not execute:
        print("PLAN", cell.key, "->", output)
        return record

    output.mkdir(parents=True, exist_ok=True)
    if condition_path is not None:
        condition_path.write_text(text, encoding="utf-8")
    (output / "condition_payload.json").write_text(
        json.dumps(condition_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output / "runner_command.json").write_text(
        json.dumps({"command": command, "condition_file": str(condition_path or "")}, indent=2) + "\n",
        encoding="utf-8",
    )
    started = datetime.now(UTC)
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        env=child_env(cell, condition_path, controls),
        text=True,
        capture_output=True,
        check=False,
    )
    ended = datetime.now(UTC)
    (output / "runner_stdout.log").write_text(completed.stdout, encoding="utf-8")
    (output / "runner_stderr.log").write_text(completed.stderr, encoding="utf-8")
    record.update(
        {
            "status": "completed",
            "returncode": completed.returncode,
            "started_at": started.replace(microsecond=0).isoformat(),
            "ended_at": ended.replace(microsecond=0).isoformat(),
            "duration_seconds": round((ended - started).total_seconds(), 3),
            "run_json_present": run_path.is_file(),
        }
    )
    (output / "runner_result.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("DONE", cell.key, "returncode=", completed.returncode)
    return record


def main() -> int:
    args = parse_args()
    manifest_path = args.manifest.resolve()
    manifest = load_manifest(manifest_path)
    validate_manifest(manifest)
    controls = required_mapping(manifest, "controls")
    cells = build_cells(manifest, args)
    root = output_root(manifest, args).resolve()
    execution = required_mapping(manifest, "execution")
    freeze_path = REPO_ROOT / str(execution.get("freeze_manifest") or "")
    freeze: dict[str, Any] = {}
    if freeze_path.is_file():
        freeze = load_json(freeze_path)
        root = root / f"revision-{int(freeze.get('pilot_revision') or 0)}"
    if args.execute:
        if not freeze:
            raise RuntimeError(
                f"pilot execution requires a freeze manifest; create {freeze_path} first"
            )
        mismatches = verify_pilot_freeze(
            freeze, task_ids=sorted({cell.task_id for cell in cells})
        )
        if mismatches:
            raise RuntimeError(
                "pilot freeze verification failed: " + json.dumps(mismatches, sort_keys=True)
            )
        if args.stage == "C":
            decision_path = REPO_ROOT / str(execution.get("resource_decision") or "")
            decision = load_json(decision_path) if decision_path.is_file() else {}
            if decision.get("continue_remaining_36") is not True:
                raise RuntimeError(
                    "stage C refused: passing stage-B resource decision is required"
                )
    plan = plan_payload(manifest_path, manifest, root, cells, controls)
    plan["pilot_revision"] = freeze.get("pilot_revision")
    plan["freeze_id"] = freeze.get("freeze_id")
    plan["stage"] = args.stage or "all"

    if args.execute:
        root.mkdir(parents=True, exist_ok=True)
        (root / "pilot_plan.json").write_text(
            json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    else:
        print(json.dumps({key: plan[key] for key in ("pilot_id", "cell_count", "output_root")}, indent=2))

    records = []
    for cell in cells:
        if args.execute:
            # Re-check immediately before every cell. This catches a task,
            # evaluator, protocol, or image mutation that occurs after the
            # stage-level verification but before a later cell starts.
            cell_mismatches = verify_pilot_freeze(freeze, task_ids=[cell.task_id])
            if cell_mismatches:
                raise RuntimeError(
                    f"pilot freeze verification failed before {cell.key}: "
                    + json.dumps(cell_mismatches, sort_keys=True)
                )
        records.append(
            run_cell(
                cell,
                root,
                controls,
                execute=args.execute,
                resume=args.resume,
                print_prompts=args.print_prompts,
            )
        )
    if args.execute:
        (root / "pilot_execution.json").write_text(
            json.dumps(
                {
                    "schema_version": "featureliftbench.ecsm_pilot_execution.v1",
                    "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
                    "records": records,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        missing = [record["key"] for record in records if record.get("status") == "completed" and not record.get("run_json_present")]
        if missing:
            print(f"warning: {len(missing)} cells completed without run.json", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
