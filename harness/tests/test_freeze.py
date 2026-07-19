from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from featureliftbench.freeze import file_manifest
from featureliftbench.freeze import manifest_digest
from featureliftbench.freeze import verify_file_manifest


class FreezeTests(unittest.TestCase):
    def test_manifest_detects_content_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "TASK.md"
            path.write_text("v1\n", encoding="utf-8")
            expected = file_manifest([path], root=root)

            self.assertEqual(verify_file_manifest(expected, root=root), [])
            path.write_text("v2\n", encoding="utf-8")
            mismatches = verify_file_manifest(expected, root=root)

            self.assertEqual(len(mismatches), 1)
            self.assertEqual(mismatches[0]["path"], "TASK.md")

    def test_manifest_digest_ignores_generated_time_and_freeze_id(self) -> None:
        left = {"generated_at": "a", "freeze_id": "x", "files": {"a": "b"}}
        right = {"generated_at": "b", "freeze_id": "y", "files": {"a": "b"}}

        self.assertEqual(manifest_digest(left), manifest_digest(right))


if __name__ == "__main__":
    unittest.main()
