# evidence/

> **Documentation status: reference · Last verified: 2026-08-29**

历史 **出题 gate** 证据（oracle / naive / copy_all 等），不是 Agent 主榜，也不是
Hard-50 Flash 校准。

| 目录 | 放什么 |
| --- | --- |
| `evidence/` | 出题期 gate（本目录） |
| `experiments/python/` | OpenHands / runtime 模型 run |
| `experiments/validation/` | Hard-50 校准、oracle 重跑、agentic-evidence 原料 |
| `reports/` | 可审查的派生摘要 |

```text
evidence/
  python/batch1/<task_id>/review/   # 历史 Python gate
  go/go-pilot/<task_id>/review/     # Go pilot gate
```

生成命令：

```bash
bash harness/scripts/run_batch1_review.sh <task_id>
bash harness/scripts/run_go_pilot_review.sh <task_id> --docker
python harness/scripts/generate_gate_report.py --all-batch1
python harness/scripts/generate_go_gate_report.py <task_id>
```

当前 release 事实见 [`docs/STATUS.md`](../docs/STATUS.md)。Python-150 工程门见
`reports/audits/v3_main_readiness.md`。不要往本目录写入新的 OpenHands 主榜或
method pilot。
