from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from featureliftbench.docker_eval import evaluate_submission_docker


class DockerEvalTests(unittest.TestCase):
    def test_evaluate_submission_docker_delegates_locally_when_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with mock.patch(
                "featureliftbench.docker_eval.evaluate_submission",
                return_value={"status": "passed"},
            ) as local_eval:
                result = evaluate_submission_docker(
                    root / "task",
                    root / "submission",
                    root / "output",
                    use_docker=False,
                )

            self.assertEqual(result["status"], "passed")
            local_eval.assert_called_once()

    def test_evaluate_submission_docker_runs_container(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_dir = root / "task"
            submission_dir = root / "submission"
            output_dir = root / "output"
            for path in (task_dir, submission_dir, output_dir):
                path.mkdir()
            (output_dir / "result.json").write_text(
                json.dumps({"status": "passed", "scores": {"final_score": 1.0}}),
                encoding="utf-8",
            )

            with mock.patch("featureliftbench.docker_eval.subprocess.run") as run_mock:
                run_mock.return_value = mock.Mock(returncode=0, stdout="", stderr="")
                result = evaluate_submission_docker(
                    task_dir,
                    submission_dir,
                    output_dir,
                    image="featureliftbench-eval:latest",
                    use_docker=True,
                )

            self.assertEqual(result["status"], "passed")
            command = run_mock.call_args.args[0]
            self.assertEqual(command[0], "docker")
            self.assertIn("featureliftbench-eval:latest", command)
            joined = " ".join(command)
            self.assertIn("/workspace/tasks/", joined)
            self.assertIn("/workspace/harness", joined)


if __name__ == "__main__":
    unittest.main()
