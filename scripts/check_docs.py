#!/usr/bin/env python3
"""Validate links, status labels, and discoverability of project documentation."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC_PORTAL = "docs/README.md"
FROZEN_POLICY_DOCS = {
    "docs/BENCHMARK_DESIGN_PRINCIPLES.md",
    "docs/FULL_REPOSITORY_SOURCE_POLICY.md",
    "harness/featureliftbench/repo_graph/README.md",
}
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
FENCED_CODE_RE = re.compile(r"(?:```|~~~).*?(?:```|~~~)", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
STATUS_RE = re.compile(
    r"(?:Documentation status|Status):\s*([^*·\n]+)", re.IGNORECASE
)


def project_docs() -> list[str]:
    command = [
        "git",
        "ls-files",
        "--cached",
        "--others",
        "--exclude-standard",
        "*.md",
        "*.mdx",
        "*.rst",
    ]
    paths = subprocess.check_output(command, cwd=ROOT, text=True).splitlines()
    return sorted(
        {
            path
            for path in paths
            if not path.startswith("benchmark/") and (ROOT / path).is_file()
        }
    )


def markdown_links(path: Path) -> list[str]:
    if path.suffix.lower() not in {".md", ".mdx"}:
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    text = FENCED_CODE_RE.sub("", text)
    text = INLINE_CODE_RE.sub("", text)
    return LINK_RE.findall(text)


def local_target(source: Path, raw: str) -> Path | None:
    value = raw.strip().strip("<>")
    if not value or value.startswith(("#", "/", "mailto:")) or "://" in value:
        return None
    target = value.split("#", 1)[0]
    if not target:
        return None
    return (source.parent / target).resolve()


def status_for(relative: str, text: str) -> str | None:
    if relative in FROZEN_POLICY_DOCS:
        return "reference"
    if relative.startswith("reports/") or relative.startswith(
        "docs/reference/research_analysis/"
    ):
        return "generated/reference"
    match = STATUS_RE.search("\n".join(text.splitlines()[:12]))
    if not match:
        return None
    return match.group(1).strip().lower()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--warnings-as-errors",
        action="store_true",
        help="Fail on duplicate H1 titles in addition to structural errors.",
    )
    args = parser.parse_args()

    docs = project_docs()
    known = {(ROOT / relative).resolve(): relative for relative in docs}
    graph: dict[str, set[str]] = defaultdict(set)
    broken: list[tuple[str, str]] = []
    missing_status: list[str] = []
    archive_without_marker: list[str] = []
    titles: dict[str, str] = {}
    statuses: dict[str, str | None] = {}

    for relative in docs:
        path = ROOT / relative
        text = path.read_text(encoding="utf-8", errors="replace")
        status = status_for(relative, text)
        statuses[relative] = status
        # Repository-provided skills are mounted read-only in some Codex workspaces.
        if status is None and not relative.startswith(".agents/skills/"):
            missing_status.append(relative)
        if relative.startswith("docs/archive/") and status != "archived":
            archive_without_marker.append(relative)
        for line in text.splitlines():
            if line.startswith("# "):
                titles[relative] = line[2:].strip()
                break
        for raw in markdown_links(path):
            target = local_target(path, raw)
            if target is None:
                continue
            if not target.exists():
                broken.append((relative, raw))
            elif target in known:
                graph[relative].add(known[target])

    reachable = {DOC_PORTAL}
    queue: deque[tuple[str, int]] = deque([(DOC_PORTAL, 0)])
    while queue:
        current, depth = queue.popleft()
        if depth >= 2:
            continue
        for target in graph.get(current, set()):
            if target not in reachable:
                reachable.add(target)
                queue.append((target, depth + 1))
    unreachable_current = sorted(
        relative
        for relative, status in statuses.items()
        if relative.startswith("docs/")
        and status == "current"
        and relative not in reachable
    )

    duplicate_titles = {
        title: sorted(path for path, value in titles.items() if value == title)
        for title, count in Counter(titles.values()).items()
        if count > 1
    }

    print(f"project_docs: {len(docs)}")
    print(f"broken_relative_links: {len(broken)}")
    print(f"missing_project_status: {len(missing_status)}")
    print(f"archive_without_marker: {len(archive_without_marker)}")
    print(f"unreachable_current_docs: {len(unreachable_current)}")
    print(f"duplicate_h1_titles: {len(duplicate_titles)}")
    for source, target in broken:
        print(f"BROKEN {source} -> {target}")
    for relative in missing_status:
        print(f"NO_STATUS {relative}")
    for relative in archive_without_marker:
        print(f"ARCHIVE_STATUS {relative}")
    for relative in unreachable_current:
        print(f"UNREACHABLE {relative}")
    for title, paths in sorted(duplicate_titles.items()):
        print(f"DUPLICATE_TITLE {title}: {', '.join(paths)}")

    errors = broken or missing_status or archive_without_marker or unreachable_current
    if args.warnings_as_errors and duplicate_titles:
        errors = True
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
