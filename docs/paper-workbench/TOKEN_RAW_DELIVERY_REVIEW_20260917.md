# 原始 token 交付物复核：可以继续整合，恢复摘要需纠正

复核对象：`experiments/token实验/token_efficiency_raw_20260917T072646Z/`。
本地复核日期：2026-09-17。未重跑模型或 Docker，未编译论文，未覆盖服务器原包或正式论文图表。

## 结论

**原始材料可接收，足以继续本地恢复和改图。服务器关于 Luna/GLM token 不可恢复、Qwen 无稳定 ID 的结论不完整。**原始 audit 缺 usage/ID 不等于所有持久化来源都缺。

原运行 `agent/openhands_persistence/conversations/<id>/base_state.json` 中的
`stats.usage_to_metrics.<role>.token_usages` 保存了逐响应 prompt/completion token 和 response_id；角色包含 agent 和 condenser。许多 Luna/GLM 原运行也存在这些记录。它们是历史持久化记录，不是用总 token、步数或 probe 估算。

Qwen 的原对齐只枚举 ActionEvent/MessageEvent，漏掉 Condensation 响应；调用数和响应数因此部分不一致。另一些运行还有 usage 中存在但事件流未出现的 response ID，仍应保留为未完全对齐，不能全部纳入。

## 独立完成的检查

- 七个压缩包 SHA256 与交付清单一致，gzip 全流读取至 EOF，全部 tar 成员可读取。
- 六个原始包与 165,341 条文件索引逐项核对；常规文件逐字节长度和 SHA256 一致，12 个链接成员只检查路径，不跟随执行。无索引缺失文件。分析包另以整体 SHA256 和完整读取校验。
- 900 个 run_id 与正式 150×6 结果清单一一对应，成功数保持 115/108/102/68/63/36。
- 从原始事件独立复算 900 条 total_unique_responses，并对全部 403 个纳入样本复核首次通过快照、原始 observation event ID、快照已知评测、最终匹配标记和后续响应计数；与交付 CSV 一致。
- 逐运行读取持久化 token_usages，核对与 accumulated_token_usage 的累加关系；进一步检查 response ID 唯一和双向完整覆盖，包含 Condensation。
- 对下面 token 候选集要求：已纳入上述重建产物分析；一个持久化会话；token_usages 完整映射全部响应；与 audit 调用数一一对应；响应事件紧随对应 audit 完成时间（0–2 秒，audit 为秒精度）；audit 状态 200；token 非负且每调用总量正；audit 中已知的逐调用 token 与持久化值一致。
- token 计算 prompt+completion，cache-read 已含在 prompt，不重复相加；边界以前产生该产物的响应不算后续调用。这里只核验历史记录，不将 SDK 存储值称为新的 provider 独立审计。

## 本地严格复核得到的候选结果

下表是用于下一步整合的本地复算结果，尚未替换正式 Fig.4、Table 3 或其输入文件。两 panel 分母独立。token 样本要求包含压缩调用的完整账本；响应指标仅计 ActionEvent/MessageEvent 中新的模型响应，**不称为完整 HTTP 请求次数**。

| 配置 | 正式成功 n | token 时间线可用 n | 后续 token 占比中位数 | 后续响应样本 n | 后续响应数中位数 |
|---|---:|---:|---:|---:|---:|
| Pro | 115 | 98 | 66.9% | 102 | 20.5 |
| Flash | 108 | 93 | 73.0% | 96 | 32.5 |
| Luna | 102 | 43 | 58.1% | 75 | 11 |
| GLM | 68 | 27 | 67.1% | 46 | 39.5 |
| Qwen | 63 | 25 | 53.7% | 50 | 17.5 |
| OSS | 36 | 31 | 37.1% | 34 | 5 |

token 共 317 条；响应共 403 条。Luna/GLM 不必再显示为无数据；Qwen 也不局限于 5 条。各配置样本任务不同，不从这些中位数推出控制任务后的效率排名。

## 对交付物的判断与剩余工作

| 检查对象 | 判断 | 下一步 |
|---|---|---|
| 原始材料完整性与正式运行范围 | 已通过本地文件与清单核对 | 可使用，无需仅为此次缺失再索要同一批日志 |
| 后续模型响应结果 | 403 个纳入样本独立复算一致 | 以独立分母更新右 panel，名称改为 responses |
| 服务器 token 恢复结论 | 需纠正：遗漏持久化逐调用 token 与压缩响应 | 本地加入持久化用量读取和稳定 ID 对齐，不沿用 audit-only 不可恢复判断 |
| 完整重建与离线评测 | 复用现有快照，不是新一次 Docker 复验 | 继续用“首次观察到的重建通过版本”；不声称最早瞬时状态或全量回放已重新证明 |
| 正式图表及 LaTeX | 尚未更新本轮恢复结果 | 同时更新方法、图、表、分母、caption 和检查，不能只改图中 n |

Table 3 的 Luna/GLM outcome token 分布也需要重新核查：完整总用量可用性与精确时间线是不同条件。不能直接用上表 token PSF 样本替代成功/失败用量表的分母。原 Table 1 作者确认的汇总不在本次修改范围。

本轮支持的故事是：在可恢复且最终成功的运行中，首次观察到通过版本之后仍有后续响应和 token 消耗。后续验证并不自动等于浪费；比例也不等同于可节省费用或计算量。

## 可复算证据

位于 `reports/paper_analysis/token_raw_review_20260917/`：

- `verify_archives.py` / `archive_checks.json`：原始包与文件索引核对，并只解出待检查数据到 `/tmp/flb_raw_review_072646/`。
- `verify_results.py` / `result_checks.json`：官方结果与响应指标独立核对，另记录 Condensation 和持久化事件完整性。
- `check_persistence_usage.py` / `persistence_usage_checks.json`：持久化逐响应 usage 覆盖、ID 与累计总量。
- `strict_candidates.py` / `strict_persistence_candidates.json`：上述严格候选的逐运行纳入理由及汇总。

运行顺序同上，Python 3.12；不执行交付包内脚本或历史工具命令。这些检查文件是本地复核材料，正式论文生成入口仍待统一更新。

## 正式整合状态

原始恢复结果现已纳入 `execution_effort_recovered.v2`，Fig.4、Table 3、方法和 RQ2 正文已同步。上面的“尚未替换”描述记录复核当时状态。Table 3 进一步按 response ID 对父子状态重复用量去重，最终纳入 764 条总量完整的记录（Luna 成功/失败 86/38，GLM 40/10）；图的 317/403 条样本与本次复核相符。
