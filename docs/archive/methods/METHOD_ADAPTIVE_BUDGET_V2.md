# Adaptive Budget V2（已停）

> **Status: archived · Last verified: 2026-08-18**
> Core-12 诊断负结果。不是 Python-200 通过率，不得写入主表。

**V2** = Main 提示 + 1.5M 主轮 + 一次仅用事件/mtime 的进度检查点 + 可选 500K
定向 repair；硬顶 2M。不使用 evaluator public/hidden tests。

Flash Core-12（n=12，诊断）：

| Arm | Functional Pass | Tokens |
| --- | ---: | ---: |
| API Main | 8/12 | 47.1M |
| V1 Main+2M | 4/12 | 22.6M |
| V2 | **2/12** | 21.9M |

V2 对 8/12 题发放了 extra repair，**extra→pass 相对 V1 为 0**。相对 V1 还丢掉
`platformdirs`（检查点把自测循环判成 stall）和 `rich`（repair 改了无关文件；hidden
已过，死在 isolation）。5/8 次 repair 未写任何 submission 文件。

裁决：不扩 Distill-24 / Python-200。早停砍掉转化尾巴；定向 repair 没有合法的
hidden 失败目标。当前 cost arm 仍是 [V1](../../METHOD_V1.md)。
