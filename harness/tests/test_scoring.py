from __future__ import annotations

import unittest

from featureliftbench.scoring import clamp
from featureliftbench.scoring import functional_gate
from featureliftbench.scoring import score_submission


class ScoringTests(unittest.TestCase):
    def test_functional_gate(self) -> None:
        self.assertEqual(
            functional_gate(build_pass=True, test_pass=True, original_import_pass=True),
            1.0,
        )
        self.assertEqual(
            functional_gate(build_pass=True, test_pass=False, original_import_pass=True),
            0.0,
        )

    def test_clamp(self) -> None:
        self.assertEqual(clamp(-1.0), 0.0)
        self.assertEqual(clamp(0.5), 0.5)
        self.assertEqual(clamp(2.0), 1.0)

    def test_score_submission_reports_extraction_ratio(self) -> None:
        scores = score_submission(
            metrics={
                "loc": 25,
                "source_loc": 100,
            },
            metadata=_metadata(),
            functional_gate_score=1.0,
        )

        self.assertEqual(scores["extraction_ratio"], 0.25)
        self.assertEqual(scores["final_score"], 0.75)

    def test_score_submission_clamps_final_score_when_output_exceeds_source(self) -> None:
        scores = score_submission(
            metrics={
                "loc": 150,
                "source_loc": 100,
            },
            metadata=_metadata(),
            functional_gate_score=1.0,
        )

        self.assertEqual(scores["extraction_ratio"], 1.5)
        self.assertEqual(scores["final_score"], 0.0)

    def test_score_submission_zeroes_when_functional_gate_fails(self) -> None:
        scores = score_submission(
            metrics={
                "loc": 25,
                "source_loc": 100,
            },
            metadata=_metadata(),
            functional_gate_score=0.0,
        )

        self.assertEqual(scores["extraction_ratio"], 0.25)
        self.assertEqual(scores["final_score"], 0.0)


def _metadata() -> dict:
    return {
        "scoring_reference": {
            "copy_all_bytes": 100,
            "copy_all_loc": 10,
            "oracle_bytes": 50,
            "oracle_loc": 5,
            "oracle_dependency_count": 0,
        }
    }


if __name__ == "__main__":
    unittest.main()
