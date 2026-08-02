from __future__ import annotations

from featurelifted import Collection, Context, UnexpectedExit, task


@task
def add(c, a: int, b: int) -> int:
    return a + b


def test_nested_collection() -> None:
    inner = Collection("tools")
    inner.add_task(add)
    outer = Collection()
    outer.add_collection(inner, "tools")
    assert outer["tools.add"](Context(), 2, 3) == 5


@task
def fail(c) -> None:
    raise UnexpectedExit("boom")


def test_task_exception_type() -> None:
    ns = Collection()
    ns.add_task(fail)
    try:
        ns["fail"](Context())
        assert False, "expected UnexpectedExit"
    except UnexpectedExit:
        pass


def test_no_upstream_import_surface() -> None:
    import re
    from pathlib import Path
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(
        rf"^\s*(?:from invoke\b|import invoke\b)",
        re.MULTILINE,
    )
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
