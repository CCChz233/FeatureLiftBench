# Plan: External-50 一天合同升格

> **Documentation status: reference · Created: 2026-08-26 · Last verified: 2026-08-29**  
> **执行日：2026-08-27。合同升格已完成**（见文末进度）。不是当前跑分入口。  
> 剩余 copy-all / 独立 freeze 仍按本文，且 **不并进 Python-150、不进 Python-200' 主表**。  
> 扩题已结束：[archive/plans/PLAN_EXTERNAL50_EXPANSION.md](archive/plans/PLAN_EXTERNAL50_EXPANSION.md)  
> 难度对齐的新 50 题不改本 split，见 [PLAN_HARD50_EXPANSION.md](PLAN_HARD50_EXPANSION.md)。

## 当天完成定义

只动 `benchmark/external50/`。不改 Python-150，不重跑模型，不换 20 个仓。

日落必须同时成立：

1. **50/50** `validate-task` 绿。
2. **0** 条 *“The extracted feature must support this observable behavior”* 模板句。
3. 每个 `required_api` 函数/方法有 `signature`（类/异常/模块可没有）。
4. Hidden/public 不再引用未声明 API；过严的 `match=` / JSON 空格 / `__all__` 黑名单：补进 spec 或删掉。
5. `TASK.md` 全由 `public_spec` 生成，hash 已同步。
6. 落盘 `reports/audits/external50_day_20260827/`：`inventory.json`、`replace_later.json`（只点名，不换题）。

**当天不做：** 换 backup 仓、copy-all 基线、新 freeze、Flash 重跑。这三项未做完之前，`STATUS.md` 里 90%–94% 继续当旧合同数字，标 stale 即可。

已改过、跳过重写：`joserfc` / `omegaconf` / `pyparsing`（仍要进 50/50 validate）。

## 为什么一天够

仓和测试已经在。工作量是 **40 道模板 spec + 24 道补签名 + Hidden 对齐**，用脚本批量 render/hash/validate，人工只写行为句子和 API 签名。不要分五波、不要先做样板再排期。

## 日程

| 时段 | 做什么 | 截止 |
| --- | --- | --- |
| 09:00–10:00 | 脚本扫 50 题：模板句、缺签名、`validate-task` 现错。写出 `inventory.json` | 表在 |
| 10:00–18:00 | **47 道**（50−3 已修）逐题改 `metadata.json` + Hidden；每 10 题跑一轮 validate | 50/50 绿 |
| 18:00–19:00 | 扫一遍剩余 `match=` / 未声明 API；写 `replace_later.json`；勾本页进度 | 目录交卷 |

卡住就放宽 Hidden 或补一句 spec，**不要**新写一整库 reference，**不要**停下来换题。

## 单题 10 分钟流程

目录：`benchmark/external50/<task_id>/`

1. 读 Hidden + `required_api`，缺的签名从测试调用补。
2. 把模板 B00x 改成一句可观察结果（谁、什么输入、看见什么）。
3. Hidden 用了未声明成员 → 写入 `required_api`；精确字符串无出处 → 删 `match=`。
4. 同步 `evaluation_spec` 条款文本。
5. render + hash + `validate-task --json`。

```bash
PYTHONPATH=harness python3 -B -m featureliftbench.cli render-task \
  benchmark/external50/<task_id> --write
PYTHONPATH=harness python3 -B -m featureliftbench.cli validate-task \
  benchmark/external50/<task_id> --json
```

`sync_spec_hashes` + `_sync_behavior_contract` 与 2026-08-26 修补同一套。禁止手写 `TASK.md`。

优先顺序（先易后难，仍当天全做）：Direct 小库 → parse/validate → 其余 Composite。Direct 名单：`semver`、`pyotp`、`ftfy`、`portalocker`、`fasteners`、`toolz`、`more_itertools`、`cacheout`、`stamina`、`pyrsistent`、`publicsuffixlist`、`puremagic`。

## 禁止

- 改 `benchmark/tasks/`
- 为压分加 Hidden
- 当天更新主表通过率
- 为配额改 `lift_type` 而不换题（换题不在当天）
- 把 AI 审计当 gold

## 规范

[TASK_DESIGN_RULES.md](TASK_DESIGN_RULES.md) · [HIDDEN_CONTRACT_PROVENANCE.md](HIDDEN_CONTRACT_PROVENANCE.md) · [07_incremental_task_rules.md](reference/07_incremental_task_rules.md)

## 进度

- [x] inventory.json
- [x] 50/50 validate-task 绿、无模板句、函数有签名
- [x] replace_later.json（仅名单）
- [x] 未改 Python-150，未改 STATUS 通过率
