# Obligation-Guided Feature Lifting

> **Status: screening · Not started · Last verified: 2026-09-06**
> 本文件是 **Obligation-Guided Feature Lifting** 的唯一规范。不是 Official Main，
> 数字不进 Python-150 / Python-200 主表。未过停线前不要开 method section。

## 定义

从公开合同生成冻结 obligation ledger。Agent 在 finish 前为每一行补上
**repo evidence** 和 **implementation evidence**。重点不是多测试。

```text
Contract → Obligations → Evidence → Implementation → Coverage Audit
```

| 维度 | Main 对照 | Obligation-Guided |
| --- | --- | --- |
| Prompt | `standard` | 同左 + 短 appendix |
| Context / reserved | 131072 / 8192 | 同左 |
| Max steps | 120 | 同左 |
| Total token cap | **无** | 同左 |
| Condenser | `token` / LLM summary | 同左 |
| Source hints | 无 | 无 |
| `public_tests/` | 不挂载 | 不挂载 |
| Hidden | evaluator-only | evaluator-only |
| Workspace extras | 无 | `obligation_ledger.json` |
| Checker / finish intercept | 无 | **无** |
| Runtime `ablation_arm` | `main` | `obligation_guided` |

机器可读冻结：[`harness/config/methods/obligation_guided.json`](../harness/config/methods/obligation_guided.json)。

Ledger 列：`requirement`、`repo_evidence.path`、`implementation.path`、
`verification`（只允许路径引用：`?` 或 `cited`）。Harness 只从
`metadata.public_spec` 的 `required_api` 与 `Bxxx`（含 isolation）开槽。
禁止 scenario stub、`run_contract_check.py`、pytest 合同矩阵、CCG finish 闸门。

## 与已 Kill 臂的差别

| 臂 | 差别 |
| --- | --- |
| Spec-adversarial | 可执行 stub + checker；本臂没有测试 |
| Pre-submit audit | 自然语言 covered/gap；本臂要求仓库路径 + 实现路径 |
| Verification-aware | 压缩自测 transcript；本臂不改 condenser |
| CGVL | 硬 finish 闸门 + 断言格；本臂过程指标 only |

## 切片与停线

从 Python-150 freeze v2 的 **Flash 有包失败** 中抽 30 题：15 Public 首败 +
15 Hidden 首败。默认不混 Pro，以便对照是同一模型的归档 Main。优先纳入
`contract_api_completion`；Hidden 池若不足 15 条非 packaging，才保留 packaging
行。Seed：`obligation-guided-pilot30-v1`。

生成（不跑 Agent）：

```bash
PYTHONPATH=harness python3 harness/scripts/sample_obligation_guided_pilot30.py --write
```

清单：[`harness/config/experiments/obligation_guided_pilot30_v1.txt`](../harness/config/experiments/obligation_guided_pilot30_v1.txt)。
缺注释 CSV / suite 时脚本失败，**不得手填题号**。

主指标仍是 evaluator `functional_gate` rescue（Main 0 → OG 1）：

| 结果 | 动作 |
| --- | --- |
| rescue ≤ **3/30** | **停**。Discussion：simple obligation tracking alone does not close the gap |
| rescue ≥ **8/30** 且至少一题 `behavior_drift` 翻盘 | 可考虑扩大；仍不是主表行 |
| 只救缺导出、drift 不动 | 记负结果，不要当瞄准最大失败模式 |

不要 Python-150 全量，不要叠 Entrypoint-Hint / Public-feedback / Spec-adversarial /
CCG / verification-aware。`run_python200_prime_paper.sh --execute` 必须拒绝本臂。

## 怎么跑（手动；本仓库实现不自动启动 suite）

Flash、同一 128k 信封。Main 可用归档 `python200-prime-v2-main-r1` 在 150 题上的
失败行作对照；若要同日对照，再跑同一 30 题 Main。

```bash
PYTHONPATH=harness python3 -B -m featureliftbench.cli run-agent benchmark/tasks \
  --agent openhands \
  --agent-profile openhands_deepseek_v4_flash_obligation_guided \
  --env-file .env \
  --eval-docker \
  --output experiments/methods/obligation_guided/<date>/obligation_guided \
  --task-file harness/config/experiments/obligation_guided_pilot30_v1.txt
```

比较：

```bash
PYTHONPATH=harness python3 harness/scripts/compare_obligation_guided_pilot30.py \
  experiments/python/openhands/deepseek-v4-flash/python200-prime-v2-main-r1 \
  experiments/methods/obligation_guided/<date>/obligation_guided
```

过程指标落盘：`agent/obligation_guided_audit.json`。
