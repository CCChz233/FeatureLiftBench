# FeatureLiftBench 核心概念

本文档用**一条主线**说明 FeatureLiftBench 在测什么、一道题由哪些部分组成、功能如何定义、测试如何验证解耦、Agent 最终要交付什么。

**适合读者：** 第一次接触项目的人、要加题/改题的维护者、读论文式 README 仍觉得信息分散的人。

**相关文档：**

| 文档 | 用途 |
| --- | --- |
| [TASK_FORMAT.md](TASK_FORMAT.md) | 题目目录与 `metadata.json` 的机器可读规范 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 四层目录与数据流 |
| [benchmark_tasks.md](benchmark_tasks.md) | 28 题清单与运行命令 |
| [BENCHMARK_STATUS.md](BENCHMARK_STATUS.md) | 当前 baseline、规格缺口、修复优先级 |
| [task_designs/TEMPLATE.md](task_designs/TEMPLATE.md) | 新题设计笔记模板 |

---

## 1. 我们在测什么

FeatureLiftBench 评估的是 **behavior-preserving feature-level decoupling**（行为保持的功能级解耦）：

> 给定一个**能跑但结构缠绕**的 Python 仓库快照，Agent 能否把**某一个功能切片**从框架、配置、全局状态、无关模块中剥离出来，做成**独立可安装、可测试、相对精简**的 Python 包，且**行为与原实现兼容**。

这与典型 SWE-bench 类任务不同：

| 维度 | SWE-bench 类 | FeatureLiftBench |
| --- | --- | --- |
| 目标 | 修 bug / 实现需求 | 解耦已有功能 |
| 输入 | issue + 仓库 | 固定 commit 仓库 + 功能规格 |
| 输出 | patch / PR | 新的独立 package |
| 主要评分 | 测试是否通过 | 测试通过 **且** 代码体量尽量小 |

当前是 **一个统一 benchmark、28 道题**，均在 `benchmark/tasks/<task_id>/`，共用同一 schema、evaluator 和评分规则。演进方式是**增删题目**，不另建第二套 collection。

评测轨道为 **Decoupling / Extraction Track**：

- 允许从 `repo/` **复制、裁剪、改 import** 相关源码；
- 允许少量胶水代码与 `pyproject.toml`；
- **不允许**把原 PyPI 包或原仓库路径作为运行时依赖；
- **不要求**与人工参考实现逐字一致，但要求行为兼容。

---

## 2. 端到端流程

```text
┌─────────────────────────────────────────────────────────────────┐
│  benchmark/tasks/<task_id>/          （题目，维护者编写）           │
│    repo/              上游仓库固定 commit 快照                    │
│    metadata.json      功能边界、输出 API、环境约束                 │
│    public_tests/      Agent 可见的 pytest                         │
│    hidden_tests/      评测时才跑（Agent 看不到）                   │
│    evaluation/        forbidden_imports、oracle_manifest          │
└───────────────────────────────┬─────────────────────────────────┘
                                │
          run-agent             │  eval（也可直接对已有 submission 阅卷）
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  experiments/<run_id>/workspace/     （Agent 工作区，脱敏副本）    │
│    repo/ + public_tests/ + metadata.json + TASK.md                 │
│    submission/featurelifted/         ← Agent 在这里写答案           │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  harness/featureliftbench/evaluator                               │
│    1. 临时 venv 安装 submission + requirements.lock               │
│    2. build：能否 import featurelifted                            │
│    3. public pytest + hidden pytest（均 import featurelifted）    │
│    4. forbidden import / dependency 静态检查                      │
│    5. 计分：FunctionalGate + ExtractionRatio                      │
└─────────────────────────────────────────────────────────────────┘
```

**关键点：**

- Agent **看不到** `hidden_tests/` 和 `evaluation/`。
- 所有测试 import 的都是 **`featurelifted`**，不是原包名（如 `iniconfig`、`sqlparse`）。
- `eval` 不依赖 Agent；维护者可用 Oracle submission 单独验证题目。

---

## 3. 一道题由什么组成

每道题是 `benchmark/tasks/<task_id>/` 下的固定布局：

```text
benchmark/tasks/<task_id>/
  metadata.json           # 机器可读「题面规格」
  requirements.lock       # 允许安装的第三方依赖（可为空）
  repo/                   # 源仓库快照（Agent 可读）
  public_tests/           # 开发期可见测试
  hidden_tests/           # 评测期隐藏测试
  evaluation/
    forbidden_imports.txt
    oracle_manifest.json  # 维护者用的最小模块闭包清单
```

| 部分 | 谁编写 | 作用 |
| --- | --- | --- |
| `repo/` | 维护者（固定 commit） | Agent 理解原实现的唯一输入 |
| `metadata.json` | 维护者 | 定义功能边界、输出 API、缠绕类型、环境约束 |
| `public_tests/` | 维护者 | 给 Agent 指路的主路径行为 |
| `hidden_tests/` | 维护者 | 卡边界、防硬编码 public、验证解耦完整性 |
| `submission/featurelifted/` | **Agent** | 最终交付的独立包 |

参考答案（Oracle）放在本地 `benchmark/submissions/<task_id>/oracle/`（gitignore），用于回归验证，不是 Agent 输入。

---

## 4. 「功能」是如何定义的

功能不是口头描述，而是由 `metadata.json` 里几组字段**共同划定边界**：

### 4.1 行为边界：`feature`

| 字段 | 含义 |
| --- | --- |
| `feature.name` / `description` | 功能名称与人类可读说明 |
| `feature.source_entrypoints` | 在 `repo/` 里应阅读的 API/模块（**实现范围**，往往较宽） |
| `feature.included_behaviors` | 必须保留的行为清单 |
| `feature.excluded_behaviors` | 明确不要带出的东西（CLI、原测试、CI 等） |

### 4.2 对外接口：`output`

| 字段 | 含义 |
| --- | --- |
| `output.package` | 固定为 `featurelifted` |
| `output.import` | Agent 必须暴露的 import 语句（**对外 API 摘要**） |
| `output.callable` / `signature` | 主入口函数 |

### 4.3 缠绕上下文：`entanglement`

标注目标功能与原仓库的耦合类型（框架耦合、配置耦合、全局状态等），用于分析和报告，**不改变**评分公式。

- **`types`**：可多选，描述叠加的耦合面（共 9 种 enum）。
- **`primary`**：互斥主类（7 种之一），用于论文图表与 `report_entanglement_coverage.py`；必须同时出现在 `types` 里。`global_state_registry_coupling` 与 `implicit_dependency_coupling` 仅作 secondary tag。

### 4.4 运行时约束：`environment`

- `network: false` — 评测禁网（靠 pip `--no-index`，非容器防火墙）
- `allowed_dependencies` / `forbidden_dependencies` — 依赖白名单/黑名单
- `forbidden_imports` — submission 源码中禁止出现的 import 名（如 `iniconfig`）

### 4.5 三层规格的关系（重要）

维护者设计题目时，实际上有三层「规格」，宽度不同：

```text
feature.source_entrypoints   ← 最宽：在 repo 里该看哪些实现
        ⊇
metadata.output.import       ← 中等：对外应暴露哪些符号
        ⊆  （理想情况应覆盖测试 import 的全部符号）
public_tests + hidden_tests  ← 最具体：用 pytest 断言的行为
```

**设计原则：**

- `source_entrypoints` 告诉 Agent「去哪里找代码」。
- `output.import` 告诉 Agent「包表面应暴露什么」——应覆盖 **public 与 hidden 测试里 import 到的所有符号**。
- `included_behaviors` 是行为方向的摘要；**hidden 测试可以比它更细**（functional discriminator），测 oracle 级细节如错误文案、边界参数。
- 若 `output.import` 比测试窄，Agent 容易只做「最小 API」而在 hidden 上失败。当前已知缺口见 [BENCHMARK_STATUS.md](BENCHMARK_STATUS.md)。

### 4.6 示例：`iniconfig__parse_config__001`

```json
"feature": {
  "name": "INI configuration parsing",
  "source_entrypoints": [
    "iniconfig.IniConfig",
    "iniconfig.ParseError",
    "iniconfig.iscommentline",
    "iniconfig.COMMENTCHARS"
  ],
  "included_behaviors": [
    "parse INI sections and key-value entries",
    "support multiline value continuations",
    "report parse errors with source path and line numbers"
  ],
  "excluded_behaviors": [
    "original project tests",
    "development tooling and CI configuration"
  ]
},
"output": {
  "package": "featurelifted",
  "import": "from featurelifted import IniConfig, ParseError, iscommentline, COMMENTCHARS",
  "callable": "featurelifted.IniConfig"
}
```

同一上游仓库可以拆多道题（如 sqlparse×4、jinja2×4）：`repo/` commit 相同，`feature` / `output` / tests 不同。

---

## 5. Agent 看到什么

`run-agent` 生成脱敏 workspace，并写入 `TASK.md`（由 `harness/featureliftbench/agent_runner.py` 的 `build_task_prompt()` 生成）。

**Agent 可见：**

- `repo/`、`public_tests/`、`requirements.lock`
- 脱敏后的 `metadata.json`（无 hidden 路径、无 `scoring_reference`）
- `TASK.md`（含工作流、Required Output API、约束）

**Agent 不可见：**

- `hidden_tests/`
- `evaluation/`

`TASK.md` 核心结构示意：

```markdown
# FeatureLiftBench Task: iniconfig__parse_config__001

## How to work
1. 读 source entrypoints 与 Required Output API
2. 从 repo/ 拷贝最小实现闭包到 submission/featurelifted/
3. 改写 import，禁止原包名
4. grep 自检 forbidden imports
5. pytest public_tests/
6. public 过 ≠ 完成（还有 hidden）
7. 提交

## Target Feature
- Source entrypoints / Included / Excluded behaviors ...

## Required Output API
- Package: featurelifted
- Import: from featurelifted import IniConfig, ...

## Constraints
- Forbidden imports 是 hard gate
- final_score = functional_gate × (1 - extraction_ratio)
```

---

## 6. 测试如何验证解耦效果

### 6.1 测的是谁

所有 pytest **只测 Agent 产出的 `featurelifted` 包**，例如：

```python
from featurelifted import IniConfig, ParseError
```

评测器在临时 venv 中安装 `submission/`，再跑测试。原仓库不在 `PYTHONPATH` 里。

### 6.2 public vs hidden

| | public_tests | hidden_tests |
| --- | --- | --- |
| Agent 能否看到 | 能，可复制到 workspace | 不能 |
| 主要目的 | 主路径 API、常规输入、基础错误 | 边界、组合场景、迁移自原仓库的 edge case |
| 设计约束 | 不暴露 hidden 的具体用例 | 不应只是重复 public 的同类样例 |

**iniconfig 示例：**

- public：`test_basic_parse_iteration_and_lookup` — 基础 section/key 解析
- hidden：`test_multiline_values_and_file_order` — 多行值、从文件读取、unicode 空白等

### 6.3 测试验证的两件事

**（1）功能正确性 — `FunctionalGate`**

三项全过才为 `1.0`，任一项失败则为 `0`：

| 门控 | 检查内容 |
| --- | --- |
| BuildPass | `featurelifted` 能在干净 venv 安装/导入 |
| TestPass | public + hidden pytest 全过 |
| OriginalImportPass | submission 未 import 原包名/禁止依赖 |

> 典型陷阱：`click` 题 public 全过，但 submission 里仍有 `import click` → gate = 0。

**（2）解耦质量 — `ExtractionRatio`**

```text
ExtractionRatio = submission 的 Python LOC / repo 的 Python LOC
```

越低越好。整包复制（Copy-All）通常能通过功能门，但 `ExtractionRatio ≈ 1`，`final_score ≈ 0`。

```text
final_score = FunctionalGate × clamp(1 - ExtractionRatio, 0, 1)
```

功能不过时 `final_score = 0`，不讨论体积。

### 6.4 当前测试规模（50 hard + 3 smoke）

| 类型 | 测试函数数 |
| --- | ---: |
| public（50 hard） | 94 |
| hidden（50 hard） | 148 |
| smoke（3 题） | 26 |
| **主榜合计** | **242** |

每题通常 1 个 public 文件 + 1 个 hidden 文件；单题约 **3–8** 个 `def test_*`（当前 hard 平均 ~4.8）。

---

## 7. 最终交付物：可复用的独立包

**是。** Agent 必须在 `submission/` 下产出一个可独立运行的 Python package：

```text
submission/
  pyproject.toml          # 推荐
  featurelifted/          # 包名固定（所有题统一）
    __init__.py
    ...                   # 从 repo 裁剪/改写后的实现
```

要求摘要：

1. 不依赖原仓库路径、原包名、网络
2. 只使用 `allowed_dependencies` 与 `requirements.lock` 中的依赖
3. 通过 public + hidden 行为测试
4. 尽量只包含目标功能相关代码
5. 禁止压缩/加密/动态生成主逻辑等投机行为（见根 README「反投机规则」）

解耦结果**不必唯一**；评分只看行为是否正确 + 体积是否够小。

---

## 8. 维护者如何验证题目设计正确

加题或改题时，建议按以下顺序验收：

### Step 1 — 结构校验

```bash
pip install -e .
featureliftbench validate-task benchmark/tasks/<task_id>/
```

检查目录、metadata schema、依赖集合冲突等（**不跑测试**）。

### Step 2 — 构建 Oracle 并通过 eval

```bash
python3 harness/scripts/build_oracle_submission.py benchmark/tasks/<task_id>/

featureliftbench eval \
  benchmark/tasks/<task_id> \
  benchmark/submissions/<task_id>/oracle \
  --output experiments/validate-<task_id>
```

Oracle 必须：`functional_gate = 1.0`，且 `extraction_ratio` 明显低于 Copy-All。

### Step 3 — Copy-All 对照

整包复制型 submission 应：

- **功能上能通过**（说明测试没有过严到连原实现都挂）
- **分数很低**（说明体积指标能区分「解耦」与「复制」）

### Step 4 — Module Probe（hard 题推荐）

从 Oracle 闭包中**删掉**某个模块 → 对应 hidden test **必须失败**。证明 hidden 真的在测必要实现，而非装饰。

记录在设计笔记 `docs/task_designs/<task_id>.md`（模板见 [TEMPLATE.md](task_designs/TEMPLATE.md)）。

### Step 5 — Agent 校准（可选）

用 `run-agent` 跑 1–2 个模型，看失败是否落在预期边界（spec 问题 vs 模型能力问题）。

---

## 9. 快速上手命令

**列出全部题目：**

```bash
python3 harness/scripts/list_tasks.py
```

**对已有 submission 阅卷：**

```bash
featureliftbench eval \
  benchmark/tasks/iniconfig__parse_config__001 \
  path/to/submission \
  --output experiments/manual-eval
```

**跑 Agent（单题）：**

```bash
python3 -B -m featureliftbench.cli run-agent \
  benchmark/tasks/iniconfig__parse_config__001 \
  --agent mini-swe-agent \
  --agent-config harness/config/agents.toml \
  --env-file .env \
  --yolo \
  --output experiments/mini-swe-agent/iniconfig-smoke
```

**跑全量 28 题：** 见 [benchmark_tasks.md](benchmark_tasks.md)。

需要 **Python 3.11+**。批量跑 mini-swe-agent 建议加 `--yolo`（非交互确认）。

---

## 10. 已知限制（读概念时一并了解）

- 评测默认用**本地 venv**（显式安装 `pytest==7.4.4`）；可选 **Docker eval**（`featureliftbench eval --docker`）→ [limitations.md](limitations.md)
- `metadata` 与测试/题面尚未完全对齐 → [BENCHMARK_STATUS.md](BENCHMARK_STATUS.md)
- Oracle 未 28 题全部纳入系统化回归
- `scoring_reference` 仅供人工对比，evaluator 不使用

---

## 11. 术语表

| 术语 | 含义 |
| --- | --- |
| Task / 题目 | `benchmark/tasks/<task_id>/` 整套目录 |
| Feature / 功能切片 | `metadata.feature` 定义的行为边界 |
| Submission | Agent 在 `submission/` 下的输出 |
| `featurelifted` | 所有题目统一的输出包名 |
| FunctionalGate | 功能三门闩（build + test + no forbidden import） |
| ExtractionRatio | 解耦后代码量占原 repo 的比例 |
| Oracle | 人工标注接近最小的参考解耦答案 |
| Copy-All | 整包复制 baseline，用于体积下界 |
| Public / Hidden tests | Agent 可见 / 不可见的 pytest |
| Entanglement | 功能与原仓库的缠绕类型标注 |
