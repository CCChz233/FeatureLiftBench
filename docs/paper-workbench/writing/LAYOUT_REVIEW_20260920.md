# Float-layout review — 2026-09-20

Reviewed all 22 manuscript pages as rendered contact sheets. No changes to prose, figure content, table values, image widths, font sizes, or page geometry.

Changes:
- Allow floats at their source location as well as page edges (`htbp`); set moderate float fractions and spacing.
- Move the construction overview next to its first discussion (Fig. 2: page 6 → 5).
- Place the main comparison table after the Results overview (Table 1: page 11 → 10), separating it from Table 2 on page 11.
- Keep the source-exposure figure and table together on page 13, separated by their interpretation.
- Keep Fig. 6 on page 14, after the sample/theme introduction.
- Distribute Fig. 7 / Table 4 / Fig. 8 over pages 15 / 16 / 17. Introduce RQ5 before Fig. 8, and prevent its figure from drifting past the Discussion boundary.
- Synchronize generated-table placement defaults so table regeneration retains `htbp`.

Final figure pages: 2, 5, 7, 12, 13, 14, 15, 17.
Final table pages: 10, 11, 13, 16, 19.

Validation: latexmk success; no overfull boxes or unresolved references; paper.py check and check_final_latex.py pass. All 13 float bodies match the pre-layout version after ignoring placement options; body text also matches after excluding float locations and layout barriers. The manuscript remains 22 pages. References retain a partially filled final page; no artificial text compression or forced page breaks were used to remove it.
