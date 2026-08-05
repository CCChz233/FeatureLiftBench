# Experiment Registry

> **Documentation status: reference · Last verified: 2026-08-04**

这是 `experiments/` 的轻量、可提交索引，不替代原始 run。

| File | Purpose |
| --- | --- |
| `inventory.json` | 全部发现的 suite、scope、category、lifecycle 和质量标记 |
| `runs.jsonl` | 一行一个 suite |
| `data_quality.json` | summary、绝对路径、缺失 eval 和重复 run ID 等问题 |
| `path_aliases.json` | 2026-08-04 物理整理的 old→new longest-prefix mapping |
| `bundle_ledger.json` | bundle SHA256、移动、保留和验证删除记录 |
| `studies/python150-current.json` | 历史 mixed-snapshot 组合视图 |
| `INVENTORY.md` | 人类可读生成摘要 |

Category：`leaderboard`、`calibration`、`smoke`、`method`、`validation`。同名
`run_id` 可以存在于不同 raw path，registry 使用 `record_id=raw_path` 区分，并在
data-quality 中显式列出重复项。

重建：

```bash
PYTHONPATH=harness python3 harness/scripts/build_experiment_registry.py
```

生成器优先读取 task-local `eval/result.json` 和 `run.json`。不要手工修改生成文件。
