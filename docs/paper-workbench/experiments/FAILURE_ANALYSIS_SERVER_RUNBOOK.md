# 服务器操作文档：Failure analysis、Pro 消融恢复与 Token 补全

版本：2026-09-15，已加入 Pro Contract-Only 恢复及 Luna / GLM token 补全。**不编译 LaTeX，不覆盖历史实验结果。**

本轮服务器共处理三项工作，范围互相独立：

| 工作 | 输入范围 | 最终交付 |
| --- | --- | --- |
| A. 系统 failure analysis | 主结果中的 241 条候选，六配置 | Fig. 8 + Table 7、标注、证据与人工复核包；见 §1–9 |
| B. Pro 消融服务中断恢复 | 固定 40-task ablation 中 Pro / Contract-Only 的 18 条 timeout + no-submission | 18 题恢复运行、新版 40 题保留清单、配对统计与消融图表更新；见 §10 |
| C. Luna / GLM token 补全 | 两模型各自论文主榜的 150 条保留运行，共 300 条 | 先恢复实测 usage；无法恢复则尽可能给出有依据且明确标注的估算，补 Table 1 token 单元格；见 §11 |

**仅 B 允许调用模型重跑上述 18 题；A、C 均为已有材料的离线分析。** 不新增 Hint arm、不重跑全部 40 题、不改另外 22 条或 Full Source，也不为补 token 重跑主榜。优先启动 B；等待其运行时可以推进 C 与 A。第 13 节为统一服务器 agent 指令。

## 1. A：Failure analysis 最终需要交付什么

需要的是「逐案证据 → 有效性判断 → 语义标注 → 汇总 → 图表与文字」，不能只交一张由报错字符串统计出来的图。

服务器 agent 本轮应完成：

1. 六个 configuration 的 **241 条候选运行全量审查**，每条有原始文件定位、公开契约编号、有效性判断和一条可核查的标注记录。
2. **Fig. 8**：六配置的输出侧失败类别分布，独立 Python 源码及 PDF / PNG，附精确绘图数据。
3. **Table 7**：类别的操作定义、全体有效样本的精确计数与分母，并明确候选、排除、有效和 unknown 数量；交可直接引用的 `.tex`。
4. 适合接入 RQ2 的英文方法、结果、限制和 caption 草稿；所有数值从汇总结果生成或核对。
5. 完整标注表、私有逐案证据包、复核队列、输入哈希、检查报告、重生成说明。
6. 两个完整可解压的交付包：**论文候选材料包**和**私有证据包**，以及 SHA-256 校验文件。

本轮 agent 可以独立交付到 **L1 精读完成 / 待独立人工复核**。这已经是完整的自动化阶段交付。不要等待人工才生成草稿，也不要把待复核草稿标成正式金标。

**正式主文根因比例的后续要求：**现有 [SOP §3、§4.7](../../FAILURE_ANALYSIS_SOP.md) 规定「L2 金标：独立人工双审……才可以把根因比例写进主文」。具体抽样和盲审见第 7 节。两次 AI 检查不算两位独立人工 reviewer；未完成时，状态必须如实保留。

## 2. 研究问题与分析边界

本证据组回答：

> Among behavioral failures with observed entrypoint source reading, what observable artifact and contract gaps remain?

它与现有 RQ2 的关系是：首败分解回答「在哪一关失败」，source-exposure 表回答「是否观察到入口源码读取」，新增分析进一步回答「这些失败产物具体有哪些可观察缺口」。

本轮固定六配置顺序：**Pro / Flash / Luna / GLM / Qwen / OSS**。完整模型 ID、显示名称和 suite 路径取 `docs/paper/paper_sources.json`，不要自己猜模型版本。

候选集合严格定义为：

```python
# 仅在冻结的 Python-150 × 六配置、900 条主结果中进行一对一连接。
candidate = (
    first_failure_stage in {"public_failure", "hidden_failure"}
    and entrypoint_explicit_read == "1"
)
```

| 配置 | 候选运行数 |
| --- | ---: |
| Pro | 29 |
| Flash | 34 |
| Luna | 33 |
| GLM | 36 |
| Qwen | 43 |
| OSS | 66 |
| 合计 | **241** |

当前候选覆盖 **89 个不同 task**。这些数字是输入身份核对值，**不是审查后的有效 Agent 失败分母**。

不要把 `entrypoint_content_exposed` 替代 `entrypoint_explicit_read`；不要扩大到 suite 目录名中的全部 200 题；不要加入 ablation、其他轮次或成功运行。源码读取不代表正确定位、理解或因果上的「读过但不会用」。本分析是对特定失败子集的描述，不能外推为所有失败的根因比例，也不能只因该子集出现缺口就宣称源码无帮助。

## 3. 输入定位与冻结核对

从服务器项目根目录执行。下文路径均相对项目根目录，不依赖本机 `/Users/chz/...`。

必须先阅读：

- `.agents/skills/featureliftbench-annotate-failures/SKILL.md`
- `docs/FAILURE_ANALYSIS_PROTOCOL.md`
- `docs/FAILURE_ANALYSIS_SOP.md`
- `docs/paper/paper_sources.json` 与 `docs/paper/paper_inputs.py`

本轮用户已指定六配置全量候选审查，因此不沿用 skill 的默认「先最强 1–2 个模型」最终范围。可以分批处理，最终要覆盖上述 241 行。旧章节文件 `docs/paper/08_experimental_analysis_chapter.md` 在当前本地版本中缺失；若服务器也没有，不要编造其内容，使用现存 Protocol / SOP 的明确规则。

核心输入：

| 输入 | 用途 |
| --- | --- |
| `docs/paper/writing/python150_membership.json` | 150 题成员身份 |
| `docs/paper/paper_sources.json` 引用的 release manifest | 冻结身份；以 manifest 实际指向为准 |
| `reports/paper_analysis/python150_prime_v2_analysis_20260905/task_results.csv` | 900 条逐任务功能结果和首败阶段 |
| `reports/paper_analysis/source_exposure/preflight/run_index.csv` | 原始 run / events 路径 |
| `reports/paper_analysis/source_exposure/diagnosis/run_exposure.csv` | 入口源码读取标记 |
| 同目录的 `entrypoint_mapping.csv`、`exposure_events.csv`、`method.json` 等 | exposure 定义、入口映射和事件依据；按实际文件清单定位 |
| `benchmark/tasks/<task_id>/` | 冻结的公开契约、测试与参考实现 |

每条候选至少检查：

```text
<retained_run>/run.json
<retained_run>/eval/result.json
<retained_run>/eval/logs/public.stdout、public.stderr 或 hidden.stdout、hidden.stderr
<retained_run>/submission/                 # 整个交付包，包括非 Python 资源
run_index 指向的 events 文件
benchmark/tasks/<task_id>/TASK.md
benchmark/tasks/<task_id>/metadata.json
benchmark/tasks/<task_id>/evaluation/behavior_contract.json
该 task 对应的 public_tests/、hidden_tests/ 和必要的上游/参考证据
```

核对 suite、task、模型、运行轮次、source snapshot、可获取的镜像 digest 与 frozen identity。镜像等字段缺失时记录缺失，不凭模型名称推断一致。

### 3.1 先跑材料盘点

本地已有只读检查脚本：

```text
reports/paper_analysis/failure_feasibility_20260915/check_materials.py
```

该脚本会向其所在目录写报告。为保留本地盘点快照，在同级新建本轮输出目录并复制脚本运行：

```bash
# 在项目根目录执行；后续命令沿用此 shell 的 FLB_ANALYSIS。
FLB_ANALYSIS="reports/paper_analysis/source_exposed_failure_analysis_$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$FLB_ANALYSIS"
cp reports/paper_analysis/failure_feasibility_20260915/check_materials.py "$FLB_ANALYSIS/check_materials.py"
python3 -B "$FLB_ANALYSIS/check_materials.py" > "$FLB_ANALYSIS/preflight_stdout.json"
```

脚本保持在 `reports/paper_analysis/<本轮目录>/` 层级才能正确解析项目根目录。它依赖旧标注文件做历史交集盘点；这些文件缺失时，可以在本轮脚本副本中将历史交集改为可选，但不能跳过主结果、成员身份或候选集合检查。文件存在不代表精读证据充分。

需要另外实现本轮严格 preflight：**先检查 CSV 原始行数、重复 key，再建立字典**，确认三个输入均为 900 个唯一 `(model, task_id)`、键集合相同，最终得到 241 行 / 89 题以及上述六个计数。不要只检查字典长度而掩盖重复行。

已知本地盘点仅有 65/241 条原始材料齐全，服务器应重新计算。若服务器数据齐全，预期 core-present 为 241/241；若不同，输出逐项缺失清单，继续处理其余可核查材料，不能声称已完成六配置全量精读。不要用新实验替代缺失的冻结运行。

### 3.2 输入差异处理

当前三个核心 CSV 的 SHA-256：

```text
task_results.csv  b538ac9d7fd278604e53ed8c52efb5d862ddc66520b61ea0bbe2d2d81da064b1
run_exposure.csv  2225770987def0556f157fbdd322665c8e4354e92298a43494978afed64f2e0b
run_index.csv     50d8de518d5dc7888cb42019044ee96a662c2dc484e6989558417a6fba35a366
```

若哈希不同，记录差异并判断是路径迁移、换行差异还是成员/结果变化。路径迁移建立显式 `path_mapping.json`，保留原索引；结果或成员身份未消解前，不生成混合版本的总计。**不能修改数据以凑成 241。**

本地 `experiments/paper-results-full-20260913T154543Z.tar.gz` 曾出现 `unexpected end of data`；服务器应使用完整原始目录，不把这个归档当完整证据来源。

## 4. 标注流程：每一行怎么做

### 4.1 先冻结 codebook，再全量精读

使用 Protocol 已定义的 primary cause，不另起一套同义分类。先选 24–36 条覆盖六配置和两类首败阶段的 pilot，记录边界案例和判定规则；pilot 仍属于最终 241 行，不能另加分母。规则修订后，按最终规则重新核对已完成行。

第一轮不要读取历史标签来决定新标签。完成独立精读后再对照旧标注，把分歧记入变更表。历史标注共 122 行，与本次候选交集 89 行，且没有独立人工复核；历史 defect flags 也只是待重新核查的线索。不能把旧两模型 census 和其他模型 postsample 直接拼成本次全量结论。

### 4.2 每条运行必须留下证据链

依次执行，并在私有逐案记录中给出文件相对路径、行号或事件 ID：

1. 核对首败 gate 与原始 evaluator 结果，读取该 gate 的首个失败日志。
2. 打开实际 submission 中相关实现及其依赖。不能仅依据异常类型、最后一行日志或已有摘要包归因。
3. 打开公开 TASK / metadata / behavior contract，将可观察缺口映射到 `B001` 形式的真实 clause ID。
4. 先判断测试是否符合冻结契约、是否存在基础设施/协议问题，再决定是否计入 Agent 分母。
5. 对有效失败选择一个 primary cause，可附多个 secondary tags；用一句脱敏事实描述证据。
6. 核对入口源码读取对应的事件。只有要归因过程原因或标记 `localization` 时，才进一步对相关轨迹作充分审查；没有这种证据就不声称过程机制。
7. 记录不确定点、缺失证据与复核需求，更新逐案 checkpoint，支持中断后续做。

同一个 task 的六份提交可能因不同原因失败，必须分别阅读。没有证据支持某个判断时，不要为了把表填满而强行分类。

### 4.3 有效性与 primary cause

`evidence_eligibility` 使用现有五个值：

```text
valid_agent_evidence
infrastructure_invalid
benchmark_invalid_candidate
policy_noncompliant
evidence_unavailable
```

未消解的来源冲突另设 `evidence_conflict=true` 并写理由，从最终比例中排除；不要擅自向上述枚举添加第六种值。根据冲突性质使用 `evidence_unavailable` 或 `benchmark_invalid_candidate`，保留原始分类。

Primary 决策按 Protocol §5.1：无提交 → 提交外/契约缺陷 → 缺必需 API → 缺内部依赖 → API 存在但语义漂移 → 独立包暴露问题 → 有直接轨迹和提交证据的定位问题 → unknown。合法 primary 标签如下：

```text
agent_process_non_delivery, localization, contract_api_completion,
dependency_closure, behavior_drift, packaging_modularization,
test_gaming_narrow, task_or_evaluator_defect, unknown
```

本候选集合理论上已通过 Build 且有可评测提交，出现 non-delivery 应优先作为身份/首败冲突调查。`test_gaming_narrow` 必须有硬编码等直接证据；Hidden 失败本身不够。空解析结果不自动等于 dependency closure，ABC / overload stub 不自动等于漏实现。

`task_or_evaluator_defect` 配 `validity_override=benchmark_invalid_candidate`，不能计入有效 Agent 失败。其他无效记录也保留在候选台账中；无法归因时用 `unknown` 并说明其因 eligibility 无效而不进入 Agent 分布。**有效但原因不明的 unknown 必须留在有效分母中。**

不把所有 `behavior_drift` 自动加总为「contract closure」。本轮默认报告原始 primary 类别和次级契约维度；如另报 closure 合并项，必须逐案提供独立的 `closure_supported` 判断和定义，不能直接采用旧 validator 打印的机械合计。

### 4.4 Hidden-only 的公平性

对 `hidden_failure`，按 Protocol §11 检查：公开 clause 映射、可从公开任务/上游合理恢复、测试的是外部行为、冻结参考实现通过、隔离确定性、无隐含网络/平台/资源依赖。

引用已有冻结 oracle / isolation 证据，不启动重评测。本轮查不到所需公平性证据时，不视作已经验证；记录缺口并按协议隔离为待审候选。发现缺陷也只记录，不能修测试后偷偷改变本轮冻结结果。

对外材料只能出现公开 clause ID 和一般行为摘要。**不公开隐藏测试名、输入、断言，也不把隐藏输入稍改写后当公开示例。** 私有审查记录可以保留完整定位。

## 5. 数据文件与统计口径

### 5.1 主标注表

`failure_root_cause_annotations.csv` 对 241 个候选各保留一行，包括所有排除项。至少包含以下字段：

```text
task_id, model, suite_id, split, lift_type, feature_family,
functional_pass, first_failure_stage, entrypoint_explicit_read,
evidence_eligibility, original_audit_class, validity_override, validity_reason,
evidence_conflict, context_violation,
root_cause_primary, secondary_tags, contract_clause_ids,
evidence_summary, evidence_path, run_directory,
close_read_tier, review_status, annotator, adjudicated,
independent_human_review, codebook_version
```

保留项目要求的字段取值；未知协议状态不要伪填为 false。`secondary_tags` 和 `contract_clause_ids` 用分号分隔。每行的 `evidence_path` 指向私有逐案说明；说明包含日志、提交、契约的具体定位及必要的上游/轨迹证据。L1 完成行用 `assistant_first_pass`、真实 annotator 身份、`independent_human_review=false`；尚未精读的行不能标 L1。

另交 `annotation_changes.csv`，保留旧标签、当前初审标签、修改理由和后续复核/裁决字段；不要覆盖历史文件。

### 5.2 分母和精确汇总

对每个模型及 pooled 总体输出：

- assigned=150；两类 behavioral-first failures 数量；其中 explicit-read 候选数量。
- 候选数、五种 eligibility 的互斥计数、冲突标志数量及其所在 eligibility。
- 有效 Agent 失败数 `N_valid`、每类 primary 的 `n`、`n/N_valid`、unknown 数量。
- Primary / Extended 首败分层、不同 task 数、L0/L1/L2 覆盖和实际人工复核数。

必须满足：五类 eligibility 合计等于候选数；有效 primary 计数合计等于 `N_valid`；六模型合计等于 pooled 总数。冲突 flag 是附加属性，不能再次扣除一遍。缺陷候选数同时给 run 数和 unique-task 数，避免一题多模型被误读成多个独立缺陷。

输出计数和未四舍五入比例，显示时再格式化。某模型 `N_valid=0` 时显示 NA，不能画成 0% 各类失败。

这是一组冻结候选运行的描述性全量计数。主图默认不做模型显著性排名，不添加伪独立的 run-level 检验。如果文字要比较小样本比例或外推差异，按 Protocol §10 补充合适区间；跨模型比较应按 task 聚类，且说明筛选后组成不同，不能解释成模型的因果效应。本轮无需为增加内容而新增显著性检验。

## 6. Fig. 8、Table 7 和论文文字

### Fig. 8：默认先做一张清晰的主图

建议 **六根横向 100% stacked bars**，每根一个 configuration，分段为有效 Agent 失败的互斥 primary cause，固定配色与类别顺序，unknown 用灰色。小分段不硬塞数字；精确值放随附数据。采用现有论文脚本的字体和输出风格，模型顺序与 Fig. 4 / Table 1 一致。

图内只保留面板标题、坐标轴、数据和极简图例。候选数、每模型有效分母、排除口径、L1/L2 状态、条件性说明放 caption。不要画饼图，不要把六类读源码事件当成六类失败原因。

主文件：`fig8_failure_analysis.py`，支持显式 `--input` 与 `--output-dir`，从本轮冻结标注/汇总读取数据，生成 PDF、PNG 和精确 plot-data CSV；不要把当前统计结果硬编码进脚本。用 Matplotlib 导出图，不调用 LaTeX，设置 `text.usetex=False`。实际打开 PNG 检查遮挡、截断和图例可读性。

### Table 7：给定义和精确总量

默认列：**Category | Operational criterion | n / N (%)**。每个 primary 类别给出简洁的操作判据和 pooled 精确数量，保留 unknown；全局零计数类别仍在机器数据中保留，表中可按篇幅说明为零。

表注写清候选总量、按原因排除的数量、有效总分母、模型各自有效 n，以及 reviewed 状态。完整六模型 × 类别的 exact counts 另交 CSV，避免在主表重复抄一遍 Fig. 8 的所有分段。Table 7 的增量是**可复核的分类定义和精确统计口径**。

交 `table7_failure_analysis.tex` 与对应 CSV，使用现有论文的 booktabs 风格；不改 `main.tex`，不编译。可另交 3–5 个脱敏代表案例，覆盖真实不同类别并附公开 clause，放 `representative_cases.md`，不强制全部挤进 Table 7。

### 文字与插入说明

`paper_insert.tex` 包括：简短方法段、由实际计数支持的结果段、Fig. 8 caption、Table 7 引用和限制段。未完成 L2 时在文件开头写 `% DRAFT: L1 assistant-first-pass; independent human review pending`，caption/文字也明确当前证据档位；不要仅靠文件注释掩盖图表的暂定性质。

限制至少包括：该分析条件化于 behavioral failure 和 observed explicit read；源码读取不等于理解；输出侧标签不证明过程因果；缺陷与 unknown 的处理；人工复核实际覆盖。

采用稳定标签 `fig:failure-analysis`、`tab:failure-analysis`。Fig. 8 / Table 7 是目标总量的工作编号，LaTeX 实际编号随插入位置变化；在 integration notes 中指出推荐 RQ2 插入点和对后续编号的影响，**不要用 setcounter 强行锁编号**。

## 7. 人工复核包：agent 做到哪里，作者还需做什么

按当前 SOP / Protocol，生成两个独立人工 reviewer 的盲审表及相同原始证据包。盲审表不显示 AI primary、AI 理由或另一位 reviewer 的标签；已完成的 AI 注释另存，不混进盲审包。

本轮固定采用 **候选全集的 30% 随机基础样本（73/241）＋全部 unknown、defect candidate、Hidden-only 的并集**。随机种子固定并记录，例如 20260915；基础样本按模型和首败阶段分层，记录取整分配和实际选择。必审集可能让总复核量明显超过 73，不得因为已超过 30% 就删去必审项。若候选身份变化，先解决身份，再重新记录抽样版本。

两位真实人工 reviewer 独立填表，保留各自原始判断；一致性在裁决前的配对标签上计算，写明样本量、缺失处理、抽样组成。可用 Cohen's κ；样本退化无法计算时如实报告，不填 1.0。有效性和 primary 分别处理：primary 一致性只在两人均判为有效的配对行上计算，同时单独报告有效性分歧，不能悄悄删除这些分歧。

分歧经记录的规则裁决；保留初审、双审和最终标签。未复核行仍为 L1，不把整张 CSV 统一标 L2。若规则修订，回查受影响的全量行并重新生成统计。

服务器 agent 未获得真实人工结果时，输出 `ready_for_human_review` 和待办数量即可；**不得虚构 reviewer、签名、κ、adjudicated=true 或 human_double_reviewed**。完成实际复核并满足协议后，才提供 `ready_for_manuscript` 状态。不要因人工尚未开始而停止其他交付。

## 8. 最终目录与验收

所有分析放本轮新目录；绘图源码同时按论文约定放入 `docs/paper/figures/scripts/fig8_failure_analysis.py`。若同名脚本已存在，先检查，避免覆盖其他工作。

```text
reports/paper_analysis/source_exposed_failure_analysis_<UTC时间>/
  README.md                         # 运行方式、范围、主要发现与限制
  STATUS.json                       # 阶段状态、完成数、缺口、人工复核状态
  provenance.json                   # 输入路径/哈希、suite/freeze、脚本版本
  path_mapping.json                 # 仅路径迁移时需要
  codebook.md
  candidate_runs.csv                # 严格 241 行的候选身份
  material_inventory.csv
  missing_materials.csv             # 无缺失也交表头
  failure_root_cause_annotations.csv
  annotation_changes.csv
  denominator_flow.csv
  primary_counts.csv                # model/category/n/denominator/proportion
  secondary_counts.csv              # 多标签，单独说明可重叠分母
  f3_annotation_summary.json
  representative_cases.md           # 仅公开安全表述
  review/                           # 抽样身份、两个盲审表、裁决模板
  private_evidence/                  # 每候选一份定位与精读记录
  scripts/                          # build cohort / aggregate / export / validate
  figures/fig8_failure_analysis.{pdf,png}
  figures/fig8_plot_data.csv
  tables/table7_failure_analysis.{tex,csv}
  paper_insert.tex
  integration_notes.md
  validation.json
  requirements.txt                  # 实际使用的依赖版本
```

脚本须允许用已审查的 CSV 重生成汇总、图和表，不要求重新运行 Agent 或重评测。提供一条可复制的重生成命令；私有证据路径使用相对路径和 manifest，不能只有服务器绝对路径。

至少执行现有 CSV 检查器：

```bash
python3 .agents/skills/featureliftbench-annotate-failures/scripts/validate_annotation_csv.py \
  "$FLB_ANALYSIS/failure_root_cause_annotations.csv"
```

其通过仅表示部分 schema 规则通过，不证明已做精读、材料完整或可发表。还必须实现本轮验收，写入 `validation.json`：

- [ ] 三个源 CSV 的原始行数、唯一键、成员集合与冻结身份相符。
- [ ] 241 候选 / 89 题 / 六模型数量匹配；主标注表无漏行、无重复、无额外运行。
- [ ] 每条 L1 有真实日志、提交、契约定位；来源文件存在且 hash 可核对；无法映射 clause 有明确理由。
- [ ] eligibility、override、primary 与 evidence-conflict 的组合合法；没有无效记录进入有效分布。
- [ ] 所有分母和 pooled / per-model 计数守恒，unknown 未被去掉，secondary 未冒充互斥分布。
- [ ] Fig. 8、Table 7、caption 和正文数值同源；四舍五入误差不改写原始计数。
- [ ] AI 检查、人工复核与裁决状态真实；必审队列完整。
- [ ] 公开候选材料经过自动扫描和语义审查，不含隐藏测试细节或凭证；私有路径未混入论文表。
- [ ] PNG 可读，图没有塞入长解释；未调用 LaTeX 编译器。
- [ ] 原 suite/run/evaluator/submission/frozen task 文件哈希未变。
- [ ] 输出包完整解压，逐文件校验通过，干净目录中能仅凭交付数据重生成图表。

注意：现有 API screen 脚本可能优先寻找 `benchmark/python200_hard_tasks` 而非 `benchmark/tasks`。调用前检查其解析路径；本轮必须审查正确冻结任务包。它只是 L0 辅助工具，不能替代 L1。

## 9. 需要从服务器带回的两个包

### A. 论文候选材料包 `failure_analysis_paper_<时间>.tar.gz`

包括 README、STATUS、codebook、公开安全的逐行标注导出（删除内部 evidence_path 等私有字段）、分母/计数 CSV、summary JSON、图 PDF/PNG/数据、Table 7 LaTeX/数据、paper_insert、代表案例、绘图/汇总/验证脚本、依赖版本和脱敏 provenance。

这个包用于本地审稿和接入论文，**不是自动发布授权**。L1 状态要随包保留。无需带服务器路径、原始轨迹、隐藏日志或隐藏测试。

### B. 私有证据包 `failure_analysis_private_<时间>.tar.gz`

包括完整标注表、变化记录、逐案证据、人工盲审/裁决模板、输入身份 manifest，以及 **241 条候选的最小完整原始证据子集**：run metadata、eval result、首败日志、完整 submission（含资源）、必要 events、冻结公开契约及其 hash。不要只带当前本地缺失的 176 条，以免再次依赖不完整本地归档。

用于复核的隐藏测试、相关参考/上游源码和已有 oracle 验证依据可以放本私有包，按 task 去重并保留目录与定位；不得混入 A 包。源仓库很大时只包含审查所需文件和其版本/hash，明确覆盖边界，不把截断摘要称为完整原始证据。

原始数据只读保留在服务器；导出 run/events 前移除 API keys、认证头和其他凭证，记录脱敏规则、原文件 hash 和导出文件 hash，不能改动原文件。若私有证据必须分卷，提供全部分卷、重组命令和整体 checksum；优先交一个完整可验证的包。不要打包整个环境、venv、缓存或无关运行。

每个包交付前执行 gzip 完整性检查、tar 全成员读取、解压后的逐文件 SHA-256 核对。提供两个包自身的 `SHA256SUMS`，避免再次出现 truncated archive。打包清单使用 allowlist，不能直接把整个报告目录递归当作公开包。

## 10. B：DeepSeek V4 Pro / Contract-Only 的 18 题恢复

### 10.1 先确定名单与原始身份

阅读 `.agents/skills/featureliftbench-run-eval/SKILL.md`。使用：

```text
docs/paper/experiments/source_ablation_40.txt
docs/paper/experiments/source_ablation_40.json
reports/paper_analysis/source_ablation_40_20260913/task_outcomes.csv
reports/paper_analysis/source_ablation_40_20260913/statistics.json
```

在旧逐题表中过滤 `model=deepseek-v4-pro`、`arm=contract_only`，确认 40 个唯一 task 与固定清单相同。逐条查原始 `record_path` 对应的 run / events / submission：**同时具有 LLM timeout 证据且没有可评测提交**才进入恢复名单。不能仅凭 `run_status=failed`、`service_error_recorded=1` 或所有 Missing 自动选择。

预期 **18 条**。导出 `pro_contract_timeout_18.csv` 和同名 task-ID 文本，记录旧 run 路径/hash、错误码/事件定位、无提交依据、恢复理由。若不是 18，先解释身份或归类差异，不能追加普通功能失败来凑数。旧组应为 Contract 6/40、Full 25/40；这是旧数据核对值，不是新结果目标。

原路径由 `task_outcomes.csv` 的 `record_path` 结合服务器实验根目录解析，一般包含 `deepseek-v4-pro/source-ablation-40-r1/contract_only/`。不要拿主榜 Pro 的同名 task 当作 ablation 运行。

### 10.2 配置不变，输出写新目录

从**原 Pro / Contract-Only 的实际 runner、run.json、持久化 agent 配置**复制运行设置：provider/model ID、generation 参数、condenser、context、预算、镜像、源快照、依赖、网络和评测策略。不要只套今天的默认 profile。

当前持久化记录显示：OpenHands maximum iterations 500，Pro harness step limit 120，逐题 wall timeout 3600 秒，context 131072、reserved output 8192。服务器要逐项核验后记录，不能将 500 和 120 误当同一个参数而相互覆盖；原 Pro condenser 也不能换成 Luna/Qwen 的配置。

保留 `source_context=contract_only`、原公开契约和原 agent 可见内容。做不调用模型的 prompt/workspace 检查，确认没有把仓库源码、reference、hidden tests 或 Hint 暴露给 agent。evaluator 仍使用原冻结 capsule 和原 Docker 流程，Contract-Only 是 agent 可见输入的条件，不是删除 evaluator 的来源证据。

新运行写入，例如：

```text
experiments/python/openhands/deepseek-v4-pro/source-ablation-40-contract-recovery-<UTC时间>/attempt-01/
```

生成真实可执行的 `run_pro_contract_recovery.sh`，只把冻结的 18 个 ID 转成 CLI 的逐个 `--task-id` 参数。优先复用原自定义 driver；若使用 CLI，先查看服务器 CLI help 并核对原命令，不能套用 `SOURCE_EXPOSURE_HINT_RUNBOOK.md` 中暂缓的 Hint 命令。保存脱敏完整命令和配置 diff。不能对原 40-task suite 直接运行会重试所有 failed 的 `--resume`。

使用服务器已有授权凭证，不打印密钥，不新建模型账户。若原模型版本不可再用，记录具体差异，不能悄悄换模型后称为同配置恢复。保守并发运行，记录任何并发/重试层面的变化以及新旧运行时间。

### 10.3 恢复规则先写入 policy，再启动

创建 `recovery_policy.json`，在任何新结果产生前固定：

- 每个入选 task 从原始 Contract-Only 初态重新运行，不能带入失败 attempt 的会话、提交或人工提示。
- 首轮只运行这 18 题一次。普通 Build / Primary / Extended / Isolation 失败，以及非服务错误造成的无提交，都是有效恢复结果，**不能因失败继续刷题**。
- 只有再次有明确服务 timeout / transport outage 且无提交，才允许按同一政策等待服务恢复后重试；默认每题最多 **3 次新增 attempt**（首轮加至多 2 次恢复），所有记录保留。若原协议有更严格的重试上限，沿用更严格值。
- 选取**按时间最早、未被明确服务中断＋无提交规则排除的恢复 attempt**，不以通过与否选择。达到上限仍无可保留恢复时，标 `unresolved_service_failure`，暂保留旧结果并如实呈现；不能宣称已经跑干净。
- 持续服务故障时停止提交新请求并报告，不能无限重试或自动升级预算。模型端每次调用的内部 retry 也单独记录，不与 task-level attempt 混淆。

目标是恢复公平的运行机会，**不是让这 18 题都通过**。新记录仍有功能失败完全正常。由于恢复发生在较晚时间，保留时间/服务版本限制，不能声称复现了原运行的所有服务条件。

### 10.4 合成新的 40-task 分析视图并更新统计

交 `retained_contract40_manifest.csv`：40 行，每行选中的原/新 run 路径、attempt、hash、来源与保留理由。必须为 **原 22 条不动 + 入选 18 条按 policy 的选择**。不要覆盖旧 `suite.json` 或旧逐题表，通过 manifest 构建新分析版本。A 的主榜 900 行与 241 候选不因本消融恢复而变化。

与原来的同题 Pro Full Source 40 条配对，生成新版 40 对和全部统计：

- 两臂 pass n/40、both / full-only / contract-only / neither，首败阶段、服务中断和无提交数。
- `Δ = Full − Contract` 的百分点差、95% paired task-bootstrap CI、双侧 exact McNemar；复用旧统计的 100,000 resamples 和 seed 20260913，并保存实现。
- 主文原有三模型检验族的 Holm 校正要**对三个原始 p 值一起重算**：Luna、Qwen 的原始结果不变，调整后 p 值仍可能变化。保留原已有 repository-bootstrap / sensitivity 项的可复现更新。
- 交 `before_after.csv`：旧 Pro、恢复后 Pro 的统计及 18 题逐条变化；保留旧 40-task 结果作 provenance / 敏感性对照，不只留好看的新版。

在新分析目录交 `task_outcomes.csv`（完整三模型 × 两臂 × 40 = 240 行）、`statistics.json`、Pro 的 40 行 pairs 和复现脚本；旧 Luna/Qwen 及 Pro Full 的逐行身份与结果必须不变。

交消融图的新版 PDF/PNG、Table 4 新版 `.tex` 与 RQ3/caption/Threats 修改片段。现有绘图入口是 `docs/paper/figures/scripts/fig5_source_ablation.py`，文件名中的 Fig. 5 不代表当前主文最终编号；它目前有 Pro 固定 dagger 标记，不能只换数字不审查脚注逻辑。新脚本副本支持显式输入，输出到 recovery 目录，不覆盖已定稿图或改全局 manifest。18 题全部恢复后，可删掉「当前分析仍含这 18 次 timeout」的表述，但要保留「服务恢复后替换运行」的方法说明；仍有未解决项时保留精确提示。

本模块验收：只新增指定 18 题的允许 attempts；22 条、Full 40 条和其他模型不变；保留清单恰好 40 条；完整分析表恰好 240 条；配对计数守恒；旧文件 hash 不变；没有 best-of-N 选择。

## 11. C：Luna / GLM 的可靠 Token 恢复与估算

### 11.1 范围和目标指标

仅处理 `paper_sources.json` 指向的主榜保留运行，过滤固定 150-task membership：**Luna 150 + GLM 150 = 300 条**，包含成功、失败和提前结束，不能只在成功集统计。不是两模型的 40-task ablation。

旧 `reports/paper_analysis/python150_prime_v2_analysis_20260905/token_usage.csv` 显示两模型各 150 条均 `usage_unverified`，旧表注记为 provider 没有返回 usage。此次用户明确要求「恢复不了估算」，因此允许另产估算结果，不沿用旧文件的 `do not impute` 限制；**旧事实与原始文件不改，估算不能冒充实测**。

最终要给 Table 1 用的 **per-run token 数的 Median、P90（单位 k=1,000）**，并给原始 token 单位、覆盖率和测量口径。当前 Table 1：Pro/Flash 是 uncached prompt + completion，Qwen/OSS 是 provider total；不能把 Luna/GLM 的估算悄悄称为 uncached 或与这两类统一成本排名。

### 11.2 先找可恢复的真实 usage

按下列优先级检查服务器已有记录：

1. 原始 API response / streaming final usage、request-ID 可匹配的已存 provider 记录。
2. 本地代理逐请求日志、OpenHands/LiteLLM 记录、事件中的 LLM metrics、run 中的 agent_usage。目录结构按实际 runner 查找。
3. 若存在完整可信的 run 累计 usage，可以恢复 run 总量；保留累计语义证据，不要求一定有逐调用记录。

先读 `harness/featureliftbench/llm_usage_proxy.py`、`openhands_runner.py` 的实际字段语义。当前实现会在缺失时累计为 0，而且 `usage_verified` 可能只证明 prompt 存在，**不能把总数为 0 或一个 verified=true 当作所有调用和 completion 完整**。

逐请求匹配、去重并识别累计快照：同一个响应在 proxy、event、metrics 多处出现只算一次；累计快照不能逐条求和；stream chunks 不能把同一 final usage 重复累加。真实不同 retry 请求会消耗 token，需要按定义保留；没有 usage 的失败请求不能凭 HTTP 错误就假定零消耗。

分开保存 prompt、completion、cached/uncached、reasoning（若 provider 单独报告）、total。cached 若已包含在 prompt 不再加一次；reasoning 若已包含在 completion 不再加一次。字段缺失用 null 和 coverage，不用 0。所有预期调用已对齐或可信 run 累计完整，才能称该 run 的 total 为 `measured`；只有部分调用恢复则为 `partial_measured`。

记录来源路径/hash、request ID、字段映射和去重依据。模型 alias、call 数与事件不一致要调查。先做覆盖两模型及长短轨迹、不同 outcome 的小样本人工核对，再批量恢复 300 条。

### 11.3 恢复不了时实际给出有依据的估算

不要停在「无法恢复」：对未完整恢复的 run 按以下证据层级尝试，并交数值、方法和限制。

**优先：逐 API 请求重建 token。** 有完整 outbound request/response payload 时，用可核实的对应 tokenizer 与 chat serialization 模板对每次请求计算：

```text
estimated visible tokens per run
  = Σ over distinct API requests (serialized input tokens + visible output tokens)
```

输入应包含 system、实际发送的历史、tool schemas、tool results、消息包装等；每次重复发送的上下文都需要重新计数。一次性 tokenize 整个最终 transcript 会严重漏掉重复 prompt，不能充当累计 token。应按实际 condensation、截断和工具调用过程重建，不能把完整历史假装每次都被发送。provider 隐藏推理、服务端包装和不可见中间调用未观察到时，明确本估算只覆盖可见 token；不能称它为完整 billed total，也不能默认隐藏 reasoning=0。

**次选：基于完整可见请求的代理 tokenizer 估算。** 无可靠对应 tokenizer 时，使用记录版本/hash 的本地 tokenizer 作为 proxy，并给模板/编码选择的敏感性范围。有可比、同时含 payload 和真实 usage 的旧记录时，先核对同 provider/model/计费语义，留出任务验证偏差，输出 MAE/相对误差等；其他模型的校准最多支持 proxy 灵敏度，不能证明 Luna/GLM 的真实 tokenizer 相同。不能只按字符数除 4 伪称精确。

**最后：缺 payload 的模型化插补。** 若部分 run 有实测或可重建 token，可在同模型中使用调用数、可见输入/输出长度、上下文规模和凝缩记录拟合估算器，按 task 分组验证，说明训练覆盖和外推区间。只在有可检查的训练/验证证据时补缺失 run；不能机械用 Pro 的 token/step 乘 Luna 或 GLM steps，也不能只用运行时长换算。只恢复少量短轨迹时尤其不能称对长轨迹估算可靠。

如果连请求内容和可信校准样本都没有，交清楚的缺证据说明；可给有依据的情景范围，但不要凭空造一个点数。此时 Table 1 继续 NA，单独给可见部分估算或下界（只有数学上成立时才叫下界）。**要求估算是要求计算一个可解释的近似值，不是要求一定把缺失格填满。**

每个 run 保存实际恢复量、估算缺失量、合计估算和方法，不重复计算已恢复请求。状态至少区分 `measured`、`partial_measured`、`estimated`、`mixed`、`unavailable`，并另设 `metric_scope`（provider_total / uncached_plus_completion / visible_input_output_proxy 等），防止数值相加后丢失语义差异。

### 11.4 怎么交数值和写入表格

- `token_calls.csv`：如有逐调用记录，交调用身份、各 token 分量、是否实测、完整性、来源与去重信息；无 call 级来源的累计 run 不伪造调用分解。
- `token_runs.csv`：固定 300 行，model/task/run、各分量、measured/estimated 状态、metric_scope、可观测调用覆盖、估算方法/版本、缺失原因、provenance。
- `token_summary.csv/json`：每模型 assigned=150、各状态 n、可统计 n、Median/P90（tokens 和 k）、选定口径、估算敏感性范围。完整性不足时，只能称「可观测子集」统计；不能把子集分位数当 150 题完整分位数。
- `token_method.md`、恢复/估算/验证脚本、校准验证数据与报告、`table1_token_cells.tex` 和明确的表注替换片段。

同一模型若需要混合实测与估算，必须先确保指标语义一致；provider total 与 visible-only proxy 不能直接混算一个 Median。可对所有 150 条统一计算 visible proxy 作为独立口径，同时另列实测覆盖。统计中只要有估算，Table 1 使用 `≈` / `est.` 或明确上标并解释，不仅在深层 README 说明。敏感性范围不是 95% CI；除非有相应统计设计，不要给区间乱贴置信标签。

本模块必须实际尝试产生 **Luna Median/P90 和 GLM Median/P90**，结果可能是实测、估算或有证据限制的未完成项；不能直接返回两行空表。不要新增昂贵模型调用、重跑 300 题、改写原 usage 或据此新增未经支持的成本结论。

## 12. 三项工作统一交付与状态

沿用 §9 的两个包，增加模块目录 `failure_analysis/`、`pro_contract_recovery/`、`token_recovery/`：

- **论文候选材料包**：A 的 Fig. 8 / Table 7；B 的恢复后消融图、Table 4 与 RQ3/caption 修改片段；C 的 Table 1 token 单元格、表注、估算方法摘要；附全部重生成所需脱敏数据与脚本。
- **私有证据包**：A 的 241 条证据；B 的全部新增 attempts、18 题选择依据、40 题 retained manifest、配置/prompt diff 和原始结果定位；C 的 token 原始证据、字段映射、去重与估算校准材料。涉及凭证时按 §9 脱敏。
- **总 README / STATUS.json**：分别列 A 精读与人工复核进度、B 已恢复/未解决数和保留规则、C 每模型实测/估算/缺失覆盖。不能一个全局 completed 掩盖子模块未完成。

不编译，不直接覆盖 `main.tex`、已定稿 figures、`paper_sources.json` 或原 CSV。将可采用的 LaTeX 与图表放新版本目录，提供 `integration_notes.md` 和建议输入 manifest 的补丁供本地接入。B 的新结果不污染 A/C 的主榜冻结身份。

所有新增包仍需完整性检查和 SHA256SUMS。最终回复必须额外给出：**Pro 原 18 题中实际恢复几题、尚有几题服务失败、新 Contract pass/40；Luna 和 GLM 各自 token Median/P90、单位、实测还是估算、覆盖多少/150。**

## 13. 可直接复制给服务器 agent 的指令

```text
请在 FeatureLiftBench 项目根目录阅读并执行：
docs/paper/experiments/FAILURE_ANALYSIS_SERVER_RUNBOOK.md

本轮共三项任务：A. Fig. 8 + Table 7 系统 failure analysis；
B. Pro / Contract-Only 的 18 条服务 timeout + no-submission 恢复；
C. Luna、GLM 主榜 token usage 恢复，无法恢复则按文档作有依据的估算。
服务器已有实验结果；请先核对完整性和冻结身份，不要默认目录齐全就证据充分。
优先启动 B，在等待运行时推进 C 和 A。以下 failure-analysis 范围仅属于 A。

固定分析范围：论文 Python-150 × 六配置的 900 条主结果中，首败为
public_failure 或 hidden_failure，且 entrypoint_explicit_read == 1 的候选。
当前预期 241 条 / 89 个 task；Pro/Flash/Luna/GLM/Qwen/OSS 分别
29/34/33/36/43/66。241 是候选数，审查后的有效 Agent 分母需要重新确定。

按已有 failure-analysis skill、Protocol 和 SOP 完成逐案 L1 精读。
每条读取原始首败日志、相关 submission、公开契约；不能依据异常名自动分类，
不能复制历史标签，不能将源码读取解释为理解或因果机制。
保留所有排除记录和 unknown，报告有效性、主类别、精确分母和证据档位。

在新的 reports/paper_analysis/source_exposed_failure_analysis_<UTC时间>/
输出完整标注、证据、统计、图表、LaTeX 插入草稿、复核模板和验证报告。
绘图 Python 同时放 docs/paper/figures/scripts/fig8_failure_analysis.py，
遵循现有图风格，图内只留必要内容，解释写 caption。

按 §10 核对并冻结 Pro 的 18 题恢复名单和 policy，只重跑这 18 题到新目录，
不得重跑另 22 题、Full Source 或其他模型。最早有效恢复 attempt 为准，不能
挑 best-of-N。组合 40 题 retained manifest，更新完整配对统计、消融图和 Table 4。
按 §11 检查 Luna/GLM 各 150 条主榜运行的真实 usage；缺失不是 0。
恢复不了时实际尝试逐请求 tokenizer 重建或有验证的估算，给 Median/P90、
单位、覆盖和 est. 标识；不能把可见文本 proxy 冒充完整 billed token。

不编译 LaTeX，不改 main.tex，不覆盖原 suite、run、eval、submission 或冻结任务。
只有 B 允许上述恢复调用；A/C 不运行新实验，不新增 Hint，不为 token 重跑主榜。
不发布或提交任何外部内容。数据身份冲突要记录并解决，不能凑数。
缺少个别证据时继续其余审查并交缺失清单，不能假装全量完成。

自主完成 L1 能完成的全部交付，生成真实的独立人工盲审队列；
没有两位真实人工复核时，状态写 ready_for_human_review，不虚构 L2 或一致性。

最终按 §12 给我含三个模块的两个包：论文候选材料包、私有证据包，附 SHA256SUMS。
最终回复列明：候选/已精读/缺材料/有效/各类排除/unknown 数量，六模型有效 n，
Fig. 8 与 Table 7 路径，当前能支持的结论，尚待人工复核数量，两个包的绝对路径。
另列 Pro 恢复/未解决数量、新 Contract pass/40，以及 Luna/GLM token Median/P90、
实测或估算状态、覆盖多少/150；提供新版消融图/Table 4、Table 1 单元格 LaTeX。
不要只给建议或计划；请实际完成材料审查、产物生成、校验和打包。
```

若服务器没有本文档或最新 paper manifest/索引，先把这些文件及其引用的输入依赖同步到服务器，再开始。不要用服务器上同名但不同版本的旧论文结果替代当前冻结口径。
