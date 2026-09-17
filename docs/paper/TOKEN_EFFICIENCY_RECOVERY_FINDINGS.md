# Fig.4 缺失数据：恢复核查与完整原始材料交付

2026-09-17。目的：区分 token 时间线、模型响应时间线、产物回放的可恢复性；不重跑 Agent，不编译，不修改正式实验结果。本次没有修改论文或正式图。

## 当前结论

- 两个 panel 不应强制使用同一联合子集。缺 token 不意味着缺模型响应事件。
- Luna/GLM：现有交付的历史逐调用用量不可用；Table 1 作者确认的汇总仍有效，但不能由总量唯一推导首次通过前后的用量。若服务器未保留原始 provider usage，精确 token PSF 无法恢复。新的 probe 或按总量摊分不能填补原运行。
- Qwen：63 个成功运行的总 token 完整；58 个的调用映射不是 exact，不能把候选前缀之和确定误当成事件匹配确定。优先核对原始事件与 audit，不需要先重跑任务。
- 右 panel 可以独立计算“首次观察到通过版本后的模型响应数”。若要继续称为“模型请求数”，必须另外计入未产出响应的重试、失败请求和辅助调用，不能混用概念。

## 本地实测的可恢复范围

下表中的候选要求交付标记为完整时间线、最终目录匹配、最终评测匹配、无 unresolved 状态，所有已交快照评测已知并存在通过版本。未重新证明完整回放，因此它是待核查队列，不是最终可发表样本。

| 配置 | 正式成功 n | 产物历史候选 n | 本地有原始事件的成功 n | 已定位首次通过事件的候选 n |
|---|---:|---:|---:|---:|
| Pro | 115 | 102 | 115 | 102 |
| Flash | 108 | 96 | 108 | 96 |
| Luna | 102 | 75 | 0 | 0 |
| GLM | 68 | 46 | 2 | 1 |
| Qwen | 63 | 50 | 0 | 0 |
| OSS | 36 | 34 | 0 | 0 |

GLM 的 `attrs__validators_core__001` 可用首次通过 observation event ID 定位到原始事件。去重 llm_response_id 后，该边界后出现 65 个此前未出现的模型响应。这里没有 token 前提，证明独立恢复响应指标可行；不等同于已核验全部 HTTP 请求。

最新 token 主包提供 calls、artifact timeline、snapshot evaluations，证据包提供产物、回放结果等，但未包含完整 openhands_events/context_audit/persistence 原文件。包内 Luna、GLM、Qwen 的 calls 行均无 response_id/event_ids，不能凭现有摘要重建精确映射。

旧 `paper-results-full-20260913T154543Z.tar.gz` 全量读取遇到 EOF，不能视为完整原始日志备份；本地目前只有 Pro/Flash 及部分 GLM 的原始事件。

## 给服务器 Agent 的执行要求

**请把正式 150 tasks × 6 configurations 共 900 个原始运行的相关原始文件完整打包交回，不要只交汇总 CSV、筛选后的成功样本、修复后的表格或几个案例。原始文件本身就是本次必需交付物。**

范围以 `docs/paper/paper_sources.json` 的正式 main comparison 和原 token 包的 `run_manifest.csv` 为准：包含成功和失败，限定正式 150 题；不要混入 ablation、probe、其他任务或新运行。即使原 suite 名称包含 python200，也按正式清单选出对应 150 题。保存全部 900 行运行索引，缺文件明确列出，不能删除该运行。

按以下顺序执行：先打包现存原始材料，再做恢复分析。**即使恢复分析未完成、usage 仍为空，也必须交回完整原始材料包**，这样本地可以继续核查，不需要反复索要日志。

### 1. 原始运行材料：必须完整交回

保留仓库相对路径，运行根目录为 `experiments/python/openhands/<configuration>/<suite>/<task_id>/`。每个正式运行收集以下内容，存在的全部打包：

| 路径或类别 | 打包范围与用途 |
|---|---|
| `run.json` 及运行根目录的其他元数据文件 | 原运行身份、配置、结果、版本与时间记录。 |
| **`agent/` 整个目录** | **递归完整打包，不只挑几个 JSON 文件。**包含所有原始事件、audit、usage、stdout/stderr、命令与配置、任务提示，以及压缩器/辅助调用记录。 |
| `agent/openhands_persistence/` 整个目录 | 包含每个 conversation 的全部 `events/`、`base_state.json`、其他状态及持久化文件；即使 `openhands_events.jsonl` 存在，也不能省略此目录。其他名称的持久化目录同样包含。 |
| `eval/` 整个目录 | 原始最终评测结果及日志。 |
| `submission/` 整个目录 | 原始最终提交；保留相对路径和文件内容。 |
| `workspace/` 中的任务输入、生成代码和运行留下的文件 | 用于核对原始最终目录及回放差异。可以排除可重新获取的 donor checkout（例如 `repo/`）、虚拟环境、安装包缓存，但必须列出排除路径；不能排除 Agent 生成的代码、测试或状态文件。 |
| 运行目录之外的关联日志 | 如原 provider/proxy 请求响应日志、压缩器日志、额外 usage 文件或持久化记录，按 run_id 提供关联索引并一并打包。若共享日志含其他实验，只导出可可靠归属本次运行的记录，并注明筛选方法。 |

`agent/` 中尤其要检查：`openhands_events.jsonl`、`context_audit.jsonl`、`openhands_usage.json`、`usage.json`、`openhands_stdout.log`、`openhands_stderr.log`、`stdout.log`、`stderr.log`，以及全部持久化事件。文件名不同则保留实际原名并在索引中说明。**不要用重新生成的文件覆盖原始文件，不截断事件内容，不仅导出最后一段日志。**

若日志含 API key、Authorization header 等凭据，仅在交付副本中定点脱敏，原件不动；记录脱敏文件和字段。保留研究需要的时间戳、request/response/event/tool-call ID、usage、工具参数与观察内容，不得把这些用于对齐的字段当作凭据删除。

### 2. 现有 token 分析的原始中间材料：一并交回

- 正式 `run_manifest.csv`、900 行 `run_metrics.csv`、完整 `calls.jsonl.gz`、`artifact_timeline.jsonl.gz`、`snapshot_evaluations.csv`。
- 全部逐运行 `identity.json`、`replay.json`、`metrics.json`、`final_reeval.json`，以及已有的回放日志、状态清单和快照评测日志。
- 原始产物快照/CAS 及 hash 对应关系。如果它们与已交的 `token_efficiency_evidence_20260917T051402Z.tar.gz` 完全一致，可在 `BASE_MATERIALS.json` 中给出该包 SHA256 并声明复用；有变化则交增量文件及完整索引。**这个复用选项不适用于此前没有交过的 `agent/` 原始日志。**
- 实际分析代码、Git commit、未提交修改 patch、运行命令和固定评测/回放镜像的 digest。原始版和修复版分目录保存。

### 3. 恢复分析工作

日志作为数据读取，不在宿主机执行历史 terminal 命令。以下分析可以在原始材料打包之后继续：

1. 响应指标：以首次通过 checkpoint 的 observation event ID 定位边界，按 llm_response_id 去重。产生该产物的响应及其余工具动作不重复计数；仅计边界后首次出现的响应。检查事件完整性、顺序、并发；缺少边界就标缺失。独立记录 `include_response_analysis`，不要要求 token usage complete。
2. Qwen token 对齐：核对 audit 与响应 ID、数量差异、顺序、时间戳语义、重试和辅助调用。优先稳定 ID；若只能用顺序，需要证明一一对应且无漏记、插入或重试歧义。最近时间匹配只能作为候选，不能直接升级 exact。确认后重算累计 token，验证单调、终态和、PSF 补数恒等式。
3. Luna/GLM token：只查原运行中真实 provider usage 或持久化 usage。若仍为空，明确不可恢复；无需新跑实验代替原运行。
4. 复用有效快照评测。若发现遗漏可能修改产物的命令、回放不一致或环境错误，仅针对受影响运行在固定 Docker 环境补回放/复评，不全量重跑 Agent。

## 最终交付物与验收

### A. 原始材料包（必交，不以恢复成功为前提）

建议命名 `token_efficiency_raw_<UTC时间>.tar.gz`；体积大时按配置分成六个独立完整的 `.tar.gz`，并在顶层索引列出全部包。每个包保留原仓库相对路径，不合并同名日志。

同时交付：

- `run_index.csv`：恰好 900 个唯一 run_id，包含 configuration、task_id、原运行路径、正式 final_pass、原始材料可用状态。按配置各 150 行，正式成功数仍为 115/108/102/68/63/36。
- `raw_file_index.csv`：每个交付文件的 run_id、原路径、包名、包内路径、字节数、交付副本 SHA256、是否脱敏；共享文件通过关联索引链接 run_id。
- `missing_files.csv`：缺失的预期文件/目录、run_id、实际查找位置与原因。文件不存在不能创建空文件冒充已有记录；usage 原本为 null 也保留原状。
- `excluded_paths.csv`：主动排除的 donor checkout、环境/缓存路径及原因；没有排除也交表头。
- `SHA256SUMS`：每个压缩包的 SHA256。
- `RAW_README.md`：900 运行范围、目录结构、打包命令、脱敏规则、缺失情况与包完整性检查结果。

**完整性验收必须实际执行：**完整读取每个 gzip 流至末尾，完整列出 tar 成员，在临时目录安全解包后逐文件校验 `raw_file_index.csv` 中的字节数和 SHA256。检查 900 个 run_id 无重复、无混入，文件索引与实际包成员对应；不要只检查“压缩包已生成”或查看文件头。解包拒绝绝对路径、`..` 路径和越界链接，符号链接需记录目标且不能借链接带入范围外文件。交付时注明哪些检查通过、哪些未完成。

### B. 修复分析包（能够完成的部分交回，未完成明确标记）

- `response_effort.csv`：run_id、first_pass_event_id、first_pass_response_id、total_unique_responses、post_pass_unique_responses、include_response_analysis、exclusion_reason、source_sha256。
- `call_alignment.csv`：run_id、call_id、response_id、对应事件、匹配依据、exact/bounded/unresolved、歧义说明；不能仅交一个 exact 字符串。
- 若 token 恢复：修正后的逐调用账本、逐状态累计用量、run metrics；保留旧结果，给出修正前后纳入数量和实际变动原因。
- `verification.json`：两个 panel 各自分母、逐运行边界核对、累计用量单调、总量对账、缺失不会作为零、请求/响应/工具动作不混用。
- `RECOVERY_STATUS.md`：逐配置说明 token PSF 与后续响应两个指标分别恢复多少、还缺什么；未恢复的字段不估填。

**最低可接收交付是 A 的完整原始材料包与索引，不要求服务器先把 B 全部做完才能发回来。只交 B 的汇总、不交 A，不满足本次要求。**

收到这些材料后，可将 Fig.4 的右 panel 扩展为独立响应样本，左 panel 使用有可靠 token 时间线的配置；不保证两个 panel 六组都能补齐。正式改图时同步更改方法、caption、n 和正文，避免仍声称两个 panel 同样本。

本地核查代码与结果：`reports/paper_analysis/token_efficiency_recovery_20260917/check_recovery.py`、`recovery_checks.json`。这两个是核查材料，不是正式图输入。
