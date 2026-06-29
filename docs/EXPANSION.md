# 扩题指南（Python 50 → 100）

**最后更新：** 2026-06-28

在 **不修改 batch-0 五十题** 的前提下，通过 `benchmark/staging/` 试选、筛选，**新增 50 道** batch-1 入主榜，达到 **100 Python decoupling tasks**。

| 资源 | 路径 |
| --- | --- |
| 候选台账 | [candidate_backlog.md](candidate_backlog.md) |
| 试选题目录 | `benchmark/staging/` |
| 正式主榜 | `benchmark/tasks/` |
| 单题格式 | [TASK_FORMAT.md](TASK_FORMAT.md) |
| 评测契约 | [BENCHMARK_SPEC.md](BENCHMARK_SPEC.md) |
| **七步执行标准** | [BATCH1_PLAYBOOK.md](../BATCH1_PLAYBOOK.md) |

**进度（手动更新）：**

| 指标 | 目标 | 当前 |
| --- | ---: | ---: |
| batch-0（冻结） | 50 | 50 |
| backlog idea | 80 | 30 |
| 首批 shortlist | 5 | 5 |
| staging 试做 | — | 3 |
| staging 进行中 | 30 | 10 |
| batch-1 已入榜 | 50 | 50 |
| 主榜合计 | 100 | 100 |

---

## 1. 选题原则

任务类型不变：**behavior-preserving feature-level decoupling**（独立 `featurelifted` 包），不是 issue / patch。

| 维度 | 要求 |
| --- | --- |
| **实用性（reuse）** | 解耦产物对应真实可复用模块（parser、配置加载、规则引擎等） |
| **缠绕（entanglement）** | 难来自真实耦合，非人为堆垃圾 |
| **可判别** | functional gate + `extraction_ratio` 区分 copy-heavy 与 compact |
| **难度（hard）** | batch-1 主榜只收 hard：非平凡闭包、跨关注点耦合、有组合 hidden；有用但过轻的切片只能进 control/sanity |
| **可评估性（testability）** | 行为必须可用 deterministic pytest 验证；hidden failure 能定位到功能缺失而不是环境/网络/时间漂移 |

**立项前必答：**

> 若 Agent 成功解耦，`featurelifted` 等价于现实中哪一类模块？谁会在什么场景 `import` 它？

### batch-0 题源（论文分层）

| 类型 | 数量 | 说明 |
| --- | ---: | --- |
| 真实 OSS 切片 | 43 | 主叙事 |
| 策展 `vibe_app` | 7 | legacy / vibe-coded 应力切片，单独报告 |

batch-1 优先 **真实 OSS + reuse 故事硬**；与 batch-0 **同库允许**，须 **不同可复用切面**。

### 新题立项检查（staging 前）

- [ ] Reuse、boundary、standalone 价值（见 [task_designs/TEMPLATE.md](task_designs/TEMPLATE.md) Practical reuse）
- [ ] 与 batch-0 不重复切面
- [ ] 能设想 compact oracle（非整库复制）与有力 hidden
- [ ] 预估 `output.import` 能完整覆盖 intended API，避免 hidden-only API 缺口
- [ ] 满足 hard gate：预估 oracle 跨 6+ 运行时文件或约 1200+ LOC，且至少两类 entanglement 共同作用
- [ ] 若候选功能本身就是单文件/薄 utility，默认不进主榜；除非能证明 hidden 组合行为足够难
- [ ] 满足 testability gate：public/hidden 都能写成离线、稳定、无网络、无时钟漂移的 pytest
- [ ] 至少 3 个 module probes 能映射到具体 hidden failure；失败原因可解释，不只是“整体 import 崩了”
- [ ] Oracle、Copy-All、naive/shallow baseline 三者预期结果不同：oracle 过且 compact；copy-all 过但 extraction 高；naive baseline 应在 hidden 挂

### 首批执行策略

不要直接并行开 50 题。首批 **5 个 shortlist** 已在 [candidate_backlog.md](candidate_backlog.md) 标出；先做 **1 个 staging pilot**。pilot 过完全部 gate 后，再扩到 20 个 staging in-progress。

首批 shortlist 优先满足：

- reuse 叙事能一句话讲清楚；
- compact oracle 闭包既不能接近整库，也不能只是单文件复制；
- 目标功能跨 parser/state、data model、config/environment、resource、registry/metaclass 中至少两类；
- hidden 可覆盖组合行为、错误类型、边界输入，而不是 public 复读；
- 测试能稳定复现上游语义，不依赖网络、真实时区数据库变化、随机数、远端服务或本机环境；
- 与 batch-0 同库时，design note 明确说明不同可复用切面。

---

## 2. Staging 与入榜

### 目录

```text
benchmark/tasks/     # 主榜（50 → 100）；run-agent 默认只跑这里
benchmark/staging/   # 试选题；list_tasks / 官方 leaderboard 不包含
benchmark/sanity/    # smoke 3 题（不变）
```

staging 单题布局与 [TASK_FORMAT.md](TASK_FORMAT.md) 相同。Oracle：`benchmark/submissions/<task_id>/oracle/`。

### 流程

完整七步见 **[BATCH1_PLAYBOOK.md](../BATCH1_PLAYBOOK.md)**。摘要：

```text
candidate_backlog.md（idea）
  → design spike（docs/task_designs/<task_id>.md）
  → benchmark/staging/<task_id>/ 实现 + oracle + naive + copy-all 分层
  → Flash 单题校准
  → 入榜清单全勾
  → 复制到 benchmark/tasks/<task_id>/
  → verify_all_oracles --task-id <task_id>
  → 更新 benchmark_tasks.md、本页进度表、backlog → promoted
```

### 验证命令

```bash
export PYTHONPATH=harness
python -B -m featureliftbench.cli validate-task benchmark/staging/<task_id>/
python3 harness/scripts/audit_output_imports.py benchmark/staging/<task_id>/ --fail-on-gap
python3 harness/scripts/build_oracle_submission.py benchmark/staging/<task_id>/
python -B -m featureliftbench.cli eval benchmark/staging/<task_id>/ \
  benchmark/submissions/<task_id>/oracle \
  --output experiments/validate-<task_id>
```

正式 baseline 或论文口径结果走 Docker eval：

```bash
python -B -m featureliftbench.cli eval benchmark/staging/<task_id>/ \
  benchmark/submissions/<task_id>/oracle \
  --output experiments/validate-<task_id>-docker \
  --docker
```

### 入榜清单（复制到 tasks/ 前）

**身份：** task_id 不与 batch-0 冲突；`docs/task_designs/<task_id>.md` 含 Practical reuse；backlog 可标 `promoted`。

**规范：** `validate-task` 过；`difficulty=hard`；`audit_output_imports.py --fail-on-gap` 无 blocking gap。

**Oracle：** functional_gate=1；ExtractionRatio 约 0.20–0.60；Copy-All 明显高于 oracle；≥3 module probes。

**测试：** hidden 非 public 复读；同库须不同切面说明；能挡住明显 shallow / public-hardcode 策略；失败原因能归因到缺失功能。

**评估性：** oracle、copy-all、naive baseline 预期分层清楚；≥3 module probes 能触发不同 hidden failure；测试不依赖网络、真实时间、外部服务或平台专有行为。

**实验：** staging pilot 至少跑一次 Flash 单题，确认 public 指引足够、hidden 判别力有效；suite 级资源异常必须能在 summary 中区分为 `resource_limit_exceeded` 或等价基础设施状态。

**操作：** 复制目录 → `verify_all_oracles.py --task-id` → 更新 catalog 与进度。

### 淘汰（dropped）

reuse 不成立、oracle 做不出、与 batch-0 重复、validate 过不了 → backlog 标 `dropped` 并记原因。

---

## 3. 分阶段计划

**硬性约束：** batch-0 不动；只新增 batch-1；先入 staging。

### Phase 0 — 机制就绪（~1 周）

- [x] [candidate_backlog.md](candidate_backlog.md) 至少 30 条 starter idea
- [x] 选出首批 **5 个 shortlist**
- [ ] staging 试点一题（validate + oracle，不必入榜）
- [ ] suite 级资源异常状态可区分（避免 OOM 混入普通 failed）
- [ ] Docker eval 用作官方 baseline 检查

### Phase 1 — backlog（~1–2 周）

- [ ] 盘点 batch-0 已覆盖源库（[benchmark_tasks.md](benchmark_tasks.md)）
- [ ] backlog **≥80** 条（≥20 条进入 staging 进行中）
- [ ] 每个 staging task 都有 design note Practical reuse + module probes

### Phase 2 — staging 试做（~4–6 周）

- [ ] staging 内 **≥50** 道 oracle 全绿（允许先试 ≥60 再淘汰）
- [ ] 每批 10 题跑 Flash spot-check，记录 functional / extraction / hidden failure pattern

### Phase 3 — 入榜（~2–4 周）

- [ ] 50 道复制到 `tasks/`；`verify_all_oracles` **100/100**
- [ ] `audit_output_imports.py --fail-on-gap` 对 100 题全绿

### Phase 4 — 集成（~1 周）

- [ ] 更新 [BENCHMARK_STATUS.md](BENCHMARK_STATUS.md)、[BENCHMARK_SPEC.md](BENCHMARK_SPEC.md)、[EXPERIMENT_RESULTS.md](EXPERIMENT_RESULTS.md)（旧实验标 batch-0）
- [ ] 100 题 full-suite 实验排期

### 不在本计划内

Go 100、修改 batch-0、替换 batch-0 弱题。

---

## 4. 相关文档

- [TASK_FORMAT.md](TASK_FORMAT.md) — `metadata.json` 与目录
- [task_designs/TEMPLATE.md](task_designs/TEMPLATE.md) — 设计笔记模板
- [benchmark_tasks.md](benchmark_tasks.md) — 主榜目录
