# Verification-aware context compression

> **Status: archived · Screening stopped · Last verified: 2026-08-29**
> Distill-24 未过停线。不要扩到 Python-200。本文件只保留筛选规范与负结果。

## 定义

同一条 OpenHands 轨迹，只改 **prompt view**：旧的自测 stdout 收成紧凑 ledger，
Agent 仍可继续验证。论文构念是：

> Keep verification state ≠ keep verification transcript

| 维度 | 值 |
| --- | --- |
| Prompt | Main `standard`，无 method 附录 |
| Context | 131072 tokens |
| Reserved output | 8192 tokens |
| Max steps | 120 |
| Total token cap | **无** |
| Information condition | Full-Repository / No-Hint |
| Runtime `ablation_arm` | `main` |
| 轨迹落盘 | 不改写 events |

两臂对照（同一 128k Main 信封；**不要**叠 recency / artifact-aware / audit）：

| Profile | Condenser | 角色 |
| --- | --- | --- |
| `openhands_deepseek_v4_flash_llm_summary` | `token` / `LLMSummarizingCondenser` | API 基线 |
| `openhands_deepseek_v4_flash_verification_aware` | verification-aware | API 自测 ledger |
| `openhands_deepseek_v4_flash_vllm_local_llm_summary` | `token` / `LLMSummarizingCondenser` | 本地 vLLM 基线 |
| `openhands_deepseek_v4_flash_vllm_local_verification_aware` | verification-aware | 本地 vLLM 自测 ledger |

机器可读冻结：[`harness/config/methods/verification_aware_compression.json`](../../../harness/config/methods/verification_aware_compression.json)。

## 压缩规则（必须保持）

- **只压 `self_test_run` 观察**（pytest / unittest / `python -c` / heredoc /
  `python /tmp/…test…`）。不压文件读、包写入、`self_test_write`。
- **全文保留**：最近一次自测；若不同，再保留最近一次失败自测（traceback）。
- **Ledger 替换 observation body**，不是额外常驻 memory。按 `command_skeleton`
  去重更新；放在**一个** host observation。其它旧自测变成
  `Verification recorded.`。
- Ledger 最多 80 条 unique skeleton；确定性抽取（exit / pytest 计数 / 异常类型），
  **不要** LLM 写语义标签。
- 自第 0 步起压；不需要 \(T^*\)。
- Overflow：无 LLM summarizer。总 body 的**保守 token 估计**（1 字符 ≤ 1
  token，不再用 4 字符/token）超过 `window - reserved` 时，**仍然只压
  self-test observation**（继续 ledger / `Verification recorded.` / 必要时
  `TOKEN_STUB` 旧自测）。**永不**因 overflow 掩 `cat`/`grep` 源码、repo
  evidence、submission 读取。永不掩 TASK/spec、ledger host、kept-full 自测。
  没有自测时不做 overflow。这不是 artifact-aware：不把整棵 `featurelifted/`
  当 persistent，只是 overflow 不得误删 code evidence。
- 运行时必须留下 `agent/condenser_launch.json` 和逐步追加的
  `agent/condenser_audit.jsonl`。缺文件就当 condenser 没挂上。

OpenHands 1.16 在 `--override-with-envs` 时会把非
`LLMSummarizingCondenser` 清成 `None`（`_apply_env_overrides` **和**
`_maybe_build_condenser`）。只补第二处仍会让自定义 condenser 在运行时消失。
2026-08-18 第一轮本地 Core-12 verification-aware 臂因此无效，不能当机制证据。

实现挂在 pinned 论文镜像 OpenHands 1.16 / SDK 1.21 之外：CLI 会剥掉非
`LLMSummarizingCondenser`。自定义 condenser 走 harness 类 + `AgentStore` patch +
`python -m featureliftbench.openhands_condenser.launch`。不要改镜像 digest。

## 筛选标准

Core-12 只做机制筛选。对照必须是**同日** LLM summary。

- Pass 低于 summary（例如 summary 8/12 而本臂 &lt; 8/12），或 **prompt tokens
  不降**，或 steps 涨到 total tokens 不降 → **停**。控制步数之后 prompt 仍不降
  也算不降。
- 不停 → Distill-24。不要把 Core-12 / Distill-24 数字写进 Python-200 主表。

## 跑 Core-12

```bash
# Local vLLM (default). API: ENDPOINT=api ./logs/run_core12_verification_aware_deepseek_flash.sh ...
./logs/run_core12_verification_aware_deepseek_flash.sh llm_summary
./logs/run_core12_verification_aware_deepseek_flash.sh verification_aware
```

任务列表：`harness/config/experiments/rescue_plus_core12_v1.txt`。
输出：`experiments/methods/verification_aware/`。

比较 Pass、prompt+completion tokens、steps：

```bash
PYTHONPATH=harness python3 harness/scripts/compare_core12_context_efficiency.py \
  experiments/methods/verification_aware/<llm_summary_run> \
  experiments/methods/verification_aware/<verification_run>
```

`run_python200_paper.sh --execute` 会拒绝本臂全量 200。

## 跑 Distill-24

同一信封、同日两臂、本地 vLLM。任务列表
`harness/config/experiments/rescue_plus_distill24_v1.txt`（含 Core-12 的 12 题
再加 12 题）。缺 `condenser_launch.json` / `condenser_audit.jsonl` 当没挂上。

```bash
./logs/run_distill24_verification_aware_deepseek_flash.sh llm_summary
./logs/run_distill24_verification_aware_deepseek_flash.sh verification_aware
```

对照仍是 Pass、prompt tokens、steps。Distill-24 也不是 Python-200 通过率。
2026-08-19 overflow 误伤源码已修：重跑 verification-aware 时 **冻结** 同日
`llm_summary` 基线 `distill24-deepseek-v4-flash-llm_summary-20260819-070656`。
`vcrpy`/`icalendar` 早停标 non-treatment failure，主 Pass 仍按 24 题计。

第一轮 **不要** 和 Artifact-aware / Recency / Pre-submit audit 叠跑。

## 筛选结论：停

同日 LLM summary 基线
`experiments/methods/verification_aware/distill24-deepseek-v4-flash-llm_summary-20260819-070656`：
**16/24**。第一轮 verification-aware
`…/verification_aware-20260819-082850`：**14/24**（22 题有 eval）。低于
「≤14/24 kill」。overflow 修补后的
`…/verification_aware-20260819-195214` 只到 20 题，不是 Distill-24 结果。

不要 Python-200，不要再调 ledger。下一正式臂是 RQ6 Public-feedback，见
[METHOD_RQ6_PUBLIC_FEEDBACK.md](METHOD_RQ6_PUBLIC_FEEDBACK.md)。
