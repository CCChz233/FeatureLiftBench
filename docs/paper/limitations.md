# Known Limitations

> **Documentation status: current · Last verified: 2026-08-20**

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

- Python-200 Main is complete for DeepSeek V4 Flash (API and local vLLM),
  Qwen3.5 122B, Qwen3.6 35B, and GPT-OSS 120B. Pass-conditioned RRES medians
  sit at 1.000 and there is no paired cross-model RRES, so compactness cannot
  be ranked across models.
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
