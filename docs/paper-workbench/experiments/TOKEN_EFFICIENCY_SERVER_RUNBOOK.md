# Token / Execution Efficiency：服务器离线分析操作文档

> 2026-09-16 · 待执行。供服务器 Agent 使用。
> 本轮交付分析证据，不直接新增 RQ、不改论文、不画正式图、不编译 LaTeX。
> 交付要求已按“拿回后可以写论文方法、结果并生成图表”复核。文件齐全与结论成立是两回事；按第 8 节提供可写范围，不以结果显著作为验收条件。

## 1. 要完成什么

对当前论文的 **150 tasks × 6 configurations = 900 次正式主实验**做离线回顾分析：

1. 同一配置内，成功与失败运行的 token / steps 分布如何？
2. 运行过程中，第一次产生完整通过评测的产物发生在什么时候？
3. 第一次通过以后，还花了多少 token、又改了多少次产物？
4. 最终失败的运行，是否曾经有一个通过的中间版本？

核心交付是每次运行的 **earliest sufficient artifact** 及其对应累计 token，而不是“最后一次写文件”或 Agent 自述完成时间。结果明显与否都照实交付，不以发现“浪费”作为成功标准。

只回放已有记录、离线评测快照。**不要重跑 Agent、调用付费模型、修改实验结果、补造用量、修复任务或重新定义通过标准。** 如数据不完整，交付覆盖率和明确的不可测原因；不要把未完成分析的运行记成从未成功。

## 2. 当前唯一正式范围

从仓库根目录运行。读取以下入口，禁止按某个目录名里的 python200 自动纳入 200 题：

- `docs/paper/paper_sources.json`：六配置、run_directory、正式输入路径。
- `docs/paper/writing/python150_membership.json`：150 个 task ID。
- `docs/paper/paper_inputs.py`：可复用 `paper_task_ids()`、`MODELS`、`run_directory()`。
- manifest 的 `main_results`：当前 900 个 model–task 最终结果。

正式顺序和成功数必须匹配：

| Configuration | 成功 / 150 |
|---|---:|
| DeepSeek V4 Pro | 115 |
| DeepSeek V4 Flash | 108 |
| GPT-5.6 Luna | 102 |
| GLM-5.3-Flash | 68 |
| Qwen3.6-35B-A3B-FP8 | 63 |
| GPT-OSS 120B | 36 |

共 492 成功、408 失败。不要混入 40-task ablation、历史 Main/V1/E50、其他 checkpoint 或重跑候选。每个 `(configuration, task_id)` 只对应原论文保留的那一次运行。服务器路径不同可以映射，但要记录原路径、映射路径与身份核验结果。

每次运行尽量收集：

- `run.json`、suite 身份、task/spec/source/evaluation capsule 的指纹。
- `agent/openhands_events.jsonl` 和 persistence events（用于相互核对或补足缺失内容）。
- `agent/context_audit.jsonl`、逐调用 provider usage、`agent/usage.json`、`agent/openhands_usage.json`。
- Agent 实际收到的 `workspace/TASK.md`、metadata、起始仓库与资源。
- 完整 `submission/`，不只 `submission/featurelifted/`。
- `eval/result.json`、日志、原评测容器身份和冻结题包。

2026-09-16 本地盘点：Pro/Flash 各 150 套轨迹、用量和最终评测文件；GLM 只有少量，其他配置的完整运行包需服务器提供。这是本地文件覆盖情况，不是对服务器数据缺失的判断。

**身份检查要看内容，不只看目录名。** 比较事件开头实际任务说明、run metadata、workspace task、最终评测 task ID 与选定任务是否对应。存在实质不一致时保留记录为 `identity_conflict`，不要自动搬用相邻目录的数据。忽略明确记录的通用提示包装差异，但不能忽略 API／行为契约或源版本差异。

## 3. 可复用代码与必须修正之处

可读、可复用：

- `harness/featureliftbench/token_utility_replay.py`
- `harness/scripts/analyze_token_utility_phase1.py`
- `harness/scripts/analyze_token_utility_phase0.py`
- `harness/scripts/analyze_token_utility_post_pass.py`
- `harness/tests/test_token_utility_replay.py`
- `docs/archive/snapshots/TOKEN_UTILITY.md`（历史方法背景，旧数字不进本轮结果）

建议新增独立入口 `harness/scripts/analyze_token_efficiency_current.py`，修复或封装公共模块，同时保留历史脚本可追溯性。下面是已检查到的问题，不能忽略：

| 现有实现 | 本轮要求 |
|---|---|
| 默认旧 `benchmark/python200_tasks` 和 `featureliftbench-eval:latest` | 使用本轮冻结 task/spec/capsule 和精确镜像 ID/digest；不要猜 `latest` |
| 默认只评第一／最后及几个 token 阈值快照 | 所有不同完整产物状态都评测，支持缓存；不能用抽样结果声称精确最早通过 |
| `last_action` 配对 observation | 用 tool_call_id/action ID 等稳定标识配对；批量工具调用不能错配 |
| `tokens_at` 用时间戳并宽限 +1 秒 | 优先 request/response ID 对齐，处理秒级精度、并发与重试；歧义给上下界 |
| `WorkspaceSandbox.run_terminal` 是宿主 `bash -lc`，只改写路径 | 在真正隔离的容器内回放；路径替换不是安全隔离 |
| 只 hash `submission/featurelifted`，忽略 symlink | 覆盖 evaluator 实际消费的完整提交、资源、配置、权限／链接等相关状态 |
| 按 hash 全局去重后只保留第一次 | 评测结果可去重，但完整事件时间线必须保留重复出现和回退，才能研究通过后退化 |
| 按 token 排序找 earliest pass | 按可确认的因果事件顺序找 earliest，token 只是该状态的累计开销 |
| 最终树匹配便自动复用旧评测 | 先复评最终提交，确认本轮环境与原结果一致；一致后才使用缓存 |
| work root 使用 `suite_dir.name` | 六配置可能有同名 suite，输出键必须包含 configuration + run ID，防止覆盖 |
| 存在 `result.json` 就视作缓存命中 | 校验输入 hash、题包、镜像、评测代码和状态；error 不能缓存成 fail |

重建最终文件一致只是必要条件：中间遗漏操作后来被覆盖，仍可能导致最终一致。对精确 T* 还必须能说明最早成功之前的所有产物改变均已捕获。

## 4. 指标定义：执行前锁定

设运行 r 的状态按已完成工具操作的因果顺序排列：`A(r,0), …, A(r,J)`。初始状态按原运行实际内容恢复，不默认为空；实际为空时也记录。相同内容再次出现保留时间线，但无需重复评测同一确定状态。

这里的 earliest 限定为**可恢复的工具操作完成边界**，不声称观察到了命令内部每次文件写入的瞬间。一个 shell 命令内部先创建再覆盖的临时版本不属于本指标的观测状态；异步任务须等到可确认的完成边界再记录。论文方法应保留这一粒度说明。

`P(r,j)=1` 表示该状态按当前冻结的完整 evaluator 获得 functional pass；包括 Build、Primary、Extended、Isolation 等正式要求。自测通过、模型声称完成、只有 Primary 通过，均不算。

- `j* = min {j : P(r,j)=1}`：最早通过的产物状态。
- `T* = C(r,j*)`：到达该状态时的累计 token。
- `Ttotal`：该次正式运行结束的累计 token，包含达到 j* 后的验证、修改、结束消息和相关模型调用。
- `First-Pass Fraction = T* / Ttotal`。
- `Post-Sufficiency Fraction = (Ttotal - T*) / Ttotal`。
- `Post-Sufficiency Tokens = Ttotal - T*`。
- `post_sufficiency_mutations`：首次通过后，完整产物状态实际改变的次数（包括回退到已有 hash，不包括无改变写入）。
- `post_sufficiency_failure_seen`：首次通过后是否出现被确认评测失败的状态。
- `ever_pass_final_fail`：曾通过、最终原结果失败；必须确认原最终提交复评仍失败。

存在多个异步修改、缺失事件或 token 对齐歧义时，不强行分配精确步骤／token。最后没有提交也可能曾产生过有效版本，不能只筛最终成功运行。

### 缺失、上下界与回退

- 完整重建且全部相关状态有效评测，始终不通过：`never_sufficient`，T* 和 PSF 为 null，**不是 0 或 1**。
- 尚有未恢复／未评测状态：`unresolved`；不能说从未成功。
- 找到一个通过状态，但更早有未知状态：只能给 `earliest_observed_pass`，它对真实首次通过位置提供上界；不混入精确 T* 中位数。
- 状态最早通过可确定，但累计 token 只有 `[L,U]`：token 指标用区间。若 Ttotal 精确，PSF 区间为 `[1-U/Ttotal, 1-L/Ttotal]`。
- Ttotal=0、未知或不一致：PSF 不可算，明确原因。
- 轨迹允许 fail→pass→fail→pass。禁止二分假定正确性单调。

本指标只判断“满足固定评测”，不是证明功能在任意输入上充分正确。通过后开销也不等于可安全省掉的浪费：Agent 当时并不知道私有 evaluator 的答案。

**持续通过的敏感性检查。** 对最终成功且全程可判定的运行，另算 `j_stable = min {j : 对所有 k≥j，P(r,k)=1}` 及 `stable_post_fraction=(Ttotal-C(r,j_stable))/Ttotal`。它不替代首次通过指标，只检验主结果是否主要由“早期短暂通过、随后破坏并修复”造成。复用已经评过的状态，无需新实验；后续有未知状态时不能认定持续通过。

## 5. Token 口径与逐调用账本

建立每次实际 LLM 请求的账本，去除**同一请求的重复日志**，但保留不同请求产生的重试成本。缺 usage 的请求不能填 0；真正无调用的事件不额外计 token。记录失败请求是否计量、压缩／辅助模型调用是否包含。

分别保存原始字段：prompt/input、completion/output、cache hit/read、cache miss/write、total、usage source 和 verified 状态。不要假设供应商的缓存字段都是可直接相加的。

建议输出两条账本，而不是把不同口径混在一起：

1. **Total token ledger**：有可靠逐调用记录时，按该 provider 定义统计 input+output（缓存是否包含明确记录）。
2. **Main-table accounting ledger**：Pro/Flash 为 uncached prompt + completion，其余为 total；用于同 Table 1 接续。

PSF、T*、Ttotal 必须使用同一条账本。跨模型并排展示时显式区分口径；token 不是 FLOPs，也不是可直接跨供应商比较的价格。

主分析优先使用含缓存输入的 **input+output total**，每个调用只计一次完整 input 与 output。只有能验证映射到此共同口径的配置，才进入同口径的六配置图表。无法恢复共同口径的配置保留本配置账本结果并单列，不能用 uncached PSF 顶替 total PSF；缓存随运行阶段变化，比例也不一定相同。若两条账本均可恢复，交回二者的 PSF 汇总敏感性对照。此选择不改变现有 Table 1。

一个响应发出多个工具调用时，该响应的全部用量在其首个工具完成前已发生，后续状态不得重复累加。以实际调用及工具因果顺序为准；有并行未完成请求、流式计量不全等情况时给区间，不按工具数量分摊 response token。

Luna / GLM 的 Table 1 汇总已由作者确认是实际总量，本轮不改表、不重新争论其名称。但它不能替代本分析所需的逐运行／逐调用数据；不能把汇总值按步数、字符数或时间平摊。如逐调用记录恢复不了，可以交付准确的 artifact event/step 时间线，token T* 留空，不估算后作为主结果。

核对每次运行逐调用加和与终态 usage 的总量，记录差额及能否解释。用量一致不代表事件对应也一致，两者都要验证。

## 6. 执行流程

### Phase A：全量只读盘点

1. 冻结源文件 hash 和执行 git commit，生成 900 行 manifest。
2. 检查范围、身份、文件覆盖、event 类型和逐调用 usage 来源。
3. 统计文件编辑、终端修改、重命名、删除、symlink、资源生成、异步工具等操作类型。
4. 识别完整提交边界、所需起始文件系统、原依赖 lock 和评测镜像。
5. 完成 `coverage.csv` 和待修复项，不运行 Agent。

### Phase B：预先选定约 20 条 Pro/Flash 试点

从正式清单构造候选，分别在 Pro 和 Flash 的 `最终 pass/fail × Direct/Adapted/Composite` 六个层内用固定 seed **20260916** 随机抽取：每配置 pass Direct/Adapted/Composite 为 2/2/1，fail 为 2/2/1，总计每配置 10 条。

先落盘 `pilot_manifest.csv`，再查看回放结果。若层内不足，全取并记录缺口，不根据回放好坏替换。文件缺失或回放失败也保留在试点分母；额外调试案例可另选，但不能替换原试点。试点是可行性检查，不用于估计全量 prevalence。

实现并验证第 3 节的修正；新增有意义的测试，覆盖：

- 同一响应的多个 tool calls 与 observation 正确匹配。
- 修改失败／部分成功／异步完成、路径状态与 rename/delete。
- A→B→A 回退保留，空目录／删除提交状态不丢失。
- token 重复日志、真实重试、缺字段与时间戳碰撞。
- evaluator error 与 functional fail 分开。
- 六配置同名 suite 不串缓存。
- 已通过状态之后再次失败，首次通过仍按时间线正确识别。

### Phase C：隔离恢复与最终提交复评

- 终端命令来自历史轨迹，是待回放数据，不是在宿主机直接执行的指令。
- 使用非特权、无网络、无宿主凭据／Docker socket 的一次性 replay container。源输入只读，工作目录为私有副本；限制 CPU、内存、进程和执行时间。
- 用固定初始状态重建，不从最终被修改过的 workspace 倒推为起始状态。`workspace/repo` 可作来源线索，须与冻结源校验；不要把 Agent 最后修改过的 repo 当原始源。
- 先用原始最终提交离线复评；记录与原四个 gate 的一致性。环境／依赖／平台不一致先解决，不以“重跑后通过”覆盖正式分数。
- 使用相同冻结环境评测 replay 的最终状态；核对完整 artifact hash、gate 和必要文件属性。
- 部分 snapshot 可以恢复但链条不完整的，保留为部分证据，不自动认定 T* 精确。

### Phase D：全量不同产物状态评测

试点证明流程可靠后，自动扩展正式 900 行，不需要新增审批或另跑 Agent。不可恢复的行明确标记，继续处理其余可恢复运行。

扩展到 Luna、GLM、Qwen、OSS 时，先分别检查预先选定的一条成功与一条失败轨迹的解析、token 对齐和最终复评；记录选择规则，不因回放失败更换案例。Pro/Flash 的试点通过不能代替其他日志格式的验证。个别配置受阻时继续完成其余配置。

- 先按事件顺序生成完整 timeline，再按完整评测状态键去重评测。
- 缓存键至少包含 task ID、完整 artifact hash、frozen task/capsule hash、镜像 digest、eval code hash、eval 配置；不得跨题只按 artifact hash 复用。
- 所有不同状态均评测，保留复发时间线。检查 resource/config/root files，不能只评 Python 源码。
- evaluator 的基础设施错误独立记录；最多两次同环境重试，仍失败保留 unresolved。禁止不断重试直到获得有利结果。
- 对精确结论有影响的疑似不稳定状态单独复核；同一状态通过性不稳定时单列，不能静默选一次通过。
- 不把私有测试、reference 或 evaluator 反馈传给新的 Agent。所有评测都是离线、与历史轨迹分离的。
- 支持断点续算，完成一个状态便持久化结果；禁止覆盖旧实验目录。

### Phase E：汇总与可视化草稿

先按 configuration 汇总，不先把六配置合成一个结论。至少给：

1. Pass/Fail 的每运行 token 与 steps：有效 n、median、Q1/Q3、P90，分开说明口径。
2. token–steps 散点，标记 outcome；只描述关联，不写“更多 token 导致失败”。
3. 最终成功且可精确测量运行的 T*/Ttotal、PSF 分布，给纳入 n / 全部成功 n。
4. 最终失败运行的 ever-pass 数量，分母为可完整判定的失败运行；给不可判定数量。
5. post-sufficiency 修改与通过性退化情况。
6. 按 lift type 的描述性分层（小样本标注 n，不解释成因果难度效应）。

统计分布的分位数按每运行指标先算再汇总。分别报告“各运行 PSF 的中位数”和“sum(post tokens)/sum(total tokens)”并正确命名，不能混用。若合并模型或比较模型，按 task cluster 处理同题相关性；探索性相关不承担因果结论。无需为了交付强行增加 p-value。

**主结果与分母固定如下：**

- 主指标：每配置“最终成功、身份与最终复评一致、完整状态链可判定、共同口径总量及 T* 精确且 total>0”的运行内，PSF 的中位数及 Q1/Q3。同时给 `included_success_n / official_success_n`、post token 中位数与 Q1/Q3；不把最终失败的曾通过运行混入。
- 次结果：Pass/Fail effort 使用各自有可靠运行总量的样本，不要求它们都能恢复 T*；ever-pass-final-fail 的分母只含完整可判定的最终失败运行。为三个分析分别给纳入标记与排除原因。
- 不把单配置内部 PSF 分布差异写成控制了 task composition 的模型排名；本轮不额外拟合新模型，也不要求六模型共同成功。
- 主 PSF 中位数另给 95% task-bootstrap percentile CI：在该配置符合主分析条件的 task ID 上有放回抽样，10,000 次，seed=20260916，每次重算中位数。若提供跨配置差值，须在有关任务 ID 并集上共同抽样、携带每题所有纳入行；记录无有效样本的 replicate，不能分别独立抽两个配置。CI 描述任务重采样的不确定性，不能修复缺失或证明因果。n<2 时 CI 留空。
- 分位数使用明确的线性插值规则（如 NumPy `method="linear"`），比例原始值保存为 0–1，表图显示百分比。按配置/outcome/lift type 比较纳入与未纳入的数量、可用 token 与 steps 分布，交回 `coverage_bias.csv`，检查可恢复样本是否明显偏向短轨迹。
- 持续通过指标与首次通过指标必须在同一可测样本上比较；账本敏感性也须使用同一批双账本可用运行，并给 n。没有符合样本时交空表及原因。

图只做独立草稿：PSF 的 ECDF／分布图，以及 token–steps 图即可。图内保留轴、图例和必要数字，方法解释写旁边说明文件。不修改论文图号、正式图片或 main.tex。

## 7. 服务器 Agent 要实现的可复现入口

建议提供统一脚本与以下子命令；**这是待实现接口，不是宣称仓库已经具备这些命令**：

```bash
# 位于仓库根目录；使用装有项目依赖的 Python。
PYTHONPATH=harness python3 -B harness/scripts/analyze_token_efficiency_current.py inventory --manifest docs/paper/paper_sources.json --output reports/paper_analysis/token_efficiency_current/inventory
PYTHONPATH=harness python3 -B harness/scripts/analyze_token_efficiency_current.py pilot --seed 20260916 --output reports/paper_analysis/token_efficiency_current/pilot
PYTHONPATH=harness python3 -B harness/scripts/analyze_token_efficiency_current.py run --scope paper150 --resume --output reports/paper_analysis/token_efficiency_current/full
PYTHONPATH=harness python3 -B harness/scripts/analyze_token_efficiency_current.py summarize --input reports/paper_analysis/token_efficiency_current/full
PYTHONPATH=harness python3 -B harness/scripts/analyze_token_efficiency_current.py package --input reports/paper_analysis/token_efficiency_current/full
```

可调整 CLI 设计，但 README 中必须写出**实际实现并运行成功**的命令，包含镜像选择、输入路径映射、输出路径、并行度及恢复方式。不要照抄旧 phase1 的默认目录和 `latest` 镜像直接开跑。建议初始 workers=2，根据服务器资源调整，不改变实验口径。

## 8. 必须交回哪些文件

交付两个压缩包，文件名带 UTC 时间戳：

### A. 主分析包 `token_efficiency_delivery_<UTC>.tar.gz`

这是我拿回来判断能否进入论文所需的主要包：

```text
README.md                         实际命令、完成范围、主要结论、限制、续跑方法
REPORT.md                         可读分析；成功/失败及各配置分别总结
manifest.json                     代码版本、输入/输出 SHA256、容器身份、冻结范围、方法版本
verification.json                 各项校验结果；不能只有 passed=true
coverage.csv                      每配置×outcome 的逐阶段覆盖和缺失原因
run_manifest.csv                  固定 900 行，包含未恢复/未评测行
pilot_manifest.csv                看回放结果前固定的 20 行及抽样规则
calls.jsonl.gz                    逐调用 token 账本，去除提示正文和凭据
artifact_timeline.jsonl.gz        每次状态事件、重复/回退、hash、因果序和累计用量
snapshot_evaluations.csv          不同状态的评测结果及身份、日志路径
run_metrics.csv                  固定 900 行最终分析指标和可用性标记
summary_by_configuration.csv      分组样本量及结果
summary_by_lift_type.csv           描述性结构分层
pass_fail_effort.csv               Pass/Fail 用量和 steps 分布
coverage_bias.csv                  纳入/未纳入的覆盖、类型和可用 effort 对照
sensitivity.csv                    同样本 first/stable、total/main-table 口径对照
unresolved.csv                    缺失、冲突、回放错误、评测错误和下一步；可为空但有表头
figures/                          独立 PNG/PDF 草稿及每张图使用的数据
paper_ready/                      下述方法、结果、表格片段和数值溯源（独立候选材料）
examples/                         少量正/负/回退案例的脱敏说明与定位信息
code/                             全部新增/修改源码、相关测试、依赖版本、相对路径说明
code.patch                        相对记录的基线 commit 的代码 diff（新增文件也包含在 code/）
```

#### 关键字段最低要求

`run_manifest.csv`：`run_id, configuration, task_id, suite_id, source_run_dir, final_pass, lift_type, identity_status, events_available, call_usage_available, final_eval_available, initial_state_available, final_artifact_available`。

`calls.jsonl.gz`：`run_id, call_id, request_id/response_id(有则保留), event_ids, started_at, ended_at, model, status, usage_source, usage_verified, input_tokens, output_tokens, total_tokens, cache_fields, accounting_basis, duplicate_of, inclusion_status, missing_reason`。同一请求多日志不能重复计数；不同模型的辅助调用要标注模型角色。

`artifact_timeline.jsonl.gz`：`run_id, state_index, event_id, tool_call_id, event_time, artifact_hash, causal_order_status, mutation_kind, reconstruction_status, token_alignment_status, accounting_basis, cumulative_tokens, cumulative_tokens_lower, cumulative_tokens_upper, eval_key`。起始／删除后空状态也保留。

`snapshot_evaluations.csv`：`run_id, task_id, artifact_hash, eval_key, image_digest, task_capsule_hash, eval_code_hash, eval_status, functional_pass, build_pass, public_pass, hidden_pass, isolation_pass, retry_count, result_path, log_path`。无效评测的 gate 为 null，不填 false。

`run_metrics.csv` 固定 900 行：

- 身份：`run_id, configuration, task_id, lift_type, final_pass`。
- 覆盖：`identity_status, replay_status, final_tree_matches, final_eval_matches, full_timeline_covered, unique_states, evaluated_states, unresolved_states`。
- 用量：`accounting_basis, token_usage_status, token_alignment_status, total_tokens, original_steps`。
- 充分性：`sufficiency_status`（`exact / bounded / never_sufficient / unresolved`）、`first_pass_state_index, first_pass_hash, first_pass_tokens, first_pass_tokens_lower, first_pass_tokens_upper, first_pass_fraction`。
- 后续开销：`post_sufficiency_tokens, post_sufficiency_fraction, post_sufficiency_fraction_lower, post_sufficiency_fraction_upper, post_sufficiency_mutations, post_sufficiency_failure_seen, ever_pass_final_fail`。
- 敏感性：`stable_first_pass_state_index, stable_first_pass_tokens, stable_post_fraction, stable_status`。
- 分析纳入：`include_psf_primary, include_effort, include_failure_history` 及每个分析各自的 `exclusion_reason`。
- `missing_reason, notes`。

`never_sufficient` 要求完整状态恢复与有效评测；`exact` 的 token 指标还需精确用量对齐。状态最早已知但 token 不明，可在 notes 和 alignment 字段区分，不能编数字。多个 accounting basis 的指标可另交 `run_metrics_by_accounting.csv`，键为 run_id+basis；主 `run_metrics.csv` 仍为 900 行。

`sufficiency_status` 只描述产物状态的可判定性，`token_alignment_status` 单独描述用量精度；例如状态 exact 但 token missing，必须 `include_psf_primary=false`，仍可支持产物历史分析。不得把“有完整 token 总量”自动等同于“有精确 T*”。

#### 可直接用于写作的候选材料（必须交付）

`paper_ready/` 至少包含：

1. `methods.md`：简短英文方法段落，写明样本、工具完成边界、完整 evaluator、token 口径、PSF 定义和 CI。仅描述实际完成的方法；细节放 README，不写成论文里的操作日志。
2. `results.md`：有真实数字支持的英文结果段落，区分观测与解释；没有足够数据的结论明确留空。末尾一句说明离线首次通过不等于 Agent 已知可以安全停止。
3. `efficiency_table.csv` 与 `efficiency_table.tex`：六行配置，列为 **Configuration / Included successes n/N / Median post-sufficiency tokens [IQR] / Median PSF [95% CI]**，统一 total 口径；不可用填 `--`，不要静默删配置。Q1/Q3、T*/Ttotal、分母和所有未显示的汇总值仍放完整数据文件。LaTeX 用 booktabs，caption 在上，独立片段，不固定 Table 编号、不并入 main.tex、不编译。
4. `figure_recipe.md`：说明 ECDF 草稿的样本、x=PSF、y=累积比例、六配置顺序和最短 caption；另附可以从交付数据重画的脚本、逐点源数据及 PNG/PDF。token–steps 图作为探索证据，不要求也进入论文。
5. `claim_evidence.csv`：`claim_id, text, configuration, accounting_basis, numerator, denominator, estimate, lower, upper, source_file, filter, metric`。论文候选文字、表格每个关键数字能追到行级数据，不只引用 REPORT.md 的转述。该文件供作者核对，无需写进论文。
6. `readiness.json`：按配置列出 `effort_ready, artifact_history_ready, psf_ready`、纳入 n/N、阻塞原因和支持的写作范围。这里 ready 表示来源与口径可验证，不表示统计显著；覆盖有限时必须限于可恢复子集，不自行宣布六配置或全部成功运行的结论。

能交付上述材料，就可以开始相应范围的论文写作，不必再回服务器补取普通汇总。**不预设 RQ5 一定成立**：若只有 effort 可用，就交付 effort 结果；若部分配置有精确 PSF，就写清这一分析范围；若全部配置证据足够，则支持完整候选 RQ。不要用“文件都生成了”代替这个判断，也不设置看完结果再调整的显著性门槛。

### B. 可复核证据包 `token_efficiency_evidence_<UTC>.tar.gz`

按 `configuration/run_id/` 组织：

- 已物化的不同完整提交状态，或等价的无损内容寻址归档。
- 状态 hash 到事件的映射、重建操作记录与错误。
- 每次离线 evaluator 的 result/log、固定配置和来源 hash。
- 必要的最终提交复评证据、首次通过状态证据、回退案例证据。

不要再次打包所有 donor 仓库造成大量重复；保留它们的冻结标识和重建位置。如果证据过大，按配置拆包并交 SHA256 清单，不能只给主包而不说明证据位置。

复核不能只依赖服务器绝对路径。随包保留正式 membership、选中结果、方法配置、必要输入摘录和环境 lock；在本地仓库中没有的冻结题包／资源须放证据包或提供可取回的对应归档。镜像记录 digest 和构建材料；私有且无法拉取的镜像提供独立归档及校验值。不要求重复携带本地已有的 donor 仓库。

打包前在新目录解包，仅用交付的行级文件和代码重建汇总表、候选 LaTeX 表、图和数值溯源，**该检查不依赖服务器原绝对路径、Docker 或模型 API**。另提供离线 evaluator 的复评命令和依赖清单；它与轻量汇总复现分开。两种检查在 verification.json 中分别记录实际成功/未执行及原因，不能互相替代。

两个包都不包含 `.env`、API key、认证头或主机凭据。私有测试日志／实现如需交回，只放证据包并标记 private，不能放公开示例或主报告。无需 git push；只交付代码和结果。

## 9. 最终验收清单

- [ ] run_manifest 和 run_metrics 都是 900 行、无重复键，恰好覆盖指定 150×6。
- [ ] 原始最终成功数仍为 115/108/102/68/63/36；没有改原实验。
- [ ] 每个配置的 assigned / usable / exact / bounded / unresolved 等覆盖计数可由行级文件复算；不同覆盖维度不混为互斥组。
- [ ] exact T* 前没有未知状态；first pass 使用完整 functional gate，未把自测当金标。
- [ ] 支持 fail→pass→fail 和相同 hash 再出现；空提交状态不消失。
- [ ] 最终文件一致、最终 gate 复评一致、原环境身份可核对；错误与失败分开。
- [ ] 所有 token 指标满足同一 accounting basis，逐调用汇总可复算；缺失不是零。
- [ ] 已定义且 total>0 的 token fraction 在 [0,1]，post=Ttotal−T*。
- [ ] 未恢复的运行没有被填成 never_sufficient；最终失败的 T* 不被强行置空（可能曾通过）。
- [ ] 图表 n 与纳入运行对应；不把每个 snapshot 当独立样本扩充样本量。
- [ ] 三个分析的纳入标记、主 PSF 口径、CI 方法、覆盖偏差和同样本敏感性对照全部落盘。
- [ ] paper_ready 内含真实方法/结果、六配置候选 LaTeX 表、图源数据和 claim_evidence；没有编造不可用结果。
- [ ] 新目录中不依赖服务器原路径即可重建表图与汇总；私有评测所需证据和环境可定位、可取回。
- [ ] 旧 Main/V1/E50 数字没有混入本轮；抽样 earliest 没有冒充精确 earliest。
- [ ] 代码支持断点恢复，缓存验证包含配置/任务/状态/环境；没有同名 suite 覆盖。
- [ ] 文档最后明确写出：本轮是否足以回答候选 RQ5，哪些配置可用、哪些结论仍不可支持。
- [ ] 不修改论文、题包、原始标签、现有图表或主结果；不编译 LaTeX，不启动新模型实验。

## 10. 可直接发给服务器 Agent 的任务

> 请执行 `docs/paper/experiments/TOKEN_EFFICIENCY_SERVER_RUNBOOK.md`。先读该文档和当前 `paper_sources.json`，以固定 Python-150 主比较的 900 次运行作为唯一范围。复用但修正旧 token utility 回放实现，先盘点，再固定 Pro/Flash 20 条试点；试点验证方法后继续扩展全量。只回放已有轨迹并离线评测不同中间提交，不重新调用 Agent、不改原始记录、不修改论文。准确区分精确 T*、有界／不可测结果和从未通过，保留每一步的证据与 token 口径。交回文档第 8 节规定的主分析包与私有证据包、可复现代码及 verification.json。若某些数据无法恢复，完成其余部分并明确交付覆盖和缺失原因，不伪造数字，不因结果不支持低效率就隐去结果。
