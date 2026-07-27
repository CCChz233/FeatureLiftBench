# RSG v2 真实 API 烟雾验收（2026-07-23）

> 这里的 “v2” 是 RSG 原型 API 版本，不是当前 FeatureLiftBench v2 Main
> freeze；本报告仅作历史基础设施证据。

- 状态：同日验收通过（基础设施 + 可选工具路径）
- 模型：`deepseek/deepseek-v4-flash` via DeepSeek API
- Agent：OpenHands（`featureliftbench-agent:openhands-rsg-pilot-v1`，宿主 harness 挂载）
- Eval：Docker（`featureliftbench-eval:latest`）

## 目标

验证 Design v2 的正式 OpenHands 路径可在真实 API 下端到端跑通：

1. `tool_only` 可选工具 bootstrap（无强制 task-closure / submission-check）
2. `flb-rsg support` 在 agent 镜像内可用
3. `auto_support` 诊断臂可注入 Operational Support Subgraph
4. 旧强制采用门不再阻塞 suite

## 套件

| 臂 | Suite 目录 | 任务 | status | final_score | RSG |
| --- | --- | --- | --- | --- | --- |
| P0 基线 | `experiments/rsg_pilot/openhands/deepseek-v4-flash/smoke-p0-baseline-v2-20260723-200737` | iniconfig | passed | 0.544 | 未启用 |
| P2 tool_only | `.../smoke-p2-tool_only-v2-20260723-200606` | iniconfig | passed | 0.522 | enabled；可选工具 **未调用**（符合 optional） |
| D0 auto_support | `.../smoke-d0-auto_support-v2-20260723-200929` | iniconfig | passed | 0.499 | bootstrap 注入 support JSON（3938 chars） |
| P2 tool_only | `.../smoke-p2-bidict-v2-20260723-201043` | bidict | passed | 0.524 | enabled；可选工具未调用 |

## 工具层抽查

在 P2 产物图上（Docker + 宿主 harness）：

```bash
flb-rsg support --graph <run>/agent/state/repo_graph/base \
  --seed IniConfig --budget-tokens 2000
```

- 修复 seed 同分优先级后：`IniConfig` → `python:iniconfig.IniConfig:class`
- 结果：status=ok，core≈13，support≈7，boundaries 非空，预算内

D0 bootstrap 含 `Diagnostic auto_support`，seeds 对齐 `source_entrypoints`，并截断到 bootstrap 字符预算。

## 验收判定

| 项 | 结果 |
| --- | --- |
| 真实 API 调用 | 通过（DeepSeek） |
| OpenHands Docker agent | 通过 |
| Docker eval | 通过 |
| tool_only bootstrap 文案 | 通过（search/inspect/support） |
| 无强制采用门阻塞 | 通过（`optional_tool_used=false` 仍 passed） |
| `support` CLI 可用 | 通过 |
| auto_support 注入 | 通过 |
| Agent 主动调用 optional 工具 | **未发生**（easy sanity 题；不作失败条件） |

## 结论

同日 **真实 API 烟雾验收通过**。正式可选工具路径与诊断臂可跑；下一步应在偏 C 类/更难任务上观察调用率与 Pass@1 / mean final_score（Phase 5），并补 Phase 3–4 关系族与离线子图质量门。
