# Go Candidate Backlog

**最后更新：** 2026-07-03

Go track 选题台账。Repo 级政策见 [GO_REPO_SELECTION.md](GO_REPO_SELECTION.md)；执行见 [GO_PILOT_PLAYBOOK.md](GO_PILOT_PLAYBOOK.md)。

**状态：** `idea` → `shortlist` → `staging` → `accepted` | `dropped` | `redesign`

---

## 进度摘要

| 指标 | 目标 | 当前 |
| --- | ---: | ---: |
| Gold tasks | 10 | **10** |
| Staging | — | 0 |
| Shortlist | 5（pilot 队列） | 5（已 promote） |

---

## P0 — Pilot 队列（建议 Phase 1–2 顺序）

| task_id（拟） | Repo | Feature slice | Entanglement | 状态 | 备注 |
| --- | --- | --- | --- | --- | --- |
| `semver__version_parse_core__001` | [Masterminds/semver](https://github.com/Masterminds/semver) | 版本解析与比较 | parser + internal normalize | **accepted** | pilot 深度参考题 |
| `humanize__bytes_format_core__001` | [dustin/go-humanize](https://github.com/dustin/go-humanize) | 字节/时间人性化格式化 | 多文件 format + locale tables | **accepted** | gold |
| `bluemonday__sanitize_policy_core__001` | [microcosm-cc/bluemonday](https://github.com/microcosm-cc/bluemonday) | HTML sanitize 策略核心 | policy registry + parser | **accepted** | gold |
| `gojsonschema__validate_core__001` | [xeipuuv/gojsonschema](https://github.com/xeipuuv/gojsonschema) | JSON Schema 校验子集 | reference resolver + types | **accepted** | gold |
| `mapstructure__decode_core__001` | [go-viper/mapstructure](https://github.com/go-viper/mapstructure) | struct map 解码 | hooks + tag reflection | **accepted** | gold |

---

## P1 — 备选（gold 6–10）

| task_id（拟） | Repo | Feature slice | 状态 |
| --- | --- | --- | --- |
| `validator__struct_validate_core__001` | [go-playground/validator](https://github.com/go-playground/validator) | 结构体 tag 校验 | **accepted** |
| `copier__deep_copy_core__001` | [jinzhu/copier](https://github.com/jinzhu/copier) | 深拷贝 | **accepted** |
| `expr__eval_core__001` | [expr-lang/expr](https://github.com/expr-lang/expr) | 表达式求值 | **accepted** |
| `doublestar__glob_match_core__001` | [bmatcuk/doublestar](https://github.com/bmatcuk/doublestar) | glob 匹配 | **accepted** |
| `uuid__parse_format_core__001` | [google/uuid](https://github.com/google/uuid) | UUID 解析/格式化 | **accepted** |
| `blackfriday__markdown_inline_core__001` | [russross/blackfriday/v2](https://github.com/russross/blackfriday) | inline markdown | idea |
| `yaml__unmarshal_subset__001` | [go-yaml/yaml](https://github.com/go-yaml/yaml) | 解析子集 | idea |
| `uuid__parse_format_core__001` | [google/uuid](https://github.com/google/uuid) | UUID 解析/格式化 | idea |
| `errors__wrap_unwrap_core__001` | [pkg/errors](https://github.com/pkg/errors) | 错误包装语义 | idea |

---

## P2 — Phase 3 候选池（目标 60+ repo）

| Repo | 备注 |
| --- | --- |
| [spf13/cobra](https://github.com/spf13/cobra) | CLI；需 library slice |
| [gorilla/mux](https://github.com/gorilla/mux) | 路由 |
| [stretchr/testify](https://github.com/stretchr/testify) | reuse 弱 |
| [etcd-io/bbolt](https://github.com/etcd-io/bbolt) | 范围大 |
| [prometheus/client_golang](https://github.com/prometheus/client_golang) | 指标 |
| [sirupsen/logrus](https://github.com/sirupsen/logrus) | 日志 |
| [uber-go/zap](https://github.com/uber-go/zap) | 日志 |
| [rs/zerolog](https://github.com/rs/zerolog) | 日志 |
| [go-resty/resty](https://github.com/go-resty/resty) | 网络；谨慎 |
| [valyala/fasthttp](https://github.com/valyala/fasthttp) | 网络；谨慎 |
| [golang-jwt/jwt](https://github.com/golang-jwt/jwt) | JWT |
| [golang/crypto](https://github.com/golang/crypto) | 加密子集 |
| [tidwall/gjson](https://github.com/tidwall/gjson) | JSON 路径 |
| [tidwall/sjson](https://github.com/tidwall/sjson) | JSON 设置 |
| [pelletier/go-toml](https://github.com/pelletier/go-toml) | TOML |
| [BurntSushi/toml](https://github.com/BurntSushi/toml) | TOML |
| [gopkg.in/yaml.v3](https://github.com/go-yaml/yaml) | YAML |
| [russross/blackfriday/v2](https://github.com/russross/blackfriday) | Markdown |
| [yuin/goldmark](https://github.com/yuin/goldmark) | Markdown |
| [asaskevich/govalidator](https://github.com/asaskevich/govalidator) | 校验 |
| [gookit/validate](https://github.com/gookit/validate) | 校验 |
| [hashicorp/hcl](https://github.com/hashicorp/hcl) | HCL |
| [hashicorp/go-version](https://github.com/hashicorp/go-version) | 版本 |
| [hashicorp/go-multierror](https://github.com/hashicorp/go-multierror) | 错误 |
| [pkg/errors](https://github.com/pkg/errors) | 错误 |
| [samber/lo](https://github.com/samber/lo) | 集合 |
| [mitchellh/mapstructure](https://github.com/mitchellh/mapstructure) | 历史 mapstructure |
| [spf13/viper](https://github.com/spf13/viper) | 配置 |
| [spf13/cast](https://github.com/spf13/cast) | 类型转换 |
| [spf13/afero](https://github.com/spf13/afero) | 文件抽象 |
| [olekukonko/tablewriter](https://github.com/olekukonko/tablewriter) | 表格 |
| [jinzhu/now](https://github.com/jinzhu/now) | 时间 |
| [araddon/dateparse](https://github.com/araddon/dateparse) | 时间解析 |
| [go-playground/universal-translator](https://github.com/go-playground/universal-translator) | i18n |
| [go-playground/locales](https://github.com/go-playground/locales) | locale |
| [klauspost/compress](https://github.com/klauspost/compress) | 压缩 |
| [andybalholm/brotli](https://github.com/andybalholm/brotli) | 压缩 |
| [minio/md5-simd](https://github.com/minio/md5-simd) | hash |
| [cespare/xxhash](https://github.com/cespare/xxhash) | hash |
| [dgryski/go-rendezvous](https://github.com/dgryski/go-rendezvous) | hash |
| [golang/groupcache](https://github.com/golang/groupcache) | 缓存 |
| [patrickmn/go-cache](https://github.com/patrickmn/go-cache) | 缓存 |
| [coocood/freecache](https://github.com/coocood/freecache) | 缓存 |
| [bluele/gcache](https://github.com/bluele/gcache) | 缓存 |
| [workiva/go-datastructures](https://github.com/workiva/go-datastructures) | 数据结构 |
| [emirpasic/gods](https://github.com/emirpasic/gods) | 数据结构 |
| [ahmetb/go-linq](https://github.com/ahmetb/go-linq) | LINQ 风格 |
| [syyongx/php2go](https://github.com/syyongx/php2go) | 工具 |
| [goware/urlx](https://github.com/goware/urlx) | URL |
| [PuerkitoBio/purell](https://github.com/PuerkitoBio/purell) | URL |
| [gobwas/glob](https://github.com/gobwas/glob) | glob |
| [ryanuber/go-glob](https://github.com/ryanuber/go-glob) | glob |
| [golang/snappy](https://github.com/golang/snappy) | 压缩 |
| [mailru/easyjson](https://github.com/mailru/easyjson) | JSON |
| [json-iterator/go](https://github.com/json-iterator/go) | JSON |
| [buger/jsonparser](https://github.com/buger/jsonparser) | JSON |
| [itchyny/gojq](https://github.com/itchyny/gojq) | jq |
| [oliveagle/jsonpath](https://github.com/oliveagle/jsonpath) | JSONPath |
| [a8m/rql](https://github.com/a8m/rql) | 查询 |
| [xo/terminfo](https://github.com/xo/terminfo) | 终端 |
| [mattn/go-runewidth](https://github.com/mattn/go-runewidth) | 宽度 |
| [rivo/uniseg](https://github.com/rivo/uniseg) | Unicode |
| [golang/freetype](https://github.com/golang/freetype) | 字体；范围 |
| [disintegration/imaging](https://github.com/disintegration/imaging) | 图像；cgo 风险 |
| [nfnt/resize](https://github.com/nfnt/resize) | 图像 |

*合计 60+ repo 候选；promote 前须逐题 repo gate + design spike。*

---

## Dropped / 暂缓

| 项 | 原因 |
| --- | --- |
| （暂无） | — |

---

## 更新规则

1. promote 后：`status=accepted`，填入正式 `task_id` 与 commit
2. drop 后：写 **原因** 一行，避免重复尝试
3. redesign：保留行，增加 `attempt` 备注

---

## 相关

- [go_task_designs/TEMPLATE.md](go_task_designs/TEMPLATE.md)
- [GO_EXPANSION.md](GO_EXPANSION.md)
