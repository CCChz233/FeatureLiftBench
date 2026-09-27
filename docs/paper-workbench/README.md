# 论文分析与历史工作区

正式论文只在 [../paper/](../paper/README.md) 编辑。这里保存数据、生成器和历史材料，不作为 Overleaf 上传目录。

正文精简时移出的 footprint 重采样细节与原描述统计保存在
[FOOTPRINT_ANALYSIS_DETAILS.md](writing/FOOTPRINT_ANALYSIS_DETAILS.md)，供复现材料使用。
执行延续分析从正文移出的各配置中位数见
[EXECUTION_ANALYSIS_DETAILS.md](writing/EXECUTION_ANALYSIS_DETAILS.md)。

| 目录/文件 | 用途 |
|---|---|
| `paper_sources.json` | 当前论文选用的数据与正式文件清单 |
| `paper_inputs.py` | 共享输入与一致性检查 |
| `data/` | 选定分析数据 |
| `writing/` | 表格生成器、复核记录、写作计划与历史说明 |
| `figures/scripts/` | 绘图脚本 |
| `figures/data/`、`figures/output/` | 绘图中间结果与预览 |
| `experiments/` | 实验配置与历史方案 |
| `output/` | 历史 PDF 等交付快照 |
| `build/current/` | 当前论文编译中间文件，不上传 |
| `supplementary.tex`、`qualitative_mapping.tex` | 本地历史材料，不作为独立 Supplement 提交 |

本目录中的 `main.tex`、`references.bib`、模板和正式图片是指向 `../paper/` 的相对符号链接，确保只有一份可编辑源文件。不要用副本覆盖这些链接。

仓库根目录命令：

```bash
python -B scripts/paper.py check
python -B scripts/paper.py tables
python -B scripts/paper.py figures
python -B scripts/paper.py build
python -B scripts/paper.py package
```

`tables` 更新正式正文中的生成数据块；`figures` 生成 [Fig. 3–8 预览](figures/scripts/README.md)，不会覆盖正式图片。`build` 更新 `docs/paper/main.pdf`；`package` 生成 `docs/paper/featureliftbench_overleaf.zip`。这些命令不运行 benchmark 实验。

旧记录中的路径反映记录当时的布局。原先 `docs/paper/` 下的分析文件现位于 `docs/paper-workbench/`；正式论文文件继续位于 `docs/paper/`。迁移前源文件哈希见 `writing/FOLDER_REORGANIZATION_20260921.json`。
