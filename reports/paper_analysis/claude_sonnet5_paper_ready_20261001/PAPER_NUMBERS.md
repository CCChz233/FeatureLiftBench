# Claude Sonnet 5，可直接写入论文的数字

功能通过 = Build ∧ Primary ∧ Extended ∧ Isolation。空提交留在分母里。`run.status` 不作为分数。Token 用 prompt + completion，含缓存输入，表内单位是百万。RRES 和 Copy 只在 89 个成功产物上计算。分位数是论文里的线性插值。

原始逐题表仍在 `reports/paper_analysis/claude_sonnet5_full_source_20260930/` 和 `reports/paper_analysis/claude_sonnet5_paired_20261001/`。

## 排名

按 Full Source 通过数：OSS 36，Qwen 63，GLM 68，Claude 89，Luna 102，Flash 108，Pro 115。

## 主表一行

| Configuration | Pass n (%) | RRES Median [IQR] | Copy Median [IQR] | Steps Median | Steps P90 | Tokens (M) Median | Tokens (M) P90 |
| --- | --- | --- | --- | --- | --- | ---: | ---: |
| Claude Sonnet 5 | 89 (59.3) | 0.92 [0.57, 1.01] | 0.89 [0.53, 0.98] | 32.5 | 79.1 | 1.81 | 4.61 |

成功产物 89。步数和 token 的分母都是 150，且 150 题 token 都已核对。

按构造组：core100 78/100（78.0%），hard50 11/50（22.0%）。

## 结构表，Claude 列

Lift type 互斥。四个机制重叠，一组任务可以同时计入多行。分母与现有表相同。

| Task structure | n | Claude pass | Claude % |
| --- | ---: | ---: | ---: |
| Direct | 56 | 44 | 78.6 |
| Adapted | 76 | 40 | 52.6 |
| Composite | 18 | 5 | 27.8 |
| Code dependencies | 139 | 84 | 60.4 |
| Data and state | 127 | 81 | 63.8 |
| Framework mechanisms | 71 | 38 | 53.5 |
| Environment and resources | 49 | 30 | 61.2 |

## RQ2 配对

Full 89/150，Contract 53/150。都过 40，只 Full 49，只 Contract 13，都不过 48。

Δ = 24.0 pp，95% 配对任务 bootstrap [14.7, 33.3]。仓库聚类区间 [13.5, 34.6]，表内用任务 bootstrap。

两臂评测胶囊摘要不一致的题：0。

Holm 是四个配置一起校正。Luna、Pro、Qwen 的原始 p 不变，校正后的 p 比现在正文里的三配置 Holm 更大。

| Configuration | Only Full | Only Contract | Raw p | Holm p |
| --- | ---: | ---: | ---: | ---: |
| DeepSeek V4 Pro | 88 | 4 | 1.18e-21 | 4.72e-21 |
| Qwen3.6-35B-A3B | 59 | 3 | 1.72e-14 | 5.17e-14 |
| GPT-5.6 Luna | 56 | 8 | 5.56e-10 | 1.11e-09 |
| Claude Sonnet 5 | 49 | 13 | 4.82e-06 | 4.82e-06 |

| Lift | n | Full | Contract | Both | Only Full | Only Contract | Neither |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Direct | 56 | 44 | 21 | 19 | 25 | 2 | 10 |
| Adapted | 76 | 40 | 28 | 18 | 22 | 10 | 26 |
| Composite | 18 | 5 | 4 | 3 | 2 | 1 | 12 |

逐题分类：`paired_claude_150.csv` 的 `pair_class`。

## RQ3 第一失败关和源码暴露

Full Source 第一失败关：通过 89，Primary 39，Extended 20，Build 2。没有缺交，没有 Isolation-first。行为失败 59。

Claude 行为失败中确认读过入口关联源码：46/59（78.0%），首次阅读步数中位 4。

下面是六配置加 Claude 的 1050 行。中位数用确认阅读的那些 run 重算，不是把两组中位数平均。

| Outcome | Runs | Source-exposed | Median first read |
| --- | ---: | --- | ---: |
| Pass | 581 | 424/581 (73.0) | 5 |
| Behavioral failure | 362 | 287/362 (79.3) | 5 |
| No submission or Build-first | 103 | 52/103 (50.5) | 5 |
| Isolation-first | 4 | 4/4 (100.0) | 10.5 |

行为失败因此是 287/362（79.3%）。原来的 241/303 不要再单独当总分母。

## Fig. 7

两块面板样本不同。未纳入的行不要填 0，原因在 `fig07_checkpoints.csv` 的 `exclusion_reason`。

| Panel | Eligible n | Median [IQR] |
| --- | ---: | --- |
| Post-pass tokens (%) | 7 | 62.9 [44.4, 65.8] |
| Subsequent responses | 60 | 10.0 [6.0, 17.2] |

点值：token 用 `include_checkpoint=True` 的 `post_sufficiency_fraction`（乘 100 得到百分数）；回复用 `include_response=True` 的 `post_responses`。

## Fig. 8

成功产物逐题值：`fig08_artifacts.csv`，89 行。失败题没有足迹。

七配置任务固定效应，10,000 次任务聚类 bootstrap，和为零中心。样本 116 题、574 个产物、98 个仓库。这不是原来六配置表上的系数。

| Configuration | Included n | RRES ratio [95% CI] | Copy pp [95% CI] |
| --- | ---: | --- | --- |
| Pro | 113 | 1.195 [1.105, 1.305] | +14.80 [+11.85, +17.80] |
| Flash | 108 | 1.323 [1.221, 1.448] | +16.07 [+13.01, +19.22] |
| Luna | 99 | 0.625 [0.553, 0.701] | -20.92 [-26.34, -15.53] |
| GLM | 68 | 1.574 [1.393, 1.790] | +13.53 [+9.89, +17.27] |
| Qwen | 63 | 1.111 [1.021, 1.226] | -2.53 [-6.79, +1.73] |
| OSS | 35 | 0.617 [0.469, 0.772] | -24.87 [-32.53, -17.66] |
| Claude | 88 | 0.939 [0.858, 1.021] | +3.92 [+0.36, +7.41] |

任务等权和仓库聚类在 `fig08_seven/fig08_seven_results.md`。方向一致。没有不连通的抽样被丢弃。

## 定性 46 例

旧 40 例不动。新增 6 例，助手编码，没有独立人工复核。主题计数：C 2，B 1，其他 3，A 0。没有新的主题类别。

| Case | Task | Theme |
| --- | --- | --- |
| SE041 | sqlalchemy__event_dispatch_core__hard3_001 | C |
| SE042 | wheel__metadata_normalize_core__hard3_001 | C |
| SE043 | isort__settings_resolver_core__hard3_001 | B |
| SE044 | astroid__nodes_core__001 | O |
| SE045 | typer__command_parser_core__001 | O |
| SE046 | jupyter_server__extension_config_core__hard3_001 | O |

选择规则和依据在 `qualitative_claude_6.csv`。
