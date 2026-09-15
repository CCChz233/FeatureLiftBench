"""Regression checks for task pairing, Holm family, and table columns, without plotting."""
import csv
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
import results_visuals
import results_tables


class ResultsEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with results_visuals.RESULTS.open(newline='',encoding='utf-8-sig') as f:
            cls.rows=list(csv.DictReader(f))
        cls.baseline=results_visuals.evidence()

    def changed_input(self,rows):
        # Keep the temporary fixture within the project for source-path bookkeeping.
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            file=Path(folder)/'results.csv'
            with file.open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=self.rows[0].keys());writer.writeheader();writer.writerows(rows)
            with patch.object(results_visuals,'RESULTS',file):return results_visuals.evidence()

    def test_input_order_does_not_change_pairing(self):
        changed=self.changed_input(self.rows[::-1])
        self.assertEqual(changed['matched'],self.baseline['matched'])
        self.assertEqual(changed['structure'],self.baseline['structure'])

    def test_duplicate_cell_is_rejected(self):
        with self.assertRaises(AssertionError):self.changed_input(self.rows[:-1]+[self.rows[0]])

    def test_conflicting_lift_type_is_rejected(self):
        rows=[dict(r) for r in self.rows];rows[0]['lift_type']='Composite' if rows[0]['lift_type']!='Composite' else 'Direct'
        with self.assertRaises(AssertionError):self.changed_input(rows)

    def test_pair_median_and_retained_ties(self):
        s=self.baseline['matched']['summary']['copy']
        self.assertAlmostEqual(s['median_delta'],-.213072)
        self.assertNotAlmostEqual(s['median_delta'],s['median_luna']-s['median_pro'])
        self.assertEqual((s['negative'],s['ties'],s['positive']),(76,3,18))
        self.assertLess(s['rank_biserial'],0)

    def test_holm_family_of_two_footprint_tests(self):
        rres=self.baseline['matched']['summary']['rres']
        copy=self.baseline['matched']['summary']['copy']
        self.assertLess(rres['wilcoxon_p'], copy['wilcoxon_p'])
        self.assertTrue(np.isclose(rres['holm_p_two_metrics'], 2*rres['wilcoxon_p']))
        self.assertTrue(np.isclose(copy['holm_p_two_metrics'], copy['wilcoxon_p']))
        self.assertEqual((rres['negative'], rres['ties'], rres['positive']), (85, 2, 10))

    def test_identity_scatter_limits_cover_all_points(self):
        points=self.baseline['matched']['points']
        rres=[p['pro_rres'] for p in points]+[p['luna_rres'] for p in points]
        copy=[p['pro_copy'] for p in points]+[p['luna_copy'] for p in points]
        self.assertEqual(len(points),97)
        self.assertGreater(min(rres),0.02)
        self.assertLess(max(rres),50)
        self.assertGreaterEqual(min(copy),0)
        self.assertLessEqual(max(copy),1)

    def test_table_columns_match_locked_spec(self):
        blocks,_=results_tables.build()
        ablation=blocks['paired-ablation']
        footprint=blocks['matched-footprint']
        self.assertIn(r'\shortstack{Full-\\only}', ablation)
        self.assertIn(r'\shortstack{Contract-\\only}', ablation)
        self.assertIn('[15.0, 55.0]', ablation)
        self.assertIn('35.0', ablation)
        self.assertNotIn('17 / 3', ablation)
        self.assertIn(' & 17 & 3 & ', ablation)
        self.assertNotIn(r'$n_{-}/n_{0}/n_{+}$', footprint)
        self.assertIn(r'\shortstack{Pro$>$\\Luna}', footprint)
        self.assertIn(' & 85 & 10 & 2 & ', footprint)
        self.assertIn(' & 76 & 18 & 3 & ', footprint)
        self.assertIn(r'$2.25\times10^{-14}$', footprint)
        self.assertIn(r'$1.18\times10^{-13}$', footprint)
        self.assertIn('two-test family of RRES and Copy', footprint)


if __name__=='__main__':unittest.main()
