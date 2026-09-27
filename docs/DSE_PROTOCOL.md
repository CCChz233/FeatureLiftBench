# DSE-40：入口引导的机械提取对照（v1.2 reviewed）

日期：2026-09-26。状态：实现与准备阶段；尚无正式评测结论。

本实验补充 RQ2，检验给定源码入口后，预先规定的机械搬迁能否满足目标契约。它不是证明模型“理解”的因果实验。DSE 获得入口位置及评测前审定的别名映射，现有 Full Source agent 不获得，因此不是完全相同输入的第三个消融臂。运行阶段无 agent，但准备阶段包含辅助人工审查，应完整披露。

## 固定输入与边界

- 使用 `docs/paper-workbench/experiments/source_ablation_40.json` 的同一 40 题（Direct 15、Adapted 20、Composite 5），不按结果筛选。
- 读取 `metadata.public_spec`、依赖锁及 canonical full-source archive；归档和物化树的 digest 必须与 source registry 一致。
- 提取阶段不读 public/hidden benchmark tests、reference、已有模型产物或 evaluator 结果，不 import/执行上游代码。
- 输出路径独立，保留全部题目和所有失败。生成器不覆盖已有 submission，评测入口拒绝自动重复已启动的实验。

## 机械规则

1. 索引根目录及嵌套 `src`/`lib` 源布局；对于根包支持源码声明的 literal `full_package_name`。排除 test/docs/example/build 等非运行目录；歧义布局不猜测。
2. 从声明入口静态解析定义或再导出；剥离 entrypoint 中源码布局前缀 `src.`/`lib.`，识别包路径中的显式 `__init__`，追踪单一静态命名父类中的方法。多重继承、动态绑定不猜测，未解析入口如实记录。
3. 对入口模块做静态 import 传递闭包，包含父包初始化。条件导入也纳入，因此允许过度提取。
4. 把仓库内顶层模块机械重命名为 `featurelifted._dse_pN`，避免仅因保留上游 import 名称而触发禁止依赖规则。重写绝对 import，保留相对 import、源码逻辑和所有未涉及 import 的文本。点式 import 保留原有根变量绑定语义。
5. 保留选中包下非 Python 资源（仍排除测试、文档、缓存树），生成必要的命名空间包结构。不执行编译扩展或源码构建钩子。
6. 为公开目标 API 查找同名静态绑定：声明入口、源码顶层包、已选模块/定义依次查找；同层歧义不猜测。允许冻结审查表显式指定已有顶层源码绑定的别名，不能覆盖已有自动映射。只再导出模块或顶层绑定，不改变调用签名，不把类方法适配成独立函数，不生成 NotImplementedError 空桩，不以 builtin 别名发明替代实现。
7. 动态 import、资源 API、distribution metadata 查询保持原样并记录风险。路径/逻辑修复不在本版本范围内。

这是一项有明确支持范围的机械程序，不代表所有可能的“复制”算法。资源/动态加载或 API 映射失败必须与已验证的行为遗漏区别解释。

## 实现与验证

- `harness/featureliftbench/direct_source_extraction.py`：提取核心。
- `harness/scripts/run_direct_source_extraction.py`：准备、环境预检、隔离评测。
- `harness/tests/test_direct_source_extraction.py`：人工构造的小型模块，不使用本次 40 题测试来调整程序。
- `harness/scripts/build_dse40_api_review.py`：可审计的逐接口判定和证据位置。
- `harness/config/experiments/dse40_api_review_v1.json`：40 题身份及 11 题、42 个顶层 API 的审查清单；其余 29 题仅记录自动名称映射，不声称已完成签名或行为审查。

```bash
PYTHONPATH=harness python3.12 -B -m pytest -q harness/tests/test_direct_source_extraction.py
python3.12 -B harness/scripts/run_direct_source_extraction.py prepare \
  --output experiments/dse/source_ablation40_v1_2_reviewed_20260926 \
  --api-review harness/config/experiments/dse40_api_review_v1.json
python3.12 -B harness/scripts/run_direct_source_extraction.py preflight \
  --output experiments/dse/source_ablation40_v1_2_reviewed_20260926 --image <pinned-evaluator-image>
python3.12 -B harness/scripts/run_direct_source_extraction.py evaluate \
  --output experiments/dse/source_ablation40_v1_2_reviewed_20260926 \
  --image <pinned-evaluator-image> --expected-image-id sha256:<verified-id>
```

准备清单保存 selection、程序、public_spec、依赖锁、源快照与每个 submission 的身份。正式评测还需核验 evaluator/task scoring files 与所选原始实验版本的对应关系；Docker image ID 验证和 catalog 检查不自动证明此对应关系。本机没有可用 Docker 时只做准备，不用 host pytest 冒充正式隔离评测。

## 结果读取与结论边界

最终需要 40 题逐题功能结果、首败 gate、lift type、API/入口映射覆盖、动态加载风险和静态源码重叠。所有产物的静态重叠要与论文只在功能成功后报告的 Copy 分开标注。当前准备记录的 `functional_status=not_evaluated` 不是失败分数。

- 总体分母保持 40；生成失败单列。环境/镜像/依赖基础设施错误单列，不能计为行为失败。
- 补充分析使用冻结时全部目标顶层 API 名称有绑定的 29 题，三种方法必须采用同一题目集合。称为 **name-covered subset**，不能称为 interface-compatible subset；名称覆盖不保证签名、成员、默认值、行为或可导入性。该集合是条件性诊断，不能替代 40 题总体结果，也不能把两个集合的差异解释成独立因果效应。
- 在正式评分前冻结映射表、29 题 ID、生成器、runner、协议和每题 submission 哈希。评分后不增补别名、不改子集、不改产物。名称覆盖不足是本程序适用范围的证据，不直接算作“源码搬迁后行为丢失”。
- gate 位置不是语义根因；需要结合日志区分 API 不对应、动态资源/导入、环境问题与行为断言。
- DSE 每题只生成一次，对照 Luna/Pro/Qwen 三组已有 Full Source 结果；共享 DSE 不能算作三组独立的 120 次运行。
- 同题比较可以沿用 paired bootstrap / McNemar；新增三次对照的多重比较处理须单独说明。
- Composite 仅 5 题，按类型结果为描述性证据。不得预先要求 Direct > Adapted > Composite。
- 若后续评测揭示的是生成器通用实现 bug，保留本版，另立修正版实验身份并完整披露，不能按 hidden 反馈只修失败题。

适当结论是“该入口引导的机械提取程序在这些任务上的能力与局限”；不能提前写成“agent 必须理解”或“源码复制一般无效”。现有 G2′ upstream re-export 检查不作为新 DSE 的结果。

## 2026-09-26 准备阶段记录

静态源码检查发现需要通用 `from module import *` 再导出支持；v1.1 增加了尊重 literal `__all__` 的解析与对应合成测试。v1/v1.1 均未进入 evaluator。准备状态及尚缺环境见 `reports/dse40_readiness_20260926.md`。

v1.2 的审查与结果见 `docs/DSE40_API_REVIEW.md`。修正两类通用入口解析，新增一个纯别名。40 题全部生成，39 题入口全部解析，29 题顶层名称全部覆盖；25 个原未映射名称中补上 1 个，剩余 24 个分布在同样的 11 题。15 项合成测试通过。没有功能评分，不据此写入论文成功率或因果结论。
