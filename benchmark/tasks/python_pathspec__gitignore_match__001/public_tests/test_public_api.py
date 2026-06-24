from __future__ import annotations

import pytest

from featurelifted import GitIgnorePatternError
from featurelifted import GitIgnoreSpec
from featurelifted import PathSpec
from featurelifted import lookup_pattern


def test_pathspec_gitignore_matching_and_check_results() -> None:
    spec = PathSpec.from_lines(
        "gitignore",
        [
            "*.py[cod]",
            "build/",
            "!build/keep.py",
        ],
        backend="simple",
    )

    files = [
        "app.py",
        "app.pyc",
        "build/app.py",
        "build/keep.py",
        "src/build/app.py",
        "README.md",
    ]

    assert sorted(spec.match_files(files)) == [
        "app.pyc",
        "build/app.py",
        "src/build/app.py",
    ]

    matched = spec.check_file("app.pyc")
    assert matched.file == "app.pyc"
    assert matched.include is True
    assert matched.index == 0

    reincluded = spec.check_file("build/keep.py")
    assert reincluded.file == "build/keep.py"
    assert reincluded.include is False
    assert reincluded.index == 2

    assert spec.check_file("README.md").include is None


def test_gitignore_spec_root_directory_and_negation_patterns() -> None:
    spec = GitIgnoreSpec.from_lines(
        [
            "*.log",
            "cache/",
            "!cache/keep.log",
            "/root.txt",
            "docs/**/build",
        ],
        backend="simple",
    )

    files = [
        "error.log",
        "src/error.log",
        "cache/a.txt",
        "cache/keep.log",
        "src/cache/a.txt",
        "root.txt",
        "src/root.txt",
        "docs/build/index.html",
        "docs/en/build/index.html",
        "x/docs/en/build/index.html",
    ]

    assert sorted(spec.match_files(files)) == [
        "cache/a.txt",
        "docs/build/index.html",
        "docs/en/build/index.html",
        "error.log",
        "root.txt",
        "src/cache/a.txt",
        "src/error.log",
    ]
    assert spec.match_file("cache/keep.log") is False
    assert spec.match_file("src/root.txt") is False


def test_registered_pattern_lookup_and_invalid_patterns() -> None:
    assert lookup_pattern("gitignore").__name__ in {
        "GitIgnoreBasicPattern",
        "GitIgnoreSpecPattern",
    }

    with pytest.raises(GitIgnorePatternError):
        GitIgnoreSpec.from_lines(["!"], backend="simple")
