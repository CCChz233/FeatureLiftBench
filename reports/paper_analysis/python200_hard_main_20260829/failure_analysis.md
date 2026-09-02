# Python-200′ 当前候选结果的具体失败归类

> **Status: evidence audit complete · semantic labels are an assistant first pass · human adjudication pending**

## 结论

收到的 suite 有 **68 个表面未通过结果**。其中 **33 个是基础设施结果**，另有 **8 个题目/评测缺陷候选**；当前可进入 Agent 根因分母的是 **27 个失败**。根因统计不使用 68 作为分母，也不把上下文违规改写为功能失败原因。

在这 27 个有效 Agent 失败的一轮输出侧审查中，主要现象是行为已经实现但语义发生漂移，其次是契约/API 完整性不足。该结论描述提交的外部表现；在完成 trajectory 双审前，不能进一步声称这些错误由搜索、记忆或预算中的某一个过程机制导致。

## 证据有效性

| 类别 | 任务 | 占 68 个未通过 | 处理 |
| --- | --- | --- | --- |
| 有效 Agent 失败 | 27 | 39.7% | 进入根因分母 |
| 基础设施无效 | 33 | 48.5% | 修复后重跑 |
| 题目/评测缺陷候选 | 8 | 11.8% | 人工裁决，裁决前排除 |

## 有效 Agent 失败的首败阶段

| 首败阶段 | 任务 | 占 27 个有效失败 |
| --- | --- | --- |
| 未提交 | 2 | 7.4% |
| Public | 17 | 63.0% |
| Hidden | 8 | 29.6% |

## 有效 Agent 失败的输出侧根因

| Primary cause | 任务 | 占 27 个有效失败 | 解释 |
| --- | --- | --- | --- |
| 行为语义漂移 | 19 | 70.4% | API 已存在，但返回、顺序、状态、解析或异常语义不同 |
| 契约/API 完整性不足 | 6 | 22.2% | 缺少模块、成员、导出、签名或必要行为分支 |
| Agent 未形成提交 | 2 | 7.4% | 正常启动但未形成可评测提交 |

本轮没有把任何任务归为 localization、dependency closure 或 packaging failure。这不等于证明 Agent 在这些方面没有问题；它只表示当前 evaluator 日志和提交没有提供足够直接证据。

## 协议合规性

有效 Agent 失败中有 **11/27** 个同时存在 context-window 违规。它们可以用于内部行为诊断，但在严格 Python-200′ 主表中仍属于冻结替换集，不能直接进入最终分数。

## 新发现的题目/评测缺陷候选

- `click__lazy_command_core__hard3_001`：首败来自未在公开契约中出现的 invoke 方法。处理：运行时 TASK 只声明 get_command 和 resolve 而 evaluator 调用 invoke
- `hatch__project_metadata_core__hard3_001`：提交满足字面小写要求但测试增加了未公开的 separator canonicalization。处理：TASK 只要求 lowercases names 而 evaluator 额外要求空格转连字符
- `hydra_core__compose_initialize_core__001`：失败发生在 public test 准备阶段且尚未调用提交实现。处理：旧 public test 在调用提交前创建固定目录并因残留目录失败；当前冻结题已改为只读 fixture
- `parsel__selector_namespace_core__hard3_001`：当前 TASK 已在实验后补入 get/getall。处理：运行时 TASK 未声明 Selector.get/getall 而 evaluator 调用 get
- `paste__dispatch_map_core__001`：提交已经返回 404 状态但测试增加了未公开的正文格式要求。处理：TASK 只要求 HTTP 404 status 而 evaluator 要求正文含字面量 404
- `pluggy__hook_wrapper_core__hard3_001`：首败直接调用未公开的 call_historic。处理：运行时 TASK 未声明 call_historic 及其签名
- `pytest__ini_markers_core__001`：当前 TASK 已在实验后补入 from_lines。处理：运行时 TASK 未声明 from_lines 而 evaluator 调用该方法
- `readme_renderer__content_type_core__hard3_001`：标题已经渲染为 h1 但测试使用与公开行为不对应的字面标记。处理：TASK 只要求选择 Markdown renderer 而 evaluator 要求输出含 markdown 字样

该修正不回写收到的原始 suite，也不静默修改旧 `failure_audit.csv`；它作为语义审查层的 validity override 单独保留。

## 当前证据可以支持什么

- 68 个未通过结果的证据有效性、首败阶段和逐任务证据路径；
- 27 个有效 Agent 失败的一轮输出侧语义归类；
- 基础设施、协议违规和题目缺陷候选与 Agent 行为的分离；
- 以 Public/Hidden 和稳定 clause ID 为单位选择代表性案例。

当前还不能支持：

- 将 assistant first-pass 标签当成人工金标；
- 从输出错误直接推出搜索、记忆、上下文压缩或动态分析能力的因果机制；
- 在 84 个严格替换任务完成前把 132/200 写入最终主表；
- 在 Hidden-only 契约完成人工双审前声称全部隐藏失败都公平且无争议。

## 下一轮人工复核

1. 双审全部 8 个 Hidden-only 失败及其公开 clause 映射；
2. 裁决题目/评测缺陷候选；
3. 对 6 个 contract/API completion 和分层抽样的 behavior drift 阅读 trajectory；
4. 记录第二 reviewer 标签、分歧和最终 adjudication；
5. 完成人工一致性后再生成论文级根因比例和代表性案例。

逐任务记录见 `failure_analysis.csv`，机器可读汇总见 `failure_analysis.json`，标注源见 `failure_root_cause_annotations.csv`。
