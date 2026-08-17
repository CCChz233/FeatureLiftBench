# Contract Closure Gate 抢救 P0（2026-08-14）

> **Status: reference · Last verified: 2026-08-17**

## 结论先行

Lite V1 目前不能被表述为“提高正确率的方法”，但仍可抢救为一个固定预算下的公开契约反馈方法。最新本地 DeepSeek-V4-Flash Python-200 结果中，Lite V1 的正式 Functional Pass 是 127/200；配对 Main 是 145/200。Lite V1 少用约 32.1% token，但少通过 18 题。因此当前证据支持的是成本—正确率折中，不支持无条件 accuracy uplift。

P0 找到一个明确且可修复的工程缺陷：检查器运行环境没有安装任务允许依赖，却把 `ModuleNotFoundError` 当成 submission 的 hard failure。这制造了大量假 repair。

## 本轮修复

1. 报告口径分离：
   - `summary.passed` 保留为历史 workflow/run status，避免破坏续跑兼容性。
   - 新增 `functional_passed`、`functional_failed`、`functional_evaluated`、`functional_unknown` 和 `functional_pass_rate`。
   - 实验分析和失败分类统一以 evaluator 的 `functional_gate` 为准，workflow pass 单列。
2. 检查器错误分类：
   - 检查器环境缺少允许依赖时记为 `unknown`，不再记为 hard fail，也不触发 repair。
   - submission 内部缺失 `featurelifted.*` 模块仍是 hard fail，避免把真实实现错误放过。
   - checker 自身崩溃记为 infrastructure unknown，始终继续正式 evaluator，但不花模型预算 repair checker。
3. 版本记录：
   - 公开契约生成器保持 `contract_closure_gate.v4`，因为 public contract 格式未变。
   - 新检查器单独记录为 `contract_closure_checker.v5`。
   - 原 Lite V1 frozen 方法只能由 `contract-closure-lite-v1-frozen.1` tag 复现；v5 结果不得冒充 frozen.1。
4. 新增离线重放工具：
   - `harness/scripts/replay_contract_closure_gate.py`
   - 它只读取公开 task metadata、归档 submission、旧 closure 报告和正式结果，不读取隐藏测试内容。

## Python-200 离线证据

输入：`python200-deepseek-v4-flash-lite-v1-vllm-local-0813-001` 的 200 题归档结果。

| 指标 | 结果 |
| --- | ---: |
| 旧版 initial repair 请求 | 35 |
| 仅由 checker 依赖环境造成的假 repair | 23 |
| 预计可避免的 repair token | 5,691,593 |
| 预计可避免的 repair 时间 | 1,513.795 秒 |
| v5 对归档最终 submission 的 hard open | 13 |
| 其中正式 Functional Fail | 11 |
| hard-open failure precision | 84.6% |

这里的 23 次和 569 万 token 是基于归档 initial 报告与实际 repair usage 的反事实投影；13 个 final hard open 是对归档“修复后 submission”的离线重放。它们说明 P0 能显著减少无效 repair，但不能单独证明 Functional Pass 会提高。

## 下一步实验门槛

P1 已新增独立的 `contract_closure_gate_lite_rescue` 实验臂，但尚未冻结，不能直接复用 `lite_v1_frozen` 名字。它目前满足：

- 保留 Lite V1 的短提示和 structure-only 主流程。
- 使用 checker v5，独立 policy id 为 `contract_closure_gate_lite_rescue.v1`。
- repair 上限为 200k token / 5 steps；只修复至多 2 个 missing API、至多 3 个明确 API/signature/forbidden-import 局部缺口；empty、broad、unknown、checker infrastructure 不 repair。
- 与同模型、同 endpoint、同 context、同 primary token/step、同 repair 上限的 sham-repair control 配对。
- 先跑 30–50 题历史 repair-stratum pilot；只有 Functional Pass 不劣于 matched control，且 token/pass 改善，才进入全量 200。

用于工程 pilot 的 35 题已冻结在 `harness/config/experiments/contract_closure_gate_lite_rescue_pilot35.txt`。这 35 题来自本次历史结果，只能用于工程验证和选择策略，不能作为最终未见测试集。

计划检查命令（不调用模型）：

```bash
./harness/scripts/run_python200_paper.sh \
  openhands_deepseek_v4_flash_contract_closure_gate_lite_rescue \
  lite-rescue-plan \
  --workers 2 \
  --agent-image <agent-image-id> \
  --eval-image <eval-image-id>
```

构造 35 题参数：

```bash
task_args=()
while IFS= read -r task_id; do
  task_args+=(--task-id "$task_id")
done < harness/config/experiments/contract_closure_gate_lite_rescue_pilot35.txt
```

Rescue 工程 pilot 命令（付费，批准实验后才加以执行）：

```bash
PYTHONPATH=harness python -B -m featureliftbench.cli run-agent benchmark/python200_tasks \
  --agent openhands-agent \
  --agent-config harness/config/agents.toml \
  --agent-profile openhands_deepseek_v4_flash_contract_closure_gate_lite_rescue \
  --env-file .env --contract-closure-gate-lite-rescue \
  --agent-docker --eval-docker --timeout-seconds 1800 --num-workers 2 \
  "${task_args[@]}" \
  --output experiments/methods/contract_closure_gate_lite_rescue/pilot35_rescue_001
```

注意：现有 `contract_closure_budget_control` 只严格匹配主轮预算，没有匹配条件式 200k/5 二次 repair。因此新 arm 已可做 smoke/工程运行，但正式成对付费 pilot 仍需先实现 sham-repair control；在此之前不能把差异解释为 checker feedback 的因果收益。

## 当前判断

方法“能救”，但论文故事应从“自测提高正确率”改成：公开契约检查能否作为一个高精度、低成本的选择性反馈信号，在固定预算下只对局部可修复失败追加计算。P0 已经消除了最主要的假信号来源；下一阶段关键是做出独立 rescue arm 和严格等预算对照，而不是立即再烧一轮全量 API。
