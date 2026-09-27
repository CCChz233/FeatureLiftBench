"""Preview the figures in the latest supplied paper PDF (Fig. 3–8).

The default writes to figures/output/latest_pdf. Formal manuscript PDFs change
only with --publish. Fig. 6 is the author-selected PNG asset, exported as-is.
"""

import argparse
from importlib import import_module
from pathlib import Path


# Printed figure number -> title, source module, drawing function, output assets.
FIGURES = {
    "3": ("Benchmark composition", "fig03_benchmark_composition", "draw_coverage",
          ("fig03a_families.pdf", "fig03b_entanglement.pdf")),
    "4": ("Repository evidence", "fig04_repository_evidence", "draw_all",
          ("fig04a_ablation_pass_rate.pdf", "fig04b_ablation_paired_gain.pdf",
           "fig04c_dse_comparison.pdf")),
    "5": ("Evaluation outcomes", "fig05_failure_stages", "draw_functional",
          ("fig05_evaluation_outcomes.pdf",)),
    "6": ("Qualitative cases (PNG asset)", "fig06_qualitative_cases", "draw",
          ("fig06_qualitative_cases.png",)),
    "7": ("Post-pass execution", "fig07_post_pass_execution", "draw_execution_effort",
          ("fig07a_post_pass_tokens.pdf", "fig07b_post_pass_responses.pdf")),
    "8": ("Successful-artifact footprints", "fig08_artifact_footprint", "draw_matched",
          ("fig08a_rres.pdf", "fig08b_copy.pdf")),
}
ALIASES = {"coverage": "3", "ablation": "4", "functional": "5",
           "qualitative": "6", "execution-effort": "7", "footprint": "8"}
DEFAULT_PREVIEW = Path(__file__).resolve().parents[1] / "output" / "latest_pdf"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="Show PDF figure-to-source mapping.")
    parser.add_argument("--only", nargs="+", choices=(*FIGURES, *ALIASES),
                        default=list(FIGURES), help="Select figure numbers or compatibility aliases.")
    destination = parser.add_mutually_exclusive_group()
    destination.add_argument("--output-dir", type=Path, help="Preview directory.")
    destination.add_argument("--publish", action="store_true",
                             help="Copy generated PDFs to docs/paper/figures explicitly.")
    args = parser.parse_args()
    if args.list:
        for number, (title, module, _, assets) in FIGURES.items():
            print(f"Fig. {number}: {title}\n  {module}.py\n  {', '.join(assets)}")
        return
    from figure_common import render
    numbers = list(dict.fromkeys(ALIASES.get(name, name) for name in args.only))
    drawings = [getattr(import_module(FIGURES[n][1]), FIGURES[n][2]) for n in numbers]
    render(drawings, None if args.publish else args.output_dir or DEFAULT_PREVIEW,
           publish=args.publish)
    if not args.publish:
        output = (args.output_dir or DEFAULT_PREVIEW).expanduser().resolve()
        for number in numbers:
            for asset in FIGURES[number][3]:
                if not (output / asset).is_file():
                    raise FileNotFoundError(f"Fig. {number}: missing {output / asset}")


if __name__ == "__main__":
    main()
