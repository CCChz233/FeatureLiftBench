"""Compatibility batch entry for the historical Fig. 1/2 schematics."""
from fig1_motivation import task
from fig2_construction import construction
from schematic_helpers import apply_paper_style

if __name__ == "__main__":
    apply_paper_style()
    task()
    construction()
