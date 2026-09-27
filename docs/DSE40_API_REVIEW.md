# DSE-40 公开源码接口审查

2026-09-26。审查已完成；正式 Docker 评测尚未执行。

本次完成的是评测前的映射审查和实验冻结。没有读取 benchmark 测试、参考实现或模型产物来选择别名、修改逻辑或修复失败。审查使用原 v1.1 准备记录、metadata.public_spec 和固定版本的完整上游源码。

## 已落实的处理

- 全部保留原 40 题：Direct 15、Adapted 20、Composite 5。
- 对原来 11 个名称未覆盖任务的全部 42 个顶层 required API 逐项记录判定、目标签名、上游候选、文件行号及文件哈希。
- 通用解析器识别包路径中的显式 `__init__`，并能追踪单一静态命名父类的方法。不生成新函数，不补充状态或异常处理。
- 接受 1 个纯别名：`requests_cache.cache_keys.create_key` → `featurelifted.create_cache_key`。两者均以 request 对象及选项生成 key；原实现原样再导出。其对 request.copy() 的要求、外部依赖、具体行为仍可能不满足目标契约，未声称等价。
- 25 个原未映射 API 中，24 个在当前规则下仍不能直接导出。不能为提升覆盖率而给它们增加适配逻辑。
- 保留已有同名导出，即使审查发现签名差异；另行记录，避免针对失败预先删改产物。

“29 题已映射”只表示 **顶层名称有绑定**。它不是 29 题接口兼容，更不是 29 题功能成功。

## 11 题的逐题结论

下表是摘要；完整逐接口证据在 `harness/config/experiments/dse40_api_review_v1.json`，审查来源与判定文本在 `harness/scripts/build_dse40_api_review.py`。

| Task | 剩余未映射 API | 公开源码显示的差异 |
| --- | --- | --- |
| pytest ini markers | MarkerRegistry、parse_linelist、split_marker_line | 逻辑分散在 Config 状态、linelist 分支及 marker 显示循环；新建独立函数或 registry 超出纯导出。修正 `__init__` 入口不等于补齐目标 API。 |
| hatch metadata | normalize_project_metadata、select_environment、MetadataValidationError | 元数据属性和环境继承 helper 依赖上下文、可变状态；目标要求独立字典输入/输出和命名异常。 |
| requests-cache | CachePolicy、get_expiration | 源码是 directive 数据与 expiration 转换，目标要求策略决策、headers/default/now 接口。仅 create_cache_key 增加别名。 |
| python-decouple | RepositoryDict | RepositoryEmpty 丢弃输入且永不命中键；不能把它换名充当字典仓库，也不在本规则下发明 builtin dict 替代实现。 |
| setuptools-scm | version_from_scm | get_version 不接受 tag/distance/dirty/node 参数；需要把显式 SCM 状态接入格式化逻辑。 |
| dateutil | ZoneResolver、parse_tzfile、UnknownZoneError、InvalidTZFileError | 上游是 tar/文件流加载及 timezone 对象；目标是 bytes 元数据、别名状态及指定异常。 |
| httpx | build_request | 入口来自 BaseClient，现已能定位；目标 free function 仍需组装实例状态及 default_* 参数，不能直接导出 unbound method。 |
| flake8 | OptionSpec、PluginSpec、classify_plugins、apply_select_ignore | 上游 argparse/loaded-plugin 数据模型与目标不一致；分类 helper 还需要额外 opts 参数。 |
| coverage | SourceSelector | InOrOut 需要 CoverageConfig、回调及 frame，目标要求直接配置参数与 modulename。 |
| readme-renderer | render_readme | markdown.render 仅处理 markdown 并返回 str/None；目标还要媒体类型分派及 warnings 返回值。 |
| poetry-core | DependencySpec、parse_project_dependencies、resolve_group | 上游依赖 ProjectPackage/DependencyGroup 对象，目标要求独立数据模型、字典输入输出及 include 遍历接口。 |

这些是候选源码与公开契约在当前规则下的差异，不是“不存在任何其他机械提取算法”的证明。未找到同名绑定的检索范围为生成器索引的 runtime Python 文件；动态生成 API 和未支持源布局不能据此断言不存在。

## 已有同名映射也有差异

在 11 题中，另外记录了 8 个已有同名导出的明显差异：

- flake8.OptionManager：上游构造函数有四个必需的 keyword-only 参数，目标允许无参构造。
- poetry.DependencyGroup：上游构造函数没有目标要求的 dependencies/includes 字段。
- decouple.Config：不接收目标的 environ 参数；直接读取 os.environ。
- decouple.Choices：上游的 flat 与 choices 含义不同，不能只看名称和位置参数。
- decouple.Csv：strip 默认值不同。
- requests-cache.create_key：源函数接收 request，目标同名函数接收 method/url。
- requests-cache.normalize_body：源函数接收 prepared request，目标接收 body/headers。
- requests-cache.normalize_headers：目标允许 None，源实现直接调用 headers.items()。

其余 9 个已有绑定仅记录可定位性及源码，不作行为认证。另 29 题尚未逐签名人工审查，所以冻结的辅助子集称为 **name-covered subset**。

## 固定分析口径

1. 主结果始终为全部 40 题，报告生成状态、四项 gate、功能通过率、类型分布及静态重叠。
2. 附加报告冻结的 29 题名称覆盖子集，Contract Only、Full Source 和 DSE 使用完全相同的题目 ID。不得按评分结果增删。
3. 11 题的名称缺失与 29 题中的实际评测失败分开解读；门槛失败位置本身不能充当语义根因。
4. DSE 获得入口提示及审定映射；现有 agents 没有这些额外提示。论文称为 entrypoint-guided mechanical extraction with a pre-specified alias map，并披露准备阶段的审查。
5. 高重叠、低通过率最多说明本规则下的源码搬迁不足以满足目标任务；不能直接证明 agent 必须有“深层理解”。

## 冻结产物与验证

新实验目录：`experiments/dse/source_ablation40_v1_2_reviewed_20260926/`。

- `prepared_suite.json`：40 题选择、源码/契约/依赖身份、映射及每个 submission 哈希。
- `api_review.json`：冻结的逐接口审查，内容与配置目录版本完全一致。
- `analysis_subsets.json`：40 题总体、29 题名称覆盖子集及其 lift type 分布。
- `static_diagnostics.json`：生成文件语法检查与所有产物的静态重叠。该指标不同于论文只对成功产物报告的 Copy。
- `freeze_manifest.json`：准备清单、程序、协议、审查报告、子集及静态诊断的哈希；相应文件另存到 `implementation/`。
- `environment_preflight.json`：当前环境状态，不是评分结果。

15 项合成测试通过。生成器没有运行任何上游代码或本次任务测试。40 题都产生了提交；39 题全部入口可静态定位，剩下 environs 的若干动态绑定方法未定位，照实保留。正式评分须先恢复 Docker 访问并确认固定 evaluator 镜像和评分资产身份，执行方式见 `docs/DSE_PROTOCOL.md`。未执行评测前，不把准备状态转换成通过/失败分数。

v1、v1.1 保留；v1.1 程序快照已补存于其 `implementation/`。新版本没有按 evaluator 反馈修改产物。
