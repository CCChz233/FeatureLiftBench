# Plan: Closure-50 —— 第三个 split，真难度扩展

> **Status: active · Created: 2026-09-12**
> 目标：在**不触碰** freeze v2 的前提下新增 50 题，构成 250 题。
> 现有 200 题主表、`benchmark/tasks/`、`benchmark/hard50/`、
> `benchmark/python200_hard_tasks/` 与 freeze `6c20ff03…` 一律不动。
>
> `closure50` 是**内部存储标识**，与 `python150` / `hard50` / `prime` / `v2` 同级，
> **不定义论文难度层级**，也不作为论文对外名称。

## 1. 为什么需要这一轮

官方 Hard-50 在 freeze v2 Official Main 上对强模型已饱和，不能再作为难度证据：

| 组 | Flash | Pro | 参考解 LOC 中位 | hidden/public 测试数比 | 通过题 copy 中位 |
| --- | ---: | ---: | ---: | ---: | ---: |
| core100 | 90/100 | 94/100 | 2461 | 2.50 | 0.98 |
| **hard3（150 内后建 50）** | **18/50（36%）** | **21/50（42%）** | **101** | **4.00** | **0.086** |
| **Hard-50（官方扩展）** | **49/50（98%）** | — | 无 reference | 1.67 | 0.66 |

诊断（`reports/paper_analysis/python150_prime_v2_analysis_20260905/task_results.csv`，900 行）：

1. **Hard-50 的难度假设是错的。** 它按「大仓 + 大切片 + copy-all 诱饵」设计，
   结果通过题 copy 中位 0.66——**agent 靠复制就能过功能门**，诱饵只惩罚 RRES，
   不惩罚 Functional Pass。
2. **hard3 才是真难。** 参考解中位仅 101 LOC，通过题 copy 中位 0.086，
   意味着 agent 几乎无法复制、必须重新实现精确语义，于是漏行为。
   Pro+Flash 在 hard3 上 61 次失败中 public 41 / hidden 20。
3. **测试密度是杠杆。** hard3 的 hidden/public = 4.0，public 往往只有 1 条浅
   smoke，agent 得不到可拟合的反馈信号；Hard-50 是 1.67。
4. **Hard-50 没有 `reference_solution`（0/50）**，导致 RRES 无锚、G2/G3 校准门
   跑不起来、出题期难度校准失准（当年校准 29/50，主跑 49/50）。

六家全灭 28 题里 22 道来自 hard3；lift 为 Adapted 16 / Composite 8 / Direct 4；
机制集中在 `registry_plugin_dispatch`(10)、`data_model_coupling`(10)、
`framework_coupling`(10)。

## 2. 难度配方（从 hard3 反向提炼）

参照样本 `benchmark/tasks/celery__signal_dispatch_core__hard3_001`
（参考解 74 LOC，六家全灭）：

| 维度 | 取值 | 为什么 |
| --- | --- | --- |
| `required_api` 规模 | 1–2 个类/函数，2–4 个成员 | 接口面小，无法靠"面大"蒙对 |
| `behaviors` 条款 | 4–5 条语义条款 + 1 条 API surface + 1 条 isolation | 每条打一个**独立**易漏分支 |
| `public_tests` | **1–2 条最浅 smoke** | 不给 agent 可拟合的反馈 |
| `hidden_tests` | **4–5 条，每条对应一个 behavior** | hidden/public ≈ 4 |
| 参考解 | **80–150 LOC，单文件优先** | 逼重实现而非复制 |
| lift type | Adapted / Composite 为主，Direct ≤ 25% | 全灭题里 Direct 仅 4/28 |
| 机制 | registry 闭合、data-model 不变量、framework 耦合 | 与 contract-closure 主张一致 |
| **上游 `core_loc`** | **≥ 3000（硬门）** | 见 §2.1 |

### 2.1 选源硬门：`core_loc ≥ 3000`

`core_loc` = 上游实现行数，排除 tests / docs / examples，计入 `.py` 与
Cython `.pyx` / `.pxd`。

**为什么这是硬门。** 配方要求参考解 80–150 LOC。若上游核心只有几百到两千行，
这个切片就是整库的大部分，agent 复制核心文件即可通过——**这正是 Hard-50 的
病**（通过题 copy 中位 0.66）。hard3 之所以成立，是从数万行核心里抽约 100 行，
比例 0.25%，复制无从下手（copy 中位 0.086）。

判据只筛掉两个极端，**不把仓库大小当难度杠杆**：核心过小（切片≈整库）、
树过大（无法作为 workspace）。文档截图等 tracked 内容不得因大而剪除
（`FULL_REPOSITORY_SOURCE_POLICY` §1），故只对单个 >5MB 或二进制合计 >20MB 拦截。

工具：
- `python3.12 scripts/probe_closure50_sources.py` — 对已定 commit 的候选做探测
- `python3.12 scripts/screen_closure50_sources.py` — 批量筛查（PyPI 解仓库，
  GitHub tags API 解 tag→commit 并落盘缓存；不用 `git ls-remote`，本网络下单次 40 秒+）

台账：`reports/closure50/source_probe.json`、`reports/closure50/source_screen.json`。

**易漏分支的可用类型**（celery 例：sender 过滤 + dispatch_uid 去重 + 异常捕获配对
+ weakref 清理）：

- 异常分支与异常类型（不只是"抛错"，是抛哪个、在哪个入口抛）
- 默认值与短路路径
- 状态转移顺序、返回值保序
- 去重 / 覆盖优先级 / 别名解析
- 弱引用与生命周期清理
- 模块级可调用性（`module.__call__` 形态）

这些**全部必须写进 `public_spec.behaviors`**。难度来自"分支多且互相独立"，
不来自"藏起来"。

## 3. 目标带与校准

**目标：DeepSeek V4 Flash 功能通过率 25%–45%**（对齐 hard3 实测 36%）。

| 基线 | 期望 |
| --- | --- |
| Oracle（参考解） | public + hidden 全过，N=3 稳定 |
| Naive / shallow | public 可过，hidden **必挂** |
| Copy-all | 功能可过，但 RRES 明显劣于 reference |
| **Flash** | **>55% 换题；25%–45% 留；15%–25% 且契约公平可留；<15% 先查假难** |

**校准必须用 Official Main 同镜像同 profile**
（`featureliftbench-agent/eval:python200-prime-<tag>`、
`openhands_deepseek_v4_flash_main`）。Hard-50 当年用出题期另一次跑做校准，
主跑差了 20 题，本轮不重复该错误。

## 4. 禁止项（会造成假难或破坏可比性）

- **事后加 Hidden 压分。** 只允许换 slice / 换仓 / 补清公开义务。
- **Hidden 使用未声明 API。** `L2_C1_SURFACE` 为 blocking。
- 过严 `match=` 正则、糊契约、未声明成员（含 dunder）。
- 靠"更大的仓库 / 更大的切片"提难度——已被 Hard-50 证伪。
- 无 `reference_solution` 就发布。本轮要求 **50/50 有参考解**。
- 与现有 200 题的 upstream 仓库重叠。
- 触碰 freeze v2 题包、`suite.json`、已有 `run.json` / `eval/result.json`。

## 5. 落地位置

沿用 Hard-50 的目录与脚本模式，全部新建，不复用旧路径：

| 组件 | 路径 |
| --- | --- |
| 开发区 | `benchmark/closure50_pilot/` |
| Release | `benchmark/closure50/` |
| Design cards | `benchmark/selection/closure50_design_cards/` |
| Ledger | `benchmark/selection/closure50_expansion_20260912.json` |
| 选题矩阵 | `benchmark/selection/closure50_selection_matrix.json` |
| Source registry | `benchmark/sources/closure50_registry.json` |
| 参考解 | `benchmark/submissions/<task_id>/oracle/` |
| Suite | `benchmark/suites.toml` 新增 `closure50`；250 合并 suite 另行决定 |

可复用脚本（按 Hard-50 同名脚本改 split 路径，不覆盖原文件）：
`build_hard50_source_registry.py`、`generate_hard50_design_cards.py`、
`materialize_hard50_pilot_oracles.py`、`build_hard50_pilot_baselines.py`。

## 6. 分阶段

### Phase 0 — 选题矩阵 + cards（当前）

生成入口：`python3 scripts/build_closure50_selection.py`（`--check` 只读校验）。
产出 `closure50_selection_matrix.json` 与 `closure50_expansion_20260912.json`。

1. [x] 本文件 + 选题矩阵（配额、配方、校准带、source policy）。
2. [x] 20 道 ledger backup 按 §2 配方**重评**：**keep 12 / revise 4 / rejected 4**，
   可复用 16 道。剔除理由记在 ledger 的 `reassessment` 字段：
   - `fabric` — SSH/凭证依赖，违反离线选源
   - `injector` — 与 `dependency_injector` 机制重复
   - `myst-parser` — Sphinx 依赖重，且 markdown-it-py / sphinx 已在 200 内
   - `executing` — frame/AST 映射对解释器版本敏感，oracle N=3 稳定性风险
3. [x] Wave 1：4 张新仓 card（pybreaker / backoff / pkginfo / pyproject-metadata）。
   **这一批全部作废**——见下方 §6.1，源门把它们否了。
4. [x] **§2.1 源门落地并回溯全部候选。** 8 道被 `core_loc` 否，2 道未解析到
   tagged revision。这是本轮最重要的修正：Phase 0 选题时只看了机制与切片设计，
   没看上游核心规模，而后者恰是"copy 能否通过"的决定因素。
5. [x] Wave 2：批量筛查 27 个候选包，**12 个过门**，与既有 4 个合格源合并为
   16 个源已清候选，6 个机制族全覆盖。
6. [ ] 补足剩余 34 道：需继续筛查新仓（shortlist 里未过门的已剔除）。
7. **不 pin、不写测试、不写参考解。** ledger 与 card 内 `commit = pending_pin`、
   `branches_verified = false`：`planned_branches` 是**待核实的设计意图**，
   不是对上游当前行为的断言。分支未读过上游的，card 显式写
   `pending_source_read` 而不是填看起来合理的分支。

Card 渲染入口：`python3 scripts/generate_closure50_design_cards.py`
（`--check` 只读校验）。card 由 ledger 驱动，且只为**源已过门**的候选生成；
源被否的 card 会被自动删除，避免留下误导性设计卡。

### 6.1 源门否掉的候选

| 包 | `core_loc` | 原定位 |
| --- | ---: | --- |
| `backoff` | 674 | Composite / workflow（wave 1） |
| `pybreaker` | 715 | Composite / workflow（wave 1） |
| `pyproject-metadata` | 1782 | Adapted / resource（wave 1） |
| `confuse` | 1847 | Adapted / config |
| `ConfigArgParse` | 1862 | Adapted / config |
| `fastjsonschema` | 1962 | Adapted / validate |
| `respx` | 2227 | Adapted / registry |
| `PyHamcrest` | 2275 | Direct / validate |

另有 `pkginfo` 与 `docutils` 标 `pending_source_resolution`：未解析到 tagged
revision（docutils 在 SourceForge 而非 GitHub），在拿到不可变 revision 前不可用。

`circuitbreaker` 早前已排除：license 为 `NOASSERTION`。

**教训写进流程：** 选源必须先过 `core_loc` 门，再谈机制族与 lift 配额。
反过来做会得到一批"设计漂亮但 copy 就能过"的题，也就是 Hard-50。

### Phase 1 — Pilot 10（难度闸）

Pilot 按 lift 分层：**Adapted 5 / Composite 3 / Direct 2**（对齐 26/16/8 配额），
层内优先取能补全机制族覆盖的候选，且**只从过了 §2.1 源门的候选中取**。
**不得为凑满 10 道而跨 lift 顶替。**

当前 pilot **10/10**，lift 恰为 5/3/2，6 个机制族全覆盖，最低 `core_loc` 3384：

| Lift | 任务（`core_loc`） |
| --- | --- |
| Adapted | kombu 序列化注册表 (17343) · traitlets 配置 (6477) · omegaconf 合并/插值 (6270) · flit 元数据 (4717) · python-benedict keypath (3720) |
| Composite | dependency-injector provider 图 (6370) · huey 任务注册 (5487) · sismic 状态图解释 (3630) |
| Direct | wcmatch glob flags (3689) · bytecode 往返 (3384) |

每题流程：pin → `closure50_pilot/` materialize → `validate-task` → oracle N=3
→ isolation → naive / copy-all 基线 → **Flash Official Main 校准**。

**开工前置：** pilot 里 8 道的 `planned_branches` 仍是
`pending_source_read`。必须先读钉住的上游列出 4–5 条独立分支，才能写契约；
凭印象写分支等于编造上游行为。

过闸判据：Flash 落在 25%–45%，且九行门禁全绿、`undetermined = 0`。
**未过闸不开后 40。**

### Phase 2 — 扩满 50 + release

backup 换题；50/50 工程门；生成 registry 与 release 实体；独立 freeze
（新 `task_set_sha256`，不改 `6c20ff03…`）。

### Phase 3 — 评测

对新 split 跑 Official Main。**独立报告**，不并进 200 主表，不重写
`docs/STATUS.md` 里的 200 数字。论文中作为扩展/挑战集单列。

## 7. 与论文的关系

当前论文（`docs/paper/main.tex`）的范围是 200 题、150×6 主比较、50×5 扩展，
难度主张由 150 内部 hard3 承担。本轮**不改这些数字**。

Closure-50 的定位是下一版 benchmark 的难度扩展；只有在 Phase 3 出分后才决定
是否进入论文，且必须另列 freeze 与条件。不得在本轮把 Closure-50 写成已有结果。

## 8. 进度

- [x] 诊断：Hard-50 饱和原因、hard3 难度配方（§1–§2）
- [x] 选题矩阵 + ledger（`scripts/build_closure50_selection.py`）
- [x] 20 道 Hard-50 backup 重评：keep 12 / revise 4 / rejected 4
- [x] **§2.1 `core_loc` 源门落地**，回溯全部候选：8 道被否、2 道待解析 revision
- [x] Wave 2 批量筛查 27 个包，12 过门；合格源池 **16 道**，6 族全覆盖
- [x] **对照缓存源码核实分支**（`scripts/closure50_verified_slices.json`）：pilot 9/10 已核实
- [x] **dependency-injector recipe_rejected**：Cython 核心无法做 80–150 LOC 纯 Python extract
- [x] **第一道题包落地**：`benchmark/closure50_pilot/kombu__serialization_registry_core__001`
  - 参考解 107 LOC；public+hidden 7 passed；naive 实现 public 过、3 条 hidden 挂
  - `validate-task` valid=true
- [ ] 读 trio cancel-scope 源码（pilot 里唯一未核实的 Composite）
- [ ] 按 kombu 模板物化剩余 9 道 + oracle N=3 / isolation
- [ ] Pilot Flash Official Main 校准，判定 25%–45%
- [ ] 继续筛源补足 50（尚缺 35；DI 被否后合格池 15）
- [ ] 扩满 50 + release + 独立 freeze
- [ ] Official Main 评测
