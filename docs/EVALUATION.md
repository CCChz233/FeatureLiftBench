# FeatureLiftBench 评测与实验规范

> **Status: current · Last verified: 2026-09-02**
> 本文件是 Main 条件、正式实验臂、评分和结果留存要求的唯一当前规范。

## Official Main

| Dimension | Required value |
| --- | --- |
| Agent | OpenHands，记录 exact profile/revision |
| Source context | pinned full upstream repository |
| Source hints | hidden |
| Benchmark tests | hidden from the agent |
| Prompt | standard |
| Attempts | one per task；不得重试已完成失败 |
| Execution | agent Docker + isolated evaluator Docker |
| Core metric 1 | Functional Pass Rate |
| Core metric 2 | Reference-Relative Extraction Size (RRES) |

Main 是 leaderboard 和论文主结果的唯一默认条件。当前论文套件是 Python-200'
（`--benchmark python200_hard`）。Task contract 与可见性以
[TASK_DESIGN_RULES.md](TASK_DESIGN_RULES.md) 为准，当前 suite identity 以
[STATUS.md](STATUS.md) 为准。

## Formal Ablations

| Arm | Only intended change | Interpretation |
| --- | --- | --- |
| Entrypoint-Hint | expose frozen source-location hints | localization information value |
| Public-Feedback | expose/mount public tests | benchmark-feedback value |
| Pruned-Context | replace full repo with declared pruned context | source-context value |
| Short-Prompt | alter prompt wording only | prompt sensitivity |

每个 ablation 必须记录 `ablation_arm` 和 changed dimension，并保持 task、model、
agent、evaluator、image、attempt policy 与其余 Main 条件不变。

## Optional Runtime Ablation

换 **coding runtime**，不换信息边界。不是上表信息消融，也不是 Official Main。

| Dimension | Required value |
| --- | --- |
| Agent | `deepseek-harness` 或 `codex`，记录 pin tag + commit |
| Source / hints / tests / prompt / attempts | 与 Official Main 相同 |
| Evaluator | isolated eval Docker，`functional_gate` + RRES |
| Execution | 默认 host CLI + eval Docker；agent 镜像可用 `FEATURELIFTBENCH_INSTALL_RUNTIME_AGENTS=1` 装入 `dsh`/`codex` |
| Slice | 先 Core-12，与同日 OpenHands+Flash Main 成对 |
| Reporting | 独立 runtime 表；**不得并入** 5-model OpenHands Python-200 主表 |

Pins、adapter 与入口见 [METHOD_AGENT_RUNTIME.md](METHOD_AGENT_RUNTIME.md)。
尚无正式分数时，STATUS / FINDINGS 只记基础设施就绪，不编造通过率。

Contract Closure 的旧 **Lite V1 协议**（checker / stop / repair）是已退役的方法
实验臂，不是默认 leaderboard，也不是当前 V1。DeepSeek Python-200 上那次对比
使用 Main 预算（120 步 + repair），不得与 45+10 Frozen 信封混比。

当前 cost arm **V1 = Main + 2M token cap**，见 [METHOD_V1.md](METHOD_V1.md)。
Rescue+、Adaptive Budget V2、Test-First Lift、TD-Cognition、Exec/Self-Contract、
CGCC-lite、FCEC 和 PDR 是历史方法研究，**停止扩样本**，见
[archive/methods/](archive/methods/README.md)。不要在 Core-12 / Distill-24 上继续
叠脚手架。正式信息消融是上表 Public-Feedback / Entrypoint-Hint 等臂。

RQ6 只跑 **Public-feedback**，且只在 Flash-12 同日成对切片上。规范见
[METHOD_RQ6_PUBLIC_FEEDBACK.md](archive/methods/METHOD_RQ6_PUBLIC_FEEDBACK.md)。读出是
`functional_gate` 加 public/hidden 翻转。**不要**把该切片写入 Python-200 主表。
Entrypoint-Hint / Pruned-Context / Short-prompt 尚未跑，不要与本臂叠。

## Evaluation Pipeline

1. 校验 suite selection、freeze 和 canonical source mapping。
2. 物化完整 pinned source，构造 No-Hint workspace；Official Main 在 agent Docker
   中运行一次。Runtime ablation 默认使用 `./setup.sh` 安装的 host `dsh`/`codex`，
   evaluator 仍进隔离 Docker。
3. 只收集 `submission/`，不把原仓库加入 runtime `PYTHONPATH`。
4. 在 source-free evaluator capsule 中运行 build、public、hidden 和 isolation gates；
   禁止网络、forbidden imports、submission subprocess 和 evaluator-private path access。
5. functional container 退出后，由 trusted metrics stage 只读计算 compactness；该阶段
   不 import、安装或执行 submission。
6. 保存逐题 `run.json`、`eval/result.json`、submission、trajectory、usage 和日志，再
   重建 suite index。

Runner 必须在模型调用前通过 strict Docker preflight。任何 source、task、evaluator、
visibility 或 attempt-policy 变化都会形成不同实验条件。

## Core Metric 1: Functional Pass Rate

```text
FunctionalPass =
  BuildPass
  AND PublicTestsPass
  AND HiddenTestsPass
  AND IsolationPass
```

`functional_gate` 为 0/1，一次完整 task attempt 对应一次 Pass@1 观察：

```text
Functional Pass Rate = sum(functional_gate) / assigned_tasks
```

兼容字段
`test_pass` 等于 public 与 hidden 的合取，`original_import_pass` 等于 isolation，
`final_score` 等于 `functional_gate`。因此 Average Final Score 与 Functional Pass Rate
数学上相同，不是第三个指标，不应重复报告。

Agent completion、step/context limit、rate limit 和 infra failure 必须另列。若 Agent
流程超时但已留下 evaluator 可通过的 submission，Functional 仍为 pass，Agent
completion 为 fail；不能用 `run.status`、`summary.passed` 或 bundle MANIFEST
覆盖 benchmark correctness。

## Core Metric 2: Reference-Relative Extraction Size

RRES 表示功能通过的提取模块相对冻结 reference 的规模，越低越紧凑：

```text
RRES = submission_normalized_loc / frozen_reference_normalized_loc
```

只对 `functional_gate = 1` 的 submission 计算；失败样本的 RRES 记为 N/A，不用一个
小而错的实现换取“紧凑”。主表报 median 和 IQR（Q1–Q3）；两方法比较时，
优先报告同一模型、同一 task 且两方都 Functional Pass 的 paired subset。

Reference 是可行紧凑实现，不是数学最小解。`copied_fraction`、文件数和依赖数可作
解释性诊断，但不是核心得分，也不能单独支撑 plagiarism claim。

## Functional Failure Classification

每道未通过题必须按首个确定失败阶段记一个互斥 primary outcome：

```text
missing_submission
  > build_failure
  > public_failure
  > hidden_failure
  > isolation_failure
  > functional_pass
```

这是诊断分类，不是新的得分。各 gate 仍保留 `pass / fail / not_evaluated / infra_unknown`
状态；缺少逐题 evaluator 证据时必须标为 `stage_evidence_unavailable`，不得根据
suite summary 猜测 public 或 hidden 失败。语义原因可另行人工标注，但不覆盖
机械阶段。

## Operational Diagnostics

Tokens、API calls、steps、time、agent completion、context/rate-limit 和 infra 信息只用于
成本和运行诊断，不进入核心排名，不与 Functional Pass 或 RRES 加权混合。

## Execution And Resume Rules

- checkout exact revision，验证 suite/task-set hash、source archives 和 image identities；
- 固定 model revision、agent runtime/adapter pin、agent profile、prompt arm、timeouts、workers 和 attempt policy；
- 先用同一 images、visibility 跑 end-to-end smoke；
- resume 只处理没有 terminal `run.json` 的题；
- 不查看 hidden failure 来调整正在运行的模型或 prompt；
- Main 不向 agent 挂载 benchmark root、tests、reference、Docker socket、host home 或 secrets；
- context、infra、rate-limit、manual intervention 和 rerun exception 单独记账。

## Required Artifacts And Reporting

每个 paper-candidate suite 必须保留：

- exact task IDs、suite/task-set hash、freeze/selection IDs；
- model、agent runtime/adapter、agent profile、arm、attempt/resume policy；
- agent/evaluator image identities（runtime ablation 另记 host binary pin）；
- per-task `run.json`、`eval/result.json`、submission、trajectory、usage/context audit；
- exception ledger 和可复现分析命令。

Core table 只报告 Functional Pass Rate 和 pass-conditioned RRES，同时给出 assigned、
evidence coverage、置信区间和 task-paired comparison。Failure table 报告互斥首败阶段及
`stage_evidence_unavailable`。运行资源只放 appendix/diagnostics。不同 source、
visibility、attempt、evaluator **或 agent runtime** 条件不得并入同一 leaderboard。

当前结果资格和解释边界见 [STATUS.md](STATUS.md)，证据位置见
[reports/README.md](../reports/README.md)。旧版细节保存在
[archive/specs/](archive/specs/README.md)，不再是当前规范。
