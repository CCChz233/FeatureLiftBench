# Go Benchmark TODO（设计收敛版）

**最后更新：** 2026-07-05
**目标：** 把 Go track 从“目录里有 10 题”推进到“10 道 hard paper-ready gold 题”，再决定是否扩到 100。

本文是 Go benchmark 的执行 TODO，也是当前优化后的设计口径。已有设计文档仍然有效：
[GO_EXPANSION.md](GO_EXPANSION.md)、
[GO_PILOT_PLAYBOOK.md](GO_PILOT_PLAYBOOK.md)、
[GO_QUALITY_RUBRIC.md](GO_QUALITY_RUBRIC.md)、
[GO_EXPERIMENT_PROTOCOL.md](GO_EXPERIMENT_PROTOCOL.md)。

---

## 0. 当前判断

Go track 的研究方向没有问题：仍然测 **behavior-preserving feature-level decoupling**，不是 bug fixing，也不是从零实现。需要改进的是 **状态口径、gate 强度、题目难度**。

当前不要再说“Go 10 hard gold 已完成”，也不要把 semver/humanize/mapstructure 三题写成 hard paper-ready。正确口径是：

| 项 | 当前 |
| --- | ---: |
| Harness MVP | 完成 |
| `benchmark/go/tasks/` 目录 | 10 原候选题 + 1 hardening attempt + 1 sanity |
| `gold_verified_calibration` | 4（3 原候选 + 1 hardening attempt；均为 Flash hidden pass + oracle footprint） |
| hard paper-ready Go gold | 0/10 |
| active hard design 候选 | 1（`mapstructure__decode_symbol_core__002`，未进 staging） |
| Go 100 | 未启动 |

3 个已校准但偏简单的 calibration/easy-B 题：

- `semver__version_parse_core__001`
- `humanize__bytes_format_core__001`
- `mapstructure__decode_core__001`

OpenHands + `deepseek/deepseek-v4-flash` 对这三题均 public+hidden pass，且 `flash_extraction == oracle_extraction`：

| task_id | Flash tier | oracle/flash extraction | 结论 |
| --- | --- | ---: | --- |
| `semver__version_parse_core__001` | B | 0.574468 | `promote_calibration` |
| `humanize__bytes_format_core__001` | B | 0.323944 | `promote_calibration` |
| `mapstructure__decode_core__001` | B | 0.597633 | `promote_calibration` |

这说明流程和 evaluator 是通的，但题目对当前强 agent 判别力不足。

已完成但未达 hard readiness 的 hardening attempt：

- `mapstructure__decode_core_hard__001`：Flash B，oracle/flash extraction 0.571253，`promote_calibration`

7 个当前应降级为 seed/staging 的模板题：

- `gojsonschema__validate_core__001`
- `doublestar__glob_match_core__001`
- `uuid__parse_format_core__001`
- `expr__eval_core__001`
- `validator__struct_validate_core__001`
- `copier__deep_copy_core__001`
- `bluemonday__sanitize_policy_core__001`

`hello_featurelifted__001` 只保留为 sanity，不进入 gold 计数。

---

## 1. 优化后的设计原则

### 1.1 分区报告

Go 与 Python 必须分开报告：

- Python 主榜：`benchmark/tasks/`，100 hard。
- Go pilot：`benchmark/go/tasks/`，目标 10 hard gold。
- 论文表格不能把 Python 与 Go 混成一个总分。
- Go 在 10 hard gold 之前只能叫 pilot / v2 track / extensibility study。

### 1.2 状态机

以后每道 Go 题只允许落在一个明确状态里：

| 状态 | 含义 | 可对外声称 |
| --- | --- | --- |
| `seed` | 只有模板、想法或候选 repo | 不能计入 benchmark |
| `staging` | 有真实 repo slice 设计，正在做 oracle/tests | 候选题 |
| `mechanical_valid` | `validate-task` 与基础 eval 能跑 | harness 可处理 |
| `gold_candidate` | oracle/naive/copy_all/probes 初步分层 | 候选 gold |
| `gold_verified` | Docker/WSL evidence 与当前文件一致，但尚未证明 agent 难度 | 机械 gold 候选 |
| `gold_verified_calibration` | 真实 agent 跑通但题目过易，常见信号是 Flash hidden pass 且 footprint 贴近 oracle | calibration / easy-B |
| `paper_ready_hard` | 真实 agent 校准显示足够判别力，文档和证据冻结 | 可进论文 hard 表 |

禁止把 `seed` 或 `mechanical_valid` 写成 `accepted` / `promote` / `gold`。
`promote_calibration` 只表示流程和题定义通过，不等于 `paper_ready_hard`。

### 1.3 证据分三层

每题必须同时有三层证据：

| 层 | 证据 | 作用 |
| --- | --- | --- |
| Task evidence | `metadata.json`、`TASK.md`、design note、public/hidden tests、probes | 证明题定义真实 |
| Baseline evidence | oracle / naive / copy_all 的 Docker eval result | 证明题可解且能分层 |
| Agent evidence | OpenHands/Flash 等真实 agent run | 证明 benchmark 有模型判别力 |

`PIPELINE_SMOKE=1` 只能证明 harness 闭环，不能作为 agent evidence。

---

## 2. 新 Go Gold Gates

这些 gate 是进入 `paper_ready_hard` 的硬门。任何一项失败，都不能进入 hard paper-ready 表。

| Gate | 名称 | 必须满足 |
| --- | --- | --- |
| G0 | no-stub shape | 不是 hello/Add 模板；有 design note；source repo 至少多文件；`TASK.md` 与真实 feature 对齐 |
| G1 | oracle | public+hidden 全过；无 forbidden import；oracle 是独立 `go.mod`；不是单文件薄 wrapper |
| G2 | naive | public pass、hidden fail；失败点指向真实 missing behavior |
| G3 | copy_all | functional pass；extraction 高；与 oracle 拉开足够差距 |
| G4 | probes | 至少 3 个 module probe；每个 probe 映射到 hidden 行为 |
| G5 | docs | design note、candidate backlog、acceptance report、task metadata 一致 |
| G6 | real agent | 至少一次真实 agent 校准；记录 A/B/C；不能只用 pipeline smoke |
| G7 | fresh evidence | `gate_report.json` 从当前 result 生成；result 与当前文件 LOC/commit 对齐 |
| G8 | hard readiness | 若 Flash hidden pass 且 `abs(flash_ext - oracle_ext) < 0.03`，或 Flash footprint 接近 copy_all，只能标 `promote_calibration`；hard 题需要 public pass / hidden fail，或 compact、non-oracle、明显低于 copy_all 的 pass |

建议增加脚本级检查：

- oracle 里出现 `func Add(` 且 task 不是 sanity，直接 fail。
- `TASK.md` 标题仍是 `hello_featurelifted__001`，直接 fail。
- `docs/go_task_designs/<task_id>.md` 不存在，直接 fail。
- `repo/` 只有 1 个 `.go` 文件且无书面例外，直接 fail。
- oracle runtime `.go` 文件数 `< 2` 且无书面例外，直接 fail。
- `flash_tier=A` 但 `flash/run.json` 来自 `PIPELINE_SMOKE=1`，不能计入 G6。

---

## 2.5 Hard Task 设计红线

下一版 Go hard task 不能再以文件为解耦边界。`repo/*.go` 文件名、注释、模块布局都不能让 agent 通过“选择一组文件并改 package name”直接等于 oracle。

必须满足：

- target behavior 以 symbol / function / method / type 为边界，而不是 `.go` 文件为边界。
- 至少两个源文件同时包含 target 和 non-target 代码；整文件复制必须显著高于 oracle extraction。
- oracle 需要重组、裁剪或改写代码，不能只是从 `repo/` 排除一批文件。
- public tests 只能描述 API 和主路径，不能透露 hidden 覆盖点或目标文件名。
- hidden tests 覆盖跨函数状态、tag/hook 顺序、错误路径和组合行为。
- 若 Flash hidden pass 且 footprint 等于 oracle，降级为 calibration。
- 若 Flash hidden pass 但 footprint 接近 copy_all，也降级为 calibration；只有 public pass / hidden fail，或 hidden pass 且 compact、非 oracle、明显低于 copy_all，才可进入 `paper_ready_hard`。

推荐结构：

- `repo/decode.go` 同时含 decode target、encode/flatten non-target、field path helpers。
- `repo/fields.go` 同时含 target tag parsing 和 non-target field cache/schema logic。
- `repo/hooks.go` 同时含 target hook composition 和 non-target hook registry/validation logic。
- `repo/value.go` 同时含 target weak conversion 和 non-target normalization helpers。
- oracle 从这些文件中抽 symbol-level subset，并适当改写依赖，不保留原文件完整内容。

---

## 3. Hard Paper-Ready Definition

一题进入 `paper_ready_hard`，必须有：

```text
benchmark/go/tasks/<task_id>/
  metadata.json
  TASK.md
  repo/
  public_tests/
  hidden_tests/
  evaluation/
    forbidden_imports.txt
    module_probes.json
  environment/go.mod

benchmark/submissions/<task_id>/
  oracle/
  naive/
  copy_all/

docs/go_task_designs/<task_id>.md

experiments/go-pilot/<task_id>/review/
  gate_report.json
  decision.md
  validate-task.log
  audit-output-imports.log
  module-probes.log
  oracle/result.json
  naive/result.json
  copy_all/result.json
  flash/run.json
```

`gate_report.json` 必须记录：

- task id
- harness git commit
- source repo commit/tag
- oracle / naive / copy_all result path
- oracle LOC、source LOC、extraction ratio
- Flash/OpenHands run id
- readiness classification（`promote_calibration` 或 `paper_ready_hard`）
- 是否 Docker eval
- 是否 pipeline smoke
- final decision

---

## 4. 当前执行计划

### Phase A - 先修口径

- [x] 把 7 个模板题在文档中降级为 `seed` 或 `staging`。
- [x] 保留 `hello_featurelifted__001` 为 sanity，不计入 10 hard gold。
- [x] 修改 Go acceptance report：目录数、calibration、hard paper-ready 三个数字分开写。
- [x] 修改 candidate backlog：不要把模板题标成 `accepted`。
- [x] 增加 no-stub gate，防止模板题再次被 promote。

完成标准：

- 所有文档都承认当前为 4 个 `gold_verified_calibration`（含 1 个 hardening attempt），hard paper-ready 仍是 `0/10`。
- 没有任何 `Add(a,b)` 模板题被称为 gold。

### Phase B - 完成 3 个候选的真实校准

对以下三题逐题重新生成 evidence：

- [x] `semver__version_parse_core__001`：G0-G5 已刷新，Flash B，`promote_calibration`
- [x] `humanize__bytes_format_core__001`：G0-G5 已刷新，Flash B，`promote_calibration`
- [x] `mapstructure__decode_core__001`：G0-G5 已刷新，Flash B，`promote_calibration`

每题执行：

- [x] 重新跑 `validate-task`。
- [x] 重新生成本地 submissions：`PYTHONPATH=harness python harness/scripts/build_go_oracle_submission.py --all-ready --variant all`。
- [x] 构建或确认 Go eval 镜像：`bash docker/build_go_eval_image.sh featureliftbench-eval-go:latest`。
- [x] 重新跑 oracle Docker eval。
- [x] 重新跑 naive Docker eval。
- [x] 重新跑 copy_all Docker eval。
- [x] 重新跑 module probes。
- [x] 检查 `result.json` 里的 LOC 与当前文件一致。
- [x] 真跑 OpenHands/Flash；不能用 `PIPELINE_SMOKE=1` 代替。
- [x] 同步 Flash 结果到 `experiments/go-pilot/<task_id>/review/flash/run.json`。
- [x] 重新生成 `gate_report.json`，使用 `promote_calibration` / `paper_ready_hard` 区分口径。
- [ ] 如需冻结 calibration 包，再生成 `decision.md`。
- [x] 更新 `go_pilot_acceptance_report.md` 到 calibration/easy-B 状态。

完成标准：

- 3 题全部达到 `gold_verified_calibration`，但不进入 hard paper-ready 表。
- 证据包可从零复核，不依赖旧 result。

结论：OpenHands + `deepseek/deepseek-v4-flash` 三题全过 hidden，且 footprint 等于 oracle，说明这些题适合 pipeline calibration，不适合作为 hard 主证据。

### Phase C - 先做 1 道 hard Go 题

首个 hardening 任务：

1. [x] 新建 `mapstructure__decode_core_hard__001`。
2. [x] TASK 只描述目标 API 和功能范围，不直接列 hidden 覆盖点。
3. [x] repo 中加入真实相近干扰文件，避免目标文件名一眼可见。
4. [x] 覆盖 nested struct、pointer fields、slice/map decode、`encoding.TextUnmarshaler`、DecodeHook 顺序、squash 冲突、unused metadata。
5. [x] 跑 `validate-task`、oracle/naive/copy_all、module probes、Docker mechanical gate。
6. [x] OpenHands + `deepseek/deepseek-v4-flash` 校准。
7. [x] 判断 Flash 是否 trivially match oracle footprint：是，降为 `promote_calibration`。

Hard task 验收标准：

- oracle pass public+hidden。
- naive public pass hidden fail，extraction ≤ 0.11。
- copy_all pass，extraction ≥ 0.85 或满足 trim exception。
- OpenHands Flash 理想结果是 public pass / hidden fail；若 hidden pass，则 extraction 必须明显低于 copy_all 且不等于 oracle。

当前结论：第一版 hardening 仍失败于 hard readiness。即使重命名干扰文件、移除 obvious `excluded` 提示，Flash 仍精准抽出 oracle 文件集。下一版需要避免干净文件边界，例如把目标行为嵌入共享文件、要求 API 语义重组，或引入必须改写的 cross-file state，而不是单纯复制目标 `.go` 文件。

### Phase C2 - 第二版 symbol-boundary hard 设计

当前 hard 设计候选：

- [x] 新建 design spike：`docs/go_task_designs/mapstructure__decode_symbol_core__002.md`。
- [x] 明确 Practical reuse 三问。
- [x] 写 Boundary Plan，目标边界落在 symbols / behavior，不落在 `.go` 文件。
- [x] 明确至少四个源文件混合 target 与 non-target symbols。
- [x] 明确 oracle transformation：裁剪、重组、修依赖，而不是整文件复制。
- [ ] 进入 staging 前做人工 design gate review。
- [ ] 生成真实 `benchmark/go/staging/mapstructure__decode_symbol_core__002`。
- [ ] 跑 oracle/naive/copy_all/probes。
- [ ] 跑 OpenHands + `deepseek/deepseek-v4-flash`。
- [ ] 只有通过 G8 hard readiness 才标 `paper_ready_hard`。

完成标准：第二版 task 即使 functional pass，也不能因为 Flash 复制了 oracle footprint 而入 hard 表；若再次 oracle-footprint hidden pass，继续降为 `promote_calibration` 并 redesign/drop。

### Phase D - 逐题把 7 个 seed 做成真题

建议顺序：

1. [ ] `gojsonschema__validate_core__001`
2. [ ] `doublestar__glob_match_core__001`
3. [ ] `uuid__parse_format_core__001`
4. [ ] `bluemonday__sanitize_policy_core__001`
5. [ ] `validator__struct_validate_core__001`
6. [ ] `copier__deep_copy_core__001`
7. [ ] `expr__eval_core__001`

每题工作循环：

1. [ ] 写 design note：`docs/go_task_designs/<task_id>.md`。
2. [ ] 明确 reusable API：谁会 import、为什么不是 copy-all。
3. [ ] 明确 included / excluded behavior。
4. [ ] 固定 source commit/tag 与 license。
5. [ ] 替换模板 `repo/`，放入真实 Go source slice。
6. [ ] 写 public tests：覆盖主路径，给 agent 足够接口提示。
7. [ ] 写 hidden tests：覆盖组合、边界、错误、状态或反射语义。
8. [ ] 写 oracle：独立 `go.mod`，不 import 原 module path。
9. [ ] 写 naive：public pass、hidden fail。
10. [ ] 写 copy_all：functional pass 但 extraction 高。
11. [ ] 写至少 3 个 module probes。
12. [ ] 跑 G0-G8。
13. [ ] 只在全部通过后标为 `paper_ready_hard`。

完成标准：

- 7 题全部从 seed 变成 hard paper-ready。
- 10 hard gold 中至少 8 个唯一 source repo。
- Flash/OpenHands A/B/C 分布真实可解释。

### Phase E - 10 Hard Gold 验收

- [ ] `benchmark/go/tasks/` 中恰好 10 个 hard gold 题，sanity 和 calibration 题单独列。
- [ ] 每题有 `decision.md` 和 `gate_report.json`。
- [ ] 每题 oracle/naive/copy_all result 都是当前文件重新跑出来的。
- [ ] 每题真实 agent 校准完成。
- [ ] 写 Go 10 hard gold 总表：source repo、feature、entanglement、oracle LOC、copy_all LOC、Flash tier。
- [ ] 更新 [BENCHMARK_SPEC.md](BENCHMARK_SPEC.md) 的 Go roadmap。
- [ ] 更新 [EXPERIMENT_RESULTS.md](EXPERIMENT_RESULTS.md) 的 Go 分区。

完成标准：

- 可以诚实写：“Go track includes 10 hard paper-ready gold tasks.”
- 仍然不和 Python 主榜混表。

### Phase F - 再决定是否扩到 100

只有 Phase E 完成后，才启动 Go 100。

- [ ] 把 repo 候选池扩到 60+。
- [ ] 先每批 5 题 staging，不允许批量 promote。
- [ ] 每题仍按 G0-G8 入榜。
- [ ] 100 题只在同一 eval image、同一 gate 版本下冻结。

---

## 5. 单题模板 TODO

复制下面清单到每个 `decision.md` 或 issue 中。

```markdown
# TODO: <task_id>

Status: seed | staging | mechanical_valid | gold_candidate | gold_verified | gold_verified_calibration | paper_ready_hard

## Design
- [ ] design note exists
- [ ] reusable API is clear
- [ ] included/excluded behavior is clear
- [ ] source commit/tag and license recorded
- [ ] at least 2 entanglement signals

## Task Files
- [ ] metadata.json
- [ ] TASK.md is not hello/Add template
- [ ] real repo snapshot
- [ ] public_tests
- [ ] hidden_tests
- [ ] environment/go.mod
- [ ] forbidden_imports.txt
- [ ] module_probes.json with >=3 probes

## Submissions
- [ ] oracle
- [ ] naive
- [ ] copy_all

## Gates
- [ ] G0 no-stub shape
- [ ] G1 oracle
- [ ] G2 naive
- [ ] G3 copy_all
- [ ] G4 probes
- [ ] G5 docs
- [ ] G6 real agent
- [ ] G7 fresh evidence
- [ ] G8 hard readiness

## Decision
Decision: promote_calibration | paper_ready_hard | redesign | drop
Flash tier: A | B | C | not_run
Notes:
```

---

## 6. 命令速查

Windows 推荐在 WSL + Docker Desktop 内执行 Go 评测。以下命令是论文口径的方向，具体参数以脚本为准。

```bash
export PYTHONPATH=harness

python harness/scripts/build_go_oracle_submission.py --all-ready --variant all

bash docker/build_go_eval_image.sh featureliftbench-eval-go:latest

python -m featureliftbench.cli validate-task benchmark/go/tasks/<task_id>

bash harness/scripts/run_go_pilot_review.sh <task_id> --docker

python -m featureliftbench.cli eval benchmark/go/tasks/<task_id> \
  benchmark/submissions/<task_id>/oracle \
  --output experiments/go-pilot/<task_id>/review/oracle \
  --docker

python -m featureliftbench.cli eval benchmark/go/tasks/<task_id> \
  benchmark/submissions/<task_id>/naive \
  --output experiments/go-pilot/<task_id>/review/naive \
  --docker

python -m featureliftbench.cli eval benchmark/go/tasks/<task_id> \
  benchmark/submissions/<task_id>/copy_all \
  --output experiments/go-pilot/<task_id>/review/copy_all \
  --docker

python harness/scripts/verify_module_probes.py \
  --task benchmark/go/tasks/<task_id> \
  --submission benchmark/submissions/<task_id>/oracle \
  --verify-oracle \
  --docker

bash harness/scripts/run_go_openhands.sh <task_id>
```

---

## 7. 论文口径

当前可写：

- FeatureLiftBench 的核心贡献是功能级解耦任务定义、数据集构建方法、oracle/naive/copy_all 分层、functional 与 extraction 双指标。
- Python 100 hard 是主实验分区。
- Go track 是 v2 pilot，当前有 4 道 `gold_verified_calibration`（其中 1 道是失败的 hardening attempt），下一步要先做出 1 道真正 hard task，再扩到 10 hard paper-ready gold。

当前不要写：

- Go 10 hard gold 已完成。
- Go 100 已启动。
- Go 与 Python 有统一总榜。
- `PIPELINE_SMOKE` 代表真实 agent 难度。

10 个 Go hard paper-ready 完成后可写：

- Go 10 hard gold 分区展示跨语言可扩展性。
- Go 与 Python 共享 decoupling 语义，但 evaluator、module layout、agent runner 分区报告。
- Go 结果只与 Go 题互比，不与 Python 总分混排。
