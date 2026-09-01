# FeatureLiftBench 文档入口

> **Status: current · Last verified: 2026-08-29**

日常只从这里进入。动态数字只维护在 [STATUS.md](STATUS.md)，方法对比结论只维护在
[FINDINGS.md](FINDINGS.md)。**论文主套件是 Python-200'（冻结 150 + Hard-50）**，
整套 Flash 收到包的审计 headline 是 132/200，但只有 183 题启动；17 题 freeze
preflight、16 题离线依赖和 59 题 context 问题去重后形成 84 题严格替换集合。闭环前
没有合格新主表分；旧 150+E50 的 21.5%–72.5% 也不是新主表。题集口径见
[汇报_题集构成.md](汇报_题集构成.md)。

## 权威（先读这些）

| Need | Document |
| --- | --- |
| 当前规模、完成度、可用结果和 blocker | [STATUS.md](STATUS.md) |
| 论文主套件 Hard-50 / Python-200' | [PLAN_HARD50_EXPANSION.md](PLAN_HARD50_EXPANSION.md) · [汇报_题集构成.md](汇报_题集构成.md) |
| 方法结论 | [FINDINGS.md](FINDINGS.md) |
| Main 条件、指标、失败分类 | [EVALUATION.md](EVALUATION.md) |
| 当前 V1（Main + 2M cap） | [METHOD_V1.md](METHOD_V1.md) |
| 出题规则 | [TASK_DESIGN_RULES.md](TASK_DESIGN_RULES.md) |
| source / freeze policy | [BENCHMARK_DESIGN_PRINCIPLES.md](BENCHMARK_DESIGN_PRINCIPLES.md) · [FULL_REPOSITORY_SOURCE_POLICY.md](FULL_REPOSITORY_SOURCE_POLICY.md) |
| 构念 | [BENCHMARK_DESIGN.md](BENCHMARK_DESIGN.md) |

## 运行与仓库

| Need | Document |
| --- | --- |
| 本地或服务器跑实验 | [RUN.md](../RUN.md) · [SERVER_RUNBOOK_PYTHON200.md](SERVER_RUNBOOK_PYTHON200.md) |
| 仓库结构：benchmark × agent × method | [benchmark/](../benchmark/README.md) · [agent/](../agent/README.md) · [method/](../method/README.md) · `benchmark/suites.toml` |
| 整理仓库、删除过时文件 | [REPOSITORY_MAINTENANCE.md](REPOSITORY_MAINTENANCE.md) |
| 脚本归属 | [scripts/README.md](../scripts/README.md) |

正式入口只有 `./scripts/run_benchmark.sh`（或 `featureliftbench` CLI）。
`--benchmark python200_hard`。不要用 `run_python200_paper.sh` 写新主表。

## 进行中的诊断（不进主表）

| Need | Document |
| --- | --- |
| RQ6 Public-feedback | [METHOD_RQ6_PUBLIC_FEEDBACK.md](METHOD_RQ6_PUBLIC_FEEDBACK.md) |
| Hidden 合同出处审计 | [HIDDEN_CONTRACT_PROVENANCE.md](HIDDEN_CONTRACT_PROVENANCE.md) |
| repository recoverability | [AGENTIC_EVIDENCE_AUDIT.md](AGENTIC_EVIDENCE_AUDIT.md) |
| DeepSeek Harness / Codex runtime | [METHOD_AGENT_RUNTIME.md](METHOD_AGENT_RUNTIME.md) |
| AutoSaddler-FLB prompt-pack 筛选 | [METHOD_AUTOSADDLER.md](METHOD_AUTOSADDLER.md) · [integrations/](../integrations/README.md) |
| token 尾巴（离线拆轨迹，不是新方法） | [TOKEN_UTILITY.md](TOKEN_UTILITY.md) |

## 组会稿（derived）

数字冲突以 STATUS 为准，不要当第二份权威。

| Need | Document |
| --- | --- |
| 跨模型 Main / 方法对比 / 失败阶段 / 题集 / 案例 | [汇报_Python200跨模型Main.md](汇报_Python200跨模型Main.md) · [汇报_实验结果表.md](汇报_实验结果表.md) · [汇报_失败原因.md](汇报_失败原因.md) · [汇报_题集构成.md](汇报_题集构成.md) · [汇报_Agent瓶颈案例.md](汇报_Agent瓶颈案例.md) |
| 导师组会：Benchmark + 分析论文定位 | [汇报_导师_benchmark分析论文.md](汇报_导师_benchmark分析论文.md) · [2026-08-31 修订稿（含完整方法与 Self-Harness）](FLB论文_导师汇报_20260831.md) |

## 计划

| Need | Document |
| --- | --- |
| Hard-50 选题矩阵 | [hard50_selection_matrix.md](hard50_selection_matrix.md) |
| External-50 合同升格（一天执行已完成；copy-all / 独立 freeze 仍见该文） | [PLAN_EXTERNAL50_TO_PYTHON150_QUALITY.md](PLAN_EXTERNAL50_TO_PYTHON150_QUALITY.md) |
| 旧 External-50 扩题计划 | [PLAN_EXTERNAL50_EXPANSION.md](PLAN_EXTERNAL50_EXPANSION.md)（兼容指针，不是执行入口） |

过期方法记录、Rescue+ / V2 负结果和旧组会稿在 [archive/](archive/README.md)。
schema、taxonomy 和语言轨道在 [reference/](reference/README.md)。实验审计在
[reports/README.md](../reports/README.md)；原始运行在 `experiments/`。

当前结果只使用 Functional Pass Rate 和 pass-conditioned / paired RRES 作核心指标。
历史 `summary.passed` 不得代替 evaluator `functional_gate`。当前 **V1 = Main + 2M
cap**，见 [METHOD_V1.md](METHOD_V1.md)。FINDINGS 中的 DeepSeek Python-200 对比仍含
已退役 Lite V1 协议（Main 预算 120 步），不是 Frozen 45 步信封，也不是当前 V1。

不再迭代 Rescue+、V2、TFL 或其它脚手架。Artifact-aware / recency / pre-submit
audit 与 verification-aware 的筛选已停，不要扩到 200。RQ6 Public-feedback
Flash-12 同日成对已齐（Main 0/12 → 4/12），见
[METHOD_RQ6_PUBLIC_FEEDBACK.md](METHOD_RQ6_PUBLIC_FEEDBACK.md)。Spec-adversarial
Hidden-4 已 Kill（Hidden 0→1 = 0/4），见
[archive/methods/METHOD_SPEC_ADVERSARIAL.md](archive/methods/METHOD_SPEC_ADVERSARIAL.md)。论文 RQ3/RQ5
token 切片已有稿；RQ6 机制稿见
[paper/04_results_rq6.md](paper/04_results_rq6.md)。数字不进 Python-200 主表。
DeepSeek Harness / Codex runtime ablation 只有基础设施，见
[METHOD_AGENT_RUNTIME.md](METHOD_AGENT_RUNTIME.md)，同样不进主表。

写论文：[paper/](paper/README.md) · RQ3/RQ5 [paper/03_results_token_utility.md](paper/03_results_token_utility.md) · RQ6 [paper/04_results_rq6.md](paper/04_results_rq6.md)。

修改文档后运行：

```bash
python3.12 scripts/check_docs.py --warnings-as-errors
```
