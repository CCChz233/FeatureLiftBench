from __future__ import annotations

from pathlib import Path

from featurelifted import GitIgnoreSpec
from featurelifted import PathSpec


def test_match_tree_files_returns_relative_paths(tmp_path: Path) -> None:
    for relpath in [
        "app.py",
        "app.pyc",
        "build/out.txt",
        "build/keep.py",
        "src/module.pyc",
        "docs/en/build/index.html",
    ]:
        path = tmp_path / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x", encoding="utf-8")

    spec = PathSpec.from_lines(
        "gitignore",
        [
            "*.py[cod]",
            "build/",
            "docs/**/build",
            "!build/keep.py",
        ],
        backend="simple",
    )

    assert sorted(spec.match_tree_files(tmp_path)) == [
        "app.pyc",
        "build/out.txt",
        "docs/en/build/index.html",
        "src/module.pyc",
    ]


def test_absolute_paths_and_custom_separators_are_normalized() -> None:
    spec = GitIgnoreSpec.from_lines(
        [
            "/project/*.tmp",
            "logs/",
            "**/cache/*.bin",
        ],
        backend="simple",
    )

    assert spec.match_file("/project/output.tmp") is True
    assert spec.match_file("/other/project/output.tmp") is False
    assert spec.match_file("logs/app.log") is True
    assert spec.match_file(r"src\logs\app.log", separators={"\\"}) is True
    assert spec.match_file(r"pkg\cache\data.bin", separators={"\\"}) is True


def test_ordering_equality_and_negated_match_files() -> None:
    base = PathSpec.from_lines("gitignore", ["*.tmp"], backend="simple")
    extra = PathSpec.from_lines("gitignore", ["generated/"], backend="simple")
    combined = base + extra

    assert len(base) == 1
    assert len(combined) == 2
    assert combined == PathSpec.from_lines("gitignore", ["*.tmp", "generated/"], backend="simple")

    files = ["readme.md", "scratch.tmp", "generated/code.py", "src/app.py"]
    assert sorted(combined.match_files(files)) == ["generated/code.py", "scratch.tmp"]
    assert sorted(combined.match_files(files, negate=True)) == ["readme.md", "src/app.py"]


def test_gitignore_spec_reinclude_inside_ignored_directory() -> None:
    spec = GitIgnoreSpec.from_lines(
        [
            "build/",
            "!build/keep.txt",
            "build/*.log",
        ],
        backend="simple",
    )

    assert spec.check_file("build/drop.txt").include is True
    assert spec.check_file("build/keep.txt").include is False
    assert spec.check_file("build/error.log").include is True
