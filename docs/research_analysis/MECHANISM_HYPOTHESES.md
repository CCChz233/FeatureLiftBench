# FeatureLiftBench 竞争机制假设（自动生成统计）

> 本文件由 `render_research_docs.py` 生成。数值来自 `trajectory_records.csv`；定性轨迹判断通过 task/path/event ID 在 `TRAJECTORY_FINDINGS.md` 审计。以下 H1–H6 是竞争解释，不预设 ECSM 正确。

## 1. 当前证据边界

450 条 frozen trajectories 中，public→hidden gap 为 98/450 (21.8%)，在 public pass 条件下为 98/319 (30.7%)；但 62/450 (13.8%) 在环境/evaluator 阶段没有有效测试结论。primary failure 的行为/接口分类依赖日志启发式，因而任何“共同机制”结论都仍是待干预验证的假设。

## H1：主要问题是定位失败

- **操作化定义：** Agent 未在预算前找到 feature source entrypoint 或首个正确 provider；Oracle Locate 提供 entrypoint/source file 后，hidden Pass@1 应接近 Oracle Closure。
- **支持证据：** `coverage__config_merge_core__001` 的真实轨迹明确说 repository empty，随后从知识重写并 hidden fail；missing submission 与一部分 public API failure 也与定位失败相容，但不是定位失败的直接证据。
- **冲突证据：** `requests_cache` 已定位 cache-key/policy 且 ratio=0.96319 仍漏明确 export；`pydantic_v1` 已扩到 15 files 仍漏 `datetime_parse`；`phonenumbers` 已找到 regional data 仍漏字段；`readme_renderer` ratio=3.044248 仍漏外部依赖。
- **可证伪预测：** Oracle Locate 相对 Strong Prompt 若在 10-task pilot 上增加至少 2 个 paired hidden pass，并与 Oracle Closure 相差不超过 1 个任务，H1 获支持；若 Oracle Locate 小而 Oracle Closure 大，H1 作为主要瓶颈被否定。
- **区分实验：** Strong Prompt vs Oracle Locate vs Oracle Closure；模型、预算、工具、测试权限固定。
- **与简单解释区别：** 这是普通检索/RepoMap 最能解决的假设；它不预测 deletion verifier 会改善 compactness。
- **当前置信度：低—中。**
- **新增数据：** first-correct-file step、entrypoint recall、空 source mount 发生率、Oracle Locate arm。

## H2：主要问题是依赖闭包恢复失败

- **操作化定义：** Agent 找到入口后，未恢复 output API、transitive provider、allowed external dependency、resource 或 runtime/global-state edge；Oracle Closure 显著优于 Oracle Locate/Static Hint。
- **支持证据：** primary labels 中 `hidden_interface_or_closure_failure`、`dependency_closure_omission` 可审计；具体有 `pydantic_v1→datetime_parse`、`requests_cache→normalize_body`、`phonenumbers→metadata field`、`readme_renderer→nh3`、`bleach→webencodings`。
- **冲突证据：** `pluggy` 与 `coverage` 的首要失败是行为语义；低 ratio 桶仍有 88/197 (44.7%) functional pass；copy-heavy `stevedore` 成功。
- **可证伪预测：** Oracle Closure 相对 Oracle Locate 至少多 2 个 paired hidden pass，且 closure recall/F1 上升、interface/build failure 下降；若只提高 footprint 而不提高 hidden，H2 被削弱。
- **区分实验：** Oracle Locate vs Static Closure Hint vs Oracle Closure；按 static import 与 runtime/resource strata 分层。
- **与简单解释区别：** localization 只给入口；闭包要求 artifact/obligation provider 集。普通依赖图只给候选，不能证明 runtime necessity。
- **当前置信度：中—高（作为重要局部机制），尚未证明主导全部失败。**
- **新增数据：** executable oracle closure、symbol/resource/runtime gold、closure P/R/F1。

## H3：主要问题是行为契约和 hidden case 不完整

- **操作化定义：** included artifacts 足以 build/import，但 Agent 未枚举并 probe 异常、顺序、边界、合并、状态转移等行为义务；hidden-aware validation 主要修复 behavior failure。
- **支持证据：** `hidden_behavior_contract_failure` 是最大的可评测单一失败标签；`pluggy` 的 historic direct-call exception、`coverage` 的 setup.cfg merge、pydantic rerun 的 structured error 都是具体案例。
- **冲突证据：** import/export/provider 缺失可被机械 closure 检查发现，不要求猜 hidden edge；contract-review tasks 会夸大表面 hidden gap。
- **可证伪预测：** Hidden-aware checklist/contract probes 显著改善 behavior cohort，但对 `datetime_parse`/`normalize_body` 等 provider omission 收益小；若只增加文本讨论不改 hidden pass，则 H3 的 prompt 版本被否定。
- **区分实验：** Strong Prompt vs hidden-aware validation（在 pilot 中由 ECSM probe state 与 decision-rule behavior subgroup读取）；另对 Oracle Closure 后残余失败分类。
- **与简单解释区别：** 不是“测试再多一点”，而是 TASK obligation→probe→fresh result 的覆盖矩阵；普通 reflection 没有新执行证据不计入。
- **当前置信度：高（局部），中（作为总体主因）。**
- **新增数据：** behavior-family gold、probe coverage、Oracle Closure 后残余错误。

## H4：主要问题是停止策略错误

- **操作化定义：** Agent 在仍有 unresolved hard reference、未覆盖 behavior/runtime obligation、stale probe 或 pending prune 时提交。当前代理指标是 unsupported completion claim。
- **支持证据：** explicit FinishAction 269/450 (59.8%)；unsupported completion claim 68/450 (15.1%)，占非环境 functional failure 68/168 (40.5%)。`requests_cache`、`click`、`coverage` 都在完成信号后暴露 hidden failure。
- **冲突证据：** 23 个 step-limit 与 2 个 timeout 并非主动早停；纯实现错误即使延后停止也可能不修复；unsupported claim 是高精度代理而非完整 stopping-error gold。
- **可证伪预测：** 在相同信息下，fresh-evidence stopping guard 降低 public-hidden gap；如果只增加 token/tool calls、hidden 不升，则 H4 被削弱。
- **区分实验：** Strong Prompt vs reflection vs hidden-aware checklist vs ECSM stopping ablation；比较 public pass 后的新增 state-changing probes，而非只比较额外步骤。
- **与简单解释区别：** “弱模型”预测 guard 也无用；停止假设预测同一模型、同一候选信息仅改变提交条件即可改善。
- **当前置信度：中—高。**
- **新增数据：** submit-time unresolved/risk snapshot、last-mutation 后 probe freshness、public-pass 后动作类型。

## H5：主要问题是 Agent workflow 与 feature lifting 不匹配

- **操作化定义：** 通用 read/edit/test workflow 没有显式维护 `obligation→provider→probe→risk`，因此 locate、expand、replace、adapter、prune、restore、stop 之间无状态连续性。
- **支持证据：** closure plan 只在 49/450 (10.9%) 出现，自生成测试只在 48/450 (10.7%) 出现；重复 path read 影响 295/450 (65.6%)。`pydantic_v1`/`phonenumbers` 的大量探索未转化为 closure completion；`sqlalchemy`/`stevedore` 成功但 copy-heavy，显示 recall 与 compactness 没有统一 controller。
- **冲突证据：** 现有 OpenHands prompt 已包含 FeatureLift 约束；一些 compact run 成功；文本规则检测不到隐式规划质量。
- **可证伪预测：** 等预算 ECSM 超过 Strong Prompt，且不仅 hidden pass 上升，还同时改善 closure F1、重复探索或 compactness；如果仅多消耗计算，H5 不成立。
- **区分实验：** Strong Prompt vs Copy-first Prune vs ECSM，并做 `ECSM - state`、`- pruning`、`- stopping guard` 消融。
- **与简单解释区别：** 不是更长 prompt、RAG 或 multi-agent；机制变量是持久 state、可执行 update 和不可绕过 guard。
- **当前置信度：中。**
- **新增数据：** 每步 state delta、动作净风险收益、prune/restore 因果日志。

## H6：主要问题是工具或 harness 噪声

- **操作化定义：** Agent 失败主要由 tool execution、schema 格式、evaluator dependency 或环境中断造成；修复噪声后方法间差异显著收缩。
- **支持证据：** tool execution error 影响 187/450 (41.6%)，harness format error 影响 193/450 (42.9%)，evaluator/environment error 影响 62/450 (13.8%)；`responses`、`yamale` 和 frozen pydantic first run 是直接案例。
- **冲突证据：** 有效评测中仍有 98/450 (21.8%) public→hidden；tool/harness error 可被恢复且也出现在通过 run；`responses`/`yamale` saved-submission 重评后仍 hidden fail（补充证据，不回写 frozen CSV）。
- **可证伪预测：** 在统一 Docker/依赖并排除 environment rows 后，若 H1–H5 的 arm 差异消失，H6 获支持；若差异保持，H6 只是重要混杂因素。
- **区分实验：** pilot 预检 reference + identical runtime；同时报告 ITT raw、environment-excluded 和 contract-review sensitivity。
- **与简单解释区别：** H6 是 measurement validity 假设，不是 Agent 方法创新。
- **当前置信度：高（噪声确实存在），低—中（作为主要共同原因）。**
- **新增数据：** 全 70 cells 的环境预检、同 submission 重评、错误重试归因。

## 2. Under- 与 over-extraction 的 task-level 对照

| feature | under proxy ≤0.25 | over proxy >0.80 | 当前解释 |
|---|---:|---:|---|
| known-ratio n | 197 | 55 | 两桶分母不同 |
| functional pass | 88/197 (44.7%) | 31/55 (56.4%) | 两端都有成功/失败，不支持单调“越少越好/越多越好” |
| public→hidden / public pass | 53/141 (37.6%) | 14/46 (30.4%) | 两端 gap 都高；差异不是因果 |
| closure plan | 19/197 (9.6%) | 6/55 (10.9%) | 两端都很少，符合但不证明共同 workflow 假设 |
| self tests | 23/197 (11.7%) | 9/55 (16.4%) | 规则只检测存在，不检测覆盖质量 |
| hidden risk discussed | 142/197 (72.1%) | 43/55 (78.2%) | 仅“讨论”不能区分两端 |
| repeated-read affected | 131/197 (66.5%) | 23/55 (41.8%) | 轨迹形态存在差异，反对简单同源断言 |
| unsupported finish | 37/197 (18.8%) | 10/55 (18.2%) | 比例接近，符合共同 stopping-risk 假设 |
| median copied files | 5.0 | 6.0 | ratio 由 LOC 而非文件数定义 |
| median tokens | 1,705,916 | 1,513,048 | over 并没有简单消耗更多 token |

任务正反例见 `TRAJECTORY_FINDINGS.md`：under-fail 为 `diskcache`/`click`/`pytest`，under-pass 为 `dynaconf`；over-fail 为 `parsel`/`requests_cache`/`readme_renderer`，over-pass 为 `sqlalchemy`/`stevedore`。因此“under 与 over 是同一不确定性的两种动作”目前仅是**待验证假设**。最小证伪实验是：Oracle Closure 是否同时减少 omission 与无必要复制；copy-first + executable deletion 是否保持 hidden 而降低 ratio。

## 3. 竞争假设的判别顺序

1. 先做统一环境预检并冻结 valid cells，控制 H6。
2. 比较 Strong Prompt→Oracle Locate，检验 H1。
3. 比较 Oracle Locate→Static Hint→Oracle Closure，检验 H2 与静态/动态分解。
4. 对 Oracle Closure 残余失败做 behavior-family probe，检验 H3。
5. 比较 Strong Prompt、Copy-first Prune、ECSM 及 stopping/state 消融，检验 H4/H5。

当前最值得先验证的是 **H2 vs H1**：Oracle Locate 与 Oracle Closure 的差值能直接决定研究应聚焦检索，还是聚焦 executable closure recovery。ECSM 只有在等预算下同时改善 hidden correctness 与 closure/compactness，并满足预注册 compute guard 时才值得继续。
