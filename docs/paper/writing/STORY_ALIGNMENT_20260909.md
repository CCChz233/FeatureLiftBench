# 论文故事与冻结结果对齐

## 当前决定

- 保留 200 题 release、六配置共同 150 题主比较、五配置额外 50 题。
- 作者最新确认已完成全部 benchmark 复核；停止七题核对，并按用户要求删除论文中相应讨论和敏感性分析。原始证据文件保留。
- 图 1 不替换、不重画；图 2/5 原图保留。A/B 仅同步分类说明与 Public/Hidden 标签。

## 已修改

1. 综合 Table 1 恢复 Pass@1、RRES/Copy 的 mean/median/IQR、Steps/Tokens 的 median/P90。拆为同一表的两个面板，数据口径在表下注明。删除被主表完全覆盖的旧附录 footprint 表。
2. RQ3 改为 Difficulty across tasks：solve frequency → 50 题构建 cohort 的表现 → 控制分析 → lift type 是描述性结构。没有重新引入 Core/Hard 作为 benchmark 产品划分。
3. 全六配置模型：Composite OR=0.655，p=0.485843。Pro/Flash/Luna：OR=0.653649，p=0.553526（正文四舍五入 0.654 / 0.554）。两者不能混称一个分析。指标以 controlled_difficulty_evidence.json 原值为准。
4. Abstract/Introduction 突出 contract-closure gap 和共同成功产物差异；不把“访问仓库”升级成“完全解决代码定位”。
5. 正文与统计图恢复 Public/Hidden，首次说明两组均不向智能体开放。图 1 原图按指示保留，其旧阶段标签未在这轮重绘。
6. 人工验证从“约半数抽检”更新为作者确认的全量任务复核；不补造 reviewer 数量、agreement 指标或逐次改动后重跑记录。
7. Figure 1 案例介绍改为 Signal/Namespace 与 supporting dispatch logic。ANY 仍是实际公开契约的一项 sentinel，正文以括号说明，未改 benchmark API。

## 镜像核查的实际结论

900 条运行使用同一 agent/evaluator ID 对。Release/oracle 使用另一对 Id；三个 producer 均读取 Docker image Id，不支持 manifest/config 字段名差异解释。Oracle summary 中 Python 3.12.2 是 host sys.version；冻结中的 Python 3.11.14 来自容器内查询。此解释不等于解决镜像内容差异。

本机 docker image ls 无法连接 Docker Desktop Linux engine；在本地证据目录未找到两组镜像的 inspect/RootFS 记录。没有启动 Docker、运行容器或重跑实验。要验证内容等价，需要原运行主机保存的四个 ID 对应的 image inspect（RootFS.Layers、Config、Created、Architecture）和必要的依赖清单。当前论文据此明确限定 oracle 与 campaign 环境的一致性主张。

## 数据与文件

- 综合主表：writing/comprehensive_table.py，由 update_tables.py 调用。
- 分类表：writing/update_structure_results.py，移到附录。
- 冻结控制模型：writing/controlled_difficulty_evidence.json。
- 镜像核对：writing/image_identity_reconciliation_20260909.json。
- 论文和五图的上传目录统一 figures/，更新 featureliftbench_overleaf.zip。

本轮不编译、渲染论文，不运行 agent 或 reference 实验。校验现有结果表、引用和图片路径；检查 A/B PNG。
