from __future__ import annotations

import re
from pathlib import Path

from featurelifted import LINE_TYPE_CONTEXT, PatchSet, PatchedFile


MULTI = """--- a/a.py
+++ b/a.py
@@ -1,1 +1,1 @@
-old
+new
--- a/b.py
+++ b/b.py
@@ -1,1 +1,2 @@
 keep
+extra
"""


def test_multiple_files() -> None:
    ps = PatchSet(MULTI)
    assert len(ps) == 2
    assert {pf.path for pf in ps} == {"a.py", "b.py"}
    assert all(isinstance(pf, PatchedFile) for pf in ps)


def test_context_lines() -> None:
    sample = """--- a/file.py
+++ b/file.py
@@ -1,2 +1,3 @@
 def f():
-    return 1
+    return 2
+    # note
"""
    hunk = PatchSet(sample)[0][0]
    ctx = [line.value for line in hunk if line.line_type == LINE_TYPE_CONTEXT]
    assert any("def f" in v for v in ctx)


def test_added_removed_counts() -> None:
    ps = PatchSet(
        """--- a/file.py
+++ b/file.py
@@ -1,2 +1,3 @@
 def f():
-    return 1
+    return 2
+    # note
"""
    )
    pf = ps[0]
    assert pf.added > 0 and pf.removed > 0


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\s*(?:from unidiff\b|import unidiff\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
