# Known Limitations

FeatureLiftBench 的已知局限与评估边界。论文 Limitations 节以此为基础；实现细节见 [03_evaluator_and_scoring.md](03_evaluator_and_scoring.md)。

## Benchmark design

- **Curated tasks.** 题目人工筛选与设计，不能代表所有「从仓库抽功能」场景。
- **Python-heavy main split.** 当前 paper-ready main 为 Python 150 题；Go split 仍在 calibration，不宜与 Python  headline 数字直接对比。
- **Feature type skew.** Python 题集中 parser、validator、config loader、plugin/registry 等可离线测试能力；并发、IO-heavy、分布式场景覆盖有限。
- **Hard-only main.** 主榜不含 easy/medium 校准梯；难度比较依赖 agent 分层与 extraction 指标，而非多级 split。

## Evaluation and scoring

- **Hidden tests are approximations.** Hidden tests 检验行为保真与反过拟合，但不是完整形式化规约；public–hidden gap 仍可能出现。
- **Compactness proxy.** `ExtractionRatio = submitted_LOC / source_LOC` 可能惩罚合理 closure，也可能漏检语义上的 over-copy；copy-all baseline 用于缓解但不能完全消除。
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
