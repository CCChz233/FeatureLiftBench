# Design card: tldextract__suffix_resolve_core__001

**status:** `design_card_ready`  
**wave:** W3  
**package:** `tldextract`  
**repository_url:** https://github.com/john-kurkowski/tldextract  
**planned_lift_type:** Composite  
**final_lift_type:** Composite  
**reclassification_reason:** None  
**feature_family:** resource_metadata_loading  
**entanglement:** resource_coupling  
**feature_one_liner:** Public suffix list + extract + cache  
**lift_review_flag:** none

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/archive/plans/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.TLDExtract(cache_dir=False|path, suffix_list_urls=()) -> callable extractor"
  - "extractor(url: str) -> ExtractResult(subdomain, domain, suffix, ...)"
  - "featurelifted.extract(url) convenience if included"
returns:
  - "ExtractResult fields"
exceptions:
  - "declare"
defaults:
  - "cache_dir=False; suffix_list_urls=() to force packaged list"
state_effects:
  - "optional disk cache \u2014 disable in tests"
```

## upstream_mapping

```yaml
primary_symbols:
  - "tldextract.TLDExtract"
  - "tldextract.extract"
supporting_components:
  - "public suffix list data packaged"
semantic_delta:
  - "suffix data resource + extract logic"
```

## oracle_basis

```yaml
basis: mixed
notes: |
  Must disable network suffix fetch; use bundled list.
```

## scope

```yaml
included:
  - "extract domain parts for HTTP URLs and hosts"
excluded:
  - "live PSL download"
```

## feasibility

```yaml
commit: null  # resolve at pin/materialize
license: "BSD-3-Clause"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "suffix_list_urls empty; no HTTP"
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

- Staging path: `benchmark/staging/tldextract__suffix_resolve_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
