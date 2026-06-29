# Batch-1 出题标准流程（Playbook）

**最后更新：** 2026-06-28

本文是 batch-1 扩题（50 → 100 hard）的**唯一执行标准**。`httpx__request_model_core__001` 与 `pydantic_v1__validation_error_core__001` 两题作为 pilot 参考；其中 `pydantic` 暴露了 **Flash 近 oracle copy 也能 functional pass** 的风险，后续按本文更严格的校准规则执行。

| 层级 | 文档 | 作用 |
| --- | --- | --- |
| **执行（本文）** | [BATCH1_PLAYBOOK.md](BATCH1_PLAYBOOK.md) | 七步流程、gate、命令、promote 决策 |
| 仓库池 | [docs/BATCH1_REPO_SELECTION.md](docs/BATCH1_REPO_SELECTION.md) | 已接受 repo、待选 repo 数量目标、同仓上限 |
| 质量评审 | [docs/BATCH1_QUALITY_RUBRIC.md](docs/BATCH1_QUALITY_RUBRIC.md) | Cursor/Agent 生成题后的客观入榜标准 |
| 工程 backlog | [TODO.md](TODO.md) | 当前 sprint、进度表、优先级 |
| 政策 | [docs/EXPANSION.md](docs/EXPANSION.md) | 选题原则、staging 政策、进度表 |
| 格式 | [docs/TASK_FORMAT.md](docs/TASK_FORMAT.md) | `metadata.json`、目录布局、评分公式 |
| 设计 | [docs/task_designs/TEMPLATE.md](docs/task_designs/TEMPLATE.md) | 单题人类设计笔记模板 |
| 契约 | [docs/BENCHMARK_SPEC.md](docs/BENCHMARK_SPEC.md) | 论文/复现口径 |
| 台账 | [docs/candidate_backlog.md](docs/candidate_backlog.md) | 候选池与 shortlist 队列 |

**硬性约束（全程遵守）：**

- batch-0 五十题冻结，不改、不替换
- 无 oracle 不进 `benchmark/tasks/`
- 一次一题：当前 staging pilot 未 promote 前，不并行开下一题
- Flash 单题模板跑通后，再扩多模型 full suite
- **functional pass 不是 promote 充分条件**；必须同时看 hidden 判别力、oracle/copy-all/naive 分层、`extraction_ratio` 和 `final_score`

---

## 总览：七步流程

```text
Step 0  选仓库 / shortlist（docs/BATCH1_REPO_SELECTION.md + docs/candidate_backlog.md）
Step 1  Design spike（docs/task_designs/<task_id>.md）
Step 2  创建 staging 目录（benchmark/staging/<task_id>/）
Step 3  构建 oracle closure（benchmark/submissions/<task_id>/oracle/）
Step 4  构建 naive baseline（benchmark/submissions/<task_id>/naive/）
Step 5  本地验证（validate / audit / eval / probes / copy-all）
Step 6  Flash 单题校准
Step 7  Promote / Redesign / Drop
```

每步有明确 gate；**前一步不过，不进入下一步**。

---

## Agent 接管模式

目标不是让 Agent “写一份看起来合理的设计”，而是让 Agent 按固定循环产出机器证据，并由客观 gate 自动推出 `promote` / `redesign` / `drop`。

### 固定循环

```text
while batch-1 target not reached:
  1. 取下一个候选
  2. 生成/更新 design note
  3. 生成 staging task + oracle/naive/copy_all
  4. 跑全部 gate
  5. 写 review evidence packet
  6. 根据 gate_report.json 决策
  7. promote 后更新 catalog；redesign/drop 后立即进入下一轮
```

Agent 默认不向人类提问；只有两类情况停下来：

- 需要联网、下载、认证、安装外部依赖或执行不可恢复操作；
- 连续两轮 redesign 后仍无法让同一题通过客观 gate。

### Evidence Packet

每道 staging 题必须生成一个证据目录：

```text
experiments/batch1/<task_id>/review/
  gate_report.json
  decision.md
  validate-task.log
  audit-output-imports.log
  module-probes.log
  oracle/result.json
  naive/result.json
  copy_all/result.json
  flash/run.json              # 若已跑 Flash
```

`gate_report.json` 是唯一决策依据，格式固定：

```json
{
  "task_id": "<task_id>",
  "attempt": 1,
  "decision": "promote | redesign | drop",
  "flash_tier": "A | B | C | not_run",
  "blocking_gates": [],
  "exceptions": [],
  "metrics": {
    "oracle_extraction": 0.0,
    "oracle_final": 0.0,
    "naive_extraction": 0.0,
    "copy_all_extraction": 0.0,
    "copy_all_delta_vs_oracle": 0.0,
    "flash_extraction": null,
    "flash_final": null
  },
  "evidence": {
    "oracle_result": "experiments/batch1/<task_id>/review/oracle/result.json",
    "naive_result": "experiments/batch1/<task_id>/review/naive/result.json",
    "copy_all_result": "experiments/batch1/<task_id>/review/copy_all/result.json",
    "flash_run": "experiments/batch1/<task_id>/review/flash/run.json"
  }
}
```

Agent 可以用 prose 解释，但 prose 不能覆盖 `gate_report.json`。如果 `blocking_gates` 非空，结论只能是 `redesign` 或 `drop`。

### 客观 Gate 常量

| Gate | 客观条件 |
| --- | --- |
| G0 task shape | `validate-task` exit 0；`audit_output_imports.py --fail-on-gap` exit 0 |
| G1 oracle | `status=passed`；public/hidden 都 pass；`functional_gate=1.0`；`0.20 <= extraction_ratio <= 0.60`；无 forbidden import；无 timeout/resource limit |
| G2 naive | public pass；hidden fail；`functional_gate=0.0`；`extraction_ratio <= 0.10`；失败不是 import/package 崩溃 |
| G3 copy_all | `status=passed`；`extraction_ratio >= 0.85`；`copy_all_extraction - oracle_extraction >= 0.25` |
| G4 probes | `verify_module_probes.py --verify-oracle` exit 0；至少 3 个 probe 映射到 hidden failure |
| G5 Flash | 至少跑一次 `deepseek_v4_flash`；按 A/B/C 档记录为校准标签，不作为默认阻塞 gate |
| G6 docs | design note 填 Result + Agent Calibration；backlog/status/catalog 更新可由 diff 检查 |

G2 的 public pass 是从现在开始的新标准。naive 的目的不是证明题很难写，而是证明 hidden 能挡住“只看 public 的浅实现”。如果 naive 连 public 都过不了，public/hidden 分层不够客观，应先 redesign。

### Metric Exceptions

G0-G4 仍是机械硬门槛。只有在指标本身误导任务质量时，允许少量写入 `gate_report.json` 的显式例外；例外不能替代 oracle/naive/copy_all/probe 的实际 evidence。

| Exception | 适用场景 | 必填证据 |
| --- | --- | --- |
| `low_oracle_extraction_A_tier_exception` | oracle 低于 0.20，但 Flash 为 A 档、copy_all 明显高、naive hidden fail，且 design note 说明功能闭包天然较小 | oracle/naive/copy_all/flash 指标；reuse 说明；非 toy 说明 |
| `copy_all_metric_exception` | copy_all pass 且与 oracle 拉开 `>=0.25`，但因源仓体量或 LOC 口径导致 extraction 未达 0.85 | copy_all 指标；delta；copy_all 覆盖说明；为什么不是 oracle 过宽 |

有 exception 的任务仍可 `decision=promote`，但 `exceptions` 必须非空，`decision.md` 必须解释，acceptance report 必须汇总。未登记的 G0-G4 偏离仍然阻塞 promote。

### 客观决策规则

| 结果 | 条件 |
| --- | --- |
| `promote` | G0-G4 全过或只有已登记 metric exception；Flash 已跑并记录 A/B 标签 |
| `promote`（B 档） | G0-G4 全过或只有已登记 metric exception；Flash 为 B 档；design note/decision 明确标注 `large-closure-pass` 或 `scoring-discriminator` |
| `redesign` | 任一 gate 可通过改边界、测试或 oracle 修复；或 Flash 为 C 档但 reuse 仍成立 |
| `drop` | reuse 不成立；oracle 无法 bounded；copy_all 与 oracle 拉不开；同一题连续 2 轮 redesign 仍不过 |

Redesign 最多两轮。超过两轮仍不过，就把原因写入 `decision.md` 和 backlog，转下一题，保证快速迭代。

---

## Step 0 — 选题

先从 [docs/BATCH1_REPO_SELECTION.md](docs/BATCH1_REPO_SELECTION.md) 确认 repo 仍值得占用 batch-1 名额，再从 [docs/candidate_backlog.md](docs/candidate_backlog.md) shortlist 取具体功能切片。

**先选 repo，再切题。** batch-1 不追求覆盖所有热门库；宁可少做，也不要把弱 repo 勉强切成题。

**Repo gate（进 shortlist 前）：**

| 维度 | 要求 |
| --- | --- |
| 真实使用 | 是真实 Python OSS 或明确策展的 legacy/vibe_app；有现实 import 场景 |
| 可切片 | 至少存在一个可独立复用的功能闭包，而不是只能整库使用 |
| 真实缠绕 | 难度来自上游结构、状态、parser、配置、资源或注册机制，不是人为制造复杂度 |
| 可固定 | 能 pin source snapshot；license 可记录；测试可离线 deterministic |
| 体量合适 | 既不是单文件 utility，也不是必须复制大半仓库才可用 |
| 不重复 | 与 batch-0 或已选 batch-1 repo 不重复同一可复用切面 |

**同仓数量上限：**

| 范围 | 规则 |
| --- | --- |
| batch-1 默认 | 一个 repo 一道题 |
| batch-1 例外 | 最多 2 道，必须是不同 reuse 切面且 oracle 重叠低 |
| batch-1 硬上限 | 3 道，需要在 design note 写明例外理由 |
| 全主榜 100 题 | 单个真实 OSS repo 最多 5 道；策展 `vibe_app` 单独报告，不作为真实 OSS 先例 |

**立项前三问（必须能一句话答清）：**

1. 解耦成功后，`featurelifted` 等价于现实中哪类可复用模块？
2. 谁会在什么场景单独 `import` 它？
3. 为什么 compact closure 比 copy-all 更合理？

**Hard gate（staging 前）：**

| 维度 | 要求 |
| --- | --- |
| Useful | 真实 OSS 切片，reuse 叙事可信 |
| Hard | 预估 oracle ≥6 运行时文件或 ~1200+ LOC；至少两类 entanglement |
| Testable | public/hidden 均为离线 deterministic pytest；≥3 module probes |
| 分层预期 | oracle compact 过；copy-all 过但高 extraction；naive hidden fail；强 Agent 不能靠薄实现轻松过 |

与 batch-0 同库时，design note 必须说明**不同可复用切面**。

---

## Step 1 — Design spike

**产物：** `docs/task_designs/<task_id>.md`（从 [docs/task_designs/TEMPLATE.md](docs/task_designs/TEMPLATE.md) 复制）

**必填章节：**

- Practical reuse（三问）
- Included / Excluded behaviors
- Public / Hidden tests 设计意图
- Module probes 表（≥3 行，每行映射到具体 hidden test）
- Manual Oracle Closure Plan 表（先填 Target，Result 在 Step 5 填）
- Go / No-Go criteria

**Status 流转：** `draft-spike` → `oracle-verified`（Step 5 后）→ `agent-calibrated`（Step 6 后）

**Spike 不过则：** 标 `dropped` 或 redesign，不建 staging。

---

## Step 2 — 创建 staging

**目录：** `benchmark/staging/<task_id>/`

```text
benchmark/staging/<task_id>/
  metadata.json
  requirements.lock          # 可为空；见下方依赖说明
  repo/                      # pinned upstream snapshot（固定 commit）
  public_tests/
  hidden_tests/
  evaluation/
    forbidden_imports.txt
    oracle_manifest.json
```

**`metadata.json` 要点：**

- `difficulty`: `"hard"`
- `tags`: 含 `batch-1`
- `environment.network`: `false`
- `output.import`: 覆盖 public tests 用到的全部符号
- `entanglement.primary`: 七选一（见 [docs/TASK_FORMAT.md](docs/TASK_FORMAT.md)）

**测试设计原则：**

| 集合 | 目的 |
| --- | --- |
| public | 主路径行为；给 agent 足够指引 |
| hidden | 组合行为、错误类型、边界；**不能**只是 public 复读 |

Hidden 断言优先用 `type` / `loc` / 结构，避免绑定完整 error message 文本（防 flaky）。

**依赖（`requirements.lock`）：**

评测器用 `pip install --no-index`（见 [docs/limitations.md](docs/limitations.md)）。策略：

1. **优先空 lock**：第三方依赖可由 venv `--system-site-packages` 满足时，lock 留空
2. **必须 pin 时**：把 wheel 放进 `benchmark/vendor-wheels/`，或在 design note 记录离线安装策略
3. `allowed_dependencies` 与 lock 内容一致

---

## Step 3 — Oracle closure

**位置：** `benchmark/submissions/<task_id>/oracle/`

```bash
export PYTHONPATH=harness
python3 harness/scripts/build_oracle_submission.py benchmark/staging/<task_id>/
```

新题源库若不在 `build_oracle_submission.py` 内置 profile 中，需添加 `build_<source>()` 与必要 patch（参考 `build_httpx` / `build_pydantic`）。

**Oracle 通过标准：**

| 检查 | 目标 |
| --- | --- |
| Functional gate | public + hidden 全过 |
| Closure 体积 | 非单文件薄 wrapper；通常 6+ 文件 |
| ExtractionRatio | **0.20 – 0.60** |
| Forbidden imports | 无 `pydantic`/`httpx`/原包名等 |
| Excluded surface | 不含 network、CLI、整库无关模块；若 oracle 必须带 excluded 模块才能过，优先 redesign |

先求**能解**，再迭代裁剪；不要求第一步就优雅。`ExtractionRatio` 落在 **0.55–0.60** 属于黄区：可以继续验证，但 design note 必须解释为什么 compact closure 仍然比 copy-all 有明显价值。

---

## Step 4 — Naive baseline

**位置：** `benchmark/submissions/<task_id>/naive/`

手写浅实现（单文件 `featurelifted/__init__.py` 即可），模拟「只抄 public API 壳」的 agent 策略。

**通过标准：**

| 检查 | 目标 |
| --- | --- |
| Public tests | 必须 pass |
| Hidden tests | **必须 fail** |
| Fail 原因 | 可归因到具体语义缺失（非 import 崩） |

**示例策略：**

- httpx：`URL=str`、`Headers=dict` → 挂在 duplicate query / raw headers / cookie merge
- pydantic：无 metaclass / 无嵌套 loc 合并 → 挂在 nested validation / root_validator

---

## Step 5 — 本地验证

全部在 staging 路径上跑（promote 前不改 `benchmark/tasks/`）。所有输出必须落到 review evidence packet。

```bash
export PYTHONPATH=harness
TASK_ID=<task_id>
TASK_DIR=benchmark/staging/$TASK_ID
REVIEW_DIR=experiments/batch1/$TASK_ID/review
mkdir -p "$REVIEW_DIR/oracle" "$REVIEW_DIR/naive" "$REVIEW_DIR/copy_all"

# 1. 目录与 metadata
python -B -m featureliftbench.cli validate-task "$TASK_DIR" \
  > "$REVIEW_DIR/validate-task.log" 2>&1

# 2. output.import 与测试对齐
python3 harness/scripts/audit_output_imports.py "$TASK_DIR" --fail-on-gap \
  > "$REVIEW_DIR/audit-output-imports.log" 2>&1

# 3. 重建 oracle（若刚改过 build 脚本）
python3 harness/scripts/build_oracle_submission.py "$TASK_DIR"

# 4. Oracle eval
python -B -m featureliftbench.cli eval "$TASK_DIR" \
  "benchmark/submissions/$TASK_ID/oracle" \
  --output "$REVIEW_DIR/oracle"

# 5. Module probes（需 Python 3.11+）
python3 harness/scripts/verify_module_probes.py "$TASK_DIR" --verify-oracle \
  > "$REVIEW_DIR/module-probes.log" 2>&1

# 6. Naive eval
python -B -m featureliftbench.cli eval "$TASK_DIR" \
  "benchmark/submissions/$TASK_ID/naive" \
  --output "$REVIEW_DIR/naive"

# 7. Copy-all eval（在 build_oracle_submission.py 中实现 build_<source>_copy_all）
python -B -m featureliftbench.cli eval "$TASK_DIR" \
  "benchmark/submissions/$TASK_ID/copy_all" \
  --output "$REVIEW_DIR/copy_all"
```

**三层 baseline 预期矩阵（Step 5 gate）：**

| Baseline | Public | Hidden | ExtractionRatio | 说明 |
| --- | --- | --- | --- | --- |
| oracle | pass | pass | 0.20 – 0.60 | compact 参考解 |
| naive | pass | **fail** | 极低（~0.01） | 挡住浅实现 |
| copy_all | pass | pass | ≥0.85，且比 oracle 高 ≥0.25 | copy-heavy 对照 |

**Module probes：** ≥3 个，每个去掉 oracle 中一个模块后，对应 hidden test 必须 fail。

**Copy-all 解释：** 不要机械要求所有题都 ≥0.95。若 source snapshot 已被裁过，copy-all 可能低于 0.95；合格标准是 copy-all 与 oracle 之间有足够罚分空间。经验线：copy-all 至少比 oracle 高 **0.30**，或 copy-all `final_score` 明显低于 oracle。若 copy-all 和 oracle 接近，说明边界太宽或上游本来就独立，优先 redesign/drop。

**Gate report 生成：** Step 5 跑完后，Agent 必须读取以下文件并写 `gate_report.json` 的 G0-G4 字段：

```text
$REVIEW_DIR/oracle/result.json
$REVIEW_DIR/naive/result.json
$REVIEW_DIR/copy_all/result.json
$REVIEW_DIR/validate-task.log
$REVIEW_DIR/audit-output-imports.log
$REVIEW_DIR/module-probes.log
```

禁止手填通过状态。`result.json` 中的 `status`、`public_tests.passed`、`hidden_tests.passed`、`scores.functional_gate`、`scores.extraction_ratio`、`scores.final_score` 是权威字段。

验证通过后，回填 design note 的 Manual Oracle Closure Plan 表。

---

## Step 6 — Flash 单题校准

```bash
export PYTHONPATH=harness
# 正式 Docker suite 用 LIVE_TRAJECTORY=1（run-batch1-docker-flash.sh 已默认）
# 仅本地无 mini / 无 live runner 的单题 staging 调试时可设 0：
# export FEATURELIFTBENCH_LIVE_TRAJECTORY=0

python -B -m featureliftbench.cli run-agent benchmark/staging/<task_id>/ \
  --agent mini-swe-agent \
  --agent-config harness/config/agents.toml \
  --agent-profile deepseek_v4_flash \
  --env-file .env \
  --yolo \
  --output experiments/batch1/<task_id>/review/flash
```

**校准分三档：**

### A 档：强判别，默认可 promote

满足任一：

- public pass，hidden **fail**（如 httpx：extraction≈0.17）
- Flash functional pass，但明显 copy-heavy：`extraction_ratio` 接近 copy-all，且 `final_score` 明显低于 oracle

这类题说明 hidden 能挡住浅实现，或 scoring 能强罚复制策略。

### B 档：中等判别，保留但必须披露

典型形态：

- Flash functional 全过，extraction 接近 oracle（如 pydantic：≈0.56，final≈0.44）
- Flash 提交是近 oracle 级大闭包，而不是薄实现

这不等于“题太简单”，但说明 **hidden 对强 Agent 的 functional 判别力有限**。B 档可以 promote，但必须满足：

- Step 5 三层 baseline 和 module probes 全部扎实；
- design note 明确标注 `large-closure-pass` / `scoring-discriminator`，不要标成强 `functional-discriminator`；
- 已尝试补 2–3 个 hidden stress tests，仍然被 Flash 近 oracle 闭包通过；
- acceptance report 和论文实验必须披露 A/B/C 分布；不得声称 batch-1 mostly defeats Flash。

### C 档：不可接受，必须 redesign/drop

满足任一：

- Flash 轻松全过且 extraction 极低（说明题太简单）
- Flash 完全无法过 public（public 指引不足或 scope 过宽）
- Flash pass 主要靠 public-hardcode / 玩具实现，而 hidden 没挡住
- copy-all 与 oracle extraction 接近，`final_score` 拉不开

Step 6 跑完后，Agent 必须读取 `$REVIEW_DIR/flash/run.json`，把 `status`、`evaluation.scores.extraction_ratio`、`evaluation.scores.final_score`、`agent.usage.total_tokens` 写入 `gate_report.json`，并据此填 `flash_tier`。没有 `flash/run.json` 时，`flash_tier=not_run`，不得 promote。Flash tier 是 calibration label，不是模型排名结论。

---

## Step 7 — Promote / Redesign / Drop

### Promote（复制到主榜）

**全部满足：**

- [ ] Step 5 三层 baseline 矩阵符合预期
- [ ] Module probes ≥3 全 verified
- [ ] `audit_output_imports.py --fail-on-gap` 无 blocking gap
- [ ] Flash 单题已跑，结果记入 design note
- [ ] Flash 校准档位已记录；若为 B，design note 有 `large-closure-pass` / `scoring-discriminator` 标记
- [ ] 若 G0-G4 有 metric exception，`gate_report.json` 和 `decision.md` 均写明 exception 类型、阈值和证据
- [ ] `experiments/batch1/<task_id>/review/gate_report.json` 存在，且 `decision=promote`
- [ ] design note status → `agent-calibrated`

**操作：**

```bash
cp -R benchmark/staging/<task_id> benchmark/tasks/<task_id>

export PYTHONPATH=harness
python3 harness/scripts/verify_all_oracles.py --task-id <task_id>
```

**文档更新（checklist）：**

- [ ] `docs/benchmark_tasks.md` — 加一行，更新主榜计数
- [ ] `docs/EXPANSION.md` — 进度表
- [ ] `docs/BATCH1_REPO_SELECTION.md` — 更新 repo 状态与同仓计数
- [ ] `docs/candidate_backlog.md` — 标 `promoted`，变更日志
- [ ] `docs/task_designs/<task_id>.md` — 填 Result 表 + Agent Calibration
- [ ] `TODO.md` — 当前题指针移到下一道 shortlist

### Redesign

题有价值但：边界太宽/窄、hidden 不够准、oracle 闭包不理想、Flash C 档、或 G0-G4 偏离没有登记 metric exception → 留在 staging 迭代，**不** promote。

### Drop

reuse 不成立、oracle 做不出、与 batch-0 重复、validate 过不了 → backlog 标 `dropped` 并记原因。

---

## Pilot 参考数据（已 promote，不作为放宽先例）

| task_id | Oracle ext | Naive hidden | Copy-all ext | Flash | 备注 |
| --- | ---: | --- | ---: | --- | --- |
| `httpx__request_model_core__001` | 0.318 | fail | 0.908 | pub pass / hidden fail，ext≈0.17 | 判别力强 |
| `pydantic_v1__validation_error_core__001` | 0.567 | fail | 0.991 | 全过，ext≈0.56 | B 档例外；判别力中等，后续不要把它当默认 promote 模板 |

---

## 当前队列与补位规则

**进度：** 主榜 **100/100**（batch-1 已入榜 **50**）。batch-1 扩题 **已完成**。

Agent 选下一题时按以下顺序，不需要人工重新排序：

1. `shortlist` 状态优先，按表格顺序取第一道未 promoted / dropped 的题；
2. `staging` 状态但缺 gate_report 的题优先补完 evidence packet；
3. 若 shortlist 为空，从 `idea` 中选 reuse 最清楚、预估 oracle 6+ 文件、可离线测试的候选，先写 design spike；
4. 如果一题两轮 redesign 后仍不过 gate，标 `dropped`，立即取下一题；
5. 每 promote/drop/redesign 一次，都必须同步更新 backlog 状态和 `decision.md`。

已完成的 batch-1 首批 10 题只作为校准样本，不再阻塞后续：

| 区间 | 状态 |
| --- | --- |
| batch-1 #1-#5 | 已入榜；A/B 混合校准样本 |
| batch-1 #6-#10 | 已入榜；B 档偏多，后续实验需按 A/B 分层报告 |

**下一阶段偏好：** 优先选能产生 A 档 Flash 结果的候选。若连续出现 B 档，先加 hidden stress tests；若仍为 B 档，可以保留但必须在 acceptance report 和论文中按校准标签披露。

---

## 相关命令速查

```bash
# 列出 staging 题（若有）
ls benchmark/staging/

# 正式题 eval（promote 后）
python -B -m featureliftbench.cli eval benchmark/tasks/<task_id>/ \
  benchmark/submissions/<task_id>/oracle \
  --output experiments/batch1/<task_id>/review/promoted-oracle

# Docker 第二层（论文口径，可选）
python -B -m featureliftbench.cli eval benchmark/staging/<task_id>/ \
  benchmark/submissions/<task_id>/oracle \
  --output experiments/batch1/<task_id>/review/docker-oracle \
  --docker
```
