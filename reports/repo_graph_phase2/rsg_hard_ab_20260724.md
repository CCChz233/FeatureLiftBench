# RSG hard3 A/B — P0 vs tuned_hard (2026-07-24)

Real DeepSeek v4 flash + OpenHands (`featureliftbench-agent:openhands-rsg-pilot-v1`).

**Root:** `experiments/rsg_pilot/openhands/deepseek-v4-flash/hard-ab-20260724-073447`

**Arms**

- `p0` = `openhands_deepseek_v4_flash_rsg_pilot_p0` (`rsg_bootstrap=tool_only`)
- `tuned` = `openhands_deepseek_v4_flash_rsg_tuned_hard` (`auto_support`, budget 5k)

## Results

| task | arm | status | public | hidden | tokens | steps | files | loc | optional `flb-rsg` |
|------|-----|--------|--------|--------|--------|-------|-------|-----|--------------------|
| transitions__state_machine_core__hard3_001 | p0 | failed | ✓ | ✗ | 591,741 | 25 | 2 | 1100 | no |
| transitions__state_machine_core__hard3_001 | tuned | failed | ✓ | ✗ | 1,232,064 | 28 | 2 | 664 | yes (`support`) |
| isort__settings_resolver_core__hard3_001 | p0 | failed | ✓ | ✗ | 1,310,798 | 39 | 7 | 797 | no |
| isort__settings_resolver_core__hard3_001 | tuned | failed | ✓ | ✗ | 1,764,904 | 49 | 9 | 1282 | yes (`support`) |
| scrapy__item_loader_core__hard3_001 | p0 | failed | ✓ | ✗ | 1,800,677 | 44 | 4 | 312 | no |
| scrapy__item_loader_core__hard3_001 | tuned | failed | ✓ | ✗ | 2,041,586 | 47 | 7 | 408 | no (bootstrap only) |

All six: `build∧public` pass, `hidden` fail → `final_score=0`.

## Takeaways

1. **Pass rate:** tuned_hard **0/3**, P0 **0/3** — no lift on these hard3 tasks.
2. **Tokens:** tuned higher on every pair (+108% / +35% / +13%).
3. **Mechanism:** support tools were used on transitions + isort; still same public✓/hidden✗ failure mode.
4. **Compactness:** mixed (transitions loc↓; isort extraction_ratio >1 on tuned).

Hard failures here look like **API/behavior closure for hidden tests**, not “couldn’t find the files” — RSG start-here does not appear to be the bottleneck.
