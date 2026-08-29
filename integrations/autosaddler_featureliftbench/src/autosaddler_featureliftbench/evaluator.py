from __future__ import annotations

import asyncio
import json
import time
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Any

from autosaddler.v2.core.domain import (
    ArtifactRef,
    Candidate,
    Case,
    Cost,
    Evaluation,
    Observation,
    canonical_json,
    sha256_digest,
)
from autosaddler.v2.core.ports import EvaluationContext
from autosaddler.v2.harness.component_map import ComponentMapHarnessSpace
from autosaddler.v2.prompting.models import Usage
from featureliftbench.agent_adapters import AgentRunConfig
from featureliftbench.agent_config import load_agent_run_config
from featureliftbench.agent_runner import run_agent_on_task
from featureliftbench.suite_utils import functional_gate_value

from .config import FeatureLiftSettings, public_task_text
from .harness import load_components, render_prompt_appendix
from .trace import bounded_trace_excerpt

PROMPT_APPEND_ENV = "FEATURELIFTBENCH_OPENHANDS_PROMPT_APPEND_FILE"


class FeatureLiftOpenHandsEvaluator:
    def __init__(
        self,
        *,
        settings: FeatureLiftSettings,
        harness_space: ComponentMapHarnessSpace,
        run_dir: Path,
    ) -> None:
        self.settings = settings
        self.harness_space = harness_space
        self.run_dir = run_dir.resolve()
        self.fingerprint = sha256_digest(
            canonical_json(
                {
                    "adapter": "autosaddler-featureliftbench/evaluator-v1",
                    "runner_mode": settings.runner_mode,
                    "agent_profile": settings.agent_profile,
                    "eval_docker": settings.eval_docker,
                    "eval_docker_image": settings.eval_docker_image,
                    "timeout_seconds": settings.timeout_seconds,
                }
            )
        )

    async def evaluate(
        self,
        candidate: Candidate,
        cases: Sequence[Case],
        context: EvaluationContext,
    ) -> Evaluation:
        if not cases or any(case.split != context.split for case in cases):
            raise ValueError("FeatureLift evaluator cases must match EvaluationContext.split")
        materialized = self.harness_space.materialize(candidate, "evaluate")
        try:
            components = load_components(materialized.root)
        finally:
            materialized.release()
        context.artifact_dir.mkdir(parents=True, exist_ok=True)
        appendix_path = context.artifact_dir / "candidate_appendix.md"
        appendix_path.write_text(render_prompt_appendix(components), encoding="utf-8")

        observations: list[Observation] = []
        for case in cases:
            for repetition in range(context.repetitions):
                cached = context.attempt_sink.completed(
                    candidate_id=candidate.candidate_id,
                    case_id=case.case_id,
                    repetition=repetition,
                )
                if cached is not None:
                    observations.append(cached)
                    continue
                observation = await self._evaluate_case(
                    candidate=candidate,
                    case=case,
                    repetition=repetition,
                    context=context,
                    components=components,
                    appendix_path=appendix_path,
                )
                observations.append(observation)

        evaluation_id = sha256_digest(context.operation_id)
        return Evaluation(
            evaluation_id=evaluation_id,
            candidate_id=candidate.candidate_id,
            split=context.split,
            purpose=context.purpose,
            iteration=context.iteration,
            requested_case_ids=tuple(case.case_id for case in cases),
            observations=tuple(observations),
            artifact_dir=ArtifactRef(
                uri=self._relative(context.artifact_dir),
                kind="featurelift-evaluation-directory",
            ),
        )

    async def _evaluate_case(
        self,
        *,
        candidate: Candidate,
        case: Case,
        repetition: int,
        context: EvaluationContext,
        components: Mapping[str, str],
        appendix_path: Path,
    ) -> Observation:
        final: Observation | None = None
        for retry in range(self.settings.max_infrastructure_retries + 1):
            attempt_id, attempt_number = context.attempt_sink.start(
                candidate_id=candidate.candidate_id,
                case_id=case.case_id,
                repetition=repetition,
            )
            started = time.monotonic()
            attempt_dir = context.artifact_dir / case.case_id / f"rep-{repetition}" / f"attempt-{attempt_number}"
            attempt_dir.mkdir(parents=True, exist_ok=True)
            try:
                if self.settings.runner_mode == "fixture":
                    run = self._fixture_run(case, components)
                else:
                    run = await asyncio.to_thread(
                        self._run_openhands,
                        case,
                        attempt_dir,
                        appendix_path,
                    )
            except Exception as error:  # noqa: BLE001 - runner exceptions are infrastructure outcomes.
                run = {
                    "status": "execution_error",
                    "errors": [f"{type(error).__name__}: {error}"],
                    "agent": {"usage": {}},
                    "evaluation": {"status": "not-run", "scores": {}},
                }
            wall_seconds = time.monotonic() - started
            normalized = self._normalize(run, wall_seconds=wall_seconds)
            cost = Cost(
                rollouts=1,
                input_tokens=normalized["prompt_tokens"],
                output_tokens=normalized["completion_tokens"],
                wall_seconds=wall_seconds,
            )
            context.attempt_sink.observe_usage(
                attempt_id,
                Usage(
                    role="task_agent",
                    model=normalized["model"] or None,
                    input_tokens=normalized["prompt_tokens"],
                    output_tokens=normalized["completion_tokens"],
                    total_tokens=normalized["total_tokens"],
                    duration_seconds=wall_seconds,
                    status="failed" if normalized["infrastructure_error"] else "success",
                    error_type="FeatureLiftInfrastructureError" if normalized["infrastructure_error"] else None,
                    usage_incomplete=normalized["usage_unverified"],
                ),
            )
            if normalized["infrastructure_error"] and retry < self.settings.max_infrastructure_retries:
                context.attempt_sink.fail(attempt_id, "featurelift_infrastructure_error", cost)
                continue

            summary_ref = self._write_summary(attempt_dir, normalized)
            trace_ref = None
            if context.capture_traces and self.settings.runner_mode == "openhands":
                trace_ref = self._write_trace(attempt_dir)
            disposition = "execution_error" if normalized["infrastructure_error"] else (
                "success" if normalized["score"] == 1.0 else "task_failure"
            )
            score = None if disposition == "execution_error" else normalized["score"]
            final = Observation.create(
                candidate_id=candidate.candidate_id,
                case_id=case.case_id,
                split=case.split,
                repetition=repetition,
                disposition=disposition,
                score=score,
                evaluator_fingerprint=self.fingerprint,
                objectives={"functional_gate": score} if score is not None else {},
                output=summary_ref,
                trace=trace_ref,
                attempts=attempt_number,
                cost=cost,
                metadata={
                    "failure_stage": normalized["failure_stage"],
                    "steps": normalized["steps"],
                    "total_tokens": normalized["total_tokens"],
                    "usage_unverified": normalized["usage_unverified"],
                    "public_task_excerpt": self._public_task_excerpt(case),
                },
            )
            context.attempt_sink.complete(attempt_id, final, cost)
            break
        if final is None:
            raise RuntimeError(f"FeatureLift evaluation produced no observation for {case.case_id}")
        return final

    def _run_openhands(self, case: Case, attempt_dir: Path, appendix_path: Path) -> dict[str, Any]:
        task_dir = self.settings.benchmark_root / str(case.payload["task_relpath"])
        base = AgentRunConfig(
            agent="openhands-agent",
            timeout_seconds=self.settings.timeout_seconds,
            env={PROMPT_APPEND_ENV: str(appendix_path)},
        )
        loaded = load_agent_run_config(
            base_config=base,
            config_path=self.settings.agent_config,
            profile_name=self.settings.agent_profile,
            env_file=self.settings.env_file,
        )
        return run_agent_on_task(
            task_dir,
            attempt_dir,
            loaded.run_config,
            agent_config_summary=loaded.summary,
            eval_docker=self.settings.eval_docker,
            eval_docker_image=self.settings.eval_docker_image,
        )

    def _fixture_run(self, case: Case, components: Mapping[str, str]) -> dict[str, Any]:
        improved = (
            components.get(self.settings.fixture_target_component) == self.settings.fixture_improved_text
        )
        return {
            "task_id": case.case_id,
            "status": "passed" if improved else "failed",
            "agent": {
                "usage": {
                    "model": "fixture-task-agent",
                    "prompt_tokens": 100,
                    "completion_tokens": 20,
                    "total_tokens": 120,
                    "assistant_steps": 2,
                    "context_audit": {"usage_unverified": False},
                }
            },
            "evaluation": {
                "status": "passed" if improved else "failed",
                "scores": {"functional_gate": 1.0 if improved else 0.0},
                "docker_sandbox_error": False,
                "resource_limited": False,
            },
            "submission": {"exists": True},
            "errors": [],
        }

    def _normalize(self, run: Mapping[str, Any], *, wall_seconds: float) -> dict[str, Any]:
        evaluation = run.get("evaluation") if isinstance(run.get("evaluation"), Mapping) else {}
        agent = run.get("agent") if isinstance(run.get("agent"), Mapping) else {}
        usage = agent.get("usage") if isinstance(agent.get("usage"), Mapping) else {}
        score = functional_gate_value(dict(run))
        infrastructure_error = bool(
            run.get("status") == "execution_error"
            or evaluation.get("docker_sandbox_error")
            or evaluation.get("resource_limited")
        )
        if not infrastructure_error and score is None:
            # Missing submissions and ordinary Agent failures are valid task failures.
            score = 0.0
        return {
            "schema_version": "autosaddler-flb-observation-summary/v1",
            "score": score,
            "run_status": str(run.get("status") or "unknown"),
            "evaluation_status": str(evaluation.get("status") or "unknown"),
            "failure_stage": _failure_stage(run, score=score, infrastructure_error=infrastructure_error),
            "infrastructure_error": infrastructure_error,
            "submission_exists": bool(
                isinstance(run.get("submission"), Mapping) and run["submission"].get("exists")
            ),
            "model": str(usage.get("model") or ""),
            "steps": _integer(usage.get("assistant_steps")),
            "prompt_tokens": _integer(usage.get("prompt_tokens")),
            "completion_tokens": _integer(usage.get("completion_tokens")),
            "total_tokens": _integer(usage.get("total_tokens")),
            "usage_unverified": (
                bool(usage["context_audit"].get("usage_unverified", True))
                if isinstance(usage.get("context_audit"), Mapping)
                else True
            ),
            "wall_seconds": wall_seconds,
        }

    def _write_summary(self, attempt_dir: Path, normalized: Mapping[str, Any]) -> ArtifactRef:
        path = attempt_dir / "adapter_summary.json"
        text = json.dumps(normalized, indent=2, sort_keys=True) + "\n"
        path.write_text(text, encoding="utf-8")
        return ArtifactRef(
            uri=self._relative(path),
            kind="featurelift-observation-summary",
            sha256=sha256_digest(text.encode("utf-8")),
            bytes=len(text.encode("utf-8")),
        )

    def _write_trace(self, attempt_dir: Path) -> ArtifactRef | None:
        source = attempt_dir / "agent" / "openhands_events.jsonl"
        excerpt = bounded_trace_excerpt(
            source,
            max_events=self.settings.max_evidence_events,
            max_chars=self.settings.max_evidence_chars,
        )
        path = attempt_dir / "sanitized_trace.json"
        text = json.dumps(excerpt, indent=2, sort_keys=True) + "\n"
        path.write_text(text, encoding="utf-8")
        return ArtifactRef(
            uri=self._relative(path),
            kind="hidden-safe-trace-excerpt",
            sha256=sha256_digest(text.encode("utf-8")),
            bytes=len(text.encode("utf-8")),
        )

    def _public_task_excerpt(self, case: Case) -> str:
        task_dir = self.settings.benchmark_root / str(case.payload["task_relpath"])
        return public_task_text(task_dir)[:8_000]

    def _relative(self, path: Path) -> str:
        return PurePosixPath(path.resolve().relative_to(self.run_dir)).as_posix()


def _failure_stage(run: Mapping[str, Any], *, score: float | None, infrastructure_error: bool) -> str:
    if infrastructure_error:
        return "infrastructure"
    if score == 1.0:
        return "passed"
    submission = run.get("submission")
    if not isinstance(submission, Mapping) or not submission.get("exists"):
        return "submission"
    evaluation = run.get("evaluation")
    if isinstance(evaluation, Mapping) and not evaluation.get("build_pass", True):
        return "build"
    return "functional"


def _integer(value: Any) -> int:
    return int(value) if isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0 else 0
