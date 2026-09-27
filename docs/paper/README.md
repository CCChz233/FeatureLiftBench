# FeatureLiftBench 论文

这里是唯一的正式写作目录，结构与 Overleaf 项目一致。

```text
paper/
├── main.tex                       # 正文：日常修改入口
├── references.bib                 # 参考文献
├── figures/                       # 正文使用的 12 个图片文件（8 张图）
├── acmart.cls                     # ACM 模板
├── ACM-Reference-Format.bst        # ACM 参考文献样式
├── acm-jdslogo.png                # 模板资源
├── LICENSE                        # 模板许可证
├── main.pdf                       # 最新本地编译结果
└── featureliftbench_overleaf.zip   # 可直接上传 Overleaf
```

在 Overleaf 中上传 ZIP，主文件选择 `main.tex`，编译器使用 pdfLaTeX。

从仓库根目录执行：

```bash
python -B scripts/paper.py build    # 编译并更新这里的 main.pdf
python -B scripts/paper.py package  # 检查后更新 Overleaf ZIP
```

当前 `main.tex` 以 2026-09-26 用户提供的论文包为基础，并按 2026-09-27 全文审阅结果修订。Overleaf ZIP 只包含正文实际引用的图片，不包含原包的 3 个未引用旧图。正文表格直接写在 `main.tex` 中；旧版主表生成标记已不存在，`scripts/paper.py check` 会检查数据范围、图片、引用及仍适用的分析输入，但不会将旧版主表生成器用于这份正文。

Benchmark 构建证据另见 [匿名构建证据包](../paper-workbench/replication/anonymous_construction_evidence.zip) 与 [说明](../paper-workbench/replication/CONSTRUCTION_EVIDENCE_README.md)。Fig. 2 现在由正文 LaTeX 排版为 Blinker 证据链实例，不再使用旧的 `fig02_construction.png`，因为旧图中的完整人工审阅与筛选流程说法缺少逐题历史记录。

分析脚本、数据、历史 PDF、检查记录与草稿全部在相邻的 [paper-workbench](../paper-workbench/README.md)。[Fig. 3–8 绘图索引](../paper-workbench/figures/scripts/README.md) 按用户提供的最新 PDF 图号列出源码和预览输出。本目录不提交独立 Supplement。

不要在 workbench 建立第二份正文：其中的正式源文件入口是指向这里的相对符号链接，脚本更新和手工编辑作用于同一份文件。Overleaf ZIP 里是实际文件，不含这些链接或工作记录。
