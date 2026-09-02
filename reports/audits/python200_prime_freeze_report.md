# Python-200′ 冻结与主实验就绪报告

更新日期：2026-09-01

## 1. 当前结论

Python-200′ 的 benchmark 工程冻结门槛已经通过，可以作为后续论文主实验的固定评测集使用。

- 正式冻结 ID：`474862c22165ac9cc8ab895f1e265dd0bb43da81f52e77561b29fde44798a8d8`
- 候选内容 ID：`769f2486c0abb9f0df6324f74b8313da6e1711febce1208c945a2511bd3a7c18`
- Compactness 注册表 ID：`b32c3dfefc82f266afd501a78064c30bc85f5c3949c0c2e2ce8d04730c75397b`
- 任务构成：Python-150 + Hard-50，共 200 题
- 信息条件：Full-Repository / No-Hint，benchmark tests 对 Agent 不可见
- 主指标：Functional Pass@1
- 功能通过定义：Build AND Public AND Hidden AND Isolation

冻结清单中的 `release_name=Python-200-prime` 是当前正式发布身份。内部 suite manifest 仍保留原有 `unreleased` 字样作为生成谱系；论文、实验和复现均应以正式冻结 ID 为唯一标识，不能只引用旧 suite ID。

## 2. 已通过的门槛

| 门槛 | 结果 | 证据 |
|---|---:|---|
| 任务结构与规范验证 | 200/200 | 正式冻结清单中的 `gates.task_validation` |
| Source 映射 | 200/200 | 候选冻结清单与 source registry |
| Source archive 校验 | 182/182 snapshots | 候选冻结清单中的 `source_verification` |
| Hidden 契约候选集未决项 | 0 | Hidden rejudgement ledger |
| Python 3.11 离线依赖/wheel | 200/200 | 冻结前统一工程门槛报告 |
| Oracle Docker 复验 | 600/600 | 200 题 × 3 次全部通过 |
| Oracle 不稳定任务 | 0/200 | 正式 Oracle summary |
| 最终镜像平台 | linux/amd64 | 镜像标签与 Docker inspect |
| 快速回归测试 | 40/40 | constitution、freeze、agent/eval Docker tests |
| 正式模型实验预检 | PASS | 200/200 runnable，Docker/配置/网络路由通过 |

Oracle 复验保留了每一次运行的完整结果，而不是只保存聚合数字；失败任务、缺失结果和不稳定任务均为空。

## 3. 最终运行环境

### Agent 镜像

- Tag：`featureliftbench-agent:python200-prime-769f2486`
- Digest：`sha256:70808ca9144711c8acdc4558cdea69614b86bed4891aebfa1c234454bffeb816`
- Platform：`linux/amd64`
- OpenHands CLI：`1.16.0`
- Benchmark label：完整候选内容 ID `769f2486…a7c18`

### Evaluator 镜像

- Tag：`featureliftbench-eval:python200-prime-769f2486`
- Digest：`sha256:b8fc25c81722ab5aeebd026bd79dffb2eab17f86a230b7d7f78926234a6ce676`
- Platform：`linux/amd64`
- Python：`3.11.14`
- Go：`1.22.5 linux/amd64`
- Benchmark label：完整候选内容 ID `769f2486…a7c18`

Oracle evidence 中记录的 evaluator image ID 与上述 evaluator digest 一致。

## 4. 核心证据文件

- 正式冻结清单：`artifacts/research_analysis/python200_prime/current_benchmark_freeze.json`
- 不可变冻结副本：`artifacts/research_analysis/python200_prime/freezes/474862c22165ac9cc8ab895f1e265dd0bb43da81f52e77561b29fde44798a8d8.json`
- 候选冻结清单：`artifacts/research_analysis/python200_prime/current_candidate_freeze.json`
- 600 次 Oracle 结果：`reports/audits/python200_prime_oracle_revalidation/summary.json`
- Compactness 注册表：`benchmark/references/python200_prime_compactness.json`
- Hidden 契约重审：`artifacts/research_analysis/hidden_provenance/python200_prime_candidate_rejudgement_20260831.json`
- 正式冻结构建器：`scripts/build_python200_prime_final_freeze.py`
- 正式主实验运行器：`harness/scripts/archive/run_python200_prime_paper.sh`

正式冻结可重复自校验：

```bash
python3.12 scripts/build_python200_prime_final_freeze.py --check \
  --agent-image featureliftbench-agent:python200-prime-769f2486 \
  --evaluator-image featureliftbench-eval:python200-prime-769f2486
```

## 5. 正式模型主实验

主实验配置已经完成无付费预检：

- Profile：`openhands_deepseek_v4_flash`
- Model：`deepseek/deepseek-v4-flash`
- Method arm：Main
- Workers：4
- Per-task timeout：3600 秒
- Max task attempts：1
- Output：`experiments/python/openhands/deepseek-v4-flash/python200-prime-deepseek-v4-flash-main-r1`

正式启动会调用模型 API 并产生费用，因此必须在明确批准后执行：

```bash
harness/scripts/archive/run_python200_prime_paper.sh \
  openhands_deepseek_v4_flash \
  python200-prime-deepseek-v4-flash-main-r1 \
  --workers 4 \
  --timeout 3600 \
  --execute
```

中断后从同一目录续跑：

```bash
harness/scripts/archive/run_python200_prime_paper.sh \
  openhands_deepseek_v4_flash \
  --workers 4 \
  --timeout 3600 \
  --resume experiments/python/openhands/deepseek-v4-flash/python200-prime-deepseek-v4-flash-main-r1 \
  --execute
```

运行器会在实验目录写入 `run_manifest.json`，绑定冻结 ID、候选 ID、task-set hash、profile、模型、两张镜像和信息条件。完成后会自动执行 suite 分析与 entanglement coverage 报告。

## 6. 论文中当前可以与不可以声称的内容

当前可以声称：Python-200′ 已形成内容寻址、环境固定、200 题三重复 Oracle 全通过且无不稳定任务的评测版本；任务、参考实现、source snapshots、compactness 基线、Hidden 契约处置和最终 Docker 环境均可追溯。

当前还不能声称：DeepSeek V4 Flash 在 Python-200′ 上的正式主表结果。该结果必须来自上述冻结 ID 对应的完整 200 题模型实验；已有 Python-150 或旧 External-50 结果不能直接替代。

主实验完成后，论文的下一项工作是报告总体 Pass@1、Python-150/Hard-50 分层结果、失败类型分布、契约类别关联、项目规模/依赖/耦合因素，以及与已有方法实验的同题配对比较。
