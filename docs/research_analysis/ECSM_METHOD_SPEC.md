# ECSM 方法规范：Executable Closure-State Machine

## 0. 方法边界与当前实现状态

ECSM 是一个**显式状态机控制器**，目标不是生成更长的提示，而是把 feature lifting 中不可见的“完成程度”变成可执行、可更新、可审计的状态，并用该状态选择 expand、probe、prune 或 stop。

当前仓库已有 `harness/featureliftbench/featurelift_agent.py` 控制器脚手架：它会写 `closure_plan.md`、`dependency_manifest.json`，并支持 `inspect_file`、`copy_file`、`write_file`、`run_public_tests`、清理临时文件和 final check。但现有 manifest 是一次性文件列表；`prune_submission` 只删除缓存文件；final check 只验证 import、forbidden import 和 public tests。它还没有：逐义务风险、运行时状态依赖、反事实删除、失败 probe 记忆和受约束停止。

本规范把“已有脚手架”与“待实现 ECSM”分开：

- **已实现并可用于 pilot**：`experiments/ecsm_pilot/run_pilot.py` 的 ECSM prompt-protocol 原型；它要求 OpenHands 写 `workspace/ecsm_state.json`，并由 `analyze_pilot.py` 读取。
- **尚未实现、本文定义的正式方法**：由代码强制执行 state transition 和 stopping guard 的 native controller。pilot 中 prompt-protocol 的结果不能单独证明状态机机制有效。

## 1. 形式化问题

给定任务契约 (T)、公开源码 snapshot (R)、公开测试 (P) 和提交 (S)，Agent 要找到最小但行为完整的可执行闭包 (C^*\subseteq R\cup A)。其中 (A) 是允许创建的 adapter/替代实现。ECSM 在第 (t) 步维护状态 (s_t)，选择动作 (a_t)，接收静态或执行观测 (o_t)，再执行：

\[
s_{t+1}=U(s_t,a_t,o_t)
\]

它最小化：

\[
L(S)=L_{omit}(S)+\lambda L_{redundant}(S)+\mu L_{compute}
\]

其中 `omit` 表示缺少 API、依赖、资源、状态转移或行为分支；`redundant` 表示可以删除但仍保留的代码；`compute` 是 token、工具调用和墙钟成本。hidden tests 只用于最终评价，不能进入 state update。

## 2. State

持久化文件：`<agent_output>/state/ecsm_state.json`；OpenHands prompt 原型暂存于 `<workspace>/ecsm_state.json`。

### 2.1 顶层接口

```python
@dataclass
class ECSMState:
    schema_version: str
    task_id: str
    revision: int
    included_symbols: dict[str, IncludedSymbol]
    included_files: dict[str, IncludedFile]
    unresolved_references: dict[str, UnresolvedReference]
    transitive_dependency_candidates: dict[str, DependencyCandidate]
    runtime_global_state_dependencies: dict[str, RuntimeStateDependency]
    observed_behavior_evidence: dict[str, BehaviorEvidence]
    failed_probes: list[ProbeFailure]
    redundancy_estimates: dict[str, RiskEstimate]
    omission_risk_estimates: dict[str, RiskEstimate]
    behavior_obligations: dict[str, BehaviorObligation]
    action_history: list[ActionRecord]
    last_mutation_revision: int
    last_green_validation_revision: int | None
```

所有实体使用稳定 ID，例如 `symbol:featurelifted.normalize_body`、`file:repo/requests_cache/cache_keys.py`、`runtime:registry:stevedore.entry_points`。状态更新必须 append-only 记录 `action_history`；可覆盖估计值，但不能删除旧观测。

### 2.2 必需字段

#### included symbols/files

记录已经进入 submission 的符号和文件，而不是“看过”的文件。

```json
{
  "artifact": "submission/featurelifted/cache_keys.py",
  "source": "repo/requests_cache/cache_keys.py",
  "provides": ["featurelifted.create_key", "featurelifted.normalize_body"],
  "provenance": "copied|adapted|rewritten",
  "last_verified_revision": 17,
  "evidence_ids": ["probe:api-import:17"]
}
```

#### unresolved references

保存静态引用和执行时未解析引用。字段至少有：`origin`、`reference`、`kind`（import/symbol/resource/runtime-state/behavior）、`first_seen_revision`、`resolution_candidates`、`severity` 和 `status`。只读过引用所在文件不算 resolved；必须由 included artifact 或明确 adapter 覆盖。

#### transitive dependency candidates

保存静态 import/call/data 引出的候选边，字段为：`from`、`to`、`edge_type`、`static_confidence`、`runtime_observed`、`selected`、`rejected_reason`。静态图只生成候选，不能直接宣告 necessity。

#### runtime/global-state dependencies

保存 registry、plugin、entry point、class-construction、cache、environment/default config 和 dynamic import。字段为：`trigger`、`state_before`、`operation`、`state_after_expected`、`probe_id`、`observed`、`replacement`。例如 plugin registration 需要执行“注册前 → 注册动作 → 查询/调用后”的状态转移 probe。

#### observed behavior evidence

每条证据必须包含：`obligation_id`、`probe_id`、`probe_type`（API/public/contract/property/state-transition/isolation/deletion）、`command`、`revision`、`returncode`、`result_digest`、`covered_symbols`、`covered_runtime_dependencies`。仅写“tests pass”不是证据。

#### failed probes

记录失败 probe 的输入摘要、错误类型、堆栈 digest、涉及符号/文件、发生 revision、修复动作和是否已被后续成功 probe supersede。相同失败不能被重复探索抹掉。

#### redundancy estimates

对每个 artifact (x) 维护 `probability`、`impact`、`basis` 和 `last_updated_revision`。未经删除实验时只能是低置信度启发式；删除后所有必要 probe 仍通过，则 `P(redundant(x))` 至少提升到 0.95；任何必要 probe 失败则降到至多 0.05 并触发 restore。

#### omission-risk estimates

对每个义务 (o) 维护 `probability` 和 `impact`。最小启发式原型：

```text
p_omit(o) = clip(
    0.35 * no_successful_probe
  + 0.25 * unresolved_reference
  + 0.20 * runtime_or_resource_unobserved
  + 0.10 * source_to_submission_mapping_missing
  + 0.10 * recent_related_probe_failure,
  0, 1)
```

`impact` 取 `{1, 2, 4}`：普通行为、TASK 明确行为、导出 API/构建/隔离硬门。该公式只用于最小原型；论文不能把手写权重当学习贡献，必须做阈值和权重敏感性消融。

## 3. Actions

统一接口：

```python
class ECSMAction(Protocol):
    action_id: str
    type: Literal[
        "locate", "expand_dependency", "replace_dependency", "create_adapter",
        "execute_probe", "prune_dependency", "restore_dependency", "finalize"
    ]
    targets: list[str]
    expected_state_change: dict[str, Any]
    preconditions: list[str]
    estimated_cost: float
```

### 3.1 locate

输入 API/行为义务，输出 source symbol/file 候选及定位证据。它只能更新候选和 source mapping，不能把候选直接加入 closure。

### 3.2 expand dependency

把一个候选文件、符号、资源或运行时状态边加入 submission，并创建它引出的新 unresolved references。expand 必须说明被解决的义务。

### 3.3 replace dependency

用允许依赖或本地替代模块替换不允许/过大的第三方依赖。必须记录原语义、替代接口和差异 probe。

### 3.4 create adapter

创建边界 adapter，例如导出重命名、兼容签名、资源 loader、plugin facade。adapter 不是默认重写；必须绑定 source evidence 和 contract probe。

### 3.5 execute probe

执行 import/API/public/contract/property/state-transition/isolation/deletion probe。probe 的命令、输入摘要、revision 和结果必须写入 state。公开测试只是其中一种 probe。

### 3.6 prune dependency

在可恢复快照中删除一个 artifact 或 symbol，标记为 `tentatively_pruned`，随后强制执行 necessity probe set；在 probe 完成前禁止 finalize。

### 3.7 restore dependency

当删除导致任何必要 probe 失败时，从快照恢复，关联失败证据，并把该 artifact 标为必要。restore 后必须重跑受影响 probe，确认恢复有效。

### 3.8 finalize

只请求提交；真正提交由 stopping guard 决定。guard 返回全部满足的证据或机器可读拒绝原因，不接受模型自由文本覆盖。

## 4. State update

### 4.1 静态分析后

1. AST/import/resource scan 只写入 `transitive_dependency_candidates`。
2. 对 included 文件中出现但尚无 provider 的 import/name/resource 创建 `unresolved_references`。
3. dynamic import、registry API、entry-point 查询、module-level mutable singleton 命中时创建 `runtime_global_state_dependencies`，并把对应义务 omission risk 至少设为 0.5。
4. 静态可达不等于必要；不得直接降低 redundancy risk 到 0。

### 4.2 文件读取后

1. 记录 `source_read` action 和内容 digest。
2. 新发现的定义/引用更新 candidate graph。
3. 只有当 source 定义被映射到 submission artifact 时才更新 included state。
4. 重复读取相同 digest 不改变 closure state，并增加 `repeat_without_state_change` 计数，供 controller 降低该动作优先级。

### 4.3 测试或 probe 后

1. 成功：添加 `BehaviorEvidence`，仅降低被该 probe 明确覆盖义务的 omission risk。
2. 失败：添加 `ProbeFailure`，把异常中的缺符号/模块/资源写入 unresolved；相关 omission risk 上升。
3. public success 不会自动把所有 behavior obligations 标成 covered。
4. 每次 submission mutation 使旧 probe 变 stale；只有 revision 不早于 `last_mutation_revision` 的绿色 probe 可参与 stopping。

### 4.4 删除实验后

1. prune 前保存 artifact digest 和 restore snapshot。
2. 删除后重跑 necessity probe set：import/API、受影响 behavior probes、public、isolation。
3. 全部通过：接受删除，更新 included 和 redundancy estimate。
4. 任一失败：立即 restore，记录 failure→artifact 因果边，再重跑失败 probe。
5. 删除期间超时/工具错误属于 inconclusive，必须 restore，不能当作删除成功。

## 5. Stopping criterion

设当前 revision 为 (r)。只有同时满足以下条件才能提交：

1. TASK/metadata 中每个输出 API 都有 `included_symbol`，且在 revision ≥ `last_mutation_revision` 的 import/signature probe 中成功。
2. 所有 `severity=hard` unresolved references 已关闭；`severity>=medium` 的 unresolved 数量为 0，或有经过 probe 的明确 replacement。
3. public tests 在最后一次 mutation 后通过。
4. 每个 included behavior family 至少有一个非平凡 contract/property/state-transition probe；公开测试可计入，但每个 family 不能只靠同一个 happy-path public case。
5. 所有 runtime/global-state dependency 均被执行观测或 adapter probe 覆盖。
6. isolation/forbidden import 检查通过。
7. 没有 pending prune；每个 prune 均有 keep 或 restore 证据。
8. `max(p_omit(o) * impact(o)) < 0.15`，且总 omission loss 小于预注册阈值 0.5。
9. 所有候选动作的估计净价值 `risk_reduction - λ*cost <= 0.05`；否则继续最高价值动作。
10. 剩余预算足以保存 state、运行 final validation 和提交；如果预算先耗尽，状态是 `budget_exhausted`，不是 `finalize_success`。

因此 `public pass`、`FinishAction` 文本或“已查看主要文件”都不是合法停止依据。

## 6. Algorithm

```text
algorithm ECSM(T, R, P, budget):
    state ← initialize_state(T)
    obligations ← parse_api_and_behavior_obligations(T)
    state.behavior_obligations ← obligations

    # 1. initialize closure / locate
    for obligation in obligations:
        candidates ← LOCATE(obligation, R)
        UPDATE(state, locate, candidates)
    RUN_STATIC_SCAN(state, candidates)
    UPDATE_RISKS(state)

    while budget.remaining > final_validation_reserve:
        # 2. expand
        if exists high_risk_unresolved(state):
            target ← argmax_candidate(expected_risk_reduction / estimated_cost)
            action ← choose(expand_dependency, replace_dependency, create_adapter, target)
            observation ← EXECUTE(action)
            state ← UPDATE(state, action, observation)
            RUN_STATIC_SCAN(state, changed_artifacts(observation))
            UPDATE_RISKS(state)
            continue

        # 3. executable validation
        uncovered ← obligations_without_fresh_evidence(state)
        if uncovered is not empty or validation_is_stale(state):
            probe ← synthesize_probe(highest_impact(uncovered), state)
            observation ← EXECUTE(probe)
            state ← UPDATE(state, execute_probe, observation)
            UPDATE_RISKS(state)
            if observation.failed:
                continue

        # 4. counterfactual pruning
        prune_target ← argmax_redundancy_with_safe_probe_set(state)
        if prune_target exists:
            snapshot ← SNAPSHOT(prune_target)
            state ← UPDATE(state, prune_dependency, snapshot)
            deletion_results ← RUN_NECESSITY_PROBES(prune_target, state)
            if all_conclusive_pass(deletion_results):
                ACCEPT_DELETE(prune_target)
                state ← UPDATE(state, prune_dependency, deletion_results)
            else:
                RESTORE(snapshot)
                restore_result ← rerun_failed_probes(deletion_results)
                state ← UPDATE(state, restore_dependency, restore_result)
            UPDATE_RISKS(state)
            continue

        # 5. risk comparison
        stop_loss ← expected_omission_loss(state)
        best_action, continue_value ← best_expected_action(state)
        if continue_value > 0.05:
            observation ← EXECUTE(best_action)
            state ← UPDATE(state, best_action, observation)
            UPDATE_RISKS(state)
            continue

        # 6. stopping
        guard ← CHECK_STOPPING_CRITERION(state)
        if guard.passed:
            final_result ← RUN_FINAL_VALIDATION(state)
            state ← UPDATE(state, execute_probe, final_result)
            if final_result.passed and CHECK_STOPPING_CRITERION(state).passed:
                PERSIST(state)
                return FINALIZE(submission, state.digest)
        else:
            action ← action_for_highest_priority_guard_failure(guard, state)
            observation ← EXECUTE(action)
            state ← UPDATE(state, action, observation)

    PERSIST(state)
    return BUDGET_EXHAUSTED_WITHOUT_FINALIZE
```

## 7. 与当前仓库的集成

### 7.1 新文件

| 文件 | 类/函数 | 责任 |
|---|---|---|
| `harness/featureliftbench/ecsm.py` | `ECSMState`, `ECSMStateStore`, `ECSMController`, `StoppingDecision` | schema、原子持久化、风险更新、动作选择、停止 guard |
| `harness/featureliftbench/ecsm_static.py` | `scan_dependencies()`, `scan_runtime_state_candidates()` | AST/resource/dynamic-state 候选，不宣告 necessity |
| `harness/featureliftbench/ecsm_probes.py` | `ProbeSpec`, `ProbeResult`, `run_probe()`, `run_necessity_probe_set()` | 隔离执行和结构化证据 |
| `harness/featureliftbench/ecsm_prune.py` | `ArtifactSnapshot`, `prune()`, `restore()` | 反事实删除与恢复 |
| `harness/tests/test_ecsm_state.py` | state/update/serialization tests | schema 与单调证据测试 |
| `harness/tests/test_ecsm_controller.py` | stopping/action tests | public-only 不可停止、失败删除必须恢复 |

### 7.2 修改现有文件

1. `harness/featureliftbench/featurelift_agent.py`
   - `FeatureLiftAgentConfig` 增加 `controller="legacy|ecsm"`、`omission_threshold`、`compute_lambda`。
   - `run()` 在 `_write_state_files()` 后构造 `ECSMStateStore` 和 `ECSMController`；不再按固定 phase 一次性执行。
   - `_action_schema()` 加入本规范八种 action；旧 action 作为底层 executor，不作为 controller action。
   - `_execute_action()` 增加 ECSM action→底层工具映射。
   - `_final_check_action()` 返回 `ProbeResult`，并调用 `controller.can_finalize()`；模型不能绕过。
   - `_prune_submission_action()` 不能再只清缓存；正式 ECSM 使用 `ecsm_prune.prune/restore`。
   - `_append_tool_observation()` 每次观测后调用 state update，记录 revision/digest。
2. `harness/featureliftbench/agent_adapters.py`
   - `FeatureLiftAgentAdapter.build_command()` 透传 `--controller ecsm` 和阈值。
3. `harness/featureliftbench/agent_config.py` 与 `harness/config/agents.toml`
   - 增加 `featurelift_controller`、`featurelift_omission_threshold`、`featurelift_compute_lambda`。
4. `harness/featureliftbench/openhands_runner.py`
   - 已加入 `FEATURELIFTBENCH_OPENHANDS_PROMPT_APPEND_FILE`，供所有 pilot arm 在同一 OpenHands runtime 注册条件；正式 ECSM 不依赖这个 prompt hook。
5. `harness/featureliftbench/llm_usage_proxy.py`
   - 已加入 `FEATURELIFTBENCH_OPENHANDS_TOTAL_TOKEN_LIMIT`，各 arm 使用同一硬上限；最多允许最后一次已发出的调用产生一次-call overshoot，之后拒绝转发。
6. `experiments/ecsm_pilot/analyze_pilot.py`
   - 优先读取 `included_source_files`；没有显式 state 时只报告可审计的 hash/line provenance，无法确认则 closure P/R/F1 为 NA，不把未知当 0。

### 7.3 最小 controller 接口

```python
class ECSMController:
    def propose(self, state: ECSMState, budget: Budget) -> ECSMAction: ...
    def update(self, state: ECSMState, action: ECSMAction, observation: Observation) -> ECSMState: ...
    def risk(self, state: ECSMState) -> RiskReport: ...
    def can_finalize(self, state: ECSMState, budget: Budget) -> StoppingDecision: ...

class ECSMStateStore:
    def load(self) -> ECSMState: ...
    def commit(self, previous_revision: int, state: ECSMState) -> str: ...  # returns digest
```

`commit` 必须先写临时文件再原子替换，并拒绝 revision 回退。这样工具中断后可以恢复，而不会把部分 state 当完成状态。

## 8. 与 baseline 的实质区别

| Baseline | 它提供什么 | ECSM 增加的不可替代机制 |
|---|---|---|
| strong prompt | 一次性工作要求 | 机器可读状态、转移、证据 freshness 和不可绕过 stopping guard |
| checklist | 离散完成项 | unresolved/risk 随观测更新；checklist 不选择 expand/prune 动作 |
| RepoMap | 文件/符号定位 | RepoMap 不表示 included closure、运行时状态或 necessity |
| static dependency graph | 静态候选边 | ECSM 把静态边当候选，必须用执行观测确认；可表示 registry/resource/dynamic state |
| more context | 更多源码可见性 | ECSM 约束决策和停止；同样上下文下仍可比较 |
| reflection | 再生成一次文本判断 | ECSM 要求新 executable evidence；无 state change 的 reflection 不降低风险 |
| copy-first | 高 recall 初始 closure | ECSM 还包含可恢复删除、necessity probe、risk comparison 和提交 guard |

ECSM 不是普通 RAG：它不以“检索更多片段”为核心；不是普通依赖图：图只生成候选；不是普通 multi-agent：没有通过角色拆分制造机制贡献。

## 9. 必要消融与失败条件

正式实验至少包含：

1. `ECSM - explicit state`：保留 prompt 和 probes，但不持久化状态。
2. `ECSM - runtime-state fields`：只保留静态 dependency state。
3. `ECSM - counterfactual prune`：不做删除验证。
4. `ECSM - stopping guard`：允许 public pass 后自行结束。
5. `ECSM risk weights shuffled/fixed threshold sensitivity`。
6. 同 token/step 上限的 Strong Prompt、Static Hint、Oracle Locate、Oracle Closure、Copy-first。

如果 ECSM 只增加 token/tool calls，hidden Pass@1、public-hidden gap、closure F1 和 final score都没有达到 `PILOT_DECISION_RULES.md` 的预注册阈值，则方法失败；不能用“state 更可解释”替代效果证据。
