# Design card: vcrpy__cassette_match_core__001

**status:** `design_card_ready`  
**wave:** W3  
**package:** `vcrpy`  
**repository_url:** https://github.com/kevin1024/vcrpy  
**planned_lift_type:** Composite  
**final_lift_type:** Composite  
**reclassification_reason:** None  
**feature_family:** protocol_state_transition  
**entanglement:** framework_coupling  
**feature_one_liner:** Cassette record/match/replay without network  
**lift_review_flag:** none

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/archive/plans/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.use_cassette(path, matcher=..., record_mode='none')"
  - "featurelifted.matchers method/uri/host/path/query subset"
  - "featurelifted.VCR(record_mode=..., match_on=...)"
returns:
  - "cassette context restores recorded responses"
exceptions:
  - "CannotOverwriteExistingCassetteException; network errors if misconfigured"
defaults:
  - "record_mode='none' in tests"
state_effects:
  - "patches HTTP libs \u2014 only urllib/stdlib in tests"
```

## upstream_mapping

```yaml
primary_symbols:
  - "vcr.VCR"
  - "vcr.use_cassette"
supporting_components:
  - "vcr.matchers"
  - "vcr.cassette"
semantic_delta:
  - "matchers + cassette store + replay"
```

## oracle_basis

```yaml
basis: mixed
notes: |
  Ship cassette fixtures; never record online in CI.
```

## scope

```yaml
included:
  - "replay cassette, match_on uri/method, custom matcher registration"
excluded:
  - "recording against internet, selenium"
```

## feasibility

```yaml
commit: null  # resolve at pin/materialize
license: "MIT"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "pre-recorded cassettes only"
```

## acceptance

```yaml
closure_review: pending
reference_pass: pending
isolation_pass: pending
no_original_import: pending
overlap_check: pending
```

## agent_notes

- Staging path: `benchmark/staging/vcrpy__cassette_match_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
