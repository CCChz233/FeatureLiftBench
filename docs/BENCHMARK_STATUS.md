# Benchmark 现状与待修问题

本文档记录 **batch-0 五十题 + 3 smoke** 的健康度、**官方 DeepSeek baseline**、评分口径与维护优先级。

**非官方实验**（本地 vLLM、SiliconFlow API）→ [EXPERIMENT_RESULTS.md](EXPERIMENT_RESULTS.md)

相关文档：[limitations.md](limitations.md) · [SETUP.md](SETUP.md) · [BENCHMARK_SPEC.md](BENCHMARK_SPEC.md) · [benchmark_tasks.md](benchmark_tasks.md) · [TASK_FORMAT.md](TASK_FORMAT.md) · [CONCEPTS.md](CONCEPTS.md)

最后更新：**2026-06-27**（题目策展 [EXPANSION.md](EXPANSION.md)；内存安全 [SETUP.md](SETUP.md) §4）

---

## 当前快照（2026-06-26）

### 规模与结构

| 分区 | 数量 | 路径 |
| --- | ---: | --- |
| **主榜 hard** | 50 | `benchmark/tasks/` |
| **Smoke 附录** | 3 | `benchmark/sanity/`（iniconfig easy；slugify、pathspec medium） |

- **26** 个源库；同库多题约 **18/50**
- 测试：**242** 条 pytest 函数（50 hard：94 public + 148 hidden；平均 **~4.8 条/题**）
- `list_tasks.py` / `analyze_benchmark_suite.py` **默认 hard-only**；smoke 需 `--root benchmark/sanity` 或 `--include-sanity`

### 质量门禁（维护者）

| 检查 | 状态 |
| --- | --- |
| `verify_all_oracles.py` | **50/50 passed** |
| Harness 单测 | **88** tests（`PYTHONPATH=harness pytest harness/tests`） |
| Design notes + module probes ≥3 | **50/50** |
| Agent 轨迹 | 每题 `experiments/.../<task_id>/agent/trajectory.json` |

### Oracle（参考解）

- **非 Agent 产物**；维护者按 design note / manifest **手工策展 closure**，由 `build_oracle_submission.py` 从 `repo/` 拷贝并改写 import → `benchmark/submissions/<task_id>/oracle/`（gitignore）
- 用途：证明题目可解、回归改题、作为 `extraction_ratio` 分母、module probe 删模块验证

### 评分与 pass 口径

**Functional pass**（suite 里的 `status: passed`）需同时满足：

1. Agent 正常结束（mini returncode=0）
2. **`functional_gate = 1`**：venv 可安装/导入 + **public + hidden pytest 全过** + 无 forbidden import
3. **`extraction_ratio` 不影响 pass/fail**（只进 `final_score`）

```text
final_score = functional_gate × (1 - extraction_ratio)
extraction_ratio = submission Python LOC / repo Python LOC
```

报告 suite 时应 **并列** functional pass rate 与 high-extraction pass（extraction≥0.8 仍 functional pass），避免把「会抄」误判为「会解耦」。

### `entanglement.primary` 分布（50 hard）

| primary | count |
| --- | ---: |
| `parser_state_coupling` | 16 |
| `framework_coupling` | 12 |
| `data_model_coupling` | 6 |
| `legacy_vibe_clutter` | 6 |
| `config_environment_coupling` | 5 |
| `resource_coupling` | 4 |
| `third_party_dependency_coupling` | 1 |

### 题源构成（策展口径）

| 类型 | 数量 | 说明 |
| --- | ---: | --- |
| **真实开源库切片** | 43 | pinned upstream `repo/`；主论文叙事 |
| **策展 vibe_app** | 7 | `benchmark/sources/vibe_app/`；legacy / vibe-coded 应力切片 |

完整原则见 [EXPANSION.md](EXPANSION.md)。

---

## Baseline 跑分

### Flash 50-hard（已冻结）

| 项 | 值 |
| --- | --- |
| Run ID | `experiments/mini-swe-agent/benchmark-50-hard-flash-001` |
| Model | `deepseek/deepseek-v4-flash` |
| Agent | `mini-swe-agent` + `--yolo`，4 workers |
| **Functional pass** | **41 / 50（82%）** |
| Failed | 9 |
| Avg `final_score` | **0.472** |
| Total tokens | ~62M |

**Functional pass 细分（41 题 passed）：**

| 类型 | 数量 | 含义 |
| --- | ---: | --- |
| High-extraction pass（ratio ≥ 0.8） | 9 | 功能过，基本 copy-heavy |
| Compact pass（ratio ≤ 0.25） | 16 | 功能过且裁剪较好 |
| 中间带 | 16 | ratio 0.25–0.8 |

**9 题 functional fail：**

`networkx__dag_topo_core__001`，`pygments__lexer_core__001`，`pytest__fixture_resolve_core__001`，`pytest__ini_markers_core__001`，`pytest__skipif_eval_core__001`，`rich__markup_parse_core__001`，`vibe_app__orm_query_ast_core__001`，`vibe_app__rules_engine_core__001`，`vibe_app__session_registry_core__001`

多数 fail 题 extraction **偏低**（Agent 试图小 closure 但在 hidden 挂）；pass 题里反而有多题 **高 extraction**（抄全仓仍过）。

**按题批次（functional pass）：**

| 批次 | pass |
| --- | ---: |
| 扩榜前 25 hard（Phase 0 加严后） | 23/25（92%） |
| 新增 25 hard | 18/25（72%） |

**校准目标 vs 现状（参考，可随论文周期再评估）：**

| 指标 | 历史校准目标 | Flash-50 现状 | 备注 |
| --- | --- | --- | --- |
| Functional pass | ~20–30% | **82%** | 当前难度下仍可用 **extraction / final_score** 区分解耦质量 |
| 强 Agent functional pass | ~35–45% | Pro **42/50（84%）** | batch-1 **+50** 进行中，见 [EXPANSION.md](EXPANSION.md) |

报告 suite 时并列：**functional pass**、**avg final_score**、**high-extraction pass（≥0.8）**、**compact pass（≤0.25）**。是否收紧 hidden 不作为冻结主榜的前提。

分析产物：

- `experiments/mini-swe-agent/benchmark-50-hard-flash-001/suite.json`
- `experiments/mini-swe-agent/benchmark-50-hard-flash-001-analysis.md`

```bash
python3 harness/scripts/analyze_benchmark_suite.py \
  experiments/mini-swe-agent/benchmark-50-hard-flash-001
python3 harness/scripts/report_entanglement_coverage.py \
  --suite-dir experiments/mini-swe-agent/benchmark-50-hard-flash-001
```

### Pro 50-hard（已冻结，re-eval 修正）

| 项 | 值 |
| --- | --- |
| Run ID | `experiments/mini-swe-agent/benchmark-50-hard-pro-20260625-125553` |
| Model | `deepseek/deepseek-v4-pro` |
| Agent | `mini-swe-agent` + `--yolo`，4 workers |
| **Functional pass** | **42 / 50（84%）**（re-eval 后；原始 agent run 为 38/50） |
| Failed | 8 |
| Avg `final_score` | **0.481** |
| Total tokens | ~61M |

**说明：** 原始 Pro run 有 **6 题 eval flake**（venv 内 `No module named pytest`），其中 4 题 submission 实际可通过。已用修复后的 evaluator + `reeval_suite.py` 重算 eval，**agent 轨迹未重跑**。

**8 题 functional fail：** `networkx__dag_topo_core__001`，`pygments__lexer_core__001`，`pytest__fixture_resolve_core__001`，`pytest__ini_markers_core__001`，`pytest__skipif_eval_core__001`，`redis__resp_parser_core__001`，`vibe_app__orm_query_ast_core__001`，`vibe_app__plugin_registry_core__001`

### Flash vs Pro 对比（50 hard，Pro 为 re-eval 后）

| 指标 | Flash | Pro | Δ |
| --- | ---: | ---: | ---: |
| Functional pass | **41/50 (82%)** | **42/50 (84%)** | Pro **+1** |
| Avg `final_score`（全 suite） | **0.472** | **0.481** | Pro **+0.009** |
| High-extraction pass（≥0.8，在 passed 内） | 9 | 9 | 相同 |
| Compact pass（≤0.25，在 passed 内） | 16 | 16 | 相同 |
| Avg `final_score`（仅 passed 题） | 0.575 | 0.572 | 接近 |
| Total tokens | ~62M | ~61M | 接近 |

**Head-to-head：** 39 题双过 · 6 题双挂 · **2 题仅 Flash 过** · **3 题仅 Pro 过**

| 仅 Pro 过（Flash fail → Pro pass） | 仅 Flash 过（Pro fail → Flash pass） |
| --- | --- |
| `rich__markup_parse_core__001` | `redis__resp_parser_core__001` |
| `vibe_app__rules_engine_core__001` | `vibe_app__plugin_registry_core__001` |
| `vibe_app__session_registry_core__001` | |

**解读：** 修正 eval flake 后，Pro **略高于** Flash 的 functional pass 与 suite 平均 `final_score`，差距很小（±1–2 题）。Pro 在 legacy vibe clutter（rules/session）和 rich 上更强；Flash 在 redis RESP、plugin_registry 等 **hidden 更严** 题上更稳。两者 functional pass 仍远高于校准目标 ~20–30%。

```bash
# 不重跑 agent，仅重算 eval（harness 修复后）
python3 harness/scripts/reeval_suite.py \
  experiments/mini-swe-agent/benchmark-50-hard-pro-20260625-125553

python3 harness/scripts/analyze_benchmark_suite.py \
  experiments/mini-swe-agent/benchmark-50-hard-pro-20260625-125553
```

### 历史：Flash 28 题（扩榜前）

| 项 | 值 |
| --- | --- |
| Run ID | `experiments/mini-swe-agent/benchmark-28-deepseek-flash-003` |
| Passed | 19/28（67.9%），含 3 道已迁出 smoke 的 easy/medium |
| Avg `final_score` | 0.407 |

仅作扩榜前后对比；**主榜 baseline 以 Flash-50 为准**。

**其他模型实验**（vLLM 6-run、SiliconFlow GLM/MiniMax/Kimi 等）见 [EXPERIMENT_RESULTS.md](EXPERIMENT_RESULTS.md)。与 Flash-50 **不可直接对比**（endpoint、稳定性、harness 版本不同）。

---

## 多模型 profile

维护者用 `harness/config/agents.toml` + `.env` 管理模型；完整 profile 表与 CLI 示例见 [benchmark_tasks.md](benchmark_tasks.md) §Running。

```bash
./harness/scripts/run_baseline.sh nex_n2_pro
./harness/scripts/run_baseline.sh deepseek_v4_flash benchmark-50-hard-flash-002
```

Nex-N2-Pro 50-hard：**待** `SILICONFLOW_API_KEY` 配置后执行；smoke 已验证 endpoint（`nex-n2-pro-smoke-001`）。

---

## 为何 functional pass 偏高（82%）— 与论文口径

1. **Pass 门槛不含 extraction** — copy-all + 改 import 即可 functional pass，`final_score` 会很低但不 fail → 须报 **high-extraction pass**。
2. **Hidden 偏少/偏软** — 平均 ~3 条 hidden/题；部分题挡不住 copy-all（可加强，但**非发表硬门槛**）。
3. **任务形态友好** — workspace 含完整 `repo/` + 清晰 `metadata.output`；强 Agent 擅长大规模 copy-edit。
4. **判别在解耦维度** — 41 题 pass 中仅 16 题 compact（ratio≤0.25），9 题 copy-heavy（≥0.8）。

**工程上 benchmark 已合格（50 题、oracle 全绿、harness 闭环）。** 后续新增或替换题须满足 [EXPANSION.md](EXPANSION.md) 的 **实用性** 检查清单；functional 难度可随模型代际 **再评估**。

---

## 扩榜交付（2026-06-25，已完成）

| Phase | 内容 |
| --- | --- |
| Phase 0 | 3 smoke 迁出；8–10 题 hidden/L3 加严 |
| Batch 1 | pytest/coverage/jinja2/vibe_app 同库 +5 |
| Batch 2 | pygments×2、lark×2、attrs +5 |
| Batch 3 | werkzeug、typer、importlib-metadata、h11、redis +5 |
| Batch 4 | faker、lark grammar、rich、marshmallow、babel +5 |
| Batch 5 | vibe ORM/plugin、networkx、json5、pluggy hookspecs +5 |

`build_oracle_submission.py` 已支持上述 family profile + manifest 驱动 OSS。

---

## Eval 可靠性（2026-06-25 修复）

**问题：** 并行 suite eval 偶发 `No module named pytest`（Pro run 6 题），因空 `requirements.lock` 时 pytest 仅依赖 `--system-site-packages`。

**修复：**

- Evaluator 在 venv 创建后 **显式安装 pinned pytest**（`pytest==7.4.4`）并 sanity check；失败重试一次
- `reeval_suite.py`：不重跑 agent，批量重算 submission eval 并更新 `run.json` / `suite.json`
- `analyze_benchmark_suite.py`：输出 `eval_flake` / `eval_flake_count` 标记基础设施误判
- **Docker eval 镜像**（`docker/Dockerfile.eval`）：官方 baseline 推荐在容器内 eval；`featureliftbench eval --docker`

**对外口径：** 论文和正式模型对比的 functional pass / `final_score` 应以 Docker eval 结果为准；local eval 只用于开发调试或定位基础设施问题。

---

## 运行安全（Docker 边界）

Untrusted submission 在 pytest 中执行；正式实验推荐同时启用 `FEATURELIFTBENCH_AGENT_DOCKER=1` 和 `FEATURELIFTBENCH_EVAL_DOCKER=1`。eval Docker 负责内存、CPU、进程数、日志、禁网和只读 mount；agent Docker 负责限制 agent 可见/可写的宿主文件范围。完整规格与 checklist → **[SETUP.md](SETUP.md) §4**。

2026-06-27 MiniMax run 因 pytest OOM 中断 → [EXPERIMENT_RESULTS.md](EXPERIMENT_RESULTS.md) §5.1 · [limitations.md](limitations.md)。后续正式 run 不应只依赖本地 `EVAL_MEMORY_MB` / `AGENT_MEMORY_MB`。

---

## 续跑与失败重试

**场景：** suite 中断、`missing_submission`、或首轮 eval/agent 失败后的二轮补跑。

| 机制 | 用法 |
| --- | --- |
| 手动续跑 | `FEATURELIFTBENCH_AGENT_DOCKER=1 FEATURELIFTBENCH_EVAL_DOCKER=1 RESUME_DIR=experiments/mini-swe-agent/<run> ./run.sh` 或 `run-agent ... --output DIR --resume` |
| 只重跑 missing_submission | `--resume --retry-only-status missing_submission` |
| 挂机自动二轮 | `EXTRA_AGENT_PASSES=1 ./run.sh` 或 `--extra-agent-passes 1` |
| 单题尝试上限 | `--max-task-attempts N`（跨 resume 累计，见 `run.json` 的 `attempt`） |
| API 限流重试 | `--retry-rate-limit N`（单题单次 invocation 内，与上面分离） |
| eval flake / Docker 口径重算 | `reeval_suite.py --docker`（**不重跑 agent**，仅重算 submission eval） |

**记录：** 重跑前旧 `run.json` 归档为 `run.attemptN.json`；`suite.json` 的 `summary.tasks_by_status` 列出各状态 task_id。

**不做：** agent 中途 trajectory checkpoint（单题仍整题 `_reset_dir` 后重跑）。

---

## 当前优先级

1. **P0 正式实验跑批**：用 `FEATURELIFTBENCH_AGENT_DOCKER=1 FEATURELIFTBENCH_EVAL_DOCKER=1` 跑 Flash / Pro 完整主榜，并保存 `suite.json`、每题 `run.json`、每题 `eval/result.json`。
2. **P0 Docker oracle 验收**：用 Docker eval 跑完整主榜 oracle，确认依赖镜像闭包和资源边界没有漏项。
3. **P0 入榜硬门**：`audit_output_imports.py --fail-on-gap` 纳入 staging 与 promote 流程。
4. **P1 题目扩榜（batch-1）**：按 [EXPANSION.md](EXPANSION.md) 从 30 条 starter idea → 5 个 hard-first shortlist → 1 个 staging pilot → **+50**；batch-0 **不修改**。主榜只收 useful + hard，轻量 utility 留作 control/sanity。
5. **P1 实验与报告**：补齐多模型完整主榜 run；分析时单独报告 functional fail、resource/log/sandbox fail 和 missing submission。
6. **P2 可选难度收紧**：对 9 题 high-extraction pass 加强 hidden（**可随论文再评估**，非阻塞，不影响 batch-0 冻结）。
7. **暂缓**：公开 hostile sandbox、Go 语言扩题（v2，见 [BENCHMARK_SPEC.md](BENCHMARK_SPEC.md)）、替换 batch-0 弱题。

**扩题（进行中）：** Python batch-1 **+50**（batch-0 不动）→ [EXPANSION.md](EXPANSION.md)

---

## Harness 与 Oracle 工具

| 路径 | 用途 |
| --- | --- |
| `harness/scripts/verify_all_oracles.py` | 主榜 oracle 一键回归 |
| `harness/scripts/build_oracle_submission.py` | 构建 oracle submission |
| `harness/scripts/verify_module_probes.py` | design probe 审计；`--verify-oracle` 删模块回归 |
| `harness/scripts/audit_output_imports.py` | metadata.output vs 测试 import |
| `harness/scripts/analyze_benchmark_suite.py` | suite 汇总 + high/compact pass 分类 + `eval_flake` |
| `harness/scripts/preflight.py` | 开跑前环境/API key/mini 预检 |
| `setup.sh` / `harness/scripts/server_setup.sh` | 一键 venv + 依赖 + 配置模板 |
| `harness/scripts/reeval_suite.py` | 不重跑 agent，批量重算 eval 并更新 suite.json |
| `harness/scripts/report_entanglement_coverage.py` | 按 primary 分层通过率 |
| `harness/scripts/calibrate_flash_baseline.sh` | Flash 50-hard 封装（Python 3.12） |
| `harness/scripts/calibrate_pro_baseline.sh` | Pro 50-hard 封装（Python 3.12） |
| `docker/Dockerfile.eval` | 可复现 eval 镜像（默认 Python 3.11 slim + pytest 7.4.4；base image 可覆盖） |
| `docker/Dockerfile.agent` | bounded agent run 镜像（pin `mini-swe-agent==1.17.3`） |
| `harness/scripts/list_tasks.py` | 默认列出主榜 tasks；`--include-sanity` 含 smoke |

Suite 产物每题目录：

```text
experiments/mini-swe-agent/<run_id>/<task_id>/
  agent/trajectory.json
  submission/
  eval/result.json
  run.json
```

---

## 规格缺口（仍有效）

| 层级 | 说明 |
| --- | --- |
| L1 | `metadata.output.import` 窄于测试实际 import → Agent 按题面做最小实现时 hidden 挂 |
| L3 | hidden 比 `included_behaviors` 严 → functional discriminator；但与 copy-all 区分仍不足 |
| 解耦维度 | 多题 Flash functional pass + extraction>0.85（click、markdown_it、pyyaml、lark、typer 等） |

详见历史 L3 表（28 题时期）及 [limitations.md](limitations.md)。
