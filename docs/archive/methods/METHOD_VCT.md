# Verified Completion Termination（VCT）

> **Status: archived · Last verified: 2026-09-02**
> 本文件是 **VCT** 的唯一规范。不是 Official Main，数字不进 Python-200' 主表。
> 规格自带的离线 kill gate 已触发：stall 终止在任何参数下都无法做到 pass 非劣。
> **不要实现组件 2，不要跑实臂。** 结论见下节。

## 离线 Kill（2026-09-01）

规格要求先做零模型成本的离线标定，标定已完成并**否决了组件 2**。

标定用去掉 Gate 的上界测试：Gate 是额外的合取项，要求它只会推迟停止、只会减少
节省，因此去 Gate 的节省是 VCT 的上界。脚本
`harness/scripts/calibrate_vct_stall.py`，报告
[`reports/paper_analysis/vct_calibration/vct_stall_calibration.md`](../../../reports/paper_analysis/vct_calibration/vct_stall_calibration.md)。

138 道 Phase 1 金标通过题、49 个 `(K, FLOOR)` 网格点：

| 网格点 | 节省合计 | 丢 pass | 其中停在 `T*` 前 | 其中停在坏树上 |
| --- | ---: | ---: | ---: | ---: |
| K=100K / FLOOR=0 | 65.1% | 52 | 52 | 0 |
| K=200K / FLOOR=1500K（达标节省中丢最少） | 26.9% | 14 | **14** | **0** |
| K=500K / FLOOR=2000K（最保守） | 14.9% | 3 | 3 | 0 |

**没有任何网格点满足丢 pass ≤ 1。** 而且在达到 25% 节省的所有点上，丢掉的 pass
**全部**来自"停止时刻还不存在任何能过的树"，停在过关后坏树上的是 **0** 道。

结构 Gate 只能挡住后一类。后一类是空集，所以 **Gate 一道也救不回来**。

机制：`required_api` 的表面在骨架阶段就闭合了，远早于行为正确。一个由结构闭合
把门的 stall 停止，必然在 `T*` 之前就触发。**结构闭合不是完成的代理。**

这与本项目其它臂撞的是同一面墙：Main 信封内所有合法信号要么是结构性的（过早
闭合），要么是 Agent 自撰的（继承它自己的盲点），**没有合法的行为信号**。同一
面墙的其它证据：checkpoint oracle 失败题 `0/51`、Phase 3 合法信号组合
AUC 0.63–0.67、以及 8 道 Hidden 首败里 4 道的义务根本不可从契约恢复
（[clause_narrowing](../../../reports/paper_analysis/python200_hard_main_20260829/clause_narrowing/clause_narrowing.md)）。

组件 1（完成下限）未被本标定否决，但它只针对 pass，**不省 token**，因此单独
存在无法达成本臂目标。若要单独筛选组件 1，必须重写目标与 kill line。

以下为原始规格，保留作为设计记录。

---

> 原目标：**pass 非劣 + token 显著下降**，不是抬 pass。不要叠
> Public-feedback、CGVL、Spec-adversarial、2M cap、repair 轮，也不要在离线标定
> 通过前跑任何模型。

## 目标设定（先纠正口径）

不追求抬 pass。checkpoint oracle 已经证明失败题上**一棵能过的树都没有**
（Flash 51 道 replay-ok 失败、385 棵独特树、`任一独特树 Functional Pass = 0/51`，
见 [TOKEN_UTILITY.md](../snapshots/TOKEN_UTILITY.md)）。因此任何"更早停"或"挑更好的中间树"
的机制都不可能救回失败题。**pass 的提升不可能来自终止机制**，把它写成目标就是
自欺。

VCT 的唯一主张是成本：**同等能力下把 token 砍掉一大块**。

## 机会在哪：浪费不在探索段

Flash 本地 Main-200、138 道有 Phase 1 金标的通过题：

| 事实 | 数值 |
| --- | --- |
| 最早充分树出现位置 `T*/T` 中位数 | **0.40** |
| 过关后仍消耗的 token 中位数 | **0.75M（占总量 60%）** |
| 一半以上 token 花在过关之后的题 | 87/138 |
| 过关后 token 里"跑自测" | **48%** |
| 过关后 token 里"继续改包" | 6%（中位数 0） |
| 过关后仍在自测的题 | 99% |

机制是 `TOKEN_UTILITY.md` 的原话：**"Agent 看不见 hidden，所以不会停"**。它用
自编用例和上游测试代替看不见的 hidden，追一个拿不到的安心感。

## 为什么 Lite V1 砍错了

Lite V1 在 Python-200 上是 Main −6.5 pp（API）/ −9.0 pp（本地），token −50.3% /
−32.1%。预算不是混淆项：`deepseek_main_vs_lite_v1_20260817.json` 记录
`method_compared.budget = main_120_step_plus_repair`，它就是 120 步。

混淆项是 prompt。Lite 的 prompt 要求"立刻可导入、约第 6 步给出 API 骨架、约第 12
步跑结构检查、**用掉约 70% 预算后停止广泛探索**"（见
[reference/CONTRACT_CLOSURE_GATE.md](../../reference/CONTRACT_CLOSURE_GATE.md)）。这是
催促型 prompt，它压缩的是**探索段**——而探索段是正确率所在。省下的 token 和丢掉
的 pp 同源。

**VCT 不加任何进度压力，只在尾巴上终止。**

## 与已 Kill 臂的差别

| 臂 | 结果 | 死因 | VCT 的不同 |
| --- | --- | --- | --- |
| Lite V1（结构门禁 + 催促 + repair） | −6.5~9.0 pp，token −50% | 催促 prompt 压缩探索 | 全程零进度压力，不提早期检查点 |
| V1（Main + 2M cap） | Core-12 8/12 → 4/12 | 统一先验截断，杀掉晚通过题 | 逐题条件触发，不设先验 token 上限 |
| Phase 3 verification-aware stop | 组合 AUC 0.63–0.67 | 用 novelty 预测 `T*` | 只用**已验证事实**，不做预测 |
| Pre-submit audit | 6/12 vs 8/12 | 模型自评清单 | harness 侧机械检查，模型不参与判定 |
| Rescue+ v2.1 / v2.2 | 3/12、2/12 | 第二个模型阶段从未奏效 | **无 repair 轮，无第二阶段** |
| Best-so-far checkpoint | 0/51 | 失败题没有过关树 | 不挑树，只决定何时停 |

## 定义

同一 128k / 120-step / No-Hint / 无 token cap 的 Main 信封。Prompt 不变，不加
任何时间表或催促语。只加两件 harness 侧机械机制。

| 维度 | Main | VCT |
| --- | --- | --- |
| Prompt | `standard` | **同左，不加附录** |
| Context / reserved | 131072 / 8192 | 同左 |
| Max steps | 120 | 同左 |
| Total token cap | 无 | 同左（无先验 cap） |
| `public_tests/` / Hidden | 不挂载 | 不挂载 |
| 结构门禁 | 无 | `flb-contract-check --structure-only`（harness 侧计算） |
| 终止 | agent finish 或步数耗尽 | 增加 VCT stall 终止 |
| Runtime `ablation_arm` | `main` | `vct` |

### 组件 1：完成下限（finish floor）

Gate 未闭合时拒绝 `finish`，把机械发现原文返回给 Agent，**在同一 primary 阶段
继续**，不开 repair 轮。

Gate 闭合定义（全部来自 `metadata.public_spec`）：`required_api` 每个 path 可
导入、kind 正确、callable 签名匹配、包可编译、无 forbidden import。

`finish` 拒绝**最多 2 次**，之后放行。原因见
[`reports/paper_analysis/python200_hard_main_20260829/clause_narrowing/`](../../../reports/paper_analysis/python200_hard_main_20260829/clause_narrowing)：
已确认存在 `required_api` 声明与隐藏断言不相容的题（installer 声明
`-> 'str | None'` 却要求 `raises(ValueError)`；zope 声明 `-> bool` 却要求成功时
返回假值）。这类题上 Gate 可能永远关不上，无上限拒绝会烧光预算。

### 组件 2：stall 终止

在 token 位置 `t` 终止，当且仅当三条**同时**成立：

1. `t ≥ FLOOR`（绝对 token 下限）
2. 当前 `submission/featurelifted/` 树的 Gate 闭合
3. `t − t_last_unique_tree ≥ K`

`t_last_unique_tree` 是最近一棵**内容哈希不同**的 `featurelifted` 树出现的位置。
若后续编辑把结构改坏，Gate 重新打开，规则不再满足，Agent 继续跑。

条件 3 不是拍的：Phase 3 试遍合法信号后，**唯一明显强于时间对照的就是"距上次
独特树多久"**——0.5–1.5M 带里 Flash AUC 0.79，而 `tokens_so_far` 只有 0.57。
条件 2 与 3 都是已发生的事实，不是对 `T*` 的预测。

## 离线标定（强制前置，先于任何模型调用）

`K` 与 `FLOOR` **不允许拍**。必须在已有 Flash 轨迹上重放标定，并在实跑前冻结。

数据与机械件都已存在：Phase 1 金标
（`token_utility_phase1_20260818.json`，138 道通过题的 `T*`）、全独特树评测
（`checkpoint_oracle_flash_fail_all_unique_20260820.json`）、重放脚本
`harness/scripts/analyze_token_utility_phase1.py`。结构 Gate 是确定性离线检查，
可逐棵独特树重算，**不需要模型调用**。

对每个候选 `(K, FLOOR)` 输出：

| 指标 | 定义 |
| --- | --- |
| `pass_lost` | 原本 Functional Pass、但规则触发时刻的树不过的题数 |
| `token_saved` | 成对 token 相对削减比例中位数 |
| `late_pass_truncated` | `T*` ≥ 2M 的 7 道题里被提前截断的数量 |
| `frozen_broken_tree` | 规则在"改坏后尚未恢复"的树上触发的题数 |

**离线 kill gate：** 若不存在任何 `(K, FLOOR)` 同时满足
`pass_lost ≤ 1/138` 且 `token_saved ≥ 25%`，**不跑实臂**。这一步零模型成本，
必须先过。

## 三臂设计

| 臂 | 内容 | 预期 |
| --- | --- | --- |
| A | 同日 Main 对照 | 基线 |
| B | A + 完成下限（组件 1） | pass 非劣；token 可能略升 |
| C | B + stall 终止（组件 2） | pass 与 B 持平；token 显著降 |

B 单独存在是为了归因：把"拒绝 finish"和"提前终止"分开，否则 C 的任何变化无法
归因。已有的 `contract_closure_budget_control` 不能替代 A，它是 64k / 45 步信封。

切片：12 题同日配对起步。题单在实现时冻结并写入本文件。

## 读出与预注册 Kill line

主指标：`eval/result.json` 的 `functional_gate`（成对），以及成对 billed token
削减比例。

| 条件 | 动作 |
| --- | --- |
| 离线标定无可行 `(K, FLOOR)` | **Kill，不跑模型** |
| B 相对同日 A 少 ≥2 题 | Kill 组件 1 |
| C 相对同日 A 少 ≥2 题 | Kill |
| C 的 token 削减 < 15% | Kill，机制不值得 |
| C：pass Δ ≥ 0 且 token 削减 ≥ 25% | 扩到更大配对切片 |

**n=12 只能筛选，不能建立非劣性。** 12 题上的 pass Δ ≥ 0 不是非劣性证据，
扩面后才谈。不得把 12 题结果写进 Python-200' 主表。

## 过程指标

落盘 `agent/vct.json`：

| 指标 | 含义 |
| --- | --- |
| `gate_closed_at_tokens` | Gate 首次闭合的 token 位置 |
| `gate_reopened_count` | 闭合后被改坏的次数 |
| `finish_rejections` | 拒绝 `finish` 的次数（上限 2） |
| `stop_reason` | `vct_stall` / `agent_finish` / `steps_exhausted` / `error` |
| `tokens_at_stop` / `total_tokens` | 终止位置与总量 |
| `unique_trees` | 独特 `featurelifted` 树数量 |
| `tokens_since_last_unique_tree_at_stop` | 终止时的 stall 长度 |

## 公平性边界

Gate 只由 `metadata.public_spec` 计算，这是 TASK.md 里 Agent 已经拿到的信息，
机械重述不构成新信息。**不得**挂载 `public_tests/`、读 hidden、读
`evaluation_spec`、读 reference solution 或回传 evaluator 结果。这条边界与
`contract_closure_gate` 的 `information_condition` 一致，也是 VCT 与 RQ6
Public-feedback 的根本区别：后者挂载了 Agent 在 Main 下看不到的测试，属于信息
消融，不是可用方法。

## 与既有预注册的冲突（必须显式声明）

[TOKEN_UTILITY.md](../snapshots/TOKEN_UTILITY.md) 的"不要做"里写明：**不写 stop 规则、不做
verification-aware stopping**。VCT 组件 2 与该条冲突。

推翻的理由必须写进论文，而不是默默改文档：当时的结论针对的是**用轨迹信号预测
`T*`**（组合 AUC 0.63–0.67，不足以支撑）。VCT 不预测 `T*`，它要求两个已验证
事实同时成立，并且用离线重放先算出 `pass_lost` 的实际代价。若离线标定给不出
`pass_lost ≤ 1/138 且 token_saved ≥ 25%`，则原预注册结论维持，本臂作废。

## 已知风险

1. Flash 有 **7/138** 道通过题的最早充分树在 2M 之后。`FLOOR` 必须由标定给出，
   不能让 stall 在这些题上提前触发。
2. **46%** 的题过关后仍会长新树，其中有改坏再恢复的（isort 0.90M 已过、改坏、
   1.49M 才恢复）。`K` 过小会把坏树冻住，`frozen_broken_tree` 必须报。
3. 组件 1 在 `required_api` 本身有缺陷的题上会白烧预算，故设 2 次拒绝上限。
4. 标定只有 Flash 一个模型的金标。Qwen 过关后重复读 51%、Flash 11%，
   `TOKEN_UTILITY.md` 明确要求分层。**跨模型前必须重标定**，不得复用 Flash 的
   `(K, FLOOR)`。

## 论文可用句（仅在离线标定与 12 题筛选都通过后）

> 用两个可机械验证的条件——公开契约结构闭合，以及此后一段无新提交产物的停滞
> ——替代固定预算上限，在跨模块功能抽取上保持功能通过率不变而显著降低 token
> 消耗。
