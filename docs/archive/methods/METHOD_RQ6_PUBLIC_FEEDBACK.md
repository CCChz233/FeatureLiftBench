# RQ6 Public-feedback

> **Status: archived · Last verified: 2026-09-02**
> 本文件是 **RQ6 Public-feedback** 信息消融的唯一规范。不是新 agent 方法，
> 数字不进 Python-200 主表。解释见 [FINDINGS.md](../../FINDINGS.md)；论文稿见
> [paper/04_results_rq6.md](../../paper/04_results_rq6.md)。
> Flash-12 同日成对 **已冻结**。不要扩到 Python-200'。

## 定义

同一 128k Main 信封，**只改一项**：把 `public_tests/` 挂进 Agent workspace，
并允许 `PYTHONPATH=submission pytest public_tests/`。Hidden 始终只在提交后由
evaluator 运行。

| 维度 | Main 对照 | Public-feedback |
| --- | --- | --- |
| Prompt | `standard` | 同左 |
| Context / reserved | 131072 / 8192 | 同左 |
| Max steps | 120 | 同左 |
| Total token cap | **无** | 同左 |
| Condenser | `token` / LLM summary | 同左 |
| Source hints | 无 | 无 |
| `public_tests/` | 不挂载 | **挂载** |
| Hidden | evaluator-only | evaluator-only |
| Runtime `ablation_arm` | `main` | `public_feedback` |

不要叠 Entrypoint-Hint、Pruned-Context、Short-prompt、verification-aware、
artifact-aware、recency、pre-submit audit、checker 或 repair。
`run_python200_paper.sh --execute` 会拒绝 `mount_public_tests`。

机器可读冻结：[`harness/config/methods/rq6_public_feedback.json`](../../../harness/config/methods/rq6_public_feedback.json)。

## 切片

Flash-12：从 Flash Main-200（本地 0812 与 API 的交集）各取 6 道
`public_failure` 与 6 道 `hidden_failure`。清单
[`rq6_public_feedback_flash12_v1.txt`](../../../harness/config/experiments/rq6_public_feedback_flash12_v1.txt)。

同日必须重跑这 12 题的 Main。不得用数周前的 145/200 套件当 n=12 对照。

## 读出

主指标仍是 evaluator `functional_gate`，外加失败阶段翻转：

| 翻转 | 解释 |
| --- | --- |
| public 0→1，hidden 仍 0 | 反馈有用，Hidden 仍难（构念对齐） |
| hidden 也大量 0→1 | 先查泄漏（public 测试是否过近 Hidden） |
| 两层都不动 | 看见 public 测试帮不了 Flash |

功能分高于同日 Main **不**替代 Python-200 主表。

## 怎么跑

Flash-12 **不要重跑**。若复现同一臂，用 catalog 方法而不是已删除的
`./logs/run_rq6_public_feedback_deepseek_flash.sh`：

```bash
./scripts/run_benchmark.sh --benchmark python200_hard --agent openhands --method main \
  --task-file harness/config/experiments/rq6_public_feedback_flash12_v1.txt
./scripts/run_benchmark.sh --benchmark python200_hard --agent openhands --method public_feedback \
  --task-file harness/config/experiments/rq6_public_feedback_flash12_v1.txt
```

历史切片落在旧 150+E50 题单上；不要把复现写成新的 Python-200' RQ6。
`run_python200_paper.sh --execute` 仍会拒绝 `mount_public_tests` 全量 200。

比较：

```bash
PYTHONPATH=harness python3 harness/scripts/compare_rq6_public_feedback.py \
  experiments/ablations/public_feedback/<pair>/main \
  experiments/ablations/public_feedback/<pair>/public_feedback
```

## 当前证据（Flash-12 已齐）

套件：`experiments/ablations/public_feedback/flash12-deepseek-v4-flash-20260819-220335/`。
快照：[`rq6_public_feedback_flash12_20260820.json`](../../../artifacts/research_analysis/current_results/rq6_public_feedback_flash12_20260820.json)。

- 端点：DeepSeek API Flash；信封如上。挂载完整性：Main 12/12 未挂，Public-feedback 12/12 已挂。
- 同日 Main：**0/12** `functional_gate`。`bleach` 无 submission，Main 未评测。
- Public-feedback：**4/12**（+4）。不进 Python-200 主表。

| 模式 | 题 | 读出 |
| --- | --- | --- |
| public 0→1，hidden 仍 0 | alembic, click, flask | 反馈有用，Hidden 仍难 |
| public 0→1，Main 上 hidden 已是 1 → gate 0→1 | decorator, filelock | 补的是 public 合同，不是 Hidden 泄漏 |
| public 0→1 且 hidden 0→1 | yamale | public 失败题上 Hidden 也被带过；先记，不当“大量泄漏” |
| public 已 1，hidden 0→1 → gate 0→1 | wheel | hidden 失败题上 Hidden 被带过；1/5 成对 |
| 两层都不动 | parse, pygments, python_decouple, schema | 看见 public 测试抬不动 Hidden |
| 不成对 | bleach | Main 无 eval；PF 仍 public 0 / hidden 0 |

public 失败组 6/6 都把 public 救回来。hidden 失败组成对 5 题里 4 题 Hidden 不动。hidden 0→1 只有 2 题（yamale、wheel），不是“大量 Hidden 被测穿”。
