# Research Questions

> **Documentation status: current · Last verified: 2026-08-17**

## RQ1 — Functional capability

Can current code agents extract independent, behavior-complete features from
full repositories under No-Hint Main?

Primary evidence:

- evaluator Functional Pass@1；
- build→public→hidden→isolation funnel；
- cross-model paired task outcomes。

## RQ2 — Compactness

How compact are functionally passing submissions relative to frozen references?

Evidence:

- Reference-Relative Extraction Size（RRES）：`submission_normalized_loc / reference_normalized_loc`；
- 只在 Functional Pass 上报告 median/IQR，方法对比使用同题双通过 subset；
- submission/reference file ratios；
- copied LOC/fraction；
- dependency footprint；
- copy-heavy pass rate；
- copy-all and reference controls。

Compactness is separate from Functional Pass and is not a minimality proof. RQ1 和 RQ2
是 leaderboard 的两项核心指标；RQ3 是运行诊断，不与前两者加权合并。

## RQ3 — Cost and efficiency

What resources do agents consume, and how does cost relate to outcome?

Evidence:

- API calls；
- prompt/completion/total tokens；
- interaction steps；
- agent/evaluator/wall-clock time；
- step/context/rate/infra failures。

## RQ4 — Failure mechanisms

Where does FeatureLift fail?

Stages:

- localization；
- API/behavior contract completion；
- dependency/resource/registry closure；
- packaging；
- isolation；
- compactness；
- process/infra。

Mechanical labels come from evaluator/run logs；semantic attribution uses
trajectory evidence and must disclose whether it is AI-assisted or manually
reviewed。

## RQ5 — Task factors

Which task properties are associated with success、compactness and cost?

Candidate variables:

- repository archetype/domain；
- source LOC/files/depth；
- task footprint/reference files/LOC；
- entanglement primary/types；
- resources、dynamic dispatch、global state；
- source popularity/long-tail；
- historical Core-100/Hard-50 construction slice。

Use correlations and stratified comparisons, not causal language from small
subgroups.

## RQ6 — Information ablations

How do controlled information changes affect results?

| Arm | Question |
| --- | --- |
| Entrypoint-Hint | How much does source localization information help? |
| Public-feedback | How much does evaluator feedback help? |
| Pruned-Context | What is the effect of reducing repository context? |
| Short-prompt | Does procedural prompt wording matter? |
| Reference Support Set | What is the closure-information upper bound? |

All arms use the same task/spec/model/agent/evaluator/environment and are
compared on the same task subset.

## Evidence order

1. Run frozen v3 Main baseline。
2. Report RQ1–RQ5 on complete suites。
3. Select a preregistered paired subset for RQ6。
4. Run method experiments only after failure mechanisms are established。

Current evidence and gaps: [STATUS.md](../STATUS.md)。
