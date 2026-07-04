# Go Pilot 验收报告（10 Gold）

**状态：** Phase 2 进行中（目录 10 题；**真 gold-quality 3/10**）
**最后更新：** 2026-07-04

---

## 摘要

| 项 | 值 |
| --- | --- |
| Spec | v2 Go pilot（10 gold，**不扩 100**） |
| 目录题数 | **10 / 10** |
| **真 gold-quality** | **3 / 10**（semver、humanize、mapstructure） |
| Unique repos（真 gold） | 3 |
| Harness | `go_eval.py` + Docker eval + `run_go_pilot_review.sh` |
| Agent baselines | `run_go_openhands.sh`（主 agent）· `run_go_baseline.sh`（copy_all） |

实验协议（与 Python 分离）：[GO_EXPERIMENT_PROTOCOL.md](GO_EXPERIMENT_PROTOCOL.md)

**策略：** 先做好 10 个 gold-quality 样例（论文骨架），再扩到 100；baseline 先跑最小三环，模型统一 `deepseek_v4_flash`，**≤120 步**。

---

## Gold-quality 六条（每题必达）

| # | 要求 | semver | humanize | mapstructure | 其余 7 题 |
| --- | --- | --- | --- | --- | --- |
| 1 功能真实有用 | design note 可答 reuse | ✓ | ✓ | ✓ | ✗ hello 模板 |
| 2 原仓缠绕 | ≥2 entanglement | ✓ | ✓ | ✓ | ✗ |
| 3 可抽独立包 | oracle go.mod | ✓ | ✓ | ✓ | 形式有、实质无 |
| 4 hidden 判别 | naive/copy 分层 | ✓ | ✓ | ✓ | stub only |
| 5 evaluator 稳定 | Docker eval pass | ✓ | ✓ | ✓ | 仅 hello 可跑 |
| 6 人类可读 | TASK + design | 部分 | ✓ | ✓ | 模板 |

---

## 题目清单

| task_id | source repo | 真 gold? | gate (mechanical) | Flash |
| --- | --- | --- | --- | --- |
| semver__version_parse_core__001 | Masterminds/semver | **是** | promote | pipeline A* |
| humanize__bytes_format_core__001 | dustin/go-humanize | **是** | promote | pipeline A* |
| mapstructure__decode_core__001 | go-viper/mapstructure | **是** | promote | stub |
| gojsonschema__validate_core__001 | xeipuuv/gojsonschema | 否 | promote* | stub |
| doublestar__glob_match_core__001 | bmatcuk/doublestar | 否 | promote* | stub |
| uuid__parse_format_core__001 | google/uuid | 否 | promote* | stub |
| expr__eval_core__001 | expr-lang/expr | 否 | promote* | stub |
| validator__struct_validate_core__001 | go-playground/validator | 否 | promote* | stub |
| copier__deep_copy_core__001 | jinzhu/copier | 否 | promote* | stub |
| bluemonday__sanitize_policy_core__001 | microcosm-cc/bluemonday | 否 | promote* | stub |

\*机械 gate 在 hello 模板上通过，**不代表 gold-quality**。

\*pipeline A：`experiments/go-openhands/go-openhands-*-pilot-001` 为 **PIPELINE_SMOKE=1** 闭环（naive 代理验证 harness）；WSL 内真实 OpenHands 待跑后替换 flash 证据。

证据：`experiments/go-pilot/<task_id>/review/gate_report.json`

---

## Baseline 最小闭环（待跑）

| Baseline | 含义 | 命令 |
| --- | --- | --- |
| **copy_all** | 整仓复制惩罚 | `bash harness/scripts/run_go_baseline.sh copy_all <task_id>` |
| **mini** | mini-swe-agent + Flash | `bash harness/scripts/run_go_baseline.sh mini <task_id>` |
| **strong** | mini + `--yolo`（加强自主） | `bash harness/scripts/run_go_baseline.sh strong <task_id>` |
| **openhands** | OpenHands headless + Flash | `bash harness/scripts/run_go_openhands.sh <task_id>` |

共用设置：agent 实验建议 `deepseek_v4_flash`、≤120 步；eval 用 `--eval-docker`。
**OpenHands 未原生接入**，通过 `--agent command` 调用；见 `run_go_openhands.sh`。

OpenHands / Cursor-like strong flow：`run_go_openhands.sh` 为当前推荐路径；`strong` 仍用 mini+yolo 占位。

---

## Flash A/B/C 分布

| Tier | Count | 说明 |
| --- | ---: | --- |
| A (pipeline) | 2 | semver/humanize：`go-openhands-*-pilot-001`（PIPELINE_SMOKE，public ✓ hidden ✗） |
| A (stub) | 7 | 含 mapstructure gate promote；其余 hello 题 seed |

正式 Flash 实验：对 gold-ready 子集跑 `run_go_baseline.sh mini`，再更新本表。

---

## 机械 Gate 汇总（目录 10 题）

| Gate | Pass rate |
| --- | ---: |
| G0–G4（hello 题） | 10/10 |
| G5 Flash recorded | 10/10（stub） |
| G6 docs | 3/10 design notes |

---

## 下一步

1. 按 playbook 深化剩余 **7** 道（一次 1–2 题）。
2. **WSL 内真跑 OpenHands**（semver/humanize），替换 pipeline flash 证据；再对 gold 子集跑 copy_all baseline。
3. 10 题全真 gold 后写论文案例表；**再**启动 Phase 3（扩 100）。

---

## 相关

- [GO_PILOT_PLAYBOOK.md](GO_PILOT_PLAYBOOK.md)
- [GO_QUALITY_RUBRIC.md](GO_QUALITY_RUBRIC.md)
