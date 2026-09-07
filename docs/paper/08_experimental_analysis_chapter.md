# Experimental Analysis 章节写法与后续分析大纲

> **Status: current · Last verified: 2026-09-06**  
> **用途：** 规定论文 *Experimental Analysis / Results & Analysis* 写什么、按什么顺序写、用哪些分母。后续实验分析按本文执行。  
> **Headline：** freeze v2 **Python-150** Official Main。官方 Hard-50 进附录。

操作层标注规范仍以
[FAILURE_ANALYSIS_PROTOCOL.md](../FAILURE_ANALYSIS_PROTOCOL.md)
为准。**怎么跑一轮 5.3 / Finding 3** 见
[FAILURE_ANALYSIS_SOP.md](../FAILURE_ANALYSIS_SOP.md)。
分类词表见
[05_failure_taxonomy.md](05_failure_taxonomy.md)。
本文只规定**这一章的论证顺序和可写结论**。

## 0. 冻结输入

主套件：Python-200′ freeze v2
`6c20ff0307762503a73cbb9ff32e9992c6446e4b17483a68373027be58cbf419`，
candidate `212930ea`。协议：OpenHands Official Main，Full-Repository / No-Hint。

| 配置 | 输出目录 | 本章角色 |
| --- | --- | --- |
| DeepSeek V4 Flash（官方 API） | `experiments/python/openhands/deepseek-v4-flash/python200-prime-v2-main-r1` | 主表 |
| gpt-5.6-luna（OpenLux，非官方 OpenAI） | `experiments/python/openhands/gpt-5.6-luna/python200-prime-v2-main-r1` | 主表；表内标明 OpenLux |
| Qwen3.6-35B-A3B-FP8（本机 vLLM :8008） | `experiments/python/openhands/qwen3.6-35b-a3b-fp8/python200-prime-v2-main-r1` | 主表 |
| GPT-OSS 120B（本机 vLLM :8009） | `experiments/python/openhands/gpt-oss-120b/python200-prime-v2-main-r1` | 主表 |
| GLM-5.3-Flash | `experiments/python/openhands/glm-5.3-flash/python200-prime-v2-main-r1` | 主表（2026-09-06 收工；Python-150 **68/150**） |
| 旗舰 GLM-5.3 错跑归档 | `.../glm-5.3/python200-prime-v2-main-r1.aborted-flagship-not-flash` | 不进主表 |

镜像：`featureliftbench-agent:python200-prime-212930ea` 与对应 eval 镜像。

**这是唯一正确的 freeze v2 Official Main 主表**（2026-09-04/05 收完，24 题补跑已叠回同一 200）。不要用 20260829、9 月 2 日另一套 Qwen、或补跑叠回前的 143/132/80。

| 模型 | Functional Pass | 空卷 |
| --- | --- | --- |
| DeepSeek V4 Flash | **157/200（78.5%）** | 0 |
| Luna (OpenLux) | **144/200（72.0%）** | 1 |
| GLM-5.3-Flash | **98/200（49.0%）** | 45 |
| Qwen3.6-35B | **86/200（43.0%）** | 31 |
| GPT-OSS 120B | **61/200（30.5%）** | 1 |

写回：[`reports/paper_analysis/python200_prime_v2_results_20260905/`](../../reports/paper_analysis/python200_prime_v2_results_20260905/README.md)。

**禁止混入本章主表的数字：** freeze `474862c2` 的 132/200 audit headline；旧 150+E50 的 21.5%–72.5%；Core-12 / RQ6 Flash-12 / Lite / 方法臂通过率；把 Qwen 空卷踢出分母后的 86/169。

主指标永远是 **Functional Pass = Build ∧ Public ∧ Hidden ∧ Isolation**。不要用 `run.status`。

150 / Hard-50 分组用 freeze 里每题的 `stratum`（`python150` / `hard50`）。先算再写「Hard-50 更难」，不要预设 drop 幅度。

## 1. 本章固定为 6 节

顺序不要改：先总体能力，再失败位置，再（短）过程层净化，再失败原因，再任务难度，再成功解质量，最后案例收束。

过程层**不要**升级成第 7 个 RQ，只作 5.2 的小节。

| 节 | 回答的问题 | 核心图/表 | Finding |
| --- | --- | --- | --- |
| 5.1 Overall Capability | 当前 Agent 有多强？ | 主 leaderboard | F1：未解决 + 模型间有差异 |
| 5.2 Failure Stage | 首先卡在哪一闸？ | Missing→…→Pass stacked bar | F2：失败主要在行为闸门 |
| 5.2.1 Process vs capability | 多少失败没真正进入考试？ | 空卷 / TVE / 超时 / 步数 | 短句：过程失败 ≠ Hidden 失败 |
| 5.3 Failure Mechanism | 为什么失败？ | 有包失败的 semantic 表 | F3：是否存在 Contract-Closure Gap |
| 5.4 Task Difficulty | 什么题更难？ | Lift Type / Entanglement / stratum | F4：难度随任务属性变化 |
| 5.5 Extraction Quality | 过题是抽取还是复制？ | 过门子集 RRES / copy fraction | F5：正确性与紧凑度是两维 |
| 5.6 Case Studies | 现象具体长什么样？ | 3–4 个案例 | 解释 Locate–Close–Isolate，不再单列 Finding |

每条未通过运行仍走协议四层：证据有效性 → 互斥首败阶段 → 语义根因 →（可选）轨迹过程原因。

## 2. 5.1 Overall Capability

**只回答能做到什么程度。不讲 TVE、contract closure、RRES。**

开场一句设定：

> We evaluate six model–agent configurations on frozen Python-150 under the same Full-Repository / No-Hint protocol.

然后直接放主表，列至少包括：Model、Functional Pass@1（150）、Core-100、hard3、Wilson 95% CI、空卷。Luna 写 `gpt-5.6-luna (OpenLux)`。官方 Hard-50 不进此表。

正文不要逐行复述表格。只分析三刀：

1. **Ceiling：** 最强配置距解决 benchmark 还有多远。例：Pro 76.7%，仍有 35 题未过。  
2. **Discrimination：** 模型差距。例：Pro 比 Qwen 高 34.7 个百分点；Pro vs Flash 不写显著更强。  
3. **hard3：** 用 150 内部 construction split，不要用官方 Hard-50 当难度打穿。

收束：

> **Finding 1.** Current coding agents exhibit substantial but incomplete feature-lifting capability, with large performance differences across model backends.

正式成绩不得改写为 Qwen 80/172。

## 3. 5.2 Failure Stage

问：没过的题首先挂在哪一层？用互斥首败：

```text
missing_submission
  → build_failure
  → public_failure
  → hidden_failure
  → isolation_failure
  → functional_pass
```

三模型并排 stacked bar。分析**分布形状**，不要报流水账。

1. Build 是否薄：若薄，说明多数交付物装得上，失败发生在成包之后。  
2. Public vs Hidden：若质量心在行为闸门，给 5.3 铺路，但本节**还不准命名** Contract Closure。  
3. Isolation 是否几乎没有：若少，行为过关后很少只因依赖源仓而挂；若多，独立性本身是难点。

> **Finding 2.** Functional failures concentrate primarily at the behavioral gates, indicating that producing a buildable package is substantially easier than recovering complete required behavior.

（若数据不支持「主要在行为闸门」，改写成实际质量心，不要硬套此句。）

Qwen 的 missing 会抬高 stacked bar。读者会误读成「不会交包」。**5.2.1 必须紧跟。**

## 4. 5.2.1 Process vs capability

篇幅短。目的：把 harness/过程失败从后面的语义分母里拿掉。**不是洗分。**

先写：

> Functional Pass remains the benchmark score regardless of process status.

再写：部分失败发生在可评测包出现之前。Qwen 28 题因 OpenHands `security_risk` 校验（TVE）空卷，中位约数十秒；这些题主表仍计失败，**不能**证明 Hidden 语义失败。Luna 第一轮 `invalid_encrypted_content` 空卷经整题补跑后为 0，脚注交代 OpenLux 协议即可。

过程现象三分开，禁止混成一种「TVE 失败」：

| 过程现象 | 主表 Functional Pass | 是否进入 5.3 分母 |
| --- | --- | --- |
| 空卷（无可用 submission） | 失败 | **否** |
| 有包且 gate=0，中途 TVE / 步数顶 / 超时 | 失败 | **是** |
| 有包且 gate=1，但 rc=86 / 123 / 124 | **通过** | 不是失败 |

可留一句、不要升级成与 F1/F2 并列的主 Finding：

> Process failures materially affect some model–harness configurations, but they are analytically distinct from artifact-level feature-lifting failures.

禁止：「Qwen 真实能力是 80/172」。

## 5. 5.3 Failure Mechanism

本章最重要的一节。5.2 回答 Where，本节回答 Why。

**分母：** 有 submission 且 `functional_gate = 0` 的题。空卷留在 5.2.1。  
**禁止：** 从 evaluator 最后一行自动推出语义原因。  
**证据：** 公开契约、最终包、源码证据、轨迹、评测日志。不足则 `unknown`。

Primary semantic cause 五类 + unknown（可加 secondary，不得重复计入分母）：

| 类 | 可观察含义 |
| --- | --- |
| Localization Failure | 未找到关键实现证据 |
| API / Contract Closure | 大方向对，required API/member/签名不完整 |
| Dependency / Resource / State Closure | 核心代码在，缺 helper、registry、config、全局状态、资源、schema、生命周期 |
| Behavioral Drift | 表面 API 在，异常、边界、返回、状态迁移或 preservation 不一致 |
| Packaging / Isolation | 逻辑大致对，但不能独立安装/隔离 |
| Unknown | 证据不足 |

Public fail ≠ 一定是 closure，也可能是 localization。Contract-Closure Gap 必须由
**API/Contract Closure + Dependency/State Closure + 一部分 Behavioral Drift**
的质量支撑，不能从「Public/Hidden 人多」直接命名。

Unknown 比例高就如实写 substantial fraction remains uncoded，不要为饼图硬标。

> **Finding 3.** （仅当闭合类明显大于 localization 时）Artifact-level failures are dominated by incomplete recovery of the required behavioral contract (a contract-closure gap), rather than by inability to emit an installable package.

Python-150 freeze v2 的 Pro+Flash 有包失败已做到 **L1 + 轨迹筛 + 过程筛**（不是 L2）：有效分母 63，闭合类 61，localization 0。Luna/Qwen/OSS 有分层后抽（45 条 L1，有效 32），**不要并进 63**。后抽未推翻 Pro+Flash 的 closure 方向；Qwen/OSS 样本额外出现 packaging / dependency_closure。可把 Finding 3 写成助手第一遍、分母仅这两家；根因比例不得当金标。执行步骤与 L0/L1/L2 质量档见 [FAILURE_ANALYSIS_SOP.md](../FAILURE_ANALYSIS_SOP.md)。

## 6. 5.4 Task Difficulty

分组 Functional Pass：Lift Type、Entanglement、`stratum`（150 vs Hard-50）。只报相关，不写因果。

分组前把 Qwen 空卷标成 process，避免「某 lift type 上 Qwen 特别差」其实是 TVE 撞号。

> **Finding 4.** Feature-lifting difficulty varies with task attributes such as lift type, entanglement, and the Hard-50 calibration stratum.

无显著差异就写不了这句，改成难度并非由单一属性主导。

## 7. 5.5 Extraction Quality

**只在 `functional_gate = 1` 的题上**报 RRES / extraction_ratio / copy fraction。正确性与紧凑度拆开。跨模型比紧凑度只用三家都过的 **paired 交集**。Hard-50 与 Python-150 的 RRES 分开。Copy-heavy pass 是成功质量，不要塞回 5.2 的 Isolation fail。

> **Finding 5.** Correctness and compactness are distinct: a functional pass does not imply a compact extraction relative to the frozen reference.

## 8. 5.6 Case Studies

3–4 个，每个只服务前面一个 Finding，用 Locate–Close–Isolate 叙事，不新开故事。

| 案例 | 服务 |
| --- | --- |
| TVE / 空卷 | 5.2.1 |
| Public 未闭合 | 5.3 |
| Hidden 行为漂 | 5.3 |
| 过门但 RRES 极差 / 拷太多 | 5.5 |

不公开 Hidden 测试名、输入或断言；只用稳定契约编号和脱敏摘要。

章末收束一段：benchmark 未饱和；失败在行为闸门；有包失败以契约闭合为主（若 F3 成立）；过门后紧凑度是第二维。本章不承诺新 Agent 方法。

## 9. 分析执行顺序（写稿前）

1. 资格核对：freeze、镜像、200 题均有 `run.json`。  
2. 出主表 + Wilson CI + 150/Hard-50。  
3. 出互斥漏斗 stacked bar。  
4. 过程层计数（空卷 / TVE / 超时 / 步数；与 gate 交叉）。  
5. 有包失败集合上做语义标注（可先分层抽样，不必 200 题全标）。  
6. 任务属性分组。  
7. 过门子集 RRES 与 paired 子集。  
8. 选案例、写 5.1–5.6。

可复用闸门优先级逻辑（如 `harness/scripts/analyze_python200_hard_main.py`），**输入必须是上表 freeze v2 目录**，不要用 `reports/paper_analysis/python200_hard_main_20260829/` 的脏 132/200。

## 10. 禁止

- 用 `suite.passed` / `run.status` 当主结果。  
- 把 Qwen 正式成绩改成 80/172。  
- 未标注就从漏斗跳到 Contract Closure。  
- 把 DeepSeek「有包仍 rc=86」与 Qwen 空卷写成同一类失败。  
- 开 `tool_alias_compat` 补跑后覆盖 Qwen 主表。  
- 把旗舰 GLM-5.3 错跑写进 Finding 1。  
- 把 RQ6、CGVL、Lite、旧 E50 写进主 leaderboard。  
- 用心理语言（「模型粗心」「没有理解」）代替可观察证据。
