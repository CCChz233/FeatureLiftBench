# 当前执行：Source Exposure 离线诊断（Entrypoint Hint 暂缓）

**最终执行决策，2026-09-13：只执行 S，离线分析现有 900 条轨迹，不新增模型调用。A（120-run Hint）暂缓；下文 A 节仅保留备选协议，不是当前执行任务。**

本文 benchmark 为固定 150 题，六配置主比较 900 条结果。已完成的源码消融为同一 40 题 × Luna / Pro / Qwen × 两臂，共 240 条保留结果。本轮不改题、不扩展到 200、不增加模型或机械 baseline，不自动给失败标注因果根因。

| 顺序 | 工作 | 新 agent runs | 交付物 | 论文位置 |
|---|---|---:|---|---|
| S | 900-run trajectory-based source exposure diagnosis | 0 | 逐事件证据、逐运行表、结果分组表、子集分析 | §3 方法、§4 结果；更细子集放附录 |
| 暂缓 | 40 题 × 3 配置 Full Source + Entrypoint Hint | 当前 0（备选 120） | 暂不执行 | 当前 Fig.5 保持实测两臂 |

**先阅读本指南，不再按旧 `SUPPLEMENTARY_EXPERIMENT_RUNBOOK.md` 的模型数、200 题范围或 mechanical baseline 计划执行。** 那是前一轮设计历史，服务器实际完成的两臂运行记录才是本次控制配置的依据。

## 0. 开始前：固定输入并核实分母

项目根目录运行（不调用模型、不执行 evaluator）：

```bash
python3 -B scripts/paper.py check
python3 -B docs/paper/experiments/prepare_process_diagnosis.py \
  --output reports/paper_analysis/source_exposure/preflight
```

第二个脚本生成：

- `preflight.json`：集合、标注规模、事件文件可用性、输入 hash。
- `run_index.csv`：900 个 model–task cells、原始结果和事件文件路径。
- `targets.private.json`：离线分析用的入口声明、参考文件列表和 closure 标注路径；**不能挂载给 agent**。

本地已检查的输入规模：

| 项目 | 当前值 | 含义 |
|---|---:|---|
| 150 题中有非空入口声明 | 150 | 不等于所有符号已正确解析 |
| 900 个运行对应非空事件文件 | 900 | 不等于轨迹完整、内容可解析 |
| `oracle_manifest.json` 中存在 `required_source_files` 字段 | 116 | 包含空列表 |
| `required_source_files` 非空 | **107** | 当前子集分母候选，不能沿用未核实的 124 |
| 存在 `evaluation/closure_gold.json` | 39 | 内容范围仍需逐题核对 |
| 40 题消融样本 | 40 / 38 仓库 | 原样复用，不重新抽题 |

如果服务器得到不同数量，先检查路径、空列表和记录对应关系，保存差异，不覆盖分母、不改原题迎合预期。`closure_gold` 中有文件级参考闭包和 unresolved symbol/runtime 的范围说明；文件名带 gold 不意味着已证明完整语义闭包。

固定输入：

- `docs/paper/writing/python150_membership.json`：150 题清单。
- `docs/paper/paper_sources.json`：六配置结果及原运行目录。
- `docs/paper/experiments/source_ablation_40.txt`：同一 40 题，SHA256 `11d9bd32cf06db4d5ccba7b83dd140294353094b9061cd21fec4263445a972b9`。
- `reports/paper_analysis/source_ablation_40_20260913/task_outcomes.csv`、`paired_outcomes.csv`：既有两臂实测结果。
- `experiments/source-ablation-40-r1-full.tar.gz`：既有服务器运行记录。

150 题清单的当前固定状态不能单独证明它早于额外 50 题结果。论文当前只说明使用同一固定集合；若要增加“在看到额外结果前预先固定”，需要有当时的清单/提交/运行时间证据。不要仅凭这次生成的 hash 作时间顺序证明。

## S. 离线轨迹诊断

**已完成第一轮文件内容暴露诊断。** 当前实现、数据和论文以以下命令为准（不调用模型，不执行任务）：

```bash
python3 -B docs/paper/experiments/prepare_process_diagnosis.py
python3 -B docs/paper/experiments/test_source_exposure.py
python3 -B docs/paper/experiments/diagnose_source_exposure.py
python3 -B docs/paper/experiments/summarize_source_exposure.py
python3 -B docs/paper/experiments/validate_source_exposure.py
python3 -B scripts/paper.py tables
python3 -B scripts/paper.py check
```

结果位于 `reports/paper_analysis/source_exposure/diagnosis/`，说明见 `REPORT.md`。主指标为显式读取后的文件内容匹配；含搜索片段作为敏感性。未实现 symbol-body exposure，不能把本文数字称为入口函数体读取率。下文是设计原则，其中精细符号范围和未覆盖工具形式不是已完成的测量。

### S1. 先建立入口与源码文件的对应关系

在每题固定源码快照中解析入口声明，保存 `task_id, declared_symbol, resolved_file, symbol_start, symbol_end, resolution_status, evidence`。规范化 `src/`、package root、re-export、别名及运行工作目录。

- 入口可能有多个；分别记录“至少一个入口文件”“所有已解析入口文件”的暴露情况。
- 区分符号门面/re-export 文件与实际实现文件；不要把读过 `__init__.py` 自动等同于到达完整实现。
- 不能解析的入口标 `unresolved`，人工检查后再固定映射；不改 benchmark 原始定义，也不能把 unresolved 当 agent 未定位。
- `harness/scripts/audit_source_entrypoints.py` 可借用静态解析逻辑，但其历史报告包含旧样本/旧分析，不能直接作为本实验输出。存在性检查也不等于语义相关性检查。

### S2. 统计“可观察到的内容暴露”，而不是指令里出现过路径

**不使用 `harness/featureliftbench/trajectory_audit.py` 的旧 source-read 汇总作为本实验结果。** 它没有逐条验证实际返回内容。本轮独立实现为 `diagnose_source_exposure.py`，通过 action/observation 配对、明确源码挂载路径和连续内容匹配确认暴露；不会把旧 `unique_source_files_read` 直接改名为 inspected。

| 字段 | 可接受证据 | 不接受的替代证据 |
|---|---|---|
| `entrypoint_search_attempt` | 对目标路径/符号的检索动作，保留原命令 | 泛泛搜索整个 repo 就算找过每个文件 |
| `entrypoint_search_hit` | 搜索工具结果实际返回该文件/符号 | 只有搜索请求、无命中结果 |
| `entrypoint_file_exposed` | 成功工具 observation 展示目标文件的非空源码；保留事件索引、路径、行范围、片段 hash | 仅 `ls/find` 文件名、失败的 `cat`、代码复制、导入执行、测试 traceback 路径 |
| `entrypoint_symbol_exposed` | 返回内容与解析出的入口定义/函数体范围相交，作为更严格的补充指标 | 只读同文件完全不相关的片段 |
| `first_file_exposure_step` | 首次符合上述规则的动作在原始 assistant/tool 序列中的位置 | 日志行号、总 event 序号和 configured action counter 混用 |

检索结果若展示实际代码片段，可单列 `search_snippet_exposed`；主分析的显式文件读取与“含搜索片段”的敏感性分开。shell `cd`、相对路径、命令链、文件编辑器 view、stdout 截断均需处理；无法确定路径或内容就标 unknown，不猜测。用户消息、prompt、模型推理中提到路径也不能算读取。

以 action/observation ID 配对，避免 condensed 历史、重复输出或持久化 events 与 JSONL 被重复计数。检索、读取是不同字段。记录全部可观察缺失：`complete / incomplete / unparsable / missing`，以及未知动作数。900 个非空文件不能保证 900 条可判定轨迹。

### S3. 输出与分母

输出目录：`reports/paper_analysis/source_exposure/`。

1. `entrypoint_mapping.csv`：入口到源码位置映射与未解决项。
2. `exposure_events.csv`：model、task、action/observation ID、step、path、line range、证据类型和片段 hash；片段可单独保存。
3. `run_exposure.csv`：全部 900 行。至少包含 trace status、结果、任一/全部入口文件暴露、symbol 暴露、首次命中步、可观察动作数、required-file coverage、closure 子集及范围状态。
4. `summary_by_model_outcome.csv`：逐配置分组结果；`summary_pooled.csv` 为便于阅读的汇总。
5. `subset_results.csv`：非空 required-source-file 子集与 closure 标注子集的分母、覆盖率。
6. `parser_validation.md`、`analysis.md`、输入/脚本 hash 清单。

正文小表可用：

| Outcome | All runs | Trace-assessable | Entrypoint file exposed n/N (%) | Median first-hit step |
|---|---:|---:|---:|---:|
| Pass | 492 | 实测 | 实测 | 实测 |
| Primary/Extended-first failure | 303 | 实测 | 实测 | 实测 |
| Delivery/Build failure | 101 | 实测 | 实测 | 实测 |
| Isolation-first failure | 4 | 实测 | 实测 | 实测 |

不要丢掉 4 个 Isolation-first failure。保留独立结果，或在正文表注明它们另报附录。门控按现有固定顺序归类。缺轨迹的运行仍进入总数，但不能作为“未读取”；暴露比例同时交代可判定分母与 unknown 数量。first-hit 中位数仅在已确认暴露的运行上计算，未命中不填 0 或总步数；同时报告命中数。按模型分层，避免将不同配置的运行长度/能力混成一个解释。

支持文件 coverage = 已暴露的已列明文件 / 非空列表中可解析的不同文件。保存原始列表大小和 unresolved 文件数；不能靠忽略未解析文件提高覆盖率。它是 **annotated-file coverage**，不是完整 closure recall。closure 的 39 题按实际 annotation scope 单独汇报；尤其不要由文件暴露推出状态、符号和全部行为闭包已经恢复。

### S4. 验收，不做自动根因归类

- 先用人工可核对的小样本验证解析器：至少 24 个运行，覆盖六配置、成功/行为失败/交付失败及 shell/editor 两类访问。抽取规则先固定；保留 parser 错例并修复后重算全部，不把修错当新实验。
- 测试至少包含：成功文件 view、失败 read、纯路径命中、代码片段搜索、相对路径、重导出、截断输出、重复事件、不完整日志。直接核对工具返回的内容。
- 不根据预期结论调整“inspected”阈值；不做 API/state/dependency 的自动 causal taxonomy。
- 如需区间，按 repository/task 对重复配置运行做成组重采样，不能把 900 行当独立任务。

可以写：**behavioral failures remain among runs with observed entrypoint-file exposure**。不能写：看过入口就等于完成 localization、理解源码、恢复闭包，或者据此证明 reasoning failure。没有暴露记录也不证明没找到代码：可能通过其他实现位置或未覆盖的工具路径获取证据。

## A. 备选协议：Entrypoint-Hint 消融（暂缓，不执行）

### A1. 固定比较与预算

GPT-5.6 Luna、DeepSeek V4 Pro、Qwen3.6-35B-A3B-FP8 各 40 题。只新增 `Full Source + Entrypoint Hint`；主对照是已完成的同模型同题 Full Source，Contract Only 保留作背景。

| 配置 | 已有 Full | 已有 Contract Only | 新 Hint |
|---|---:|---:|---:|
| Luna | 40 | 40 | 40 |
| Pro | 40 | 40 | 40 |
| Qwen | 40 | 40 | 40 |

新 Hint 与 Full 的对比不直接依赖 Pro Contract-only 的 18 次 timeout，但新增组是稍后运行的，仍可能存在服务时间变化。保留 provider/model 的实际标识、运行时间、错误、重试策略；不能仅因参数名相同就宣称排除了所有时间混杂。模型端点已经变更且无法复用时先记录，不能悄悄换成其他配置。

**复用服务器前一轮 Full 的实际配置，不从旧指南推断预算：** 240 条持久化记录均为 OpenHands maximum iterations 500；Pro 另有 harness step limit 120，Luna/Qwen 未设置该 override。逐题 timeout 3600、context 131072、reserved 8192；Pro 的 condenser 与 Luna/Qwen 不同。按各配置匹配已有 Full，不要为了“统一”把全部新 Hint 改成 120 steps。

### A2. Hint 内容仅为入口符号与文件路径

从 S1 的固定映射为同一 40 题生成 **单独的 allowlist 文件** `entrypoint_hints.json`，只含 task ID 与入口 `symbol`、仓库相对 `file`。人工核对映射与目标能力直接相关；不因模型表现替换入口。

示例格式（仅结构示例，不能当真实入口）：

```json
{"task_id": "<real task ID>", "entrypoints": [{"symbol": "package.module.function", "file": "src/package/module.py"}]}
```

追加到已有 Full prompt 的固定块：

```text
## Source entrypoint hints
The following locations may help you start inspecting the implementation:
- <symbol> — repo/<relative-file-path>
These are starting points, not a complete dependency closure.
```

不提供源码片段、依赖图、required_source_files、closure_gold、reference、benchmark tests 或必要文件集合；不附额外解题步骤；不修改公开行为契约或 evaluator。所有任务仍可 inspect 完整仓库。entrypoint hint 只降低初始定位成本，不等于消除了全部 localization。

### A3. 代码接入与正式执行

当前 CLI 已有 `--agent-source-hints`、`--source-context full_repository`，但其默认来源是已有 metadata 符号，prompt 分支也可能修改定位说明，**不能直接假设打开开关就符合上述仅追加 symbol+path 的实验**。

服务器侧先在上一轮 Full runner 上完成最小接入：使用 allowlist 追加固定块，保留原始 Full prompt 其他内容。若复用现有开关，必须补充路径、记录变动，并验证没有额外导出 metadata。`required_source_files`/closure 仅供离线分析，不能给到 agent。不要改变原题 metadata 以实现提示。

从旧 Full 命令复制 agent config/profile、Docker image、provider/env、预算、并发、错误恢复策略；输出改为新目录。下面是 **接口模板，不是已核对过服务器 profile 的一键命令**：

```bash
mapfile -t TASK_IDS < docs/paper/experiments/source_ablation_40.txt
TASK_ARGS=()
for task_id in "${TASK_IDS[@]}"; do TASK_ARGS+=(--task-id "$task_id"); done

# 必须先在服务器设为前一轮 Full 使用的实际配置与镜像。
: "${FULL_AGENT_CONFIG:?}" "${FULL_PROFILE:?}" "${FULL_ENV_FILE:?}"
: "${FULL_AGENT_IMAGE:?}" "${FULL_EVAL_IMAGE:?}" "${MODEL_SLUG:?}"

# 仅在 symbol+file 注入和 prompt/workspace 检查完成后运行；
# 还需继承原 Full runner 的 provider、并发与恢复选项。
PYTHONPATH=harness python3 -B -m featureliftbench.cli run-agent benchmark/tasks \
  --agent openhands --agent-config "$FULL_AGENT_CONFIG" \
  --agent-profile "$FULL_PROFILE" --env-file "$FULL_ENV_FILE" \
  --source-context full_repository --agent-source-hints --no-agent-public-tests \
  --agent-docker --agent-docker-image "$FULL_AGENT_IMAGE" \
  --eval-docker --eval-docker-image "$FULL_EVAL_IMAGE" \
  --timeout-seconds 3600 --extra-agent-passes 0 \
  --output "experiments/source-entrypoint-hint-40-r1/$MODEL_SLUG" \
  "${TASK_ARGS[@]}"
```

若上一轮使用自定义 Python driver，优先修改它，而不是切换到不同默认行为的 CLI。不要直接 `--resume` 重跑所有 failed：默认 resume 可能重试失败任务。按已有 recovery policy 恢复未完成/指定基础设施错误，保留所有旧 attempt；最终保留规则预先固定，不选 best-of-N。

正式 120 runs 前完成不调用模型的 40 题 prompt/workspace dry check：去掉固定 Hint 块后与 Full contract/prompt 对齐；agent 只多看到 entrypoint allowlist；两组源快照、evaluator capsule、依赖和参数保持对应一致。确需端到端 smoke 时用 `source_ablation_smoke_3.txt` 中非正式样本，单独记录，不混入 120。

### A4. 分析与解释

逐模型做 Hint vs Full 的同题配对：Pass rate、Hint-only / Full-only、配对差值（百分点）、95% paired bootstrap CI、exact McNemar；三个主比较做 Holm 校正。给 missing / Build / Primary / Extended / Isolation 的首败变化，以及提示后实际入口暴露率（复用 S 的规则）作为 manipulation check。

- 小增益或不显著：只能说 **under this hint intervention, observed improvement is limited/uncertain**；不能直接证明 localization 不是瓶颈。要看置信区间、Hint 是否正确、agent 是否真的读取以及是否有 ceiling effect。
- 大增益：支持提供入口指引有帮助，不等于精确测得“全部定位成本”；提示还可能改变注意力或解题顺序。
- 模型间差别：先报告每个配置的效果与不确定性。“一个显著、另一个不显著”不等于两个效果显著不同。
- 无论方向如何都完整报告 40 题；不删掉反向配对、超时或未交付。错误敏感性放附录，不取代主分母。

输出 `hint_outcomes.csv`、`hint_vs_full_pairs.csv`、`hint_statistics.json`、`prompt_diff_audit.json`、`runtime_comparison.json` 和全部运行原始记录。三组共 360 条保留结果，但本轮仅新增 120。

## 论文落点与停止条件

当前叙事已调整：保留真实 author review；Source Ablation 升为 RQ3，task variation 降为描述性分析；摘要分开定量 behavioral boundary 与定性 contract-closure；§5 定位 illustrative mechanisms；论文不讨论额外 50 题池。

S 已完成：方法放 §3，**Trace-Based Diagnosis of Source Exposure** 结果放 §4，紧接 RQ3 的 Source Ablation。正文一张 outcome × exposure 表；支持文件子集和方法限制放附录，逐模型完整汇总保存在报告中。摘要、引言、结论均报告 241/303（79.5%）；Threats 明确文件内容暴露不等于入口函数体读取、完整 localization/understanding/closure。

A 暂缓，当前 Fig.5 保持已完成的两臂实测结果，不添加第三臂或预测数字。

最终交付压缩包只含本轮离线报告、代码、证据索引和 checksum；不要包含 `.env`、API keys 或凭据。当前只完成 S，不启动 A，不追加模型、200 题、机械 baseline、全量 repeats 或自动根因分类。
