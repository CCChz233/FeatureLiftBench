# Python-200′ candidate paper tables

> **Status: internal candidate tables · Not eligible for the final leaderboard**

## Received-suite audit headline

| Scope | Functional passes | Assigned | Raw rate | Eligibility |
| --- | --- | --- | --- | --- |
| Python-150 | 103 | 150 | 68.7% | 17 preflight blocks; context audit open |
| Hard-50 | 29 | 50 | 58.0% | 16 dependency failures; context audit open |
| Python-200′ | 132 | 200 | 66.0% | candidate blocked |

Do not caption this as a leaderboard table. It reports the received package exactly, including infrastructure outcomes.

## Eligibility partition

| Partition | Tasks | Passes | Treatment |
| --- | --- | --- | --- |
| Fixed clean subset | 116 | 95 | retain |
| Strict replacement union | 84 | unknown | replace by frozen task ID |
| Total | 200 | unknown | final score after replacement |

The replacement union contains 59 context violations, 17 freeze-preflight blocks, and 16 dependency failures with overlap removed. The fixed subset is 95/116; this is not a standalone benchmark score.

## Failure attribution for discussion

| Outcome | Tasks | Claim class |
| --- | --- | --- |
| No submission | 2 | model/output |
| Offline dependency unavailable | 16 | infrastructure |
| Freeze preflight blocked | 17 | infrastructure |
| Hidden-only behavior | 8 | model/output |
| Public behavior | 25 | model/output |
