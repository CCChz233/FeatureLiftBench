# Design card: dateparser__parse_settings_pipeline_core__001

**status:** `validated_staging`  
**wave:** W1  
**package:** `dateparser`  
**repository_url:** https://github.com/scrapinghub/dateparser  
**planned_lift_type:** Composite  
**final_lift_type:** Composite  
**reclassification_reason:** None  
**feature_family:** parse_tokenize_decode  
**entanglement:** parser_state_coupling  
**feature_one_liner:** Settings + language detect + parse date strings into datetime  
**lift_review_flag:** none  
**skim_status:** `pass` (2026-07-31)

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.Settings(**options) -> Settings"
  - "featurelifted.parse(date_string: str, date_formats: list[str] | None = None, languages: list[str] | None = None, locales: list[str] | None = None, region: str | None = None, settings: Settings | dict | None = None) -> datetime | None"
  - "featurelifted.detect_languages(text: str, languages: list[str] | None = None) -> list[str]"
returns:
  - "parse returns datetime or None"
  - "detect_languages returns list[str] of language shortcodes (e.g. 'en', 'es', 'fr')"
exceptions:
  - "TypeError when a settings value is None (upstream replace validation); allowlisted keys only are tested"
  - "TypeError on bad argument types where upstream raises TypeError"
settings_allowlist:
  - "PREFER_DATES_FROM"        # values: 'current_period' | 'past' | 'future'
  - "RETURN_AS_TIMEZONE_AWARE" # bool
  - "TIMEZONE"                # e.g. 'UTC', 'US/Eastern'
  - "TO_TIMEZONE"             # e.g. 'UTC'
  - "DATE_ORDER"              # e.g. 'MDY', 'DMY', 'YMD'
  - "STRICT_PARSING"          # bool
  - "REQUIRE_PARTS"           # list of parts when used
locale_test_subset:
  languages:
    - "en"
    - "es"
    - "fr"
  example_inputs:
    - "2020-01-15"
    - "January 15, 2020"
    - "15 de enero de 2020"
    - "15 janvier 2020"
    - "yesterday"   # relative; only with PREFER_DATES_FROM / RELATIVE support if present in allowlist usage
defaults:
  - "Only settings_allowlist keys are required; other upstream settings may exist but are out of test scope"
state_effects:
  - "Settings may cache language detectors; must be process-local and offline"
```

## upstream_mapping

```yaml
primary_symbols:
  - "dateparser.parse"
  - "dateparser.conf.Settings"
supporting_components:
  - "dateparser.languages"
  - "dateparser_data (locale/date data files bundled in repo snapshot)"
semantic_delta:
  - "Compose Settings + language detection + parse into one declared pipeline"
  - "settings_allowlist and locale_test_subset freeze the Mixed oracle surface"
```

## oracle_basis

```yaml
basis: mixed
notes: |
  Upstream parse/Settings behavior for allowlisted keys; detect_languages return type and
  language shortcodes declared here. Relative phrases only when covered by allowlisted settings.
```

## scope

```yaml
included:
  - "parse with date_formats / languages / locales / settings from allowlist"
  - "detect_languages returning list[str] shortcodes for en/es/fr subset"
  - "timezone-aware results when RETURN_AS_TIMEZONE_AWARE / TIMEZONE / TO_TIMEZONE set"
excluded:
  - "dateparser.search.search_dates"
  - "network access"
  - "fresh language model downloads"
  - "settings keys outside settings_allowlist"
  - "languages outside en/es/fr for required tests"
```

## feasibility

```yaml
commit: "08c78d3b8bcdd2f721dff8ffaf25de482fd696dd"  # tag v1.4.1
license: "BSD-3-Clause"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none expected (pure python + data files)"
offline_resources: |
  Bundle from upstream tree (no download at eval time):
  - dateparser/data/ (and dateparser_data if present)
  - language/locale YAML or JSON data files required for en/es/fr
```

## acceptance

```yaml
closure_review: pass
reference_pass: pass
isolation_pass: pass
no_original_import: pass
overlap_check: pass
```

## agent_notes

- Staging path: `benchmark/staging/dateparser__parse_settings_pipeline_core__001/`
- Skim passed after settings/locale freeze; pin commit before materialize.
- Do not promote to `benchmark/tasks/` in pilot wave.
- If offline data closure proves intractable at pin time, mark blocked and use ledger backup.
