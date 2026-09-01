# 导师汇报：FeatureLiftBench 论文进展与转向建议

> **用途：** 2026-08-31 向导师汇报论文进展。  
> **建议时长：** 10–15 分钟主讲，其余内容作备用。  
> **数字口径：** 以 [`STATUS.md`](STATUS.md) 和 [`FINDINGS.md`](FINDINGS.md) 为准。  
> **一句话结论：** 论文建议从“提出一个稳定涨分的 Agent 方法”转向 **Benchmark + Empirical Analysis**；方法实验不是删掉，而是作为负结果和失败机理证据。

---

## 1. 我希望导师今天帮我判断什么

我希望导师重点判断四件事：

1. 是否同意将论文定位为 **仓库级功能抽取 Benchmark + 实证分析**，不再以方法涨点为主贡献。
2. 论文主套件是否坚持使用 **Python-200′ = 冻结 Python-150 + Hard-50**，将过易的 External-50 降为旁路对照。
3. 新主套件的跨模型实验做到什么深度：至少补一个中等能力模型，还是做 3–4 个模型的完整梯度。
4. Hidden 公平性审计、多次运行稳定性、第二 Agent runtime 这三项中，哪些必须在投稿前完成。

---

## 2. 建议的开场（可直接照着讲）

> 我目前已经完成了 FeatureLiftBench 的核心任务资产：我们定义了一个现有代码基准没有直接覆盖的任务——让 Agent 从完整、相互纠缠的仓库中，抽出一个行为完整、可独立安装、且相对紧凑的功能包。
>
> 我原来希望在这个 benchmark 上再提出一个能稳定提升成功率的 Agent 方法。但我试了自测、合同检查、repair、上下文压缩、自适应预算和 checkpoint 等多类合法干预，都没有相对最强 Main baseline 产生稳定、可复现的 Functional Pass 提升。
>
> 这些负结果不是单纯的“方法失败”。它们共同指向一个反复出现的现象：当 Agent 看不到评测测试时，往往能找到相关代码、交付可构建的包、甚至通过主路径，但仍然无法把公开契约里的边界行为完整闭合。在已测子集和协议中，现有脚手架可以改善过程，却很难补上 Hidden 层的行为缺口。
>
> 因此我想请您判断：我们是否应该把论文主线调整为“一个新的仓库级评测任务，加上对当前 Agent 能力边界的系统分析”。

### 汇报时的语气

不要说“方法做不出来，所以退而求其次做 benchmark”。建议说：

> **方法实验没有形成稳定的主表提升，但它们让我们看到了一个稳定且可研究的能力缺口。论文转向是由证据推动的，不是降低目标。**

---

## 3. Benchmark 到底测什么

### 3.1 任务不是修 bug，也不是从零写代码

Agent 获得：

- 一个完整、固定 commit 的真实 Python 仓库；
- 完整的公开功能契约（`TASK.md` / `public_spec`）；
- 可以自由阅读和修改的仓库上下文。

Agent 不获得：

- 源码位置提示；
- Public / Hidden 评测测试；
- 参考实现。

Agent 需要交付一个可独立安装的 `featurelifted` 包，不允许运行时回连原仓库。

### 3.2 评测是确定性的

\[
\text{Functional Pass}
= \text{Build} \land \text{Public} \land \text{Hidden} \land \text{Isolation}
\]

- **Public** 验证公开契约的主路径。
- **Hidden** 验证同一契约中的边界、异常类型、导出和保真细节。
- **Isolation** 检查提交物能否真正脱离上游独立运行。

对于功能通过的提交，再单独报告 **RRES**（相对参考实现的归一化规模），用于区分“功能做对”和“抽取得紧凑”。两者不加权成一个总分。

### 3.3 论文主套件已成型

| 范围 | 任务 | 仓库 | 论文角色 |
| --- | ---: | ---: | --- |
| 冻结 Python-150 | 150 | 127 | 基础主套件 |
| Hard-50 | 50 | 50，与 150 仓库不重叠 | 经强模型校准的难子集 |
| **Python-200′** | **200** | **176** | **新论文主套件** |
| External-50 | 50 | 50 | 过易 / copy-heavy 的旁路对照 |

Hard-50 的 Flash 独立设计校准为 **29/50 = 58%**，落在预设的 40%–65% 目标带。External-50 上 Flash 达到 90%–94%，且大量通过解接近整仓复制，因此不再适合稀释主表难度。

这部分可以对导师概括为：

> Benchmark 的核心资产已经成型：任务定义、题集、冻结源码、确定性评测、隔离检查和离线依赖都已经具备。当前欠缺的是论文级实验闭环，而不是重新设计任务。

---

## 4. 当前 Agent 在这个 Benchmark 上暴露了什么

### 4.1 不要把结论简化成“Agent 找不到代码”

现有证据更支持如下表述：

> **当前 Agent 已经具备一定的仓库导航、代码复用和包交付能力；更难的是在 No-Hint、test-blind 设定下，将公开契约中的主路径和边界行为全部闭合。**

这是一个证据支持的诊断，不是排他性因果结论：我们还没有对每条轨迹的 localization 进行独立金标标注。

### 4.2 跨模型结果说明这个任务有明显的能力梯度

在已被新套件取代的旧 Python-200（150 + External-50）上，Full-Repository / No-Hint Main 的 Functional Pass 从 **21.5% 到 72.5%**：

| 模型 | Functional Pass | 用途 |
| --- | ---: | --- |
| DeepSeek V4 Flash | 144–145/200（72.0%–72.5%） | 强模型能力上限，但被过易 E50 抬高 |
| Qwen3.5 122B / Qwen3.6 35B | 95–96/200（约 48%） | 中间能力带 |
| GPT-OSS 120B | 43/200（21.5%） | 弱模型对照 |

这张表只证明“任务能区分模型”，不是新 Python-200′ 的最终主表。

### 4.3 强模型不是只在第一关失败

旧套件上，Flash API Main 的互斥结果为：Pass 144、未交付 5、Build 2、Public 27、Hidden 22、Isolation 0。在已经进入行为评测的失败中，有很大一部分是 **Public✓ Hidden✗**：主路径看起来完成了，但边界行为仍不完整。

弱模型则更容易早一层卡在 Public。Isolation 首败在已统计主结果中接近 0，因此“偷偷 import 上游”不是当前主故事。

### 4.4 三个真题案例可以把“契约闭合”讲清楚

| 任务 | Agent 表面上已经做到 | 实际失败点 |
| --- | --- | --- |
| `itsdangerous` 定时签名 | 加签、解签、roundtrip 正常 | 过期时应抛 `SignatureExpired`，而不是笼统签名错误 |
| `configobj` 配置读写 | 能读、能写回 | 注释保留、`configspec` 校验等保真契约没有闭合 |
| `requests_cache` cache-key | 找到并复制了相关实现 | 缺少契约要求的 `normalize_body` 导出 |

一句话概括：

> **会签名不等于过期语义正确；会读写配置不等于保真；找到代码甚至大段复制，也不等于契约闭合。**

详细案例见 [`汇报_Agent瓶颈案例.md`](汇报_Agent瓶颈案例.md)。

---

## 5. 我们试过哪些改进，为什么没有形成方法论文

不建议在汇报时按实验时间线逐个念方法名。更清楚的讲法是：我们验证了四类假设，但没有哪一类产生稳定的 Functional Pass 收益。

| 原始假设 | 已尝试干预 | 代表证据 | 现在的解释 |
| --- | --- | --- | --- |
| Agent 只是不会验证 | 自编探针、先测后写、verification ledger | TD 与 Main 持平；TFL 低于 Main 且 token 约 ×2.7；VA 14/24 < 同日 baseline 16/24 | 自编测试容易围绕 Agent 已有的错误假设打转 |
| Agent 缺一个更强的契约检查 | Self-Contract、Exec-Contract、Spec-adversarial | 可以挡住空包或救回 Public，但 Spec-adversarial Hidden-4 仍为 0/4 | 把公开契约变成 checklist，不会自动生成缺失的边界语义 |
| Agent 需要第二轮 repair 或保留最佳中间包 | PDR、Rescue+、Best-so-far | PDR 持平且更贵；Rescue+ 无稳定增益；51 道失败题的全部独特中间树中 0 道曾经过关 | 许多失败轨迹中根本没有出现过正确解，不是最后一次修改把它覆盖了 |
| Agent 只是预算和上下文用得不够聪明 | 2M token cap、自适应早停、压缩上下文、结构提示 | Qwen 干净 E50 成对子集 Main 35 → cap 19；Flash Core-12 8 → 4；其他支架未稳定涨分 | 省 token 不等于提升正确性；早停还可能截掉后程转化 |

### 5.1 一个很重要的对照：Public 和 Hidden 可以被分开移动

在同一模型、同一批 12 道题、同一天的成对实验中，唯一变化是将 `public_tests/` 提供给 Agent，Hidden 始终不可见：

| 条件 | Functional Pass |
| --- | ---: |
| Main（看不到评测测试） | 0/12 |
| Public-feedback | 4/12 |

更关键的是：

- 6 道 Public 失败题的 Public 层 **6/6 被救回**；
- 5 道原本就是 Hidden 失败的成对题中，**4/5 的 Hidden 不变**。

这支持一个比“Agent 不会自测”更精确的判断：

> **可执行的 Public 反馈能修复一部分主路径，但并不等于 Hidden 行为信息。Public 失败和 Hidden 失败是两层不同的问题。**

### 5.2 负结果应该如何进入论文

这些实验不进主 leaderboard，也不包装成一个成功方法。它们可以用于：

- 证明简单增加自测、repair 或预算管理不足以解决任务；
- 将失败从“没有调好 prompt”提升为“信息边界下的契约闭合问题”；
- 支持 Discussion 中对未来 Agent 的设计要求：更好的契约推理、边界例生成、完整性证据和停机判断。

---

## 6. 为什么这可以是一篇 Benchmark + Analysis 论文

### 6.1 论文不是“只发布一批题”

建议锁定四项主贡献：

1. **新任务。** 形式化 repository-level, behavior-preserving feature extraction，并明确 Full-Repository / No-Hint / test-blind 信息边界。
2. **新 Benchmark。** 200 道真实 Python OSS 任务、176 仓，冻结源码与评测；包含校准难子集和 copy-trap 题。
3. **双轴评测。** 将行为正确性（Functional Pass）和抽取紧凑度（RRES）分开，配合确定性 Docker evaluator 和互斥失败漏斗。
4. **实证发现。** 分析跨模型能力梯度、契约闭合失败、Public/Hidden 信息差异、紧凑度和 token 无效尾部，并系统报告脚手架负结果。

### 6.2 论文的中心主张

可以先用一句工作性 thesis 统一全文：

> **FeatureLiftBench 揭示，当前代码 Agent 已能在完整仓库中产生看似可用的功能包，但仍系统性地困难于在不可见评测下完成行为契约闭合；正确性与紧凑度也是两个不能相互替代的能力维度。**

这句话在论文中最终必须用新主套件的合格数字、Hidden 公平性审计和轨迹案例来支撑。在这些证据闭环前，它是研究假设，不是已经完全证实的因果结论。

### 6.3 汇报时将六个 RQ 压缩成四个问题

正文可以继续保留完整 RQ1–RQ6，但向导师汇报时可压缩为：

1. **能力：** 当前 Agent 在仓库级功能抽取上能做到什么？
2. **质量：** 通过的提交是否真正独立且紧凑？
3. **失败机理：** 它们失败在哪一关，受哪些任务纠缠因素影响？
4. **信息与资源：** Public 反馈、上下文、预算和脚手架如何改变结果？

---

## 7. 对当前实验结果必须保持的诚实口径

### 7.1 新 Python-200′ 还没有可以写进摘要的最终分数

2026-08-29 收到的 Flash 结果包记录了 **132/200 = 66.0%**，但这只是 **received-suite audit headline**：

- 只有 183 题真正启动 Agent；
- 17 题在启动前被 freeze 哈希检查挡住；
- 16 题的首败是评测端离线依赖不足，不是模型生成包构建失败；
- 59 题触发 context-window 资格审计，其中 37 题功能通过；
- 三类问题去重后，严格替换集合为 **84 题**。

固定不动的 116 题中有 95 题通过。因此 66% 不能作为 leaderboard 或摘要数字，95/200–179/200 也只是替换前的逻辑压力范围，不是对最终成绩的估计。

### 7.2 严格替换已经启动，但还有一个论文级资格问题

当前已完成：

- 冻结 Python-200′ 输入的独立物化与校验；
- CPython 3.11 Linux 离线 wheel 闭包 **200/200**；
- 84 题严格替换列表冻结；
- 独立替换目录已启动，不覆盖原始收到包。

但当前替换运行使用的 agent / evaluator 镜像 digest 与 2026-08-29 收到包不同。因此这批结果可以用于验证工程闭环，但在不加条件地按 task ID 合并成最终主表之前，必须二选一：

1. 找回并使用原包的同一镜像身份重跑 84 题；或
2. 使用当前固定镜像干净重跑全部 200 题。

第二种成本更高，但作为论文主表更干净。这是本次需要向导师主动披露的实验设计问题。

### 7.3 汇报时不要说错的话

| 不要说 | 建议表述 |
| --- | --- |
| “我们新主表是 72% 或 66%” | 72% 属于旧 150+E50；66% 是新包审计 headline，最终分数待合格重跑 |
| “Hard-50 已证明比 150 难” | 29/50 是独立设计校准；收到包的 split 对比被基础设施反向混杂 |
| “Agent 主要不会定位” | 案例和漏斗显示大量失败在主路径或 Hidden 行为；但 localization 还没有独立金标 |
| “Hidden 失败都是模型的问题” | Hidden 契约公平性还需要双视角审计和敏感性分析 |
| “我们的新方法提升了成功率” | 已试脚手架没有稳定超过 Main，它们作为负结果和机理证据 |
| “Agent 运行状态 passed 才算过” | 论文只认 evaluator `functional_gate`，不用 workflow 退出状态当成绩 |

---

## 8. 接下来的论文执行路线

接下来不建议继续横向新开 Agent 方法。应按“前一道证据闸门合格，再扩下一道”的方式推进。

### Gate A：获得可投稿的单模型主表

- 固定任务输入、Agent 配置、prompt、预算、依赖和两个 Docker 镜像身份。
- 解决当前 84 题替换与原包镜像不同的资格问题。
- 产出 Python-200′ / Python-150 / Hard-50 三个切片的 Functional Pass、互斥失败漏斗与 RRES。
- 在此之前，摘要不写最终分数。

### Gate B：将“Agent 缺陷”做成可审查的分析

- 完成失败漏斗和代表性案例卷宗；
- 将“契约闭合”拆成可编码类别：缺导出、错误语义、边界值、状态/资源闭包、保真缺失等；
- 对一个分层样本进行双视角独立审计，优先使用双人复核；如果使用双 Agent，必须明确标注为 AI-assisted，不当作 human gold 或人类标注一致性；
- 将基础设施失败与模型/输出失败严格分开。

### Gate C：补齐新套件的跨模型证据

最低可接受方案：Flash + 一个中等能力模型，旧 Python-200 只作为历史对照。

更完整的方案：强 / 中 / 弱至少三个能力带，全部使用同一冻结的 Python-200′ 主套件和运行配置。

### Gate D：做 Hidden 公平性和稳健性审计

- 报告全量 / observable-only / conservative 三组 Hidden 敏感性口径；
- 对分层子集做多次运行，评估 Pass@1 的波动；
- 如果不做第二 runtime，正文必须将结论收窄为“在 OpenHands Official Main 协议下”。

### Gate E：冻结 Paper Bundle 并写作

- 冻结 suite SHA、freeze id、镜像 digest、逐题评测结果和重建命令；
- 正文数字只从 paper bundle 生成；
- 同步写 Task、Benchmark Construction、Evaluation Protocol 和 Limitations，不等所有模型跑完再动笔。

---

## 9. 建议的论文结构

1. **Introduction**：功能抽取不等于 issue repair、定位或绿场生成。
2. **Task Formulation**：Full-Repository / No-Hint / test-blind 设定与行为保持目标。
3. **Benchmark Construction**：真实仓库、题集冻结、Hard-50 校准、taxonomy 和 leak 防护。
4. **Evaluation Protocol**：Functional Pass、RRES、失败漏斗与确定性 evaluator。
5. **Main Results**：新 Python-200′ 跨模型主表、分片与紧凑度。
6. **Failure Analysis**：契约闭合类型、典型案例、任务因素。
7. **Information and Resource Analysis**：Public-feedback、\(T^*\)、token 尾部和脚手架负结果。
8. **Related Work and Discussion**：与 issue repair、code generation、repository understanding 和 agent benchmark 的区别。
9. **Limitations and Reproducibility**：Hidden 可观测性、runtime 绑定、单次运行、taxonomy 标注。

---

## 10. 10–15 分钟口头汇报顺序

| 时间 | 讲什么 | 只记住的一句话 |
| --- | --- | --- |
| 0:00–1:30 | 研究问题与转向建议 | 这是证据驱动的转向，不是退守 |
| 1:30–4:00 | Benchmark 任务和题集 | 测的是仓库级、独立、行为保持的功能抽取 |
| 4:00–7:00 | Agent 缺陷与三个案例 | 找到和复制代码不等于契约闭合 |
| 7:00–9:00 | 四类方法假设与负结果 | 过程支架可以救 Public，但未稳定提升 Functional |
| 9:00–11:00 | Benchmark + Analysis 论文主张 | 新任务 + 新评测 + 新题集 + 能力边界分析 |
| 11:00–13:00 | 证据缺口与下一步 | 先做干净主表和 Hidden 审计，停止新开方法 |
| 13:00–15:00 | 请导师拍板 | 定位、跨模型深度、稳健性要求和投稿范围 |

---

## 11. 汇报前 5 分钟检查清单

- [ ] 检查 84 题替换运行的最新进度，但不将中途通过率当成结果。
- [ ] 如果替换已跑完，仍先检查镜像 digest、context 资格和 Docker evaluator 合格性。
- [ ] 如果还没有合格主表，保留“66% 只是 audit headline”的表述。
- [ ] 主讲只展示三张证据：题集定义、失败漏斗/案例、方法负结果分组表。
- [ ] 把“希望导师拍板的四个问题”放在结尾，不要以“您觉得怎么办”泛泛收尾。

---

## 附录 A：一页纸版本

**论文定位**

FeatureLiftBench：仓库级、行为保持的功能抽取 Benchmark + Empirical Analysis。

**Benchmark**

200 题，176 仓；冻结 Python-150 + Hard-50。评测 Functional Pass 与 RRES，前者测正确性，后者测通过解的紧凑度。

**核心发现**

当前 Agent 往往能找到并复用相关代码，但在 test-blind 设定下容易出现契约闭合失败：主路径通过，边界行为、异常语义、导出或保真性不完整。Public-feedback 能救 Public，但 Hidden 多数不动。

**方法结论**

自测、契约检查、repair、checkpoint、预算和上下文脚手架均未稳定超过无帽 Main。这些不作为新方法主表，而作为信息边界与失败机理的证据。

**当前缺口**

新套件还没有论文合格的最终主表；84 题替换已启动，但与原包镜像 digest 不同。还需要新套件跨模型实验、Hidden 公平性审计和至少一项稳健性证据。

**建议决策**

停止新开方法，先完成合格主表、契约闭合分析、Hidden 审计和跨模型证据，将论文写成 Benchmark + Analysis。

---

## 附录 B：证据索引

| 内容 | 文档 |
| --- | --- |
| 当前题集、结果和资格口径 | [`STATUS.md`](STATUS.md) |
| 方法结论与负结果 | [`FINDINGS.md`](FINDINGS.md) |
| 题集构成 | [`汇报_题集构成.md`](汇报_题集构成.md) |
| Agent 失败案例 | [`汇报_Agent瓶颈案例.md`](汇报_Agent瓶颈案例.md) |
| 收到包审计 | [`paper_readout.md`](../reports/paper_analysis/python200_hard_main_20260829/paper_readout.md) |
| 失败与 context 审计 | [`failure_audit.md`](../reports/paper_analysis/python200_hard_main_20260829/failure_audit.md) · [`context_audit.md`](../reports/paper_analysis/python200_hard_main_20260829/context_audit.md) |
| 严格替换任务列表 | [`strict_replacement_task_ids.txt`](../reports/paper_analysis/python200_hard_main_20260829/strict_replacement_task_ids.txt) |
| 论文 RQ | [`paper/02_research_questions.md`](paper/02_research_questions.md) |
| 顶会准备闸门 | [`paper/07_top_conference_readiness_plan.md`](paper/07_top_conference_readiness_plan.md) |
