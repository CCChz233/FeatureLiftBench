# 论文图形工作区

最新 PDF 的 Fig. 3–8 与源码、输出文件的逐项对应关系见 [scripts/README.md](scripts/README.md)。Fig. 1、Fig. 2 为 PPT 图片。

`scripts/draw_all.py` 默认把所有预览写入 `output/latest_pdf/`，不会改动 `docs/paper/figures/` 中的正式图片。`data/` 保存派生数据和历史分析产物；`scripts/legacy/` 保存旧版绘图方案。Fig. 6 的正式图是 PNG 资产，`scripts/fig06_qualitative_cases.py` 只负责原样导出预览。

```bash
python -B docs/paper-workbench/figures/scripts/draw_all.py --list
python -B docs/paper-workbench/figures/scripts/draw_all.py
```
