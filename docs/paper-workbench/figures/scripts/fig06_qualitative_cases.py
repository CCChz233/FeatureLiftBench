"""Fig. 6: export the author-selected qualitative illustration for preview.

The manuscript uses a hand-edited PNG. The older Matplotlib vector diagram in
legacy/fig06_qualitative_mechanisms.py is a different composition and must not be used
as a renderer for the published figure.
"""

from pathlib import Path
from shutil import copy2

import paper_style
from figure_common import run_single


SOURCE = paper_style.MANUSCRIPT_FIGURES_DIR / "fig06_qualitative_cases.png"


def draw() -> None:
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)
    destination = Path(paper_style.OUTPUT_DIR) / SOURCE.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.resolve() != SOURCE.resolve():
        copy2(SOURCE, destination)
    print(destination)


if __name__ == "__main__":
    run_single(draw, __doc__)
