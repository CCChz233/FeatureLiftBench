# Fig. 1 的论证目标：为什么需要评测跨边界的功能复用

状态：研究定位与构图建议，尚未替换图片或修改 main.tex。上一版 fig1_evidence_v2 是任务解释图，可保留作为后续示例素材；首图应更早建立动机。

## 首图需要证明的观点

现有仓库中已经存在的功能，并不自动成为可独立复用的组件。我们评测智能体能否利用完整实现证据，在新的包边界下保持规定行为，同时摆脱源仓库的运行时依赖。

英文研究问题：Can an agent preserve an existing capability when its original repository context is no longer available at runtime?

英文任务定位：Intact implementation evidence, a new package boundary, and source-free behavioral evaluation.

关键区别是推理阶段与交付后运行阶段对源仓库的不同角色：源仓库是可利用的实现证据，但不能成为新包的运行时依赖。Source-free 指源仓库不可用，不表示提交代码、标准库或允许的第三方依赖都不可用。

## 参考论文给出的启示

- SWE-bench Figure 1：issue、真实仓库、补丁和测试组成具体任务；Figure 2 另讲数据构建。可学习具体的输入/产物/判定对象，而非照搬模块排布。
  https://arxiv.org/pdf/2310.06770
- FeatureBench Figure 1：任务定义与结果并列；任务同时包括现有仓库扩展与从零构建。因此不能把我们定位为首个独立功能生成或首个 feature-level benchmark。
  https://arxiv.org/pdf/2602.10975
- FeatBench Figure 1 和 Section 3.1：用具体自然语言需求及仓库、环境、测试解释任务。需求驱动值得借鉴，四组件清单不必照搬。
  https://arxiv.org/pdf/2509.22237
- OSWorld Figure 1：用真实任务场景展示跨应用需求，Figure 2 再描述环境机制。可学习先展示需要完成的事情，再解释评测设施的组织方式。
  https://arxiv.org/html/2404.07972v2
- 软件移植已有研究。我们的论证应承接复用问题，而非宣称首次提出功能迁移。
  https://earlbarr.com/publications/autotransplant.pdf

以上是对论文图注、任务定义和引言的综合解读，不代表所有优秀论文都必须遵循同一种首图模板。

## 应先讲的需求

示意需求：Reuse an existing capability as an independent component while preserving its required behavior.

例子可以是将框架里的配置处理、开发工具里的解析功能或已有注册机制用于新包。明确这是基于 benchmark 任务的动机场景，不伪装为收集到的真实用户原话、用户研究或工业需求统计。

独立复用需求可以涉及依赖策略或新 API 边界，但图中不声称我们测量了体积部署收益、维护成本或安全收益。也不暗示安装完整库通常是错误选择；任务针对明确需要独立组件的复用场景。

## 推荐的最终构图：上方定位，中央矛盾，下方评测问题

### 上方约 25%：三个评测目标的对照

不画大面积排行榜或勾叉矩阵，使用三条紧凑、平行的任务轨迹：

1. Repository modification：issue + repository → patch → revised repository。
2. Feature implementation：feature requirement (+ incomplete context) → implement feature。另用短注说明存在 from-scratch 设置，不把 FeatureBench L2 归入原仓库内编辑。
3. Feature lifting：intact source + contract → independent package → source-free behavior。

前两行灰色，第三行强调色。论文名称和引用放 caption 或适量小标签。对照的是指定任务目标，不是断言既有任务不需要理解依赖、不测行为或不允许代码复用。

### 中央约 60%：一个需求引出的边界变化

左侧标为 Existing capability，表现源仓库轮廓及目标功能和支持逻辑。避免罗列大量文件名。仅选一个具体行为链，建议 Blinker 弱引用接收器生命周期：连接接收器 → 弱引用支持 → 回调清理。

源仓库里既有与目标行为相关的支持逻辑，也有与当前合同无关的项目功能。颜色区分目标、必要支持和无关上下文，不把所有源代码都画成需要丢弃的内容。图形连线如被解释为真实调用关系，须来自当前固定源版本。

右侧标为 Independent component，显示新的 featurelifted 包，承载同一项目标行为以及重建的支持逻辑。原源仓库在右侧运行环境中不可用。把移出原仓库后失去上下文支撑作为中心事件，而不是让机器人或 Docker 图标占据中心。

连接两侧的箭头标为 Preserve required behavior，穿过 New package boundary。允许代码复制、改编、重写，保持的是合同规定的行为，不强制代码结构或唯一最小依赖闭包。

在跨越边界的附近放三个短问题：

- What belongs to the capability?
- Which supporting behavior must be retained?
- Does it work without the source repository?

这些是任务挑战，不是声称现有实验分别测得了定位率、闭包恢复率和因果失败比例。

### 下方约 15%：FeatureLiftBench 如何把需求变为可检验的问题

一个可观察例子：A weak receiver is collected → it must no longer be invoked。左右用同一行为标记对应，说明行为要求跨边界保持。

一条精简评测说明：Evaluate the submitted package without the source repository。不再堆四个 gate、RRES、Copy、Steps、Tokens 或完整隐藏测试规则；这些留给任务定义、协议和结果图。

## 必须避免的夸大

- 不写：现有 benchmark 都只是修 bug。
- 不写：现有 benchmark 都不考察依赖、行为保持或独立功能生成。
- 不写：有源代码参考却失败，所以失败必然与定位无关。
- 不写：证明任意目标项目集成成功、全部上游语义等价、最小依赖闭包或完全可发布的包质量。
- 不将示意图中的失败路径包装为实际 Blinker 实验结果。
- 不将 source repository unavailable 画成 copying source code forbidden。

## 与 Introduction 的衔接

1. 跨边界复用既有能力的需求。
2. 已有实现不等于可独立运行：隐含支持行为需要被恢复与重新组织。
3. 修改原仓库、实现缺失功能和基于完整实现重建独立组件，具有不同任务目标。
4. FeatureLiftBench 用完整源证据、公开契约、新包边界和源仓库不可用的执行条件定义评测。
5. 已有结果表明包交付与合同满足仍存在落差，详见结果部分；首图不必加入数字。

## 候选英文 caption

Motivation and task positioning of FeatureLiftBench. Reusing an existing capability as an independent component changes its execution context: supporting behavior available in the source repository must be preserved or reconstructed within a new package boundary. Repository modification and feature implementation evaluate related objectives; feature lifting specifically provides intact implementation evidence and evaluates the resulting package without runtime access to the source repository. The illustrated receiver-lifetime requirement exemplifies behavior that must survive this transition. FeatureLiftBench operationalizes this reuse objective through explicit contracts and source-free execution.

本稿优先确定论证，不继续叠加图片细节。下一张正式设计应按上述论证重新组织，不能仅在 v2 顶部增加一段动机文字。
