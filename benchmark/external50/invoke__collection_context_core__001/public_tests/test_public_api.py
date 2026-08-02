from __future__ import annotations

from featurelifted import Collection, Context, MockContext, task


@task
def hello(c, name: str = "world") -> str:
    return f"hi {name}"


def test_collection_task_call() -> None:
    ns = Collection()
    ns.add_task(hello)
    assert ns["hello"](Context(), name="Ada") == "hi Ada"


@task
def run_cmd(c) -> int:
    c.run("echo hi")
    return 1


def test_mock_context_run() -> None:
    ns = Collection()
    ns.add_task(run_cmd)
    ctx = MockContext(run=True)
    assert ns["run_cmd"](ctx) == 1
    assert ctx.run.called
