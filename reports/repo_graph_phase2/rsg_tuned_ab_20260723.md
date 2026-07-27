# RSG tuned 版本对照（DeepSeek v4 flash）

> 历史 RSG 消融，使用 pre-v2 profile；不是 Full-Repository / No-Hint
> Main 结果。

更新：2026-07-23

## 目标

- 简单题：降 token  
- 难题：提通过率  

## 调参版本

Profiles（`harness/config/agents.example.toml`）：

- `openhands_deepseek_v4_flash_rsg_tuned_efficient`：`auto_support` 紧凑 start-here + 限制探索指令 + 更小预算/步数  
- `openhands_deepseek_v4_flash_rsg_tuned_hard`：同注入、更大 support 预算  

代码：`support.guidance` / `render_compact_guidance`，bootstrap 注入「只先读 start-here」。

## 真实 API 结果

### Easy：`iniconfig__parse_config__001`

| 轮次 | 臂 | status | final_score | tokens | 相对 P0 |
| --- | --- | --- | --- | --- | --- |
| ab1 | P0 | passed | 0.544 | 258k | — |
| ab1 | tuned_efficient | passed | 0.499 | 303k | +17%（未赢） |
| **ab2** | **P0** | **passed** | **0.516** | **298k** | — |
| **ab2** | **tuned_efficient（加严指令）** | **passed** | **0.499** | **220k** | **-25.9%** |

ab2 目录：`experiments/rsg_pilot/openhands/deepseek-v4-flash/tuned-ab2-20260723-223134`

### Hard：`transitions__state_machine_core__hard3_001`（tuned_hard）

- status: **failed**（public pass，hidden fail）  
- tokens: 1.25M  
- functional_gate=0  
- 目录：`.../tuned-ab-20260723-222557/tuned-hard-transitions`  

本轮**没有**同题 P0 对照，不能声称难题增益。

## 结论

1. **简单题降 token：有一次成功证据（约 -26%），且仍 passed。** 单次噪声大，需复现。  
2. **难题提通过率：尚未证明。** 当前 hard 跑仍是 classic public→hidden 失败。  
3. 关键杠杆是 **紧凑 start-here 注入 + 禁止先全域搜索**，不是可选 CLI 调用率。

## Easy 3-round repro
- dir: `experiments/rsg_pilot/openhands/deepseek-v4-flash/tuned-easy-repro-20260723-223851`

| round | arm | status | final_score | tokens | steps |
| --- | --- | --- | ---: | ---: | ---: |
| 1 | p0 | passed | 0.5442 | 236775 | 19 |
| 1 | tuned | passed | 0.5442 | 338333 | 24 |
| 2 | p0 | passed | 0.4993 | 231730 | 13 |
| 2 | tuned | passed | 0.4993 | 337096 | 20 |
| 3 | p0 | passed | 0.4993 | 567896 | 31 |
| 3 | tuned | passed | 0.5442 | 237243 | 18 |

mean delta tuned-p0: -41243 tokens (-11.9%); wins 1/3
