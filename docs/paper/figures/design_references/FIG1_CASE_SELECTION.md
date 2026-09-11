# Fig. 1 案例选择：coverage.py 路径重映射

## 推荐结论

推荐使用现有任务 `coverage__path_remap_core__001` 的 `PathAliases` 作为下一版 Fig. 1 的中心案例。该任务出现在当前 200 题冻结清单中。这里的推荐针对首图的解释力，不是任务难度排名或模型失败统计。

本轮浏览了 200 题任务清单，细读了 coverage 路径重映射、isort 配置解析、Alembic 版本图、Flake8 插件选项、Flask 路由和 APScheduler cron 的任务契约，并进一步比较前三者的实现或测试。未执行实验、模型产物或 reference。

## 为什么选它

1. **需求具体**：原项目文档明确说明，不同机器和 checkout 根目录产生的文件路径需要统一。
2. **功能边界清楚**：只复用路径规则和重映射行为，不需要实现覆盖率采集、数据合并 I/O、SQLite 存储或 CLI。
3. **行为差异直观**：同一条匹配规则，映射目标存在与不存在时，应返回不同结果。
4. **可展示实现关联**：`PathAliases` 依赖 glob 转换、路径规范化、存在性检查与异常定义；一个入口类不等于完整行为实现。
5. **读者负担较小**：两条路径和一个存在性条件即可理解关键行为，无需先讲迁移图或配置层级。

| 对照案例 | 优点 | 作为首图中心案例的代价 |
|---|---|---|
| Blinker Signal | 实现简洁，弱引用语义有辨识度 | 本身已是独立事件库，跨边界复用的动机需要额外解释 |
| isort settings | 配置、profile、路径规则分布清楚 | 优先级与文件发现需要占用较多说明空间 |
| Alembic RevisionMap | 与数据库迁移框架解耦的目标明确 | version-parent、dependency、branch/head 语义较多 |
| coverage PathAliases | 内部能力、具体需求、条件行为容易串联 | 不宜把它描述成整个 benchmark 最难或最复杂的任务 |

## 真实证据与用于解释的场景

**真实上游用途**：coverage.py 将来自不同机器的测量路径映射到报告机器上的文件路径。该用途见源仓库 `doc/config.rst` 的 `[paths]` 节和 `PathAliases` 类文档。

**建议用于首图的说明性复用场景**：一个独立的分析报告查看器，希望把 CI 路径映射到本地工作区，并沿用 coverage.py 的路径别名语义。它需要路径处理能力，但其输出契约不包含覆盖率测量和存储。

后一个场景是依据真实功能提出的说明性使用情境，不是已完成的用户研究、真实客户需求或已部署集成。图注应使用 “illustrative reuse scenario”。禁止暗示安装 coverage.py 在工程上不可行；选择新的依赖边界是本任务的约束和复用目标。

## 首图建议采用的微型例子

为减少文字，使用一个 POSIX 风格的示意工作区，只有一条显式别名规则：

```text
Rule:  /ci/*/src  ->  /workspace/src
Input: /ci/job42/src/a.py

Mapped target exists:      /workspace/src/a.py
Mapped target is missing: /ci/job42/src/a.py  (unchanged)
```

这是从已有契约、代码和测试推导的说明性实例，路径名为展示而改写；本轮没有执行这个具体输入。最终绘图可直接使用已有测试的路径名，或保留上述易读路径并标注示例。

该例子采用一条规则，所以不存在目标时返回原路径；不要把它推广成多规则情况下立即返回原路径。原实现会继续尝试后续规则。

解释重点：**路径字符串匹配成功，只完成了契约的一部分；是否接受映射，还取决于目标存在性等行为。** 不将示意行为画成任何模型的实测失败，不将其标成 SWE-bench 的通过/失败结果。

另可在契约小条目中列出：unmatched paths unchanged、separator normalization、invalid patterns rejected。无需在首图展示全部边界输入。

## 源实现如何简化成图

主框标注 `coverage.py — source repository`，内部强调：

- `PathAliases.add / map`：入口。
- `globs_to_regex`：规则编译。
- `canonical_filename / sep`：路径规范化与分隔符。
- `source_exists`：默认存在性判断；API 也支持传入 `exists` 回调。
- `ConfigError`：无效规则异常。

前四组位于 `coverage/files.py` 内，不要画成四个不同源文件。`ConfigError` 位于 `coverage/exceptions.py`。`files.py` 还引用 `coverage.env` 和 `coverage.misc`，但首图不需要展开所有辅助模块。

灰色背景可标示不属于输出范围的 surrounding system：measurement、combine/storage、CLI。它们用于说明功能边界，不表示该功能对每个模块都有直接依赖。

输出标注 `featurelifted.PathAliases`，到 source-free evaluation 的箭头上标注 `Submitted package only`。评测端用上面的两种存在性条件显示行为要求。

**必须区分两种“源”**：评测不可访问的是 coverage.py 原仓库；示例中的 `/workspace/src/a.py` 是映射目标/受控文件环境，可以由评测 fixture 或 `exists` 回调提供。不能把 source-free 画成禁止一切文件访问或不允许测试环境提供数据。

## 本地证据入口

以下路径相对项目根目录 `E:/FeatureLiftBench`：

- `artifacts/research_analysis/python200_prime/current_benchmark_freeze.json:862`：任务在冻结集合中。
- `benchmark/tasks/coverage__path_remap_core__001/TASK.md`：API、范围、契约、禁止上游导入。
- `benchmark/tasks/coverage__path_remap_core__001/metadata.json`：任务用途与上游 commit。
- `benchmark/tasks/coverage__path_remap_core__001/repo/doc/config.rst:491`：跨机器路径的真实用途；565 行说明存在性与后续规则。
- `benchmark/tasks/coverage__path_remap_core__001/repo/coverage/files.py:380`：`PathAliases` 类；408 行 `add`；447 行 `map`。
- `benchmark/tasks/coverage__path_remap_core__001/public_tests/test_public_api.py:11`：通配前缀映射。
- `benchmark/tasks/coverage__path_remap_core__001/hidden_tests/test_hidden_behavior.py:31`：目标不存在时保持原路径。
- `benchmark/tasks/coverage__path_remap_core__001/evaluation/oracle_manifest.json`：记录的源文件集合；不视为已证明的唯一最小依赖闭包。

## 候选英文图注

> An illustrative feature-lifting task: reusing coverage.py's path-remapping capability in a new package. The source repository provides implementation evidence for alias matching, path normalization, and existence-aware mapping. The lifted artifact must preserve the specified behavior when evaluated without access to the source repository. With a single matching alias, an existing target is accepted, whereas a missing target leaves the input path unchanged.

本轮仅选案例并整理绘图依据；未改论文、未替换图片。
