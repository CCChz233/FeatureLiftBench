# Related-work source audit

For the current bibliography metadata and version choices, see
[BIBLIOGRAPHY_REVIEW.md](BIBLIOGRAPHY_REVIEW.md) (2026-09-08). The older source
notes below are retained as review history.

## 2026-09-08 narrative and comparison-table integration

The current `../main.tex` now includes a rewritten introduction and a seven-row
task-interface comparison (`tab:positioning`). This revision uses primary papers
to explain related task formulations; it does not compare leaderboard scores or
claim a systematic literature search. Existing bibliography keys are sufficient.

| Source checked | Use in the manuscript |
| --- | --- |
| [SWE-bench, §2.2](https://arxiv.org/html/2310.06770#S2.SS2) | Issue and repository input, patch output, tests on the revised project. |
| [SWE-Bench Pro, §3.2 and §4](https://arxiv.org/html/2509.16941) | Issue-oriented changes with requirements and relevant interface information; does not reduce its scope to bug fixing. |
| [FeatureBench, §3.1–3.2 and Appendix B](https://arxiv.org/html/2602.10975v1) | Separate L1 and L2 rows. L1 removes the feature, L2 removes the repository at inference; callable interfaces are supplied. |
| [FeatBench v2, §3.1](https://arxiv.org/html/2509.22237v2) | Base repository plus requirements without code hints; feature and regression checks. |
| [Automated Software Transplantation, original author-hosted paper](https://crest.cs.ucl.ac.uk/autotransplantation/downloads/autotransplantation.pdf) | Donor-to-host reuse as an antecedent; annotations, analysis and testing. Direct PDF fetch timed out; the indexed original paper supplied the relevant abstract/introduction text. |
| [Terminal-Bench, §2](https://arxiv.org/html/2601.11868) | Task environments, executable verification, and separate construction/validation/analysis discussion. |
| [OSWorld, environment and benchmark sections](https://arxiv.org/html/2404.07972) | Initial-state setup and execution-based task evaluation. |

The FeatureLiftBench row and the synthesis across rows are the authors'
positioning of the local task definition. They do not assert that standalone
construction or software extraction is new. The strongest common thread is
intact donor access, bounded output obligations, donor-free artifact execution,
and separate footprint measurement. The table is maintained as authored LaTeX;
the 12 generated result tables remain unchanged.

The dated audit below is preserved as source-review history.

Status: Verified primary-source audit and proposed prose, 2026-09-07. This is a focused review, not a systematic literature review. No experiments were run. `main.tex` and the root `references.bib` were not changed by this subtask.

Integration update (2026-09-07): the primary agent incorporated the reviewed prose
and corrected bibliography into `../main.tex` and `../references.bib` after the
user authorized LaTeX drafting. The earlier subtask status above describes the
source audit at the time it was written.

Two additional entries support the benchmark discussion: [SWE-Bench Pro v2](https://arxiv.org/abs/2509.16941v2)
for longer-horizon tasks and trajectory failure analysis, and [OSWorld](https://arxiv.org/abs/2404.07972)
for task initialization and execution-based evaluation. Titles and full author
lists were checked against these primary records. No dynamic leaderboard scores
from these papers are used in the manuscript.

## Changes that matter to the paper's positioning

- **Extraction is an established research objective.** Automated software transplantation already extracts executable behavior from a donor and adapts it to an unrelated host. FeatureLiftBench's defensible contribution is an agent benchmark with a particular information interface and artifact evaluation, not the invention of automated feature extraction. See [Barr et al., original ISSTA 2015 paper](https://crest.cs.ucl.ac.uk/autotransplantation/downloads/autotransplantation.pdf).
- **FeatureBench includes standalone construction.** Its Section 3.1 defines both incremental development (L1) and implementation from scratch (L2). Therefore, neither “feature-development benchmarks only modify an existing repository” nor “independent/callable modules are absent from prior benchmarks” is safe. Its collection pipeline removes feature implementations from source to create tasks; FLB instead exposes an intact donor as implementation evidence. See [FeatureBench Sections 3.1–3.2](https://arxiv.org/html/2602.10975v1#S3).
- **No-Hint needs a precise qualifier.** FeatBench explicitly withholds code hints, including function signatures. FLB withholds source-location hints while specifying its output API; do not imply an identical information interface. See [FeatBench v2](https://arxiv.org/abs/2509.22237v2).
- **Terminal-Bench is broader than repository editing.** The current paragraph groups it with benchmarks that retain an original repository as the execution target. Split that assertion: Terminal-Bench has varied command-line tasks with their own environments. See [original Terminal-Bench paper](https://arxiv.org/abs/2601.11868).

## Existing bibliography

| Key | Verification and action |
|---|---|
| `example`, `example2`, `example3` | Explicit fabricated template entries. They are not cited by the inspected main text. Remove from the submission bibliography. |
| `jimenez2024swebench` | Title and ICLR 2024 venue verified by [the official repository](https://github.com/SWE-bench/SWE-bench); full authors are Carlos E. Jimenez, John Yang, Alexander Wettig, Shunyu Yao, Kexin Pei, Ofir Press, Karthik Narasimhan. The [original arXiv record](https://arxiv.org/abs/2310.06770) dates the preprint to 2023; using conference year 2024 is correct. The OpenReview page triggered a browser challenge in this audit. |
| `yang2024sweagent` | Title, authors, year and interface claim verified in the [original paper](https://arxiv.org/abs/2405.15793). Official project [citation instructions](https://swe-agent.com/latest/background/) confirm NeurIPS 2024. Replace `others` with Kilian Lieret, Shunyu Yao, Karthik Narasimhan, Ofir Press after the first three authors, and normalize Carlos E. Jimenez. The current page range was not independently checked against the NeurIPS proceedings record. |
| `merrill2026terminalbench` | Real, verified [arXiv:2601.11868](https://arxiv.org/abs/2601.11868), submitted January 17, 2026. Title and first three authors match. The full author list contains 85 names. `@misc` with arXiv eprint/URL is cleaner than a journal field naming an arXiv preprint. |
| `yao2026harnessbench` | Real, verified [arXiv:2605.27922](https://arxiv.org/abs/2605.27922), submitted May 27, 2026. Title and first three authors match. Remaining authors: Yaoming Li, Zhengyang Wang, Wenhan Yu, Zhewen Tan, Yuxuan Tian, Guangxiang Zhao, Lin Sun, Xiangzheng Zhang, Tong Yang. Its abstract directly supports model--harness reporting. Not cited in the inspected old prose; used in the proposal. |
| `chen2021codex` | Real, title and 2021 date verified at [arXiv:2107.03374](https://arxiv.org/abs/2107.03374). HumanEval is synthesis from docstrings with functional correctness tests. Change from `@inproceedings` with an arXiv `booktitle` to `@misc` with `eprint = {2107.03374}`, `archivePrefix = {arXiv}`, and the URL. |
| `weiser1984slicing` | Mark Weiser, “Program Slicing,” IEEE TSE SE-10(4), 352–357, July 1984 confirmed by the [original paper scan](https://www.cs.kent.edu/~jmaletic/cs63901/readings/Weiser84.pdf). The DOI landing page did not resolve through the browser tool; the current DOI was not contradicted. The source itself calls a slice an independent program, so independence alone is not a novelty claim. |
| `tarr1999degrees` | Title, all four authors, ICSE 1999 and May 1999 date confirmed by the [authors' IBM Research record](https://research.ibm.com/publications/n-degrees-of-separation-multi-dimensional-separation-of-concerns). It supports overlapping concerns and multi-dimensional decomposition. The existing pagination and DOI were not independently verified because the DOI landing page failed to load. |
| `dit2013featurelocation` | Full authors, title, volume 25(1), pages 53–95, January 2013 and DOI verified by [the publisher](https://onlinelibrary.wiley.com/doi/abs/10.1002/smr.567). “Malcom” matches the publisher; do not change it to “Malcolm.” Online-first date is November 28, 2011; journal issue year 2013 is correct. |

No evidence of fabricated research papers was found among the substantive existing entries. Placeholder entries are the only explicit fictitious references.

## Added primary sources and exact uses

1. **Barr et al. (2015), Automated Software Transplantation.** [Original author-hosted paper](https://crest.cs.ucl.ac.uk/autotransplantation/downloads/autotransplantation.pdf); [author-submitted award copy](https://human-competitive.org/sites/default/files/barr-harman-jia-marginean-petke-paper.pdf). Supports analysis plus tests/search to extract donor functionality and adapt it to a host. Abstract and introduction establish lightweight annotations and programmer-provided test suites. The author-hosted PDF was searchable but direct opening failed; the text was available through the indexed original paper.
2. **Zhou et al. (2026), FeatureBench.** [Original paper with full author list and ICLR 2026 acceptance](https://arxiv.org/abs/2602.10975); [full text](https://arxiv.org/html/2602.10975v1). Section 3.1 supports both development settings; Section 3.2 supports test-driven dependency tracing and feature-removal task construction. No cross-benchmark numerical comparison is used.
3. **Chen, Li, and Li (2026 version), FeatBench.** [Version 2 paper](https://arxiv.org/abs/2509.22237v2); [full text](https://arxiv.org/html/2509.22237v2). The first preprint was September 2025 and had a different title. The BibTeX deliberately cites the revised February 18, 2026 version and its current title. Supports natural-language feature requirements without code hints and existing-repository feature implementation.
4. **Wang et al. (2025), OpenHands.** [Original paper, full author list, and ICLR 2025 acceptance](https://arxiv.org/abs/2407.16741). The preprint first appeared in July 2024. Use 2025 for the conference citation. Supports an extensible developer-agent runtime with tools, sandboxed execution and evaluation integration; FLB's exact runtime revision still needs its own local experimental record.

## Integration notes

- `related_work.tex` uses four new keys supplied by `verified_references.bib` and eight substantive existing keys.
- Add the four entries to the root bibliography, then correct the old reference types and replace truncated author fields where practical. Do not load a duplicate entry under an existing key.
- The proposal is about 580 prose words and replaces the four old subsections. The conceptual positioning table should be dropped or revised so that it explicitly distinguishes FeatureBench L1 and L2; its old blanket “feature addition → modified source repository” row is not an adequate characterization of the related literature.
- Exact source-to-source score comparisons are intentionally absent because task distributions, budgets, and agent configurations differ.
