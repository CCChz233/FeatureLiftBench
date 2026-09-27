# 过程诊断准备与当前论文修改

只计划两项：S 为已有 900 条主运行的离线 source-exposure 诊断；A 为已有 40 题 × 三配置新增 Hint 第三臂，共 120 条正式运行。执行规格见 `../experiments/SOURCE_EXPOSURE_HINT_RUNBOOK.md`。

## 当前已做

- 新增只读预检脚本，生成 private annotation inventory 和 900 行原运行索引；未运行模型或 evaluator。
- 本地观察到 150 题入口声明，900 个非空事件文件，107 题非空 required_source_files，39 个 closure_gold 文件。入口解析正确性、轨迹完整性、真正源码暴露均尚未分析；107 不能改写成此前建议中的 124。
- 保留作者复核 150 题和 450/450 reference replay；删除 Threats 的 future independent audit 承诺，没有升级成已完成独立审核。
- RQ3 改为 performance variation；摘要和引言区分 76/77 的定量门控结果与 inspected artifacts 的定性 contract-closure 现象。
- §5 小节改为 illustrative mechanisms，保留两个任务四个产物，不宣称代表性原因分布。
- 额外 50 题未来扩展缩成一句；固定 150 集合不附加未经证明的历史 preregistration 时间顺序。
- 新过程诊断和 Hint 结果只加入 LaTeX 注释，尚未写成已完成实验，也没有预测数据表。现有 Fig.5 仍为实测两臂。

## 服务器侧尚需完成

1. 核对入口符号到文件/定义范围的映射；验证能区分检索、文件名命中、源码返回和未成功工具调用的轨迹解析器。
2. 完成 900 条运行的 observable exposure 分析及子集报告，保留 unknown 和独立 Isolation-first 类别。
3. 在前一轮 Full runner 上实现/核对仅 symbol+file 的 Hint allowlist 注入；现有 --agent-source-hints 不自动满足该严格协议。
4. 按同题同配置跑 120 条 Hint，保留原始轨迹/失败/恢复记录，分析 Hint vs Full 的配对结果。

原始 benchmark 与运行记录未改动；未编译或渲染论文。新的全文与 Overleaf 包在本轮静态检查后更新。
