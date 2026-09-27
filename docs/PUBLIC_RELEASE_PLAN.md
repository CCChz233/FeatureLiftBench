# FeatureLiftBench 论文代码公开整理

盘点日期：2026-09-26。本文基于当前工作区，而非仅基于已提交版本。
配套机器可读盘点：[PUBLIC_RELEASE_INVENTORY.json](PUBLIC_RELEASE_INVENTORY.json)。
这是发布范围与准备清单，不代表已完成公开打包、许可证审查或全新环境复现。

## 1. 整个项目在做什么

FeatureLiftBench 是一个 **功能抽取 benchmark 与实证研究项目**：给 coding agent 一个固定版本的真实上游仓库，以及目标功能的完整行为契约，要求它交付可以独立安装、独立运行的软件包。

例如，任务可以要求从配置库中抽出环境变量优先级、配置文件解析和类型转换功能。产物既要实现这些行为，也不能在运行时偷偷依赖原仓库。

流程是：

```text
固定版本的源仓库 + 公开行为契约
                   ↓
     OpenHands + 指定模型定位、理解并抽取功能
                   ↓
              独立 submission
                   ↓
  无原仓库运行环境：Build → Primary → Extended → Isolation
                   ↓
  功能通过率；通过产物的 RRES、复制比例；过程诊断
                   ↓
            逐题结果 → 统计 → 论文图表
```

Functional Pass 要求四道门全部通过。RRES 是成功产物的规范化代码行数除以冻结参考实现的规范化代码行数；参考实现不是数学上的最小实现。Steps、Tokens 是过程诊断，不能代替功能正确性。

当前论文边界以 [paper_sources.json](paper-workbench/paper_sources.json) 和 [python150_membership.json](paper-workbench/writing/python150_membership.json) 为准：

- 150 个 Python 任务，126 个源仓库，132 个固定快照。
- 六个 OpenHands 配置 × 150 题，共 900 条主实验结果。
- 三配置 × 40 题 × Full Source / Contract Only，共 240 条消融结果。
- 失败阶段、源码读取证据、定性案例、执行过程及成功产物规模分析。

本篇核心贡献是任务集、评测协议和实证发现。历史 contract-closure、repo graph、其他 runtime、Go 任务及额外 Hard-50 不应混入本篇主实验。

## 2. 各目录的职责

| 当前路径 | 职责 | 发布时的定位 |
| --- | --- | --- |
| `benchmark/tasks/` | 任务契约、元数据、依赖、测试和源材料 | 按显式 150 题清单选择 |
| `benchmark/sources/` | 上游身份、commit、快照与哈希 | 保留身份与恢复能力 |
| `harness/` | CLI、agent runner、工作区边界、评测与指标 | 核心研究代码 |
| `docker/` | agent 与 evaluator 运行环境 | 复现实验必需部分 |
| `agent/`、`method/` | runtime / protocol catalog | 保留 Main 及其依赖；历史臂单独标注 |
| `scripts/`、`tools/` | 运行、任务维护、分析入口 | 保留当前流程及被调用依赖 |
| `docs/paper/` | 正文、参考文献、正式图像 | 论文源码，非实验复现包 |
| `docs/paper-workbench/` | 数据清单、分析与绘图、证据检查 | 论文复算核心 |
| `reports/`、`artifacts/` | 逐题派生结果、冻结身份、分类和验证记录 | 按论文依赖选择 |
| `experiments/` | 原始运行、轨迹、产物及恢复记录 | 精选、脱敏后作为数据附件 |
| `archive/`、`docs/archive/` | 历史实验和文件迁移记录 | 不整库发布；提取仍被当前流程依赖的材料 |
| `exports/` | 服务器传输包、历史发布包 | 不直接当作论文开源包 |

## 3. 建议公开哪些材料

建议分为一个代码仓库和配套的数据附件。小型代码、契约和分析数据放在代码仓库；较大的源快照、运行记录、产物和离线依赖按版本打包，附下载位置、SHA-256 和恢复步骤。

### A. 核心代码与实验环境：应公开

- `pyproject.toml`、`harness/featureliftbench/`、相关 `harness/tests/`。
- Python agent / evaluator 的 Dockerfile、构建脚本、entrypoint。
- `scripts/run_benchmark.sh` 及实际调用链、源码物化脚本。
- `agent/registry.toml`、`method/registry.toml`、使用到的 suite/config、runtime pins。
- 不含凭据的六配置 Main 和三配置消融设置：模型标识、agent revision、prompt、步数、上下文与超时、单次 attempt、镜像身份。
- 任务设计、源码身份、评测规范和结果字段说明。

首次整理应优先保证运行依赖齐全。不能仅按目录名删除历史方法模块：现有 runner 和 catalog 仍可能引用它们。可以先保留并注明“非论文实验”，再在独立变更中裁剪。

### B. 150 个任务与评分材料：应公开或提供可获取的版本化附件

对 membership 中每个 task ID，保留：

- `TASK.md`、`metadata.json`、`requirements.lock`。
- `public_tests/`、`hidden_tests/`、`evaluation/` 中评分所需文件。
- canonical source 身份、固定 revision、快照 digest 和恢复方法。
- 对应的 reference/oracle 实现、冻结 reference 指标与验证记录。
- 原始 freeze 与 membership 的关系、任务构建/修订记录和必要的历史身份文件。

**测试公开与 agent 可见是两件事。** Main 运行时，benchmark 的 public/hidden 两组测试均不提供给 agent；评测器单独使用。名称中的 `public` 也不代表 Main 必须把它挂载给 agent。源仓库自己的测试和文档是另一类材料。

本次盘点：选定 150 题的两组测试与 oracle manifest 都已被 Git 跟踪；2026-09-01 发布记录还说明部分 Python-150 hidden tests 已进入公开历史。因此它们可以作为已发布评测资产，不能一概声称是从未公开的秘密 holdout。未来运行需记录评测日期和版本，保持运行时隔离。

参考实现目前主要在：

```text
archive/paper_unrelated_20260914/benchmark/submissions/<task_id>/oracle/
archive/paper_unrelated_20260914/benchmark/references/
```

150 个所选任务均找到 oracle 目录，但这只是存在性盘点，不是代码、digest 或执行正确性复验。发布时需要恢复明确的可访问路径，并核验与冻结版本一致。只有 oracle manifest 和历史 450/450 记录，不等于已交付可重跑的 reference 实现。

上游材料优先通过 registry + 固定 commit + 物化脚本恢复；如附带快照，应逐项保留对应许可证、归属和来源记录。当前 `benchmark/tasks/*/repo/` 中已有大量跟踪文件，不能假定 `.gitignore` 已排除所有上游代码，也不能未验证就整块移除。

### C. 论文数据与分析：应公开

以 [paper_sources.json](paper-workbench/paper_sources.json) 为起点，发布其输入和运行分析脚本实际访问的依赖：

| 论文证据 | 当前主要位置 |
| --- | --- |
| 150 题身份与构成 | `docs/paper-workbench/writing/python150_membership.json`、`chapter2_python150_task_inventory.json`、`chapter2_python150_evidence.json` |
| 900 条主实验结果 | `reports/paper_analysis/python150_prime_v2_analysis_20260905/task_results.csv` |
| 主表与配对统计 | `reports/paper_analysis/python150_paper_analysis_final/` 中所需 CSV/JSON |
| 最终保留的 240 条消融 | `docs/paper-workbench/data/source_ablation_retained_20260921/` |
| 消融源记录与重算 | `reports/paper_analysis/source_ablation_40_20260913/`、`writing/recompute_retained_ablation.py` |
| 源码暴露分析 | `reports/paper_analysis/source_exposure/diagnosis/` 及统计文件引用的上游派生记录 |
| 执行过程分析 | `docs/paper-workbench/data/token_efficiency_20260917/`、`execution_effort.py` |
| 定性 40-case 分析 | `docs/paper-workbench/data/qualitative_themes_20260920/`、案例选择和映射说明 |
| 图表与检查 | `scripts/paper.py`、`paper_inputs.py`、所需 `writing/*.py`、模板、`figures/scripts/` 和依赖 |

不能只发布最终图表和汇总百分比；需要逐题数据、分母、筛选规则、统计参数、随机种子和缺失值说明。定性样本内的类别计数也不能当成所有失败的总体比例。

历史消融文件有多个口径。当前入口选择的 Pro Contract Only 为 **6/40 通过、18 个 Missing**；发布需保留最终选择依据及来源关系，避免读者误用旧的 7/40 文件。保留必要的版本/例外记录，不能通过删除旧记录制造不存在的证据完整性。

`paper_sources.json` 不是全部传递依赖的打包白名单：例如源码暴露读取和历史 reference 校验还会访问清单以外的文件。应在干净发布目录实际执行检查，补齐依赖。

### D. 原始运行与生成产物：建议公开可恢复部分，并披露覆盖率

按 task/model/arm/attempt 组织 `run.json`、`eval/result.json`、submission、轨迹、usage、终止原因及例外记录。大文件可放配套数据附件，代码仓库保存索引和校验和。

当前完整逐题主结果矩阵有 900 条，但本地原始主实验 profile 仅 **307/900**：Pro 150、Flash 150、GLM 7。其余 593 未恢复。profile 存在也不自动代表该次运行的轨迹、产物、usage 均完整，应分别报告覆盖率。

可以公开“论文数值复算材料 + 已恢复原始证据”；在补齐之前，不应称为“900 次完整原始实验包”。源码暴露的 900 条派生记录也不能替代原始轨迹。

### E. 论文源码：可公开，不能替代代码与数据

`docs/paper/` 中正文、参考文献和当前正式图片可以随发布提供。`scripts/paper.py package` 生成的是 Overleaf 论文包，不含完整 benchmark、分析依赖和实验原始数据。

当前部分示意图是经后期编辑的定稿资产；应发布定稿图片并标明可重建范围，不宣称所有图都能从现存 Python 脚本逐像素生成。

## 4. 不应整包放进论文公开仓库的内容

| 内容 | 处理 |
| --- | --- |
| `.env`、真实 `agents.toml`、本地连接配置、密钥 | 排除；仅留示例和环境变量名 |
| 原始轨迹中的认证头、token、服务凭据 | 发布前检查并脱敏；保留原始记录与脱敏副本的映射 |
| 额外 Hard-50、Go/pilot、未纳入论文的方法实验 | 不纳入论文必需包；如另发，明确范围 |
| `.git/`、虚拟环境、缓存、编译中间文件、重复 ZIP/TAR | 不进入数据附件 |
| 全部 `experiments/`、`archive/`、`exports/` | 按依赖和证据选择，不直接递归打包 |
| 编辑器设置、agent skills、内部写作草稿与设计备选 | 通常不是复现必需项 |

“不整包发布”不等于删除本地文件。尤其归档中的 reference、freeze 依赖和结果来源仍需提取进发布材料。排除完整上游仓库时也不能误删任务运行所必需的资源或构建文件。

## 5. 当前发布前要处理的具体缺口

| 优先级 | 观察到的问题 | 完成标准 |
| --- | --- | --- |
| 必需 | `docs/paper-workbench/` 当前 Git 跟踪文件数为 0；迁移后的文件已在工作区存在 | 对选定文件逐项纳入发布；从导出的仓库验证实际存在。不能直接依赖 `git archive HEAD` |
| 必需 | 根目录没有 `LICENSE` 和 `CITATION.cff`；`docs/paper/LICENSE` 是 LPPL 文本 | 明确自有代码、任务数据及第三方内容的许可证范围，补引用元数据；不把论文模板许可证自动当作整个项目许可证 |
| 必需 | reference 与离线依赖已归档；旧 bundle 脚本仍访问历史路径 | 提供可执行的恢复/下载流程，核验对应 150 题的 reference 与指标 registry |
| 必需 | 当前规范写 150 步，示例配置仍有大量历史 120 步值 | 发布独立、明确的论文配置，并记录历史运行配置与当前复现配置的关系；不覆盖历史原始 profile |
| 必需 | 部分 README 仍指向不存在的 `docs/paper/writing/`、`paper_sources.json` 和绘图路径 | 统一到当前 `docs/paper-workbench/`，消除发布入口死链接 |
| 必需 | 核心安装依赖与图表分析依赖分开，默认系统 Python 为 3.9 | 声明 Python 版本与两类安装步骤，在干净环境验证 |
| 必需 | 源资产、冻结历史与代码可能受不同许可证约束 | 完成第三方来源/许可清单；本次没有逐个审查 126 个上游项目 |
| 需披露/恢复 | 缺少 593 个原始主实验 profile | 补齐或准确公布缺失清单与各类证据覆盖率，不用重跑结果冒充原记录 |
| 需复验 | 尚未在独立发布副本做 Docker smoke、reference 和全链路复现 | 记录运行命令、环境、镜像身份、预期输出和实际验收结果 |

本次仅检查敏感配置文件名的跟踪情况，没有完成内容级密钥扫描或完整 Git 历史审计。发现一个被跟踪的上游 `tests/.env` 路径，不凭文件名判断它是实际凭据泄露。

## 6. 建议的整理执行顺序

1. 固定当前论文 membership、manifest、数据文件哈希；记录工作区相对提交的变化。
2. 在独立发布目录按白名单装配材料，首版尽量保留现有路径以减少 import 和 provenance 断裂。不要改变 frozen task/hash 来追求目录美观。
3. 加入迁移后的分析代码和数据、必要的历史 freeze、归档 reference 及其恢复映射；明确排除范围。
4. 补论文专用实验配置、依赖安装说明、LICENSE/CITATION 和第三方来源说明；检查凭据、绝对路径与符号链接。
5. 从干净副本执行离线数值检查，再做任务/源码恢复、Docker smoke 和 reference 验证。原始证据严格审计独立报告。
6. 将大数据附件与代码版本绑定，记录 SHA-256、缺失项和恢复命令，再创建正式 release/tag。

没有必要为了首次公开大规模改名和重构所有目录。把“当前论文所用内容、安装入口、执行入口、数据来源、已知限制”讲清楚，比把历史路径全部重命名更重要。

## 7. 本次已经验证到什么程度

在现有 Python 3.12.2 环境中实际执行：

```bash
python -B scripts/paper.py check
PYTHONPATH=harness python -B -m featureliftbench.cli catalog check
python -B scripts/paper.py audit
```

- `check`：通过；核对 150 题范围、900 条结果、当前论文引用、表格及执行过程派生数据。
- `catalog check`：通过；不代表源码、Docker 或外部 API 已就绪。
- `audit`：按预期失败，明确报告 307/900 profile 可用、593 缺失。
- 系统默认 Python 3.9 的尝试分别遇到缺少 SciPy / `tomllib`，改用已有 Python 3.12 环境后前两项通过。发布文档应提供规范环境安装流程。

本次没有运行模型、Docker 评测、完整 harness 测试、参考实现复验或论文编译，也没有发布远程仓库。新增的是本指南与材料盘点，未搬移任务、实验或论文数据。

## 8. 对外介绍可以怎样写

可按实际发布结果使用下列中文描述，并补上具体版本与链接：

> 我们发布 FeatureLiftBench 的 150 个 Python 任务、固定源仓库身份、评测实现、实验配置及论文分析代码，并提供主实验与消融的逐题结果和相应证据索引。复现材料区分基于保存结果的论文数值复算、独立产物重新评分和调用模型重新运行实验。原始运行记录的可用范围及缺失项在数据说明中明确列出。

这段文字需要在对应材料实际发布后使用；不要提前写成“全部原始实验已公开”或“完整一键复现已验证”。
