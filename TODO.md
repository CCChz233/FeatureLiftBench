# FeatureLiftBench TODO

工程 backlog（非文档导航）。文档入口 → [docs/README.md](docs/README.md)

| 主题 | 文档 |
| --- | --- |
| 扩题 50→100 | [BATCH1_PLAYBOOK.md](BATCH1_PLAYBOOK.md)（七步执行）· [docs/EXPANSION.md](docs/EXPANSION.md) · [docs/candidate_backlog.md](docs/candidate_backlog.md) |
| 官方 baseline | [docs/BENCHMARK_STATUS.md](docs/BENCHMARK_STATUS.md) |
| vLLM / API 实验 | [docs/EXPERIMENT_RESULTS.md](docs/EXPERIMENT_RESULTS.md) · [RUN.md](RUN.md) |
| 已知局限 | [docs/limitations.md](docs/limitations.md) |

**当前状态（2026-06-28）：** batch-0 **50 hard** 冻结（grandfather） · batch-1 **50/50 入榜** · 主榜 **100/100 hard** · Oracle **100/100** · batch-1 质量验收 **进行中**（G0–G4 evidence 50/50，Flash 运行中）

## 现在照这个做

**当前唯一主线：** batch-1 **质量验收** — evidence + Flash + gate promote（见 [docs/BENCHMARK_ACCEPTANCE_2026-06-28.md](docs/BENCHMARK_ACCEPTANCE_2026-06-28.md)）

**当前正在做的题：** Flash 校准（`experiments/run-batch1-flash-missing.sh`）

**本轮目标：** batch-1 **50/50 promote** — **已完成**

**当前最近一步：** 质量验收通过；`check_batch1_acceptance.py` **50/50**。

### 为什么先做这一题

`httpx__request_model_core__001` 的目标不是轻量 URL parser，而是从 HTTPX 中解耦一个离线 HTTP request builder：

```text
Request / URL / Headers / QueryParams / Cookies
+ client/request merge semantics
- network / transport / response / async runtime
```

这题只有在同时满足以下三点时才继续推进：

| Gate | 必须满足 |
| --- | --- |
| Useful | 提取物是真实可复用的离线 request model / request builder |
| Hard | 不是单文件 helper；跨 URL、headers、cookies、body、merge 语义等多个模块 |
| Testable | public/hidden 都是 deterministic offline pytest；oracle/copy-all/naive baseline 能分层 |

### 当前进度

| 项 | 目标 | 当前 |
| --- | ---: | ---: |
| batch-0（冻结） | 50 | 50 |
| backlog idea | 80 | 30 |
| hard-first shortlist | 5 | 5 |
| design spike | 1 | 1（`httpx` 已写） |
| staging pilot | 1 | 1（已 promote） |
| staging 进行中 | 20 | 0 |
| batch-1 已入榜 | 50 | 50 |
| 主榜合计 | 100 | 100 |

### 本周执行清单

按顺序做，前一步不过不要往后走。

1. **确认 spike 边界**
   - 文件：[docs/task_designs/httpx__request_model_core__001.md](docs/task_designs/httpx__request_model_core__001.md)
   - 产物：确认 output API、included/excluded behaviors、hidden 测试点。
   - 通过标准：仍然是 useful + hard + testable；如果降成 URL-only，直接 redesign。

2. **创建 staging 目录**
   - 目标目录：`benchmark/staging/httpx__request_model_core__001/`
   - 必备文件：
     ```text
     metadata.json
     requirements.lock
     repo/
     public_tests/
     hidden_tests/
     evaluation/forbidden_imports.txt
     evaluation/oracle_manifest.json
     ```
   - 产物：HTTPX pinned source snapshot + 初版 metadata/tests/evaluation。

3. **做 throwaway oracle closure**
   - 位置：`benchmark/submissions/httpx__request_model_core__001/oracle/`
   - 目标：先能证明题可解，不要求第一次就优雅。
   - 通过标准：
     - oracle functional pass；
     - oracle closure 不是单文件薄 wrapper；
     - 不包含 network-capable API surface。

4. **做 naive baseline**
   - 目标：写一个浅实现，例如 `URL=str`、`Headers=dict`、`QueryParams=dict`。
   - 通过标准：public 可以过一部分或大部分，但 hidden 必须因为真实语义缺失而失败。
   - 失败原因应指向 duplicate query、raw headers、cookie merge、body/header interaction 等具体行为。

5. **跑本地验证**
   ```bash
   export PYTHONPATH=harness
   python -B -m featureliftbench.cli validate-task benchmark/staging/httpx__request_model_core__001/
   python3 harness/scripts/audit_output_imports.py benchmark/staging/httpx__request_model_core__001/ --fail-on-gap
   python3 harness/scripts/build_oracle_submission.py benchmark/staging/httpx__request_model_core__001/
   python -B -m featureliftbench.cli eval benchmark/staging/httpx__request_model_core__001/ \
     benchmark/submissions/httpx__request_model_core__001/oracle \
     --output experiments/validate-httpx__request_model_core__001
   python3 harness/scripts/verify_module_probes.py benchmark/staging/httpx__request_model_core__001/ \
     --verify-oracle
   ```

6. **跑 Flash 单题校准**
   ```bash
   export PYTHONPATH=harness
   python -B -m featureliftbench.cli run-agent benchmark/staging/httpx__request_model_core__001/ \
     --agent mini-swe-agent \
     --agent-config harness/config/agents.toml \
     --agent-profile deepseek_v4_flash \
     --env-file .env \
     --yolo \
     --output experiments/mini-swe-agent/httpx__request_model_core__001-flash-001
   ```
   - 通过标准：public 指引够清楚，hidden 有判别力；copy-heavy pass 只能拿低 final_score。

7. **决定 promoted / redesign / dropped**
   - Promote 条件：oracle 过、copy-all 过但 high extraction、naive hidden fail、module probes ≥3、Flash 结果有判别力。
   - Redesign 条件：题有价值但边界太宽/太窄、hidden 不够准、oracle closure 不理想。
   - Drop 条件：不好稳定评估、必须复制大半 HTTPX、或实际难度只是轻量 utility。

### 当前不要做

- 不要修改 batch-0 50 题。
- 不要为了数量开 10 个 staging。
- 不要先补多模型 full run；模型实验等第一题模板跑通后再继续。
- 不要让没有 oracle 的题进入 `benchmark/tasks/`。
- 不要把网络 I/O、transport、response streaming 或 async runtime 纳入 `httpx` 这题。

### 后续队列

`httpx` pilot 跑通后，按这个顺序推进下一批 hard-first spike：

1. `pydantic_v1__validation_error_core__001`
2. `python_dateutil__rrule_core__001`
3. `jsonpath_ng__expression_eval_core__001`
4. `configobj__roundtrip_config_core__001`

完整扩题规则见 [docs/EXPANSION.md](docs/EXPANSION.md)，**七步执行标准**见 [BATCH1_PLAYBOOK.md](BATCH1_PLAYBOOK.md)，候选池见 [docs/candidate_backlog.md](docs/candidate_backlog.md)。

---

## 项目目标

FeatureLiftBench 要评估的不是“模型会不会从零写代码”，而是：

```text
Agent 能否在保持目标功能行为正确的前提下，
把该功能从框架、配置、状态、资源、环境和无关模块中解耦出来，
形成独立、可安装、可测试、相对精简、可复用的 Python package。
```

现实意义：评估 Agent 能否把 vibe coding 和 legacy code 中常见的“能跑但混乱”的仓库整理成更模块化、可维护、可复用的软件资产。

前 10 条任务属于早期 **clean OSS pilot**；主榜现已 **50 hard**，entanglement 七类已标满。题源与缠绕分布见 [benchmark_tasks.md](docs/benchmark_tasks.md)。

## 核心关系

FeatureLiftBench 先按四类东西理解：

```text
benchmark/tasks/          # 题目
benchmark/submissions/    # Agent 或 baseline 的答案
harness/featureliftbench/ # 阅卷器代码
experiments/              # 成绩单
```

也就是：

```text
任务 + 答案 -> 阅卷器 -> 结果
```

## 语言和难度口径

当前 v0 先固定为 **Python-only feature-level decoupling benchmark**。不在第一版混入 JavaScript/TypeScript、Go 或 Rust，避免把多语言工具链问题和 Agent 解耦能力混在一起。

三档难度先按这个标准讨论：

| 难度 | 标准 | 当前/候选 |
| --- | --- | --- |
| Easy | Oracle closure 通常不超过 1-3 个运行时文件，约 500 LOC 以内；无第三方运行时依赖；目标 API 单一；hidden tests 主要覆盖基础边界。 | `iniconfig`，候选 `python-dotenv` |
| Medium | Oracle closure 通常为 4-10 个运行时文件，约 500-2500 LOC；允许 0-1 个小型白名单依赖；功能跨多个 helper/module；涉及 unicode、路径、转义、排序、错误类型、文件遍历或多参数组合。 | `python-slugify`、`python-pathspec`，候选 `tabulate`、`xmltodict`、`python-frontmatter` |
| Hard | Oracle closure 通常超过 10 个运行时文件或 2500 LOC；存在 lexer/parser 状态机、插件/注册机制、round-trip 保真、复杂配置继承、数据文件或多依赖交互；hidden tests 覆盖组合行为和错误恢复。 | `tomlkit`、`packaging`、`pluggy`、`click`、`markdown-it-py`、`PyYAML`、`jsonschema` |

当前 benchmark：**主榜 50 hard**（`benchmark/tasks/`）+ **3 smoke**（`benchmark/sanity/`）。完整列表见 [`docs/benchmark_tasks.md`](docs/benchmark_tasks.md)。

历史 28 题 Flash baseline：**19/28 passed**（`benchmark-28-deepseek-flash-003`）。**当前主 baseline：Flash-50** `benchmark-50-hard-flash-001` → **41/50 (82%)** functional；Pro-50 re-eval **42/50 (84%)**。本地 vLLM 与 SiliconFlow 实验见 [docs/EXPERIMENT_RESULTS.md](docs/EXPERIMENT_RESULTS.md)。

## 已完成 sprint：50 hard 扩榜（2026-06-25）

| 优先级 | 事项 | 状态 |
| --- | --- | --- |
| P0 | Smoke 3 题迁至 `benchmark/sanity/`；默认 hard-only | **完成** |
| P0 | 加严 8–10 道 Flash 过易 hard（hidden/L3） | **完成** |
| P0 | 新增 25 hard（5 批） | **完成** |
| P0 | `verify_all_oracles.py` 50/50 | **完成** |
| P0 | Design notes 50/50 + module probes ≥3 | **完成** |
| P1 | 文档：benchmark_tasks / BENCHMARK_STATUS / README / limitations | **完成** |
| P1 | Pro-50 baseline（`deepseek_v4_pro`）re-eval 冻结 | **完成**（42/50） |
| P2 | 难度校准：functional 压向 20–30% | **暂缓**（用 extraction / final_score 区分） |

## 已完成 sprint：28 题夯实（2026-06-24）

| 优先级 | 事项 | 状态 |
| --- | --- | --- |
| P0 | 补 8 题 `metadata.output.import` + `audit_output_imports.py` | **完成** |
| P0 | 28 题 oracle `eval` 可回归 | **完成** |
| P0 | L1 import + design note 28/28 + module probes ≥3 | **完成** |
| P1 | `TASK.md` 工作流 / forbidden import / hidden 提示 | **完成** |
| P2 | L3 included_behaviors 微调（Flash 失败 7 题） | **完成** |

## Benchmark 维护（新增 / 删除）

| 操作 | 步骤 |
| --- | --- |
| 新增 | 见 [`docs/TASK_FORMAT.md`](docs/TASK_FORMAT.md) + design note + Oracle |
| 删除 | 移除 `benchmark/tasks/<task_id>/` 与对应 design note |
| 清单 | `python3 harness/scripts/list_tasks.py` |
| 分析 | `python3 harness/scripts/analyze_benchmark_suite.py experiments/.../<run_id>` |

单题 design note 模板：[`docs/task_designs/TEMPLATE.md`](docs/task_designs/TEMPLATE.md)。机器可读格式：[`docs/TASK_FORMAT.md`](docs/TASK_FORMAT.md)。

目标（hard 子集校准）：强 Agent suite 功能通过率 **35–45%**；通过者 `extraction_ratio` 标准差 **> 0.15**。

## Entangled / 多题同库（已并入统一 benchmark）

- [x] `entanglement` 字段与全量 metadata。
- [x] `entanglement.primary`（7 类互斥主标签）+ `report_entanglement_coverage.py` + **50 hard** 标注。
- [x] sqlparse / coverage / jinja2 / pytest / vibe_app 多题同库设计。
- [x] Agent 校准记录：[`experiments/mini-swe-agent/extreme-18-analysis.md`](experiments/mini-swe-agent/extreme-18-analysis.md)（历史 run 名称保留）。

## 目录结构

架构与目录见 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)；题目格式见 [`docs/TASK_FORMAT.md`](docs/TASK_FORMAT.md)。

```text
docs/           # 文档
benchmark/      # 数据集（tasks、sources、本地 Oracle）
harness/        # 工具链（evaluator + agent + scripts + tests）
experiments/    # 本地实验产物（gitignore）
```

核心关系：

```text
benchmark/tasks/ + benchmark/submissions/  →  harness/featureliftbench  →  experiments/
```

## CLI MVP

先只做三个命令：

```bash
featureliftbench validate-task benchmark/tasks/<task_id>/
featureliftbench eval benchmark/tasks/<task_id>/ benchmark/submissions/<submission_id>/ --output experiments/<run_id>/
featureliftbench score experiments/<run_id>/result.json
featureliftbench run-agent benchmark/tasks/<task_id>/ --agent mini-swe-agent --model <model> --output experiments/<run_id>/
```

`eval` 仍然支持手工准备 submission；真实 Agent 则通过 `run-agent` 生成 submission 后自动评测。

## Result 格式

`result.json` 当前包含这些核心字段：

```json
{
  "task_id": "iniconfig__parse_config__001",
  "submission": "copy_all",
  "status": "failed",
  "build_pass": false,
  "test_pass": false,
  "original_import_pass": false,
  "environment": {
    "venv_dir": "/tmp/featureliftbench-eval-.../.venv",
    "python": "/tmp/featureliftbench-eval-.../.venv/bin/python",
    "install_mode": "path"
  },
  "dependency_install": {
    "returncode": 0,
    "passed": true,
    "duration_seconds": 0.0,
    "timed_out": false,
    "skipped": true,
    "reason": "dependency lock is empty"
  },
  "submission_install": {
    "returncode": 0,
    "passed": true,
    "duration_seconds": 0.0,
    "timed_out": false,
    "skipped": true,
    "reason": "submission has no pyproject.toml; using PYTHONPATH"
  },
  "public_tests": {
    "returncode": 0,
    "passed": true,
    "duration_seconds": 0.0,
    "timed_out": false,
    "skipped": false,
    "reason": ""
  },
  "hidden_tests": {
    "returncode": 0,
    "passed": true,
    "duration_seconds": 0.0,
    "timed_out": false,
    "skipped": false,
    "reason": ""
  },
  "metrics": {
    "file_count": 0,
    "loc": 0,
    "source_loc": 0,
    "package_bytes": 0,
    "dependency_count": 0,
    "suspicious_file_count": 0
  },
  "scores": {
    "functional_gate": 0.0,
    "extraction_ratio": 0.0,
    "final_score": 0.0
  },
  "logs": {
    "dir": "outputs/<run_id>/logs"
  },
  "errors": []
}
```

## 实现顺序

### Phase 0: 建骨架

- [x] 创建 `pyproject.toml`。
- [x] 创建 `featureliftbench/`。
- [x] 创建 `tasks/`、`submissions/`、`outputs/`。
- [x] 创建 `tests/`。
- [x] 让 `featureliftbench --help` 能跑。

### Phase 1: 任务格式和校验

- [x] 写 `featureliftbench/schemas/task_metadata.schema.json`。
- [x] 写 `metadata.py` 读取 metadata。
- [x] 写 `validate.py` 检查任务目录。
- [x] 检查 `task_id` 和目录名一致。
- [x] 检查 `repo/`、`public_tests/`、`hidden_tests/`、`requirements.lock` 是否存在。
- [x] 检查 allowed dependencies 和 forbidden dependencies 不冲突。
- [x] 写基本单元测试。

### Phase 2: 第一个任务

先做：

```text
tasks/iniconfig__parse_config__001/
```

需要准备：

- [x] 固定 `iniconfig` 源仓库 commit。
- [x] 保存 `repo/` 快照。
- [x] 写 `metadata.json`。
- [x] 写 `requirements.lock`。
- [x] 写 public tests。
- [x] 写 hidden tests。
- [x] 写 `evaluation/forbidden_imports.txt`。
- [x] 写 `evaluation/oracle_manifest.json`。

### Phase 3: Evaluator MVP

- [x] 创建临时运行目录。
- [x] 确保原始 `repo/` 不在运行路径里。
- [x] 安装或导入 submission。
- [x] 运行 public tests。
- [x] 运行 hidden tests。
- [x] 检查 forbidden imports。
- [x] 输出 `result.json`。

这一阶段只需要判断能不能过测试，不急着把评分做复杂。

### Phase 4: 基础指标和评分

- [x] 统计文件数。
- [x] 统计 Python LOC。
- [x] 统计 package bytes。
- [x] 统计依赖数量。
- [x] 实现 `FunctionalGate`。
- [x] 简化评分为 `FunctionalGate` + `ExtractionRatio`。
- [x] 跑 Copy-All/Oracle 类 submission，确认功能通过和提取比例可区分。

### Phase 4.5: Evaluator Hardening

- [x] 使用临时 venv 运行评测。
- [x] 使用 `venv --system-site-packages` 复用当前环境里的 pytest。
- [x] public/hidden tests 使用 venv Python 执行。
- [x] 支持有 `pyproject.toml` 的 submission editable install。
- [x] 支持无 `pyproject.toml` 的 submission 通过 `PYTHONPATH` fallback。
- [x] 支持 pyproject 安装失败但根目录存在输出包时 `PYTHONPATH` fallback。
- [x] 空 `requirements.lock` 跳过依赖安装。
- [x] 非空 `requirements.lock` 校验 allowed/forbidden dependencies。
- [x] 检查 submission 声明的 forbidden dependencies。
- [x] 在 `result.json` 中输出 environment、dependency_install、submission_install。
- [x] 更新 `result.schema.json`。
- [x] 用 Oracle、Copy-All、forbidden dependency submission 做端到端验证。

### Phase 5: 第二个任务

再做：

```text
tasks/python_slugify__slugify_core__001/
```

这个任务用来验证：

* 第三方依赖白名单；
* unicode 行为测试；
* forbidden dependency 检查；
* Copy-All 与 Oracle 的体积分差。

完成状态：

- [x] 固定 `python-slugify` 源仓库 commit。
- [x] 保存 `repo/` 快照。
- [x] 写 `metadata.json`。
- [x] 写包含 `text-unidecode==1.3` 的 `requirements.lock`。
- [x] 写 public tests。
- [x] 写 hidden tests。
- [x] 写 `evaluation/forbidden_imports.txt`。
- [x] 写 `evaluation/oracle_manifest.json`。
- [x] 验证 allowed dependency lock 安装路径。
- [x] 验证 Oracle submission 可通过且 `final_score=1.0`。
- [x] 验证 Copy-All submission 可通过但 `final_score=0.2`。
- [x] 验证声明 `python-slugify` dependency 会被 forbidden dependency 检查拦截。

### Phase 5.5: 第三个任务

新增：

```text
tasks/python_pathspec__gitignore_match__001/
```

这个任务用来验证：

* gitignore 风格 pattern 编译和路径匹配；
* 目录模式、根路径模式、`**`、否定模式和错误模式；
* 无第三方依赖的中等规模纯 Python 解耦；
* Copy-All 与 simple-backend Oracle 的体积分差。

完成状态：

- [x] 固定 `python-pathspec` 源仓库 commit。
- [x] 保存 `repo/` 快照。
- [x] 写 `metadata.json`。
- [x] 写空 `requirements.lock`。
- [x] 写 public tests。
- [x] 写 hidden tests。
- [x] 写 `evaluation/forbidden_imports.txt`。
- [x] 写 `evaluation/oracle_manifest.json`。
- [x] 验证 Oracle submission 可通过且 `final_score=1.0`。
- [x] 验证 Copy-All submission 可通过但 `final_score=0.2`。

### Phase 5.75: 第四个任务和难度 metadata

新增：

```text
tasks/tomlkit__roundtrip_document__001/
```

这个任务用来验证：

* Hard 难度的 parser/formatter round-trip 解耦；
* TOML 文档解析、编辑和格式保留 dump；
* 注释、空行、表顺序、inline table、array of tables、multiline/literal strings；
* 错误类型、错误行列信息和 unicode escape 边界；
* Copy-All 与 package-only Oracle 的体积分差。

完成状态：

- [x] 固定 `tomlkit` 源仓库 commit。
- [x] 保存 `repo/` 快照。
- [x] 写 `metadata.json`，标记 `difficulty=hard`。
- [x] 写空 `requirements.lock`。
- [x] 写 public tests。
- [x] 写 hidden tests。
- [x] 写 `evaluation/forbidden_imports.txt`。
- [x] 写 `evaluation/oracle_manifest.json`。
- [x] 验证 Oracle submission 可通过且 `final_score=1.0`。
- [x] 验证 Copy-All submission 可通过但 `final_score=0.2`。
- [x] 为四条现有 task 补 `difficulty` 和 `tags`。
- [x] 更新 metadata schema 和 validator，支持可选 `difficulty/tags`。

### Phase 6: Agent Harness

这一阶段目标是让真实 Agent 能在不看到 hidden/evaluation 的情况下完成任务，然后把生成的 `submission/` 交给 evaluator。

- [x] 新增 redacted agent workspace：
  - [x] 复制 `repo/`。
  - [x] 复制 `public_tests/`。
  - [x] 复制 `requirements.lock`。
  - [x] 写裁剪后的 `metadata.json`。
  - [x] 写 `TASK.md`。
  - [x] 不暴露 `hidden_tests/`、`evaluation/`、`scoring_reference`。
- [x] 新增通用 Agent adapter 接口。
- [x] 新增 `mini-swe-agent` adapter。
- [x] 新增通用 `command` adapter，方便后续接其他 Agent。
- [x] 新增 `run-agent` CLI。
- [x] 支持传单个任务目录运行。
- [x] 支持传 `tasks/` 数据集根目录批量运行并输出 `suite.json`。
- [x] 支持 `run-agent tasks --num-workers N` 并行运行 suite。
- [x] 保存 agent prompt、stdout、stderr 和 trajectory 路径。
- [x] 在 `run.json/suite.json` 中记录 agent step/token 用量。
- [x] Agent 运行后自动收集 `workspace/submission/`。
- [x] 自动调用 evaluator 生成 `eval/result.json`。
- [x] 用 fake command agent 做端到端测试。
- [x] 新增共享 Agent API 配置：
  - [x] `config/agents.example.toml` 作为非敏感模板。
  - [x] `.env` 保存本地 API key/base URL。
  - [x] `run-agent --agent-config --agent-profile --env-file`。
  - [x] 将 `FEATURELIFTBENCH_API_KEY` 映射到 `OPENAI_API_KEY`、`LITELLM_API_KEY`。
  - [x] 将 `FEATURELIFTBENCH_API_BASE` 映射到 `OPENAI_BASE_URL`、`OPENAI_API_BASE`。
  - [x] 将模型名映射到 `FEATURELIFTBENCH_MODEL`、`MSWEA_MODEL_NAME`。
  - [x] 支持在 profile 里配置 `agent_bin`，方便直接复用 conda/venv 内的 Agent。
  - [x] `run.json/suite.json` 只记录无密钥摘要，不记录 API key。

当前可运行：

```bash
python3 -B -m featureliftbench.cli run-agent \
  tasks \
  --agent mini-swe-agent \
  --agent-config config/agents.toml \
  --env-file .env \
  --num-workers 2 \
  --output outputs/mini-swe-agent/<run_id>
```

## 暂时不做

这些是明确的后续 backlog，不属于当前 pilot MVP 必做项：

* `featureliftbench/task/` 子包；
* `featureliftbench/evaluation/` 子包；
* `featureliftbench/baselines/` 子包；
* `docs/` 设计文档（已整理为 [docs/README.md](docs/README.md) 索引）；
* 更复杂的多 Agent leaderboard/report；
* 复杂 RelevanceScore；
* Docker eval 官方流程固化与 Agent 容器化；
* Go v2 多语言扩题（见 [BENCHMARK_SPEC.md](docs/BENCHMARK_SPEC.md)）。

等 evaluator 或 checks 模块继续膨胀时再拆子包。

---

## 历史里程碑（pilot → 50 hard，存档）

以下 Phase 0–6 checklist 为 **2026-06 初 pilot 开发记录**，路径已迁移至 `benchmark/tasks/`；保留供追溯，**非当前待办**。
