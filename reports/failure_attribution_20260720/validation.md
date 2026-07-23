# Validation

**Status: PASS — 27/27 checks passed.**

| Check | Status | Detail |
|---|---|---|
| base row count | PASS | observed=550 |
| audit row count | PASS | observed=550 |
| unique run ids | PASS | observed=550 |
| model-task grain | PASS | expected=550 |
| token identity | PASS | all rows |
| formal passes | PASS | observed=225 |
| public passes | PASS | observed=401 |
| hidden passes | PASS | observed=228 |
| evaluator coverage | PASS | observed=533 |
| failure stages sum | PASS | stage_sum=325 |
| infrastructure failures | PASS | expected=62 |
| condensation runs | PASS | observed=288 |
| condensation events | PASS | observed=552 |
| clean install executions | PASS | observed=0 |
| context windows | PASS | observed=[131072, 204800] |
| dynamic group coverage | PASS | {False: {'size': 118, 'sum': 47}, True: {'size': 432, 'sum': 178}} |
| representative case count | PASS | expected=16 |
| module priority counts | PASS | observed={'Semantic closure planner': 85, 'Implementation and repair loop': 80, 'Budgeted exploration scheduler': 32, 'Targeted runtime semantics engine': 43, 'Boundary and packaging planner': 15, 'Verification state machine': 2, 'Evidence memory and condenser': 2, 'Localization': 5} |
| module ceiling arithmetic | PASS | ceiling=direct_failures/550*100 |
| PoC threshold arithmetic | PASS | 20% recovery column is a scenario, not a forecast |
| module artifact coverage | PASS | observed=8 |
| cold-start observed entry coverage | PASS | observed=523 |
| cold-start within-five count | PASS | expected=475 |
| explicit closure plans | PASS | observed=62 |
| notebook executed | PASS | code_cells=9 |
| notebook error free | PASS | errors=0 |
| no obvious secrets | PASS | scanned md/csv/json outputs |

The validation establishes arithmetic, coverage, notebook execution, and output hygiene. It does not validate the causal truth of heuristic stage labels; that requires blinded human adjudication and interventions.
