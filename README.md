# FeatureLiftBench

**Concepts (start here):** [docs/CONCEPTS.md](docs/CONCEPTS.md) · **Architecture:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) · **Task format:** [docs/TASK_FORMAT.md](docs/TASK_FORMAT.md) · **Benchmark status:** [docs/BENCHMARK_STATUS.md](docs/BENCHMARK_STATUS.md) · **Directory map:** [docs/DIRECTORY.md](docs/DIRECTORY.md) · **Task catalog:** [docs/benchmark_tasks.md](docs/benchmark_tasks.md)

**FeatureLiftBench: Can Code Agents Decouple Features from Entangled Repositories?**

中文名称暂定为：

**FeatureLiftBench：面向缠绕仓库的功能级解耦评测基准**

FeatureLiftBench 是一个面向代码智能体的仓库级评测基准，用于评估 Agent 能否在保持目标功能行为正确的前提下，将该功能从原仓库的框架、配置、状态、资源、环境和无关模块中解耦出来，形成一个**独立可安装、可测试、相对精简、可复用**的 Python package。

与主要关注 bug 修复或功能实现的 SWE benchmark 不同，FeatureLiftBench 关注一种更贴近维护场景的能力：

> Agent 能否面对“能跑但结构混乱、功能边界不清、依赖缠绕”的仓库，重新理解已有功能，将它解耦、抽取、重组为可复用的软件单元？

## 项目动机

未来软件工程中的一个重要问题，不只是“模型能不能写代码”，而是“模型能不能把已经存在但结构混乱的代码重新理解、解耦、抽取和复用”。

这种问题会越来越常见：

* **Vibe coding 项目**：代码能跑，但目录组织随意、冗余较多、模块边界不清、隐式依赖和全局状态混在一起；
* **传统 legacy code**：功能散落在历史模块、框架适配层、配置系统、资源文件和兼容逻辑中，文档缺失，修改风险高；
* **快速增长的内部工具**：最初只是脚本或 demo，后来承载真实业务，却没有形成高内聚、低耦合的结构。

真实软件维护不只包括“修 bug”和“加功能”。开发者经常需要从复杂或缠绕的仓库中解耦出某个稳定功能，例如：

* 将一个 parser 从完整工具链中拆出来；
* 将一个 formatter 或 converter 做成独立库；
* 将 CLI 的一个子命令变成可复用 API；
* 从历史项目中抽取稳定 utility，去除框架、配置和运行时依赖；
* 从 vibe-coded app 中剥离一个业务规则、数据转换器、模板渲染器或配置解析器。

这个过程要求 Agent 具备以下能力：

* 理解目标功能的行为边界；
* 识别必要文件、函数、类、数据文件、配置和外部依赖；
* 将目标功能从框架、全局状态、环境变量、资源路径和无关模块中解耦；
* 保持原有 API 行为兼容；
* 删除无关代码、测试、文档、构建配置和历史兼容包袱；
* 在没有原始仓库路径的干净环境中运行。

FeatureLiftBench 的目标是系统评估这种“功能级解耦”能力，而不是单纯评估代码补全、bug 修复或测试驱动重写能力。

## 现实意义

FeatureLiftBench 的现实意义在于评估代码智能体能否把“能跑但混乱”的已有仓库转化为更模块化、可复用、可维护的软件资产。

现有很多代码 Agent benchmark 主要关注 bug fixing 或 feature implementation；但真实工程中还存在大量维护任务：理解已有代码、识别功能边界、剥离框架和配置耦合、裁剪隐式依赖，并在保持行为正确的前提下形成独立模块。这类任务在传统 legacy code 中长期存在，也会随着 vibe coding 产生的大量原型和内部工具变得更普遍。

因此，FeatureLiftBench 关注的是一种补充性的工程能力：**behavior-preserving feature-level decoupling**，即在行为保持约束下，从缠绕仓库中恢复出清晰、可安装、可测试、可复用的功能模块。

## 缠绕仓库口径

这里的 **entangled repository / 缠绕仓库** 指的是：目标功能虽然已经存在并能运行，但它与仓库中的其他结构耦合在一起，难以直接复用。常见缠绕形态包括：

* **Framework coupling**：目标逻辑依赖 CLI、Web framework、插件系统、测试框架或应用生命周期；
* **Config/environment coupling**：行为由配置文件、环境变量、默认路径或运行时 settings 隐式控制；
* **Global state / registry coupling**：逻辑依赖 singleton、全局 registry、cache、hook manager 或副作用初始化；
* **Resource coupling**：功能需要模板、schema、locale、grammar、测试数据或其他资源文件；
* **Implicit dependency coupling**：跨模块 import 链长，必要依赖和无关依赖混在一起；
* **Legacy/vibe-coded clutter**：重复代码、历史兼容层、未使用模块、命名混乱、文档缺失。

当前 benchmark **主榜 50 道 hard**（`benchmark/tasks/`），另有 **3 道 smoke**（`benchmark/sanity/`）。均在统一 schema、evaluator 与评分规则下；题目之间主要差别是 **`difficulty`**、**`entanglement`** 和 **功能范围**。完整清单见 [`docs/benchmark_tasks.md`](docs/benchmark_tasks.md)；架构说明见 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)。

演进方式：**新增或删除** `benchmark/tasks/` 下的题目，不另建第二套 benchmark 或 harness。

## 任务定义

每个 benchmark 样例给定：

* 一个真实开源仓库的固定 commit；
* 一个目标功能或目标解耦对象描述；
* 一个或多个源入口 API；
* 一个期望输出 API；
* public tests；
* hidden tests；
* 任务级约束和评测规则。

Agent 需要在 `submission/` 目录下生成一个解耦后的 Python package。该 package 必须满足：

1. 可以在干净环境中独立安装或导入；
2. 不依赖原始仓库目录、原始仓库包名或网络资源；
3. 通过目标功能的 public 和 hidden tests；
4. 尽量少包含与目标功能无关的代码和依赖；
5. 保持可读、可审查的源码形态，不能通过压缩、加密、动态生成等方式规避体积指标。

本项目不要求 Agent 输出与人工参考解耦版本完全一致。功能级解耦结果可能不唯一，所以 FeatureLiftBench 当前主要从**行为正确性**和**解耦 footprint** 两个方面评价：功能必须正确，代码规模相对原仓库越小，说明越少携带无关缠绕结构。

## 解耦与重写边界

FeatureLiftBench 默认评测 **Decoupling / Extraction Track**：

* 允许复制、裁剪和适配原仓库中与目标功能相关的源码；
* 允许为独立运行补充少量胶水代码、包装代码和构建配置；
* 不要求逐字保留原实现；
* 不允许完全绕开原实现，基于测试样例重新写一个窄实现；
* 不允许把原始仓库或原始 PyPI 包作为运行时依赖。

后续可以单独增加 **Rewrite Track**，用于评估 Agent 根据功能说明重写模块的能力。但 Rewrite Track 必须与 Decoupling / Extraction Track 分开报告，否则“理解并解耦已有代码”和“按说明重新实现”两类能力会混在一起，影响结论。

## Submission 格式

每个 Agent 输出必须放在固定目录中：

```text
submission/
  pyproject.toml          # 推荐；如果没有，评测器会尝试直接 import
  featurelifted/
    __init__.py
    ...
```

任务的 `metadata.json` 会指定期望输出 API。例如：

```json
{
  "output": {
    "package": "featurelifted",
    "import": "from featurelifted import slugify",
    "callable": "featurelifted.slugify",
    "signature": "slugify(text, **kwargs)"
  }
}
```

评测器只保证从 `submission/` 构建和安装 Agent 输出，不会把原始仓库加入 `PYTHONPATH`。

## Agent Harness

`eval` 命令只负责给已有 submission 阅卷；真正接入 Agent 时使用 `run-agent`：

```bash
python3 -B -m featureliftbench.cli run-agent \
  benchmark/tasks/iniconfig__parse_config__001 \
  --agent mini-swe-agent \
  --model <model-name> \
  --output experiments/mini-swe-agent/iniconfig
```

传入 `benchmark/tasks/` 根目录时会按数据集批量运行 **主榜 50 hard**，并写出 `suite.json`：

```bash
python3 -B -m featureliftbench.cli run-agent \
  benchmark/tasks \
  --agent mini-swe-agent \
  --model <model-name> \
  --num-workers 2 \
  --output experiments/mini-swe-agent/<run_id>
```

列出题目：`python3 harness/scripts/list_tasks.py`。按难度或 tag 切片：`python3 harness/scripts/list_tasks.py --difficulty hard --paths`。

`--num-workers` 只在传入 `benchmark/tasks/` 这类数据集根目录时生效；默认 `1` 保持串行。跑真实模型时建议先用 `2` 或 `3`，避免 API 限流和本机资源争用。

Agent Harness 会为每个任务创建一个 agent 可见 workspace：

```text
experiments/<run_id>/
  workspace/
    repo/
    public_tests/
    requirements.lock
    metadata.json        # redacted，不包含 hidden/evaluation/scoring_reference
    TASK.md
    submission/          # Agent 在这里写最终答案
  agent/
    prompt.txt
    stdout.log
    stderr.log
    trajectory.json      # mini-swe-agent --output
  submission/            # 从 workspace/submission 收集出的答案
  eval/
    result.json
    logs/
  run.json               # includes agent.usage when available
```

跑完整 suite 后，`suite.json` 会汇总每条任务的 agent 用量：

```text
experiments/mini-swe-agent/<suite_run_id>/
  suite.json             # summary + agent_usage_totals + per-task agent_usage
  <task_id>/
    run.json             # agent.usage + evaluation scores
    agent/
      trajectory.json    # mini 原始轨迹；逐步命令与 token 明细在这里
```

历史实验目录里还可能有 `agent_usage.json` / `agent_usage.md`，它们是早期从 `trajectory.json` 手工聚合的报告。

跨模型对比见：

```text
experiments/mini-swe-agent/suite-comparison.json
experiments/mini-swe-agent/suite-comparison.md
```

### Agent 轨迹与用量指标

`mini-swe-agent` 会把完整交互轨迹写到每条任务的 `agent/trajectory.json`。其中：

* **逐步交互**：`messages` 数组；`role == "assistant"` 的条数 ≈ 交互 step 数。
* **Token 统计**：`info.model_stats` 里的 `api_calls`、`prompt_tokens`、`completion_tokens`、`total_tokens`。
* **Agent 耗时**：`run.json` 里的 `agent.duration_seconds`（单条墙钟时间）。
* **评测分数**：`eval/result.json` 或 `run.json` 里的 `evaluation.scores`。

`run-agent` 会把可用的 token/step 写进单条 `run.json` 的 `agent.usage`，并在 suite 根目录的 `suite.json` 中写入 `agent_usage_totals`。标准接入方式是让 Agent 写 `agent/usage.json`；mini-swe-agent 会 fallback 解析 `agent/trajectory.json`。

`cost_usd` 不进入 harness 结果；当前只记录 token、API call 和 step 数。

用 `jq` 查看单条轨迹统计：

```bash
jq '.info.model_stats' experiments/mini-swe-agent/<suite_run_id>/<task_id>/agent/trajectory.json
```

推荐运行 CLI 时使用 **Python 3.11+**（例如 `python3.12`）。系统自带的 `python3` 若为 3.9/3.10，会因缺少 `tomllib` 无法启动。

`hidden_tests/`、`evaluation/` 和未公开评测规则不会进入 agent workspace。Agent 只能看到源仓库、public tests、锁定依赖和裁剪后的任务说明。

当前内置两个 adapter：

* `mini-swe-agent`：调用 `mini --task <TASK.md内容> --output agent/trajectory.json --exit-immediately`，支持 `--model`、`--config`、`--yolo`、`--agent-bin`；
* `command`：用于调试或接入其他 Agent，命令模板可使用 `{workspace}`、`{task_file}`、`{submission_dir}`、`{agent_output_dir}`。

### Agent API 配置

FeatureLiftBench 自己不直接调用模型 API。它只负责：

1. 读取一份共享配置；
2. 启动 Agent 子进程；
3. 把统一的 API/model 环境变量传给 Agent；
4. 收集 Agent 写出的 `submission/` 并评测。

推荐配置方式是：

```text
harness/config/agents.toml   # 非敏感配置：model、profile、cost limit
.env                 # 敏感配置：API key、可选 base URL
```

先复制模板：

```bash
cp harness/config/agents.example.toml harness/config/agents.toml
```

然后创建本地 `.env`：

```bash
FEATURELIFTBENCH_API_KEY=sk-...
FEATURELIFTBENCH_API_BASE=https://api.openai.com/v1
```

如果使用 OpenAI-compatible router，也只改这两个变量：

```bash
FEATURELIFTBENCH_API_KEY=<router-key>
FEATURELIFTBENCH_API_BASE=https://<router-host>/v1
```

`run-agent` 会把这一个 key 映射给常见 Agent/SDK 环境变量：

```text
FEATURELIFTBENCH_API_KEY
OPENAI_API_KEY
LITELLM_API_KEY
```

如果配置了 base URL，也会映射为：

```text
FEATURELIFTBENCH_API_BASE
OPENAI_BASE_URL
OPENAI_API_BASE
```

模型名会同时传入 CLI 的 `--model` 和环境变量：

```text
FEATURELIFTBENCH_MODEL
MSWEA_MODEL_NAME
```

这样后续接入其他 Agent 时，优先让它们读取 `FEATURELIFTBENCH_*`；如果它们已经兼容 OpenAI SDK/LiteLLM，通常也能直接使用 `OPENAI_API_KEY` 或 `LITELLM_API_KEY`。

如果 Agent 装在 conda 或其他虚拟环境里，可以把可执行文件路径放进 profile：

```toml
[profiles.default]
model = "openai/gpt-5.4-mini"
agent_bin = "/Users/<you>/anaconda3/envs/miniswe/bin/mini"
```

命令行里的 `--agent-bin` 仍然会覆盖 profile 配置，适合临时切换 Agent 安装位置。

运行示例：

```bash
python3 -B -m featureliftbench.cli run-agent \
  tasks \
  --agent mini-swe-agent \
  --agent-config harness/config/agents.toml \
  --agent-profile default \
  --env-file .env \
  --yolo \
  --num-workers 2 \
  --output experiments/mini-swe-agent/first-run
```

密钥不会写入 `run.json` 或 `suite.json`；结果里只记录 `api_key_present=true/false` 和使用的 profile/model/base URL。`.env` 和本地 `harness/config/agents.toml` 已在 `.gitignore` 中忽略。

例如本地自定义 Agent 可以这样接入：

```bash
python3 -B -m featureliftbench.cli run-agent \
  benchmark/tasks/iniconfig__parse_config__001 \
  --agent command \
  --agent-command "python my_agent.py {task_file} {submission_dir}" \
  --output experiments/custom/iniconfig
```

## Benchmark 目录结构

每个任务样例的标准结构见 [`docs/TASK_FORMAT.md`](docs/TASK_FORMAT.md)。摘要：

```text
benchmark/tasks/<task_id>/
  metadata.json
  requirements.lock
  repo/                 # 固定 commit 的源仓库快照
  public_tests/
  hidden_tests/
  evaluation/
    forbidden_imports.txt
    oracle_manifest.json
```

`repo/` 是任务输入的一部分，Agent 可以读取它。`hidden_tests/` 在正式评测时不可见。Agent 在 `submission/featurelifted/` 下写出解耦后的 package（包名固定为 `featurelifted`）。

当前 benchmark **主榜 50 hard** + **3 smoke**。完整列表与 **Flash-50 / Pro baseline** 见 [`docs/benchmark_tasks.md`](docs/benchmark_tasks.md) 与 [`docs/BENCHMARK_STATUS.md`](docs/BENCHMARK_STATUS.md)。

早期 10 题示例：

* `iniconfig__parse_config__001`：解耦出 INI 配置解析 API；
* `python_slugify__slugify_core__001`：解耦出 slugify 核心转换 API；
* `python_pathspec__gitignore_match__001`：解耦出 gitignore 风格路径匹配 API；
* `tomlkit__roundtrip_document__001`：解耦出 TOML 文档解析、编辑和 round-trip dump API；
* `packaging__requirement_marker_specifier__001`：解耦出 PEP 440/508 version/specifier/requirement/marker 语义；
* `pluggy__hook_call_order__001`：解耦出 hook spec、plugin 注册和调用顺序语义；
* `click__option_parser__001`：解耦出 CLI command/option/argument 解析核心；
* `markdown_it__commonmark_render__001`：解耦出 CommonMark 解析和 HTML rendering 核心；
* `pyyaml__safe_load_dump__001`：解耦出安全 YAML load/dump 核心；
* `jsonschema__validator_core__001`：解耦出 JSON Schema Draft 2020-12 核心验证行为；
* `sqlparse__parse_format_core__001`：解耦出 SQL parse、split、token tree 和 formatter 核心行为。

## Metadata Schema

完整字段说明、校验规则和示例见 [`docs/TASK_FORMAT.md`](docs/TASK_FORMAT.md)。JSON Schema：[`harness/featureliftbench/schemas/task_metadata.schema.json`](harness/featureliftbench/schemas/task_metadata.schema.json)。

一个任务的 `metadata.json` 核心字段包括：

```json
{
  "task_id": "python_slugify__slugify_core__001",
  "language": "python",
  "source": {
    "name": "python-slugify",
    "url": "https://github.com/un33k/python-slugify",
    "commit": "<fixed-commit-hash>",
    "license": "MIT"
  },
  "feature": {
    "name": "slugify core conversion",
    "description": "Convert unicode text into URL-safe slugs.",
    "source_entrypoints": ["slugify.slugify"],
    "included_behaviors": [
      "unicode transliteration",
      "separator handling",
      "case normalization",
      "allowed character filtering"
    ],
    "excluded_behaviors": [
      "command line interface",
      "packaging metadata from the original project"
    ]
  },
  "entanglement": {
    "level": "medium",
    "types": [
      "third_party_dependency_coupling",
      "implicit_dependency_coupling"
    ],
    "description": "Slug conversion behavior is coupled to transliteration dependency choices and option handling helpers.",
    "signals": [
      "allowed text-unidecode dependency",
      "multiple option combinations",
      "original package import is forbidden"
    ]
  },
  "output": {
    "package": "featurelifted",
    "import": "from featurelifted import slugify",
    "callable": "featurelifted.slugify",
    "signature": "slugify(text, **kwargs)"
  },
  "environment": {
    "python": "3.11",
    "network": false,
    "timeout_seconds": 60,
    "dependency_lock": "requirements.lock",
    "allowed_dependencies": ["text-unidecode"],
    "forbidden_dependencies": ["python-slugify"],
    "forbidden_imports": ["slugify"]
  },
  "tests": {
    "public": "public_tests/",
    "hidden": "hidden_tests/",
    "command": "pytest"
  }
}
```

这些字段的含义：

* `source.commit` 固定可复现实验输入；
* `feature.included_behaviors` 和 `feature.excluded_behaviors` 定义功能边界；
* `entanglement.level/types/description/signals` 标注目标功能与原仓库的缠绕强度、缠绕类型和可观察信号；
* `output` 定义 Agent 必须暴露的接口；
* `dependency_lock` 固定允许依赖的版本，评测时只能从本地 wheel/cache 安装；
* `allowed_dependencies` 是运行时依赖白名单，未列出的第三方依赖默认不允许；
* `forbidden_dependencies` 至少包括原始项目本身；
* `forbidden_imports` 至少包括原始项目暴露的 import 包名。

### 缠绕类型标签

`metadata.entanglement.types` 当前支持以下标签，用于后续按能力维度分析 Agent 表现：

| 标签 | 含义 |
| --- | --- |
| `framework_coupling` | 目标逻辑与 CLI/Web/test framework/插件系统/生命周期绑定 |
| `config_environment_coupling` | 行为依赖配置文件、环境变量、默认路径或运行时 settings |
| `global_state_registry_coupling` | 行为依赖 singleton、cache、registry、hook manager 或副作用初始化 |
| `resource_coupling` | 目标功能需要模板、schema、locale、grammar、数据文件等外部资源 |
| `implicit_dependency_coupling` | 必要依赖隐藏在跨模块 import 链中，和无关依赖混杂 |
| `parser_state_coupling` | 目标功能依赖 lexer/parser 状态机、token stream 或错误恢复机制 |
| `data_model_coupling` | 行为与内部 AST、Document、ValidationError、Context 等数据模型强绑定 |
| `third_party_dependency_coupling` | 目标功能依赖少量允许保留的第三方包，需和原包自身依赖区分 |
| `legacy_vibe_clutter` | 存在重复代码、历史兼容层、命名混乱、无用模块或脚本式结构 |

## 评测流程

每个 submission 按以下步骤评测：

1. 创建干净 Python 环境；
2. 确认原始仓库路径不在 `PYTHONPATH`、`sys.path` 或当前工作目录中；
3. 从锁定文件和本地 wheel/cache 安装任务允许的第三方依赖，依赖安装使用 `pip --no-index`；
4. 安装或导入 `submission/`；
5. 执行构建检查和 import 检查；
6. 运行 public tests 和 hidden tests；
7. 执行 forbidden import 检查；
8. 统计 submission Python LOC 和原始 repo Python LOC；
9. 输出功能是否通过和提取比例。

当前 evaluator 还没有容器级运行时断网；已知实现限制见 [docs/limitations.md](docs/limitations.md)。

如果 Build Pass、Test Pass 或 Original Import Check 失败，该任务视为未通过。功能通过后，主要看提取后的代码占原始仓库代码的比例。

## 测试设计

每个任务至少包含三类测试：

* **API contract tests**：验证输出 API、函数签名、异常类型和返回类型；
* **behavior tests**：覆盖常规输入、边界情况、错误输入和兼容性行为；
* **migrated source tests**：从原仓库测试中筛选并迁移出的目标功能相关测试。

hidden tests 应覆盖 public tests 未暴露的边界，不应只重复 public tests 的同类样例。对于 parser、converter、formatter 等功能，优先加入 property-style tests 或参数化边界测试，降低硬编码通过的可能性。

## 评分方式

FeatureLiftBench 当前只保留两个核心信号：

```text
FunctionalGate = BuildPass × TestPass × OriginalImportPass
ExtractionRatio = SubmissionPythonLOC / SourceRepoPythonLOC
```

其中：

* `BuildPass`：package 能否在干净环境中安装或导入；
* `TestPass`：public 和 hidden tests 是否全部通过；
* `OriginalImportPass`：是否没有导入原始仓库路径、原始仓库包名或禁止依赖。
* `ExtractionRatio`：解耦后 Python LOC 占原始 repo Python LOC 的比例，越低越好。

`final_score` 只是兼容 CLI 汇总用的派生值：功能不过为 0，功能通过时为 `clamp(1 - ExtractionRatio, 0, 1)`。讨论和排序时优先直接看 `FunctionalGate` 和 `ExtractionRatio`。

## 反投机规则

以下行为应直接判为失败或施加高额惩罚：

* 导入原始仓库目录、原始包名或原始项目的 PyPI 包；
* 在运行时下载代码、安装依赖或访问网络；
* 将大量源码压缩成字符串、base64、zip、pickle 或二进制 blob 后动态加载；
* 使用 `eval`、`exec`、动态 import 生成主要功能逻辑；
* 复制完整仓库、完整测试目录、完整文档目录或完整 CI 配置；
* 引入与目标功能无关的大型框架依赖；
* 通过硬编码 public tests 样例返回结果。

这些规则不是为了限制合理实现，而是为了确保分数反映“理解功能边界并解耦必要代码”的能力。

## Baseline

计划比较以下方法：

| 方法 | 说明 | 作用 |
| --- | --- | --- |
| Copy-All | 直接复制整个源仓库并做最小包装 | 投机性下界 |
| Manual Oracle Closure | 人工标注接近最小的必要文件和依赖 | 最小化参考上界 |
| LLM-only | 只给任务说明和 public tests，让模型生成输出 | 基础模型能力 |
| Bash Agent | Agent 可使用 shell 查看仓库、运行测试和编辑文件 | 实际代码代理能力 |
| RepoMap Agent | 给 Agent 提供仓库级静态摘要 | 测试摘要是否有帮助 |
| Graph-guided Agent | 使用 import graph、call graph 和测试覆盖信息辅助解耦 | 测试结构化上下文价值 |

Copy-All 不应被当作合理解决方案，只用于证明最小化指标能惩罚直接复制。

## 仓库选择原则

### 语言选择

第一版只选 **Python**。

原因：

* 当前 evaluator、task schema、public/hidden tests 和 Agent Harness 都已经围绕 Python package、`pytest`、`venv` 跑通；
* Python 生态里有大量适合功能级解耦的小到中型库，能快速覆盖 parser、formatter、converter、配置加载器、utility 模块和框架适配层；
* 第一版如果混入多语言，会把“Agent 是否会解耦功能”和“评测器是否支持多语言工具链”混在一起，实验结论会变脏；
* 语言字段仍保留在 `metadata.json` 中，后续可以扩展 JavaScript/TypeScript、Go 或 Rust，但不和 Python v0 混合报告。

因此 v0 的口径是：

```text
FeatureLiftBench v0 = Python-only feature-level decoupling benchmark
```

后续多语言版本应该单独分轨，例如 `FeatureLiftBench-Python`、`FeatureLiftBench-JS`，不要直接混成一个总分。

### 难度分层

正式任务按三档难度设计。难度不是按源仓库大小粗暴划分，而是按**目标功能的最小可行解耦闭包**划分。实际标注应在 Manual Oracle Closure 做完后确认。

| 难度 | 标准 | 典型任务 |
| --- | --- | --- |
| Easy | Oracle closure 通常不超过 1-3 个运行时文件，约 500 LOC 以内；无第三方运行时依赖；目标 API 单一；功能主要是纯函数、轻量 parser 或简单 class；hidden tests 覆盖边界但不要求复杂状态推理。 | 单文件 parser、配置读取、简单 formatter、轻量 converter |
| Medium | Oracle closure 通常为 4-10 个运行时文件，约 500-2500 LOC；允许 0-1 个小型白名单依赖；功能跨多个 helper/module；需要处理路径、unicode、转义、排序、错误类型、文件遍历或多参数组合；Copy-All 和 Oracle 体积差距明显。 | 多模块 parser、URL/text converter、gitignore/path matching、表格 formatter |
| Hard | Oracle closure 通常超过 10 个运行时文件或 2500 LOC；存在 lexer/parser 状态机、插件/注册机制、round-trip 保真、复杂配置继承、数据文件或多依赖交互；public tests 不能充分暴露关键边界，hidden tests 需要覆盖组合行为和错误恢复。 | TOML/Markdown/模板子集、CLI 参数解析核心、格式保持 parser |

难度分层的目标是让结果可解释：

* Easy 看 Agent 是否能完成基本功能解耦；
* Medium 看 Agent 是否能识别跨模块依赖和边界；
* Hard 看 Agent 是否能在复杂内部结构中裁剪出稳定、可维护的最小闭包。

当前 pilot task 的难度：

| Task | 暂定难度 | 原因 |
| --- | --- | --- |
| `iniconfig__parse_config__001` | Easy | 目标集中、无第三方依赖、API 和行为边界清楚 |
| `python_slugify__slugify_core__001` | Medium | unicode/transliteration/options 行为较多，允许一个小型依赖 |
| `python_pathspec__gitignore_match__001` | Medium | 跨多个模块，涉及 gitignore 语义、路径规范化、tree walking 和错误模式 |
| `tomlkit__roundtrip_document__001` | Hard | parser/formatter 状态复杂，要求保留注释、空行、表顺序、字符串格式和错误位置信息 |
| `packaging__requirement_marker_specifier__001` | Hard | PEP 440/508 解析、比较、marker evaluation 和错误语义组合复杂 |
| `pluggy__hook_call_order__001` | Hard | plugin manager 状态、hook wrapper、firstresult 和调用顺序语义复杂 |
| `click__option_parser__001` | Hard | command/group/context、类型转换、错误输出和 CliRunner 行为组合复杂 |
| `markdown_it__commonmark_render__001` | Hard | block/inline parser、token tree、HTML escaping 和 rule control 组合复杂 |
| `pyyaml__safe_load_dump__001` | Hard | 安全 loader/dumper、anchors/aliases/merge keys、多文档和错误语义复杂 |
| `jsonschema__validator_core__001` | Hard | validator 组合规则、错误 path/schema_path、format checker 和 schema errors 复杂 |
| `sqlparse__parse_format_core__001` | Hard-plus | SQL lexer、statement splitter、grouping passes、token tree 和 formatter filters 组合复杂 |

当前已有 8 条 Hard/Hard-plus task。下一步重点不再是单纯补数量，而是分析真实 Agent 在 10 条历史 suite 和新增 hard-plus 任务上的功能通过率、token/step 成本和 extraction ratio 分布。

### 仓库选择原则

Python v0 候选任务应满足：

* 源仓库 license 允许再分发和评测使用；
* 固定 commit 下测试稳定；
* 目标功能边界可以被人工解释和标注；
* 不依赖数据库、浏览器、GPU、云服务或大型本地服务；
* 可以在无网络环境下评测；
* 适合解耦 parser、formatter、converter、配置加载器、模板处理器、CLI 子命令、框架适配层或 utility 模块。

Pilot 可以从小仓库开始，但正式版需要加入中型仓库、legacy 风格项目和 vibe-coded 项目中的局部功能，否则 Copy-All 与真正解耦的差距太小，任务区分度不足。

当前已采用：

* `iniconfig`
* `python-slugify`
* `python-pathspec`
* `tomlkit`
* `packaging`
* `pluggy`
* `click`
* `markdown-it-py`
* `PyYAML`
* `jsonschema`

下一轮任务不应只追求数量，而应补充更贴近项目目标的 entangled / hard-plus 样例，例如从 `jinja2`、`pygments`、`sqlparse`、`pytest`、`coverage.py` 或小型 vibe-coded app 中解耦局部功能。

候选 hard-plus 任务先按“缠绕类型覆盖”设计，而不是只按仓库名扩展：

| 候选任务 | 目标功能 | 主要缠绕类型 |
| --- | --- | --- |
| `jinja2__template_render_core__001` | 解耦模板解析、变量替换、filter 和错误语义的最小渲染核心 | `framework_coupling`, `resource_coupling`, `parser_state_coupling`, `data_model_coupling` |
| `pytest__mark_config_core__001` | 解耦 mark/skip/xfail 解析和配置合并核心 | `framework_coupling`, `config_environment_coupling`, `global_state_registry_coupling` |
| `coverage__source_filter_core__001` | 解耦 source/include/omit 路径过滤和配置继承逻辑 | `config_environment_coupling`, `resource_coupling`, `implicit_dependency_coupling` |
| [`sqlparse__parse_format_core__001`](docs/task_designs/sqlparse__parse_format_core__001.md) | 解耦 SQL tokenization、statement split 和 formatter 子集 | `parser_state_coupling`, `data_model_coupling`, `implicit_dependency_coupling` |
| `vibe_app__rules_engine__001` | 从小型脚本式 app 中解耦业务规则/数据转换核心 | `legacy_vibe_clutter`, `config_environment_coupling`, `global_state_registry_coupling` |

## 项目路线

### 阶段一：Pilot

* 已完成 10 条 Python clean OSS pilot task 的最小闭环；
* 已覆盖 Easy、Medium、Hard 三档，其中 Hard/Hard-plus 已扩到 8 条；
* 每个仓库优先设计 1 个功能级解耦任务；
* 固定源仓库 commit 和 license 信息；
* 编写 metadata、public tests、hidden tests 和 forbidden import 规则；
* 实现干净环境评测脚本；
* 跑通 Copy-All、Manual Oracle Closure 和真实 Agent baseline；
* 验证最小化指标能区分 Copy-All 与真正解耦。

### 阶段二：Benchmark v0

* ~~扩展到 30-50 个任务~~（**已完成**：50 hard + 3 smoke）；
* 加入 entangled / hard-plus 任务，覆盖框架耦合、配置耦合、全局状态、资源文件和 legacy/vibe-coded clutter；
* 继续校准 metadata schema；
* 校准任务难度标签；
* 校准缠绕类型标签；
* 加入结构化评测报告；
* 跑 Bash Agent、RepoMap Agent 和基础 graph-guided baseline；
* 总结失败模式。

### 阶段三：完整 Benchmark

* 扩展到 80-120 个任务；
* 覆盖更多中型仓库、vibe-coded 项目、legacy 风格项目和多种功能类型；
* 做工具上下文、依赖图、调用图、测试覆盖信息的消融实验；
* 发布 benchmark、评测代码、baseline 结果和任务构建指南。

## 研究问题

FeatureLiftBench 主要关注以下问题：

1. 当前代码 Agent 能否从真实、混乱或缠绕的仓库中正确解耦已有功能？
2. Agent 是否真正理解功能边界，还是倾向于复制大量无关框架、配置、状态和资源代码？
3. 仓库依赖图、调用图、测试覆盖信息和代码索引能否提升功能级解耦质量？
4. Agent 在解耦任务中的主要失败模式是什么：行为缺失、依赖漏带、环境耦合、资源遗漏，还是 copy-heavy？
5. 最小化指标如何设计，才能惩罚 Copy-All，又不鼓励不可维护的压缩实现？
6. 除了 bug 修复和功能实现，仓库级代码 Agent 还应该如何评估“理解、解耦、重组和复用”能力？

## 当前状态

FeatureLiftBench **统一 benchmark** 已落地：主榜 **50 hard** + smoke **3**，共用同一 schema、evaluator 与评分。完整清单见 [`docs/benchmark_tasks.md`](docs/benchmark_tasks.md)；目录说明见 [`docs/DIRECTORY.md`](docs/DIRECTORY.md)。

演进方式：在 `benchmark/tasks/` 下**新增或删除**题目，不另建第二套 collection。

已完成 pilot 与 hard 任务的 `mini-swe-agent` suite 校准。示例：`sqlparse__parse_format_core__001` baseline（deepseek-v4-pro）：通过，`extraction_ratio≈0.487`，45 steps，856k tokens。

最近一次 hard 子集 suite（18 题，`extreme` tag）：`experiments/mini-swe-agent/extreme-18-suite-001/`（14/18 通过）。分析：`python3 harness/scripts/analyze_benchmark_suite.py experiments/mini-swe-agent/extreme-18-suite-001`。

## 待讨论问题

以下设计需要在 pilot 中进一步验证：

* Decoupling / Extraction Track 是否需要通过代码相似度约束“必须来自原实现”；
* allowed dependencies 应该采用严格白名单，还是允许标准小型依赖；
* Manual Oracle Closure 是每个任务必需，还是只在一部分任务中人工标注；
* RelevanceScore 应该完全自动化，还是允许少量人工 manifest；
* hidden tests 是否应该包含 property-style tests，以及如何保证稳定性；
* entangled / hard-plus 任务应该优先来自真实 legacy/vibe-coded 项目，还是从成熟 OSS 中人为选择高度耦合的局部功能？

已知实现缺口、评测局限与当前实验口径问题见 [docs/limitations.md](docs/limitations.md)。

## 引用

Coming soon.

## License

Coming soon.
