# Method Experiments

> **Documentation status: archived evidence · Last verified: 2026-08-29**

本目录保存方法 pilot、ablation、负结果，以及 **不进主表** 的 screening。
它们不是 OpenHands Python-200' leaderboard。

| Path | Role |
| --- | --- |
| `autosaddler_flb/` | AutoSaddler prompt-only screening（进行中的对接试验） |
| 其余 `*_pilot/`、`contract_closure_*`、`ablation/` | 已停脚手架 / 历史负结果 |

V1 Core-12 诊断路径以 [METHOD_V1.md](../../docs/METHOD_V1.md) 为准（不一定仍在本目录顶层）。

方法解释：当前臂见 [`docs/FINDINGS.md`](../../docs/FINDINGS.md)；停用稿见
[`docs/archive/methods/`](../../docs/archive/methods/README.md)。
AutoSaddler 规范见 [`docs/archive/methods/METHOD_AUTOSADDLER.md`](../../docs/archive/methods/METHOD_AUTOSADDLER.md)。

新正式 ablation 应使用标准 Python suite 布局，并在 metadata 中登记 arm。
