# Experiment registry

这个目录是 `experiments/` 的轻量、可提交索引，不替代原始 run。

| 文件 | 用途 |
| --- | --- |
| `inventory.json` | 所有发现的 suite、指标、scope、生命周期和质量标记 |
| `runs.jsonl` | 一行一个 suite，便于脚本、SQL 或 notebook 读取 |
| `data_quality.json` | 旧 summary、绝对路径等已知数据质量问题 |
| `studies/python150-current.json` | core-100 + hard50 的当前同任务集组合视图 |
| `INVENTORY.md` | 给人阅读的生成摘要 |

重建：

```bash
PYTHONPATH=harness python harness/scripts/build_experiment_registry.py
```

生成器优先读取 task-local `eval/result.json` 和 `run.json`。不要手工编辑生成文件；状态规则或 study 组成应修改生成器后重建。
