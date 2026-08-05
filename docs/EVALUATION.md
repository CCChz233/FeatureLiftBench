# FeatureLiftBench 评测与实验规范

> **Status: current · Last verified: 2026-08-04**
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
| Primary metric | evaluator Functional Pass@1 |
| Secondary metrics | compactness、cost 和 process diagnostics |

Main 是 leaderboard 和论文主结果的唯一默认条件。Task contract 与可见性以
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
agent、evaluator、image、attempt policy 与其余 Main 条件不变。Test-First Lift、
TD-Cognition、Exec/Self-Contract、CGCC-lite、FCEC 和 PDR 是历史方法研究，不是当前
正式实验臂，见 [archive/methods/](archive/methods/README.md)。

## Evaluation Pipeline

1. 校验 suite selection、freeze 和 canonical source mapping。
2. 物化完整 pinned source，构造 No-Hint workspace，在 agent Docker 中运行一次。
3. 只收集 `submission/`，不把原仓库加入 runtime `PYTHONPATH`。
4. 在 source-free evaluator capsule 中运行 build、public、hidden 和 isolation gates；
   禁止网络、forbidden imports、submission subprocess 和 evaluator-private path access。
5. functional container 退出后，由 trusted metrics stage 只读计算 compactness；该阶段
   不 import、安装或执行 submission。
6. 保存逐题 `run.json`、`eval/result.json`、submission、trajectory、usage 和日志，再
   重建 suite index。

Runner 必须在模型调用前通过 strict Docker preflight。任何 source、task、evaluator、
visibility 或 attempt-policy 变化都会形成不同实验条件。

## Functional Pass

```text
FunctionalPass =
  BuildPass
  AND PublicTestsPass
  AND HiddenTestsPass
  AND IsolationPass
```

`functional_gate` 为 0/1，一次完整 task attempt 对应一次 Pass@1 观察。兼容字段
`test_pass` 等于 public 与 hidden 的合取，`original_import_pass` 等于 isolation，
`final_score` 等于 `functional_gate`。

Agent completion、step/context limit、rate limit 和 infra failure 必须另列。若 Agent
流程超时但已留下 evaluator 可通过的 submission，Functional 仍为 pass，Agent
completion 为 fail；不能用 `run.status` 覆盖 benchmark correctness。

## Compactness And Cost

Compactness 是 reference-relative 次指标，不与 Functional 相乘：

```text
reference_relative_loc_ratio = submitted_loc / reference_loc
compactness_score = min(1, reference_loc / submitted_loc)
```

同时报告 submitted/reference file count、copied LOC/fraction、runtime dependency、
tokens、API calls、steps 和 time。Reference 是可行紧凑实现，不是数学最小解；
`copied_fraction` 也不能单独支撑 plagiarism claim。

## Execution And Resume Rules

- checkout exact revision，验证 suite/task-set hash、source archives 和 image identities；
- 固定 model revision、agent profile、prompt arm、timeouts、workers 和 attempt policy；
- 先用同一 images、visibility 跑 end-to-end smoke；
- resume 只处理没有 terminal `run.json` 的题；
- 不查看 hidden failure 来调整正在运行的模型或 prompt；
- Main 不向 agent 挂载 benchmark root、tests、reference、Docker socket、host home 或 secrets；
- context、infra、rate-limit、manual intervention 和 rerun exception 单独记账。

## Required Artifacts And Reporting

每个 paper-candidate suite 必须保留：

- exact task IDs、suite/task-set hash、freeze/selection IDs；
- model、agent profile、arm、attempt/resume policy；
- agent/evaluator image identities；
- per-task `run.json`、`eval/result.json`、submission、trajectory、usage/context audit；
- exception ledger 和可复现分析命令。

Primary table 报告 Functional Pass@1、assigned/completed、置信区间和 task-paired
comparison。Secondary table 报告 correctness funnel、compactness、cost 和明确预注册的
slices。不同 source、visibility、attempt 或 evaluator 条件不得并入同一 leaderboard。

当前结果资格和解释边界见 [STATUS.md](STATUS.md)，证据位置见
[reports/README.md](../reports/README.md)。旧版细节保存在
[archive/specs/](archive/specs/README.md)，不再是当前规范。
