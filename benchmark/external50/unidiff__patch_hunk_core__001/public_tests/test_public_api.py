from __future__ import annotations

from featurelifted import LINE_TYPE_ADDED, LINE_TYPE_REMOVED, PatchSet, UnidiffParseError


SAMPLE = """--- a/file.py
+++ b/file.py
@@ -1,2 +1,3 @@
 def f():
-    return 1
+    return 2
+    # note
"""


def test_parse_patchset() -> None:
    ps = PatchSet(SAMPLE)
    assert len(ps) == 1
    assert ps[0].path == "file.py"
    assert len(ps[0]) == 1


def test_hunk_lines() -> None:
    hunk = PatchSet(SAMPLE)[0][0]
    added = [line.value for line in hunk if line.line_type == LINE_TYPE_ADDED]
    removed = [line.value for line in hunk if line.line_type == LINE_TYPE_REMOVED]
    assert any("return 2" in v for v in added)
    assert any("return 1" in v for v in removed)


def test_parse_error_short_hunk() -> None:
    bad = "--- a/x\n+++ b/x\n@@ -1,1 +1,1 @@\n+only\n"
    try:
        PatchSet(bad)
        assert False, "expected UnidiffParseError"
    except UnidiffParseError:
        pass
