# FeatureLiftBench 文档入口

> **Status: current · Last verified: 2026-08-20**

日常只从这里进入。动态数字只维护在 [STATUS.md](STATUS.md)，方法对比结论只维护在
[FINDINGS.md](FINDINGS.md)。

## 当前入口

| Need | Document |
| --- | --- |
| 看当前规模、完成度、可用结果和 blocker | [STATUS.md](STATUS.md) |
| 看当前 V1 方法（Main + 2M cap） | [METHOD_V1.md](METHOD_V1.md) |
| 看 context-efficiency 筛选（LLM Summary / Recency / Artifact-aware） | [METHOD_ARTIFACT_AWARE.md](METHOD_ARTIFACT_AWARE.md) |
| 看 verification-aware 自测压缩筛选（已停） | [METHOD_VERIFICATION_AWARE.md](METHOD_VERIFICATION_AWARE.md) |
| 看 pre-submit explicit-contract audit | [METHOD_PRE_SUBMIT_AUDIT.md](METHOD_PRE_SUBMIT_AUDIT.md) |
| 看 RQ6 Public-feedback 信息消融 | [METHOD_RQ6_PUBLIC_FEEDBACK.md](METHOD_RQ6_PUBLIC_FEEDBACK.md) |
| 看 Hidden 合同出处审计（进行中） | [HIDDEN_CONTRACT_PROVENANCE.md](HIDDEN_CONTRACT_PROVENANCE.md) |
| 用 Agent 自动校准/审计 Hidden 行为的 repository recoverability | [AGENTIC_EVIDENCE_AUDIT.md](AGENTIC_EVIDENCE_AUDIT.md) |
| 看方法结论：V1 cost tax、旧 Lite、已停脚手架、RQ6 | [FINDINGS.md](FINDINGS.md) |
| 离线拆已有轨迹的 token 尾巴（不是新方法） | [TOKEN_UTILITY.md](TOKEN_UTILITY.md) |
| 组会投屏：跨模型 Main / 方法对比 / 失败阶段 / 题集 / 案例 | [汇报_Python200跨模型Main.md](汇报_Python200跨模型Main.md) · [汇报_实验结果表.md](汇报_实验结果表.md) · [汇报_失败原因.md](汇报_失败原因.md) · [汇报_题集构成.md](汇报_题集构成.md) · [汇报_Agent瓶颈案例.md](汇报_Agent瓶颈案例.md) |
| 本地或服务器开始跑实验 | [RUN.md](../RUN.md) · [SERVER_RUNBOOK_PYTHON200.md](SERVER_RUNBOOK_PYTHON200.md) |
| 理解 benchmark 构念 | [BENCHMARK_DESIGN.md](BENCHMARK_DESIGN.md) |
| 设计或审核 task | [TASK_DESIGN_RULES.md](TASK_DESIGN_RULES.md) |
| 确认 source/freeze policy | [BENCHMARK_DESIGN_PRINCIPLES.md](BENCHMARK_DESIGN_PRINCIPLES.md) · [FULL_REPOSITORY_SOURCE_POLICY.md](FULL_REPOSITORY_SOURCE_POLICY.md) |
| 确认 Main、两项核心指标、失败分类和结果留存 | [EVALUATION.md](EVALUATION.md) |
| 写论文 | [paper/](paper/README.md) · RQ3/RQ5 token 切片 [paper/03_results_token_utility.md](paper/03_results_token_utility.md) · RQ6 [paper/04_results_rq6.md](paper/04_results_rq6.md) |

过期方法记录、Rescue+ / V2 负结果和旧组会稿在 [archive/](archive/README.md)。
schema、taxonomy 和语言轨道在 [reference/](reference/README.md)。实验审计在
[reports/README.md](../reports/README.md)；原始运行在 `experiments/`。

当前结果只使用 Functional Pass Rate 和 pass-conditioned / paired RRES 作核心指标。
历史 `summary.passed` 不得代替 evaluator `functional_gate`。当前 **V1 = Main + 2M
cap**，见 [METHOD_V1.md](METHOD_V1.md)。FINDINGS 中的 DeepSeek Python-200 对比仍含
已退役 Lite V1 协议（Main 预算 120 步），不是 Frozen 45 步信封，也不是当前 V1。

不再迭代 Rescue+、V2、TFL 或其它脚手架。Artifact-aware / recency / pre-submit
audit 与 verification-aware 的筛选已停，不要扩到 200。RQ6 Public-feedback
Flash-12 同日成对已齐（Main 0/12 → 4/12），见
[METHOD_RQ6_PUBLIC_FEEDBACK.md](METHOD_RQ6_PUBLIC_FEEDBACK.md)。Spec-adversarial
Hidden-4 已 Kill（Hidden 0→1 = 0/4），见
[METHOD_SPEC_ADVERSARIAL.md](METHOD_SPEC_ADVERSARIAL.md)。论文 RQ3/RQ5
token 切片已有稿；RQ6 机制稿见
[paper/04_results_rq6.md](paper/04_results_rq6.md)。数字不进 Python-200 主表。

`PLAN_EXTERNAL50_EXPANSION.md` 仅为旧 design cards 保留兼容路径，不是当前执行入口。

修改文档后运行：

```bash
python3 scripts/check_docs.py --warnings-as-errors
```
