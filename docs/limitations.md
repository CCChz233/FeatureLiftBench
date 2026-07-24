# Known Limitations

FeatureLiftBench 的已知局限与评估边界。论文 Limitations 节以此为基础；设计前提见 [BENCHMARK_DESIGN.md](BENCHMARK_DESIGN.md)；实现细节见 [03_evaluator_and_scoring.md](03_evaluator_and_scoring.md)。

## Benchmark design

- **Curated tasks.** 题目人工筛选与设计，不能代表所有「从仓库抽功能」场景。
- **Python-heavy main split.** 当前 experiment-ready main 为 Python 150
  题；独立人工审核尚未完成，因此 paper-ready 发布仍待定。Go split 仍在
  calibration，不宜与 Python headline 数字直接对比。
- **Feature type skew.** Python 题集中 parser、validator、config loader、plugin/registry 等可离线测试能力；并发、IO-heavy、分布式场景覆盖有限。
- **Hard-only main.** 主榜不含 easy/medium 校准梯；难度比较依赖 agent 分层与 extraction 指标，而非多级 split。
- **Spec migration (2026-07).** 宪法工程已落地（validate / render / migrate CLI），主榜已达 **150/150 engineering-compliant**、0 legacy，并完成迁移后 Oracle 复验。但独立人工 paper-gold 审核仍为 0/150；历史 legacy 模型结果与 compliant rerun **不得混报**。见 [CONSTITUTION_MIGRATION.md](CONSTITUTION_MIGRATION.md)。
- **Human review gap.** 当前自动内容审计为完整非模板化契约
  **150/150**、experiment-ready **150/150**；独立人工审核仍为
  **0/150**。因此可以运行正式模型实验，但不能宣称 paper-ready
  adjudicated benchmark。
- **Repository evidence availability.** 默认 Main 鼓励 Agent 自己发现、改写和
  编写测试；48/150 当前源码快照含可发现的上游测试文件。该比例是 Agent
  可用证据统计，不是合格门槛，因为 benchmark 明确评估 Agent 自行发现或构造
  验证用例的能力。
- **Public feedback asymmetry.** 默认 Main 在提交前不暴露任何 Benchmark
  evaluator tests；Public-feedback 是显式挂载基础 evaluator tests 的对照臂。
  历史结果中的 `Main`/`No-public` 使用旧命名，比较时必须按真实可见性重标。
- **Attribution evidence.** 550-run 失败归因为 entrypoint-conditioned OpenHands 上的自动启发式观察，待人工复核，非严格因果分解。

## Evaluation and scoring

- **Hidden tests are deeper coverage of the public contract, not a secret second spec**（宪法要求）；若题面违规引入未声明义务，则属出题错误而非 Agent 能力。
- **Compactness proxy.** `extraction_ratio` 可能惩罚合理 closure，也可能漏检语义 over-copy；**不是**最小闭包证明。
- **Functional gate is binary.** Build + tests + forbidden-import 全过才计分；部分正确提取与 compact 失败无法细分 partial credit。
- **Reference LOC variability.** `oracle_loc` / reference closure 并非每题都完整填充；compactness 跨题比较需结合 task-local manifest。
- **Path leakage checks.** 禁止 import 原仓库路径；symlink、动态 import、资源路径等检测随 harness 演进，未必覆盖所有绕过方式。

## Oracle and baselines

- **Oracle is a construction baseline, not ground truth.** Oracle submission 由 harness 构建；relocation、vendor、grammar resource 等规则迭代会影响「可复现 oracle」而非 task 语义本身。
- **Versioned quarantine.** 历史 freeze 可能含 quarantine 题；aggregate 必须使用当前 [STATUS.md](STATUS.md) 中的 freeze 与 ledger 口径。

## Annotations and paper release

- **AI-assisted annotations.** v1.1 behavior contracts、closure gold、taxonomy 含 AI-assisted 行；在独立人工审阅完成前，不能写成 human gold。
- **Pilot scope.** ECSM Pilot-10 用于机制诊断，不能外推 Python150 总体表现；Pilot 执行另受数据导出授权约束。

## Agent and runtime

- **Docker boundary.** Agent/eval 默认 Docker 隔离；宿主机路径、网络、资源限制与真实 IDE 环境可能不同。
- **Model and harness coupling.** 分数依赖 agent 框架（如 OpenHands）、模型版本与 prompt；跨 run 比较需冻结 [paper_runs_frozen.md](paper_runs_frozen.md) 中的 run ID。

## Related

- 失败标签：[05_failure_taxonomy.md](05_failure_taxonomy.md)
- 当前 gate 状态：[STATUS.md](STATUS.md) · [research_analysis/V11_IMPLEMENTATION_STATUS.md](research_analysis/V11_IMPLEMENTATION_STATUS.md)
