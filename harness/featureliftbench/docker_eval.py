"""Run evaluation inside a Docker image for reproducible baselines."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .evaluator import evaluate_submission
from .paths import REPO_ROOT

DEFAULT_EVAL_IMAGE = "featureliftbench-eval:latest"


def evaluate_submission_docker(
    task_dir: str | Path,
    submission_dir: str | Path,
    output_dir: str | Path,
    *,
    image: str = DEFAULT_EVAL_IMAGE,
    use_docker: bool = True,
) -> dict:
    """Evaluate a submission in Docker when ``use_docker`` is True."""

    if not use_docker:
        return evaluate_submission(task_dir, submission_dir, output_dir)

    task_path = Path(task_dir).resolve()
    submission_path = Path(submission_dir).resolve()
    output_path = Path(output_dir).resolve()
    output_path.mkdir(parents=True, exist_ok=True)
    harness_root = (REPO_ROOT / "harness").resolve()

    # Task validation requires the mount basename to match metadata task_id.
    container_task = f"/workspace/tasks/{task_path.name}"
    container_submission = "/workspace/submission"
    container_output = "/workspace/output"

    command = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{harness_root}:/workspace/harness:ro",
        "-v",
        f"{task_path}:{container_task}:ro",
        "-v",
        f"{submission_path}:{container_submission}:ro",
        "-v",
        f"{output_path}:{container_output}",
        image,
        "eval",
        container_task,
        container_submission,
        "--output",
        container_output,
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode not in {0, 1}:
        raise RuntimeError(
            "docker eval failed\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )

    result_path = output_path / "result.json"
    if not result_path.is_file():
        raise RuntimeError(
            "docker eval did not write result.json\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
    return json.loads(result_path.read_text(encoding="utf-8"))


def repo_root() -> Path:
    return REPO_ROOT
