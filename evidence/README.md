# evidence/

> **Documentation status: reference · Last verified: 2026-08-04**

历史出题 gate 证据（oracle / naive / copy_all / Flash 校准），不是 v2
Agent 主榜跑分。

与 `experiments/`（OpenHands 结果）分离。

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

当前 v2 release 证据见 `reports/audits/v2_main_readiness.*`、
`reports/audits/v2_oracle_revalidation/` 和 active benchmark freeze。
