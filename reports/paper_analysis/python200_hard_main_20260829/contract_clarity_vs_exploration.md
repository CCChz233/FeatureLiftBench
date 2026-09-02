# 契约对齐失败：模型探索不足，还是 TASK 写得不清楚？

> **Status: second-pass causal audit · 19 个一审“契约对齐”功能失败 · human adjudication pending**

## 结论

答案不是简单的二选一。对 19 个此前标为“契约对齐”的功能失败逐题复核后：

| 主归因 | 任务数 | 占 19 题 | 论文处理 |
| --- | ---: | ---: | --- |
| 模型为主 | 12 | 63.2% | 可进入 Agent 失败分析 |
| 模型与 TASK 共同造成 | 3 | 15.8% | 单列 mixed，不宜作强因果结论 |
| TASK 精确判定规则不足 | 4 | 21.1% | 修题前从 Agent 失败分母排除 |

更重要的是，**模型问题并不主要表现为“完全没有深入探索仓库”**。19 题中有 9 题的轨迹属于深度探索、8 题属于中等但范围偏窄、只有 2 题因步数预算耗尽而没有完成。排除 4 道精确判定规则不足的题后，剩余 15 题中仍有 8 题进行了深度探索。

因此更准确的论文结论是：

> 当前 Agent 的主要缺陷不是读取文件太少，而是没有把 TASK 中的功能契约转化为能够区分正确与近似正确实现的验收测试；它经常进行了较深探索，却在错误入口、错误组合或错误 oracle 上完成验证。

## 判定方法

本轮采用两个互不替代的轴，避免用“失败了”反推 TASK 清楚，也避免用“读了很多文件”反推探索有效：

- `explicit_exact`：失败的可观察入口、状态保护、输入变体或异常规则能从运行时 TASK 直接推出。
- `explicit_general`：核心行为明确，但 evaluator 选取的具体表示、操作组合或编码没有逐字规定。
- `underspecified_exact_oracle`：至少存在两种都符合 TASK 字面描述的实现，而 evaluator 只接受其中一种。
- `deep`：轨迹检查了目标实现及相邻入口/依赖，并进行了多轮测试或 differential 对照。
- `moderate`：定位到相关实现并做了验证，但集中于单一入口、表示或 happy path。
- `budget_exhausted`：在形成 TASK 要求的完整接口和最终验证前达到 step limit。

归因规则为：精确契约下遗漏入口、状态或边界，记为 `model_primary`；一般契约下模型仍有合理探索机会、但 evaluator 细节没有完全公开，记为 `mixed`；精确 oracle 无法从 TASK 唯一推出，记为 `task_spec_primary`。

实验容器中 Agent 可见的是 `TASK.md`、`metadata.json`、上游 `repo/`、`requirements.lock` 和空的 `submission/`，不包含 benchmark 的 `public_tests/` 或 `hidden_tests/`。因此，本轮不会把“测试文件里写了例子”视为 TASK 已经向模型公开；如果未来运行协议保证 public tests 对 Agent 可见，可以对相应条目重新裁决。

## TASK 清晰度复核

| TASK 清晰度 | 任务数 | 含义 |
| --- | ---: | --- |
| 精确可判定 | 9 | 失败的入口、状态、边界或输出可由 TASK 直接推出 |
| 核心行为清楚、精确边界未列举 | 6 | 可以要求模型实现核心行为，但对某个表示或组合的归因需保守 |
| 精确 oracle 未公开 | 4 | evaluator 在异常类型、模板绑定或语法形式上选择了 TASK 无法唯一确定的规则 |

需要从原先 19 个“对齐失败”中降级的 4 题如下：

| 任务 | 未写清的精确规则 | 建议 |
| --- | --- | --- |
| Cookiecutter | `{0}/{1}` 如何由 `gh:org/template` 拆分并绑定 | 在 TASK 加入多占位符示例，或改测试为已声明的单参数模板 |
| Decorator | caller 收到原始 `args/kwargs` 形状，还是签名绑定后的等价形状 | 明确“保留调用形状”，给出 keyword 参数示例 |
| Installer | 多个 `.dist-info` 时返回 `None` 还是抛 `ValueError` | 把异常类型写进 Required Behavior/API |
| Yamale | schema primitive 必须支持 `str`/`int` 还是 `str()`/`int()` | 明确文法并给出最小 schema 示例 |

这 4 题不是说 evaluator 的选择一定不合理，而是说**现有 TASK 不足以把未命中该选择稳定归因给模型**。

## 模型到底哪里探索得不够

“探索深度”需要分成两个概念：

1. **原始探索量**：读了多少源码、跑了多少测试、是否追踪依赖闭包。
2. **契约导向的选择性探索**：是否找到了每条公开行为真正生效的入口，并为状态、表示、异常和组合边界建立反例。

本轮结果显示，问题主要在第二项。

| 验证失效方式 | 典型任务 | 证据 |
| --- | --- | --- |
| 测了功能，但测错入口 | Aiohttp、Importlib Resources | 校验或对象构造在局部探针中成立，实际 API 入口仍失败 |
| 测了单项，没有测组合 | Dateutil、Python-decouple | alias/load、quoted value/comment 分开通过，组合路径失败 |
| 自测 oracle 太弱或错误 | Pygments | 测了 `stripall`，但断言没有捕获普通 `Text` 空白 token |
| 遗漏已声明输入变体 | Scrapy、Tox、Zope Interface | class 输入、brace group、错误 value guard 均已由 TASK 直接约束 |
| 深入阅读但没有形成交付 | Pylint、Typer | 源码探索消耗完 step budget，缺失明确导出或子模块 |

### 深度探索仍失败的代表例子

- **Alembic**：Agent 声称通过大量上游与自建测试，但没有验证 merge 后 base revision 仍可查询。这里不是探索量不足，而是任务特定图不变量没有进入自测。
- **Scrapy**：Required API 明确接受 `type[Item] | Item`。Agent 已注意 class/instance 差异，却没有把该类型联合转成两个独立验收用例。
- **Zope Interface**：TASK 明确说 unregister 只删除 matching value。Agent 测了注册和正常删除，却没有测试错误 value 不得改变状态。

### 中等探索、范围偏窄的代表例子

- **Celery**：实现引入了上游对 `**kwargs` 的额外限制，自测没有使用零参数普通 callable。
- **Python-decouple**：39 项本地测试仍漏掉“带引号值 + 行尾注释”的交叉组合。
- **Tox**：测试了复杂表达式，但漏掉 evaluator 使用的最直接 brace group 边界。

## 论文应如何表述

可以使用的强结论：

> 在严格可归因的 12 个模型主因失败中，失败更常来自契约操作化与验收 oracle 的缺口，而非完全缺少仓库探索；大量源码读取和自选测试并不能保证跨模块功能契约闭合。

需要保守处理的结论：

- 不应直接写“19 个契约对齐失败全是 Agent 失败”；二审发现其中 4 个精确 oracle 未公开。
- 3 个 mixed 题（Dateutil、Keyring、MkDocs）可用于讨论任务表达与模型推理的交互，但不宜单独支撑模型能力百分比。
- “探索深度”不能仅用工具调用数或读取文件数衡量，应报告**契约条款覆盖率、入口覆盖率、状态转移覆盖率和组合边界覆盖率**。

## 对 benchmark 和 Agent 的直接改进

Benchmark 侧：

1. 为每个 evaluator 断言维护 `TASK clause -> observable assertion` 映射。
2. 对异常类型、默认值、字符串文法、registry key 编码和多参数模板等不可自然推出的规则，必须在 TASK 中给最小例子。
3. 主表前对本表 4 个 `underspecified_exact_oracle` 题修订并重新评测；修订前不计入 Agent 失败分母。

Agent 侧：

1. 先把 Required API 的联合类型、异常、状态保护和平台参数展开成验收矩阵，再读实现。
2. 每条契约至少生成一个正例和一个反例；组合语法需做 pairwise 交叉。
3. 最终验证必须走公开入口，不能只测内部 helper 或等价局部探针。
4. 若自测与上游行为冲突，应优先回到 TASK 寻找可判定证据；TASK 不可判定时标记不确定，而不是宣布完全完成。

## 证据与限制

- 母表：`failure_process_analysis.csv`
- 本轮逐题标注：`contract_clarity_vs_exploration.csv`
- 原始轨迹：`experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/*/agent/openhands_events.jsonl`
- evaluator 证据：同目录各任务的 `eval/logs/public.stdout` 或 `hidden.stdout`
- 本轮没有重跑实验；结论来自保留的运行时 TASK、提交、轨迹和首败日志。
- 当前是单 reviewer 二审。论文定稿前，4 个 TASK 主因和 3 个 mixed 项应由第二位 reviewer 独立裁决。
