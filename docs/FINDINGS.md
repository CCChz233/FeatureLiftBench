# 当前论文发现与历史方法边界

> **Status: current · Last verified: 2026-09-14**

本页仅概括当前 150 题论文。历史方法结论与旧数据未删除，整理前版本保存在
[本轮快照](archive/snapshots/fse_sync_20260914/README.md) 的 `before.zip`。
正式数值以 [paper_sources.json](paper/paper_sources.json) 和正文为准。

1. 六配置的 Functional Pass@1 为 24.0%–76.7%，尚未全部解决这组任务。点估计不建立每一对配置的显著排序。
2. Pro/Flash 均交付产物，77 次合计失败中 76 次首败位于行为门；首败阶段是可观察边界，不是语义根因。
3. 40 题源码消融中，Luna 从 9/40 提高到 23/40，Qwen 从 1/40 提高到 12/40；Pro 的增益需结合 18 次 Contract-only timeout 解释。
4. 303 次行为首败中，241 次有入口关联源文件内容返回证据。文件内容暴露不证明已完整定位或理解功能。
5. 同题通过的产物仍存在大小与直接源码重合差异。正确性与提取特征应分别报告，复制率不是质量总分。

历史 V1、closure、repo graph、Public-feedback、其他 runtime 与 AutoSaddler 的数据属于不同实验条件，不能写成当前论文的方法效果。
