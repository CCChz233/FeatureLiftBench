from __future__ import annotations

import tempfile
from pathlib import Path

from featurelifted import LocalTarget, Task, build


def test_local_target_complete_and_build() -> None:
    with tempfile.TemporaryDirectory() as directory:
        target = LocalTarget(str(Path(directory) / "result.txt"))

        class WriteResult(Task):
            def output(self):
                return target

            def run(self) -> None:
                with self.output().open("w") as stream:
                    stream.write("done")

        task = WriteResult()
        assert not task.complete()
        assert build([task], local_scheduler=True, workers=1)
        assert task.complete()
        with target.open("r") as stream:
            assert stream.read() == "done"


def test_dependency_runs_first() -> None:
    with tempfile.TemporaryDirectory() as directory:
        events: list[str] = []
        dependency_target = LocalTarget(str(Path(directory) / "dependency.txt"))
        root_target = LocalTarget(str(Path(directory) / "root.txt"))

        class Dependency(Task):
            def output(self):
                return dependency_target

            def run(self) -> None:
                events.append("dependency")
                with self.output().open("w") as stream:
                    stream.write("ready")

        dependency = Dependency()

        class Root(Task):
            def requires(self):
                return dependency

            def output(self):
                return root_target

            def run(self) -> None:
                events.append("root")
                with self.output().open("w") as stream:
                    stream.write("joined")

        assert build([Root()], local_scheduler=True, workers=1)
        assert events == ["dependency", "root"]
