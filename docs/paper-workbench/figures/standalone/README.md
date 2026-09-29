# 当前论文：逐图独立脚本

> **Status: current · Last verified: 2026-09-29**

一张图一个 `.py` 文件，脚本之间互不导入，所需数值已写入各自文件。这里只用于**当前正文**的单图样式调整；Fig. 4(a–c) 是正文所用的 **40 题**版本。修改实验数值时，应先检查 [可复算流程](../scripts/README.md) 和 [论文输入清单](../../paper_sources.json)，不要只改图中的常量。

```bash
python -m pip install numpy==1.26.4 matplotlib==3.9.2
python docs/paper-workbench/figures/standalone/fig04a_ablation_pass_rate.py --output-dir /tmp/flb-figure-preview
```

输出是同名 PDF/PNG，**不会自动替换** [正式图片](../../../paper/figures/)；先检查，再更新正式图片和正文引用。Fig. 6 是手工编辑 PNG，没有逐元素 Python 绘图源码；其脚本只是导出内嵌定稿图。Fig. 1/2 也没有对应的 Python 绘图源码。

此前在这个目录修改的 **150 题 RQ2** Fig. 4(a–d) 与组合试画已原样移至 [草稿目录](../drafts/rq2_150/README.md)，本目录的 Fig. 4(a–c) 已恢复为当前 40 题正文版。草稿没有自动进入论文。
