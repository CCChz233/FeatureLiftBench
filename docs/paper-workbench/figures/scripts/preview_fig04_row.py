"""Arrange the three Fig. 4 panel PDFs at their intended one-row paper size.

This is a layout preview; the manuscript may continue to include the panels
individually. Run draw_all.py --only 4 before using this script.
"""

import argparse
from pathlib import Path

import pymupdf


HERE = Path(__file__).resolve().parents[1]
PANELS = (
    "fig04a_ablation_pass_rate.pdf",
    "fig04b_ablation_paired_gain.pdf",
    "fig04c_dse_comparison.pdf",
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=HERE / "output/latest_pdf")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--gap-in", type=float, default=0.18)
    args = parser.parse_args()
    if args.gap_in < 0:
        parser.error("--gap-in must be nonnegative")

    sources = [pymupdf.open(args.input_dir / name) for name in PANELS]
    try:
        width, height = sources[0][0].rect.width, sources[0][0].rect.height
        if any(len(src) != 1 or abs(src[0].rect.width - width) > 0.1
               or abs(src[0].rect.height - height) > 0.1 for src in sources):
            raise ValueError("Fig. 4 panels must have equal one-page canvas sizes")
        gap = args.gap_in * 72
        row = pymupdf.open()
        page = row.new_page(width=3 * width + 2 * gap, height=height)
        for i, src in enumerate(sources):
            x = i * (width + gap)
            page.show_pdf_page(pymupdf.Rect(x, 0, x + width, height), src, 0)
        output = args.output_dir or args.input_dir
        output.mkdir(parents=True, exist_ok=True)
        pdf_path = output / "fig04_one_row_preview.pdf"
        png_path = output / "fig04_one_row_preview.png"
        row.save(pdf_path, garbage=4, deflate=True)
        page.get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False).save(png_path)
        row.close()
        print(pdf_path)
        print(png_path)
    finally:
        for src in sources:
            src.close()


if __name__ == "__main__":
    main()
