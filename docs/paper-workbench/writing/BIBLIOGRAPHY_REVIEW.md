# Bibliography review — 2026-09-08

The active bibliography is [`../references.bib`](../references.bib). All 14
existing citation keys are retained and used by `main.tex`. This revision changes
bibliographic metadata and formatting only; it does not change manuscript prose.
`verified_references.bib` and `original_references_20260907.bib` remain historical
materials, not alternate active bibliographies.

## Changes and source decisions

| Entry | Decision and supporting source |
| --- | --- |
| SWE-bench | Retain ICLR 2024 and normalize the conference name; [OpenReview record](https://openreview.net/forum?id=VTF8yNQM66). |
| SWE-agent | Use the [official NeurIPS 2024 proceedings record](https://proceedings.neurips.cc/paper_files/paper/2024/hash/5a7c947568c1b1328ccc5230172e1e7c-Abstract-Conference.html); add volume 37, DOI, and proceedings URL. |
| OSWorld | Use the [official NeurIPS 2024 proceedings record](https://proceedings.neurips.cc/paper_files/paper/2024/hash/5d413e48f84dc61244b6be550f1cd8f5-Abstract-Datasets_and_Benchmarks_Track.html); add volume 37, DOI, and proceedings URL. |
| Terminal-Bench | Restore the full 85-author list from [arXiv](https://arxiv.org/abs/2601.11868). Retain the paper's actual title, which does not contain “2.0,” and its 2026 preprint status. |
| Evaluating Large Language Models Trained on Code | Restore the full 58-author list from the [arXiv record](https://arxiv.org/abs/2107.03374); retain the 2021 preprint. |
| Harness-Bench | Retain the 2026 preprint and add the subject class from [arXiv](https://arxiv.org/abs/2605.27922). |
| SWE-Bench Pro | Keep [arXiv v2](https://arxiv.org/abs/2509.16941v2), its 22 authors, and 2025 date. Do not combine this version with the earlier OpenReview submission's different author list or treat submission as acceptance. |
| FeatBench | Keep [arXiv v2](https://arxiv.org/abs/2509.22237v2), revised February 18, 2026. The current title and year refer to this revision, not the differently titled 2025 first version. |
| FeatureBench | Retain ICLR 2026, supported by the [arXiv acceptance comment](https://arxiv.org/abs/2602.10975) and [official OpenReview paper](https://openreview.net/pdf/5a73d3028cb1df0955fd6a1e37f104849abdc762.pdf). Retain the arXiv URL because a stable forum identifier was not established in this review. |
| OpenHands | Use the [ICLR 2025 OpenReview record](https://openreview.net/forum?id=OJd3ayDDoF), keeping the full author list. |
| Classic software-engineering references | Retain the existing publication records for Weiser, Tarr et al., Dit et al., and Barr et al. Correct BibTeX suffix parsing for Stanley M. Sutton, Jr., and use the canonical ACM DOI URL for software transplantation. |

The classic references were checked against available original/publisher records:
[Weiser's original paper](https://www.cs.kent.edu/~jmaletic/cs63901/readings/Weiser84.pdf),
[IBM's Tarr et al. record](https://research.ibm.com/publications/n-degrees-of-separation-multi-dimensional-separation-of-concerns),
[Wiley's Dit et al. record](https://onlinelibrary.wiley.com/doi/10.1002/smr.567),
and [Barr et al.'s author-hosted paper](https://crest.cs.ucl.ac.uk/autotransplantation/downloads/autotransplantation.pdf).
Dit et al. keeps the journal issue year 2013 rather than the online-first year
2011, and the author's published spelling “Malcom Gethers.” Some publisher
endpoints were inaccessible; existing classic DOI and page fields were retained
where they could not be independently rechecked. Unverified NeurIPS page ranges
were not added.

## Formatting and checks

- Protect benchmark names and acronyms against bibliography-style case changes.
- Use complete author lists in the source; leave display truncation to the style.
- Normalize field layout, conference naming, and preprint fields without changing keys.
- Check that all 14 entries are cited, with no duplicate keys or missing citations.
- Check required fields, brace balance, author-list completeness, and DOI syntax.

[`bibliography_validation.json`](bibliography_validation.json) records the static
checks and bibliography digest. These checks do not verify rendered bibliography
layout. No LaTeX compilation, rendering, or new experiments were performed.
