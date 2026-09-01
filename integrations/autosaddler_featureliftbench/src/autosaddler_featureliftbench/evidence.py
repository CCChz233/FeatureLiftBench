from __future__ import annotations

import json
from collections.abc import Mapping

from autosaddler.v2.core.domain import ArtifactRef, Evaluation, sha256_digest
from autosaddler.v2.storage.local import LocalRunStore

_MAX_PUBLIC_TASK_EXCERPT_CHARS = 2500


class FeatureLiftEvidenceBuilder:
    """Build a compact training-only packet without evaluator-private details."""

    def __init__(self, store: LocalRunStore) -> None:
        self.store = store

    def build(self, evaluation: Evaluation) -> ArtifactRef:
        if evaluation.split != "train":
            raise ValueError("FeatureLift optimization evidence may use training evaluations only")
        observations = []
        for observation in evaluation.observations:
            trace = None
            if observation.trace is not None:
                trace = self._verified_json(observation.trace)
            metadata = observation.metadata
            observations.append(
                {
                    "case_id": observation.case_id,
                    "disposition": observation.disposition,
                    "functional_score": observation.score,
                    "failure_stage": metadata.get("failure_stage"),
                    "steps": metadata.get("steps"),
                    "total_tokens": metadata.get("total_tokens"),
                    "usage_unverified": metadata.get("usage_unverified"),
                    "public_task_excerpt": _bounded_excerpt(metadata.get("public_task_excerpt")),
                    "trace_excerpt": trace,
                }
            )
        evidence_id = sha256_digest(evaluation.evaluation_id)
        return self.store.write_json(
            f"evidence/{evidence_id.removeprefix('sha256:')}/training_evidence.json",
            {
                "schema_version": "autosaddler-featureliftbench-evidence/v1",
                "evaluation_id": evaluation.evaluation_id,
                "candidate_id": evaluation.candidate_id,
                "split": "train",
                "private_evaluator_details_exposed": False,
                "observations": observations,
            },
            kind="hidden-safe-training-evidence",
        )

    def _verified_json(self, artifact: ArtifactRef) -> Mapping[str, object]:
        path = self.store.run_dir / artifact.uri
        payload = path.read_bytes()
        if artifact.sha256 is not None and sha256_digest(payload) != artifact.sha256:
            raise ValueError(f"FeatureLift evidence artifact digest drift: {artifact.uri}")
        value = json.loads(payload)
        if not isinstance(value, dict):
            raise TypeError(f"FeatureLift evidence artifact must be an object: {artifact.uri}")
        return value


def _bounded_excerpt(value: object) -> object:
    if not isinstance(value, str):
        return value
    if len(value) <= _MAX_PUBLIC_TASK_EXCERPT_CHARS:
        return value
    return value[:_MAX_PUBLIC_TASK_EXCERPT_CHARS] + "\n...[truncated]..."

