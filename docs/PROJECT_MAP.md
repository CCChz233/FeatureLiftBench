# FeatureLiftBench 项目地图

> **Status: current · Last verified: 2026-09-14**

本项目当前服务于一篇 benchmark 与实证分析论文。新版正文来自用户提供的 `FSE.zip`，
可编辑入口是 [main.tex](paper/main.tex)。论文比较的是完整源码可见时，智能体能否把既有功能
重构为可独立运行、保持公开契约行为的软件包。

## 研究与实验范围

- 150 个 Python 任务，126 个源仓库、132 个固定快照。
- 六个 OpenHands 配置共同评测全部 150 题，900 条保留结果。
- 三配置 × 40 题 × Full Source / Contract Only 两臂，240 条消融结果。
- 900 条主实验轨迹的派生源码暴露记录；241/303 次行为首败有入口关联文件内容返回证据。
- 题目构建的参考执行记录为 150 × 3 = 450 次通过。这是历史记录核对，不是本轮重跑。

路径中的 `python200_hard`、`prime`、`v2` 是已有存储或实验标识。
当前论文的任务集合由 [python150_membership.json](paper/writing/python150_membership.json) 明确限定。

## 论文 → 数据 → 代码

| 论文位置 | 内容 | 主要证据 / 代码 |
| --- | --- | --- |
| §2 Benchmark | 契约、构建、验证、组成 | `benchmark/tasks/`、任务索引、`chapter2_python150_evidence.json` |
| §3 Protocol | 可见边界、四门评测、统计与消融 | `docs/EVALUATION.md`、`harness/featureliftbench/evaluator.py`、`docker_eval.py` |
| §4 RQ1 / 主表 | 功能结果、RRES、Copy、Steps、Tokens | `task_results.csv` → `writing/comprehensive_table.py` → `writing/templates/main_table.tex` |
| §4 RQ2 / Fig. 5 | 首败阶段 | `redraw_data.functional_results()` → `fig4_functional_results.py` |
| §4 RQ3 / Fig. 6 | 源码证据消融 | `source_ablation_40_20260913/` → `fig5_source_ablation.py` |
| §4 源码暴露表 | 按最终结果分组的读取证据 | `source_exposure/diagnosis/` → `writing/templates/source_exposure_table.tex` |
| §4 RQ4 / Fig. 7 | 同题通过产物的配对差异 | `task_results.csv` → `fig7_matched_footprint.py` |
| §5 Discussion | 行为遗漏案例与解释边界 | `writing/chapter5_case_evidence.json`、正文案例 |
| 历史附录 | 分类交叉图、多配置产物图 | 文件保留，当前精简正文不引用 |

所有正式路径与模型顺序见 [paper_sources.json](paper/paper_sources.json)。
完整 [绘图源码索引](paper/figures/scripts/README.md) 将当前 renderer 与历史设计分开。

## 当前图形资产

当前正文七张图、六张表，实际引用九个图片文件；旧附录资产不编入：

| 图号 | 资产 | 代码状态 |
| --- | --- | --- |
| Fig. 1 | `fig1.png` | AI 编辑定稿；仅有历史 Python 设计源码 |
| Fig. 2 | `fig2.png` | AI 编辑定稿；仅有历史 Python 设计源码 |
| Fig. 3 | `fig3a_families.pdf` + `fig3b_entanglement.pdf` | 当前双子图源码可运行 |
| Fig. 4 | `fig4_structure.pdf` | 新增结构分组点图 |
| Fig. 5 | `fig4.pdf` | 原失败阶段图；保留资产文件名 |
| Fig. 6 | `fig5a_pass_rate.pdf` + `fig5b_paired_gain.pdf` | 原源码消融图；正式 PDF 保留 |
| Fig. 7 | `fig7_matched_footprint.pdf` | 新增 Pro–Luna 同题差值图 |

未引用的旧组合图和备选图留作设计记录，不进入 Overleaf 打包清单。

## 实验记录在哪里

| 配置 | 当前主表结果 | 本地主实验 profile / 150 |
| --- | ---: | ---: |
| DeepSeek V4 Pro | 115/150 | 150 |
| DeepSeek V4 Flash | 108/150 | 150 |
| GPT-5.6 Luna | 102/150 | 0 |
| GLM-5.3-Flash | 68/150 | 7 |
| Qwen3.6-35B-A3B-FP8 | 63/150 | 0 |
| GPT-OSS 120B | 36/150 | 0 |

GLM 目录中恢复了 12 题，其中仅 7 题属于论文选定的 150 题。
因此本地可查 profile 为 307/900；完整逐题结果矩阵仍有 900 条。
详见 [原始结果恢复记录](../experiments/paper_results_20260913/README.md)。

Luna/GLM 的 150 条结果均缺少可核验供应商 Token 用量，表中保留 `—`。
Pro/Flash 报 uncached prompt + completion；Qwen/OSS 报 provider total，不能跨组作统一成本排名。

## 哪些内容属于历史研究

`method/` 与 `harness/` 中保留 V1 token cap、contract-closure、repo graph、
Public-feedback、其他 runtime 与 AutoSaddler 等实验支持。这些不构成当前论文的已验证方法贡献。
历史记录位于 `docs/archive/`、`archive/paper_unrelated_20260914/` 和各报告的原路径。
运行 catalog 保留历史 suite 标识；它不能替代当前论文的 150 题身份清单。

## 日常修改边界

- 改论述：`docs/paper/main.tex`、`references.bib`。
- 改表格排版：`docs/paper/writing/templates/`；数值由脚本从记录计算。
- 改图：每图一个 `fig*.py`；先用 `--output-dir` 生成预览再核对。
- 查分数：从 `paper_sources.json` 指向的逐题表出发，不从旧目录名或 run.status 猜测。
- 执行新实验：先读 [RUN.md](../RUN.md)，恢复对应源码、依赖与镜像身份。

## 检查如何分层

`paper.py check` 检查任务范围、数值、当前表格、所有引用和打包图片；
对现有历史源记录要求字节哈希匹配，或仅经明确 LF/CRLF 换行转换后匹配原哈希。
只在已知的归档位置解析已搬迁文件，不能用任意同名文件代替。
`paper.py audit` 进一步要求所有 900 个原始运行 profile，当前会明确失败。
`catalog check` 检查配置与 adapter 一致性，不执行 Docker 或证明环境已可运行。

这次整理的修改、验证和剩余问题见 [FSE 同步记录](paper/FSE_SYNC_20260914.md)。

当前扩充方案、任务完成情况及检查边界见 [Results 视觉证据计划](paper/RESULTS_VISUAL_PLAN.md)。
