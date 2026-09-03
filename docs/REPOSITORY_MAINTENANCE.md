# FeatureLiftBench 仓库整理与维护手册

> **Status: current · Last verified: 2026-09-02**
> 目标：整个仓库清晰、可维护；过时文件删除；当前论文身份不被整理误改。
> 本文是可复用流程，不是某一次清理的执行记录。每次大规模整理另写维护记录。

## 1. 目标

整理要同时做到三件事：

1. **清晰**：每个顶层目录一种职责；当前入口只有一套；同一事实只有一个 current 来源。
2. **可维护**：新成员能从 `docs/README.md`、`RUN.md` 和 catalog 理解、运行、改仓库。
3. **删除过时资产**：退役文档、重复副本、可重建缓存、放错位置的 checkout、不再被引用的一次性脚本应当删除或归档后删除，而不是无限堆积。

「清爽」服从身份保护。可以删过时文件，不能把 freeze、题包、唯一轨迹或旧套件结果伪装成新 Main。

本手册覆盖整个工作区：Git 跟踪的代码和文档、未跟踪的题包与 archive、原始实验、派生报告、venv/runtime/cache、根目录入口和退役脚本。

## 2. 不可破坏的原则

这些规则优先于「磁盘变小」：

1. **先盘点，后移动或删除。** 没有恢复方法的资产不得删除。
2. **整理与功能改动分开。** 未归属的工作区修改先处理完再开整理提交。
3. **禁止 `git clean -fd`、`git clean -fdx` 及等价大范围删除。** 必须按路径、按批次删。
4. **结果只认逐题 evaluator `functional_gate`。** 不得把 Agent `run.status` 写成 Pass。
5. **不得改写已完成实验。** Resume 只能补没有 terminal `run.json` 的任务。
6. **不得把旧套件结果重命名成当前 Main。** 套件、freeze、agent、method、镜像、attempt policy 必须保留身份。
7. **不得把 generated suite 的符号链接物化成第二份 task 实体。** Hard-50 不得因整理写入 `benchmark/tasks/`。
8. **高风险路径默认只盘点。** 移动或删除须维护者明确同意（见 §5）。
9. **整理变更不得和功能变更混成一个提交。**
10. **发现凭据只报告路径，不输出内容。** `.env` 和本地 agent 配置不得进 Git。

## 3. 什么算过时，什么必须留

### 3.1 默认删除或清理

满足下列条件之一，且能指出重建命令或 canonical 副本时，应当删：

| 类型 | 例子 | 删除前最低证明 |
| --- | --- | --- |
| 可重建缓存 | `__pycache__`、`.pytest_cache`、`build/`、integration `.venv`、`third_party/runtimes/` | pin / `setup.sh` / 安装命令仍可用 |
| 放错位置的生成物 | `artifacts/` 或 `docs/` 下的完整 upstream checkout、Agent workspace | 不是 freeze；不是唯一轨迹 |
| 未引用的一次性脚本 | 根目录旧 `run_*.sh`（正式入口已有替代）、scratch notebook | `RUN.md` / `docs/README.md` 已不指向它 |
| 重复 payload | 与已登记 SHA256 相同的第二份 bundle / archive 副本 | digest 一致 |
| 已归档的重复文档 | `docs/` 里仍标 current、但已被 `docs/archive/` 替代且无 current 链接 | `check_docs.py` 通过 |
| 未被论文或 STATUS 引用的 smoke/debug run | `experiments/smoke/` 里过期试跑 | 无 `reports/` / 论文稿引用 |

过时文档的处理顺序：**先改入口链接，再标 `Status: archived` 并移入 `docs/archive/`，确认无 current 引用后再删原路径。** 负结果方法稿（Rescue+、V2、TFL 等）默认归档保留，不直接删——它们仍是 RQ4 证据。只有「同一内容已在 archive 且 current 树里还有一份」才删 current 树里那份。

### 3.2 默认保留

| 类型 | 例子 |
| --- | --- |
| 当前权威 | `docs/STATUS.md`、`docs/FINDINGS.md`、`docs/EVALUATION.md`、freeze、suite JSON、source registry |
| 题包与依赖 | `benchmark/tasks/`、`benchmark/hard50/`、`benchmark/external50/`、`benchmark/sources/`、wheels、reference |
| 唯一原始运行 | `experiments/` 下仍被报告或论文引用的逐题 `run.json` / `eval/result.json` / 轨迹 |
| 已归档但仍被引用 | `docs/archive/` 中论文或 FINDINGS 链到的负结果 |
| 正式入口 | `RUN.md`、`setup.sh`、`scripts/run_benchmark.sh`、`featureliftbench` CLI |

组会稿已归档到 `docs/archive/snapshots/`，是 **derived**：数字冲突以 `docs/STATUS.md` 为准，不要当成第二份权威。

### 3.3 Unknown

来源、引用、重建方式任一项说不清 → 本轮 **不删不移**，记入维护记录。Unknown 不是删除许可。

## 4. 仓库资产模型

整理时每个目录或文件归入一类：

| 类别 | 定义 | 典型位置 | 默认处理 |
| --- | --- | --- | --- |
| Authority | 当前规范或机器事实的唯一来源 | `docs/STATUS.md`、registry、freeze、suite JSON | 跟踪；修改需审计 |
| Source | 产品代码、测试和维护脚本 | `harness/`、`docker/`、`integrations/`、`scripts/`、`tools/` | 跟踪；正常评审 |
| Benchmark payload | task、测试、source、wheel、reference | `benchmark/` | 按 release policy 跟踪或打包 |
| Raw evidence | 原始模型运行、轨迹和逐题 evaluator 结果 | `experiments/`（见该目录 README） | 默认不进 Git；登记、只追加 |
| Derived evidence | 可由原始证据重建的分析 | `reports/`、小型 `artifacts/` | 只跟踪小型可审查结果；过时可删 |
| Freeze artifact | 论文或 release 身份快照 | `artifacts/research_analysis/*/freezes/` | 跟踪；禁止覆盖 |
| Transfer bundle | 传输或发布压缩包 | `experiments/bundles/`、`exports/` | payload 不进 Git；跟踪 SHA256 |
| Historical gate | 出题期 oracle/naive/copy_all 校准 | `evidence/` | 不接收新的 Agent 主榜跑分 |
| Archive | 已退役但仍可能被引用 | `archive/`、`docs/archive/` | 文档可跟踪；大 payload 外部保存 |
| Rebuildable cache | 可用 setup/构建/运行再生 | venv、runtime、cache、`build/` | 忽略；确认 pin 后删除 |
| Compat wrapper | 根目录薄转发脚本 | `run_benchmark.sh`、`run_experiment.sh` | 只保留仍被文档引用的 |
| Vendor checkout | 按 pin 安装的上游，不进本仓库 git | `AutoSaddler/` | gitignore；可删本地目录 |
| Unknown | 无法证明来源或恢复方式 | 任意 | 冻结 |

判断：

```text
它是否仍被 current 入口、freeze 或唯一原始实验引用？
  ├─ 是 → Keep / Track
  └─ 否
      ├─ 能否用仓库命令和固定输入重建？ → Remove（缓存）或删派生报告
      ├─ 是否已有带 SHA256 的 canonical 副本？ → Remove 副本，或 Externalize 后删本地第二份
      ├─ 是否已有 Status: archived 且无 current 链接？ → Remove 重复 current 副本
      └─ 说不清 → Unknown，本轮停止
```

原始实验的目录合同以 [`experiments/README.md`](../experiments/README.md) 为准（`python/`、`methods/`、`validation/`、`bundles/`、`registry/` 等）。不要在本手册另造平行 run 布局。可提交的 suite 索引、路径映射和 bundle ledger 放在 `experiments/registry/`，不新建第二套登记处。

## 5. 谁可以删除什么

| 风险 | 谁执行 | 例子 |
| --- | --- | --- |
| 低 | 维护流程可直接删 | 缓存、未激活 venv、`.DS_Store` |
| 中 | 可删，但单独提交并跑文档/catalog | 退役 root wrapper、未引用 smoke、放错的 checkout、重复 bundle |
| 高 | **默认禁止**；须维护者在维护记录里点名同意 | `benchmark/` 题包与 source、freeze、仍被引用的逐题结果、`docs/STATUS.md` 所依身份 |

Agent 或协作者按本手册整理时：低/中风险可以做；高风险只登记建议，不擅自 `git rm` 或移动题包。

## 6. 顶层目录职责

新增内容必须落入下表。不要为了暂时方便再开新的顶层目录。

| 路径 | 唯一职责 | 不应放入 |
| --- | --- | --- |
| `benchmark/` | task package、suite、source registry、freeze 输入、离线依赖 | 模型运行日志、临时分析 |
| `agent/` | Agent 公共目录和稳定 ID | adapter 实现、凭据 |
| `method/` | Method 公共目录和协议映射 | 大型运行结果、临时 prompt |
| `harness/` | CLI、adapter、evaluator、Docker orchestration、单元测试 | 原始模型结果 |
| `integrations/` | 不改 harness 核心的外部方法对接 | `.venv`、上游 git 副本（用 pin 安装） |
| `docker/` | 正式镜像定义 | 本地 image tar |
| `scripts/` | 仓库维护、release、分析、正式运行入口 | 一次性 scratch |
| `tools/` | 研究分析/taxonomy/审计生成脚本 | 原始 suite 输出、题包 |
| `docs/` | 当前规范、runbook、论文文本 | 大型机器结果、完整 checkout |
| `docs/archive/` | 已退役但仍需引用的文档 | 标成 current 的规范 |
| `artifacts/` | 小型 freeze、selection、taxonomy、current 快照 | 完整上游 repo、Agent workspace |
| `reports/` | 小型派生审计 | 原始轨迹、完整 suite |
| `experiments/` | 原始实验与 bundle；布局见其 README | 手写权威规范 |
| `evidence/` | **历史出题 gate**（oracle / naive / copy_all 等） | 新的 OpenHands 主榜或 method pilot |
| `archive/` | 本地历史 payload 暂存 | 当前运行入口、当前规范 |
| `third_party/` | 由 pin 安装的 runtime | 应提交的项目源码 |
| `exports/` | 对外传输包和校验和 | 唯一原始证据 |
| `AutoSaddler/` | 可选本地 clone；gitignore | 不得 `git add` |

### 6.1 根目录入口

正式入口：

- 说明：`README.md`、`RUN.md`、`BUNDLE.md`
- 安装：`setup.sh`
- 跑实验：`./scripts/run_benchmark.sh`（或 CLI `featureliftbench`）
- 薄兼容转发：`run_benchmark.sh` → `scripts/run_benchmark.sh`；`run_experiment.sh` → `scripts/run_experiment.sh`
- 2026-09-02 已删除根目录旧 wrapper（`run.sh`、`run_openhands.sh`、`run_easy.sh`、`start_run.sh` 等）。不要再往根目录加新的 `run_*.sh`。新脚本进 `scripts/` 或 `harness/scripts/`。

## 7. 什么时候启动整理

满足任一条件即可开一轮：

- 根目录出现新的临时脚本、tarball 或运行输出；
- **未被 gitignore、也未在 registry 登记** 的未跟踪文件明显干扰日常 `git status`（不要用「含 ignore 的全部 untracked」当阈值）；
- 可重建缓存单个目录超过约 500 MB；
- 两个 current 文档数字或套件身份冲突；
- 正式实验缺 registry / suite 身份 / 逐题结果路径；
- `artifacts/`、`reports/`、`docs/` 混入完整 workspace 或 checkout；
- 组合 suite 被复制成第二份实体而不是 symlink；
- current 树里仍留着已归档方法的重复稿；
- release 前、论文数字冻结前、批量 promotion 前后；
- 距上次完整盘点超过三个月。

## 8. 标准整理流程

### 阶段 A：只读基线

不移动、不删除。记录：

```bash
git rev-parse HEAD
git status --short --untracked-files=all
git diff --stat
git diff --cached --stat
du -sh ./* ./.agents ./.github 2>/dev/null | sort -h
find . -maxdepth 2 -type d -name .git -print
find . -type f -size +50M -not -path './.git/*' -print
git ls-files .env harness/config/agents.toml flb.local.toml
```

维护记录里保存这些命令的摘要，不要粘贴凭据文件内容。

### 阶段 B：和工作区分开

把已有改动分成：题包/合同、harness、method 实验、文档、纯整理、缓存。同一文件既有功能改动又有整理改动时，先做完功能改动再整理。

### 阶段 C：清单

每个超过 10 MB、超过 100 个文件、或参与论文数字的目录登记：

```text
path:
category:
referenced_by:
canonical_copy:
rebuild_command:
size_bytes:
sha256_or_tree_digest:
retention: keep | archive | delete-candidate
proposed_action:
decision:
approver:          # 高风险必填
```

大资产登记进 `experiments/registry/`。freeze / suite / source 身份继续用现有 JSON，不另造事实源。

### 阶段 D：五种动作

| 动作 | 何时用 |
| --- | --- |
| Keep | 仍被 current 入口、freeze 或唯一实验引用 |
| Track | 小型、稳定、需要评审 |
| Ignore | 本地生成、不进 Git（同时可从磁盘 Remove） |
| Externalize | 必须留、但太大；仓库只留 SHA256 与获取说明 |
| Remove | 过时、可重建、或与 canonical digest 重复 |

`Unknown` 不是动作。

### 阶段 E：按风险批次删除或迁移

**低风险（直接清）**

- `.DS_Store`、`__pycache__`、`.pytest_cache`、`.ruff_cache`
- `build/`、`dist/`、`*.egg-info/`
- 未激活且可用 pin 重装的 `.venv`、`integrations/**/.venv`、`third_party/runtimes/`
- gitignore 的 `AutoSaddler/` 本地 clone（pin 仍在 `integrations/autosaddler_featureliftbench/AUTOSADDLER_PIN.json`）

**中风险（单独提交）**

- 文档和 `RUN.md` 已不再指向的根目录旧 wrapper
- `artifacts/` 里误放的完整 repo checkout
- 无引用的 smoke/debug run
- 与已登记 SHA256 重复的 bundle 副本
- current 树中与 `docs/archive/` 重复的过时方法稿（先改链接）

**高风险（须点名同意）**

- `benchmark/tasks/`、`benchmark/hard50/`、`benchmark/external50/`、`benchmark/hard50_pilot/`
- `benchmark/sources/`、`benchmark/vendor-wheels/`、reference submissions
- freeze、selection、source registry
- 仍被 STATUS / 论文 / reports 引用的 `experiments/` 逐题结果
- 仍被 FINDINGS 或论文引用的 archive

高风险不与缓存清理同批。

### 阶段 F：按批次验证

| 刚完成的批次 | 最少检查 |
| --- | --- |
| 低风险缓存 | `git status --short` |
| 文档、入口、ignore | `python3 scripts/check_docs.py --warnings-as-errors` |
| catalog / method / agent 目录 | `PYTHONPATH=harness python3 -B -m featureliftbench.cli catalog check` |
| 题包、suite、symlink | `python3 scripts/check_task_lifecycle.py` 以及对应 Oracle/Docker 门 |
| harness 代码 | 相关单元测试 |
| **移动或归档任何脚本** | **`PYTHONPATH=harness python3.12 -m pytest harness/tests -q` 必须全绿，不得靠 `--ignore` 掩盖** |

不要用文档检查代替题包功能门。文档检查也**发现不了**脚本移动造成的代码级断链：
`check_docs.py` 只查相对链接，`importlib.util.spec_from_file_location` 硬编码的路径
不在它的视野里。2026-09-02 复盘的实例见 §9 末。

批次结束后再看状态和体积：

```bash
git status --short --untracked-files=all
du -sh ./* ./.agents ./.github 2>/dev/null | sort -h
```

### 阶段 G：记录与提交

记录必须包含：日期、起始 commit、处理列表、每项删除的恢复方法、digest、验证命令、遗留 Unknown、suite/freeze 是否不变。

提交拆分：

1. policy / inventory（含本手册）
2. ignore / 缓存清理
3. 入口与退役脚本
4. 文档导航与归档
5. 证据/archive 迁移或删除（中高风险单独）

## 9. 专项规则

### 9.1 Benchmark 与 suite

- 实体只在 canonical split；组合视图用 symlink 或规定的 materialization。
- `benchmark/python200_hard_tasks/` 不是第二编辑源。
- 新题从 staging/pilot promotion，不直接写入 Main。
- Hard-50、External-50、Python-150、superseded 150+E50 身份不得合并。
- 清理前检查断链和 symlink 指向。

### 9.2 Experiments

- 原始 run 只追加。completed run 重跑后不得沿用同一 Pass@1 身份。
- 正式 run 登记 benchmark、agent、method、model、profile、镜像、attempt policy。
- 大结果不进 Git；Git 里只留 registry、checksum、必要小快照。
- 报告必须能回到逐题 `run.json` 与 `eval/result.json`。
- 新的 method/runtime 跑分进 `experiments/methods/` 或 `experiments/python/`，**不要**写入 `evidence/`。

### 9.3 Artifacts、reports、evidence

- `artifacts/`：freeze / selection / taxonomy / 小型 current snapshot。发现完整 checkout 就删或迁到忽略的实验目录。
- `reports/`：解释和审计，不覆盖 machine authority。同一统计只留一个 current；更旧的归档或删除重复。
- `evidence/`：历史出题 gate。新校准若要长期留，按 experiments 合同放，并在 registry 登记。

### 9.4 文档

- 数字：`docs/STATUS.md`
- 方法结论：`docs/FINDINGS.md`
- 评分与实验边界：`docs/EVALUATION.md`
- 出题规则：`docs/TASK_DESIGN_RULES.md`
- current 文档必须能从 `docs/README.md` 两跳到达。
- 历史文档进 `docs/archive/` 时标 `Status: archived`。
- 移动或删除文档前列出旧→新引用，同一批改链接，然后跑 `check_docs.py`。

已停用但仍要解释负结果的方法：保留 archive 一份即可，不要在 `docs/` 根上再留 current 副本。

### 9.5 本地 runtime

- `.venv`、integration venv、Agent runtime、npm tree 都可删后重装。
- 上游工具用 pin + setup，不把嵌套 Git 当本仓库源码提交。
- 清理前确认 pin 文档仍在（例如 AutoSaddler `AUTOSADDLER_PIN.json`）。

## 10. `.gitignore`

`.gitignore` 只阻止跟踪，不代替删除。改规则时：

1. 列出将被忽略的已跟踪文件；
2. 确认其中没有 freeze、测试、result snapshot、checksum；
3. 针对生成目录，避免过宽顶层通配；
4. 对 README / registry / SHA256 写显式例外；
5. `git check-ignore -v <path>`；
6. 再跑文档和 catalog 检查。

权威小文件 + 本地大 payload 并存时：默认 ignore payload，显式跟踪 README/registry/checksum。

## 11. 验收

一轮整理完成须同时满足：

- [ ] 过时/重复/可重建项已按清单删除或归档，而不是只移到另一个杂项目录
- [ ] 删除项都有重建命令或已验证 canonical 副本
- [ ] 高风险路径未在未批准的情况下被改
- [ ] 日常 `git status` 不再被未登记未 ignore 的垃圾淹没
- [ ] 根目录没有新的一次性脚本或运行输出；旧 wrapper 有去留结论
- [ ] current 文档可发现、无断链；过时文档不标 current
- [ ] 该跑的 docs / catalog / lifecycle / 测试已跑
- [ ] suite symlink、题量、source registry、freeze 身份未被意外改变
- [ ] 论文与 STATUS 数字仍能追溯到逐题 `functional_gate`
- [ ] 维护记录含日期、commit、digest、恢复方法、Unknown
- [ ] 整理提交与功能提交分开

判断标准：任意保留结果能说明来源；任意删除能说明如何恢复；任意 current 入口只指向一种实验语义。

## 12. 周期性清单

**每次正式实验后：** 登记身份与路径；确认逐题结果落盘；临时 workspace 与长期 raw evidence 分开；失败 run 先看是否还要做故障分析再删。

**每月：** 根目录新增文件；未 ignore 未跟踪文件；缓存体积；`artifacts/` / `reports/` 是否混入 workspace；STATUS 与其它 current 文档是否冲突；过时 current 文档。

**每季度或 release 前：** 完整流程；重建大资产 checksum；archive 与 experiments 去重；source/wheel/task/suite/freeze；docs、catalog、lifecycle、必要 Docker preflight；更新本文 `Last verified`。

## 13. 维护记录模板

复制到 `experiments/registry/` 或 `reports/audits/`（跟踪的小文件）或本地忽略目录：

```markdown
# Repository maintenance — YYYY-MM-DD

## Baseline

- Start commit:
- Branch:
- Active suites:
- Freeze / source digests:
- Tracked modifications:
- Untracked (not ignored):
- Workspace size:

## Scope

- Included:
- Excluded:
- High-risk approval:

## Asset decisions

| Path | Category | Size | Decision | Recovery | Digest | Approver |
| --- | --- | ---: | --- | --- | --- | --- |

## Changes

- Removed:
- Archived:
- Kept:
- Tracked:
- Ignored:
- Externalized:

## Validation

- [ ] git status
- [ ] docs check（若动了文档/入口）
- [ ] catalog check（若动了 catalog）
- [ ] lifecycle（若动了题包）
- [ ] suite/source/freeze identity
- [ ] 相关测试

## Unresolved

- Unknown:
- Follow-up owner:
- Next review:
```

## 14. 整理后发现问题

1. 立刻停止继续删，不造同名替代品冒充原资产。
2. 用维护记录找回原路径、digest、动作。
3. 从 canonical experiment、release bundle 或外部归档恢复。
4. 校验 SHA256 / tree digest。
5. 重跑受影响的 docs / catalog / lifecycle / Oracle。
6. 在记录里写事故原因和新的防护。
7. 无法证明与原资产一致时标为新版本，不得冒充原 freeze 或原 Pass@1。

### 14.1 已复盘事故：脚本归档断链（commit `50fcf71f`）

`50fcf71f`（Stratify official scripts）把 44 个脚本移进 `archive/`，其中两个仍被
硬编码路径引用，移动后**运行即失败**：

| 被移动 | 断链的引用方 | 性质 |
| --- | --- | --- |
| `scripts/harden_experiment_contracts.py` | `scripts/generate_contract_api_patches.py`（**在用脚本**）、`harness/tests/test_contract_hardening.py` | 生产代码 + 测试 |
| `scripts/audit_new_protocol_readiness.py` | `harness/tests/test_new_protocol_audit.py` | 测试 |

后果：三个测试在收集阶段就报 `FileNotFoundError`，一度被用 `--ignore` 绕过；而
`generate_contract_api_patches.py` 是 freeze v2 给 `required_api` 补成员要用的工具，
断了却没人发现。2026-09-02 已把三处路径改指 `scripts/archive/`，
`harness/tests` 恢复 **666 passed / 0 failed，无 ignore**。

`run_agentic_evidence_canaries.py` 是同一次归档里的另一类错误：它没有断链，但被归到
"killed-method / one-shot comparators"，而它其实是 Hidden provenance Gate 0/1 的
在用 runner。分类错误不会被任何自动检查抓到，只能靠归档时确认"这个脚本服务的
DoD 项是否还开着"。

**防护**：移动脚本后必须跑全量 `harness/tests` 且不得使用 `--ignore`；归档前先
`rg -n "scripts/<name>.py"` 全仓搜一遍硬编码引用，并确认该脚本没有在服务任何未关闭的
DoD 勾。
