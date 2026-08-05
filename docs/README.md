# FeatureLiftBench 文档入口

> **Status: current · Last verified: 2026-08-04**

日常只需要从以下文档进入：

| Need | Document |
| --- | --- |
| 看当前规模、完成度、可用结果和 blocker | [STATUS.md](STATUS.md) |
| 看现有实验结果能/不能说明什么 | [FINDINGS.md](FINDINGS.md) |
| 本地或服务器开始跑实验 | [RUN.md](../RUN.md) · [SERVER_RUNBOOK_PYTHON200.md](SERVER_RUNBOOK_PYTHON200.md) |
| 理解 benchmark 构念 | [BENCHMARK_DESIGN.md](BENCHMARK_DESIGN.md) |
| 设计或审核 task | [TASK_DESIGN_RULES.md](TASK_DESIGN_RULES.md) |
| 确认 source/freeze policy | [BENCHMARK_DESIGN_PRINCIPLES.md](BENCHMARK_DESIGN_PRINCIPLES.md) · [FULL_REPOSITORY_SOURCE_POLICY.md](FULL_REPOSITORY_SOURCE_POLICY.md) |
| 确认 Main、ablation、评分和结果留存 | [EVALUATION.md](EVALUATION.md) |
| 写论文 | [paper/](paper/README.md) |

补充 schema、lifecycle、taxonomy、语言轨道和生成分析集中在
[reference/](reference/README.md)；过期方法、计划、runbook 和旧规范集中在
[archive/](archive/README.md)。实验与审计证据由 [reports/README.md](../reports/README.md)
索引，原始运行保留在 `experiments/`。

`PLAN_EXTERNAL50_EXPANSION.md` 仅为旧 design cards 保留兼容路径，不是当前执行入口。
动态数字只维护在 `STATUS.md`。修改文档后运行：

```bash
python3 scripts/check_docs.py --warnings-as-errors
```
