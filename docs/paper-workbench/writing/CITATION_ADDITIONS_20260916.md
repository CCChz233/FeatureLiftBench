# Claim and method citation additions — 2026-09-16

Added eight references at specific claims in the active `../main.tex`, bringing
the manuscript to 25 distinct cited works (28 bibliography entries, three unused).
These additions support concepts and existing methods; they do not change
experiments, metrics, numerical results, or the four-subsection Related Work
organization. No LaTeX compilation.

| Location | Citation | Supported claim and original source |
| --- | --- | --- |
| Introduction opening | `krueger1992reuse` | Reuse involves selecting, adapting, and integrating existing artifacts. [ACM publisher record and abstract](https://doi.org/10.1145/130844.130856). |
| Task formulation | `meyer1992contract` | Contracts make interface obligations explicit. [Author-hosted original paper](https://se.inf.ethz.ch/~meyer/publications/computer/contract.pdf), pp. 41–42; [author publication list](https://se.inf.ethz.ch/~meyer/publications/index_date.html). This does not claim the benchmark implements Eiffel assertions or formal verification. |
| Benchmark validation opening | `barr2015oracle` | Correctly judging intended behavior is the test-oracle problem. [Original paper](https://philmcminn.com/publications/barr2015.pdf) and [author's publication record / BibTeX](https://philmcminn.com/publications/oracles). This supports the validation motivation, not the benchmark's own validation outcomes. |
| Copy metric interpretation | `roy2009clones` | Syntactic similarity and semantic equivalence are distinct; clone types and editing scenarios motivate this distinction. [Publisher record and abstract](https://www.sciencedirect.com/science/article/pii/S0167642309000367). The local three-line threshold remains our operational definition and is not attributed to this paper. |
| Paired ablation statistical method | `fagerland2013mcnemar` | Exact conditional McNemar testing for matched binary outcomes. [Original article](https://doi.org/10.1186/1471-2288-13-91), with [publisher-hosted PDF](https://bmcmedresmethodol.biomedcentral.com/counter/pdf/10.1186/1471-2288-13-91.pdf). The citation identifies the exact conditional variant; it does not claim that the article recommends it over mid-p. The actual existing computation and p-values are unchanged. |
| Multiple comparisons | `holm1979multiple` | Holm's sequentially rejective correction. [Original article scan](https://www.ime.usp.br/~abe/lista/pdf4R8xPVzCnX.pdf), pp. 65–70; [stable journal archive identifier](https://www.jstor.org/stable/4615733). |
| Footprint confidence intervals | `field2007cluster` | Cluster resampling for clustered observations. [Publisher abstract and metadata](https://rss.onlinelibrary.wiley.com/doi/10.1111/j.1467-9868.2007.00593.x). The citation supports the general resampling approach, not a theorem establishing validity for our exact success-selected design or comparison-graph rejection rule. |
| Related Work: refactoring | `opdyke1992refactoring` | Refactoring operations with preconditions for behavior preservation. [University dissertation record and abstract](https://www.ideals.illinois.edu/items/72240). This establishes the classic foundation preceding EM-Assist and SWE-Refactor. |

Most additions are foundational rather than recent benchmarks because the
identified gaps concern definitions, measurement, and statistical methods.
Recent neighboring benchmarks remain in the rewritten Related Work section.
RRES remains explicitly defined as this paper's metric; our empirical findings
do not acquire external citations merely to increase the reference count.
