# Related Work 更新与来源核对

> **Status: archived · Historical paper record**

保留 §7.1–7.4 结构，新增四篇引用；Table 5 仅新增 RepoZero 一行，并同步保存的表格片段。未改实验、统计值或其他图表。

- §7.1：NL2Repo-Bench 的空工作区与需求驱动 Python library construction；RepoZero 的 API specification 驱动、禁止读取原库实现的 black-box reproduction。合并重复定位段，突出完整 donor 在构建阶段可见、目标 package 在评测阶段脱离 donor 的边界。
- §7.3：SWE Refactor Bench 的 migration completeness 与 behavioral correctness 分别验证；保留原 SWE-Refactor 引用，明确两者不是同一工作。Feature lifting 不要求特定迁移、结构对应或最小抽取。
- §7.4：BeyondSWE/SearchSWE 的搜索收益有限且不均，以及外部信息与本地实现、版本约束整合的问题；连接源码消融与确认读取后的失败分析。

## 原始来源

- [NL2Repo-Bench v2](https://arxiv.org/abs/2512.12730v2)：2025-12 首发、2026-01-08 修订；本次按所引用修订版记为 2026，并在 BibTeX 注明版本。作者列表依据 arXiv 当前元数据。
- [RepoZero v3](https://arxiv.org/html/2605.07122v3)：摘要与 §2 定义 black-box reproduction；Appendix C 明确禁止读取 Python/C++ library source。这里的“不可见”指原库实现，不是禁止提供 API 调用驱动代码或行为示例。作者列表依据 arXiv v3 元数据。
- [SWE Refactor Bench v1](https://arxiv.org/abs/2608.23564v1)：2026-08-24；Migration Audit 验证迁移发生，行为检查承担另一层验证。
- [BeyondSWE v2](https://arxiv.org/abs/2603.03194v2)：2026-05-26 修订；摘要说明收益 limited and uneven，强调 precise、version-compatible、locally actionable changes。另核对 [v1 Appendix D](https://arxiv.org/html/2603.03194v1#A4) 的信息整合与版本约束案例。

四篇均按 arXiv 预印本引用，不推定会议接收信息。Table 5 不添加 note；解释保留在正文。

## 验证

静态引用检查通过（29 个引用键）；正文编译为 22 页，References 从第 21 页开始。无 overfull 或未解析引用。目视检查 Table 5、§7.3–7.4 及新增参考文献，未见裁切或重叠。Overleaf 包已更新。

## 后续复核

作者再次确认保留 Pro 7/40、12 次未交付，只修措辞。Results、Fig.4 辅助描述和 Threats 删除未交付源于长上下文执行的归因，改为行为重建与成功交付的混合效应；分数、CI、p 值不变。RepoZero 官方 v1 是 5 位作者，v3 是 10 位作者；本论文明确引用 v3，保留与该版本官方元数据一致的 10 人列表。修订后编译与静态检查通过，PDF 与 Overleaf 包已更新。

## 提交前引用清理

按作者要求统一引用 RepoZero v1：Zhaoxi Zhang、Yiming Xu、Weikang Li、Jiahui Liang、Yunfang Wu；链接与版本注记同步改为 v1 / May 8, 2026，覆盖上文此前的 v3 选择。正文 4 处 Supplement/S1/S2 指向改为 replication materials；当前不提交独立 Supplement，相关本地工作文件从 Overleaf 包清单移除但不删除。
