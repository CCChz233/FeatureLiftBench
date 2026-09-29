# Pro ablation 最终保留结果

> **Status: archived · Historical paper record**

本记录覆盖此前同日的 Pro 数值口径；正文只描述本次 ablation 的保留结果。

- 数据：240 个 arm outcomes、120 个配对行，三配置各 40 个相同任务；逐行核对配对 0/1 值与 task outcomes 一致。
- 统计脚本：`recompute_retained_ablation.py`；paired task bootstrap 100,000 次，seed 20260913，百分位 95% CI。精确双侧条件 McNemar 检验，三配置统一 Holm 校正。
- Pro：Full Source 25/40，Contract Only 6/40，18 次未交付；both=5，Full-only=20，Contract-only=1，neither=14。
- 差值 47.5 pp，CI [30.0, 65.0] pp；原始 p=2.09808349609375e-5，Holm p=6.29425048828125e-5。
- Luna、Qwen 的主要配对统计不变。主实验、源码读取分析、Fig.3 和 Table 1 不变。
- 方法中的未交付计作失败与 Threats 中行为重建/成功交付的解释保持不变。正文与补充材料不增加其他运行记录分析。
- manifest、表格生成器、图形数据检查、静态校验和保存的表格片段同步更新，避免下次生成恢复旧值。

验证：完整数据/表格检查通过；Fig.4 绘图时再次逐对重算并核对 bootstrap CI。正文编译为 22 页，无 overfull 或未解析引用，目视检查 Table 3 与 Fig.4 正常。PDF 文本不含作者指定禁用词；Luna/Qwen 的主要统计与前版一致。Overleaf 包已更新。
