# Results draft: Python-200′ DeepSeek V4 Flash candidate

> **Draft status: audit-ready candidate; replace bracketed eligibility language after strict replacement runs.**

## Main result is not yet leaderboard-eligible

The received OpenHands suite records 132 functional passes across 200 selected tasks
(66.0%; Wilson 95% 59.2%–72.2%). We do not report
this value as the Python-200′ leaderboard result. Although all task IDs match the registered
selection, 17 Python-150 tasks were rejected before agent launch by a freeze-spec hash check,
16 Hard-50 tasks failed offline dependency installation, and 59 attempted runs exceeded the
configured prompt allowance. Their union contains 84 tasks.

## Infrastructure accounts for nearly half of nominal non-passes

The received package contains 68 nominal non-passes. Of these,
33 (48.5%)
are infrastructure outcomes: 17 freeze-preflight blocks and 16 unavailable-dependency failures.
The remaining model/output evidence comprises two runs with no submission, 25 first failing public
tests, and eight passing public tests but failing hidden tests. No task first fails isolation.
This separation prevents execution-environment failures from being interpreted as model capability.

## Raw split rates are confounded

The raw package yields 103/150 (68.7%) on
Python-150 and 29/50 (58.0%) on Hard-50. These rates
must not be used as a clean difficulty comparison: the 17 freeze blocks occur only in Python-150,
whereas all 16 dependency-install failures occur in Hard-50. The independent Hard-50 calibration
remains benchmark-design evidence; the new full-suite comparison awaits the frozen replacement set.

## Taxonomy and compactness analyses are prepared but provisional

The received outcomes show Direct 60/68, Adapted 63/100, and Composite 9/32. Pass-conditioned
median RRES differs sharply by split (Python-150 0.990; Hard-50 0.286). We retain these cuts as
analysis specifications rather than final findings because replacement outcomes may change the
composition. Final reporting will preserve split-specific RRES and use paired subsets for method or
cross-model comparisons.

## Eligibility sensitivity and next step

After freezing the 84-task replacement union, the untouched subset
contains 95 passes among 116
tasks. The logical final range before replacement is
95/200–179/200;
this is a stress bound, not an estimate. The final table will merge replacement outcomes for the
frozen union with original outcomes for all other task IDs and will retain both provenance layers.
