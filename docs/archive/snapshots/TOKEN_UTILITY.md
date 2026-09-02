# Token utility 回顾分析（离线）

> **Status: archived · Last verified: 2026-09-02**
> 这不是新方法臂。禁止据此写 stop / repair / V3。金标只能是某一时刻
> `submission/featurelifted/` 的 `functional_gate`，不能是轨迹叙事。
> Phase 3：验证循环组合 AUC 弱，不写停机规则。距上次独特树的间隔是唯一
> 明显信号，仍然不是 stop 规则。
> Characterization：T* 必须按模型 × Lift 分层；`metadata.difficulty` 不是
> 科学 easy/medium/hard。

在已有 Main / V1 轨迹上回答两件事：

1. 长轨迹上有效计算落在哪一段（论文 **RQ3** 的成本切片，不是新协议；capability
   通过率仍是 RQ1）。稿：[paper/03_results_token_utility.md](../../paper/03_results_token_utility.md)。
2. 合法运行时信号能否把「有效尾巴」和空转分开。分不开就不要写停机规则。

V2 已经用「最近有没有写 submission」当进展，把自测判成 stall。本分析必须先离线
标金标，再谈相关，禁止先拍 Progressing / Stagnating。

## 数据（已有，不新跑）

| 套件 | 路径 |
| --- | --- |
| Flash 本地 Main-200 | `experiments/python/openhands/deepseek-v4-flash/python200-deepseek-v4-flash-vllm-local-0812-001` |
| Flash API E50 Main | `experiments/python/openhands/deepseek-v4-flash/external50-deepseek-v4-flash-0805-main-001` |
| Qwen3.6-35B V1-200 | `experiments/python/openhands/qwen3.6-35b-a3b-fp8/python200-qwen3.6-35b-a3b-fp8-v1-0817-001` |
| Qwen3.6-35B E50 Main | `experiments/python/openhands/qwen3.6-35b-a3b-fp8/external50-qwen3.6-35b-a3b-fp8-0817-main-001` |
| Qwen3.5-122B E50 Main | `experiments/python/openhands/qwen3.5-122b-a10b-fp8/external50-qwen3.5-122b-a10b-fp8-0817-main-001` |
| GPT-OSS 120B E50 Main | `experiments/python/openhands/gpt-oss-120b/external50-gpt-oss-120b-0817-main-001` |

每题用 `agent/openhands_events.jsonl`（写事件）和 `agent/context_audit.jsonl`
（按次 `prompt_tokens + completion_tokens` 累加）。事件时间戳是无时区 ISO，审计是
UTC `Z`；对齐时两者都按 UTC 解析。指标仍是 `eval/result.json` 的
`functional_gate`。

必须按模型分层。Flash 后期 token 常有用；Qwen 后期常空转。同一条停机规则会对
两个模型做相反的事。

## Phase 0 — 最后一次改包（代理，不是金标）

**问题：** 最后一次改 `submission/featurelifted/` 时，已经花了总 token 的几成？
那之后的尾巴**不能再改包**，因此不可能再改变 Functional Pass。

**不能证明：** 最后一次写入是否必要；更早的 snapshot 是否已经能过。失败题没有
「再花 200K 就会过」的反事实。Main vs V1 是独立抽样，不是同一条轨迹在 2M 截断。

```bash
.venv/bin/python harness/scripts/analyze_token_utility_phase0.py \
  experiments/python/openhands/deepseek-v4-flash/python200-deepseek-v4-flash-vllm-local-0812-001 \
  experiments/python/openhands/qwen3.6-35b-a3b-fp8/python200-qwen3.6-35b-a3b-fp8-v1-0817-001 \
  experiments/python/openhands/qwen3.6-35b-a3b-fp8/external50-qwen3.6-35b-a3b-fp8-0817-main-001 \
  --output artifacts/research_analysis/current_results/token_utility_phase0_20260818.json
```

2026-08-18 结果（只统计检测到 package write 的题）：

| 套件 | 子集 | n | 最后写包 / 总 token 中位数 | 写包后尾巴中位数 | 最后写入 ≥2M |
| --- | --- | ---: | ---: | ---: | ---: |
| Flash 本地 Main | Pass | 143 | **0.59** | 495K | 14.7%（21 题） |
| Flash 本地 Main | Fail | 53 | 0.75 | 323K | 22.6% |
| Qwen V1-200 | Pass | 54 | 0.72 | 351K | 3.7% |
| Qwen V1-200 | Fail | 131 | **0.88** | 185K | 23.7% |
| Qwen E50 Main | Pass | 36 | 0.71 | 554K | **25.0%** |
| Qwen E50 Main | Fail | 11 | 0.86 | 495K | 54.5% |

读法：

- Flash 通过题中位数在总用量 **59%** 处就停写包，之后还有约 0.5M token 的收尾；
  只有 **3.5%** 通过题把最后写入压到最后 5% token。这是「尾巴不能改结果」，不是
  「尾巴之前已经能过」。
- Flash 通过题仍有 **21/143** 最后一次改包发生在 2M 之后。这些是 2M cap 的风险集，
  但只有 Phase 1 能说更早的树是否已经过关。
- Qwen V1 **失败**题把最后写入顶到轨迹尽头（中位数 0.88；**44/131** ≥0.95）。它们
  在 2M 帽下一直改到停，不是改完再空转。
- Qwen E50 成对 YN（Main 过、V1 不过）**17** 题里，Main 最后写入 ≥2M 的只有 **7**
  题。其余 10 题 Main 在 2M 前就停写了；V1 失败来自另一条独立轨迹，不能写成
  「同一条 Main 被 2M 截断」。

未检出 package write：Flash 4 题（其中 2 题仍 Functional Pass）、Qwen V1 15 题、
Qwen E50 3 题。Phase 1 用 terminal 回放补了大部分 copy；仍匹配不上的不做金标。

## Phase 1 — 最早充分 snapshot（真金标，已完成）

回放：成功的 `file_editor` observation 带完整 `new_content`；会改包的 terminal
（`cp` / `sed -i` / heredoc）在沙箱里执行，repo 取实验 `workspace/repo`（agent
当时看到的树，不是 `python200_tasks/*/repo` 的精简布局）。最后一棵树的内容哈希
必须等于磁盘 `submission/featurelifted/`，否则这题不做金标。

评测：把独特树物化成 `submission/`，用官方 `featureliftbench-eval:latest`
（`sha256:a491d620…`）跑 `functional_gate`。最后一棵树若哈希匹配，直接复用原
`eval/result.json`，不覆盖原 suite。默认抽样：第一棵、最后一棵、1.0/1.5/2.0M
边界。对「最早通过 ≥2M」的候选题补评了全部独特树。

```bash
PYTHONPATH=harness .venv/bin/python harness/scripts/analyze_token_utility_phase1.py eval \
  experiments/python/openhands/deepseek-v4-flash/python200-deepseek-v4-flash-vllm-local-0812-001 \
  experiments/python/openhands/qwen3.6-35b-a3b-fp8/external50-qwen3.6-35b-a3b-fp8-0817-main-001 \
  --workers 6 \
  --output artifacts/research_analysis/current_results/token_utility_phase1_20260818.json \
  --work-root artifacts/research_analysis/token_utility_phase1_work
```

2026-08-18 结果：

| 套件 | 回放匹配 | Pass 有金标 | 最早通过 / 总量 中位数 | 最早通过 ≥2M | 2M 处的树已过 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Flash 本地 Main | 189/200 | 138/145 | **0.40** | **7** | 131/138 |
| Qwen E50 Main | 45/50 | 34/36 | **0.54** | **5** | 29/34 |

读法：

- Flash 通过题中位数在总用量 **40%** 处已经有一棵能过的树。Phase 0 最后一次写包
  中位数 0.59，所以不少后段写入发生在包已经能过之后。
- Phase 0 的 21 道「最后写入 ≥2M 且通过」里，只有 **7** 道最早充分 snapshot 也
  ≥2M。其余 14 道 2M 之后还在改包，但更早的树已经 Functional Pass。
- 这 7 道（attrs、faker、pendulum、phonenumbers、pydantic_settings、
  python_multipart、python_statemachine）在本条 Main 轨迹上是 high-utility late
  tokens：2M 处的树不过（或 2M 前还没有包）。
- 其余 131/138 道在 2M 前最后一棵已评测树上已经能过。2M cap 丢掉的是这 7 道，
  不是 21 道最后写入。
- 未匹配回放的 7 道 Flash 通过题（babel、h2、invoke、lark、markdown_it、passlib、
  pyyaml）没有金标。
- 非晚通过题仍可能只用了抽样树，因此 `earliest_pass_frac` 是上界；那些上界都
  <2M，所以「是否需要 2M 之后」对它们仍然成立。

失败题：Flash 51 道回放匹配的失败里，22 道 public 曾经绿、hidden 从未绿。不要把
public 变绿写成接近 hidden。

## Checkpoint oracle（离线 · 2026-08-20 · Kill 抬 Pass）

问的是：Main 轨迹上是否曾经有一棵独特树 Functional Pass，只是最后交卷交错了。
不是新 Agent 臂。失败题补评了 **全部** unique tree（不再用 1.0/1.5/2.0M 抽样）。

```bash
PYTHONPATH=harness .venv/bin/python harness/scripts/analyze_token_utility_phase1.py eval \
  experiments/python/openhands/deepseek-v4-flash/python200-deepseek-v4-flash-vllm-local-0812-001 \
  --all-unique --workers 6 \
  --output artifacts/research_analysis/current_results/checkpoint_oracle_flash_fail_all_unique_20260820.json
```

Flash 本地 Main-200、51 道 replay-ok 失败、385 棵独特树、334 次 docker eval（最后一棵复用原 `eval/result.json`）：

| 读出 | 结果 |
| --- | ---: |
| 任一独特树 Functional Pass | **0/51** |
| public 曾经绿、hidden 从未绿 | 22 |
| hidden 曾经绿（public 全程红，gate 仍 0） | 7 |
| 欠采样 | **0** |

通过题上 T* vs 最后一棵树（Phase 1 已有金标，138 题）：74 题 T* 就是 last；37 题 T* 字节更小，中位只少 **0.47%**。

**Kill 抬 Pass。** 失败不是「有过关树被扔掉」。不要实现 Best-so-far / artifact checkpoint Agent。紧凑性差额不够开新臂。摘要：[`checkpoint_oracle_flash_fail_summary_20260820.json`](../../../artifacts/research_analysis/current_results/checkpoint_oracle_flash_fail_summary_20260820.json)。

## Characterization — T* 按模型 × Lift × 难度

金标仍是 Phase 1 的最早充分 snapshot。这里把 `T*/T_total`、过关后 token、尾巴里
verification（`self_test_run` + `self_test_write`）按轴切开。Flash / Qwen / OSS
不画在一张未分层的图里。External-50 与 Python-200 的 Lift 构成不同，也不混。

**Lift type** 是科学任务轴（Direct / Adapted / Composite），标签来自
`reports/contract_closure_200/machine_audit.json`（200/200）。

**难度不是** `metadata.difficulty`：那个字段是建设产物（Python-150 全标 hard，
External-50 全标 medium）。下面用建设队列当**非正式代理**：`python150` /
`hard3`（题 ID `__hard3_`）/ `external50`。`entanglement.level` 也附上；它几乎
分不开 T*。

```bash
PYTHONPATH=harness python3 harness/scripts/analyze_token_utility_characterize.py \
  --phase1 artifacts/research_analysis/current_results/token_utility_phase1_20260818.json \
           artifacts/research_analysis/current_results/token_utility_phase1_cross_e50_20260818.json \
  --post-pass artifacts/research_analysis/current_results/token_utility_post_pass_existing_gold_20260818.json \
              artifacts/research_analysis/current_results/token_utility_post_pass_cross_e50_20260818.json \
  --output artifacts/research_analysis/current_results/token_utility_characterize_20260818.json
```

### 按模型（金标通过题）

| 模型 | n | T*/T 中位 | T* 中位 | 过关后 token 中位 | 过关后占比 | 尾巴里 verification | ≥2M 才过 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Flash 本地 Main-200 | 138 | **0.40** | 0.47M | **0.75M** | 60% | 55% | 7 |
| Flash API E50 | 42 | **0.36** | 0.53M | **0.95M** | 64% | 57% | 5 |
| Qwen3.6-35B E50 | 34 | 0.54 | 0.95M | 0.86M | 46% | 49% | 5 |
| Qwen3.5-122B E50 | 37 | 0.51 | 0.49M | 0.51M | 49% | 48% | 1 |
| GPT-OSS 120B E50 | 16 | 0.49 | 0.17M | **0.10M** | 51% | 33% | 0 |

Flash 中位约 40% 处已经能过，之后仍烧掉 0.75–0.95M。Qwen 第一次过关更晚（中位
50% 出头），绝对尾巴仍然长。OSS 占比也约一半，但总量小，尾巴只有 0.10M。
verification 占过关后 token 的一半左右（OSS 更低，33%）。

### Flash Main-200 × Lift type

这是 138 道金标通过题里最干净的任务分层（Direct 58 / Adapted 52 / Composite 28）：

| Lift | n | T*/T 中位 (p25–p75) | T* 中位 | 过关后 token | 过关后占比 | verification |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Direct | 58 | **0.36** (0.25–0.54) | 0.39M | 0.74M | 64% | 58% |
| Adapted | 52 | 0.40 (0.26–0.54) | 0.58M | 0.79M | 60% | 53% |
| Composite | 28 | **0.51** (0.33–0.58) | 0.62M | 0.70M | 49% | 54% |

Flash「40% 已经能过」主要是 Direct / Adapted。Composite 更晚（中位 51%），但过关后
仍有 0.70M、尾巴里一半是自测。**不是只有简单题提前过、难题花光预算。** Composite
也不是过关后就不烧 token。

### Flash Main-200 × 非正式难度

| 队列 | n | T*/T 中位 | T* 中位 | 过关后 token | 过关后占比 |
| --- | ---: | ---: | ---: | ---: | ---: |
| python150（非 hard3） | 82 | 0.35 | 0.48M | 0.85M | 65% |
| hard3 | 10 | 0.39 | 0.49M | 0.74M | 61% |
| external50 | 46 | 0.42 | 0.43M | 0.63M | 58% |

hard3 只有 10 道金标通过，T*/T 并不更晚。`entanglement.level` 也分不开：high 105
题中位 0.40，medium 28 题 0.39，low 5 题 0.38。**不要用 metadata.difficulty 或
纠缠强度当 T* 的难度故事。** Lift type 才拉开差距。

Lift × 队列交叉里，n≥8 的格子：Direct/python150 0.35（n=46）、Adapted/python150
0.38（n=34）、Composite/external50 0.51（n=22）、Direct/external50 0.37（n=12）。
hard3 交叉格 n<8，不当主结果。

### External-50 Main × 模型 × Lift

同一 50 题、不同模型。E50 本身 Composite 偏多；OSS 能过的题更偏 Direct（8/16），
不能把 OSS 的 T* 写成「更会做 Composite」。n<8 标了 *。

| 模型 | Direct T*/T (n) | Adapted T*/T (n) | Composite T*/T (n) |
| --- | ---: | ---: | ---: |
| Flash API | 0.35 (12) | 0.44 (11) | 0.36 (19) |
| Qwen-35B | 0.49 (11) | **0.61** (11) | 0.56 (12) |
| Qwen-122B | 0.46 (11) | 0.44 (10) | **0.60** (16) |
| OSS-120B | 0.57 (8) | 0.49 (6*) | 0.48 (2*) |

读法：

- Qwen 的 Composite / Adapted 更常把第一次通过压到轨迹后半；Flash Direct 仍然最早。
- Flash API Composite 的 **T*/T 中位 0.36，但 T* 绝对量 0.88M、过关后中位 2.08M**。
  分数提前过关，并不省绝对 token。
- OSS 格子太小，只说明会过的弱模型轨迹短，不说明 Composite 对 OSS 更容易。

快照：[`token_utility_characterize_20260818.json`](../../../artifacts/research_analysis/current_results/token_utility_characterize_20260818.json)。

## Phase 2 — 成对 2M 税（已完成，仍不是截断同一轨迹）

Qwen E50 Main 过、V1 不过：18 题（V1 无 `functional_pass` 的也算不过）。Main
轨迹金标：

| Main 最早通过 | 题数 | 含义 |
| --- | ---: | --- |
| <2M（2M 处的树已过） | 12 | 这条 Main 被 2M 截断仍会过；V1 失败是另一条样本 |
| ≥2M | 5 | 这条 Main 确实需要 2M 之后：configupdater、ftfy、furl、invoke、langcodes |
| 回放失败 | 1 | sqlglot，无金标 |

ftfy 补评全部 23 棵独特树后，最早通过仍在 **8.17M**。这是 late-token 的硬例子。

不要把 18 道 YN 全部写成 cap 税。

## 过关后还在干什么

Flash 本地 Main、138 道有金标的通过题。过关后的尾巴中位数 **0.75M token，占总用量
60%**（p25 45%，p90 80%）。87/138 题一半以上的 token 发生在已经 Functional Pass
之后。Agent 看不见 hidden，所以不会停。

过关后 billed token 构成（总量约 129M，按随后一个 ActionEvent 归类；`python - <<`
heredoc 算自测）：

| 活动 | 占过关后 token |
| --- | ---: |
| 跑自测（`python -c`、`python - <<`、pytest、上游测试 shim） | **48%** |
| 写自测脚本 | 5% |
| 读自己的包 / 上游测试 / 仓库 | 18% |
| 继续改 `featurelifted` | 6% |
| isolation / 禁 import 检查 | 4% |
| finish / tracker / 清理 | 9% |
| 其它（空 terminal、安装依赖） | 10% |

99% 的通过题过关后仍在自测；49% 会去读上游 `tests/`。只有 **44%** 过关后还改包，
且改包只占尾巴 token 的 6%（中位数 0）。约 46% 的题过关后还会产生新的独特树；
isort 在 0.90M 已过、随后改坏、1.49M 才恢复。后段写入不是无害抛光。

机制：用「自己编的用例 + 上游测试」代替看不见的 hidden。这看起来像进展，所以
V2 把「最近没写文件」当 stall 会误杀；但这些 token 也改变不了已经成立的
Functional Pass。

快照：[`token_utility_post_pass_existing_gold_20260818.json`](../../../artifacts/research_analysis/current_results/token_utility_post_pass_existing_gold_20260818.json)。

## 跨模型 — 过关后是不是都在自测

不是同一件事的复制。External-50 Main、同一 50 题、Phase 1 金标：

| 模型 | 金标通过 | 过关后占比中位 | 过关后 token 中位 | 仍自测 | 尾巴里自测 | 读上游 `tests/` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Flash API | 42 | **64%** | **0.95M** | 100% | 50% | **52%** |
| Flash 本地 | 46 | **58%** | 0.63M | 100% | 49% | **44%** |
| Qwen3.6-35B | 34 | 46% | 0.86M | 100% | 51% | **3%** |
| Qwen3.5-122B | 37 | 49% | 0.51M | 100% | 50% | 11% |
| GPT-OSS 120B | 16 | 51% | **0.10M** | 94% | 34% | 6% |

读法：

- **Qwen 和 Flash 都在过关后自测。** 通过题几乎题题还跑自己写的用例；尾巴里约一半
  token 是自测。继续改包只占尾巴的 5–8%。
- **Flash 独有的是上游测试 oracle。** 43–52% 的 Flash 通过题过关后会读
  `repo/tests/`；Qwen-35B 只有 3%。不能把「读上游测试代替 hidden」写成所有模型的
  机制。
- **量级差一档。** OSS 过关后占比也约 50%，但总用量中位 0.37M、尾巴只有 0.10M。
  Flash API 尾巴是 0.95M。Qwen-35B 第一次过关更晚（中位 0.95M），所以占比低于
  Flash，绝对尾巴仍然长。
- **2M 之后才过的题也分层。** Flash API E50 5/42、Qwen-35B 5/34、Qwen-122B 1/37、
  OSS 0/16。会过的弱模型轨迹往往在 2M 前就过了；需要晚 token 的题在弱模型上更常
  整题失败。

脚本：`harness/scripts/analyze_token_utility_post_pass.py`。快照：
[`token_utility_post_pass_cross_model_20260818.json`](../../../artifacts/research_analysis/current_results/token_utility_post_pass_cross_model_20260818.json)。

## 过关后的 verification loop

金标通过题、T* 之后还在自测。问题不是「有没有自测」，而是：**这次自测有没有新信息、后面有没有新的独特树。**

定义（全程不看 Hidden / evaluator）：

- **新信息：** 命令骨架（heredoc / `python -c` 体裁掉）或结果指纹（pytest `passed/failed` + exit，否则观察值去 ANSI）第一次出现。两者都见过才算 identical rerun。
- **随后新树：** 这次自测之后 **250K token 内** 出现与当前不同的独特 `featurelifted` 树。更远的树不算这次自测引起的。
- **有用 verification：** 发生在 T* **之前**，且随后有新树或 20 步内有 package write。T* 之后的自测改变不了已经成立的 Functional Pass，单独统计。

只在 Phase 1 金标通过题上做。Qwen V1-200 没有金标，不编 T*。失败题没有 T*，不进这个表。

```bash
PYTHONPATH=harness python3 harness/scripts/analyze_token_utility_phase3.py \
  --phase1 artifacts/research_analysis/current_results/token_utility_phase1_20260818.json \
  --output artifacts/research_analysis/current_results/token_utility_phase3_20260818.json
```

| | Flash 本地 Main（138） | Qwen-35B E50 Main（34） |
| --- | ---: | ---: |
| 自测次数 T* 前 / 后 | 334 / **1482** | 92 / **228** |
| 过关后仍自测的题 | 99% | 100% |
| T* 前：新信息且 250K 内新树 | **50%** | **53%** |
| T* 前：新信息但没有很快新树 | 48% | 37% |
| T* 后：新信息且很快新树 | 12% | 11% |
| T* 后：新信息、没有很快新树 | **85%** | **72%** |
| T* 后 identical rerun（命令+结果都见过） | 1.8% | **14%** |
| 读路径重复率 T* 前 → 后 | 0.8% → 11% | **21% → 51%** |
| 过关后又长出独特树的题 | 46% | 44% |

读法：

- **Flash 过关后不是在重复同一条 pytest。** 85% 的过关后自测仍是新命令或新结果，但 250K token 内不长新树。空转是「还在发明新探针」，不是 stub 重放。
- **Qwen 重复更多。** 过关后 14% 的自测是 identical rerun，读路径一半是重复读。和 Flash 不是同一类浪费。
- **T* 之前大约一半自测后面很快有新树**（Flash 50%，Qwen 53%）。另一半是过关前就已经在探、还没改包。
- 过关后仍有约 1/5 的自测后面会出现新独特树（任意更晚的树，不限 250K）。这和 isort 改坏再恢复是同一类：后段写入不是无害抛光，也不能当成「没有新 patch 就可以停」。

## Phase 3 — 合法信号 vs 金标

标签：`already_enough = 1` 若累计 token `t ≥ T*`，否则 0。只在金标通过题上做。特征只用当时历史上能看见的东西，**不含 T\*、Hidden、evaluator、未来的树。**

合法特征：连续自测次数、self-test 命令/结果 novelty、距上次**独特树**的 token/步数、窗口内重复命令率/重复读率、窗口内新树数。`tokens_so_far` 和累计独特树数只当对照（单调时间代理），不叫验证信号。

控制：0.5–1.5M token 带。这一带里 `tokens_so_far` 的 AUC 会掉下来；若验证信号也掉，说明它只是「轨迹后期」。

预测 `t ≥ T*` 的 AUC（不过拟合、不写 stop 规则）：

| 切片 | Flash 合法组合 | Flash `tokens_since` 上次独特树 | Flash `tokens_so_far` 对照 | Qwen 合法组合 | Qwen `tokens_since` | Qwen `tokens_so_far` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 全部 Action | 0.63 | **0.86** | 0.84 | 0.64 | **0.88** | 0.81 |
| billed call | 0.63 | 0.86 | 0.85 | 0.65 | 0.88 | 0.84 |
| 只看自测 Action | 0.68 | 0.67 | 0.64 | 0.79 | 0.78 | 0.52 |
| **0.5–1.5M 带** | 0.67 | **0.79** | **0.57** | 0.63 | **0.81** | 0.69 |

自测行上的 novelty 特征接近随机或反向：Flash 自测切片里 `self_test_out_novel` AUC **0.45**（过关前略更新），`self_test_pair_novel` 0.50。过关前后自测都在出新探针，**不能靠「这次自测新不新」判断已经做够。**

`frac_recent_self_test_out_novel` 在全部 Action 上 AUC 0.79，是假象：过关后窗口里更常出现自测，没有自测时该特征是 0。限制在自测行上降到 0.40。

读法：

- **验证循环组合 AUC 0.63–0.67，不够写停机规则。** 连续自测、重复命令、novelty 合在一起分不开 `t < T*` 和 `t ≥ T*`。这条 early-stopping 线停在这里，不要据此做 verification-aware stopping。
- **唯一明显强于时间对照的信号是「距上次独特树多久」。** 在 0.5–1.5M 带里 Flash 的 `tokens_so_far` 只剩 0.57，`tokens_since_last_useful_write` 还是 0.79。这是 stall-after-edit，不是 self-test novelty。它接近 V2 的「最近没写 submission」，但金标对齐的是独特树而不是任意写文件。现在仍然**不写 stop 规则**：过关后 46% 的题还会长新树，其中有的会改坏。
- Flash / Qwen 必须继续分层。Qwen 过关后重复读 51%，Flash 11%；同一条「重复读就停」会对两个模型做不同的事。

快照：[`token_utility_phase3_20260818.json`](../../../artifacts/research_analysis/current_results/token_utility_phase3_20260818.json)。脚本：`harness/scripts/analyze_token_utility_phase3.py`。单测：`harness/tests/test_token_utility_phase3.py`。

论文 RQ3/RQ5 稿：[paper/03_results_token_utility.md](../../paper/03_results_token_utility.md)。

## 不要做

- 不新跑 200 题、不写 V3 / `behavior_probe` / 新 stop 规则。Phase 3 组合
  AUC 不够，不要做 verification-aware stopping。下一正式臂是 RQ6
  Public-feedback，不是从本文件推停机。
- 不把 Phase 0 的 `last_write_frac` 写进论文当 token utility。
- 不把 Main vs V1 的 YN 当成同一轨迹截断。
- 不把 Flash 和 Qwen 画在一张未分层的图里。
- 不把 `metadata.difficulty` 写成科学 easy/medium/hard；Python-150 全是 hard、
  External-50 全是 medium。难度代理只用 hard3 / python150 / external50，并标明
  非正式。
