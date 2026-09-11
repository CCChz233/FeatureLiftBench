# 第五章案例与讨论写作依据

2026-09-08。扩写 `../main.tex` §5.2–5.3；保持 §5.1 的七题敏感性集合、既有标注和数值表不变。
只读取本地契约、提交代码与保存的评测记录，没有执行模型、提交代码或 reference，没有编译或渲染。

## 案例选择与范围

选取既有 Pro/Flash 失败全集中的两个任务，分别精读两个模型的提交，共四份产物。四份均记录为 Build 和 Isolation 通过、Public 首败。例子用于说明实现偏差，不构成代表性抽样或独立人工复核的原因分布。

原正文的 Alembic、aiohttp 简例未继续作为确定的 agent 错误扩写：前者涉及字面 revision ID 与符号标识的优先级，后者涉及非法输入的判定边界，不能仅凭摘要消除这些解释问题。这是选例决定，不是新增缺陷裁定；没有修改历史标签、七题排除集或统计分母。

## 案例 1：poetry-core 的输入覆盖不完整

- Task ID：`poetry_core__dependency_groups_core__hard3_001`。
- 当前公开契约：B001 要求从 PEP 621 project metadata 构造组；B002 另要求 mapping 形式的 dependency-groups 及传递 include；B003 要求循环 include 抛出 ValueError。
- Pro：提交 `featurelifted/__init__.py` 的 `parse_project_dependencies` 第 136–151 行只读取 `dependency-groups`；`resolve_group` 第 154–179 行有递归和环检测。
- Flash：同文件第 185–209 行接受 group mapping 的不同拼写或嵌套，没有普通 project dependencies / optional-dependencies 路径；第 223–255 行有递归与环检测。
- 保存的 Public 首败记录显示 parser 返回空映射。正文不复刻评测输入或断言。
- 解释：API 和后续 resolver 已存在，但一种公开要求的输入没有进入对象构造流程。保留历史 `behavior_drift` 标签，正文以 **B001** 支撑这一点；旧 CSV 的 B002/B003 引用不被静默重写。
- 工程启示：从各类公开输入跟踪到对象构造和后续调用，不能只检查导出名。

## 案例 2：tox 的公开入口绕过已有展开逻辑

- Task ID：`tox__factor_expression_core__hard3_001`。
- 当前公开契约：B001/B003 明确要求 `find_envs` 从 brace/factor expression 得到环境名。
- Pro：`find_envs` 第 102–113 行只收集 `expand_factors` 的非空 factor 分量；第 125–148 行仅在发现规定的冒号分隔符时生成该分量；第 151–159 行和后续代码已存在 factor/笛卡尔积展开逻辑。
- Flash：对应位置为第 96–107、119–138、141–145、162–192 行，关键调用条件相同。
- 保存的 Public 首败记录显示独立表达式返回空集合。正文不公开测试名称、样例值或断言。
- 解释：已有 helper，但公开入口把输入送入另一种语法上下文，在进入 helper 之前跳过。这是静态调用路径事实，不推断 agent 意图或信息遗失的原因。
- 工程启示：通过导出 API 验证完整调用路径和 helper 前置条件，不能把 helper 的存在当作行为完成。

## 讨论与结果的对应

| 讨论段落 | 现有证据 | 提出的方向及限制 |
| --- | --- | --- |
| 从公开接口追踪义务 | RQ2：Pro/Flash 77 次失败中 76 次 Public/Hidden 首败；两个案例 | 连接输入条件、实现路径和输出；未证明 obligation record 或 probes 能提分 |
| 分别验证交付边界与语义覆盖 | 四份案例通过 Build/Isolation；全体存在未交付和加载失败 | 在允许依赖且无 donor 的环境验证交付；不将 Isolation residual 少解释为源独立性已解决 |
| 成功后报告 footprint | RQ4：Pro/Luna 97 个共同成功任务 | correctness、relative size、copy fraction 分别报告；缩小后需再验证，不将尺寸解释为维护成本 |
| 用分组指导分析 | RQ3：Core/hard3 对比及 lift type 混杂 | 分层取样、匹配任务族；不将构建标签当成普遍因果解释 |
| 契约与分数可追溯 | §5.1：七题排除影响通过率和 all-fail 数量 | 争议、裁定、版本分别记录；原始分数与敏感性并列 |

## 机器可读索引

`chapter5_case_evidence.json` 记录四条案例的任务/模型/运行目录、历史运行身份、公开条款、代码位置和来源 SHA-256。路径是本地证据位置，不是公开数据仓库链接。

证据等级保持 **L1 assistant close-read**；未新增完整轨迹因果审查或独立人工一致性结果。新建议仍为未验证研究方向。
