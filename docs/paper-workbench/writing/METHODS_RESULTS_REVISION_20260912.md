# 方法、流程图与实验解释修订

> **Status: current · Last verified: 2026-09-12**

本次修改依据现有 main.tex、任务格式、reference registry、构造脚本以及已保存主实验表格。没有启动实验，也没有编译或渲染整篇论文。

## 修改内容

1. 第二章以 200 个任务的输入、交付与评测组成开篇，集中区分 agent 可见材料和维护者私有资产。
2. 构建部分补充契约如何限定复用边界，以及 reference 的源码复制、导入改写、任务专用适配和保存实现等构建途径。用既有 signal-registry 例子连接行为义务、实现和评测，不声称所有 reference 都由同一个脚本生成。
3. 验证部分区分自动结构检查、AI 辅助证据、作者语义判断和 reference 重放。38 题/6 次的修复记录移到附录。明确 reference 通过不单独证明测试公平或完整。
4. 分类部分先说明功能类别、提取类型、缠绕机制三个轴，再解释实验覆盖。任务和分类计数不变。
5. RQ2 增加 OSS 与 GLM/Qwen 的失败分布差别；RQ3 小标题避免暗示构建批次的因果解释；RQ4 末增加六配置综合观察和效率解释。
6. 主表 Steps 标为 Recorded assistant steps，并明确日志交互计数与配置 action budget 的区别；同步修改生成器，数值不变。
7. Fig. 2 保留原有双带与 release 构图，更新 Source-independent reference 和 Retain validated tasks，修正 AI 编辑产生的黑背景为白背景。
8. 表格检查支持上一轮已加入的明确标记假设表；它单独登记为 unverified_hypothetical_tables，不参与实测数值核对，也不写入原主实验数据。

## 依据与解释范围

- 主结果与配置来源仍为 [paper_sources.json](../paper_sources.json)。
- reference 的既有 registry：`benchmark/references/python200_prime_compactness.json`。
- 参考构建工具：`harness/scripts/build_oracle_submission.py` 的 manifest 复制、import rewrite、任务适配分支；这些操作存在，不代表所有任务或某位作者都使用了相同路径。
- 任务可见性：`docs/reference/06_task_schema.md`；行为边界以公开契约为准。
- OSS：2 个 missing、18 个 Build-first、70 个 Public-first、23 个 Hidden-first；这些是首结果类别，不是人工标注的根因。
- Pro/Flash、Luna、Qwen 的产物差异沿用同题成功配对，未从 Copy 推断模型理解、意图或维护性。
- 假设消融表完整保留，尚无实测解释加入摘要或结论。

## 仍需补充的事实

主文可写的方法内容已经补上；以下没有凭推测填写，仍以 LaTeX 注释保留待核对：

- 初始 reference 编写中作者与 AI 的实际分工、模型/工具与覆盖情况。
- 人工复核人数、日期、任务级记录，以及 AI 审核的具体模型、输入/输出和提示词记录。
- 正在服务器运行的消融条件、真实配对结果与统计分析。

不宣称独立盲审、双人一致性、全部 oracle 手写、统一 AI 自动生成，或审核后逐题重跑的时序。

## Fig. 2 编辑记录

使用内置 imagegen 编辑原 PNG，无 Python 像素编辑。正式文件为 `docs/paper/figures/fig02_construction_validation.png`；原图保留于 `docs/archive/snapshots/paper_methods_results_20260912/`。旧 PDF 不参与正文打包，未用其冒充新版。

第一次提示词：

```text
Edit the attached finalized scientific paper flowchart, preserving its entire existing layout, every box, icon, arrow, numbers, colors, typography, and all other wording. Make EXACTLY TWO small textual edits: (1) in construction stage 4 replace 'Independent reference' with 'Source-independent reference' (fit on one line if possible, otherwise two well-spaced lines in that same card). (2) In the right-side Frozen release card insert 'Retain validated tasks' as a small legible subtitle directly below 'Frozen release', using existing whitespace before the icon; do not overlap the icon. Do not redesign. Do not change 200 Python tasks, 176 source repositories, 182 pinned snapshots, All 200 retained tasks, 600/600 passing runs, or 3 executions per task. Keep existing blue construction band, orange validation band, clear arrow direction and horizontal landscape proportions. White page background, crisp high resolution text. All other text must remain verbatim and fully legible, no cropping.
```

背景修复提示词：

```text
Edit this scientific flowchart with ONE change: replace ALL BLACK BACKGROUND OUTSIDE THE COLORED PANELS AND RIGHT RELEASE CARD with SOLID PURE WHITE (#FFFFFF). The black area is not intended design: it was erroneously flattened transparency. This includes the large gap around the right-hand arrows, between the two bands, and outer margins. Preserve dark text and icon details inside the cards, preserve all blue/orange arrows and outlines, all words/numbers verbatim (especially Source-independent reference, Retain validated tasks, 200, 176, 182, 600/600). Preserve exact layout, same aspect ratio. Do NOT add text or redesign anything. Output high-resolution legible print-ready scientific figure on WHITE background.
```

目视检查：两处标签正确，200/176/182、200 packages、200 retained tasks、3 executions 与 600/600 均保留；箭头方向、框结构与原意一致。AI 输出并非逐像素保真的原 PPT 编辑，最终 PNG 为 1941 × 810；不声称整篇排版已经验证。
