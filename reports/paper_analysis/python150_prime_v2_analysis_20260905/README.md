# Python-150 freeze v2 分析（六模型）

输入：`python200-prime-v2-main-r1`（Pro 为同协议的 `python150-prime-v2-main-r1`）。只切 Python-150。Functional Pass = build ∧ public ∧ hidden ∧ isolation。空卷 = `submission/` 无文件，计失败。不用 `run.status`。GLM-5.3-Flash 已于 2026-09-06 收工，进 5.1/5.2/5.4/5.5。官方 Hard-50 不分析。Finding 3 分母仍是 Pro+Flash，不把 GLM 有包失败并进去。

复现：`python3 reports/paper_analysis/python150_prime_v2_analysis_20260905/analyze_python150_prime_v2.py`。F3 L1：`write_f3_annotations.py`（标签来自 SOP 精读，不是 packets 规则引擎）。Token 诊断：`token_usage.csv`。

## 5.1 能力

| 模型 | Pass | Wilson 95% | Core-100 | hard3 | 空卷 |
|---|---|---|---|---|---|
| DeepSeek V4 Pro | **115/150（76.7%）** | 69.3–82.7% | 94/100 | 21/50 | 0 |
| DeepSeek V4 Flash | **108/150（72.0%）** | 64.3–78.6% | 90/100 | 18/50 | 0 |
| Luna (OpenLux) | **102/150（68.0%）** | 60.2–74.9% | 82/100 | 20/50 | 6 |
| GLM-5.3-Flash | **68/150（45.3%）** | 37.6–53.3% | 62/100 | 6/50 | 38 |
| Qwen3.6-35B | **63/150（42.0%）** | 34.4–50.0% | 55/100 | 8/50 | 25 |
| GPT-OSS 120B | **36/150（24.0%）** | 17.9–31.4% | 25/100 | 11/50 | 2 |

Ceiling：最强 Pro 仍 35 题未过；28 题六家全灭（22 道 hard3）。GLM 没有解开这 28 题。未饱和。

Discrimination：Pro 比 Qwen 高 34.7pp，比 GLM 高 31.3pp，比 OSS 高 52.7pp（McNemar p≪0.001）。Pro vs Luna 18/5，p≈0.011。Pro vs Flash 10/3，p≈0.092，Wilson 重叠，**不能**写成 Pro 显著强于 Flash。Flash vs Luna p≈0.33。Luna vs GLM 43/9，p≈2×10⁻⁶。**GLM vs Qwen 27/22，p≈0.57，不能写成 GLM 强于 Qwen。** 不得把 Qwen 改成 63/125，也不得把 GLM 改成 68/112。

**F1.** Current coding agents exhibit substantial but incomplete feature-lifting capability on frozen Python-150, with large performance differences across model backends.

## 5.2 首败

| 模型 | Pass | Missing | Build | Public | Hidden | Isolation |
|---|---:|---:|---:|---:|---:|---:|
| Pro | 115 | 0 | 0 | 25 | 10 | 0 |
| Flash | 108 | 0 | 0 | 26 | 15 | 1 |
| Luna | 102 | 6 | 3 | 27 | 12 | 0 |
| GLM | 68 | 38 | 3 | 31 | 8 | 2 |
| Qwen | 63 | 25 | 6 | 35 | 21 | 0 |
| GPT-OSS | 36 | 2 | 18 | 70 | 23 | 1 |

Pro/Flash Build=0。失败主要在 Public/Hidden。Isolation 全表 4 次（Flash 1、GLM 2、OSS 1）。Qwen 的 Missing 是 TVE 空卷；GLM 的 Missing 是未交包（见 5.2.1），不是 Hidden 语义失败。

**F2.** Functional failures concentrate primarily at the behavioral gates: producing a buildable package is substantially easier than recovering complete required behavior.

本节不命名 Contract Closure。

### 5.2.1 过程

空卷不进 5.3。有包失败才进。过门但 `run.status≠passed` 仍算通过。

| 模型 | 空卷 | 其中 TVE/加密 | 5.3 有包失败分母 | 过门但 status≠passed |
|---|---:|---:|---:|---:|
| Pro | 0 | 0 | 35 | 2 |
| Flash | 0 | 0 | 42 | 82 |
| Luna | 6 | 5 | 42 | 54 |
| GLM | 38 | 1 | 44 | 23 |
| Qwen | 25 | 25 | 62 | 25 |
| GPT-OSS | 2 | 2 | 112 | 0 |

Qwen 25 空卷全是 `security_risk` TVE，不得改写成 63/125。GLM 38 空卷只有 1 条 TVE：多数是探索中途 `Goodbye` 未写 `submission/`（空卷侧 api_calls 中位 15），与 Qwen 的工具校验崩不是同一过程。Luna 6 空卷：3 TVE、2 `invalid_encrypted_content`、1 未写文件。`infrastructure_error.json` 在过门题上也很常见，是恢复后的 hiccup，不是未交付。Flash 82 道、GLM 23 道过门题 `run.status≠passed`，继续不用 `run.status`。GLM 的 44 条有包失败**不**并进 Finding 3 的 63。

### 5.2.2 Token / 步数（诊断，不是主指标）

每题 runner 都写 `agent/usage.json`，suite 有 `agent_usage_totals`。分析切 Python-150。`total_tokens` 是各次 API `usage` 之和；Pro/Flash 含 prompt cache，所以中位 2.4M/4.2M **不是**计费量。有 cache 账的用 `incremental` = uncached prompt + completion。Luna 与 GLM 的供应商响应没有 token 字段（150/150 `usage_unverified`），不能事后编。表：`token_usage.csv`。

| 模型 | token 有数 | 中位 total | 中位 incremental | 中位 completion | 中位 API calls | 中位 steps | 中位时长 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Pro | 150/150 | 2.42M | 88.0k | 32.8k | 43 | 42 | 8.0 min |
| Flash | 150/150 | 4.23M | 123.6k | 55.8k | 65 | 63 | 7.8 min |
| Luna | 0/150 | — | — | — | 29 | 36 | 8.0 min |
| GLM | 0/150 | — | — | — | 84 | 86 | 21.2 min |
| Qwen | 150/150 | 1.82M | —（无 cache 账） | 30.2k | 51 | 42 | 13.2 min |
| GPT-OSS | 150/150 | 0.53M | — | 12.9k | 24 | 19 | 1.6 min |

GLM 步数和墙钟最高，但 token 缺失，不能据此比较 FLOPs。OSS 最短。不得把 total_tokens 写成美元成本。

Process failures materially affect some model–harness configurations, but they are analytically distinct from artifact-level feature-lifting failures.

## 5.3 机制

操作规范：[docs/FAILURE_ANALYSIS_SOP.md](../../../docs/FAILURE_ANALYSIS_SOP.md)。本轮是 SOP **L1 精读**（契约 + 首败日志 + 提交）加轨迹筛 localization，不是 L0 残差桶。`assistant_first_pass`，无独立人工双审（未到 L2）。空卷不进。

**身份：** freeze `6c20ff03…`，镜像 `featureliftbench-agent/eval:python200-prime-212930ea`，No-Hint Main。Pro `python150-prime-v2-main-r1`（150）；其余模型同 freeze 切 Python-150。GLM-Flash 150/150 为 freeze v2，镜像 150/150 命中 `212930ea`。GLM 有包失败 44 条本轮未做 L1，不进下表。

有包失败 77（Pro 35 + Flash 42）。L0+L1 题目缺陷 **14 条 / 7 题** 不进 Agent 分母：`click.invoke`、`pluggy.call_historic`、`hatch` 连字符、`readme` 字面 `markdown`、`pytest` ini（B003 保留 description 空白 vs 测试要去掉）、`flake8.register_options`（required_api 未声明成员）、`setuptools_scm`（默认 `node` + B003 vs 公开测试要纯 `1.2.3`）。

有效 Agent 分母 **63**（Pro 28 / Flash 35）。这是 Finding 3 的分母，**不要**把后抽并进来。

轨迹层（4.5，localization）：63/63 有效失败都对 `repo/` 做了 find/grep/cat 或文件查看。`poetry` 读的是 poetry-core，只是接到 PEP 735 而公开输入是 `project.dependencies`。localization 仍为 0，但是筛过轨迹后的 0。

过程层（Protocol §6 筛查，不是金标）：Pro+Flash 77 条有包失败全部深读过 repo；0 条 `scope_not_inspected`；0 条命令里的 budget 字样；12 条最后一次编辑发生在最后一次 probe 之后（`stale_verification`）。**不**用过程标签改写输出侧 drift。

| Primary | 合计 | Pro | Flash |
|---|---:|---:|---:|
| behavior_drift | 54 | 26 | 28 |
| contract_api_completion | 7 | 2 | 5 |
| packaging_modularization | 2 | 0 | 2 |
| unknown | 0 | 0 | 0 |
| localization | 0 | 0 | 0 |
| dependency_closure | 0 | 0 | 0 |

闭合类（API 未闭合 + drift）61/63。主体是 drift。API 未闭合 7：缺异常分支（`aiohttp`、`installer`）、缺短路径（`json_logic` and）、模块不可调用（Flash `pendulum.datetime`、`python_dateutil.relativedelta`）、别名未解析（Flash `dateutil` zone）。Packaging 2：Flash `typer` Isolation `forbidden_imports`；Flash `bleach` 源码仍 `from bleach`（Hidden 命中公开条款 B006，Isolation gate 未拦住）。

同题不同因：Pro `keyring` 返回类而不是实例；Flash env 名 `BackendNotFound`。

### 后抽（Luna / Qwen / OSS）

SOP：未后抽不能写五模型机制。本轮对三家有包失败做分层抽样（seed `python150-postsample-v1`）：每家强制纳入已知缺陷题，再按 Build/Public/Hidden/Isolation 配额抽，共 **45** 条 L1。表：`postsample_annotations.csv`。

L0 扫了三家全部 132 条 Public 失败（名扫描）。L1 后抽又补进 2 道契约冲突：`flake8.register_options`、`setuptools_scm` 默认 node。已知缺陷题在抽样里仍剔除（含 Qwen 的 pytest Hidden）。`readme` 在 Qwen/OSS 上是 **Build**（缺 `pygments`/`nh3`），不当成 markdown 字面标记缺陷。

有效后抽 **32**（45−13 缺陷）：

| Primary | 合计 | Luna | Qwen | OSS |
|---|---:|---:|---:|---:|
| behavior_drift | 14 | 4 | 7 | 3 |
| contract_api_completion | 9 | 4 | 0 | 5 |
| dependency_closure | 4 | 0 | 3 | 1 |
| packaging_modularization | 5 | 0 | 1 | 4 |
| localization | 0 | 0 | 0 | 0 |

闭合类 27/32。localization 仍为 0（45/45 抽样也读过 repo）。与普查不同的是：**Qwen/OSS 的 Build 失败是缺传递依赖或仍 import 原包**，这在 Pro/Flash 有包失败上几乎没有。Luna 有效失败仍是 drift 与缺导出各半，没有 Build 包装主因。

后抽 **不能**并进 63，也 **不能**写成五模型同一张饼图。它只支持一句：强模型上的 closure 故事在 Luna 上同方向；弱模型额外有包装/依赖闭合失败。GLM 未抽。

**F3 闸门：** L1 精读；Pro+Flash 不是缺包；轨迹上 localization=0 且闭合类 61/63。后抽未推翻该方向，但 packaging/dependency 在 OSS/Qwen 样本里出现。未做 L2，比例仍是助手第一遍。

证据分层（SOP 4.6）：L0 筛查 Pro+Flash 77 + 三家 Public 132；L1 精读普查 77 + 后抽 45；轨迹筛普查 67 + 后抽 45；L2 0。

Hidden-only（Protocol §11，AI 辅助，普查）：25 条 / 17 题，冻结契约上 hidden→公开 clause 均已映射（未映射 0）。标注用到的 clause ID 都在 `public_clauses` 内。5 题冻结契约自带 mapping `conflict_count>0`。绝大多数题仍是 `formal_human_double_review_pending`。

**F3（助手 L1，非金标；分母=Pro+Flash 63）。** Artifact-level failures on the Pro+Flash slice are dominated by incomplete recovery of the required behavioral contract (a contract-closure gap), rather than by inability to emit an installable package or by failing to inspect the source tree. A stratified Luna/Qwen/OSS sample does not reverse that direction on Luna, but adds packaging and missing-helper failures on the weaker backends.

## 5.4 难度

Pro：Core-100 **94/100** vs hard3 **21/50**（χ²(1)=50.4）。Flash 90/100 vs 18/50（χ²(1)=48.2）。GLM 62/100 vs 6/50（χ²(1)=33.6）。六家全灭 28 题中 22 道是 hard3。OSS 几乎不掉（25%→22%）。GLM Adapted 24/76，其中 27 空卷，分组前已标成过程。Direct 40/56，Composite 4/18。

Lift type（Pro）：Direct 51/56，Adapted 55/76，Composite 9/18（n=18，Wilson 宽）。Flash 同方向。Qwen Adapted 含 16 空卷，分组前已标成过程。Entanglement level 全是 high，无分层。primary 上 Pro：parser_state 41/45，framework 18/28。`registry_plugin_dispatch` 11/22 vs `serialize_format_render` 18/19。

**F4.** Feature-lifting difficulty on Python-150 varies with the in-suite hard3 construction split and, more weakly, with lift type; entanglement level is uniformly high and cannot be tested here.

官方 Hard-50 不在此。

## 5.5 紧凑度（仅过门）

| 模型 | n | RRES 中位 | copy 中位 | copy-heavy | compact |
|---|---:|---:|---:|---:|---:|
| Pro | 115 | 0.993 | 0.957 | 108 | 4 |
| Flash | 108 | 0.998 | 0.968 | 105 | 1 |
| Luna | 102 | 0.815 | 0.164 | 54 | 37 |
| GLM | 68 | 1.013 | 0.947 | 64 | 0 |
| Qwen | 63 | 0.975 | 0.757 | 43 | 9 |
| GPT-OSS | 36 | 0.983 | 0.180 | 18 | 12 |

成对交集：Pro ∩ Luna = 97，copy 中位 0.966 vs 0.191。Pro ∩ Flash = 105，两边都是 copy-heavy。GLM ∩ Luna = 59，copy 中位 0.938 vs 0.275。原五家都过 24 题；六家都过 17 题：Pro/Flash copy ≈0.96–0.98，GLM 0.89，Luna 0.51。

**F5.** Correctness and compactness are distinct: a functional pass does not imply a compact extraction relative to the frozen reference.

## 5.6 案例

- TVE：`babel__plural_core__001`（Qwen，无包）。
- 过程空卷（非 TVE）：`alembic__revision_map_core__hard3_001`（GLM 探索中途结束、无包；同题 Pro/Flash 是 Public drift）。
- Public / drift：`alembic__revision_map_core__hard3_001`（两家：`get_revision('base')` 走符号 base，把 id 为 base 的 revision 影掉）。
- Hidden / API 未闭合：`aiohttp__url_params_core__hard3_001`（异常类和 token 检查都在，Hidden 仍有未抛出的无效名；不公开断言）。
- Isolation / packaging：`typer__command_parser_core__001`（Flash Isolation `forbidden_imports`）。Flash `bleach` 是 Hidden 先败：公开行为与 Isolation gate 都过，源码仍有禁止的原包 import（公开隔离条款 B006）。OSS 后抽 `lark`：提交在评测时从 `repo/` 加载上游包，隔离环境里该路径不存在。
- 题目缺陷：`pytest__ini_markers_core__001`（B003 保留 description 空白，公开测试要去掉）；`flake8.register_options` 与 `setuptools_scm` 默认 node 同属公开契约冲突。
- Copy：`blinker__signal_registry_core__001` 三家过门，RRES Pro 9.0 / Flash 18.4 / Luna 4.6，都是 copy-heavy。

## 收束

Python-150 未饱和（最强 76.7%，28 题六家全灭）。失败主要在 Public/Hidden。GLM-Flash **68/150**，与 Qwen 同档（McNemar n.s.），空卷 38 是未交包而不是 TVE。5.3 对 Pro+Flash 77 条有包失败做了 L1+轨迹筛+Hidden clause 映射+过程筛：剔除题目缺陷后 drift 为主，localization 在读过仓库的前提下为 0。GLM 44 条有包失败未标。Luna/Qwen/OSS 分层后抽 45 条：Luna 同方向；Qwen/OSS 额外有 Build 包装/缺依赖。无 L2。难度由 150 内部 hard3 撑住。过门后 Pro/Flash/GLM 几乎 copy-heavy，Luna 同题更紧。
