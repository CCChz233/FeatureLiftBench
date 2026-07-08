# evidence/

**出题 gate 证据**（oracle / naive / copy_all / flash 校准），不是 agent 主榜跑分。

与 `experiments/`（OpenHands 结果）分离。

```text
evidence/
  python/batch1/<task_id>/review/   # Python 100 题 gate
  go/go-pilot/<task_id>/review/     # Go pilot gate
```

生成命令：

```bash
bash harness/scripts/run_batch1_review.sh <task_id>
bash harness/scripts/run_go_pilot_review.sh <task_id> --docker
python harness/scripts/generate_gate_report.py --all-batch1
python harness/scripts/generate_go_gate_report.py <task_id>
```
