# FeatureLiftBench

**Can code agents decouple features from entangled repositories?**

FeatureLiftBench 是一个仓库级代码 Agent benchmark。它给 Agent 一个固定
版本的完整源码仓库和完整公开功能契约，要求 Agent 自主定位实现、理解依赖、
发现或构造验证方法，并把目标功能抽取成独立、行为完整且紧凑的 Python
package。

[当前状态](docs/STATUS.md) ·
[设计原则](docs/BENCHMARK_DESIGN_PRINCIPLES.md) ·
[运行实验](docs/SERVER_RUNBOOK_PYTHON150.md) ·
[文档索引](docs/README.md)

## 当前状态

截至 2026-07-27：

- Python v3 External Main：**150/150 ready**；
- source registry：**126 个外部开源仓库、132 个 immutable snapshots**，
  Main 中没有本地 curated source；
- Curated split：**7 题**，与 Main 分离；
- Full-Repository / No-Hint：**150/150**；
- Docker Oracle：**450/450**（150 题 × 3 次），0 unstable；
- 对抗性 isolation canaries：**12/12**；
- active benchmark freeze：见
  [`artifacts/research_analysis/v3/current_benchmark_freeze.json`](artifacts/research_analysis/v3/current_benchmark_freeze.json)；
- v3 模型 baseline：**尚未运行**。

已有四模型结果使用旧的 `mixed_snapshot_v1` 源码条件，只能作为历史或
消融证据，不能换标签成为 v3 结果。详见
[实验清单](docs/EXPERIMENTS.md)。

## 测什么

目标不是 bug fixing，也不是按需求从零实现一个新功能。主任务是
behavior-preserving feature extraction：

1. 在完整真实仓库中定位目标功能；
2. 恢复必要的 API、行为、内部依赖、资源和配置；
3. 去掉原项目的框架、全局状态、无关模块和运行时耦合；
4. 在 `submission/` 中交付可独立安装或导入的 `featurelifted` package；
5. 通过提交后执行的私有 evaluator；
6. 在功能通过的前提下，用 reference-relative 指标衡量紧凑性。

典型缠绕包括 parser state、data model、framework/plugin、config/environment、
resource、third-party dependency 和 legacy/vibe clutter。

## Main 的信息边界

| Agent 可见 | Agent 不可见 |
| --- | --- |
| 完整、固定、经 digest 校验的上游源码树 | source entrypoints、文件/符号/行号提示 |
| 由 `public_spec` 生成的完整 `TASK.md` | benchmark `public_tests/` 与 `hidden_tests/` |
| 锁定依赖和统一输出目录 | reference/oracle、evaluation 配置 |
| 上游仓库自带的 tests/docs/examples/resources | 难度、纠缠标签和 reference support set |
| Agent 自己创建的测试和工具输出 | 任何 submission 后的 evaluator 反馈 |

这里的 `public tests` 表示较基础的 evaluator regression layer，`hidden
tests` 表示更深的边界和组合行为层；在默认 test-blind Main 中二者都只在
submission 完成后运行。若把基础 evaluator tests 提供给 Agent，必须显式
标为 `Public-feedback` 消融臂。

## 输入与输出

正式 workspace：

```text
workspace/
  TASK.md
  repo/                  # canonical full source snapshot
  requirements.lock
  submission/
    pyproject.toml
    featurelifted/
      __init__.py
      ...
```

`repo/` 由 [`benchmark/sources/registry.json`](benchmark/sources/registry.json)
指向的 immutable archive 物化，不使用 task-local 裁剪源码作为 v3 Main
输入。Agent 只能写 `submission/`，评测时原仓库不会进入 submission 的
`PYTHONPATH`。

## 评测

主指标是每题一次 evaluator 运行得到的 Functional Pass@1：

```text
FunctionalPass =
  BuildPass
  ∧ PublicTestsPass
  ∧ HiddenTestsPass
  ∧ IsolationPass
```

功能结果与 Agent 进程是否超步数、token 用量和紧凑性分别报告，不混成一个
headline composite。紧凑性只相对 frozen reference 计算，包含：

- submission/reference Python LOC；
- submitted/reference file count；
- copied LOC / copied fraction；
- dependency footprint；
- excess copied LOC（reference support 信息充分时）。

完整上游仓库 LOC 不作为紧凑性分母。兼容字段 `final_score` 当前等于
`functional_gate`；compactness 单独输出。完整定义见
[Evaluator and Scoring](docs/03_evaluator_and_scoring.md)。

## 数据集

| Split | 数量 | 用途 |
| --- | ---: | --- |
| `benchmark/tasks/` | 150 | Python v3 External Main |
| `benchmark/curated/tasks/` | 7 | Curated extension；不进入 headline |
| `benchmark/sanity/` | 3 | harness smoke |
| `benchmark/go/tasks/` | 12 | Go seed/calibration，非 paper-ready Main |

Python-150 来自 126 个 canonical external repositories。按任务来源类型：

- library：102/150；
- developer tooling：29/150；
- framework/plugin：17/150；
- application/service：2/150。

旧 `core100` / `hard50` 只保留为构造和分析切片；当前 150 题 metadata
均标为 `hard`，经验难度要在首轮冻结 v3 baseline 后重新校准。仓库规模、
领域、纠缠分布与来源集中度见
[Python inventory](docs/python/02_python_repo_task_inventory.md)。

## 快速开始

推荐 Python 3.11+、Docker 和 Linux/WSL2：

```bash
PYTHON=python3.12 SKIP_MINI=1 ./setup.sh
cp harness/config/agents.example.toml harness/config/agents.toml
```

在 `.env` 中配置模型 API，然后构建 agent/eval 镜像：

```bash
FEATURELIFTBENCH_AGENT_PYTHON_BASE=python:3.12-slim \
FEATURELIFTBENCH_INSTALL_OPENHANDS=1 \
  docker/build_agent_image.sh featureliftbench-agent:latest

docker/build_eval_image.sh featureliftbench-eval:latest
```

正式 Python-150 runner 默认只生成 plan，不调用模型：

```bash
./harness/scripts/run_python150_paper.sh \
  <openhands-profile> \
  <run-id>
```

确认 plan 显示 150/150 v3-ready、Full-Repository / No-Hint、agent/eval
Docker、active freeze 和每题一次 Pass@1 后再执行：

```bash
./harness/scripts/run_python150_paper.sh \
  <openhands-profile> \
  <run-id> \
  --workers 1 \
  --execute
```

服务器部署、smoke、监控、续跑和结果验收见
[v3 Python-150 Server Runbook](docs/SERVER_RUNBOOK_PYTHON150.md)。
本地命令速查见 [RUN.md](RUN.md)。

## 任务维护

单题事实源是：

- `benchmark/tasks/<task_id>/metadata.json`；
- 由 `public_spec` 生成的 `TASK.md`；
- public/hidden tests 与 `evaluation_spec`；
- canonical source registry；
- frozen reference/compactness records；
- 自动 lifecycle、No-Hint、Oracle、isolation 和 determinism gates。

校验单题：

```bash
PYTHONPATH=harness .venv/bin/python -B -m featureliftbench.cli \
  validate-task benchmark/tasks/<task_id>
```

新增任务先进入 `benchmark/staging/` 或 `benchmark/batch3_pilot/`，通过完整
门禁后才允许 promotion。规则见
[Task Design Rules](docs/TASK_DESIGN_RULES.md) 和
[Incremental Task Rules](docs/07_incremental_task_rules.md)。

## 项目结构

```text
benchmark/
  tasks/                 # Python-150 task definitions and evaluator assets
  sanity/                # smoke tasks
  sources/               # canonical source registry; archives are local/ignored
  references/            # private/frozen reference records
harness/
  featureliftbench/      # runner, evaluator, workspace and freeze logic
  scripts/               # maintained operational scripts
docs/                    # current project documentation
experiments/             # local/raw model runs and transport bundles
reports/                 # audits, result summaries and historical evidence
artifacts/               # machine-readable research/freeze artifacts
```

任务包里的 `repo/` 是 Pruned-Context 消融的冻结输入；v3 Agent workspace 使用 canonical
source registry 物化的完整快照。大体积 source archives 和原始模型输出默认
不提交 Git。

## 结果边界

- 当前 benchmark 工程上已经可以启动完整 v3 实验。
- 当前还没有可写入 v3 论文主表的模型结果。
- 历史 mixed-snapshot 结果可用于说明模型差异和失败模式，但不能回答
  Full-Repository / No-Hint 条件下的最终性能。
- 独立人工审核已取消为准入门槛；AI-assisted/maintainer 记录只能表述为
  provenance，不能写成 independent human gold。

## 文档

完整导航见 [docs/README.md](docs/README.md)。日常只需要：

- [STATUS.md](docs/STATUS.md)：当前数字和是否可跑；
- [CURRENT_RESEARCH.md](docs/CURRENT_RESEARCH.md)：下一步；
- [BENCHMARK_DESIGN_PRINCIPLES.md](docs/BENCHMARK_DESIGN_PRINCIPLES.md)：核心原则；
- [EXPERIMENTS.md](docs/EXPERIMENTS.md)：已有和缺失实验；
- [REPORTS_INDEX.md](docs/REPORTS_INDEX.md)：证据位置。

## Citation and License

论文引用信息和 benchmark release license 尚待最终发布时补齐。上游源码按
各自许可证获取；source policy 记录 URL、revision、license、archive digest
和复现方式，详见
[Full-Repository Source Policy](docs/FULL_REPOSITORY_SOURCE_POLICY.md)。
