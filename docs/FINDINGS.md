# 当前方法结论

> **Status: current · Last verified: 2026-08-20**
> 跨模型 Main leaderboard 只维护在 [STATUS.md](STATUS.md)。
> **当前 cost arm V1 = Main + 2M cap**，规范见 [METHOD_V1.md](METHOD_V1.md)。
> 指标定义见 [EVALUATION.md](EVALUATION.md)。

本文只解释方法对比。Rescue+、V2、TFL、Core-12、RQ6 Flash-12 和 Spec-adversarial
Hidden-4 通过率不进入 Python-200 主表。

## 结论先行

1. **无帽 Main 仍是最强合法协议。** Flash API 144/200、本地 145/200。
2. **V1（2M cap）有明确的 Pass 税。** Qwen3.6-35B V1 为 **55/200**。干净 External-50
   成对 n=46：Main 35 → V1 19。Flash Core-12：8/12 → 4/12。
3. **旧 Lite V1（checker + stop + repair）不能替代 Main。** DeepSeek API −6.5 pp，
   本地 −9.0 pp；成对 RRES Δ 中位数 0。
4. **脚手架补不了 hidden。** TFL / TD / PDR / Self-Contract / Exec-Contract / V2 /
   Spec-adversarial 均未相对 Main 抬 Functional Pass。合法反馈对不齐评测私有行为。
5. **Verification-aware 已停。** Distill-24 同日 LLM summary **16/24**，VA
   **14/24**，低于停线。overflow 修补重跑未齐，不当 24 题结果。不要扩到 200。
6. **RQ6 Public-feedback 解释 Main 的信息边界，不是新方法。** Flash-12 同日成对
   已齐：Main **0/12** → Public-feedback **4/12**。public 失败 6/6 救回 public；
   hidden 失败成对 5 题里 4 题 Hidden 不动。yamale / wheel 两道 hidden 0→1，不是
   大量泄漏。数字不进 Python-200 主表。见
   [METHOD_RQ6_PUBLIC_FEEDBACK.md](METHOD_RQ6_PUBLIC_FEEDBACK.md) 与
   [paper/04_results_rq6.md](paper/04_results_rq6.md)。
7. **Spec-adversarial 已 Kill。** Hidden-4 同日成对：Main **0/4** → SA **0/4**；
   Hidden 0→1 = **0/4**。过程上四题 checker 全绿，仍抬不动 Hidden。不要
   Distill-24 / Python-200。见 [METHOD_SPEC_ADVERSARIAL.md](METHOD_SPEC_ADVERSARIAL.md)。
8. **Best-so-far checkpoint 已 Kill。** Flash 本地 Main 51 道失败题补评全部独特树，
   Functional 0→1 = **0/51**。不是「过关树被最后一棵覆盖」。不要实现 checkpoint
   Agent。见 [TOKEN_UTILITY.md](TOKEN_UTILITY.md)。
9. Token 金标见 [TOKEN_UTILITY.md](TOKEN_UTILITY.md)；论文 RQ3/RQ5 稿见
   [paper/03_results_token_utility.md](paper/03_results_token_utility.md)。
   Flash 通过题中位数 60% 的 token 花在已经 Functional Pass 之后，主要是自测。
   Direct \(T^\*/T\) 0.36、Composite 0.51；非正式难度分不开。不要写一条跨模型
   停机规则。

## 瓶颈

强模型（Flash）功能失败主体是 hidden：包能交、能 build，边界行为不对。弱模型
（Qwen / GPT-OSS）更多卡在 public。Isolation / 缺包都不是主故事。V1 砍掉的是
强模型 2M 之后仍在转化的尾巴；弱模型长跑还会空转。RQ6 已完成的成对题说明：
Flash 过不了 public，往往是因为看不见可执行 public 测试（RQ6：public 失败 6/6
救回）；过了 public 仍过不了 Hidden，不是同一层信息（hidden 失败成对 4/5 不动）。
Spec-adversarial 把 public_spec 做成可执行清单并关绿，Hidden-4 仍 0→1 = 0/4，
说明「对齐公开合同」也补不齐私有 Hidden。

## V1 = Main + 2M（当前 cost arm）

Qwen3.6-35B Python-200 V1 已完成。快照
[`qwen_v1_vs_main_20260818.json`](../artifacts/research_analysis/current_results/qwen_v1_vs_main_20260818.json)。

| 范围 | Main | V1 | 说明 |
| --- | ---: | ---: | --- |
| Qwen V1 全量 | — | **55/200（27.5%）** | 约 329M tokens；118 题用量 ≥1.9M |
| 成对 both-known n=181 | 75 | 53 | YY 42 / YN 33 / NY 11；token −40% |
| External-50 干净 n=46 | 35 | 19 | YN 17 / NY 1；18/35 道 Main 通过题本身 ≥2M |

V1 全量失败阶段（互斥）：Pass 55，缺包 10，Build 15，Public 86，Hidden 34，
Isolation 0。

不要把 leaderboard 上 Qwen Main **95/200** 与 V1 55/200 直接相减：c150 Main 使用
默认 condenser，且早于 V1 约三周。NY=11 不是 cap 收益（多数是样本噪声或
confounded c150）。Flash API 全量 V1 未跑；Core-12 诊断为 8→4。

不补跑 gpt-oss / 122B / 27B 的 V1-200。

## DeepSeek Main vs 旧 Lite V1 协议

比较的是同一旧协议、Main 预算（120 步 + repair），不是 45+10 Frozen 信封，
也不是当前 V1。快照
[`deepseek_main_vs_lite_v1_20260817.json`](../artifacts/research_analysis/current_results/deepseek_main_vs_lite_v1_20260817.json)。

| 运行端点 | 方法 | Functional Pass | Pass Rate | RRES（通过题）median [Q1, Q3] |
| --- | --- | ---: | ---: | --- |
| API | Main | **144/200** | **72.0%** | 144/144，1.000 [0.930, 1.001] |
| API | Lite V1 | 131/200 | 65.5% | 131/131，1.000 [0.932, 1.002] |
| 本地 vLLM | Main | **145/200** | **72.5%** | 145/145，1.000 [0.858, 1.000] |
| 本地 vLLM | Lite V1 | 127/200 | 63.5% | 127/127，1.000 [0.798, 1.000] |

Python-200 的 RRES 中位数大量贴在 1.000，主要来自 External-50 的 copy-heavy
通过解。方法对比必须用成对子集。

`final_score` 等于 `functional_gate`，Average Final Score 只是 Pass Rate 的另一种
写法，不是紧凑度。

### Functional 成对对比

| 范围 | 两者都过 | 仅 Main 过 | 仅 Lite 过 | 两者都失败 |
| --- | ---: | ---: | ---: | ---: |
| API Python-150 | 84 | **15** | 4 | 47 |
| API Python-200 | 126 | **18** | 5 | 51 |
| 本地 Python-150 | 83 | **15** | 2 | 50 |
| 本地 Python-200 | 125 | **20** | 2 | 53 |

Lite 几乎救不回 Main 的失败题，却会丢掉更多 Main 已经能过的题。

### 成对 RRES

Δ = Lite − Main，负值表示 Lite 更紧凑。

| 范围 | 成对题数 | Main 中位数 | Lite 中位数 | Δ 中位数 | Lite 更小 / 相等 / 更大 |
| --- | ---: | ---: | ---: | ---: | ---: |
| API Python-150 | 84 | 0.983 | 0.989 | **0.000** | 39 / 4 / 41 |
| API Python-200 | 126 | 1.000 | 1.000 | **0.000** | 39 / 46 / 41 |
| 本地 Python-150 | 83 | 0.948 | 0.957 | **0.000** | 38 / 6 / 39 |
| 本地 Python-200 | 125 | 1.000 | 1.000 | **0.000** | 38 / 48 / 39 |

中位数差为 0。不能宣称 Lite V1 更紧凑。

### 失败阶段

互斥首败：`missing → build → public → hidden → isolation`。

| 运行端点 / 方法 | Pass | 未交付 | Build | Public | Hidden | Isolation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| API Main | 144 | 5 | 2 | 27 | 22 | 0 |
| API Lite V1 | 131 | 8 | 3 | 39 | 19 | 0 |
| 本地 Main | 145 | 2 | 1 | 28 | 24 | 0 |
| 本地 Lite V1 | 127 | 2 | 2 | 39 | 30 | 0 |

Lite 多掉的题主要落在 Public / Hidden，不是 isolation。

### 资源诊断（非核心指标）

同模型内 Main vs Lite，全部 assigned tasks 的 prompt + completion：

| 条件 | Main | Lite V1 | 变化 |
| --- | ---: | ---: | ---: |
| API Python-200 | 642.8M | 319.7M | **−50.3%** |
| 本地 Python-200 | 349.6M | 237.4M | **−32.1%** |

跨模型 token 不能当成成本。

## 已停方法（RQ4，不是半成品主线）

| 臂 | 证据 | 机制 |
| --- | --- | --- |
| TD-Cognition | Flash 12 题 4/12 = Main，零翻盘 | 自编探针锁死错误故事 |
| Self-Contract | alembic+click 闸门绿，Functional 0/2 | 空包必红挡不住错题 |
| TFL | 1/6 vs Main 2/6；~2.71× tokens | 上游 oracle + 错误 API 映射 |
| Exec-Contract clean3 | public 可翻，Functional 仍 0 | 抬 public，抬不动 hidden |
| PDR held-out | 2/6 = Main；+16.99M tokens | 开发集规则换题不转正 |
| Rescue+ v2.2 | 2/12 < v2.1 3/12 | 第二轮 repair 无成本收益 |
| V2 adaptive budget | Core-12 2/12；extra→pass=0 | 早停砍尾巴；自测 ≠ hidden |
| Artifact-aware / recency | Core-12 均 8/12 = LLM summary；token 73.8M / 85.9M vs 65.0M | Pass 持平，token 未降 |
| Pre-submit audit | Core-12 6/12 < summary 8/12 | Pass 回退 |
| Verification-aware | Distill-24 14/24 < 同日 LLM summary 16/24 | 自测 ledger 不抬 Pass；overflow 修补重跑未齐 |

归档：[archive/methods/](archive/methods/README.md)。RQ6 不是脚手架，见
[METHOD_RQ6_PUBLIC_FEEDBACK.md](METHOD_RQ6_PUBLIC_FEEDBACK.md)。

## 可以与不可以宣称

可以宣称：

- Main 在 Flash Python-200 上保留最多 Functional Pass；
- V1 在 Qwen 上节省 token，但 Functional Pass 下降；干净 E50 切片尤其清楚；
- 旧 Lite V1 的正确性代价为 6.5–9.0 个百分点，成对 RRES 无优势；
- 已试过的合法脚手架没有稳定抬高 Functional Pass；
- Verification-aware Distill-24 低于同日 LLM summary，已停；
- 在 Flash-12 同日成对上，Public-feedback 把 public 失败题的 public 层 6/6 救回，
  hidden 失败成对题多数 Hidden 不动（4/5）；这解释 Main 的 test-blind 边界，不是
  主表提升。
- 通过题上，最早充分 snapshot 通常远早于停跑：Flash Main-200 中位 \(T^\*/T=0.40\)
  （Direct 0.36 / Composite 0.51），过关后中位 0.75M，约一半是自测。

不可以宣称：

- V1 或 Lite 已经优于 Main；
- 把 token 节省写成功能质量改进；
- 把 Rescue+ / V2 / Main+2M / RQ6 / verification-aware **Core-12 或 Flash-12**
  写进 Python-150/200 主表；
- 把当前 **V1** 与旧 Lite V1 混称为同一个方法；
- 用跨模型 token 或跨模型 RRES 比较成本或天生紧凑度；
- Qwen Main 95/200 与 V1 55/200 是干净成对 cap 效应；
- 最后一次改包的位置就是 token utility；
- 自测 novelty 已经强到可以写停机规则。

## Token 尾巴

Phase 0 代理：[`token_utility_phase0_20260818.json`](../artifacts/research_analysis/current_results/token_utility_phase0_20260818.json)。
Phase 1 金标：[`token_utility_phase1_20260818.json`](../artifacts/research_analysis/current_results/token_utility_phase1_20260818.json)。
协议见 [TOKEN_UTILITY.md](TOKEN_UTILITY.md)。

| 套件 | Pass 最后写包/总量 中位数 | Pass 最早充分树/总量 中位数 | 最后写入 ≥2M | 最早充分 ≥2M |
| --- | ---: | ---: | ---: | ---: |
| Flash 本地 Main | 0.59（n=143） | **0.40**（n=138） | 21/143 | **7/138** |
| Qwen E50 Main | 0.71（n=36） | **0.54**（n=34） | 9/36 | **5/34** |

Flash 通过题多数在总用量 40% 处已经有能过的树。Phase 0 的 21 道「2M 后还在写」
里只有 7 道 2M 前的树还不能过。Qwen E50 YN 18 题里，Main 轨迹真正需要 2M 之后
的是 5 题（ftfy 最早通过 8.17M）；12 题 Main 在 2M 前已过，V1 失败不是截断。
不要据此写 stop 规则。过关之后的 token 主要花在自测上；Flash 独有上游 `tests/`
oracle。按模型 × Lift 的 \(T^\*\) 表见
[paper/03_results_token_utility.md](paper/03_results_token_utility.md)，分析见
[TOKEN_UTILITY.md](TOKEN_UTILITY.md)。

## 证据与复现

```bash
python harness/scripts/reconcile_current_deepseek_results.py
PYTHONPATH=harness python3 harness/scripts/merge_python200_main_results.py
```

DeepSeek 脚本读取本机实验目录中的 `suite.json` 与逐题 `eval/result.json`。
