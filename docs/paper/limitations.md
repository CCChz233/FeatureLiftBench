# Known Limitations

> **Documentation status: current · Last verified: 2026-08-04**

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

- The balanced extension has not yet been completed across the paper model set, so no final
  Python-200 leaderboard is available.
- The archived DeepSeek baseline is partial and cannot be extended to a complete score by only
  running the new extension.
- Pass@1 uses one trajectory per task and does not estimate sampling variance. Repeated trials
  require a separately preregistered experiment.
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

Current gate status is maintained in [STATUS.md](../STATUS.md), result boundaries in
[STATUS.md](../STATUS.md), and design assumptions in
[BENCHMARK_DESIGN.md](../BENCHMARK_DESIGN.md).
