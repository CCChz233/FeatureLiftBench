# Offline standard-subset × received-package slice (2026-09-02)

> Not a leaderboard. No Agent/API runs.

Intersect v2 contract labels (168 meets / 32 violates / 0 undetermined) with
the 2026-08-29 DeepSeek V4 Flash received package.

Regenerate:

```bash
python3.12 reports/paper_analysis/python200_hard_main_20260829/export_offline_standard_slice.py
```

Headline sensitivity, **fixed eligible 116 only** (no freeze block, wheel gap,
or context violation):

| Slice | n | Pass | Rate |
| --- | ---: | ---: | ---: |
| Fixed 116 | 116 | 95 | 81.9% |
| meets ∩ 116 | 96 | 81 | 84.4% |
| violates ∩ 116 | 20 | 14 | 70.0% |
| meets ∩ replacement 84 | 72 | — | not eligible |

C4 test-overlap advisory: 29/200; 2 overlap violates, 27 overlap meets.

LaTeX snippets are copied to `docs/paper/offline_tables/` and
`docs/paper/fse26/tables/`.
