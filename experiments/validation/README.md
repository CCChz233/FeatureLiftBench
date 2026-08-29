# Validation Evidence

> **Documentation status: reference · Last verified: 2026-08-29**

本目录是 **raw validation**（reference / oracle / preflight / 校准），不是
OpenHands leaderboard。新的模型主榜跑分写入 `experiments/python/`。

| Path | Role |
| --- | --- |
| [`hard50/`](hard50/README.md) | Hard-50 Flash 校准、copy-heavy 换题、pilot gate（2026-08-29 从 experiments 根迁入） |
| [`agentic_evidence/`](agentic_evidence/README.md) | Hidden provenance 审计 workspace；小结在 `reports/agentic_evidence/` |
| `batch3/` | 历史 100→150 reference evaluation |
| `external50/` | External-50 reference audit |
| `v1_1/` | control、oracle、infra 和 repair validation |

这些目录是构建与审计证据。Hard-50 校准数字能否写进 STATUS 由
[`docs/STATUS.md`](../../docs/STATUS.md) 决定。
