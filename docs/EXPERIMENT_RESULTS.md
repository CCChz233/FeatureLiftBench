# FeatureLiftBench 实验结果汇总

本文档集中记录历史 **batch-0 50 hard** agent 实验结果。当前主榜已经扩到 **100 hard**；正式论文/模型对比需要按 [RUN.md](../RUN.md) 的 agent Docker + eval Docker 流程重新跑 100 题。官方历史 DeepSeek baseline 见 [BENCHMARK_STATUS.md](BENCHMARK_STATUS.md)；评分定义见 [CONCEPTS.md](CONCEPTS.md) 第 6 节。

**最后更新：** 2026-06-27（题目策展 [EXPANSION.md](EXPANSION.md)；MiniMax OOM 记录）

---

## 1. 评价指标

单题 `FunctionalGate`、`ExtractionRatio`、`final_score` 定义见 **[CONCEPTS.md](CONCEPTS.md) 第 6 节**。下文只列 **suite 汇总与多轮分析** 口径。

### 1.1 Suite 级汇总

| 字段 | 含义 | 是否主榜 headline |
|------|------|-------------------|
| **passed** | 单题 `status=passed` 的数量（agent 正常结束 **且** eval functional pass） | **是** |
| **average_final_score** | 当前 suite 全部题目的 `final_score` 算术平均（失败题为 0） | 是（辅） |
| **missing_submissions** | `workspace/submission/` 无文件、未 eval 的题数 | 否（运行质量） |
| **recovered_submissions** | 从错路径 auto-recover 后再 eval 的题数（见 harness 改动） | 否（审计） |
| **by_status.failed** | 有 submission 但 functional 未过的题数 | 否 |

报告当前 100 题正式结果时，应并列 functional pass、average `final_score`、high-extraction pass、compact pass，并单独披露 resource/log/sandbox failure；历史 50-hard 结果只用于 pilot 对照。

单题 **passed** 判定（[`run_status`](harness/featureliftbench/suite_utils.py)）：

```text
submission 存在 → eval 完成 → agent.passed 且 eval.status=passed → passed
否则 → failed 或 missing_submission
```

### 1.2 多轮实验衍生指标（分析用，非 harness 内置）

| 指标 | 定义 |
|------|------|
| **pass@1（单次 run）** | 该 run 的 `summary.passed` |
| **pass@k（any）** | k 次独立 run 中至少 1 次 functional pass 的题数 |
| **pass@k（all）** | k 次 run 全部 functional pass 的题数 |
| **mean ± std** | k 次 run 的 passed 或 pass rate 的均值与标准差 |

### 1.3 Agent 运行统计（不影响 functional pass）

来自 `agent/trajectory.json` 或 `usage.json`，写入 `agent_usage_totals`：

- `assistant_steps` / `api_calls`
- `prompt_tokens` / `completion_tokens` / `total_tokens`

---

## 2. 本地 vLLM 实验协议（2026-06-26）

| 项 | 值 |
|----|-----|
| 题目集 | `benchmark/tasks/`（50 hard） |
| Agent | mini-swe-agent 1.17.3 + `--yolo` |
| Workers | 2 |
| GPT-OSS | profile `gpt_oss_120b_vllm`，vLLM `:8008` |
| Qwen | profile `qwen3_coder_30b_vllm`，vLLM `:8009` |
| 正式对比 | 各模型 **3 次独立 full run**（新 `RUN_ID`，非 resume） |
| 注 | 下表 6 轮在 **misplaced auto-recover 落地前** 跑完，`recovered_submissions=0` |

---

## 3. 正式结果：3 轮 × 50 hard

### 3.1 每轮汇总

| Run ID | 模型 | passed | pass rate | missing | avg final_score | total_tokens |
|--------|------|-------:|----------:|--------:|----------------:|-------------:|
| [gpt-oss-run1-20260626-165024](../experiments/mini-swe-agent/benchmark-50-hard-gpt-oss-run1-20260626-165024/) | GPT-OSS-120B | 7/50 | 14% | 10 | 0.094 | ~50.0M |
| [gpt-oss-run2-20260626-184810](../experiments/mini-swe-agent/benchmark-50-hard-gpt-oss-run2-20260626-184810/) | GPT-OSS-120B | 4/50 | 8% | 14 | 0.092 | ~40.1M |
| [gpt-oss-run3-20260626-200637](../experiments/mini-swe-agent/benchmark-50-hard-gpt-oss-run3-20260626-200637/) | GPT-OSS-120B | 8/50 | 16% | 9 | 0.095 | ~99.6M |
| [qwen-run1-20260626-165622](../experiments/mini-swe-agent/benchmark-50-hard-qwen3-coder-run1-20260626-165622/) | Qwen3-Coder-30B | 4/50 | 8% | 3 | 0.051 | ~28.4M |
| [qwen-run2-20260626-185334](../experiments/mini-swe-agent/benchmark-50-hard-qwen3-coder-run2-20260626-185334/) | Qwen3-Coder-30B | 12/50 | 24% | 0 | 0.162 | ~32.8M |
| [qwen-run3-20260626-203041](../experiments/mini-swe-agent/benchmark-50-hard-qwen3-coder-run3-20260626-203041/) | Qwen3-Coder-30B | 5/50 | 10% | 2 | 0.087 | ~30.3M |

### 3.2 三轮聚合

| 模型 | passed（每轮） | mean ± std | pass rate mean | missing mean | pass@3 (any) | pass@3 (all) |
|------|----------------|------------|----------------|--------------|--------------|--------------|
| GPT-OSS-120B | 7, 4, 8 | **6.3 ± 1.7** | **12.7%** | 11.0 | **15/50** | 0/50 |
| Qwen3-Coder-30B | 4, 12, 5 | **7.0 ± 3.6** | **14.0%** | 1.7 | **14/50** | **1/50** |

**Qwen 唯一 pass@3（三轮均过）：** `vibe_app__plugin_registry_core__001`

**两模型均至少过 1 次的 8 题：**

`coverage__report_core__001`, `json5__parse_core__001`, `pytest__mark_expression_core__001`,
`vibe_app__csv_transform_core__001`, `vibe_app__plugin_registry_core__001`,
`vibe_app__pricing_rules_core__001`, `vibe_app__session_registry_core__001`,
`vibe_app__yaml_config_bootstrap__001`

### 3.3 与官方 DeepSeek baseline 对比（口径不同）

| 设置 | Functional pass | 说明 |
|------|----------------:|------|
| DeepSeek Flash（官方 API） | 41/50 (82%) | [BENCHMARK_STATUS.md](BENCHMARK_STATUS.md) |
| DeepSeek Pro（官方 API） | 42/50 (84%) | 同上 |
| 本地 GPT-OSS-120B（3-run mean） | ~6.3/50 (13%) | 本表 §3.2 |
| 本地 Qwen3-Coder-30B（3-run mean） | ~7.0/50 (14%) | 本表 §3.2 |

不可直接对比：模型、endpoint、agent 稳定性（missing_submission）、eval harness 版本均不同。

### 3.4 深度分析（6 轮 × 50 题 = 300 题次）

数据来源：[formal-50hard-6run-summary.json](../experiments/mini-swe-agent/formal-50hard-6run-summary.json)（join `metadata.json` + `eval/result.json`）。

#### 失败 taxonomy（300 题次）

| failure_mode | 次数 | 占比 | 含义 |
|--------------|-----:|-----:|------|
| **test_fail** | 108 | 36.0% | build 过，但 public 或 hidden 测挂（且非 public-only 模式） |
| **public_only_fail** | 59 | 19.7% | build 过、**public 过、hidden 挂** |
| **build_fail** | 53 | 17.7% | 包装不上 / import 失败 |
| **missing_submission** | 38 | 12.7% | 无 submission，未 eval |
| **passed** | 40 | 13.3% | functional pass |
| **forbidden_import_fail** | 2 | 0.7% | forbidden import / dependency |

→ 有 submission 且 build 过的失败里，**public-only（过可见测、挂 hidden）占大头**（59 / 167 ≈ 35%）。

#### 按模型（各 150 题次）

| 模型 | passed | pass rate | missing | public_only | build_fail |
|------|-------:|----------:|--------:|------------:|-----------:|
| GPT-OSS-120B | 19 | 12.7% | **33** | 25 | 33 |
| Qwen3-Coder-30B | 21 | 14.0% | **5** | 34 | 20 |

GPT-OSS 主要输在 **missing_submission + build_fail**；Qwen 更常 **public 过 hidden 挂**。

#### 按上游项目（source，每题 6 次 attempt）

| source | attempts | passed | pass rate | 备注 |
|--------|----------|-------:|----------:|------|
| **vibe_app** | 42 | 19 | **45.2%** | 7 题 × 6 次；最好的一组 |
| **json5** | 6 | 3 | **50.0%** | 单题 |
| **packaging** | 6 | 2 | 33.3% | |
| **pluggy** | 12 | 3 | 25.0% | 2 题 |
| coveragepy | 30 | 2 | 6.7% | 5 题 |
| pytest | 24 | 2 | 8.3% | 4 题 |
| sqlparse | 24 | 1 | 4.2% | 4 题 |
| lark | 18 | 1 | 5.6% | 3 题 |
| **jinja2** | 30 | 0 | **0%** | 5 题 × 6 次全挂 |
| **babel** | 6 | 0 | **0%** | 6 次均为 public_only 或 missing |
| attrs, Faker, jsonschema, marshmallow, networkx, typer, werkzeug 等 | 各 6 | 0 | 0% | |

#### 解耦质量（functional pass 的 40 题次）

| 类型 | 次数 | 说明 |
|------|-----:|------|
| **compact pass**（ratio ≤ 0.25） | 23 | 真解耦居多 |
| **copy-heavy pass**（ratio ≥ 0.8） | 9 | functional 过但几乎整包复制 |
| **public_only_fail** | 59 | 未 functional pass，但 public 曾过 |

copy-heavy 典型题：`click__option_parser__001`, `json5__parse_core__001`, `pluggy__hook_*`, `pyyaml__safe_load_dump__001`

compact 典型题：多数 `vibe_app__*`, `coverage__report_core__001`, `pytest__mark_expression_core__001`

#### 稳定性（每题 6 次 attempt = 3 GPT + 3 Qwen）

| 指标 | 数量 |
|------|-----:|
| **从未 functional pass** | **29 / 50** 题 |
| 至少 pass 1 次（不稳定或稳定） | 21 题 |
| 6 次全过 | 0 题 |
| 两模型均至少 pass 1 次 | 8 题（见 §3.2） |

从未通过的 29 题含：全部 **jinja2**（5）、**sqlparse** 除 token_tree 外（3）、**babel**、**werkzeug**、**typer** 等。

#### Token 与结果

| 指标 | 中位数 total_tokens |
|------|--------------------:|
| functional pass 题次 | **192,453** |
| 非 pass 题次 | **433,092** |

失败 run 往往 **更耗 token**（多轮试错），不是「花更多就更容易过」。

---

## 4. 早期 / 探索性 Run（非 3 轮协议）

| Run ID | 模型 | passed | missing | avg final_score | 备注 |
|--------|------|-------:|--------:|----------------:|------|
| [pro-20260626-133146](../experiments/mini-swe-agent/benchmark-50-hard-pro-20260626-133146/) | GPT-OSS-120B | 5/50 | 1 | 0.053 | 含 missing 重试；[analysis.md](../experiments/mini-swe-agent/benchmark-50-hard-pro-20260626-133146-analysis.md) |
| [qwen-20260626-140803](../experiments/mini-swe-agent/benchmark-50-hard-qwen3-coder-20260626-140803/) | Qwen3-Coder-30B | 6/50 | 3 | 0.081 | 单次；[analysis.md](../experiments/mini-swe-agent/benchmark-50-hard-qwen3-coder-20260626-140803-analysis.md) |

---

## 5. SiliconFlow API 实验（进行中）

| 项 | 值 |
|----|-----|
| Provider | SiliconFlow（`SILICONFLOW_API_KEY` / `SILICONFLOW_API_BASE`） |
| 协议 | `NUM_WORKERS=1`、`RETRY_RATE_LIMIT=5`；见 [RUN.md](../RUN.md) |
| 状态 | **首轮探索中**，尚无完整 `suite.json` |

| Run ID | Profile | 模型 | 进度（2026-06-26） | 备注 |
|--------|---------|------|-------------------|------|
| [glm-5.2-run1-20260626-230548](../experiments/mini-swe-agent/benchmark-50-hard-glm-5.2-run1-20260626-230548/) | `glm_5_2` | GLM-5.2 | 2/50 完成（attrs、babel **passed**）；click 进行中 | 单题 ~1M tokens、~¥5–6/题；全量 50 题估算 **¥250–300** |
| [minimax-m2.5-run1-20260626-233336](../experiments/mini-swe-agent/benchmark-50-hard-minimax-m2.5-run1-20260626-233336/) | `minimax_m2_5` | MiniMax-M2.5 | 42/50 完成；12 passed、29 missing、1 failed；`vibe_app__csv_transform_core__001` 中断 | 无完整 `suite.json`；系统日志显示 `pytest` OOM；续跑须启用 [SETUP.md](SETUP.md) §4 默认配置 |
| — | `kimi_k2_7_code` | Kimi-K2.7-Code | **未开始** | |

> GLM / MiniMax run 若在 **live trajectory** harness 落地前启动，进度条可能仍显示 `0 toks`；重跑或等当前题结束后再看 `trajectory.json`。

### 5.1 MiniMax run1 中断说明（2026-06-27）

MiniMax run1 最后停在 `vibe_app__csv_transform_core__001`：

- 目录存在，但没有 `run.json` / `trajectory.json`
- `workspace/submission/` 与 `submission/` 均为空
- `agent/stdout.log` 停在 prompt / 早期输出，未正常收尾

同一时间段服务器内核日志出现多条 `Out of memory: Killed process ... (pytest)`。这说明至少有测试阶段的 `pytest` 进程被 OOM killer 杀死。现有日志只能确认 OOM 发生在 pytest 执行 untrusted submission 时，不能 100% 将唯一触发源归到某一道题；但该 run 的中断形态与系统级 OOM 一致。

续跑前须确认 harness 内存上限（`run.sh` 默认已开，见 [SETUP.md](SETUP.md) §4）：

```bash
AGENT_PROFILE=minimax_m2_5 \
  RESUME_DIR=experiments/mini-swe-agent/benchmark-50-hard-minimax-m2.5-run1-20260626-233336 \
  ./run.sh
```

内存规格说明见 [SETUP.md](SETUP.md) §4。该 run 发生在 harness 内存上限落地**之前**，续跑/重跑须在实验记录中注明 harness 版本。

---

## 6. 未完成 Run（无 suite.json，可忽略）

以下目录为中断或重复启动，**不计入统计**：

- `benchmark-50-hard-gpt-oss-run1-20260626-164351`
- `benchmark-50-hard-gpt-oss-run1-20260626-164649`
- `benchmark-50-hard-gpt-oss-run2-20260626-164624`
- `benchmark-50-hard-gpt-oss-run2-20260626-165016`
- `benchmark-50-hard-gpt-oss-run3-200637`
- `benchmark-50-hard-gpt-oss-run3-20260626-165018`
- `benchmark-50-hard-minimax-m2.5-run1-20260626-233336`（pytest OOM 后中断；续跑见 [SETUP.md](SETUP.md) §4）

---

## 7. 分析产物

| 类型 | 路径 | 说明 |
|------|------|------|
| 原始结果 | `experiments/mini-swe-agent/<run_id>/suite.json` | 权威数据源 |
| 单 run enrichment | `experiments/mini-swe-agent/<run_id>-comparison.json` | `analyze_benchmark_suite.py` |
| 单 run 报告 | `experiments/mini-swe-agent/<run_id>-analysis.{md,json}` | 同上 |
| **6 轮跨 run 汇总** | [formal-50hard-6run-summary.json](../experiments/mini-swe-agent/formal-50hard-6run-summary.json) | failure taxonomy + 按 source 分组 |
| GPT 三轮 aggregate | [gpt-oss-3run-aggregate.json](../experiments/mini-swe-agent/gpt-oss-3run-aggregate.json) | mean/std |
| Qwen 三轮 aggregate | [qwen-3run-aggregate.json](../experiments/mini-swe-agent/qwen-3run-aggregate.json) | mean/std |
| 官方 baseline | [BENCHMARK_STATUS.md](BENCHMARK_STATUS.md) | DeepSeek Flash/Pro |

生成 / 更新分析：

```bash
cd FeatureLiftBench

# 单 run enrichment
python harness/scripts/analyze_benchmark_suite.py \
  experiments/mini-swe-agent/<run_id>

# 同模型三轮 mean/std
python harness/scripts/analyze_benchmark_suite.py --aggregate \
  experiments/mini-swe-agent/benchmark-50-hard-gpt-oss-run1-20260626-165024 \
  experiments/mini-swe-agent/benchmark-50-hard-gpt-oss-run2-20260626-184810 \
  experiments/mini-swe-agent/benchmark-50-hard-gpt-oss-run3-20260626-200637 \
  --output experiments/mini-swe-agent/gpt-oss-3run-aggregate.json

# 跨 run 汇总（join metadata + failure taxonomy）
python harness/scripts/summarize_experiment_runs.py \
  experiments/mini-swe-agent/benchmark-50-hard-gpt-oss-run1-20260626-165024 \
  experiments/mini-swe-agent/benchmark-50-hard-gpt-oss-run2-20260626-184810 \
  experiments/mini-swe-agent/benchmark-50-hard-gpt-oss-run3-20260626-200637 \
  experiments/mini-swe-agent/benchmark-50-hard-qwen3-coder-run1-20260626-165622 \
  experiments/mini-swe-agent/benchmark-50-hard-qwen3-coder-run2-20260626-185334 \
  experiments/mini-swe-agent/benchmark-50-hard-qwen3-coder-run3-20260626-203041 \
  --output experiments/mini-swe-agent/formal-50hard-6run-summary.json
```

---

## 8. 维护说明

新增一轮实验后，请更新：

1. **§3.1** 表格：从 `suite.json` 读取 `summary` 与 `agent_usage_totals`
2. **§3.2 / §3.4**：重跑 `summarize_experiment_runs.py` 更新跨 run 汇总
3. **§4 / §5 / §6**：探索性 run、SiliconFlow API run、中断 run 的归类
4. 文首 **最后更新** 日期

快速查看某 run：

```bash
python3 -c "
import json; from pathlib import Path
p=Path('experiments/mini-swe-agent/<run_id>/suite.json')
s=json.loads(p.read_text()); print(s['summary']); print(s.get('agent_usage_totals'))"
```
