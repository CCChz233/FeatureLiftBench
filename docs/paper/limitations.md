# Known Limitations

> **Documentation status: current · Last verified: 2026-08-28**

## Dataset Construction

- **Maintainer selection.** Tasks and balanced replacements were selected through a
  maintainer/AI-assisted workflow. This is not a random sample of Python repositories.
- **Library/tooling skew.** The release emphasizes Python libraries, tooling and framework
  components; it does not establish performance on large product applications, GUI, GPU,
  cloud-native or distributed systems.
- **Popular upstream projects.** Well-known repositories may be represented in model training.
  Popular-vs-long-tail and contamination sensitivity remain incomplete.
- **Mechanism balance.** Repository diversity does not guarantee balanced parser state,
  registry, resource, dependency and lifecycle mechanisms. Use the frozen balance audit rather
  than broad claims from package count alone.
- **Evidence quality.** Upstream tests, docs and examples vary greatly, so task difficulty also
  reflects upstream engineering quality.

## Task Design and Gold Evidence

- Public and hidden tests are constrained by one public contract, but finite tests cannot prove
  complete semantic equivalence.
- Contract, taxonomy and closure records include AI-assisted curation and are not independently
  adjudicated human gold unless explicitly marked.
- Frozen reference implementations are feasible solutions, not proofs of a unique minimal
  closure.
- Current closure-gold completeness is uneven; copied-fraction and extraction diagnostics must
  not be promoted to headline authenticity claims without manual audit.
- A behaviorally equivalent rewrite can pass even if it does not literally extract upstream
  code. The benchmark measures reconstruction under repository evidence, not internal intent.

## Evaluation

- Functional Pass is binary and gives no headline partial credit.
- Compactness, copy and dependency metrics are proxies and may miss semantic copying or count
  common templates.
- Isolation checks cover known imports, paths, resources and dependency channels but cannot
  prove absence of every possible bypass.
- Agent completion and evaluator Functional status can disagree; both must be reported.
- Context-window violations and infrastructure exceptions can affect model comparisons and need
  a declared sensitivity policy.
- Existing archived results require evaluator-image attestation or re-evaluation before exact
  frozen-environment claims.

## Experimental Evidence

- 论文主套件 Python-200'（150+Hard-50）已有 DeepSeek V4 Flash OpenHands Main
  收到包的 **audit headline 132/200（66.0%）**，但仅 183 题启动：17 题
  freeze-preflight blocked、16 题离线依赖失败、59 题触发 context-window audit，三类
  问题去重后需严格替换 84 题；闭环前不能作为最终主表。旧 Python-200
  （150+External-50）Main 在 OpenHands 下对 Flash / Qwen3.5 / Qwen3.6 / GPT-OSS
  完整，Pass@1 为 21.5%–72.5%；该套件上 pass-conditioned RRES 中位数贴 1.000，
  主要来自 External-50 copy-heavy，**不能**当新主表，也不能跨模型排紧凑度。
- 候选整套结果拆分为 Python-150 103/150、Hard-50 29/50；单模型单次结果不能替代
  跨模型主表或运行稳定性分析。
- Official Main is OpenHands. DeepSeek Harness and Codex adapters exist as an
  optional runtime ablation with pinned revisions, but they have no scored
  Core-12 or Python-200 results yet and must not be merged into the OpenHands
  leaderboard ([METHOD_AGENT_RUNTIME.md](../METHOD_AGENT_RUNTIME.md)).
- Lite V1 **protocol** (checker / repair) has been compared with Main only on
  DeepSeek. That comparison shows a token saving, a Functional Pass drop, and no
  paired RRES advantage. The current cost arm is **V1 = Main + 2M cap**, not
  that protocol; Qwen3.6 Python-200 V1 is complete (55/200).
- Pass-conditioned \(T^\*\) is undefined on failures. Public-test green on a
  failing trajectory is not proximity to Hidden. RQ6 Public-feedback on
  Flash-12 recovers public on all six public-failure tasks; four of five
  paired hidden-failure tasks stay hidden 0
  ([04_results_rq6.md](04_results_rq6.md)).
- RQ6 numbers are an information ablation of Main. They are not Python-200
  pass rates and must not replace uncapped Main.
- Default unique-tree sampling makes \(T^\*/T\) an upper bound on tasks that
  pass before 2M; those bounds are still below 2M.
- Qwen V1-200 has no Phase 1 gold. Do not invent \(T^\*\) for unmatched
  replay.
- `metadata.difficulty` is construction metadata, not a scientific
  easy/medium/hard rubric.
- Historical mixed-snapshot and method-pilot results may support mechanism hypotheses or negative
  results, but their absolute rates are not current Main results.
- Go remains calibration evidence and is not part of the Python paper leaderboard.

## Reproducibility and Licensing

- Results depend on source archives, Python, offline wheels, Docker, the agent framework, model
  provider/router behavior and resource limits. Recording a freeze reduces but does not remove
  platform dependence.
- Large archives and raw runs are not fully committed to Git; durable reproduction requires
  preserving verified bundles and checksums.
- Upstream snapshots retain heterogeneous licenses. Redistribution of source, references and
  submissions must follow each upstream license.
- Model APIs and serving stacks can change after a run even when a model name remains constant;
  exact model revision and image identity are required.

Current gate status and result boundaries are in [STATUS.md](../STATUS.md);
interpretation is in [FINDINGS.md](../FINDINGS.md); design assumptions are in
[BENCHMARK_DESIGN.md](../BENCHMARK_DESIGN.md).
