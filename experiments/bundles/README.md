# Experiment bundles

实验传输包的落地区。原始压缩包通常很大，默认不进 Git；校验和与说明文件进 Git。

- 新收到且尚未确认的包放 `incoming/`。
- 导入前检查压缩包成员，拒绝绝对路径和 `..` 路径穿越。
- 导入后保留原包与 SHA-256，原始 run 放回其规范的 track/model/run 目录。
- bundle 只是传输副本，不参与指标扫描。
