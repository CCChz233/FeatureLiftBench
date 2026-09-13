# 论文代码与数据工作流

> **Status: current · Last verified: 2026-09-11**

最终 benchmark 为 200 题、176 个仓库、182 个快照；主比较为相同 150 题上的六配置结果，扩展为五配置的其余 50 题。

## 唯一入口

[paper_sources.json](paper_sources.json) 登记输入、模型 ID / 全名 / 顺序、运行目录与 Overleaf 清单。[paper_inputs.py](paper_inputs.py) 统一读取配置。它们选择现有最终材料，不复制或重命名题包与原始结果。

```text
200 题身份记录与索引 + 150 × 6 逐题结果 + 五配置扩展结果
                          │
                paper_sources.json
                          │
             表格脚本 / 分类统计 / 绘图数据
                          │
        main.tex + references.bib + figures/
                          │
           featureliftbench_overleaf.zip
```

## 日常命令

从项目根目录执行：

| 命令 | 作用 |
| --- | --- |
| `python -B scripts/paper.py check` | 只读核对范围、900 条结果、配置与当前表格 |
| `python -B scripts/paper.py tables` | 更新生成表格和两段数值文字，保留其他正文 |
| `python -B scripts/paper.py figures` | 生成 Fig. 3–5 数据与 PNG/PDF；不修改定稿 Fig. 1/2 |
| `python -B scripts/paper.py package` | 先检查，再打包正文、bib、模板与五图 |

绘图需安装 NumPy / Matplotlib，本机可用 `D:/Anaconda3/python.exe`。这些命令不启动 agent、不执行任务、不编译 LaTeX。`check` 核对输入与数值关系，不声称重新进行了任务语义或环境等价性审核；绘图后仍需目视检查。

## 文件职责

| 类别 | 当前文件 |
| --- | --- |
| 正文与文献 | `main.tex`、`references.bib` |
| 主比较 | 清单中的 `main_results`，900 条 model–task 结果 |
| 扩展评测 | 清单中五配置 `run_directory` 下的 `eval/result.json` |
| 配对统计与交叉检查 | `paired_statistics`、`main_summary` |
| 任务组成 | `task_inventory`、`lift_taxonomy`、`mechanism_taxonomy` |
| 五张数据表、两段数值文字 | `writing/update_tables.py` |
| 附录分类结果表 | `writing/update_structure_results.py` |
| Fig. 3–5 数据 / 绘制 | `figures/scripts/redraw_data.py` / `redraw_figures.py` |
| 图形样式 | `figures/scripts/paper_style.py`，模型名称来自公共清单 |

Fig. 3 左侧覆盖全部 200 题，右侧使用有一致归一化机制字段的共同 150 题。字段覆盖范围不改变 benchmark 总数。

## 历史材料与后续整理

旧目录继续作为存储路径使用，不能据目录中的 `final`、`v2` 或日期自动选择来源；以清单指定文件为准。

旧组装器、历史敏感性分析、版本与镜像核对报告保留，但不参与日常表格生成。任务集合、唯一性、functional gates、配置、分母与配对统计检查继续保留。历史字段不被擦除，也不自动成为论文中的新 benchmark 名称或当前问题声明。

整理前的入口文档见 [快照目录](../archive/snapshots/paper_workflow_20260911/README.md)。本轮没有移动题包、原始运行、轨迹、freeze 或定稿图片。

后续先完成论文写作，并同步清理正文中不必要的开发历史；保留实际协议与复现信息。如需对外发布代码，再单独整理安装、源码获取和运行示例，当前写作不依赖全面重构 harness。
