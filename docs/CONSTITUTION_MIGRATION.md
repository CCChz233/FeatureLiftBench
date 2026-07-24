# 规格宪法迁移手册

**状态：** 2026-07-24 · 工程已落地 · **150/150 engineering-compliant**（0 legacy）

**上位规范：** [TASK_DESIGN_RULES.md](TASK_DESIGN_RULES.md) · [BENCHMARK_DESIGN.md](BENCHMARK_DESIGN.md)

本文说明如何把主榜任务从 **legacy 双轨规格** 迁到 **`public_spec` 合规**，以及如何分报实验结果。

---

## 1. 当前进度

| 项 | 状态 |
| --- | --- |
| Schema / hash | ✅ `harness/featureliftbench/task_spec.py` |
| 生成器 | ✅ `task_render.py`：`render(public_spec) → TASK.md` |
| 宪法校验 | ✅ `constitution_validate.py`；`validate-task` 对 compliant 自动启用 |
| 迁移 CLI | ✅ `migrate-task-spec` / `render-task` / `annotate-spec-status` |
| 合规统计 | ✅ `scripts/report_spec_compliance.py` |
| 试点三题 | ✅ 见下表 |
| Hard-50 批次 | ✅ 50/50 validate + Oracle functional gate |
| Core-100 两批 | ✅ 100/100 validate + Docker Oracle functional gate |
| Python 主榜 | ✅ 150/150 compliant；0 legacy |

### 已 compliant 试点

| task_id | 历史 hidden 重判要点 |
| --- | --- |
| `isort__settings_resolver_core__hard3_001` | `ProfileDoesNotExist` 写入 `required_api` |
| `transitions__state_machine_core__hard3_001` | `model.parent.state` 写入 behavior **B004** |
| `scrapy__item_loader_core__hard3_001` | 未定义字段 `KeyError` 写入 behavior **B006** |

冻结合规清单：
[spec_compliance_frozen_20260724.csv](../reports/audits/spec_compliance_frozen_20260724.csv)

全量 150 题协议就绪度：
[new_protocol_readiness.md](../reports/audits/new_protocol_readiness.md)

Oracle 与 spec 的冻结标识见
[STATUS.md](STATUS.md)；原始运行目录和模型实验结果不纳入代码仓库。

> 全部 150 题的 `manual_review` 明确标注为 AI 辅助逐题审核，`independent_human_review: false`。这满足当前工程迁移与可执行门禁，但不冒充独立人工 paper-gold。

---

## 2. 合规定义（过关标准）

一道题标 **`spec_status: compliant`** 须同时满足：

1. `metadata.public_spec` 为唯一 Agent 可见契约（完整 `required_api` surface + 可观察 behaviors）
2. 包内 `TASK.md` = `render(public_spec)`，且 `spec_hash` / `generated_task_hash` 一致
3. `metadata.evaluation_spec` 完成双向覆盖（required API/behavior ↔ hidden；测试只用已声明 API）
4. 旧门禁仍过：reference、isolation、forbidden、public+hidden
5. §8 人工审核清单通过（记录在 `evaluation_spec.manual_review`）

未迁移题保持 **`spec_status: legacy`**。**不得**将 legacy 与 compliant 主结果混报。

---

## 3. 单题迁移流程

1. 从 legacy `metadata` + `evaluation/behavior_contract.json` + hidden 测试起草 `public_spec` / `evaluation_spec`（试点可用 `migrate-task-spec` 自动起草）。
2. **Dry-run：**

```bash
PYTHONPATH=harness python -B -m featureliftbench.cli migrate-task-spec benchmark/tasks/<task_id> --dry-run
```

3. **正式迁移**（写入 `metadata.json`、`TASK.md`，同步 behavior contract hash）：

```bash
PYTHONPATH=harness python -B -m featureliftbench.cli migrate-task-spec benchmark/tasks/<task_id>
```

4. **校验：**

```bash
PYTHONPATH=harness python -B -m featureliftbench.cli validate-task benchmark/tasks/<task_id> --json
```

5. 仅渲染 TASK（不写盘）：

```bash
PYTHONPATH=harness python -B -m featureliftbench.cli render-task benchmark/tasks/<task_id>
PYTHONPATH=harness python -B -m featureliftbench.cli render-task benchmark/tasks/<task_id> --write
```

6. 在 `evaluation_spec.hidden_failure_rejudgement` 记录历史 hidden failure 是否仍属合法契约。

---

## 4. 批量标注与报表

主榜未迁移题标 legacy（已执行一次；新题入库时亦应设置）：

```bash
PYTHONPATH=harness python -B -m featureliftbench.cli annotate-spec-status benchmark/tasks
```

合规统计：

```bash
python3 scripts/report_spec_compliance.py benchmark/tasks
python3 scripts/report_spec_compliance.py benchmark/tasks --csv reports/audits/spec_compliance.csv
```

生命周期审计（含 `spec_status` 列）：

```bash
python3 scripts/check_task_lifecycle.py
```

---

## 5. Agent 侧行为（compliant vs legacy）

| 类型 | Agent workspace 中的 TASK |
| --- | --- |
| **compliant** | `render(public_spec)`（与包内 `TASK.md` 一致）；默认 Main 追加 evaluator-test-blind workspace 说明 |
| **legacy** | harness `build_task_prompt()`（旧双轨；待迁移） |

Compliant 任务 **不得** 再手写包内 `TASK.md` 与 `public_spec` 分叉。

---

## 6. 实验与 rebaseline

### 6.1 分报规则

- 历史 legacy 主榜 run（Flash 91/150 等）继续按 **legacy 口径** 解读。
- 当前主榜已全量 compliant；各批次须 **单独** 重跑基线后再做方法/臂对照。
- 规格或 hidden 变更后，评估是否重冻 oracle / leaderboard。

### 6.2 Compliant 重跑示例

```bash
./run_experiment.sh --arm main \
  --tasks isort__settings_resolver_core__hard3_001,transitions__state_machine_core__hard3_001,scrapy__item_loader_core__hard3_001 \
  --run-id compliant-pilot-main

./run_experiment.sh --arm public_feedback \
  --tasks isort__settings_resolver_core__hard3_001,transitions__state_machine_core__hard3_001,scrapy__item_loader_core__hard3_001 \
  --run-id compliant-pilot-public-feedback
```

### 6.3 与实验臂的关系

Public-feedback / Short-prompt **不替代** 规格合规。见 [EXPERIMENT_ARMS.md](EXPERIMENT_ARMS.md) §6。

**禁止：** 删除任务包内 `public_tests/` 来实现 test-blind Main；任务包保留两级
evaluator tests，由 workspace materialization 隔离。Public-feedback 必须通过
显式 ablation profile / `--agent-public-tests` 启用。

---

## 7. 后续批次建议

1. ~~hard-50 / API 双轨已知题~~（已完成）  
2. ~~Diagnostic-40 / 高风险纠缠题~~（已完成）  
3. ~~其余 core-100~~（已完成）  

工程迁移、契约 hardening 与 spec freeze 已闭环。当前可启动 compliant
Python-150 模型实验；全量独立人工 paper-gold 审核按计划延后到实验后，
只阻塞 paper-ready 发布。新实验与历史 legacy 结果必须分报。

---

## 8. 工程模块索引

| 模块 | 路径 |
| --- | --- |
| Spec / hash | `harness/featureliftbench/task_spec.py` |
| TASK 生成 | `harness/featureliftbench/task_render.py` |
| 宪法校验 | `harness/featureliftbench/constitution_validate.py` |
| 迁移草稿 | `harness/featureliftbench/task_spec_migrate.py` |
| validate 集成 | `harness/featureliftbench/validate.py` |
| CLI | `harness/featureliftbench/cli.py` |
