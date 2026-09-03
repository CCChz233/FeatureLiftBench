# Hidden contract provenance audit

> **Status: current candidate remediation complete; historical consensus still pending · Started: 2026-08-20 · Last checked: 2026-09-02**
> 这是 RQ4 机制标注，不是新 Agent 方法。不看 Hidden 测试源码当「仓库证据」。
> 切片：Flash Main Hidden-failure 并集 33 题。

## 问题

Hidden 失败是 **模型没闭合已写明的行为**，还是 **test-blind 下规格观测不到**？

## 切片

Flash No-Hint Main-200 Hidden 首败并集（本地 0812 ∪ API）：

- 清单：[`harness/config/experiments/hidden_provenance_flash33_v1.txt`](../harness/config/experiments/hidden_provenance_flash33_v1.txt)
- n=33（本地 24、API 22、交集 13）
- 评测日志：题在本地 Hidden 失败则用 0812；否则用 API 对应 suite

不扩到 public 失败题。不叠新方法臂。

## 编码（断言级，再汇总到题）

合法依据：**仅** `metadata.public_spec` / 生成的 `TASK.md`、以及 agent 可见的 `repo/`。
**禁止**把 `hidden_tests/` 内容当成 Recoverable 证据（那是泄漏）。
标注者可以读 Hidden 测试，只为了知道「评测在查哪条行为」，再回到 spec/repo 找出处。

| 档 | 定义 |
| --- | --- |
| **Explicit** | 失败的 Hidden 断言所查的行为，在 `public_spec` 行为条款或 `required_api`（含 members/签名）里写明，不需要猜。 |
| **Recoverable** | spec 未逐字写该断言，但上游 `repo/` 里有单一、明确的实现/文档/自测，agent 在 Full-Repository 下应当能恢复。 |
| **Ambiguous** | repo 里 ≥2 套说得通的目标行为（版本分叉、可选后端、兼容层），合法信息无法唯一决定 Hidden 选哪套。 |
| **Underdetermined** | 仅凭 spec+repo **无法**确定 Hidden 要的具体观测（错误类型、索引语义、默认值、匹配是否必须 full-string 等），而该观测又未写进 public_spec。 |

一条 Hidden 测试函数可以打一档。一题多个失败断言取：

- `task_primary`：最严重档（Underdetermined > Ambiguous > Recoverable > Explicit 的「规格问题」优先），并另报 `explicit_share`。
- 题级主因用于论文表；断言级列表进 JSON。

若 `task_primary=Underdetermined`，记为 **规格观测问题（可能是题缺陷）**，不是模型能力结论。

## 不做

- 不把 checkpoint / spec-adversarial / Public-feedback 写进本审计。
- 不因此改 Hidden 测试或放水。发现 Underdetermined 只标注，另开题修复队列。
- 不宣称 33 题分布可外推到 Qwen/OSS，除非另标。

## 产出

- 数据包：`artifacts/research_analysis/hidden_provenance/flash33_packets.json`
- 标注（**AI 初标，非 gold**）：`artifacts/research_analysis/hidden_provenance/flash33_labels.json`

## 初标分布（n=33，待双 Agent consensus）

| 档 | n | 读法 |
| --- | ---: | --- |
| Explicit | 11 | 模型没按已写明的条款做 |
| Recoverable | 4 | 仓里有唯一实现，spec 没写细 |
| Ambiguous | 0 | 初标没有「多目标打架」 |
| Underdetermined | 18 | Hidden 观测在 spec+repo 下无法唯一确定 |

初标 **Underdetermined 过半**，但容易把「没逐字写进 spec」标成这一档。论文表前必须由两个独立 Agent 按同一公开输入复核 Underdetermined vs Recoverable；错误字符串、JSON 空格、`__all__` 黑名单等冲突保持 `abstain`，不强行归类。该 Agent 审计本身不是 human gold。

不要把这 33 题分布写成 Qwen/OSS 结论。不要据此改 Hidden 测试。

## Python-200′ current-candidate remediation

The 18 `Underdetermined` labels above describe historical task revisions and
remain unchanged as provenance. For the current `python200_hard` candidate:

- 17/18 tasks are in Python-200′; `joserfc__jwt_claims_core__001` belongs to the
  superseded External-50 and is not in the paper suite;
- 11 current tasks now make the disputed obligation explicit in `public_spec`;
- 6 current tasks narrow evaluator assertions that required an unjustified exact
  string, index convention, denylist, or serialization spelling;
- therefore the current candidate has **0 unresolved items from this preliminary
  18-task blocker list**.

Machine-readable ledger:
[`python200_prime_candidate_rejudgement_20260831.json`](../artifacts/research_analysis/hidden_provenance/python200_prime_candidate_rejudgement_20260831.json).

This is an AI-assisted maintainer rejudgement, not independent human gold. It
does not retroactively make the old Flash-33 labels or old model runs eligible
for the new freeze.

2026-09-02 inventory (Gate 0 **passed** on the R5 re-run under the amended
protocol path `budget_exhausted_with_valid_record`; Gate 1 unblocked but
deliberately not run, so still only wave3/wave10; initial labels replayable and
not gold):
[`reports/agentic_evidence/GATE_CHECK_20260902.md`](../reports/agentic_evidence/GATE_CHECK_20260902.md).

Until Flash-33 reaches 33/33 dual-auditor consensus, Hidden provenance is a
**declared limitation**, not a result: no Hidden-fairness number here may be
reported as gold, and Gate 2 sensitivity analysis cannot be run.
