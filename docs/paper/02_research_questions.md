# Research Questions

> **Documentation status: current · Last verified: 2026-08-28**

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

**Where sufficiency occurs.** On trajectories that eventually pass, report
\(T^\*/T_{\mathrm{total}}\) using the earliest unique `featurelifted` tree with
`functional_gate=1.0`, not last package write. Stratify Flash / Qwen / OSS and
Direct / Adapted / Composite. Draft:
[03_results_token_utility.md](03_results_token_utility.md). This is a cost
slice, not a new protocol and not a stopping rule.

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
subgroups. For cost-on-pass trajectories, lift type (Direct / Adapted /
Composite) is the task axis that moves \(T^\*\); informal difficulty and
`metadata.difficulty` do not. See
[03_results_token_utility.md](03_results_token_utility.md).

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
compared on the same task subset. Public-feedback is the first arm; it is an
information ablation of Main, not a competing method. Draft:
[04_results_rq6.md](04_results_rq6.md).

Changing the coding runtime (DeepSeek Harness / Codex vs OpenHands) is **not**
RQ6. It is an optional appendix factor with the same information boundary; see
[METHOD_AGENT_RUNTIME.md](../METHOD_AGENT_RUNTIME.md). Do not merge those scores
into the OpenHands Python-200 Main table.

## Evidence order

1. 论文主表是 Python-200'（150+Hard-50），**尚未出分**。旧跨模型 Python-200
   （150+E50，21.5%–72.5%）见 [STATUS.md](../STATUS.md)，只作 superseded 对照。
2. DeepSeek 旧 Python-200 上可报告 RQ1–RQ4 机制（Main vs 已退役 Lite V1），换套件后
   主表数字要重跑。
3. Cost arm：**Qwen3.6-35B V1-200 已完成**（55/200，旧套件）；Flash 全量 V1 未跑，
   Core-12 诊断已表明 cap 税。见 [FINDINGS.md](../FINDINGS.md)。已有 Main 轨迹上的
   \(T^\*\) 成本切片见 [03_results_token_utility.md](03_results_token_utility.md)。
4. RQ6：Flash-12 Public-feedback 同日成对已齐（Main 0/12 → 4/12）。机制稿
   [04_results_rq6.md](04_results_rq6.md)。Entrypoint-Hint 等其余臂未跑。
   数字不进主表。
5. 不再开新方法臂，也不再从 token 尾巴写 early-stopping。历史脚手架负结果只作
   RQ4，见 [archive/methods/](../archive/methods/README.md)。不要单列 ADE。
6. Optional DeepSeek Harness / Codex runtime ablation 只有基础设施，没有正式
   分数；不进主表。见
   [METHOD_AGENT_RUNTIME.md](../METHOD_AGENT_RUNTIME.md)。

Current evidence and gaps: [STATUS.md](../STATUS.md)。
