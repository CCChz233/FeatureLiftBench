"""Batch entry for paper figures. Edit the individual fig*.py files to draw.

The existing --only names and paper.py figures command remain supported.
Fig. 1/2 are image-edited assets; their historical renderers live in legacy/.
"""
import argparse
from pathlib import Path

from figure_common import render
from fig3_composition import draw_coverage
from fig4_functional_results import draw_functional
from fig5_source_ablation import draw_all as draw_source_ablation
from fig7_matched_footprint import draw_matched as draw_footprint
from fig4_structure import draw_structure

DRAWINGS = {
    "coverage": draw_coverage,
    "structure": draw_structure,
    "functional": draw_functional,
    "footprint": draw_footprint,
    "ablation": draw_source_ablation,
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="+", choices=tuple(DRAWINGS),
                        default=list(DRAWINGS))
    parser.add_argument("--output-dir", type=Path,
                        help="Write images and data here without replacing the paper figures.")
    args = parser.parse_args()
    render([DRAWINGS[name] for name in args.only], args.output_dir)


if __name__ == "__main__":
    main()
