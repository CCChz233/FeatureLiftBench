# Public Contract Closure Gate：2026-08-10 实验记录

> **Status: archived · Last verified: 2026-08-17**
> 过程记录，不是当前协议。Rescue+ 已停，见
> [ContractClosureGate_LiteRescuePlus_20260816.md](ContractClosureGate_LiteRescuePlus_20260816.md)。

## 1. 今天解决的问题

本轮工作从 Agent 失败分析出发，聚焦一个具体问题：Agent 经常完成了大部分实现，
但没有逐项闭合公开 API 契约，最终因为缺 API、签名、成员、异常或依赖问题失败。

最初方案 `contract_closure_gate` 要求 Agent 在同一主轮中：

1. 实现代码；
2. 编写覆盖全部公开 `Bxxx` 条款的行为 case；
3. 运行确定性结构检查和行为证据检查；
4. 对可操作缺口执行一次限额 repair；
5. 始终运行正式私有 evaluator。

该方法不读取 evaluator、隐藏测试或参考答案。`PUBLIC_CONTRACT.json` 只从
`metadata.public_spec` 单向生成，因此它属于公开规格的机器可读重述，不是作弊。

## 2. Full Gate 的初步结果

在三个历史 API 失败任务上，Full Gate v2 得到 2/3 Functional Pass，但消耗
9,297,148 token，约为历史 Main 的 2.6 倍。Token 构成中约 98% 是 prompt，
说明主要开销不是模型回答过长，而是 OpenHands 在多轮中反复携带不断增长的历史。

轨迹进一步显示，强制编写和调试完整行为 case 会占用大量步骤与上下文，而这些
Agent 自写测试只是软证据，不能替代正式 evaluator。

## 3. 今天实现的 Lite 方法

新增独立实验臂 `contract_closure_gate_lite`，保留确定性结构闭合，移除强制行为
case。其执行顺序为：

1. Agent 根据公开规格实现 `submission/featurelifted/`；
2. Agent 运行 `./flb-contract-check --structure-only --summary`；
3. Harness 在隔离环境中复查编译、导入、API 路径、kind、members、签名和禁用依赖；
4. 只有结构缺口才触发一次 repair；
5. 无论门禁结果如何，都运行正式私有 evaluator。

默认低 token 配置：

- context window：65,536；
- output reserve：8,192；
- primary：最多 2,000,000 token、45 OpenHands steps；
- repair：最多 500,000 token、10 OpenHands steps；
- 单条 observation：最多 16,000 字符；
- repair 与 primary 分开记账。

同时扩展了使用量代理，记录 DeepSeek 返回的：

- `prompt_cache_hit_tokens`；
- `prompt_cache_miss_tokens`；
- `effective_uncached_prompt_tokens`；
- cache hit rate。

缓存指标会进入 `usage.json`、suite 汇总和
`run.json.contract_closure.usage_totals`。Raw token 与缓存后输入分开报告，避免把
价格优化误写成算法 token 优化。

## 4. 真实 API 三题结果

模型为 `deepseek/deepseek-v4-flash`，Agent 和 evaluator 均使用 Docker。Lite
方法三题全部通过正式 evaluator。

| Task | Full Gate v2 | Lite | Token 降幅 |
| --- | ---: | ---: | ---: |
| `pytest__skipif_eval_core__001` | Pass / 2,467,813 | Pass / 493,568 | 80.00% |
| `pytest__fixture_resolve_core__001` | Fail / 3,128,126 | Pass / 960,316 | 69.30% |
| `rich__markup_parse_core__001` | Pass / 3,701,209 | Pass / 1,708,991 | 53.83% |
| **合计** | **2/3 / 9,297,148** | **3/3 / 3,162,875** | **65.98%** |

汇总变化：

- Functional Pass：2/3 → 3/3；
- raw token：9,297,148 → 3,162,875，减少 65.98%；
- prompt token：9,109,238 → 3,075,637，减少 66.24%；
- API calls：235 → 93，减少 60.43%；
- Agent steps：231 → 94，减少 59.31%；
- Agent 累计时间：1,767.24 秒 → 790.62 秒，减少 55.26%；
- repair：0/3；
- DeepSeek prompt cache：2,914,688 hit / 160,949 miss，命中率 94.77%。

## 5. 当前可以得出的结论

Lite 方法已经取得阶段性成功：在这个开发切片上，它同时提高了通过率并将 raw
token 降低约三分之二。收益不是仅由 DeepSeek cache 造成，因为未折算缓存的 raw
token 本身也显著下降。

结果支持以下工作假设：

> 对当前 Python API feature-lifting 任务，确定性结构闭合是高价值硬信号；强制
> Agent 编写覆盖全部行为条款的自测可能增加认知负担和上下文成本，边际收益不足。

三题都没有触发 repair，因此本轮收益主要来自更聚焦的主轮，而不是事后修复。

## 6. 目前不能声称的结论

这还不是通用方法已经成立的最终证据，原因包括：

1. 样本只有三题；
2. 同时改变了行为 case、step 上限、context window、observation 长度和 token cap；
3. 模型运行具有随机性；
4. repair 分支尚未在真实 API 中触发；
5. Rich 虽然正式通过，但主 Agent 仍触及 step limit；
6. Fixture 和 Rich 各出现一次超过 57,344 配置阈值的 prompt，最大分别为
   63,075 和 63,536，说明 condenser 审计仍需收紧。

因此，准确表述应为：**pilot success，而不是 final method success**。

## 7. 下一步因果验证

下一轮新增等预算 `budget_control`：

- 与 Lite 使用相同模型、64k context、45 steps、2M primary token cap；
- 不提供 `PUBLIC_CONTRACT.json`、结构 checker 或缺口报告；
- 只提供通用“复查公开要求和实现完整性”提示；
- 正式 evaluator、Docker 环境和任务选择与 Lite 完全一致。

先在 12 个历史 API/依赖失败任务上配对运行 Budget Control 与 Lite Gate。主要报告：

- Functional Pass；
- raw token、cache miss token、时间；
- Gate repair 触发率；
- 结构门禁对正式失败的预测能力；
- 配对任务上的 win / tie / loss。

若 Lite 在等预算下仍比 control 多通过至少 1–2 题，且 token 不高于 control，才把
收益归因于 Public Contract Closure Gate，而不是单纯的预算控制或随机采样。

### 7.1 三题等预算 control smoke

实现 control 后，立即在同一三题上使用真实 API、相同 Docker 环境和相同主轮预算
进行配对 smoke：

| Task | Budget Control | Lite Gate | Lite token 变化 |
| --- | ---: | ---: | ---: |
| `pytest__skipif_eval_core__001` | Pass / 710,058 | Pass / 493,568 | -30.49% |
| `pytest__fixture_resolve_core__001` | Pass / 1,604,840 | Pass / 960,316 | -40.16% |
| `rich__markup_parse_core__001` | Fail / 2,031,869 | Pass / 1,708,991 | -15.89% |
| **合计** | **2/3 / 4,346,767** | **3/3 / 3,162,875** | **-27.24%** |

这组结果排除了“只要把预算改成 64k/45 steps/2M 就会得到同样收益”的简单解释。
在完全相同的主轮上限下，Lite 三题均使用更少 token，且在 Rich 上由 fail 变为
pass。Control 的 fixture 和 Rich 都到较晚步骤才开始写实现，Rich 最终触及 token/step
边界并正式失败；Lite 更早进入实现和结构闭合。

这一结果仍是三题、单次采样，但它把证据从“低 token 配置有效”推进到：

> **结构化公开契约闭合反馈可能具有独立于预算控制的增益。**

因此继续执行 12 题配对 pilot 是合理的，而不是直接冻结方法。

### 7.2 剩余九题运行方式

三题 smoke 已经构成配对数据，下一步只需运行任务清单
`experiments/methods/contract_closure_gate_lite/pilot12_remaining9_task_ids_20260810.txt`
中的九题。Control 和 Lite 必须使用相同任务清单、worker 数和 Docker 配置；输出到
不同目录，不覆盖既有证据。

```bash
task_args=()
while IFS= read -r task_id; do
  task_args+=(--task-id "$task_id")
done < experiments/methods/contract_closure_gate_lite/pilot12_remaining9_task_ids_20260810.txt

PYTHONPATH=harness python -B -m featureliftbench.cli run-agent benchmark/tasks \
  --agent openhands-agent \
  --agent-config harness/config/agents.toml \
  --agent-profile openhands_deepseek_v4_flash_contract_closure_budget_control \
  --env-file .env --contract-closure-budget-control \
  --agent-docker --eval-docker --timeout-seconds 1800 --num-workers 2 \
  "${task_args[@]}" \
  --output experiments/methods/contract_closure_budget_control/pilot12_remaining9_control

PYTHONPATH=harness python -B -m featureliftbench.cli run-agent benchmark/tasks \
  --agent openhands-agent \
  --agent-config harness/config/agents.toml \
  --agent-profile openhands_deepseek_v4_flash_contract_closure_gate_lite \
  --env-file .env --contract-closure-gate-lite \
  --agent-docker --eval-docker --timeout-seconds 1800 --num-workers 2 \
  "${task_args[@]}" \
  --output experiments/methods/contract_closure_gate_lite/pilot12_remaining9_lite
```

## 8. 实验产物

- Lite 三题合并摘要：
  `experiments/methods/contract_closure_gate_lite/slice3_real_api_20260810-summary.md`
- Skipif suite：
  `experiments/methods/contract_closure_gate_lite/real_api_skipif_20260810_2/`
- Fixture + Rich suite：
  `experiments/methods/contract_closure_gate_lite/real_api_remaining2_20260810_1/`
- Full Gate v2 对照：
  `experiments/methods/contract_closure_gate/slice3_api_failures_v2_20260810/`
- Budget Control 三题对照：
  `experiments/methods/contract_closure_budget_control/slice3_real_api_20260810_1/`
