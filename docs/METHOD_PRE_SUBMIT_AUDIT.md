# Pre-submit explicit-contract audit

> **Status: current · Last verified: 2026-08-18**
> 本文件是 **B = explicit-contract forgetting** 的机制筛选规范。Prompt-only，
> 不碰 Hidden，不加 checker / repair。Core-12 不是 Python-200 通过率。

## 定义

同一 128k Main 信封、LLM Summary condenser、No-Hint、无 public tests。只在
TASK 末尾要求 agent 对照 **已经写在 TASK.md 里的** Required API 与 `Bxxx`
条款做一次提交前清单。

| 维度 | 值 |
| --- | --- |
| Prompt | Main + pre-submit audit 附录 |
| Context | 131072 tokens |
| Reserved output | 8192 tokens |
| Max steps | 120 |
| Total token cap | **无** |
| Condenser | `token` / LLM Summary（不与 A 臂叠加） |
| Checker / Hidden / public tests | **关闭** |
| Runtime `ablation_arm` | `pre_submit_contract_audit` |

机器可读冻结：[`harness/config/methods/pre_submit_contract_audit.json`](../harness/config/methods/pre_submit_contract_audit.json)。

禁止：发明新 contract、猜测 Hidden、寻找 evaluator tests、`flb-contract-check`、
repair 轮。

强制格式：

```
PRE-SUBMIT CONTRACT AUDIT
- B001: covered
- required API: gap missing export
AUDIT_RESULT: gaps|complete
```

## 过程指标

Functional Pass 不是唯一结果。还要记：

| 指标 | 含义 |
| --- | --- |
| `audit_executed` | 轨迹里出现了上述 header / `AUDIT_RESULT` |
| `explicit_gap_found` | 清单标了 gap，或 `AUDIT_RESULT: gaps` |
| `continued_after_gap` | gap 之后仍有 submission 写入 |
| Public 0→1 flip vs llm_summary | 相对 A 基线的成对翻盘（有 public 分数时再填） |

落盘：`agent/pre_submit_audit.json`。

## 跑 Core-12

第一轮 **不要** 和 artifact-aware / recency 叠跑。

```bash
./logs/run_core12_pre_submit_audit_deepseek_flash.sh
```

输出：`experiments/methods/pre_submit_audit/`。
`run_python200_paper.sh --execute` 会拒绝该臂全量 200。

**筛选结果（停）。** Core-12 为 6/12，低于同日 LLM-summary 对照 8/12。Pass
回退，不扩 Distill-24 / Python-200。数字不进主表。
