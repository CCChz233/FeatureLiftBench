# Test-First Lift：面向 FLB 的在线自适应等价测试

> **Documentation status: archived · Indexed: 2026-08-04**

**方法简称：** TFL（Test-First Lift）

**状态：正式负结果（已归档）· 不再修补 · 不扩样本**

正式 pilot：`experiments/methods/test_first_lift_pilot/dev6_tfl_p0_20260731` →
Functional **1/6**，相对 Main **−1**。裁决：
[VERDICT.md](../../../experiments/methods/test_first_lift_pilot/dev6_tfl_p0_20260731/VERDICT.md)。

**实验臂：** `--arm test_first_lift`（保留可复现；默认研究主线已离开本臂）

**更新时间：** 2026-07-31

## 0. 归档结论（先读）

TFL 回答了关键问题：**“会写测试”≠“会写与 FLB 目标语义对齐的测试”。**

改写假设：

> 对同构 API，生成真实 characterization 可能比实现容易；  
> 对 FLB 大量 cross-API / Adapted / Composite 任务，写正确 paired test
> 本身就要求先解决目标语义映射，难度并不低于模块剥离。
> （Lift 类型见 [LIFT_TAXONOMY.md](../../reference/LIFT_TAXONOMY.md)。）

无 API 消融（冻结 TFL cases × Main submission）显示 TFL 会主动施加错误语义
（Pyramid `commit` 投影）、把 adapter 猜测写进“上游 oracle”
（setuptools_scm schemes）、以及断言过粗（Pytest 只记 BaseException）。
`returns` 近同构成功能工作。成本约 Main 的 **2.71×**。

**下一步不是修 TFL**，而是
[CONTRACT_CLOSURE_AUDIT.md](../plans/CONTRACT_CLOSURE_AUDIT.md)，随后候选主线
[METHOD_SPEC_CLOSURE.md](METHOD_SPEC_CLOSURE.md)。

## 1. 一句话（原主张，已证伪为充分条件）

在 Full-Repository / No-Hint / test-blind 不变的条件下，强制同一个 Agent
先把原仓库当作可执行 oracle，自主编写少量、带完整 setup 的
characterization cases；Harness 只执行上游、记录并冻结答案；随后 Agent
再实现 `featurelifted`，并用自己冻结的 cases 获得执行反馈。

```text
TASK + full repo
  → Agent 自主测试/调试原仓库并写 paired cases
  → Harness 独立双跑 upstream，冻结 observation
  → 同一 Agent 实现 featurelifted
  → 对冻结 oracle 做 characterization verify
  → 无条件进入 private formal evaluator
```

原主张：

> **在模块剥离前强制进行上游 characterization，能否相对 Main 提高
> Functional Pass@1。**

正式答案：**不能**（dev-6：1/6 vs Main 2/6）。上游答案经错误 adapter 仍可
成为错误目标契约。
## 2. 为什么是这条路

现有实验把问题定位到“测试来源和行为闭包”：

- TD-Cognition：Agent 自编探针，但答案也由 Agent 自己猜；12 题相对 Main
  零翻盘。
- clean3：模板约束能提升部分 public，但出题质量决定上限；held-out clean-6
  与 Main 同为 2/6。
- Self-Authored：Alembic 写 101 个、Click 写 41 个自编 tests，内部全部通过，
  formal 仍 0/2；空包必红挡不住错误故事。
- PDR：候选后自由探针与二次修复增加 16.99M tokens，clean-6 Functional
  仍为 2/6。
- FCEC：dependency doctor 已让 selected upstream pytest 6/6 通过，但 raw
  call trace 无法重建 receiver pre-state，也无法自动跨越 FLB adapter；
  dev-6 为 0/6 admission。

TFL 只改一个核心变量：

```text
Agent 既出问题又猜答案
        ↓
Agent 只决定怎么问；原仓库执行决定答案
```

## 3. 与 R2E 的关系及 FLB 适配

最接近的先行工作是 R2E（ICML 2024）：

- R2E 让 LLM 为真实函数/方法生成 equivalence-test harness；
- 原实现作为 reference oracle，避免 LLM 预测 expected output；
- harness 包含文件、对象、依赖等完整 setup，而不是只生成原始 I/O；
- self-equivalence 过滤错误或随机测试，并用 coverage 评价强度。

参考：

- R2E 代码（MIT）：<https://github.com/r2e-project/r2e>
- R2E 论文与方法：<https://r2e.dev/>
- Repo2RLEnv 的小型 R2E-style 实现（Apache-2.0）：
  <https://huggingface.github.io/Repo2RLEnv/pipelines/equivalence_tests/>

TFL 不宣称发明 equivalence testing。它适配 R2E 尚未覆盖的 FLB 条件：

| 维度 | R2E 常见设定 | TFL / FLB |
| --- | --- | --- |
| 生成时机 | 离线生成 benchmark harness | **推理时在线生成**，是方法轨迹的一部分 |
| 粒度 | 单函数/方法 | **模块级 API、签名、状态与行为闭包** |
| 接口关系 | reference/candidate 通常同签名 | 上游与 `featurelifted` 可重命名、改签名、重封装 |
| 状态 | 以局部 FUT setup 为主 | 需要 Agent 主动构造 receiver pre-state 和操作序列 |
| 谁使用测试 | 后续代码生成 Agent | 同一个 Agent 先写 case，冻结后再剥离 |
| 结果指标 | equivalence harness 通过 | private public ∧ hidden 的 FLB Functional |

因此工程上不引入整套 R2E。FLB 已有 repo snapshot、Docker、dependency
doctor、Agent runner 和 formal evaluator；只重写一个薄的
**adaptive equivalence layer**，并在论文中明确引用 R2E。

## 4. 方法不变量

### 4.1 可见性

Agent 可见：

- `TASK.md` 与完整公开功能契约；
- Required Output API；
- `repo/` 完整原仓库；
- 自己生成的 characterization 与 Harness 记录的 oracle。

Agent和方法均不可见：

- benchmark `public_tests/`；
- `hidden_tests/`；
- evaluation capsule；
- formal 失败日志；
- 任何研究者根据 formal 结果回填的场景、字面量或提示。

### 4.2 自主权边界

Phase A 的 Agent 自己决定：

- 搜索哪些源文件和上游 tests；
- 使用 pytest、Python 脚本还是 `pdb`；
- 测哪些公开行为；
- 如何构造输入、fixture、临时文件和对象前置状态；
- 如何把上游 API 场景适配到 `featurelifted` API；
- 投影返回值、异常或状态中的哪些稳定字段；
- 写多少 cases（上限 15）。

Harness 不选择测试、不生成行为断言、不做 raw call replay，也不把 coverage
目标变成新的 TASK 要求。Harness 只负责执行、规范化、冻结和比较。

### 4.3 因果范围

主方法使用**同一个 Agent、同一个连续上下文**：

- Phase A 的动态探索记忆属于方法机制；
- freeze 是强制阶段边界；
- Phase B 不能修改已冻结的 case/oracle。

“Phase B 换一个全新 Agent”只作为以后可能的机制消融，用于区分认知收益与
测试产物收益；不进入 v1 主实验。

## 5. 工作区与最小 case API

```text
workspace/
  TASK.md
  metadata.json
  repo/
  characterization/
    README.md
    REQUIRED_API.json
    case_*.py
  flb-test-first
  oracle.json
  characterization.lock
  submission/
    featurelifted/
```

每个 case 是普通 Python 文件，定义：

```python
CASE_ID = "stable-short-id"
TASK_CLAUSE = "B003 or a faithful public-clause summary"
REQUIRED_API = [
    "featurelifted.Registry.commit",
]


def run_upstream():
    # Agent 自主构造原仓库 receiver、pre-state 与触发操作。
    # 只返回 TASK 相关、稳定、JSON-compatible 的投影。
    return {
        "inputs": {"name": "demo"},
        "pre_state": {"pending": 2},
        "result": None,
        "exception": {"type": "Conflict"},
        "state_after": {"pending": 2},
    }


def run_featurelifted():
    # 使用 TASK Required API 重建语义等价场景。
    # 不允许手写 expected；返回同一 observation shape。
    return {
        "inputs": {"name": "demo"},
        "pre_state": {"pending": 2},
        "result": None,
        "exception": {"type": "Conflict"},
        "state_after": {"pending": 2},
    }
```

这里的“同一场景”是语义要求，不要求两端对象类型或参数名字面一致。FLB 的
adapter 本来就可能改变表示；Agent 必须在两个 runner 中显式写出这种映射。

## 6. Observation 协议

TFL 不序列化整个对象，也不建立通用对象图恢复器。Agent 主动选择一个小而稳定
的投影，Harness 只规范化以下字段：

| 字段 | 含义 | 约束 |
| --- | --- | --- |
| `inputs` | 场景的 canonical 输入摘要 | 可选；不得含 secret、临时绝对路径 |
| `pre_state` | 操作前、TASK 可观察状态 | 可选；只投影公开语义所需成员 |
| `result` / `return` | 返回值的稳定投影 | 可选；JSON-compatible |
| `exception` | 异常类型或公开语义 kind | 不比较 message；不得锁 formal 字面量 |
| `state_after` / `post_state` | 操作后的稳定状态 | stateful case 优先提供 |

规范化规则：

- dict key 排序；
- set 排序；
- bytes 以 UTF-8 replacement 解码；
- 异常只保留 `type`；
- 禁止时间戳、随机 id、内存地址、临时绝对路径等非确定性信息；
- 每次 upstream 执行在独立进程中完成，两次 canonical JSON 必须一致。

Observation 的字段集合就是该 case 的轻量 schema；v1 不增加独立 DSL、AST
dataflow verifier 或通用 serializer。

## 7. 两阶段协议

### 7.1 Phase A — Characterize

Agent首先只做动态理解：

1. 阅读 TASK 和 Required API；
2. 在 `repo/` 中搜索相关实现与上游 tests；
3. 实际运行代码，可使用 pytest/脚本/`pdb`；
4. 在 `characterization/` 写 1–15 个 paired cases；
5. 每个 Required callable/path 至少出现在一个 case 的 `REQUIRED_API`；
6. 运行 `./flb-test-first freeze`。

禁止：

- 在 observation 或 candidate runner 中硬编码从 formal 获得的答案；
- 使用 benchmark evaluator 文件；
- 用 `assert True`、空 case 或只检查 import 代替行为；
- 让 `run_featurelifted()` 返回常量而不调用目标 API；
- 为通过 freeze 而删除公开契约要求。

### 7.2 Freeze — Harness 记录上游答案

`./flb-test-first freeze` 对每个 case：

1. 校验最小接口和唯一 `CASE_ID`；
2. 在两个独立进程中运行 `run_upstream()`；
3. 要求两次规范化 observation 完全一致；
4. 写入 Harness-owned `oracle.json`；
5. 用临时空 `featurelifted` 运行 `run_featurelifted()`；
6. **每个 case** 都必须相对空包失败或与 upstream observation 不同；
7. 检查 Required API 声明覆盖；
8. 清空任何 pre-freeze submission；
9. 对 `characterization/` 与 `oracle.json` 共同计算 lock；
10. 写入 `characterization.lock`，进入 Phase B。

Freeze 失败时，Agent可在 Phase A 剩余预算内修正 cases 后重试；不启动独立的
批评 Agent 或 PDR repair Agent。

Required API 声明覆盖只是防漏清单，例如防止再次漏掉 Click `invoke`；它不是
case 语义正确性的证明。最终正确性仍由 formal Functional 决定。

### 7.3 Phase B — Lift

Freeze 成功后，同一个 Agent：

1. 从空 `submission/` 开始；
2. 实现独立的 `submission/featurelifted/`；
3. 不得运行时 import、访问或打包原仓库；
4. 运行 `./flb-test-first verify`；
5. 只能修改 submission，不能修改 characterization/oracle/lock。

`verify` 对每个 case：

```text
run_featurelifted()
→ normalize
→ compare with frozen upstream observation
```

本地 characterization 失败不触发第二个 Agent，也不阻止 formal。

### 7.4 Formal — 无条件评测

所有完成/超时/本地失败的 method outcomes 都进入统一结果表：

- 有 submission：无论 characterization 是否绿，都运行 private formal；
- 无 submission：记 missing submission / Functional fail，不从分母剔除；
- Phase A 未 freeze：单列 `freeze_failed`，不得伪称 execution-guided success；
- headline 始终是 formal Functional，而不是 freeze 或 characterization pass。

## 8. Gate：只防空，不替 Agent 做语义判断

TFL v1 只保留下列机械条件：

| 条件 | 目的 |
| --- | --- |
| 1–15 个合法 cases | 防空产物和无限膨胀 |
| upstream 独立双跑稳定 | 防 flaky/global-state 假绿 |
| Harness 写 oracle | Agent 不猜 expected |
| 每个 case 空包必红 | 防常量/vacuous case |
| Required API 声明覆盖 | 防明显漏方法 |
| characterization + oracle lock | 防 Phase B 改题 |
| formal 无条件执行 | 防选择性报告 |

v1 明确不做：

- 自动 trace → replay；
- 通用 receiver serialization；
- AST 参数流/taint 证明；
- coverage 强门；
- mutation search；
- formal-feedback repair；
- 第二个测试 Agent、批评 Agent 或实现 repair Agent；
- CoverUp 内嵌 LLM loop；
- PDR/CGCC 叠加。

如果简单协议不能提升 Functional，应接受负结果，而不是继续叠门禁把 Harness
变成另一个实现者。

## 9. 与现有工具的复用边界

| 工具/工作 | v1 用法 | 不采用 |
| --- | --- | --- |
| R2E | 借 equivalence oracle、完整 setup、自等价验证思想 | 不引入整套 extractor/RPyC/Docker |
| Repo2RLEnv | 借 stub-fail / oracle-pass 质量门 | 不限于 pure top-level function |
| Pynguin | 可由 Agent 自主尝试，作为输入探索草稿 | 不作为强制依赖或最终 adapter |
| CoverUp | 借鉴重复执行与 coverage feedback | 不嵌套第二个 LLM loop |
| debug-gym | 借鉴 debugger 是 Agent action space 的观点 | v1 不替换 OpenHands runtime |
| FLB FCEC | 复用 dependency doctor、Docker 与审计经验 | 不复用 raw trace replay |
| FLB Self-Contract | 复用 freeze/hash 经验 | 不接受 Agent 自写 expected |

## 10. 公平性与非泄漏

### 10.1 与 Main 相同

- 相同模型与版本；
- 相同 Full-Repository / No-Hint TASK；
- 相同 agent/evaluator Docker；
- 相同 formal evaluator；
- 相同 attempt=1；
- 相同 benchmark-test-blind 可见性；
- 尽量使用相同总 step/token 上限。

TFL 允许 Agent自行把预算分配给 characterization 和 implementation；这正是
方法干预。额外 API calls、tokens、wall time 必须完整报告。

若 TFL 后续有正结果，再增加 matched-compute Main，排除“仅仅多算了”的解释；
matched-compute 不是 dev-6 Phase A 基础设施门槛。

### 10.2 Eval-blind 允许项

允许：

- TASK/public_spec；
- Required API；
- 原仓 source/tests/config；
- 从原仓实际执行得到的 observation；
- 与上述信息机械相关的稳定性、覆盖和锁检查。

禁止：

- public/hidden evaluator tests；
- formal 失败类型、文案、输入或图结构；
- 根据 formal 结果修改 case prompt、gate 或 oracle；
- 用已打开任务的 formal 尸检生成新方法规则，再把同题称为 clean evidence。

## 11. 审计产物

每题至少保存：

```text
test_first_lift_freeze.json
test_first_lift_phase.json
oracle.json
characterization.lock
characterization/
agent/
submission/
eval/result.json
```

`test_first_lift_phase.json` 至少报告：

- `freeze_success`；
- `valid_case_count`；
- `required_api_coverage`；
- upstream 双跑失败原因；
- stub-fail 结果；
- lock/freeze 校验；
- `characterization_pass`；
- Agent return code、timeout、tokens、steps、latency；
- formal public/hidden/Functional。

原始 run 产物写入 `experiments/`，不覆盖旧结果，不提交 secret 或 `.env`。

## 12. 实验设计与预注册

### 12.1 开发集

只使用已经打开的 PDR/FCEC dev-6：

```text
pyramid__configurator_action_core__hard3_001
pytest__marker_registry_core__hard3_001
setuptools_scm__version_normalize_core__hard3_001
poetry_core__dependency_groups_core__hard3_001
returns__result_pipeline_core__hard3_001
parsel__selector_namespace_core__hard3_001
```

它们不再是 held-out evidence，只用于机制淘汰。默认对照是已冻结 Main：
Functional 2/6。

### 12.2 分阶段 go / no-go

Phase A 基础设施门：

- ≥4/6 `freeze_success`；
- 每个成功任务至少一个非空、稳定、空包必红的 case；
- 成功任务 Required API 声明覆盖 100%；
- 无 evaluator 访问、oracle 篡改或 freeze 语义违规。

低于 4/6：

- 停止，不启动大规模 Implementation；
- 只允许修通通用基础设施错误；
- 不得根据 formal 失败补场景。

完整 dev-6 方法门：

- 相对 Main 至少 **2 个 Functional flips**；
- **0 个 Functional regressions**；
- 所有结果均按 formal 计，不按本地 contract 选择；
- 报告成本，不以 token 增长掩盖零收益。

未达到：TFL v1 记为负结果，停止扩样本。

达到：冻结方法代码、prompt、gate、Docker digest 与任务选择规则，再抽新的
untouched hard clean-6。

### 12.3 运行命令

```bash
./run_experiment.sh --arm test_first_lift \
  --task-file experiments/methods/test_first_lift_pilot/task_ids_dev6.txt \
  --workers 1 --timeout 3600 --docker
```

单题机制 smoke：

```bash
./run_experiment.sh --arm test_first_lift \
  --tasks returns__result_pipeline_core__hard3_001 \
  --workers 1 --timeout 3600 --docker
```

在 Phase A/pilot 正式调用外部模型前，仍需按具体方法臂确认对应 TASK/repo
派生数据的 API 发送授权；既有 Main/PDR 授权不自动扩张为 TFL 授权。

## 13. P0 完成状态与 METHOD_FREEZE

现有实现：

```text
harness/featureliftbench/test_first_lift/
harness/scripts/flb_test_first.py
harness/tests/test_test_first_lift.py
```

### 13.1 P0 清单（2026-07-31 完成）

| # | 要求 | 状态 |
| --- | --- | --- |
| 1 | lock 覆盖 `characterization/` + `oracle.json`；verify 兼容 legacy 仅 characterization 锁 | 完成（`lock_schema=v2\|legacy`） |
| 2 | empty-stub 逐 case 必红；任一 `vacuous_pass` 则 freeze fail | 完成 |
| 3 | freeze 成功清空 `submission/`，不 restore pre-freeze backup | 完成 |
| 4 | 无 submission / freeze fail 仍计入 suite 分母；formal 路径无条件 | 完成（`included_in_suite_denominator`） |
| 5 | `test_first_lift_phase.json` 分离 `freeze_success` / `characterization_pass` / `formal_functional` | 完成（phase v2） |
| 6 | upstream vs featurelifted PYTHONPATH 域隔离 | 已有（`cases._pythonpath_for_target`）；returns smoke 通过 |
| 7 | 单测：oracle/case tamper、legacy lock、flaky、vacuous、per-case stub、Required API、submission cleared、phase 指标 | 完成 |
| 8 | 方法源码 / prompt / image digest 记录字段 | 见 §13.2 |

### 13.2 METHOD_FREEZE（正式 pilot 审计字段）

正式 Phase A / full 结果必须可追溯下列冻结记录（写入 suite/`run.json` 的
`benchmark_freeze` / `experiment_conditions`，并在报告中复述）：

| 字段 | 含义 |
| --- | --- |
| `tfl_package_tree_sha256` | `harness/featureliftbench/test_first_lift/**/*.py` 树哈希 |
| `tfl_task_appendix_sha256` | `task_appendix()` 文本 SHA-256 |
| `tfl_openhands_appendix_sha256` | `openhands_appendix()` 文本 SHA-256 |
| `agent_runtime.image_id` | agent Docker image digest |
| `evaluator_runtime.image_id` | eval Docker image digest |
| `model` / `agent_profile` | 与 Main 对照相同的模型与 profile 族 |
| `lock_schema` | 每题 `v2`（正式）或 `legacy`（仅 smoke 兼容） |

P0 合入时参考快照（启动正式 pilot 前应重算确认）：

```text
tfl_package_tree_sha256 =
  46aca5c1b37c2134968779ee7fd54842c8609ad0f8669220520b9e2907bd57d1
tfl_task_appendix_sha256 =
  3a7407ef4127f4e0bbdb9d941b90d484857fcf790dfbe5d5ff42bf5728cd5b9a
tfl_openhands_appendix_sha256 =
  3a7407ef4127f4e0bbdb9d941b90d484857fcf790dfbe5d5ff42bf5728cd5b9a
agent image (featureliftbench-agent:latest) =
  sha256:cc6229204b71d871ebd3eea0a251c9947e8b5631aeb652a4159d8591d43033fe
eval image (featureliftbench-eval:latest) =
  sha256:cccf858c5f9b278de16bf9317aa032fd61c022dd1c257016ab08d5b68990f368
```

正式命令（**仅复现归档实验**；勿作为继续开发入口）：

```bash
./run_experiment.sh --arm test_first_lift \
  --task-file experiments/methods/test_first_lift_pilot/task_ids_dev6.txt \
  --docker --workers 1 --timeout 3600 \
  --output experiments/methods/test_first_lift_pilot/dev6_tfl_p0_YYYYMMDD
```

`dev6_20260731` = unofficial smoke；`dev6_tfl_p0_20260731` = 正式负结果。  
Headline：formal Functional − Main Functional = **−1**。不再扩样本。

## 14. 预期、风险与可证伪性

为什么可能有效：

- Agent擅长通过搜索和运行代码构造具体状态，比通用 tracer 自动恢复对象状态更
  灵活；
- 原仓而非 Agent 提供答案，降低 Self-Authored/TD 的错误 oracle 风险；
- Required API 清单降低漏方法；
- 同一上下文保留 Phase A 动态理解，符合“动态分析带动剥离”的原始机制。

为什么仍可能失败：

- Agent选择的场景浅、偏或只覆盖易分支；
- 上游与 target adapter 语义映射仍可能写错；
- TASK/evaluator 本身不闭合的要求无法从干净协议中恢复；
- 测试覆盖率不等于行为闭包；
- Phase A 消耗实现预算；
- 自己写的投影可能丢掉关键 state。

因此预期只写成可证伪假说，不预测具体任务成功顺序。Headline 结论只能来自：

```text
TFL Functional − Main Functional
```

而不能来自 freeze、case 数、coverage 或 characterization 全绿。

## 15. 论文定位

若结果为正，方法贡献可表述为：

> **Online agent-authored adaptive equivalence testing for module lifting：**
> 在 repository-level、cross-API、stateful feature extraction 中，让同一代码
> Agent 在实现前自主构造 reference-grounded characterization harness，并将
> 上游动态行为冻结为执行反馈。

必须同时说明：

- equivalence-test oracle 思想继承 R2E；
- 新点是 online inference-time protocol、模块/API adapter/state closure、
  Full-Repo/No-Hint/test-blind 设定，以及相对 Main 的 Functional 验证；
- 若 dev/held-out 未提升，结论是该适配未获支持，而不是把 gate success 当成
  方法成功。

若结果为负，TFL 仍能形成清晰边界：

> 即使 Agent 可以自主运行原仓并获得真实 oracle，测试选择和跨 API 状态映射
> 仍可能与模块剥离本身同样困难。
