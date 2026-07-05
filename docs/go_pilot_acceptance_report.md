# Go Pilot 验收报告（Calibration + Hardening）

**状态：** hardening 进行中（4 道 calibration/easy-B 已完成真实 Flash；hard paper-ready 0/10）
**最后更新：** 2026-07-05

---

## 摘要

| 项 | 值 |
| --- | --- |
| Spec | v2 Go pilot（目标 10 hard gold，**不扩 100**） |
| 目录题数 | **10 原候选 + 1 hardening attempt + 1 sanity** |
| **gold_verified_calibration** | **4**（3 原候选 + `mapstructure__decode_core_hard__001`） |
| **Hard paper-ready** | **0 / 10** |
| Active hard design candidates | **1**（`mapstructure__decode_symbol_core__002`，未进 staging） |
| Unique repos（calibration） | 3 |
| Harness | `go_eval.py` + Docker eval + `run_go_pilot_review.sh` |
| Agent baselines | `run_go_openhands.sh`（主 agent）· `run_go_baseline.sh`（copy_all） |

实验协议（与 Python 分离）：[GO_EXPERIMENT_PROTOCOL.md](GO_EXPERIMENT_PROTOCOL.md)

**策略：** 把 4 个 easy-B 保留为 pipeline calibration；下一版 hard task 必须避免干净文件边界抽取，验证 hard gate 有效后再复制模式扩到 5 道、10 道。

---

## Calibration 结论

| # | 要求 | semver | humanize | mapstructure | 结论 |
| --- | --- | --- | --- | --- | --- |
| 1 功能真实有用 | design note 可答 reuse | ✓ | ✓ | ✓ | calibration 可保留 |
| 2 原仓缠绕 | ≥2 entanglement | ✓ | ✓ | ✓ | source slice 合格 |
| 3 可抽独立包 | oracle go.mod | ✓ | ✓ | ✓ | oracle 可复核 |
| 4 hidden 判别 | naive/copy 分层 | ✓ | ✓ | ✓ | 机械 gate 合格 |
| 5 evaluator 稳定 | Docker eval pass | ✓ | ✓ | ✓ | harness 合格 |
| 6 agent 难度 | Flash 不应 oracle-footprint 全过 | ✗ | ✗ | ✗ | 不进 hard paper-ready |

判定规则：当 OpenHands + Flash hidden pass 且 `abs(flash_ext - oracle_ext) < 0.03` 时，结果记为 `promote_calibration`，不记为 hard paper-ready。

---

## 题目清单

| task_id | source repo | 状态 | gate/readiness | Flash |
| --- | --- | --- | --- | --- |
| semver__version_parse_core__001 | Masterminds/semver | **gold_verified_calibration** | promote_calibration | B, hidden pass, ext=oracle=0.574468 |
| humanize__bytes_format_core__001 | dustin/go-humanize | **gold_verified_calibration** | promote_calibration | B, hidden pass, ext=oracle=0.323944 |
| mapstructure__decode_core__001 | go-viper/mapstructure | **gold_verified_calibration** | promote_calibration | B, hidden pass, ext=oracle=0.597633 |
| mapstructure__decode_core_hard__001 | go-viper/mapstructure | **gold_verified_calibration** | promote_calibration | B, hidden pass, ext=oracle=0.571253 |
| mapstructure__decode_symbol_core__002 | go-viper/mapstructure | **shortlist** | design gate pending | not run |
| gojsonschema__validate_core__001 | xeipuuv/gojsonschema | seed | not hard-ready | stub |
| doublestar__glob_match_core__001 | bmatcuk/doublestar | seed | not hard-ready | stub |
| uuid__parse_format_core__001 | google/uuid | seed | not hard-ready | stub |
| expr__eval_core__001 | expr-lang/expr | seed | not hard-ready | stub |
| validator__struct_validate_core__001 | go-playground/validator | seed | not hard-ready | stub |
| copier__deep_copy_core__001 | jinzhu/copier | seed | not hard-ready | stub |
| bluemonday__sanitize_policy_core__001 | microcosm-cc/bluemonday | seed | not hard-ready | stub |

\*旧的 pipeline A 证据来自 **PIPELINE_SMOKE=1** 闭环（naive 代理验证 harness），不再计入 Flash。

证据：`experiments/go-pilot/<task_id>/review/gate_report.json`

---

## Baseline / Agent 闭环

| Baseline | 含义 | 命令 |
| --- | --- | --- |
| **copy_all** | 整仓复制惩罚 | `bash harness/scripts/run_go_baseline.sh copy_all <task_id>` |
| **mini** | mini-swe-agent + Flash | `bash harness/scripts/run_go_baseline.sh mini <task_id>` |
| **strong** | mini + `--yolo`（加强自主） | `bash harness/scripts/run_go_baseline.sh strong <task_id>` |
| **openhands** | OpenHands headless + Flash | `bash harness/scripts/run_go_openhands.sh <task_id>` |

共用设置：agent 实验建议 `deepseek_v4_flash`、≤120 步；eval 用 `--eval-docker`。
OpenHands 通过 `--agent command` 调用；见 `run_go_openhands.sh`。

OpenHands / Cursor-like strong flow：`run_go_openhands.sh` 为当前推荐路径；`strong` 仍用 mini+yolo 占位。

---

## Flash A/B/C 分布

| Tier | Count | 说明 |
| --- | ---: | --- |
| B calibration | 4 | semver/humanize/mapstructure + hardening attempt：Flash hidden pass 且 `flash_extraction == oracle_extraction` |
| not run | 1 | `mapstructure__decode_symbol_core__002` 仅为 design shortlist，尚未进入 staging |
| stub/seed | 7 | 其余 hello 题 seed，不计入 Flash 分布 |

正式 hard 实验：下一版 hard task 先做非文件边界抽取设计，再跑 OpenHands + Flash。

---

## 机械 Gate 汇总（不含 sanity）

| Gate | Pass rate |
| --- | ---: |
| G0 no-stub | 4/11（3 calibration + 1 hardening；7 题仍是 hello/add.go 模板） |
| G1–G4 fresh baseline evidence | 4/11 已通过 |
| G5 real Flash/OpenHands | 4/11 已跑，但均为 calibration |
| G6 docs | 4/11 design notes |
| G8 hard readiness | 0/11 hard paper-ready |

---

## 下一步

1. 设计第二版 hard task：`mapstructure__decode_symbol_core__002`，避免“复制一组目标 `.go` 文件”即可过关。
2. 优先尝试非文件边界抽取：目标行为嵌在共享文件里，oracle 需要重组而不是整文件复制。
3. 继续使用 hard-readiness gate：Flash hidden pass 且 oracle footprint 相同一律降为 calibration。
4. 保留 4 道 calibration/easy-B，不进入 hard 主表。

---

## 相关

- [GO_PILOT_PLAYBOOK.md](GO_PILOT_PLAYBOOK.md)
- [GO_QUALITY_RUBRIC.md](GO_QUALITY_RUBRIC.md)
