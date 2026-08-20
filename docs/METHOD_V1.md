# V1：Main + 2M token cap

> **Status: current · Last verified: 2026-08-18**
> 本文件是当前 **V1** 方法的唯一规范。旧 `contract_closure_gate_lite_v1*`
> 协议（checker / structure-stop / repair）已退役，只作历史对照。
> 结果解释见 [FINDINGS.md](FINDINGS.md)；不要把 Core-12 写成 Python-200 通过率。

## 定义

**V1 = Main 论文协议 + 2,000,000 total-token cap。**

| 维度 | 值 |
| --- | --- |
| Prompt | Main `standard`，无 contract-closure 附录 |
| Context | 131072 tokens |
| Reserved output | 8192 tokens |
| Max steps | 120 |
| Total token cap | **2,000,000**（`openhands_total_token_limit`） |
| Checker / structure-stop / repair | **关闭** |
| Information condition | Full-Repository / No-Hint |
| Runtime `ablation_arm` | `main`（协议未改，只加 cap） |
| `run_python200_paper.sh` method label | `v1` |

机器可读冻结：[`harness/config/methods/v1.json`](../harness/config/methods/v1.json)。

## 为什么这样定

DeepSeek Python-200 上，旧 Lite V1 协议（checker + stop + repair，Main 预算）
Functional Pass 低于 Main，成对 RRES 无优势，见 [FINDINGS.md](FINDINGS.md)。
2026-08-17 Core-12 诊断（**不是** Python-200 通过率）比较了 Main、旧 Lite V1 与
Main+2M：Main+2M Pass ≥ 旧 Lite V1，token 远低于 Main。裁决
`keep_cap_kill_v1_protocol`：保留 2M cap，拆掉 checker/stop/repair，并把该方法
**就叫 V1**。

Core-12 报告：
`experiments/methods/main_2m_cap/core12-deepseek-v4-flash-main-2m-cap-0817-001/core12-deepseek-v4-flash-main-2m-cap-0817-001-comparison.md`。

## Profiles

| Profile | 用途 |
| --- | --- |
| `openhands_deepseek_v4_flash_v1` | DeepSeek API 全量 Python-200 |
| `openhands_qwen3_6_35b_a3b_fp8_v1` | 本机 Qwen3.6-35B 单 endpoint（默认 `:8014`） |
| `openhands_qwen3_6_35b_a3b_fp8_v1_p8030` … `_p8033` | 四路并行，各 50 题 |

`openhands_deepseek_v4_flash_main_2m_cap` 是 V1 的别名，仅保留给 Core-12 路径。

名字以 `_v1` 结尾，或含 `_v1_p<port>` 的 profile，必须满足上表信封；
`run_python200_paper.sh` 会拒绝漂移。

## 跑全量 Python-200

Qwen3.6-35B V1-200 **已经跑完**，不要重复启动下面的 tmux 分片。下列命令仅供复现。
DeepSeek API V1-200 按 [STATUS.md](STATUS.md) 当前不作为 blocker。

Plan-only：

```bash
./harness/scripts/run_python200_paper.sh \
  openhands_deepseek_v4_flash_v1 \
  python200-v1-plan
```

DeepSeek API 单进程：

```bash
./logs/run_python200_v1_deepseek_flash.sh
```

Qwen3.6-35B 四路并行（`:8030`–`:8033`，各 50 题；**已完成并合并**）。复现：

```bash
export FEATURELIFTBENCH_AGENT_DOCKER_NETWORK=host
./logs/start_python200_v1_qwen35b_4shard_tmux.sh
```

| tmux | 端口 | 分片 |
| --- | --- | --- |
| `flb-v1-qwen35b-p8030` | 8030 | 题 0–49 |
| `flb-v1-qwen35b-p8031` | 8031 | 题 50–99 |
| `flb-v1-qwen35b-p8032` | 8032 | 题 100–149 |
| `flb-v1-qwen35b-p8033` | 8033 | 题 150–199 |
| `flb-v1-qwen35b-merge` | — | 等四路 `.done` 后合并 |

分片输出：
`experiments/python/openhands/qwen3.6-35b-a3b-fp8/python200-qwen3.6-35b-a3b-fp8-v1-0817-001-shardN-p803N/`

合并后的正式 suite：
`experiments/python/openhands/qwen3.6-35b-a3b-fp8/python200-qwen3.6-35b-a3b-fp8-v1-0817-001/`

题单：[`harness/config/experiments/python200_v1_shards/`](../harness/config/experiments/python200_v1_shards/)。
手动合并：

```bash
PYTHONPATH=harness python3 harness/scripts/merge_python200_v1_shards.py \
  --output experiments/python/openhands/qwen3.6-35b-a3b-fp8/python200-qwen3.6-35b-a3b-fp8-v1-0817-001 \
  experiments/python/openhands/qwen3.6-35b-a3b-fp8/python200-qwen3.6-35b-a3b-fp8-v1-0817-001-shard{0,1,2,3}-p803{0,1,2,3}
```

本机 vLLM 的 agent 容器必须 `FEATURELIFTBENCH_AGENT_DOCKER_NETWORK=host`。
Qwen External-50 Main 已完成；不要与占用同一 API 端口的其它 Main 跑抢流量。
`:8030`–`:8033` 的 V1 分片互不抢 endpoint。

## 命名与历史对照

| 名字 | 含义 | 状态 |
| --- | --- | --- |
| **V1** | Main + 2M cap | **当前 cost arm** |
| Lite V1 / `contract_closure_gate_lite_v1*` | checker + stop + repair | 退役；DeepSeek Python-200 数字仍在 FINDINGS 中作历史对照 |
| Frozen Lite V1 45+10 | 同上协议、pilot 信封 | 不可与 Main / 当前 V1 混比 |
| Adaptive Budget V2 | 1.5M + 检查点 + 500K repair | 退役；Core-12 2/12 |

## 已完成的结果

| 范围 | Functional Pass | 说明 |
| --- | ---: | --- |
| Qwen3.6-35B Python-200 V1 | **55/200** | 正式 cost arm；约 329M tokens |
| Flash Core-12 V1 | 4/12 | 对照 Main 8/12；**不是** Python-200 |
| Flash API V1-200 | 未跑 | 不作为 blocker；不补跑其它模型 V1-200 |

Qwen 与 Main 的成对解释、E50 干净切片和 cap 税见 [FINDINGS.md](FINDINGS.md)。

## 停扩

V1 只是 cost arm，不是比 Main 更强的方法。不要在 V1 上再叠 checker、repair、
behavior_probe 或 V2 早停。Adaptive Budget V2 已在 Core-12 证伪，见
[archive/methods/METHOD_ADAPTIVE_BUDGET_V2.md](archive/methods/METHOD_ADAPTIVE_BUDGET_V2.md)。

不要把 Core-12 / Distill-24 通过率写进 Python-200 主表。
