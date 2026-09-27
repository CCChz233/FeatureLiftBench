# Related Work revision — 2026-09-16

Implemented in `../main.tex` and `../references.bib`. No LaTeX compilation.
The older `related_work.tex` is a historical draft used by the explicitly gated
initial-draft assembler; the active manuscript is `../main.tex`.

## Organization

1. **Repository-Level Coding and Feature Development** — begins with the nearest
   benchmark comparisons; explicitly retains FeatureBench's from-scratch setting.
2. **Feature Location, Extraction, and Software Reuse** — connects slicing and
   feature location to transplantation and Foundry/prodScalpel.
3. **Behavior-Preserving Refactoring and Transformation** — adds EM-Assist and
   SWE-Refactor, distinguishing a requested transformation within a project from
   delivering a capability across an independent package boundary.
4. **Repository Context and Evidence Utilization** — one short paragraph linking
   retrieval/completion studies to the paper's source-evidence questions.

The standalone harness subsection is removed. OpenHands is cited at the setup's
framework declaration, and SWE-agent / Harness-Bench support the existing
model–harness interpretation there. Table 7 adds SWE-Refactor and narrows the
transplantation row to donor–host transplantation so it does not overgeneralize
the broader product-line literature. Empirical results and figure assets are
unchanged.

## Added references and primary-source decisions

| Citation key | Verified source and use |
| --- | --- |
| `souza2025foundry` | [Author-deposited accepted paper and abstract](https://discovery.ucl.ac.uk/id/eprint/10196236/) describe tests, feature annotations, implantation points, and product-line integration. Use the 2025 journal publication year and DOI confirmed in the [authors' FSE 2025 Journal First entry](https://conf.researchr.org/details/fse-2025/fse-2025-journal-first/49/Software-Product-Line-Engineering-via-Software-Transplantation), rather than the repository's 2024 accepted-manuscript date. Unverified volume/page metadata omitted. |
| `pomian2024emassist` | Use the published title *Next-Generation Refactoring: Combining LLM Insights and IDE Capabilities for Extract Method*, rather than the earlier *Together We Go Further* preprint title. [Author-hosted paper](https://danny.cs.colorado.edu/papers/EM-Assist.pdf); [ICSME 2024 program](https://conf.researchr.org/details/icsme-2024/icsme-2024-papers/2/Next-Generation-Refactoring-Combining-LLM-Insights-and-IDE-Capabilities-for-Extract-); [author-institution record with DOI and pages](https://experts.colorado.edu/display/pubid_384101). |
| `xu2026swerefactor` | [Original paper, v1](https://arxiv.org/html/2602.03712v1), especially Section 3.2, verifies target-method/refactoring-type inputs and project compilation, tests, and structural verification. Cited as an arXiv preprint; no conference acceptance inferred. |
| `zhang2023repocoder` | [ACL proceedings record](https://aclanthology.org/2023.emnlp-main.151/) and its BibTeX export establish authors, title, venue, pages, and DOI. Used for iterative retrieval and generation; does not conflate its evaluation dataset with Liu et al.'s RepoBench. |
| `liu2024repobench` | [Official ICLR 2024 proceedings](https://proceedings.iclr.cc/paper_files/paper/2024/hash/d191ba4c8923ed8fd8935b7c98658b5f-Abstract-Conference.html) verify the retrieval/completion/pipeline distinction and publication year. |
| `ding2023crosscodeeval` | [Official NeurIPS 2023 proceedings](https://proceedings.neurips.cc/paper_files/paper/2023/hash/920f2dced7d32ab2ba2f1970bc306af6-Abstract-Datasets_and_Benchmarks.html) and the [authors' repository citation](https://github.com/amazon-science/cceval) verify metadata and cross-file completion scope. |

FeatureBench's incremental and from-scratch distinction was checked against
[Section 2 of the original paper](https://arxiv.org/html/2602.10975v1).
No related-work performance numbers are imported into the manuscript, and no
claim of priority for feature extraction, transplantation, or behavior preservation
is introduced.
