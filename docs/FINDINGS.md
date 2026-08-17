# 当前实验结果：Main vs Frozen Lite V1

> **Status: current · Last verified: 2026-08-17**
> 本文是当前 DeepSeek Python-200 方法对比的唯一手写结论。指标定义见
> [EVALUATION.md](EVALUATION.md)，机器可读快照见
> [`deepseek_main_vs_frozen_lite_v1_20260817.json`](../artifacts/research_analysis/current_results/deepseek_main_vs_frozen_lite_v1_20260817.json)。

## 结论先行

Frozen Lite V1 尚不能替代 Main。在两个 DeepSeek 运行端点上，Main 的 Functional Pass
Rate 都明显更高：API 高 **6.5 个百分点**，本地 vLLM 高 **9.0 个百分点**。
Lite V1 是“更省资源但牺牲正确性”的方法，不是已经改进好的新主方法。

RRES 证据目前不足以回答“Lite 是否比 Main 更紧凑”：API Lite 和本地 Main
缺少逐题 evaluator 产物，无法在同一端点、同一题、两方都通过的样本上成对比较。

## 两项核心指标

| 运行端点 | 方法 | Functional Pass | Pass Rate | RRES（通过题） |
| --- | --- | ---: | ---: | --- |
| API | Main | **144/200** | **72.0%** | 部分可用：99/144，median 0.985 [0.786, 1.034] |
| API | Frozen Lite V1 | 131/200 | 65.5% | 不可用：0/131 |
| 本地 vLLM | Main | **145/200** | **72.5%** | 不可用：0/145 |
| 本地 vLLM | Frozen Lite V1 | 127/200 | 63.5% | 完整：127/127，median 1.000 [0.798, 1.000] |

注：表中两个 RRES 数值来自不同端点、不同方法且覆盖不同，**不能直接比较**。
在补齐缺失证据前，紧凑度方法对比必须记为 N/A。

`final_score` 在当前 evaluator 中等于 `functional_gate`，所以 Average Final Score 只是
Pass Rate 的另一种写法，不是“模块更紧凑”的指标。

## Functional 成对对比

| 可成对范围 | 两者都过 | 仅 Main 过 | 仅 Lite 过 | 两者都失败 |
| --- | ---: | ---: | ---: | ---: |
| API Main-150 | 84 | **15** | 4 | 47 |
| 本地 vLLM Python-200 | 125 | **20** | 2 | 53 |

两个端点都呈现同一方向：Lite 救回的 Main 失败题很少，但会丢掉更多 Main
本来能通过的题。这不是单一 endpoint 的偶然现象。

## 失败阶段

下表按 `missing → build → public → hidden → isolation` 的首败优先级计数。没有
逐题 `eval/result.json` 时标为“阶段证据缺失”，不猜测失败关卡。

| 运行端点 / 方法 | Pass | 未交付 | Build | Public | Hidden | Isolation | 阶段证据缺失 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| API Main | 144 | 5 | 1 | 24 | 21 | 0 | 5 |
| API Lite V1 | 131 | 8 | — | — | — | — | 61 |
| 本地 Main | 145 | 2 | — | — | — | — | 53 |
| 本地 Lite V1 | 127 | 2 | 2 | 39 | 30 | 0 | 0 |

API Main 的细分关卡来自 Main-150；External-50 只能确认 45 过、5 失败，无法
进一步分解。因此只有本地 Lite V1 是完整 Python-200 失败阶段分布。它的 73 个
失败中，Public 39，Hidden 30，说明主要损失确实在契约主路径和深层行为闭包，
不是 isolation。

## 数据口径纠正

历史 results-pack README 把 `summary.passed` 标成了 Functional pass。这个字段是
workflow/run status，导致 API Main 被误写为 122，本地 Main 被误写为 117。本文统一
使用 evaluator `final_score/functional_gate`。原始包作为不可变证据保留，但其 README
不再是当前结果入口。

## 可以与不可以宣称的结论

可以宣称：

- Main 在 API 和本地 vLLM 两组 Python-200 证据上都显著保留了更多 Functional Pass；
- Frozen Lite V1 的正确性代价为 6.5–9.0 个百分点；
- 本地 Lite V1 的已知失败主要集中在 Public 和 Hidden。

不可以宣称：

- Lite V1 已经优于 Main；
- Lite V1 的 RRES 优于 Main；
- 从两组不匹配的 RRES 摘要推导方法紧凑度因果；
- 将 token 节省当作功能质量改进。

## 证据与复现

数据源：

- `python200-deepseek-v4-flash-lite-v1-vllm-local-0813-001-results-latest.tar.gz`
  SHA256 `0d950fb1210a5a40ed746fe31eeedb40f1a3d53f1fca0badead6ad83f9612208`
- `FeatureLiftBench-deepseek-v4-flash-150-20260805.tar.gz`
  SHA256 `d4b5303ccdaf1d5a188001e0b24de1694bf928af8647dacbae194db46cb6e28b`

重建命令：

```bash
python harness/scripts/reconcile_current_deepseek_results.py
```

当前最大的证据缺口是 API Lite、本地 Main 和 API Main External-50 的逐题
`eval/result.json`。补齐它们后，才能做完整的失败阶段和 paired RRES 对比。
