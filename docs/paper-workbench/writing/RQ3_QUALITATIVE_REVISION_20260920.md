# RQ3 定性分析修订（2026-09-20）

按作者指令，RQ3 改为 **How Can Behavioral Preservation Fail After Relevant Source Has Been Observed?**。

- 保留 Fig.5、Table 3 和 RQ4；与修改前源码逐字节比较一致。Table 3 仍是 241/303（79.5%）。
- 删除 303 → 241 → 228 → 201 → 176 的分类流，以及 176/68、69.3% 和各属性频率。摘要、方法、结果、讨论、Threats 和结论已同步。
- §3.5 使用 purposively diverse 40-case sample。选择来自既有候选池，以不同任务、固定配置配额和功能族/lift type/旧复核状态覆盖为准，hash 仅用于破同分；不称随机或代表性样本。
- 选样清单核实为 40 个不同任务、六配置、十功能族；30 development + 10 rule-check。逐条与 run_exposure.csv 连接，40 条均为 confirmed explicit source read 且 Primary/Extended 首败。
- 双人独立复核按现有作者确认的 A/B 范围描述；不新增或改写人工标注，不把定性样本当 prevalence 估计。
- Fig.6 保留三组目的性成功/失败对照，以矢量机制图呈现；移除属性构成图和 codebook 表。旧证据文件保留，不参与正文统计、默认绘图及正式图片打包。
- 生成器、静态检查、资源清单和当前工作说明已同步；后续 tables 不会重新插入 taxonomy 表。

## 验证

`paper.py check`、`paper.py tables`、`check_final_latex.py`、`paper.py package` 均成功；latexmk 编译成功，无未解析引用或 overfull。保留一条 underfull vbox 提示。
当前 PDF 共 21 页，结论及参考文献起始位于第 20 页；本轮仅完成定性口径修改，未做全文压缩。
渲染检查第 13–14 页，Fig.5、Table 3、新 Fig.6 与定性案例可读。

此次删除定量分类分母并不构成对历史评测疑点的新裁决；冻结任务、分数、旧台账不变。

## 未变正文块 SHA-256

- fig5: `49a9c9017345a3cffd3f2fccd9b50cf0f9d7b902258357a3e36ee1b7863080f4`
- table3: `c7777d3c54622432008a8d8672dd412c41101963e65494d9ff790f30e4f65fc7`
- rq4: `6eb990058a08bc3a7eb7982c27589a7e67dd314b1dc1fadc35cf95bba919dc3d`

## 机制图与全样本映射补充

- 逐条复核 40 条现有台账及证据，新增轻量 case→theme 映射：ambient assumptions 3 条、supporting representations/pipelines 2 条、destination-specific adaptation 4 条，其余 31 条保留 Other/case-specific。计数仅描述本目的性样本，只放补充材料。
- 新映射为 assistant evidence synthesis，不冒充新增双人人工主题标注；原作者复核记录保留。
- 方法使用 source-exposed Primary/Extended-first 的客观描述，保留部分 API member 缺失的限定；真实历史选样过程在补充材料交代，不包装成随机抽样。
- 正文以全样本观察连接 recurring themes 和三组配对案例。图6重画为矢量图，生成器支持隔离预览。
- 最终正文 21 页、补充材料 4 页；已目视核对图6及补充映射跨页排版，编译与静态检查通过，Overleaf 包已更新。
