# Go Pilot 出题标准流程（Playbook）

**最后更新：** 2026-07-03

Go track **10 gold** 阶段的唯一执行标准。政策见 [GO_EXPANSION.md](GO_EXPANSION.md)；格式见 [GO_TASK_FORMAT.md](GO_TASK_FORMAT.md)。

| 层级 | 文档 | 作用 |
| --- | --- | --- |
| **执行（本文）** | [GO_PILOT_PLAYBOOK.md](GO_PILOT_PLAYBOOK.md) | 七步流程、gate、命令、promote |
| 政策 | [GO_EXPANSION.md](GO_EXPANSION.md) | 10 gold → 100、论文骨架 |
| Harness | [GO_HARNESS_PLAN.md](GO_HARNESS_PLAN.md) | Phase 0 工程清单 |
| 仓库池 | [GO_REPO_SELECTION.md](GO_REPO_SELECTION.md) | Go repo 接受标准与浓度 |
| 质量评审 | [GO_QUALITY_RUBRIC.md](GO_QUALITY_RUBRIC.md) | 入榜客观标准 |
| 候选台账 | [go_candidate_backlog.md](go_candidate_backlog.md) | shortlist 与状态 |
| 设计 | [go_task_designs/TEMPLATE.md](go_task_designs/TEMPLATE.md) | 单题设计笔记 |
| 格式 | [GO_TASK_FORMAT.md](GO_TASK_FORMAT.md) | metadata、目录、测试 |
| 契约 | [BENCHMARK_SPEC.md](BENCHMARK_SPEC.md) §11 | 论文/复现 |

**硬性约束：**

- Python `benchmark/tasks/` **冻结**，Go 题只进 `benchmark/go/`
- 无 oracle 不进 `benchmark/go/tasks/`
- Phase 1：**一次一题**；Phase 2：每批最多 3 题，每题独立 evidence
- **functional pass 不是 promote 充分条件**；必须 oracle/naive/copy_all/probe/Flash 分层
- Phase 0 harness DoD 未完成前，不得 promote

---

## 总览：七步流程

```text
Step 0  选 Go 仓库 / shortlist（GO_REPO_SELECTION + go_candidate_backlog）
Step 1  Design spike（docs/go_task_designs/<task_id>.md）
Step 2  创建 staging（benchmark/go/staging/<task_id>/）
Step 3  Oracle closure（benchmark/submissions/<task_id>/oracle/）
Step 4  Naive + copy_all baseline
Step 5  本地验证（validate / audit / eval / probes）
Step 6  Flash 单题校准（deepseek_v4_flash）
Step 7  Promote / Redesign / Drop → benchmark/go/tasks/
```

---

## Agent 接管模式

```text
while gold_count < 10:
  1. 取 go_candidate_backlog 下一项 shortlist
  2. 写/更新 go_task_designs/<task_id>.md
  3. 生成 staging + oracle/naive/copy_all
  4. 跑全部 gate → gate_report.json
  5. decision.md
  6. promote → 更新 catalog；否则 redesign（≤2 轮）或 drop
```

**Evidence Packet：**

```text
experiments/go-pilot/<task_id>/review/
  gate_report.json
  decision.md
  validate-task.log
  audit-output-imports.log
  module-probes.log
  oracle/result.json
  naive/result.json
  copy_all/result.json
  flash/run.json
```

`gate_report.json` 格式与 Python batch-1 相同（见 [BATCH1_PLAYBOOK.md](../BATCH1_PLAYBOOK.md)），`experiments/batch1/` 改为 `experiments/go-pilot/`。

---

## 客观 Gate 常量

| Gate | 客观条件 |
| --- | --- |
| G0 task shape | `validate-task` exit 0；`audit_output_imports.py --fail-on-gap` exit 0 |
| G1 oracle | `status=passed`；public+hidden pass；`functional_gate=1.0`；`0.20 <= extraction_ratio <= 0.60` |
| G2 naive | public pass；hidden fail；`functional_gate=0.0`；`extraction_ratio <= 0.10` |
| G3 copy_all | pass；`extraction_ratio >= 0.85`；delta vs oracle `>= 0.25` |
| G4 probes | `verify_module_probes.py --verify-oracle`；≥3 probe |
| G5 Flash | 至少一次 `deepseek_v4_flash`；记录 A/B/C |
| G6 docs | design note、backlog、Go catalog 一致 |

Metric exceptions 同 Python：`low_oracle_extraction_A_tier_exception`、`copy_all_metric_exception`（登记在 `gate_report.json`）。

---

## Step 0 — 选题

1. 读 [GO_REPO_SELECTION.md](GO_REPO_SELECTION.md) — repo 是否值得占用 Go 名额
2. 读 [go_candidate_backlog.md](go_candidate_backlog.md) — 取 `status=shortlist` 项
3. **先选 repo，再切 feature slice**

**Repo gate：**

| 维度 | 要求 |
| --- | --- |
| 真实使用 | 知名 Go OSS；`go.mod` 可 pin；license 清晰 |
| 可切片 | 存在可独立复用的 API（非仅 CLI） |
| 缠绕 | 多 package / internal / init / 全局状态至少其一 |
| 体量 | 非单文件工具；oracle 不必 vendor 整仓 |
| 离线测试 | 可无网络写 table-driven tests |
| 不重复 | 不与已有 Go/Python 题同源同 API |

**Pilot 首题建议：** backlog 中 `priority=P0` 且 harness 风险低（纯 stdlib 测试、无 cgo）。

---

## Step 1 — Design spike

复制 [go_task_designs/TEMPLATE.md](go_task_designs/TEMPLATE.md) → `docs/go_task_designs/<task_id>.md`。

必填：Why、Practical reuse、Source、Entanglement、Target API、Included/Excluded、Test plan、Go/No-Go（入榜决策，非 Go 语言）。

**Design gate：** 另一人（或 Agent 第二遍）能仅凭 design note 说出 oracle 大约多少 `.go` 文件、naive 会漏什么 hidden。

---

## Step 2 — 创建 staging

```bash
mkdir -p benchmark/go/staging/<task_id>/{repo,evaluation/public_tests,evaluation/hidden_tests,environment}
cp docs/go_task_designs/<task_id>.md  # 人类参考，不进 staging
```

填写 `metadata.json`、`TASK.md`、`environment/go.mod`（harness module）。

---

## Step 3 — Oracle

```bash
PYTHONPATH=harness python harness/scripts/build_oracle_submission.py \
  --task benchmark/go/staging/<task_id> \
  --output benchmark/submissions/<task_id>/oracle
```

手工调整至 G1 预期；**禁止** submission import 原 module path。

---

## Step 4 — Baselines

| 变体 | 意图 |
| --- | --- |
| naive | 只看 public 的浅实现；public 过、hidden 挂 |
| copy_all | 大段复制/重导出；functional 可能过但 extraction 高 |

```bash
# 模板生成后人工裁剪
cp -r benchmark/submissions/<task_id>/oracle benchmark/submissions/<task_id>/naive
# 删减至 naive 策略...
```

---

## Step 5 — 本地验证

```bash
export PYTHONPATH=harness

python -m featureliftbench.cli validate-task benchmark/go/staging/<task_id>

python -m featureliftbench.cli audit_output_imports benchmark/go/staging/<task_id> \
  benchmark/submissions/<task_id>/oracle --fail-on-gap

python -m featureliftbench.cli eval benchmark/go/staging/<task_id> \
  benchmark/submissions/<task_id>/oracle \
  --output experiments/go-pilot/<task_id>/review/oracle --docker

python -m featureliftbench.cli eval benchmark/go/staging/<task_id> \
  benchmark/submissions/<task_id>/naive \
  --output experiments/go-pilot/<task_id>/review/naive --docker

python -m featureliftbench.cli eval benchmark/go/staging/<task_id> \
  benchmark/submissions/<task_id>/copy_all \
  --output experiments/go-pilot/<task_id>/review/copy_all --docker

python harness/scripts/verify_module_probes.py \
  --task benchmark/go/staging/<task_id> \
  --submission benchmark/submissions/<task_id>/oracle \
  --verify-oracle
```

> **注意：** Phase 0 完成前，上述 `eval` 可能失败——先完成 [GO_HARNESS_PLAN.md](GO_HARNESS_PLAN.md)。

---

## Step 6 — Flash 校准

```bash
PYTHONPATH=harness python -m featureliftbench.cli run-agent benchmark/go/staging/<task_id> \
  --model deepseek_v4_flash \
  --output experiments/go-pilot/<task_id>/flash \
  --docker
```

| Tier | 含义 |
| --- | --- |
| A | public 过、hidden 挂，或靠大闭包低 final |
| B | 近 oracle extraction 仍 pass |
| C | 低 extraction 或 public 硬编码过 hidden → redesign/drop |

---

## Step 7 — Promote / Redesign / Drop

**Promote：**

```bash
git mv benchmark/go/staging/<task_id> benchmark/go/tasks/<task_id>
```

更新：

- `docs/go_candidate_backlog.md` → `accepted`
- `docs/benchmark_tasks.md` Go 分区
- `experiments/go-pilot/<task_id>/review/decision.md`

**Redesign：** ≤2 轮；记录 blocking_gates。

**Drop：** reuse 不成立或 G3 拉不开；backlog 标 `dropped` 并写原因。

---

## 10 Gold 完成检查单

Phase 2 收尾时，确认：

- [ ] `benchmark/go/tasks/` 恰好 **10** 题（或文档登记例外）
- [ ] 每题有 `experiments/go-pilot/<task_id>/review/gate_report.json` 且 `decision=promote`
- [ ] ≥ **8** 个唯一 source repo（10 题中）
- [ ] Flash A/B/C 分布写入 `docs/go_pilot_acceptance_report.md`（可新建）
- [ ] 无题依赖 cgo / 网络
- [ ] [GO_HARNESS_PLAN.md](GO_HARNESS_PLAN.md) DoD 全勾
- [ ] 论文方法节可引用 10 题案例表

---

## 扩到 100（Phase 3 预告）

10 gold  playbook 稳定后：

1. 将 `go_candidate_backlog` 扩至 60+ repo 候选
2. 允许 Agent 并行 staging，但 **promote 仍逐题 gate**
3. 浓度限制见 [GO_REPO_SELECTION.md](GO_REPO_SELECTION.md)
4. 不修改本 playbook 的 G0–G4 常量

---

## 命令速查

| 动作 | 命令 |
| --- | --- |
| 健康检查（未来） | `bash harness/scripts/check_run_health.sh experiments/go-pilot/<run_id>` |
| 单题 oracle | 见 Step 5 |
| Windows | 在 WSL 内执行；见 [WINDOWS.md](WINDOWS.md) |
