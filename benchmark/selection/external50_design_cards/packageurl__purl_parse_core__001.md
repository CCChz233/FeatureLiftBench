# Design card: packageurl__purl_parse_core__001

**status:** `design_card_ready`  
**wave:** W4  
**package:** `packageurl-python`  
**repository_url:** https://github.com/package-url/packageurl-python  
**planned_lift_type:** Adapted  
**final_lift_type:** Adapted  
**reclassification_reason:** None  
**feature_family:** parse_tokenize_decode  
**entanglement:** data_model_coupling  
**feature_one_liner:** PackageURL parse/to_string normalize  
**lift_review_flag:** none

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.PackageURL.from_string(purl: str) -> PackageURL"
  - "featurelifted.PackageURL(type, namespace=None, name=..., version=None, qualifiers=None, subpath=None)"
  - "featurelifted.PackageURL.to_string() -> str"
returns:
  - "PackageURL; to_string purl"
exceptions:
  - "ValueError on invalid purl"
defaults:
  - "namespace/version optional"
state_effects:
  - "none"
```

## upstream_mapping

```yaml
primary_symbols:
  - "packageurl.PackageURL"
supporting_components:
semantic_delta:
  - "Normalize qualifiers ordering as upstream"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  PURL parse/normalize.
```

## scope

```yaml
included:
  - "from_string, to_string, field access"
excluded:
  - "package ecosystem network lookups"
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
offline_resources: "strings"
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

- Staging path: `benchmark/staging/packageurl__purl_parse_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
