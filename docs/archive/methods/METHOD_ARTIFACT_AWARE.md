# Artifact-aware retention（信息角色 condenser）

> **Status: archived · Screening stopped · Last verified: 2026-08-29**
> 本文件是 **A = context efficiency** 的机制筛选规范。不改轨迹、不加 2M cap、
> 不碰 Hidden。Core-12 不是 Python-200 通过率。

## 定义

同一条 OpenHands 轨迹，只改 **prompt view**：按信息角色压缩观察，而不是按
新旧。FeatureLift 只是这种不对称最明显的地方；论文构念是 persistent vs
ephemeral，不是「永远保留 `featurelifted/`」。

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

三臂对照（同一 128k Main 信封）：

| Profile | Condenser | 角色 |
| --- | --- | --- |
| `openhands_deepseek_v4_flash_llm_summary` | `token` / `LLMSummarizingCondenser` | 基线 |
| `openhands_deepseek_v4_flash_recency_masking` | recency window=100 | 新旧对照 |
| `openhands_deepseek_v4_flash_artifact_aware` | artifact-aware | 信息角色 |

机器可读冻结：[`harness/config/methods/artifact_aware_retention.json`](../../../harness/config/methods/artifact_aware_retention.json)。

## 压缩规则（必须保持）

**Persistent 不能被 evict**，但 **不要每步回灌整棵 submission 树**。只保留每个
已写入 artifact 路径的 **最新** observation body；该路径更早的版本变成
`Superseded file contents: {path}`。

同一 `path+hash` 再读 **保留短 stub**（例如 `Re-read unchanged file: repo/foo.py`），
不丢 revisit 事件。hash 变了则再给全文。

超过 token 阀时，只省略 **ephemeral** 观察；persistent 不进这个阀。

Recency Masking 只按窗口丢掉旧 observation body：
`Observation omitted (outside attention window)`。它不是信息角色基线。

实现挂在 pinned 论文镜像 OpenHands 1.16 / SDK 1.21 之外：CLI 会剥掉非
`LLMSummarizingCondenser`。自定义 condenser 走 harness 类 + `AgentStore` patch +
`python -m featureliftbench.openhands_condenser.launch`。不要改镜像 digest。

## 筛选标准

Core-12 只做机制筛选，不是非劣效检验。若 tokens 不降或 Pass 明显回退则停；
否则 Distill-24。不要把 Core-12 数字写进 Python-200 主表。

**筛选结果（停）。** 相对 LLM summary（8/12，65.0M tokens），recency 与
artifact-aware 也是 8/12，token 分别为 73.8M 与 85.9M。Pass 持平、token 未降，
不扩 Distill-24 / Python-200。

## 跑 Core-12

```bash
./logs/run_core12_context_efficiency_deepseek_flash.sh llm_summary
./logs/run_core12_context_efficiency_deepseek_flash.sh recency_masking
./logs/run_core12_context_efficiency_deepseek_flash.sh artifact_aware
```

任务列表：`harness/config/experiments/rescue_plus_core12_v1.txt`。
输出：`experiments/methods/artifact_aware/`。

比较 Pass、prompt+completion tokens、steps：

```bash
PYTHONPATH=harness python3 harness/scripts/compare_core12_context_efficiency.py \
  experiments/methods/artifact_aware/<llm_summary_run> \
  experiments/methods/artifact_aware/<recency_run> \
  experiments/methods/artifact_aware/<artifact_run>
```

`run_python200_paper.sh --execute` 会拒绝 recency / artifact 全量 200。

第一轮 **不要** 和 Pre-submit audit 叠在同一 run。B 臂见
[METHOD_PRE_SUBMIT_AUDIT.md](METHOD_PRE_SUBMIT_AUDIT.md)。
