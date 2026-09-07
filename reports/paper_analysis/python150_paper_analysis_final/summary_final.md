# Python-150 freeze v2 最终数据汇总

本文档把主实验全部**数字与逐题原始结果**收在一处，不依赖图片。  
Functional Pass = build ∧ public ∧ hidden ∧ isolation。空卷计失败。不用 `run.status`。  
Finding 3 仅 Pro+Flash 有包失败 L1，有效分母 n=63，assistant first pass，不是金标。官方 Hard-50 只进附录。

输入：`reports/paper_analysis/python150_prime_v2_analysis_20260905/task_results.csv`  
复现：`.venv/bin/python reports/paper_analysis/python150_paper_analysis_final/build.py`

模型：Pro = DeepSeek V4 Pro；Flash = DeepSeek V4 Flash；Luna = GPT-5.6 Luna (OpenLux)；GLM = GLM-5.3-Flash；Qwen = Qwen3.6-35B；OSS = GPT-OSS 120B。

---

## 1. 主表（数据层冻结）

分母 150。Functional Pass = build ∧ public ∧ hidden ∧ isolation。空卷计失败。  
RRES / Copy 只在 **Functional Pass 的包**上算（六家过门样本均无缺失）。Steps / Tokens 是 **150 题全过程**（含失败与空卷）。  
Pro/Flash tokens = incremental（uncached prompt + completion）。Qwen/OSS = provider `total_tokens`。Luna/GLM 原始运行没有可靠 token 字段，记为 —，不猜。IQR 报 \([Q_1, Q_3]\)（线性分位）。

### 1.1 能力

| 模型 | Pass@1 | Wilson 95% | Core-100 | hard3 | 空卷 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Pro | 115/150 (76.7%) | 69.3–82.7% | 94/100 (94.0%) | 21/50 (42.0%) | 0 |
| Flash | 108/150 (72.0%) | 64.3–78.6% | 90/100 (90.0%) | 18/50 (36.0%) | 0 |
| Luna | 102/150 (68.0%) | 60.2–74.9% | 82/100 (82.0%) | 20/50 (40.0%) | 6 |
| GLM | 68/150 (45.3%) | 37.6–53.3% | 62/100 (62.0%) | 6/50 (12.0%) | 38 |
| Qwen | 63/150 (42.0%) | 34.4–50.0% | 55/100 (55.0%) | 8/50 (16.0%) | 25 |
| OSS | 36/150 (24.0%) | 17.9–31.4% | 25/100 (25.0%) | 11/50 (22.0%) | 2 |

### 1.2 过门紧凑度（n = Pass）

| 模型 | n | Mean RRES | Median RRES | IQR RRES | Mean Copy | Median Copy | IQR Copy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Pro | 115 | 1.781 | 0.993 | [0.769, 1.290] | 0.777 | 0.957 | [0.716, 0.987] |
| Flash | 108 | 1.730 | 0.998 | [0.893, 1.221] | 0.810 | 0.968 | [0.839, 0.990] |
| Luna | 102 | 0.953 | 0.815 | [0.310, 1.002] | 0.415 | 0.164 | [0.048, 0.967] |
| GLM | 68 | 2.473 | 1.013 | [0.917, 1.158] | 0.843 | 0.947 | [0.811, 0.979] |
| Qwen | 63 | 1.556 | 0.975 | [0.650, 1.228] | 0.645 | 0.757 | [0.326, 0.972] |
| OSS | 36 | 1.176 | 0.983 | [0.292, 1.648] | 0.305 | 0.180 | [0.007, 0.530] |

Mean RRES > Median：过门包有右尾（少数提交远大于参考实现）。Luna copy 的 IQR 几乎跨满 [0, 1]，中位 0.164 掩盖了双峰，所以 Mean Copy 是 0.415。

### 1.3 过程（150 题）

| 模型 | Median steps | P90 steps | Median tokens | P90 tokens | token 口径 |
| --- | ---: | ---: | ---: | ---: | --- |
| Pro | 41.5 | 80.1 | 88020 | 225314 | incremental |
| Flash | 63 | 116.2 | 123618 | 269526 | incremental |
| Luna | 35.5 | 74.4 | — | — | 无字段 |
| GLM | 85.5 | 127 | — | — | 无字段 |
| Qwen | 41.5 | 106.6 | 1818620 | 5521030 | total_tokens |
| OSS | 19 | 61.1 | 525960 | 1877320 | total_tokens |

CSV：`csv/main_table.csv`，`csv/pass_compactness.csv`。

McNemar（精确二项双侧）：

- Pro vs Flash：Pro独过 10，Flash独过 3，p=0.09229
- Pro vs Luna：Pro独过 18，Luna独过 5，p=0.01062
- GLM vs Qwen：GLM独过 27，Qwen独过 22，p=0.5682

**能写：** 24.0%–76.7%；Pro 仍 35/150 未过；28 题六家全灭（22 道 hard3）；GLM 与 Qwen 同档。  
**不能写：** Pro 显著强于 Flash；GLM 强于 Qwen；Qwen 63/125 或 GLM 68/112。

---

## 2. 首败（互斥）

每题恰好一个 first-failure stage。Isolation 列是「第一道倒下的门」，不是 Isolation 失败总数。

| 模型 | Pass | Missing | Build | Public | Hidden | Isolation | 合计 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Pro | 115 | 0 | 0 | 25 | 10 | 0 | 150 |
| Flash | 108 | 0 | 0 | 26 | 15 | 1 | 150 |
| Luna | 102 | 6 | 3 | 27 | 12 | 0 | 150 |
| GLM | 68 | 38 | 3 | 31 | 8 | 2 | 150 |
| Qwen | 63 | 25 | 6 | 35 | 21 | 0 | 150 |
| OSS | 36 | 2 | 18 | 70 | 23 | 1 | 150 |

---

## 3. 独立四门（非互斥，仅有包）

同一提交可同时败多门。Isolation residual = 已过 build∧public∧hidden，只败 Isolation。

| 模型 | 有包 | 空卷 | Pass | Build fail | Public fail | Hidden fail | Isolation fail | Isolation given Build | Isolation residual | 首败 Isolation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Pro | 150 | 0 | 115 | 0 | 25 | 29 | 0 | 0 | 0 | 0 |
| Flash | 150 | 0 | 108 | 0 | 26 | 36 | 1 | 1 | 1 | 1 |
| Luna | 144 | 6 | 102 | 3 | 30 | 35 | 3 | 0 | 0 | 0 |
| GLM | 112 | 38 | 68 | 3 | 34 | 38 | 5 | 2 | 2 | 2 |
| Qwen | 125 | 25 | 63 | 6 | 41 | 58 | 8 | 2 | 0 | 0 |
| OSS | 148 | 2 | 36 | 18 | 88 | 100 | 22 | 4 | 1 | 1 |

原始 Isolation fail 合计 39；binding residual 合计 **4**。  
**能写：** Independence is rarely the binding constraint; preserving complete behavior is.  
**不能写：** 仅凭首败 Isolation≈0 就下结论，而不报这张非互斥表。

---

## 4. 难度谱（0/6–6/6）

每题 `num_models_solved` = 六模型 Functional Pass 之和。

| Solved | Core-100 | hard3 | 合计 |
| --- | ---: | ---: | ---: |
| 0/6 | 6 | 22 | 28 |
| 1/6 | 0 | 7 | 7 |
| 2/6 | 4 | 5 | 9 |
| 3/6 | 17 | 5 | 22 |
| 4/6 | 31 | 5 | 36 |
| 5/6 | 27 | 4 | 31 |
| 6/6 | 15 | 2 | 17 |

五模型对照（去掉 GLM；未解集不变）：

| Solved | Core-100 | hard3 | 合计 |
| --- | ---: | ---: | ---: |
| 0/5 | 6 | 22 | 28 |
| 1/5 | 0 | 8 | 8 |
| 2/5 | 9 | 4 | 13 |
| 3/5 | 32 | 6 | 38 |
| 4/5 | 33 | 6 | 39 |
| 5/5 | 20 | 4 | 24 |

### 4.1 六家全灭（0/6，n=28）

| task_id | split | Lift Type | feature_family |
| --- | --- | --- | --- |
| alembic__revision_map_core__hard3_001 | hard3 | Adapted | algorithm_data_structure |
| build__pyproject_backend_core__hard3_001 | hard3 | Adapted | validate_normalize_construct |
| celery__signal_dispatch_core__hard3_001 | hard3 | Adapted | registry_plugin_dispatch |
| click__lazy_command_core__hard3_001 | hard3 | Adapted | registry_plugin_dispatch |
| cookiecutter__repo_finder_core__hard3_001 | hard3 | Composite | config_resolve_discover |
| decorator__signature_preserving_core__001 | core100 | Direct | workflow_session_orchestration |
| filelock__reentrant_lock_core__001 | core100 | Adapted | workflow_session_orchestration |
| flake8__plugin_options_core__hard3_001 | hard3 | Composite | registry_plugin_dispatch |
| flask__route_dispatch_core__001 | core100 | Adapted | registry_plugin_dispatch |
| hatch__project_metadata_core__hard3_001 | hard3 | Adapted | resource_metadata_loading |
| jupyter_core__paths_resolver_core__hard3_001 | hard3 | Adapted | config_resolve_discover |
| keyring__backend_select_core__hard3_001 | hard3 | Composite | registry_plugin_dispatch |
| license_expression__policy_core__hard3_001 | hard3 | Direct | parse_tokenize_decode |
| mkdocs__plugin_config_core__hard3_001 | hard3 | Composite | registry_plugin_dispatch |
| multidict__multidict_mutation_core__hard3_001 | hard3 | Direct | algorithm_data_structure |
| parsel__selector_namespace_core__hard3_001 | hard3 | Adapted | parse_tokenize_decode |
| pluggy__hook_wrapper_core__hard3_001 | hard3 | Adapted | registry_plugin_dispatch |
| poetry_core__dependency_groups_core__hard3_001 | hard3 | Composite | resource_metadata_loading |
| pygments__lexer_core__001 | core100 | Direct | parse_tokenize_decode |
| pytest__ini_markers_core__001 | core100 | Composite | config_resolve_discover |
| pytest__marker_registry_core__hard3_001 | hard3 | Composite | registry_plugin_dispatch |
| python_decouple__config_repository_core__001 | core100 | Adapted | config_resolve_discover |
| readme_renderer__content_type_core__hard3_001 | hard3 | Adapted | serialize_format_render |
| requests_cache__cache_key_core__hard3_001 | hard3 | Composite | cache_retry_policy |
| scrapy__item_loader_core__hard3_001 | hard3 | Adapted | registry_plugin_dispatch |
| setuptools_scm__version_normalize_core__hard3_001 | hard3 | Adapted | resource_metadata_loading |
| starlette__route_matching_core__hard3_001 | hard3 | Adapted | registry_plugin_dispatch |
| yamale__schema_validate_core__hard3_001 | hard3 | Adapted | validate_normalize_construct |

### 4.2 仅 1/6 通过（n=7）

| task_id | split | Lift Type | 通过的模型 |
| --- | --- | --- | --- |
| aiohttp__url_params_core__hard3_001 | hard3 | Adapted | Luna |
| dateutil__zone_resolver_core__hard3_001 | hard3 | Composite | Pro |
| installer__wheel_record_core__hard3_001 | hard3 | Adapted | Pro |
| platformdirs__app_dirs_core__hard3_001 | hard3 | Adapted | Luna |
| responses__request_matcher_core__hard3_001 | hard3 | Composite | Luna |
| tox__factor_expression_core__hard3_001 | hard3 | Adapted | OSS |
| virtualenv__interpreter_spec_core__hard3_001 | hard3 | Adapted | Flash |

### 4.3 六家全过（6/6，n=17）

| task_id | split | Lift Type |
| --- | --- | --- |
| boltons__iterutils_core__001 | core100 | Adapted |
| cachetools__cache_eviction_core__001 | core100 | Direct |
| coverage__glob_matcher_core__001 | core100 | Direct |
| diskcache__eviction_policy_core__hard3_001 | hard3 | Composite |
| h11__message_parse_core__001 | core100 | Direct |
| humanize__naturaltime_core__001 | core100 | Direct |
| isodate__duration_parse_core__001 | core100 | Adapted |
| jinja2__compile_render_core__001 | core100 | Adapted |
| jsonpointer__resolve_core__001 | core100 | Direct |
| markdown_it__commonmark_render__001 | core100 | Direct |
| pluggy__hook_call_order__001 | core100 | Direct |
| pyramid__configurator_action_core__hard3_001 | hard3 | Composite |
| pytest__mark_expression_core__001 | core100 | Adapted |
| python_dotenv__env_parse_core__001 | core100 | Direct |
| python_frontmatter__roundtrip_core__001 | core100 | Direct |
| python_multipart__form_parse_core__001 | core100 | Direct |
| rfc3986__uri_parse_core__001 | core100 | Adapted |

---

## 5. Lift Type × hard3

题数（混杂来源）：Direct 53/56 在 Core；Composite 15/18 在 hard3。

| Split | Direct | Adapted | Composite | 合计 |
| --- | ---: | ---: | ---: | ---: |
| core100 | 53 | 44 | 3 | 100 |
| hard3 | 3 | 32 | 15 | 50 |

通过率（空卷计入失败）。pooled-6 = 六模型人次；pooled-5 = 去掉 GLM。

| 模型 | Split | Direct | Adapted | Composite |
| --- | --- | --- | --- | --- |
| Pro | core100 | 51/53 (96.2%) | 41/44 (93.2%) | 2/3 (66.7%) |
| Pro | hard3 | 0/3 (0.0%) | 14/32 (43.8%) | 7/15 (46.7%) |
| Flash | core100 | 49/53 (92.5%) | 39/44 (88.6%) | 2/3 (66.7%) |
| Flash | hard3 | 1/3 (33.3%) | 12/32 (37.5%) | 5/15 (33.3%) |
| Luna | core100 | 44/53 (83.0%) | 36/44 (81.8%) | 2/3 (66.7%) |
| Luna | hard3 | 1/3 (33.3%) | 14/32 (43.8%) | 5/15 (33.3%) |
| GLM | core100 | 40/53 (75.5%) | 22/44 (50.0%) | 0/3 (0.0%) |
| GLM | hard3 | 0/3 (0.0%) | 2/32 (6.2%) | 4/15 (26.7%) |
| Qwen | core100 | 31/53 (58.5%) | 22/44 (50.0%) | 2/3 (66.7%) |
| Qwen | hard3 | 0/3 (0.0%) | 5/32 (15.6%) | 3/15 (20.0%) |
| OSS | core100 | 15/53 (28.3%) | 9/44 (20.5%) | 1/3 (33.3%) |
| OSS | hard3 | 1/3 (33.3%) | 7/32 (21.9%) | 3/15 (20.0%) |
| pooled | core100 | 230/318 (72.3%) | 169/264 (64.0%) | 9/18 (50.0%) |
| pooled | hard3 | 3/18 (16.7%) | 54/192 (28.1%) | 27/90 (30.0%) |
| pooled_five | core100 | 190/265 (71.7%) | 147/220 (66.8%) | 9/15 (60.0%) |
| pooled_five | hard3 | 3/15 (20.0%) | 52/160 (32.5%) | 23/75 (30.7%) |

Core vs hard3 χ²：

| 模型 | Core pass | hard3 pass | χ² | p |
| --- | ---: | ---: | ---: | ---: |
| Pro | 94/100 | 21/50 | 47.52 | 5.444e-12 |
| Flash | 90/100 | 18/50 | 45.57 | 1.471e-11 |
| Luna | 82/100 | 20/50 | 25.13 | 5.369e-07 |
| GLM | 62/100 | 6/50 | 31.64 | 1.857e-08 |
| Qwen | 55/100 | 8/50 | 19.24 | 1.151e-05 |
| OSS | 25/100 | 11/50 | 0.04 | 0.8393 |

### 5.1 Logistic

`passed ~ C(model) + hard3 + C(lift_type, Treatment(Direct))`，cluster SE by task_id。  
参考类：Flash（all6 / five_no_glm / strong3 的 intercept 都是 Flash）。

| 拟合 | 项 | coef | SE | z | p | OR |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| all6 | Intercept | 2.029 | 0.251 | 8.08 | 6.737e-16 | 7.604 |
| all6 | Model[T.GLM] | -1.427 | 0.226 | -6.32 | 2.553e-10 | 0.240 |
| all6 | Model[T.Luna] | -0.240 | 0.205 | -1.17 | 0.2401 | 0.786 |
| all6 | Model[T.OSS] | -2.551 | 0.277 | -9.20 | 3.517e-20 | 0.078 |
| all6 | Model[T.Pro] | 0.304 | 0.157 | 1.94 | 0.0525 | 1.355 |
| all6 | Model[T.Qwen] | -1.592 | 0.224 | -7.12 | 1.092e-12 | 0.204 |
| all6 | Lift[T.Adapted] | -0.395 | 0.267 | -1.48 | 0.1389 | 0.673 |
| all6 | Lift[T.Composite] | -0.423 | 0.607 | -0.70 | 0.4858 | 0.655 |
| all6 | hard3 | -1.903 | 0.358 | -5.31 | 1.073e-07 | 0.149 |
| strong3 | Intercept | 2.125 | 0.324 | 6.56 | 5.236e-11 | 8.377 |
| strong3 | Model[T.Luna] | -0.267 | 0.227 | -1.17 | 0.2407 | 0.766 |
| strong3 | Model[T.Pro] | 0.334 | 0.172 | 1.95 | 0.05147 | 1.397 |
| strong3 | Lift[T.Adapted] | -0.118 | 0.451 | -0.26 | 0.7931 | 0.889 |
| strong3 | Lift[T.Composite] | -0.425 | 0.718 | -0.59 | 0.5535 | 0.654 |
| strong3 | hard3 | -2.387 | 0.459 | -5.20 | 1.945e-07 | 0.092 |
| five_no_glm | Intercept | 1.894 | 0.249 | 7.60 | 2.91e-14 | 6.645 |
| five_no_glm | Model[T.Luna] | -0.236 | 0.201 | -1.17 | 0.2401 | 0.790 |
| five_no_glm | Model[T.OSS] | -2.509 | 0.274 | -9.17 | 4.751e-20 | 0.081 |
| five_no_glm | Model[T.Pro] | 0.299 | 0.154 | 1.94 | 0.05244 | 1.348 |
| five_no_glm | Model[T.Qwen] | -1.563 | 0.221 | -7.06 | 1.611e-12 | 0.210 |
| five_no_glm | Lift[T.Adapted] | -0.201 | 0.290 | -0.69 | 0.4878 | 0.818 |
| five_no_glm | Lift[T.Composite] | -0.313 | 0.637 | -0.49 | 0.6236 | 0.731 |
| five_no_glm | hard3 | -1.890 | 0.392 | -4.82 | 1.456e-06 | 0.151 |

**判定：** 控制 hard3 后 Composite **不显著**（strong3 OR=0.65, p=0.55）。不要把 Direct→Adapted→Composite 写成独立 finding。难度轴是 hard3。OSS 的 Core vs hard3 不显著（p=0.84）。

---

## 6. 紧凑度（成对）

只在**共同 Functional Pass** 的题上比 copy fraction。

| 配对 | n | median copy A | median copy B | 中位数之差 | median(A−B) | A>B | B>A | 平 | Wilcoxon p | rank-biserial r | median RRES A | median RRES B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pro vs Luna | 97 | 0.966 | 0.191 | 0.774 | 0.213 | 76 | 18 | 3 | 1.18e-13 | 0.881 | 0.993 | 0.697 |
| Flash vs Luna | 92 | 0.970 | 0.204 | 0.766 | 0.209 | 75 | 14 | 3 | 4.24e-13 | 0.885 | 0.999 | 0.713 |

未配对、仅过门（分母不同，不能当同题比较；与 §1.2 同一套数）：

| 模型 | n | Mean RRES | Median RRES | IQR RRES | Mean Copy | Median Copy | IQR Copy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Pro | 115 | 1.781 | 0.993 | [0.769, 1.290] | 0.777 | 0.957 | [0.716, 0.987] |
| Flash | 108 | 1.730 | 0.998 | [0.893, 1.221] | 0.810 | 0.968 | [0.839, 0.990] |
| Luna | 102 | 0.953 | 0.815 | [0.310, 1.002] | 0.415 | 0.164 | [0.048, 0.967] |
| GLM | 68 | 2.473 | 1.013 | [0.917, 1.158] | 0.843 | 0.947 | [0.811, 0.979] |
| Qwen | 63 | 1.556 | 0.975 | [0.650, 1.228] | 0.645 | 0.757 | [0.326, 0.972] |
| OSS | 36 | 1.176 | 0.983 | [0.292, 1.648] | 0.305 | 0.180 | [0.007, 0.530] |

**能写：** 同题 Wilcoxon。**不能写：** Luna 因 copy 低就更好；用未配对中位给 150 题再排一次名。


### 6.1 Pro ∩ Luna 逐题 copy（n=97）

| task_id | hard3 | Lift Type | copy_Pro | copy_Luna | Pro−Luna |
| --- | --- | --- | ---: | ---: | ---: |
| attrs__validators_core__001 | False | Direct | 0.9957 | 0.1493 | 0.8463 |
| babel__plural_core__001 | False | Adapted | 0.9208 | 0.7833 | 0.1375 |
| bidict__bidirectional_map_core__001 | False | Direct | 0.9887 | 0.0847 | 0.9040 |
| bleach__sanitize_core__001 | False | Adapted | 0.9940 | 0.0485 | 0.9455 |
| blinker__signal_registry_core__001 | False | Direct | 0.5784 | 0.1147 | 0.4638 |
| boltons__iterutils_core__001 | False | Adapted | 0.5870 | 0.1588 | 0.4282 |
| cachetools__cache_eviction_core__001 | False | Direct | 0.9787 | 0.7467 | 0.2320 |
| cattrs__structure_core__001 | False | Direct | 0.9970 | 0.0749 | 0.9221 |
| chameleon__template_compile_core__001 | False | Adapted | 0.9677 | 0.9637 | 0.0040 |
| click__option_parser__001 | False | Adapted | 0.9989 | 0.9995 | -0.0006 |
| configobj__roundtrip_config_core__001 | False | Direct | 0.9993 | 0.9993 | 0.0000 |
| coverage__config_merge_core__001 | False | Adapted | 0.9277 | 0.1493 | 0.7784 |
| coverage__glob_matcher_core__001 | False | Direct | 0.8291 | 0.1402 | 0.6889 |
| coverage__report_core__001 | False | Adapted | 0.7557 | 0.2160 | 0.5397 |
| coverage__source_selection_core__001 | False | Adapted | 0.8016 | 0.0379 | 0.7637 |
| dataclasses_json__serde_core__001 | False | Direct | 0.9455 | 0.0412 | 0.9043 |
| diskcache__eviction_policy_core__hard3_001 | True | Composite | 0.0000 | 0.0000 | 0.0000 |
| distlib__wheel_metadata_core__hard3_001 | True | Adapted | 0.0426 | 0.0460 | -0.0034 |
| dynaconf__settings_merge_core__001 | False | Adapted | 0.9209 | 0.0671 | 0.8538 |
| environs__typed_env_core__001 | False | Direct | 0.9093 | 0.1429 | 0.7664 |
| faker__provider_core__001 | False | Direct | 0.9936 | 0.9347 | 0.0589 |
| fsspec__url_chain_core__hard3_001 | True | Adapted | 0.0859 | 0.0000 | 0.0859 |
| glom__spec_eval_core__hard3_001 | True | Adapted | 0.9552 | 0.0000 | 0.9552 |
| h11__message_parse_core__001 | False | Direct | 0.9973 | 0.9945 | 0.0027 |
| h2__frame_parse_core__001 | False | Adapted | 0.2666 | 0.1229 | 0.1437 |
| httpx__request_model_core__001 | False | Adapted | 0.9752 | 0.0442 | 0.9310 |
| humanize__naturaltime_core__001 | False | Direct | 0.9148 | 0.5087 | 0.4061 |
| importlib_metadata__entry_points_core__001 | False | Direct | 0.8627 | 0.4747 | 0.3881 |
| intervaltree__interval_tree_core__001 | False | Direct | 0.9792 | 0.9949 | -0.0156 |
| isodate__duration_parse_core__001 | False | Adapted | 0.9044 | 0.7336 | 0.1709 |
| isort__settings_resolver_core__hard3_001 | True | Adapted | 0.2403 | 0.0225 | 0.2177 |
| itsdangerous__timed_serializer_core__001 | False | Adapted | 0.2717 | 0.0861 | 0.1856 |
| jinja2__compile_render_core__001 | False | Adapted | 0.9900 | 0.9941 | -0.0041 |
| jinja2__filters_tests_core__001 | False | Adapted | 0.9868 | 0.9954 | -0.0086 |
| jinja2__lexer_parser_core__001 | False | Adapted | 0.9488 | 0.2634 | 0.6854 |
| jinja2__loader_inheritance_core__001 | False | Adapted | 0.9959 | 0.0753 | 0.9206 |
| json5__parse_core__001 | False | Direct | 0.9959 | 0.9967 | -0.0008 |
| jsonpath_ng__expression_eval_core__001 | False | Direct | 0.9961 | 0.0868 | 0.9093 |
| jsonpointer__resolve_core__001 | False | Direct | 0.8286 | 0.4636 | 0.3650 |
| jsonschema__validator_core__001 | False | Direct | 0.9678 | 0.0571 | 0.9107 |
| lark__grammar_loader_core__001 | False | Direct | 0.9988 | 0.9978 | 0.0010 |
| lark__visitor_transform_core__001 | False | Adapted | 0.9987 | 0.9987 | 0.0000 |
| mako__lexer_expression_core__001 | False | Direct | 0.9771 | 0.2611 | 0.7161 |
| markdown__extensions_core__001 | False | Adapted | 0.9950 | 0.9952 | -0.0002 |
| markdown_it__commonmark_render__001 | False | Direct | 0.9982 | 0.9973 | 0.0009 |
| marshmallow__schema_core__001 | False | Direct | 0.9660 | 0.9676 | -0.0016 |
| msgpack__pack_unpack_core__001 | False | Adapted | 1.0000 | 0.9887 | 0.0113 |
| networkx__dag_topo_core__001 | False | Direct | 0.4068 | 0.1138 | 0.2930 |
| packaging__requirement_marker_specifier__001 | False | Direct | 0.9842 | 0.9752 | 0.0091 |
| parse__format_parser_core__001 | False | Direct | 0.8553 | 0.0236 | 0.8316 |
| parso__python_parse_core__001 | False | Direct | 0.9830 | 0.9678 | 0.0152 |
| passlib__hash_context_core__001 | False | Direct | 0.9568 | 0.0000 | 0.9568 |
| pathvalidate__sanitize_core__001 | False | Direct | 0.9974 | 0.0480 | 0.9494 |
| pendulum__parse_format_core__001 | False | Adapted | 0.7148 | 0.1455 | 0.5693 |
| phonenumbers__parse_format_core__001 | False | Direct | 0.9852 | 0.0544 | 0.9308 |
| pluggy__hook_call_order__001 | False | Direct | 0.9972 | 0.1913 | 0.8059 |
| pydantic__field_validator_core__hard3_001 | True | Adapted | 0.0128 | 0.0000 | 0.0128 |
| pydantic_settings__env_source_core__001 | False | Adapted | 0.9699 | 0.0994 | 0.8705 |
| pydantic_v1__validation_error_core__001 | False | Adapted | 0.9810 | 0.0000 | 0.9810 |
| pygments__formatter_core__001 | False | Direct | 0.9573 | 0.9712 | -0.0139 |
| pyramid__configurator_action_core__hard3_001 | True | Composite | 0.1410 | 0.0000 | 0.1410 |
| pytest__fixture_resolve_core__001 | False | Composite | 0.1654 | 0.0184 | 0.1469 |
| pytest__mark_expression_core__001 | False | Adapted | 0.9603 | 0.8760 | 0.0843 |
| pytest__skipif_eval_core__001 | False | Composite | 0.4516 | 0.1695 | 0.2821 |
| python_box__config_box_core__001 | False | Direct | 0.9752 | 0.0872 | 0.8880 |
| python_dateutil__relativedelta_core__001 | False | Direct | 0.9656 | 0.9730 | -0.0074 |
| python_dateutil__rrule_core__001 | False | Direct | 0.9510 | 0.9507 | 0.0003 |
| python_dotenv__env_parse_core__001 | False | Direct | 0.9922 | 0.2750 | 0.7172 |
| python_frontmatter__roundtrip_core__001 | False | Direct | 0.8853 | 0.5991 | 0.2863 |
| python_multipart__form_parse_core__001 | False | Direct | 0.9831 | 0.9513 | 0.0317 |
| pyyaml__safe_load_dump__001 | False | Adapted | 0.9907 | 0.9831 | 0.0076 |
| redis__resp_parser_core__001 | False | Adapted | 0.9699 | 0.3835 | 0.5864 |
| referencing__json_schema_refs_core__001 | False | Adapted | 0.9830 | 0.1585 | 0.8245 |
| returns__result_pipeline_core__hard3_001 | True | Adapted | 0.0385 | 0.0000 | 0.0385 |
| rfc3986__uri_parse_core__001 | False | Adapted | 0.9781 | 0.0850 | 0.8931 |
| ruamel_yaml__roundtrip_core__001 | False | Adapted | 0.9773 | 0.9776 | -0.0003 |
| sortedcontainers__sorted_list_core__001 | False | Direct | 0.9866 | 0.1436 | 0.8430 |
| sphinx__extension_registry_core__hard3_001 | True | Composite | 0.1795 | 0.0000 | 0.1795 |
| sqlalchemy__event_dispatch_core__hard3_001 | True | Adapted | 0.0229 | 0.0000 | 0.0229 |
| sqlparse__parse_format_core__001 | False | Adapted | 0.9786 | 0.9799 | -0.0013 |
| sqlparse__parse_split_core__001 | False | Adapted | 0.9821 | 0.9815 | 0.0006 |
| sqlparse__token_tree_core__001 | False | Adapted | 0.9793 | 0.9879 | -0.0086 |
| stevedore__extension_manager_core__hard3_001 | True | Composite | 0.4020 | 0.1889 | 0.2131 |
| tabulate__table_format_core__001 | False | Direct | 1.0000 | 0.9892 | 0.0108 |
| tenacity__retry_state_core__hard3_001 | True | Adapted | 0.3873 | 0.2198 | 0.1676 |
| tomlkit__roundtrip_document__001 | False | Direct | 0.9695 | 0.9704 | -0.0009 |
| trafaret__validation_rules_core__hard3_001 | True | Adapted | 0.0150 | 0.0154 | -0.0004 |
| transitions__state_machine_core__hard3_001 | True | Adapted | 0.3487 | 0.0107 | 0.3380 |
| typer__command_parser_core__001 | False | Direct | 0.3005 | 0.0092 | 0.2913 |
| urllib3__retry_backoff_core__001 | False | Direct | 0.8993 | 0.7278 | 0.1714 |
| voluptuous__schema_validate_core__001 | False | Direct | 0.8978 | 0.0710 | 0.8268 |
| websockets__handshake_parse_core__001 | False | Adapted | 0.9251 | 0.4444 | 0.4806 |
| werkzeug__routing_core__001 | False | Adapted | 0.9128 | 0.9523 | -0.0394 |
| wheel__metadata_normalize_core__hard3_001 | True | Adapted | 0.4545 | 0.0448 | 0.4098 |
| wsproto__frame_parse_core__001 | False | Adapted | 0.9872 | 0.9914 | -0.0042 |
| xmltodict__xml_parse_core__001 | False | Direct | 0.7180 | 0.3590 | 0.3590 |
| yarl__url_model_core__001 | False | Adapted | 0.9956 | 0.9994 | -0.0039 |

### 6.2 Flash ∩ Luna 逐题 copy（n=92）

| task_id | hard3 | Lift Type | copy_Flash | copy_Luna | Flash−Luna |
| --- | --- | --- | ---: | ---: | ---: |
| attrs__validators_core__001 | False | Direct | 0.9971 | 0.1493 | 0.8478 |
| babel__plural_core__001 | False | Adapted | 0.9807 | 0.7833 | 0.1974 |
| bidict__bidirectional_map_core__001 | False | Direct | 0.9895 | 0.0847 | 0.9049 |
| blinker__signal_registry_core__001 | False | Direct | 0.9169 | 0.1147 | 0.8023 |
| boltons__iterutils_core__001 | False | Adapted | 0.9413 | 0.1588 | 0.7825 |
| cachetools__cache_eviction_core__001 | False | Direct | 0.9774 | 0.7467 | 0.2308 |
| cattrs__structure_core__001 | False | Direct | 0.9957 | 0.0749 | 0.9208 |
| chameleon__template_compile_core__001 | False | Adapted | 0.9653 | 0.9637 | 0.0016 |
| click__option_parser__001 | False | Adapted | 0.9988 | 0.9995 | -0.0007 |
| configobj__roundtrip_config_core__001 | False | Direct | 0.9987 | 0.9993 | -0.0007 |
| coverage__config_merge_core__001 | False | Adapted | 0.8733 | 0.1493 | 0.7241 |
| coverage__glob_matcher_core__001 | False | Direct | 0.6410 | 0.1402 | 0.5008 |
| coverage__report_core__001 | False | Adapted | 0.8392 | 0.2160 | 0.6232 |
| coverage__source_selection_core__001 | False | Adapted | 0.8364 | 0.0379 | 0.7985 |
| dataclasses_json__serde_core__001 | False | Direct | 0.9349 | 0.0412 | 0.8938 |
| diskcache__eviction_policy_core__hard3_001 | True | Composite | 0.0000 | 0.0000 | 0.0000 |
| distlib__wheel_metadata_core__hard3_001 | True | Adapted | 0.0380 | 0.0460 | -0.0080 |
| dynaconf__settings_merge_core__001 | False | Adapted | 0.9928 | 0.0671 | 0.9257 |
| environs__typed_env_core__001 | False | Direct | 0.9805 | 0.1429 | 0.8377 |
| faker__provider_core__001 | False | Direct | 0.9960 | 0.9347 | 0.0613 |
| fsspec__url_chain_core__hard3_001 | True | Adapted | 0.0276 | 0.0000 | 0.0276 |
| h11__message_parse_core__001 | False | Direct | 0.9953 | 0.9945 | 0.0007 |
| h2__frame_parse_core__001 | False | Adapted | 0.2701 | 0.1229 | 0.1471 |
| httpx__request_model_core__001 | False | Adapted | 0.9604 | 0.0442 | 0.9161 |
| humanize__naturaltime_core__001 | False | Direct | 0.9412 | 0.5087 | 0.4325 |
| importlib_metadata__entry_points_core__001 | False | Direct | 0.8127 | 0.4747 | 0.3380 |
| intervaltree__interval_tree_core__001 | False | Direct | 1.0000 | 0.9949 | 0.0051 |
| isodate__duration_parse_core__001 | False | Adapted | 0.8659 | 0.7336 | 0.1323 |
| isort__settings_resolver_core__hard3_001 | True | Adapted | 0.3648 | 0.0225 | 0.3423 |
| itsdangerous__timed_serializer_core__001 | False | Adapted | 0.3918 | 0.0861 | 0.3057 |
| jinja2__compile_render_core__001 | False | Adapted | 0.9957 | 0.9941 | 0.0017 |
| jinja2__filters_tests_core__001 | False | Adapted | 0.9867 | 0.9954 | -0.0087 |
| jinja2__lexer_parser_core__001 | False | Adapted | 0.9559 | 0.2634 | 0.6925 |
| jinja2__loader_inheritance_core__001 | False | Adapted | 0.9873 | 0.0753 | 0.9121 |
| json5__parse_core__001 | False | Direct | 0.9934 | 0.9967 | -0.0032 |
| json_logic__evaluator_core__hard3_001 | True | Direct | 0.8239 | 0.0719 | 0.7520 |
| jsonpath_ng__expression_eval_core__001 | False | Direct | 0.9959 | 0.0868 | 0.9091 |
| jsonpointer__resolve_core__001 | False | Direct | 1.0000 | 0.4636 | 0.5364 |
| jsonschema__validator_core__001 | False | Direct | 0.9897 | 0.0571 | 0.9326 |
| lark__grammar_loader_core__001 | False | Direct | 0.9982 | 0.9978 | 0.0004 |
| lark__visitor_transform_core__001 | False | Adapted | 0.9990 | 0.9987 | 0.0003 |
| mako__lexer_expression_core__001 | False | Direct | 0.9805 | 0.2611 | 0.7194 |
| markdown__extensions_core__001 | False | Adapted | 0.9932 | 0.9952 | -0.0020 |
| markdown_it__commonmark_render__001 | False | Direct | 0.9982 | 0.9973 | 0.0009 |
| marshmallow__schema_core__001 | False | Direct | 0.9903 | 0.9676 | 0.0228 |
| msgpack__pack_unpack_core__001 | False | Adapted | 0.9700 | 0.9887 | -0.0188 |
| networkx__dag_topo_core__001 | False | Direct | 0.9580 | 0.1138 | 0.8442 |
| packaging__requirement_marker_specifier__001 | False | Direct | 0.9802 | 0.9752 | 0.0050 |
| parse__format_parser_core__001 | False | Direct | 0.8372 | 0.0236 | 0.8136 |
| parso__python_parse_core__001 | False | Direct | 0.9817 | 0.9678 | 0.0139 |
| passlib__hash_context_core__001 | False | Direct | 0.9784 | 0.0000 | 0.9784 |
| pathvalidate__sanitize_core__001 | False | Direct | 0.9974 | 0.0480 | 0.9494 |
| phonenumbers__parse_format_core__001 | False | Direct | 0.9878 | 0.0544 | 0.9333 |
| pluggy__hook_call_order__001 | False | Direct | 0.9902 | 0.1913 | 0.7989 |
| pydantic_settings__env_source_core__001 | False | Adapted | 0.9420 | 0.0994 | 0.8426 |
| pydantic_v1__validation_error_core__001 | False | Adapted | 0.9806 | 0.0000 | 0.9806 |
| pygments__formatter_core__001 | False | Direct | 0.9805 | 0.9712 | 0.0093 |
| pyramid__configurator_action_core__hard3_001 | True | Composite | 0.0000 | 0.0000 | 0.0000 |
| pytest__fixture_resolve_core__001 | False | Composite | 0.0972 | 0.0184 | 0.0788 |
| pytest__mark_expression_core__001 | False | Adapted | 0.9233 | 0.8760 | 0.0473 |
| pytest__skipif_eval_core__001 | False | Composite | 0.3333 | 0.1695 | 0.1638 |
| python_box__config_box_core__001 | False | Direct | 0.9721 | 0.0872 | 0.8849 |
| python_dateutil__rrule_core__001 | False | Direct | 0.9078 | 0.9507 | -0.0429 |
| python_dotenv__env_parse_core__001 | False | Direct | 0.9942 | 0.2750 | 0.7192 |
| python_frontmatter__roundtrip_core__001 | False | Direct | 0.8207 | 0.5991 | 0.2216 |
| python_multipart__form_parse_core__001 | False | Direct | 0.9865 | 0.9513 | 0.0352 |
| pyyaml__safe_load_dump__001 | False | Adapted | 0.9939 | 0.9831 | 0.0108 |
| redis__resp_parser_core__001 | False | Adapted | 0.9463 | 0.3835 | 0.5628 |
| referencing__json_schema_refs_core__001 | False | Adapted | 0.9839 | 0.1585 | 0.8254 |
| returns__result_pipeline_core__hard3_001 | True | Adapted | 0.1190 | 0.0000 | 0.1190 |
| rfc3986__uri_parse_core__001 | False | Adapted | 0.9887 | 0.0850 | 0.9036 |
| ruamel_yaml__roundtrip_core__001 | False | Adapted | 0.9751 | 0.9776 | -0.0024 |
| schema__nested_validate_core__hard3_001 | True | Adapted | 0.5583 | 0.0176 | 0.5406 |
| sortedcontainers__sorted_list_core__001 | False | Direct | 0.9661 | 0.1436 | 0.8225 |
| sphinx__extension_registry_core__hard3_001 | True | Composite | 0.1292 | 0.0000 | 0.1292 |
| sqlalchemy__event_dispatch_core__hard3_001 | True | Adapted | 0.0000 | 0.0000 | 0.0000 |
| sqlparse__parse_format_core__001 | False | Adapted | 0.9809 | 0.9799 | 0.0010 |
| sqlparse__parse_split_core__001 | False | Adapted | 0.9835 | 0.9815 | 0.0020 |
| sqlparse__token_tree_core__001 | False | Adapted | 0.9830 | 0.9879 | -0.0049 |
| stevedore__extension_manager_core__hard3_001 | True | Composite | 0.4637 | 0.1889 | 0.2748 |
| tabulate__table_format_core__001 | False | Direct | 1.0000 | 0.9892 | 0.0108 |
| tomlkit__roundtrip_document__001 | False | Direct | 0.9695 | 0.9704 | -0.0009 |
| trafaret__validation_rules_core__hard3_001 | True | Adapted | 0.1129 | 0.0154 | 0.0975 |
| transitions__state_machine_core__hard3_001 | True | Adapted | 0.1819 | 0.0107 | 0.1712 |
| urllib3__retry_backoff_core__001 | False | Direct | 0.9489 | 0.7278 | 0.2211 |
| voluptuous__schema_validate_core__001 | False | Direct | 0.9580 | 0.0710 | 0.8871 |
| websockets__handshake_parse_core__001 | False | Adapted | 0.9434 | 0.4444 | 0.4990 |
| werkzeug__routing_core__001 | False | Adapted | 0.9355 | 0.9523 | -0.0168 |
| wheel__metadata_normalize_core__hard3_001 | True | Adapted | 0.2119 | 0.0448 | 0.1671 |
| wsproto__frame_parse_core__001 | False | Adapted | 0.9671 | 0.9914 | -0.0243 |
| xmltodict__xml_parse_core__001 | False | Direct | 0.8843 | 0.3590 | 0.5253 |
| yarl__url_model_core__001 | False | Adapted | 0.9956 | 0.9994 | -0.0039 |

---

## 7. Token / steps（附录）

Pro/Flash = incremental（uncached prompt + completion）。Qwen/OSS = provider `total_tokens`（无 cache 账）。Luna/GLM = 无 token 字段。

| 模型 | Pass | token 字段 | n_tokens | median tokens | P90 tokens | median steps | P90 steps | usage_unverified |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Pro | 115 | incremental_tokens | 150 | 88020 | 225314 | 41.500 | 80.100 | 0 |
| Flash | 108 | incremental_tokens | 150 | 123618 | 269526 | 63.000 | 116.2 | 0 |
| Luna | 102 | total_tokens | 0 | — | — | 35.500 | 74.400 | 150 |
| GLM | 68 | total_tokens | 0 | — | — | 85.500 | 127.0 | 150 |
| Qwen | 63 | total_tokens | 150 | 1818620 | 5521030 | 41.500 | 106.6 | 0 |
| OSS | 36 | total_tokens | 150 | 525960 | 1877320 | 19.000 | 61.100 | 0 |

Core vs hard3：

| 模型 | split | n | passed | median tokens | median steps |
| --- | --- | ---: | ---: | ---: | ---: |
| Pro | core100 | 100 | 94 | 81509 | 41.000 |
| Pro | hard3 | 50 | 21 | 118318 | 49.500 |
| Flash | core100 | 100 | 90 | 108258 | 62.500 |
| Flash | hard3 | 50 | 18 | 202895 | 64.500 |
| Luna | core100 | 100 | 82 | — | 37.000 |
| Luna | hard3 | 50 | 20 | — | 31.000 |
| GLM | core100 | 100 | 62 | — | 86.000 |
| GLM | hard3 | 50 | 6 | — | 81.000 |
| Qwen | core100 | 100 | 55 | 2172840 | 44.500 |
| Qwen | hard3 | 50 | 8 | 1375320 | 37.000 |
| OSS | core100 | 100 | 25 | 608744 | 21.000 |
| OSS | hard3 | 50 | 11 | 374088 | 15.000 |

Pass vs Fail：

| 模型 | outcome | n | median tokens | median steps |
| --- | --- | ---: | ---: | ---: |
| Pro | pass | 115 | 86640 | 41.000 |
| Pro | fail | 35 | 115732 | 45.000 |
| Flash | pass | 108 | 113398 | 63.000 |
| Flash | fail | 42 | 179408 | 63.000 |
| Luna | pass | 102 | — | 37.000 |
| Luna | fail | 48 | — | 31.000 |
| GLM | pass | 68 | — | 85.500 |
| GLM | fail | 82 | — | 87.000 |
| Qwen | pass | 63 | 2127880 | 44.000 |
| Qwen | fail | 87 | 1463600 | 36.000 |
| OSS | pass | 36 | 387166 | 17.000 |
| OSS | fail | 114 | 551630 | 20.000 |

Mann–Whitney（双侧）：

| 模型 | 字段 | median Core vs hard3 | p | median Pass vs Fail | p |
| --- | --- | --- | --- | --- | --- |
| Pro | incremental_tokens | 81509 vs 118318 | 9.72e-06 | 86640 vs 115732 | 0.00971 |
| Flash | incremental_tokens | 108258 vs 202895 | 1.13e-05 | 113398 vs 179408 | 0.000337 |
| Qwen | total_tokens | 2172841 vs 1375316 | 0.00129 | 2127880 vs 1463605 | 0.0089 |
| OSS | total_tokens | 608744 vs 374088 | 0.0544 | 387166 vs 551630 | 0.399 |

Pro/Flash：hard3 更耗 token，通过率仍大幅下降。**能写：** Additional interaction budget alone does not eliminate the hard-tail gap.  
**不能写：** 美元成本；Luna/GLM token 排名；把 Pro/Flash 的 total_tokens 当计费量。

---

## 8. Pro vs Flash 不一致题（13 题）

McNemar 10 vs 3，p=0.092。Pro 没有主要在救 Composite（10 题里只有 2 道 Composite）。Flash 反超 3 题全是 hard3 行为失败。

| task_id | 谁过 | hard3 | Lift Type | Pro 首败 | Flash 首败 | Pro L1 | Flash L1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bleach__sanitize_core__001 | Pro | False | Adapted | functional_pass | hidden_failure | — | packaging_modularization |
| dateutil__zone_resolver_core__hard3_001 | Pro | True | Composite | functional_pass | hidden_failure | — | contract_api_completion |
| glom__spec_eval_core__hard3_001 | Pro | True | Adapted | functional_pass | hidden_failure | — | behavior_drift |
| installer__wheel_record_core__hard3_001 | Pro | True | Adapted | functional_pass | hidden_failure | — | contract_api_completion |
| jupyter_server__extension_config_core__hard3_001 | Pro | True | Composite | functional_pass | hidden_failure | — | behavior_drift |
| pendulum__parse_format_core__001 | Pro | False | Adapted | functional_pass | public_failure | — | contract_api_completion |
| pydantic__field_validator_core__hard3_001 | Pro | True | Adapted | functional_pass | hidden_failure | — | behavior_drift |
| python_dateutil__relativedelta_core__001 | Pro | False | Direct | functional_pass | public_failure | — | contract_api_completion |
| tenacity__retry_state_core__hard3_001 | Pro | True | Adapted | functional_pass | hidden_failure | — | behavior_drift |
| typer__command_parser_core__001 | Pro | False | Direct | functional_pass | isolation_failure | — | packaging_modularization |
| json_logic__evaluator_core__hard3_001 | Flash | True | Direct | hidden_failure | functional_pass | contract_api_completion | — |
| schema__nested_validate_core__hard3_001 | Flash | True | Adapted | hidden_failure | functional_pass | behavior_drift | — |
| virtualenv__interpreter_spec_core__hard3_001 | Flash | True | Adapted | public_failure | functional_pass | behavior_drift | — |

---

## 9. Semantic L1（Finding 3，不是金标）

仅 Pro+Flash 有包失败普查。有效 Agent 分母 n=63（题目缺陷已剔除）。assistant_first_pass。不要并入 GLM/Qwen/OSS。

| primary | 合计 | Pro | Flash |
| --- | ---: | ---: | ---: |
| behavior_drift | 54 | 26 | 28 |
| contract_api_completion | 7 | 2 | 5 |
| packaging_modularization | 2 | 0 | 2 |

有效行：Pro 28，Flash 35，合计 63。闭合类（API 未闭合 + drift）占绝大多数。localization 为 0。


逐条（有效 Agent 行）：

| task_id | 模型 | 首败 | primary | eligibility |
| --- | --- | --- | --- | --- |
| aiohttp__url_params_core__hard3_001 | Pro | hidden_failure | contract_api_completion | valid_agent_evidence |
| alembic__revision_map_core__hard3_001 | Pro | public_failure | behavior_drift | valid_agent_evidence |
| build__pyproject_backend_core__hard3_001 | Pro | public_failure | behavior_drift | valid_agent_evidence |
| celery__signal_dispatch_core__hard3_001 | Pro | public_failure | behavior_drift | valid_agent_evidence |
| cookiecutter__repo_finder_core__hard3_001 | Pro | public_failure | behavior_drift | valid_agent_evidence |
| decorator__signature_preserving_core__001 | Pro | public_failure | behavior_drift | valid_agent_evidence |
| filelock__reentrant_lock_core__001 | Pro | public_failure | behavior_drift | valid_agent_evidence |
| flask__route_dispatch_core__001 | Pro | public_failure | behavior_drift | valid_agent_evidence |
| json_logic__evaluator_core__hard3_001 | Pro | hidden_failure | contract_api_completion | valid_agent_evidence |
| jupyter_core__paths_resolver_core__hard3_001 | Pro | public_failure | behavior_drift | valid_agent_evidence |
| keyring__backend_select_core__hard3_001 | Pro | public_failure | behavior_drift | valid_agent_evidence |
| license_expression__policy_core__hard3_001 | Pro | hidden_failure | behavior_drift | valid_agent_evidence |
| mkdocs__plugin_config_core__hard3_001 | Pro | public_failure | behavior_drift | valid_agent_evidence |
| multidict__multidict_mutation_core__hard3_001 | Pro | public_failure | behavior_drift | valid_agent_evidence |
| parsel__selector_namespace_core__hard3_001 | Pro | public_failure | behavior_drift | valid_agent_evidence |
| platformdirs__app_dirs_core__hard3_001 | Pro | public_failure | behavior_drift | valid_agent_evidence |
| poetry_core__dependency_groups_core__hard3_001 | Pro | public_failure | behavior_drift | valid_agent_evidence |
| pygments__lexer_core__001 | Pro | hidden_failure | behavior_drift | valid_agent_evidence |
| pytest__marker_registry_core__hard3_001 | Pro | hidden_failure | behavior_drift | valid_agent_evidence |
| python_decouple__config_repository_core__001 | Pro | hidden_failure | behavior_drift | valid_agent_evidence |
| requests_cache__cache_key_core__hard3_001 | Pro | hidden_failure | behavior_drift | valid_agent_evidence |
| responses__request_matcher_core__hard3_001 | Pro | hidden_failure | behavior_drift | valid_agent_evidence |
| schema__nested_validate_core__hard3_001 | Pro | hidden_failure | behavior_drift | valid_agent_evidence |
| scrapy__item_loader_core__hard3_001 | Pro | public_failure | behavior_drift | valid_agent_evidence |
| starlette__route_matching_core__hard3_001 | Pro | hidden_failure | behavior_drift | valid_agent_evidence |
| tox__factor_expression_core__hard3_001 | Pro | public_failure | behavior_drift | valid_agent_evidence |
| virtualenv__interpreter_spec_core__hard3_001 | Pro | public_failure | behavior_drift | valid_agent_evidence |
| yamale__schema_validate_core__hard3_001 | Pro | public_failure | behavior_drift | valid_agent_evidence |
| aiohttp__url_params_core__hard3_001 | Flash | hidden_failure | contract_api_completion | valid_agent_evidence |
| alembic__revision_map_core__hard3_001 | Flash | public_failure | behavior_drift | valid_agent_evidence |
| bleach__sanitize_core__001 | Flash | hidden_failure | packaging_modularization | valid_agent_evidence |
| build__pyproject_backend_core__hard3_001 | Flash | public_failure | behavior_drift | valid_agent_evidence |
| celery__signal_dispatch_core__hard3_001 | Flash | public_failure | behavior_drift | valid_agent_evidence |
| cookiecutter__repo_finder_core__hard3_001 | Flash | public_failure | behavior_drift | valid_agent_evidence |
| dateutil__zone_resolver_core__hard3_001 | Flash | hidden_failure | contract_api_completion | valid_agent_evidence |
| decorator__signature_preserving_core__001 | Flash | public_failure | behavior_drift | valid_agent_evidence |
| filelock__reentrant_lock_core__001 | Flash | public_failure | behavior_drift | valid_agent_evidence |
| flask__route_dispatch_core__001 | Flash | public_failure | behavior_drift | valid_agent_evidence |
| glom__spec_eval_core__hard3_001 | Flash | hidden_failure | behavior_drift | valid_agent_evidence |
| installer__wheel_record_core__hard3_001 | Flash | hidden_failure | contract_api_completion | valid_agent_evidence |
| jupyter_core__paths_resolver_core__hard3_001 | Flash | public_failure | behavior_drift | valid_agent_evidence |
| jupyter_server__extension_config_core__hard3_001 | Flash | hidden_failure | behavior_drift | valid_agent_evidence |
| keyring__backend_select_core__hard3_001 | Flash | public_failure | behavior_drift | valid_agent_evidence |
| license_expression__policy_core__hard3_001 | Flash | hidden_failure | behavior_drift | valid_agent_evidence |
| mkdocs__plugin_config_core__hard3_001 | Flash | public_failure | behavior_drift | valid_agent_evidence |
| multidict__multidict_mutation_core__hard3_001 | Flash | public_failure | behavior_drift | valid_agent_evidence |
| parsel__selector_namespace_core__hard3_001 | Flash | public_failure | behavior_drift | valid_agent_evidence |
| pendulum__parse_format_core__001 | Flash | public_failure | contract_api_completion | valid_agent_evidence |
| platformdirs__app_dirs_core__hard3_001 | Flash | public_failure | behavior_drift | valid_agent_evidence |
| poetry_core__dependency_groups_core__hard3_001 | Flash | public_failure | behavior_drift | valid_agent_evidence |
| pydantic__field_validator_core__hard3_001 | Flash | hidden_failure | behavior_drift | valid_agent_evidence |
| pygments__lexer_core__001 | Flash | hidden_failure | behavior_drift | valid_agent_evidence |
| pytest__marker_registry_core__hard3_001 | Flash | hidden_failure | behavior_drift | valid_agent_evidence |
| python_dateutil__relativedelta_core__001 | Flash | public_failure | contract_api_completion | valid_agent_evidence |
| python_decouple__config_repository_core__001 | Flash | hidden_failure | behavior_drift | valid_agent_evidence |
| requests_cache__cache_key_core__hard3_001 | Flash | hidden_failure | behavior_drift | valid_agent_evidence |
| responses__request_matcher_core__hard3_001 | Flash | hidden_failure | behavior_drift | valid_agent_evidence |
| scrapy__item_loader_core__hard3_001 | Flash | public_failure | behavior_drift | valid_agent_evidence |
| starlette__route_matching_core__hard3_001 | Flash | hidden_failure | behavior_drift | valid_agent_evidence |
| tenacity__retry_state_core__hard3_001 | Flash | hidden_failure | behavior_drift | valid_agent_evidence |
| tox__factor_expression_core__hard3_001 | Flash | public_failure | behavior_drift | valid_agent_evidence |
| typer__command_parser_core__001 | Flash | isolation_failure | packaging_modularization | valid_agent_evidence |
| yamale__schema_validate_core__hard3_001 | Flash | public_failure | behavior_drift | valid_agent_evidence |

---

## 10. 逐题主表（150 题 × 6 模型）

`pass_*`：1 = Functional Pass，0 = 失败。`stage_*` = first-failure stage。

| task_id | split | Lift | family | solved | Pro | Flash | Luna | GLM | Qwen | OSS | st_Pro | st_Flash | st_Luna | st_GLM | st_Qwen | st_OSS |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |
| aiohttp__url_params_core__hard3_001 | hard3 | Adapted | validate_normalize_construct | 1/6 | 0 | 0 | 1 | 0 | 0 | 0 | hidden | hidden | pass | public | hidden | hidden |
| alembic__revision_map_core__hard3_001 | hard3 | Adapted | algorithm_data_structure | 0/6 | 0 | 0 | 0 | 0 | 0 | 0 | public | public | public | missing | public | public |
| apscheduler__cron_trigger_core__hard3_001 | hard3 | Adapted | protocol_state_transition | 3/6 | 1 | 1 | 0 | 0 | 0 | 1 | pass | pass | public | missing | public | pass |
| arrow__parse_format_core__001 | core100 | Adapted | parse_tokenize_decode | 2/6 | 1 | 1 | 0 | 0 | 0 | 0 | pass | pass | missing | public | public | public |
| astroid__nodes_core__001 | core100 | Adapted | parse_tokenize_decode | 2/6 | 1 | 1 | 0 | 0 | 0 | 0 | pass | pass | hidden | missing | hidden | public |
| attrs__validators_core__001 | core100 | Direct | validate_normalize_construct | 4/6 | 1 | 1 | 1 | 1 | 0 | 0 | pass | pass | pass | pass | hidden | public |
| babel__plural_core__001 | core100 | Adapted | cache_retry_policy | 4/6 | 1 | 1 | 1 | 1 | 0 | 0 | pass | pass | pass | pass | missing | hidden |
| bidict__bidirectional_map_core__001 | core100 | Direct | algorithm_data_structure | 5/6 | 1 | 1 | 1 | 1 | 0 | 1 | pass | pass | pass | pass | missing | pass |
| bleach__sanitize_core__001 | core100 | Adapted | validate_normalize_construct | 3/6 | 1 | 0 | 1 | 1 | 0 | 0 | pass | hidden | pass | pass | build | public |
| blinker__signal_registry_core__001 | core100 | Direct | registry_plugin_dispatch | 5/6 | 1 | 1 | 1 | 1 | 1 | 0 | pass | pass | pass | pass | pass | build |
| boltons__iterutils_core__001 | core100 | Adapted | algorithm_data_structure | 6/6 | 1 | 1 | 1 | 1 | 1 | 1 | pass | pass | pass | pass | pass | pass |
| build__pyproject_backend_core__hard3_001 | hard3 | Adapted | validate_normalize_construct | 0/6 | 0 | 0 | 0 | 0 | 0 | 0 | public | public | public | public | public | public |
| cachetools__cache_eviction_core__001 | core100 | Direct | cache_retry_policy | 6/6 | 1 | 1 | 1 | 1 | 1 | 1 | pass | pass | pass | pass | pass | pass |
| cattrs__structure_core__001 | core100 | Direct | serialize_format_render | 5/6 | 1 | 1 | 1 | 1 | 1 | 0 | pass | pass | pass | pass | pass | public |
| celery__signal_dispatch_core__hard3_001 | hard3 | Adapted | registry_plugin_dispatch | 0/6 | 0 | 0 | 0 | 0 | 0 | 0 | public | public | public | public | public | public |
| cerberus__schema_validate_core__001 | core100 | Direct | validate_normalize_construct | 3/6 | 1 | 1 | 0 | 1 | 0 | 0 | pass | pass | hidden | pass | hidden | public |
| chameleon__template_compile_core__001 | core100 | Adapted | serialize_format_render | 4/6 | 1 | 1 | 1 | 1 | 0 | 0 | pass | pass | pass | pass | missing | build |
| click__lazy_command_core__hard3_001 | hard3 | Adapted | registry_plugin_dispatch | 0/6 | 0 | 0 | 0 | 0 | 0 | 0 | public | public | public | public | public | public |
| click__option_parser__001 | core100 | Adapted | parse_tokenize_decode | 4/6 | 1 | 1 | 1 | 1 | 0 | 0 | pass | pass | pass | pass | public | public |
| configobj__roundtrip_config_core__001 | core100 | Direct | config_resolve_discover | 4/6 | 1 | 1 | 1 | 1 | 0 | 0 | pass | pass | pass | pass | public | public |
| cookiecutter__repo_finder_core__hard3_001 | hard3 | Composite | config_resolve_discover | 0/6 | 0 | 0 | 0 | 0 | 0 | 0 | public | public | missing | public | public | public |
| coverage__config_merge_core__001 | core100 | Adapted | config_resolve_discover | 5/6 | 1 | 1 | 1 | 1 | 1 | 0 | pass | pass | pass | pass | pass | hidden |
| coverage__glob_matcher_core__001 | core100 | Direct | config_resolve_discover | 6/6 | 1 | 1 | 1 | 1 | 1 | 1 | pass | pass | pass | pass | pass | pass |
| coverage__path_remap_core__001 | core100 | Adapted | config_resolve_discover | 5/6 | 1 | 1 | 0 | 1 | 1 | 1 | pass | pass | build | pass | pass | pass |
| coverage__report_core__001 | core100 | Adapted | serialize_format_render | 3/6 | 1 | 1 | 1 | 0 | 0 | 0 | pass | pass | pass | public | public | public |
| coverage__source_selection_core__001 | core100 | Adapted | config_resolve_discover | 3/6 | 1 | 1 | 1 | 0 | 0 | 0 | pass | pass | pass | public | public | hidden |
| croniter__cron_parse_core__001 | core100 | Direct | protocol_state_transition | 3/6 | 1 | 1 | 0 | 1 | 0 | 0 | pass | pass | public | pass | build | public |
| dataclasses_json__serde_core__001 | core100 | Direct | serialize_format_render | 5/6 | 1 | 1 | 1 | 1 | 1 | 0 | pass | pass | pass | pass | pass | public |
| dateutil__zone_resolver_core__hard3_001 | hard3 | Composite | resource_metadata_loading | 1/6 | 1 | 0 | 0 | 0 | 0 | 0 | pass | hidden | missing | public | public | hidden |
| decorator__signature_preserving_core__001 | core100 | Direct | workflow_session_orchestration | 0/6 | 0 | 0 | 0 | 0 | 0 | 0 | public | public | public | public | public | public |
| deepdiff__deep_compare_core__001 | core100 | Direct | algorithm_data_structure | 2/6 | 1 | 1 | 0 | 0 | 0 | 0 | pass | pass | missing | build | build | public |
| diskcache__eviction_policy_core__hard3_001 | hard3 | Composite | cache_retry_policy | 6/6 | 1 | 1 | 1 | 1 | 1 | 1 | pass | pass | pass | pass | pass | pass |
| distlib__wheel_metadata_core__hard3_001 | hard3 | Adapted | resource_metadata_loading | 5/6 | 1 | 1 | 1 | 0 | 1 | 1 | pass | pass | pass | hidden | pass | pass |
| dynaconf__settings_merge_core__001 | core100 | Adapted | config_resolve_discover | 3/6 | 1 | 1 | 1 | 0 | 0 | 0 | pass | pass | pass | missing | public | public |
| email_validator__validate_core__001 | core100 | Direct | parse_tokenize_decode | 4/6 | 1 | 1 | 0 | 1 | 1 | 0 | pass | pass | public | pass | pass | isolation |
| environs__typed_env_core__001 | core100 | Direct | config_resolve_discover | 5/6 | 1 | 1 | 1 | 0 | 1 | 1 | pass | pass | pass | missing | pass | pass |
| faker__provider_core__001 | core100 | Direct | resource_metadata_loading | 3/6 | 1 | 1 | 1 | 0 | 0 | 0 | pass | pass | pass | isolation | public | public |
| filelock__reentrant_lock_core__001 | core100 | Adapted | workflow_session_orchestration | 0/6 | 0 | 0 | 0 | 0 | 0 | 0 | public | public | public | public | missing | public |
| flake8__plugin_options_core__hard3_001 | hard3 | Composite | registry_plugin_dispatch | 0/6 | 0 | 0 | 0 | 0 | 0 | 0 | public | public | public | missing | public | public |
| flask__route_dispatch_core__001 | core100 | Adapted | registry_plugin_dispatch | 0/6 | 0 | 0 | 0 | 0 | 0 | 0 | public | public | public | public | public | build |
| fs__url_opener_core__hard3_001 | hard3 | Adapted | registry_plugin_dispatch | 2/6 | 1 | 1 | 0 | 0 | 0 | 0 | pass | pass | public | public | public | public |
| fsspec__url_chain_core__hard3_001 | hard3 | Adapted | config_resolve_discover | 3/6 | 1 | 1 | 1 | 0 | 0 | 0 | pass | pass | pass | public | hidden | public |
| glom__spec_eval_core__hard3_001 | hard3 | Adapted | algorithm_data_structure | 2/6 | 1 | 0 | 1 | 0 | 0 | 0 | pass | hidden | pass | missing | hidden | public |
| h11__message_parse_core__001 | core100 | Direct | protocol_state_transition | 6/6 | 1 | 1 | 1 | 1 | 1 | 1 | pass | pass | pass | pass | pass | pass |
| h2__frame_parse_core__001 | core100 | Adapted | protocol_state_transition | 5/6 | 1 | 1 | 1 | 1 | 1 | 0 | pass | pass | pass | pass | pass | hidden |
| hatch__project_metadata_core__hard3_001 | hard3 | Adapted | resource_metadata_loading | 0/6 | 0 | 0 | 0 | 0 | 0 | 0 | public | public | public | public | public | missing |
| httpx__request_model_core__001 | core100 | Adapted | validate_normalize_construct | 4/6 | 1 | 1 | 1 | 1 | 0 | 0 | pass | pass | pass | pass | missing | public |
| humanize__naturaltime_core__001 | core100 | Direct | serialize_format_render | 6/6 | 1 | 1 | 1 | 1 | 1 | 1 | pass | pass | pass | pass | pass | pass |
| importlib_metadata__entry_points_core__001 | core100 | Direct | resource_metadata_loading | 4/6 | 1 | 1 | 1 | 1 | 0 | 0 | pass | pass | pass | pass | missing | public |
| importlib_resources__traversable_tree_core__hard3_001 | hard3 | Composite | resource_metadata_loading | 2/6 | 1 | 1 | 0 | 0 | 0 | 0 | pass | pass | hidden | build | hidden | hidden |
| installer__wheel_record_core__hard3_001 | hard3 | Adapted | resource_metadata_loading | 1/6 | 1 | 0 | 0 | 0 | 0 | 0 | pass | hidden | hidden | hidden | hidden | hidden |
| intervaltree__interval_tree_core__001 | core100 | Direct | algorithm_data_structure | 4/6 | 1 | 1 | 1 | 1 | 0 | 0 | pass | pass | pass | pass | missing | public |
| isodate__duration_parse_core__001 | core100 | Adapted | parse_tokenize_decode | 6/6 | 1 | 1 | 1 | 1 | 1 | 1 | pass | pass | pass | pass | pass | pass |
| isort__settings_resolver_core__hard3_001 | hard3 | Adapted | config_resolve_discover | 3/6 | 1 | 1 | 1 | 0 | 0 | 0 | pass | pass | pass | missing | missing | public |
| itsdangerous__timed_serializer_core__001 | core100 | Adapted | serialize_format_render | 4/6 | 1 | 1 | 1 | 0 | 0 | 1 | pass | pass | pass | public | hidden | pass |
| jinja2__compile_render_core__001 | core100 | Adapted | serialize_format_render | 6/6 | 1 | 1 | 1 | 1 | 1 | 1 | pass | pass | pass | pass | pass | pass |
| jinja2__extensions_core__001 | core100 | Adapted | registry_plugin_dispatch | 4/6 | 1 | 1 | 0 | 1 | 1 | 0 | pass | pass | public | pass | pass | build |
| jinja2__filters_tests_core__001 | core100 | Adapted | serialize_format_render | 5/6 | 1 | 1 | 1 | 1 | 1 | 0 | pass | pass | pass | pass | pass | public |
| jinja2__lexer_parser_core__001 | core100 | Adapted | parse_tokenize_decode | 3/6 | 1 | 1 | 1 | 0 | 0 | 0 | pass | pass | pass | public | public | public |
| jinja2__loader_inheritance_core__001 | core100 | Adapted | resource_metadata_loading | 5/6 | 1 | 1 | 1 | 0 | 1 | 1 | pass | pass | pass | missing | pass | pass |
| json5__parse_core__001 | core100 | Direct | parse_tokenize_decode | 5/6 | 1 | 1 | 1 | 1 | 1 | 0 | pass | pass | pass | pass | pass | public |
| json_logic__evaluator_core__hard3_001 | hard3 | Direct | cache_retry_policy | 3/6 | 0 | 1 | 1 | 0 | 0 | 1 | hidden | pass | pass | hidden | hidden | pass |
| jsonpath_ng__expression_eval_core__001 | core100 | Direct | parse_tokenize_decode | 4/6 | 1 | 1 | 1 | 1 | 0 | 0 | pass | pass | pass | pass | missing | build |
| jsonpointer__resolve_core__001 | core100 | Direct | parse_tokenize_decode | 6/6 | 1 | 1 | 1 | 1 | 1 | 1 | pass | pass | pass | pass | pass | pass |
| jsonschema__validator_core__001 | core100 | Direct | validate_normalize_construct | 5/6 | 1 | 1 | 1 | 1 | 0 | 1 | pass | pass | pass | pass | missing | pass |
| jupyter_core__paths_resolver_core__hard3_001 | hard3 | Adapted | config_resolve_discover | 0/6 | 0 | 0 | 0 | 0 | 0 | 0 | public | public | public | public | public | public |
| jupyter_server__extension_config_core__hard3_001 | hard3 | Composite | registry_plugin_dispatch | 2/6 | 1 | 0 | 0 | 1 | 0 | 0 | pass | hidden | hidden | pass | hidden | public |
| keyring__backend_select_core__hard3_001 | hard3 | Composite | registry_plugin_dispatch | 0/6 | 0 | 0 | 0 | 0 | 0 | 0 | public | public | hidden | public | missing | public |
| lark__grammar_loader_core__001 | core100 | Direct | resource_metadata_loading | 4/6 | 1 | 1 | 1 | 0 | 1 | 0 | pass | pass | pass | isolation | pass | build |
| lark__parse_tree_core__001 | core100 | Direct | parse_tokenize_decode | 3/6 | 1 | 1 | 0 | 1 | 0 | 0 | pass | pass | build | pass | build | build |
| lark__visitor_transform_core__001 | core100 | Adapted | algorithm_data_structure | 4/6 | 1 | 1 | 1 | 0 | 1 | 0 | pass | pass | pass | public | pass | public |
| license_expression__policy_core__hard3_001 | hard3 | Direct | parse_tokenize_decode | 0/6 | 0 | 0 | 0 | 0 | 0 | 0 | hidden | hidden | public | public | public | public |
| mako__lexer_expression_core__001 | core100 | Direct | parse_tokenize_decode | 4/6 | 1 | 1 | 1 | 1 | 0 | 0 | pass | pass | pass | pass | public | build |
| markdown__extensions_core__001 | core100 | Adapted | parse_tokenize_decode | 5/6 | 1 | 1 | 1 | 1 | 1 | 0 | pass | pass | pass | pass | pass | build |
| markdown_it__commonmark_render__001 | core100 | Direct | parse_tokenize_decode | 6/6 | 1 | 1 | 1 | 1 | 1 | 1 | pass | pass | pass | pass | pass | pass |
| marshmallow__schema_core__001 | core100 | Direct | serialize_format_render | 4/6 | 1 | 1 | 1 | 1 | 0 | 0 | pass | pass | pass | pass | missing | public |
| mkdocs__plugin_config_core__hard3_001 | hard3 | Composite | registry_plugin_dispatch | 0/6 | 0 | 0 | 0 | 0 | 0 | 0 | public | public | public | public | public | public |
| msgpack__pack_unpack_core__001 | core100 | Adapted | serialize_format_render | 4/6 | 1 | 1 | 1 | 1 | 0 | 0 | pass | pass | pass | pass | missing | build |
| multidict__multidict_mutation_core__hard3_001 | hard3 | Direct | algorithm_data_structure | 0/6 | 0 | 0 | 0 | 0 | 0 | 0 | public | public | public | public | public | public |
| networkx__dag_topo_core__001 | core100 | Direct | algorithm_data_structure | 4/6 | 1 | 1 | 1 | 0 | 1 | 0 | pass | pass | pass | missing | pass | public |
| packaging__requirement_marker_specifier__001 | core100 | Direct | parse_tokenize_decode | 5/6 | 1 | 1 | 1 | 1 | 1 | 0 | pass | pass | pass | pass | pass | build |
| parse__format_parser_core__001 | core100 | Direct | parse_tokenize_decode | 5/6 | 1 | 1 | 1 | 1 | 1 | 0 | pass | pass | pass | pass | pass | public |
| parsel__selector_namespace_core__hard3_001 | hard3 | Adapted | parse_tokenize_decode | 0/6 | 0 | 0 | 0 | 0 | 0 | 0 | public | public | public | public | missing | public |
| parso__python_parse_core__001 | core100 | Direct | parse_tokenize_decode | 5/6 | 1 | 1 | 1 | 1 | 1 | 0 | pass | pass | pass | pass | pass | public |
| passlib__hash_context_core__001 | core100 | Direct | validate_normalize_construct | 4/6 | 1 | 1 | 1 | 1 | 0 | 0 | pass | pass | pass | pass | hidden | hidden |
| pathvalidate__sanitize_core__001 | core100 | Direct | validate_normalize_construct | 4/6 | 1 | 1 | 1 | 1 | 0 | 0 | pass | pass | pass | pass | missing | hidden |
| pendulum__parse_format_core__001 | core100 | Adapted | parse_tokenize_decode | 3/6 | 1 | 0 | 1 | 1 | 0 | 0 | pass | public | pass | pass | public | public |
| phonenumbers__parse_format_core__001 | core100 | Direct | parse_tokenize_decode | 5/6 | 1 | 1 | 1 | 1 | 1 | 0 | pass | pass | pass | pass | pass | hidden |
| platformdirs__app_dirs_core__hard3_001 | hard3 | Adapted | config_resolve_discover | 1/6 | 0 | 0 | 1 | 0 | 0 | 0 | public | public | pass | public | missing | public |
| pluggy__hook_call_order__001 | core100 | Direct | registry_plugin_dispatch | 6/6 | 1 | 1 | 1 | 1 | 1 | 1 | pass | pass | pass | pass | pass | pass |
| pluggy__hook_specs_core__001 | core100 | Direct | registry_plugin_dispatch | 4/6 | 1 | 1 | 0 | 1 | 1 | 0 | pass | pass | missing | pass | pass | hidden |
| pluggy__hook_wrapper_core__hard3_001 | hard3 | Adapted | registry_plugin_dispatch | 0/6 | 0 | 0 | 0 | 0 | 0 | 0 | public | public | public | public | missing | public |
| poetry_core__dependency_groups_core__hard3_001 | hard3 | Composite | resource_metadata_loading | 0/6 | 0 | 0 | 0 | 0 | 0 | 0 | public | public | public | public | public | public |
| pydantic__field_validator_core__hard3_001 | hard3 | Adapted | validate_normalize_construct | 3/6 | 1 | 0 | 1 | 0 | 1 | 0 | pass | hidden | pass | missing | pass | public |
| pydantic_settings__env_source_core__001 | core100 | Adapted | config_resolve_discover | 4/6 | 1 | 1 | 1 | 0 | 1 | 0 | pass | pass | pass | build | pass | public |
| pydantic_v1__validation_error_core__001 | core100 | Adapted | validate_normalize_construct | 3/6 | 1 | 1 | 1 | 0 | 0 | 0 | pass | pass | pass | missing | missing | public |
| pygments__formatter_core__001 | core100 | Direct | serialize_format_render | 5/6 | 1 | 1 | 1 | 1 | 0 | 1 | pass | pass | pass | pass | public | pass |
| pygments__lexer_core__001 | core100 | Direct | parse_tokenize_decode | 0/6 | 0 | 0 | 0 | 0 | 0 | 0 | hidden | hidden | build | hidden | missing | public |
| pyramid__configurator_action_core__hard3_001 | hard3 | Composite | workflow_session_orchestration | 6/6 | 1 | 1 | 1 | 1 | 1 | 1 | pass | pass | pass | pass | pass | pass |
| pytest__fixture_resolve_core__001 | core100 | Composite | registry_plugin_dispatch | 4/6 | 1 | 1 | 1 | 0 | 1 | 0 | pass | pass | pass | public | pass | public |
| pytest__ini_markers_core__001 | core100 | Composite | config_resolve_discover | 0/6 | 0 | 0 | 0 | 0 | 0 | 0 | public | public | public | missing | hidden | public |
| pytest__mark_expression_core__001 | core100 | Adapted | parse_tokenize_decode | 6/6 | 1 | 1 | 1 | 1 | 1 | 1 | pass | pass | pass | pass | pass | pass |
| pytest__marker_registry_core__hard3_001 | hard3 | Composite | registry_plugin_dispatch | 0/6 | 0 | 0 | 0 | 0 | 0 | 0 | hidden | hidden | hidden | hidden | hidden | hidden |
| pytest__skipif_eval_core__001 | core100 | Composite | cache_retry_policy | 5/6 | 1 | 1 | 1 | 0 | 1 | 1 | pass | pass | pass | hidden | pass | pass |
| python_box__config_box_core__001 | core100 | Direct | config_resolve_discover | 5/6 | 1 | 1 | 1 | 1 | 1 | 0 | pass | pass | pass | pass | pass | hidden |
| python_dateutil__relativedelta_core__001 | core100 | Direct | algorithm_data_structure | 4/6 | 1 | 0 | 1 | 1 | 1 | 0 | pass | public | pass | pass | pass | hidden |
| python_dateutil__rrule_core__001 | core100 | Direct | protocol_state_transition | 5/6 | 1 | 1 | 1 | 1 | 1 | 0 | pass | pass | pass | pass | pass | public |
| python_decouple__config_repository_core__001 | core100 | Adapted | config_resolve_discover | 0/6 | 0 | 0 | 0 | 0 | 0 | 0 | hidden | hidden | hidden | hidden | hidden | hidden |
| python_dotenv__env_parse_core__001 | core100 | Direct | config_resolve_discover | 6/6 | 1 | 1 | 1 | 1 | 1 | 1 | pass | pass | pass | pass | pass | pass |
| python_frontmatter__roundtrip_core__001 | core100 | Direct | serialize_format_render | 6/6 | 1 | 1 | 1 | 1 | 1 | 1 | pass | pass | pass | pass | pass | pass |
| python_multipart__form_parse_core__001 | core100 | Direct | parse_tokenize_decode | 6/6 | 1 | 1 | 1 | 1 | 1 | 1 | pass | pass | pass | pass | pass | pass |
| pyyaml__safe_load_dump__001 | core100 | Adapted | serialize_format_render | 5/6 | 1 | 1 | 1 | 1 | 1 | 0 | pass | pass | pass | pass | pass | build |
| readme_renderer__content_type_core__hard3_001 | hard3 | Adapted | serialize_format_render | 0/6 | 0 | 0 | 0 | 0 | 0 | 0 | public | public | public | public | build | build |
| redis__resp_parser_core__001 | core100 | Adapted | protocol_state_transition | 5/6 | 1 | 1 | 1 | 1 | 1 | 0 | pass | pass | pass | pass | pass | public |
| referencing__json_schema_refs_core__001 | core100 | Adapted | config_resolve_discover | 5/6 | 1 | 1 | 1 | 1 | 1 | 0 | pass | pass | pass | pass | pass | public |
| requests_cache__cache_key_core__hard3_001 | hard3 | Composite | cache_retry_policy | 0/6 | 0 | 0 | 0 | 0 | 0 | 0 | hidden | hidden | hidden | public | hidden | public |
| responses__request_matcher_core__hard3_001 | hard3 | Composite | registry_plugin_dispatch | 1/6 | 0 | 0 | 1 | 0 | 0 | 0 | hidden | hidden | pass | hidden | hidden | public |
| returns__result_pipeline_core__hard3_001 | hard3 | Adapted | workflow_session_orchestration | 5/6 | 1 | 1 | 1 | 1 | 0 | 1 | pass | pass | pass | pass | hidden | pass |
| rfc3986__uri_parse_core__001 | core100 | Adapted | parse_tokenize_decode | 6/6 | 1 | 1 | 1 | 1 | 1 | 1 | pass | pass | pass | pass | pass | pass |
| rich__markup_parse_core__001 | core100 | Adapted | parse_tokenize_decode | 3/6 | 1 | 1 | 0 | 0 | 1 | 0 | pass | pass | missing | missing | pass | build |
| ruamel_yaml__roundtrip_core__001 | core100 | Adapted | serialize_format_render | 5/6 | 1 | 1 | 1 | 1 | 1 | 0 | pass | pass | pass | pass | pass | public |
| schema__nested_validate_core__hard3_001 | hard3 | Adapted | validate_normalize_construct | 4/6 | 0 | 1 | 1 | 1 | 0 | 1 | hidden | pass | pass | pass | hidden | pass |
| scrapy__item_loader_core__hard3_001 | hard3 | Adapted | registry_plugin_dispatch | 0/6 | 0 | 0 | 0 | 0 | 0 | 0 | public | public | public | public | public | public |
| setuptools_scm__version_normalize_core__hard3_001 | hard3 | Adapted | resource_metadata_loading | 0/6 | 0 | 0 | 0 | 0 | 0 | 0 | public | public | public | missing | public | public |
| sortedcontainers__sorted_list_core__001 | core100 | Direct | algorithm_data_structure | 4/6 | 1 | 1 | 1 | 1 | 0 | 0 | pass | pass | pass | pass | hidden | public |
| sphinx__extension_registry_core__hard3_001 | hard3 | Composite | registry_plugin_dispatch | 5/6 | 1 | 1 | 1 | 1 | 0 | 1 | pass | pass | pass | pass | public | pass |
| sqlalchemy__event_dispatch_core__hard3_001 | hard3 | Adapted | registry_plugin_dispatch | 5/6 | 1 | 1 | 1 | 0 | 1 | 1 | pass | pass | pass | missing | pass | pass |
| sqlparse__format_filters_core__001 | core100 | Direct | serialize_format_render | 4/6 | 1 | 1 | 0 | 1 | 1 | 0 | pass | pass | hidden | pass | pass | public |
| sqlparse__parse_format_core__001 | core100 | Adapted | parse_tokenize_decode | 3/6 | 1 | 1 | 1 | 0 | 0 | 0 | pass | pass | pass | missing | build | build |
| sqlparse__parse_split_core__001 | core100 | Adapted | parse_tokenize_decode | 4/6 | 1 | 1 | 1 | 0 | 1 | 0 | pass | pass | pass | missing | pass | public |
| sqlparse__token_tree_core__001 | core100 | Adapted | parse_tokenize_decode | 3/6 | 1 | 1 | 1 | 0 | 0 | 0 | pass | pass | pass | missing | missing | build |
| starlette__route_matching_core__hard3_001 | hard3 | Adapted | registry_plugin_dispatch | 0/6 | 0 | 0 | 0 | 0 | 0 | 0 | hidden | hidden | hidden | missing | hidden | public |
| stevedore__extension_manager_core__hard3_001 | hard3 | Composite | registry_plugin_dispatch | 4/6 | 1 | 1 | 1 | 0 | 1 | 0 | pass | pass | pass | missing | pass | public |
| tabulate__table_format_core__001 | core100 | Direct | serialize_format_render | 3/6 | 1 | 1 | 1 | 0 | 0 | 0 | pass | pass | pass | missing | public | build |
| tenacity__retry_state_core__hard3_001 | hard3 | Adapted | cache_retry_policy | 2/6 | 1 | 0 | 1 | 0 | 0 | 0 | pass | hidden | pass | missing | missing | missing |
| tomlkit__roundtrip_document__001 | core100 | Direct | serialize_format_render | 5/6 | 1 | 1 | 1 | 0 | 1 | 1 | pass | pass | pass | missing | pass | pass |
| tox__factor_expression_core__hard3_001 | hard3 | Adapted | parse_tokenize_decode | 1/6 | 0 | 0 | 0 | 0 | 0 | 1 | public | public | public | missing | missing | pass |
| trafaret__validation_rules_core__hard3_001 | hard3 | Adapted | validate_normalize_construct | 4/6 | 1 | 1 | 1 | 0 | 0 | 1 | pass | pass | pass | missing | missing | pass |
| transitions__state_machine_core__hard3_001 | hard3 | Adapted | protocol_state_transition | 4/6 | 1 | 1 | 1 | 0 | 1 | 0 | pass | pass | pass | missing | pass | hidden |
| typer__command_parser_core__001 | core100 | Direct | workflow_session_orchestration | 2/6 | 1 | 0 | 1 | 0 | 0 | 0 | pass | isolation | pass | missing | public | public |
| urllib3__retry_backoff_core__001 | core100 | Direct | cache_retry_policy | 4/6 | 1 | 1 | 1 | 0 | 1 | 0 | pass | pass | pass | missing | pass | hidden |
| virtualenv__interpreter_spec_core__hard3_001 | hard3 | Adapted | parse_tokenize_decode | 1/6 | 0 | 1 | 0 | 0 | 0 | 0 | public | pass | hidden | missing | missing | public |
| voluptuous__schema_validate_core__001 | core100 | Direct | validate_normalize_construct | 4/6 | 1 | 1 | 1 | 0 | 1 | 0 | pass | pass | pass | missing | pass | hidden |
| websockets__handshake_parse_core__001 | core100 | Adapted | protocol_state_transition | 3/6 | 1 | 1 | 1 | 0 | 0 | 0 | pass | pass | pass | missing | public | hidden |
| werkzeug__routing_core__001 | core100 | Adapted | registry_plugin_dispatch | 4/6 | 1 | 1 | 1 | 0 | 1 | 0 | pass | pass | pass | missing | pass | public |
| wheel__metadata_normalize_core__hard3_001 | hard3 | Adapted | resource_metadata_loading | 4/6 | 1 | 1 | 1 | 0 | 1 | 0 | pass | pass | pass | missing | pass | hidden |
| wsproto__frame_parse_core__001 | core100 | Adapted | protocol_state_transition | 5/6 | 1 | 1 | 1 | 0 | 1 | 1 | pass | pass | pass | missing | pass | pass |
| xmltodict__xml_parse_core__001 | core100 | Direct | serialize_format_render | 4/6 | 1 | 1 | 1 | 0 | 1 | 0 | pass | pass | pass | missing | pass | hidden |
| yamale__schema_validate_core__hard3_001 | hard3 | Adapted | validate_normalize_construct | 0/6 | 0 | 0 | 0 | 0 | 0 | 0 | public | public | public | missing | missing | build |
| yarl__url_model_core__001 | core100 | Adapted | parse_tokenize_decode | 3/6 | 1 | 1 | 1 | 0 | 0 | 0 | pass | pass | pass | missing | public | hidden |

---

## 11. 可直接写进论文的 Finding

**F1.** Current coding agents exhibit substantial but incomplete feature-lifting capability on frozen Python-150, with large performance differences across model backends (24.0%–76.7%). The strongest backend still fails 35/150 tasks; 28 tasks are unsolved by every backend.

**F2.** Functional failures concentrate at the behavioral gates. Among delivered packages, independent isolation failure after passing build, public, and hidden checks occurs only 4 times across six models × 150 tasks. Independence is rarely the binding constraint; preserving complete behavior is.

**F3.** On the Pro+Flash artifact-fail slice (n=63 valid agent rows), L1 close-read is dominated by incomplete recovery of the required behavioral contract rather than by missing packages or uninspected source trees. This remains an assistant-first-pass analysis, not a gold taxonomy.

**F4.** Feature-lifting difficulty on Python-150 is identified by the in-suite hard3 construction split (Pro 94/100 vs 21/50). After controlling for model and hard3, Composite is not significantly harder than Direct (OR=0.65, p=0.554). The apparent Direct → Adapted → Composite gradient is confounded with construction-split composition (Composite is 15/18 hard3; Direct is 53/56 Core) and is not an independent benchmark finding.

**F5.** Comparable functional success conceals systematically different extraction strategies. On the 97 tasks passed by both Pro and Luna, median copy fraction is 0.966 vs 0.191 (Wilcoxon p=1.2e-13, matched-pairs rank-biserial r=0.88).
