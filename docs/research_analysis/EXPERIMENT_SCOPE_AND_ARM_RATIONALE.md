# 七组实验的作用与规模策略

## 1. 决策结论

七个实验组构成的是一套**机制诊断矩阵**，不是七个都需要在 Python-150 上跑满的最终 leaderboard 方法。

首轮固定为 10 tasks × 7 arms × 1 seed = 70 cells。它的目标是区分 localization、dependency closure、behavior validation、expand–prune 和 stopping/workflow 五类解释，而不是估计全量平均性能或做显著性宣称。

不建议直接运行 150 × 7 = 1,050 个新 run：

1. Oracle Locate 和 Oracle Closure 是诊断性上界，不是可部署方法，没有必要在全量任务上反复测量。
2. 如果 Strong Prompt 已经接近 ECSM-Prompt，或者 Oracle Locate 已经接近 Oracle Closure，前 10 题就足以触发停止/转向，后续 980 个 run 没有研究价值。
3. 每个 cell 有 6M total-token guard；1,050 cells 的理论预算上限是 6.3B tokens。实际消耗会低于上限，但仍不应在机制尚未成立前投入。
4. 150 个任务中存在不同环境历史和 62 条 evaluator/environment artifact；先在统一环境的小矩阵建立因果方向，证据更干净。
5. 七臂全量会把“机制诊断”和“最终方法效果”混在一起，反而削弱论文叙事。

## 2. 七个 arm 的角色

| Arm | 改变的变量 | 主要问题 | 是否需要扩到全量 |
|---|---|---|---|
| Standard | 无干预 | 统一环境下的当前基线 | 最终可扩，但首轮只跑分层任务 |
| Strong Prompt | 工作要求更明确，无新信息 | 是否只是 prompt mismatch | 最终主对照，值得扩 |
| Oracle Locate | 给正确入口位置 | localization 上限 | 仅诊断子集 |
| Static Closure Hint | 给 AST import 候选 | 普通静态依赖图是否足够 | 视 pilot 结果保留为简单基线 |
| Oracle Closure | 给 required files 和 target API | closure-selection 上限 | 仅诊断子集 |
| Copy-first then Prune | recall-first expansion + 删除验证 | expand–prune 是否可行 | 作为方法消融，按信号扩展 |
| ECSM-Prompt | 显式 state、probe、risk、guarded stop 的结构化提示协议 | workflow/state 协议是否有增量价值 | 通过 go gate 后再决定是否实现 Native ECSM Controller |

Oracle arms 不能作为最终方法结果：它们读取任务构造时的 oracle manifest，只用于测量“定位正确”和“闭包已知”的上限差异。当前非 Oracle 候选是 `ECSM-Prompt`，它仍不是 Native ECSM Controller。

## 3. 分阶段运行计划

### Phase A：基础设施 smoke

- 规模：2 tasks × 7 arms = 14 cells。
- 任务：`boltons__iterutils_core__001`、`schema__nested_validate_core__hard3_001`。
- 目标：验证 condition provenance、相同预算/工具、token guard、Docker evaluator、submission schema 和分析器。
- 允许结论：只能判断实验实现是否正确，不能判断机制。

### Phase B：四题资源门禁

- 规模：4 tasks × 5 arms = 20 cells。
- 任务：`pluggy__hook_specs_core__001`、`pydantic_v1__validation_error_core__001`、`lark__grammar_loader_core__001`、`websockets__handshake_parse_core__001`。
- arms：Standard、Strong Prompt、Oracle Locate、Oracle Closure、ECSM-Prompt。
- 目标：只判断是否值得投入剩余 36 cells。阈值与 `purpose: resource_allocation_only` 以 `PILOT_DECISION_RULES.md` 为准。
- 允许结论：只能报告资源门禁是否触发，不能据 4 题正式否定或确认机制。

### Phase C：补齐冻结的 70-cell Pilot

- 规模：补齐剩余 36 cells，使完整矩阵达到 10 tasks × 7 arms × 1 seed = 70 cells。
- 前置条件：Stage B 资源门禁触发。
- 统计：task-level paired wins/losses、绝对任务数和预注册阈值；不做显著性宣称。
- 若门禁未触发：合法停止在 34 cells，只报告“当前资源门禁未触发”。

完整 Pilot-10 不是为了代表 Python-150，而是为了最大化机制可区分性。任务和分层在看结果前冻结，避免事后挑案例。

### Phase D：方向确认集

只有 Phase B 通过 go gate 才进入。建议冻结 24–30 个任务，覆盖更多仓库，但不再跑全部七组：

- 必跑：Standard、Strong Prompt、Native ECSM（仅在实现并验证 controller 后）。
- 简单机制对照：根据 pilot 选择 Static Hint 或 Copy-first 中表现更强的一组。
- Oracle Locate/Closure：仍只保留原 10–12 个诊断任务，不扩到 24–30 个。
- seeds：先补第二 seed 检查方向稳定；论文定稿前对最终主对照补足预注册 seeds。

如果 Native ECSM Controller 尚未实现，Phase D 不能用 ECSM-Prompt 冒充正式方法。必须先完成 `ECSM_METHOD_SPEC.md` 中 state transition、probe freshness 和 stopping guard。

### Phase E：Python-150 外部有效性

不默认执行七臂全量。只有以下条件同时成立才考虑扩大：

1. ECSM-Prompt 相对 Strong Prompt 达到 `PILOT_DECISION_RULES.md` 的最低 hidden/gap 门槛，并由后续 Native ECSM 确认；
2. 至少一个 closure strata 和一个 behavior/global-state strata 获益；
3. token 和 tool-call 成本未超过预注册 guard；
4. 24–30 题确认集方向稳定；
5. benchmark environment artifact 已清理或有一致的 exclusion/reevaluation protocol。

即使进入 Phase E，也优先选择：

- 使用已有 Python-150 frozen Standard 结果做描述性背景；
- 在全量上只运行最终 ECSM 或 ECSM/Strong Prompt 两组；
- Oracle arms 不进入全量；
- Static/Copy-first 只在对应消融子集运行。

## 4. 当前 10-task 分层

| Stratum | Tasks | 作用 |
|---|---|---|
| explicit/static closure | `requests_cache`, `pydantic_v1`, `coverage` | 区分 Locate、Static Hint、Oracle Closure |
| behavior/registry contract | `pluggy`, `celery` | 检查 closure 已知后的行为与 dispatch 残差 |
| parser/resource/deep closure | `lark`, `websockets`, `sqlparse` | 检查静态文件图之外的 parser/resource/state 义务 |
| sanity controls | `boltons`, `schema` | 检测协议或 prompt 是否造成简单任务回退 |

## 5. 扩展与停止规则

| Pilot 观察 | 下一步 |
|---|---|
| Strong Prompt ≈ ECSM-Prompt | 暂停 Native ECSM 投入；优先报告 prompt/workflow baseline |
| Oracle Locate ≈ Oracle Closure ≫ Strong | 转向 localization；不扩 ECSM |
| Oracle Closure ≫ Oracle Locate | 继续 closure-state/ECSM 方向 |
| Static Hint ≈ Oracle Closure | 静态依赖图已足够；ECSM 创新空间弱 |
| Copy-first 提升 hidden、ratio 恶化 | 实现 counterfactual necessity verifier，再决定是否扩 |
| ECSM-Prompt 提升 hidden 但 >1.5× compute | 先做效率/状态消融，不扩任务数 |
| ECSM-Prompt 达到 hidden、gap、closure/compactness 和 compute 合取门槛 | 再实现 Native ECSM，并进入 24–30 题确认集 |
| 所有组无提升 | 优先审计 behavior contract、工具和环境；停止方法叙事 |

精确阈值以 `PILOT_DECISION_RULES.md` 为准，本文件只规定实验规模和各 arm 的科学角色。

## 6. 论文报告边界

- 70-cell pilot 可以决定研究方向，但不能支持“在 Python repository feature lifting 上普遍有效”的最终结论。
- Oracle arms 的结果报告为 mechanism ceiling，不计入最终方法平均分。
- 所有主比较保持同模型、同总 token guard、同最大步骤、同工具、同温度、同 public-only 权限和同提交协议。
- 同时报告 raw、environment-excluded 和 contract-clean 口径。
- 未运行的 cell 保持 NA，不能按失败或零分填充。
