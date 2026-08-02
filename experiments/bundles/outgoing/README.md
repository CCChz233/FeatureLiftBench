# Outgoing bundles

本机打出的传输包（默认不进 Git；`*.sha256` 可进 Git）。

生成可跑整包：

```bash
./scripts/build_runnable_bundle.sh
```

`build_runnable_bundle.sh` 只从当前 `HEAD` 的已提交文件构建，并在压缩前
强制通过 source、selection、dependency、wheel 与 freeze 检查。工作树中
未提交的方法开发改动不会进入 bundle。

重建已冻结的 Python-150 v3 release（freeze `846b8147...`）：

```bash
./scripts/build_v3_846_release_bundle.sh
```

该脚本固定 hardened base 与 freeze 修复 revision，只额外复制本机
canonical source archives 和 oracle trees；不会打包 `.env` 或
`harness/config/agents.toml`。
