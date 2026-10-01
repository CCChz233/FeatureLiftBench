# Claude paired Full Source and Contract Only

Full 89/150, Contract 53/150.
both 40, full_only 49, contract_only 13, neither 48.
Delta 24.0 pp, 95% paired task bootstrap [14.7, 33.3].
Exact McNemar p 4.818e-06; Holm across four configurations 4.818e-06.
Capsule mismatches: 0.

| Configuration | Only Full | Only Contract | Raw p | Holm p (four tests) |
| --- | ---: | ---: | ---: | ---: |
| GPT-5.6 Luna | 56 | 8 | 5.563e-10 | 1.113e-09 |
| DeepSeek V4 Pro | 88 | 4 | 1.181e-21 | 4.724e-21 |
| Qwen3.6-35B-A3B | 59 | 3 | 1.725e-14 | 5.175e-14 |
| Claude Sonnet 5 | 49 | 13 | 4.818e-06 | 4.818e-06 |
