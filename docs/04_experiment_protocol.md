# Experiment Protocol

## Official Main

```text
Agent: OpenHands
Model: exact specified identifier/profile
Arm: Main
Source: canonical full-repository snapshot
Hints: none
Benchmark tests visible to Agent: none
Sandbox: agent Docker + evaluator Docker
Split: Python-150
Attempts: 1 per task
Primary: evaluator Functional Pass@1
Secondary: reference-relative compactness
```

Active benchmark freeze 和执行状态见 [STATUS.md](STATUS.md)。服务器操作见
[SERVER_RUNBOOK_PYTHON150.md](SERVER_RUNBOOK_PYTHON150.md)。

## Required baselines

| Baseline | Purpose | Main table? |
| --- | --- | --- |
| OpenHands + target model | End-to-end Agent ability | Yes |
| Multiple model strengths | Model discrimination | Yes |
| Copy-all control | Compactness sanity check | No, diagnostic |
| Frozen reference | Evaluator/oracle and compactness reference | No, construction control |
| Naive/stub control | Hidden-test discrimination | No, task-quality control |

Single-shot LLM、mini-swe-agent 或其他 Agent 可以作为扩展 baseline，但必须
单独记录 agent harness，不能只按模型名比较。

## Ablations

| Arm | Changes from Main |
| --- | --- |
| Entrypoint-Hint | Adds frozen source-location hints |
| Public-feedback | Exposes basic evaluator tests |
| Pruned-Context | Replaces full source with declared pruned snapshot |
| Short-prompt | Compresses prompt wording only |
| Reference Support Set | Upper-bound closure information, if run |

除声明变量外，task/spec/model/agent/evaluator/environment 必须保持一致。详细
定义见 [EXPERIMENT_ARMS.md](EXPERIMENT_ARMS.md)。

## Before execution

1. Checkout exact code revision。
2. Verify active benchmark freeze。
3. Materialize and digest-check 132 source snapshots。
4. Validate all 150 tasks and No-Hint workspaces。
5. Verify 450/450 Oracle evidence or rerun if freeze changed。
6. Build fixed agent/eval images and record digests。
7. Freeze model profile、prompt arm、timeouts、workers 和 attempt policy。
8. Run one end-to-end smoke with the same images and visibility。

Runner plan mode must complete without calling the model. Any source/spec/
evaluator/environment change invalidates the old freeze.

## During execution

- One task gets at most one model attempt。
- Resume only tasks without terminal `run.json`。
- Do not retry a completed model failure and still label the suite Pass@1。
- Log context-limit、step-limit、rate-limit、infra failure and manual intervention。
- Do not inspect hidden failures to tune the running model/prompt。
- Do not expose benchmark root、hidden/public evaluator assets、reference、
  Docker socket、host home or secrets to the Agent container。

## Required artifacts

Per task:

```text
run.json
submission/
eval/result.json
agent trajectory/stdout/stderr
usage and timing
```

Per suite:

```text
suite.json
benchmark freeze ID
task ID set
agent/eval image digests
model/profile/arm
attempt and resume policy
exception ledger
checksums/data-quality report
```

## Reporting

Primary table:

- evaluator Functional Pass@1；
- assigned/completed；
- confidence interval；
- model/agent/profile；
- context/infra exception counts。

Secondary tables:

- build→public→hidden→isolation funnel；
- compactness vector；
- tokens、steps、API calls、latency；
- repository/domain/entanglement/source-size/task-footprint slices；
- paired ablations。

`run.status`、agent completion 和 evaluator functional gate must be shown
separately when they disagree.

## Repeats

Default paper comparison is one Pass@1 attempt per task, not 100 repeated suite
runs. Additional repetitions answer variance/stability questions and must be
reported as a separate experiment:

- same frozen task set；
- same model/profile/arm；
- independent run IDs/seeds when available；
- Pass@k or variance estimator specified before execution。

Repeated model runs are not required to establish benchmark validity; Oracle
repetition and deterministic gates establish benchmark execution stability.

## Data hygiene

- Main never exposes benchmark public/hidden tests before submission。
- Hidden never becomes a tuning set。
- Exact protocol differences are visible labels, not footnotes。
- Historical `mixed_snapshot_v1` results remain historical。
- Raw results remain in `experiments/`; tracked summaries include checksums and
  provenance but no secrets。

Living experiment inventory: [EXPERIMENTS.md](EXPERIMENTS.md). Result
interpretation: [FINDINGS.md](FINDINGS.md)。
