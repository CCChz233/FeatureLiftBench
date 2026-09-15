"""Shared export and CLI helpers; figure-specific drawing stays in fig*.py."""
from pathlib import Path
import argparse

from figure_data import prepare_matplotlib
prepare_matplotlib()
from matplotlib import pyplot as plt
import paper_style

BLUE = "#0072B2"
INK = "#202B33"
MUTED = "#56616A"
WIDTH = 7.2
_sync_paper_pdf = True


def publish_pdf(path):
    """Sync a rendered PDF only when writing the default paper output."""
    if path.suffix == '.pdf' and _sync_paper_pdf:
        (paper_style.FIGURES_DIR / path.name).write_bytes(path.read_bytes())


def finish(fig, name):
    """Write PDF/PNG and sync the manuscript PDF only for default output."""
    for path in paper_style.save_figure(fig, name):
        publish_pdf(path)
        print(path)
    plt.close(fig)


def render(drawings, output_dir=None):
    """Run selected drawings, optionally isolating both images and derived data."""
    import redraw_data

    global _sync_paper_pdf
    previous = paper_style.OUTPUT_DIR, redraw_data.FIGURES_DIR, _sync_paper_pdf
    try:
        if output_dir is not None:
            destination = Path(output_dir).expanduser().resolve()
            paper_style.OUTPUT_DIR = destination
            redraw_data.FIGURES_DIR = destination
            _sync_paper_pdf = False
        paper_style.apply_paper_style()
        for draw in drawings:
            draw()
    finally:
        paper_style.OUTPUT_DIR, redraw_data.FIGURES_DIR, _sync_paper_pdf = previous


def run_single(draw, description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--output-dir", type=Path,
                        help="Write images and data here without replacing the paper figures.")
    args = parser.parse_args()
    render([draw], args.output_dir)
