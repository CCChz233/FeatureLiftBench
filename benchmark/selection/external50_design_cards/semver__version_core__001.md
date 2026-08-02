# Design card: semver__version_core__001

**status:** `validated_staging`  
**wave:** W5  
**package:** `semver`  
**repository_url:** https://github.com/python-semver/python-semver  
**planned_lift_type:** Direct  
**final_lift_type:** Direct  
**reclassification_reason:** None  
**feature_family:** validate_normalize_construct  
**entanglement:** data_model_coupling  
**feature_one_liner:** Version parse/compare/bump  
**lift_review_flag:** none  
**skim_status:** `pass` (2026-07-31)

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.Version.parse(version: str) -> Version"
  - "featurelifted.Version(major: int, minor: int = 0, patch: int = 0, prerelease: str | None = None, build: str | None = None)"
  - "featurelifted.Version.compare(self, other: Version) -> int"
  - "featurelifted.Version.bump_major(self) -> Version"
  - "featurelifted.Version.bump_minor(self) -> Version"
  - "featurelifted.Version.bump_patch(self) -> Version"
  - "featurelifted.Version.replace(self, **parts) -> Version"
  - "str(Version) / Version.__eq__/__lt__/__le__/__gt__/__ge__"
returns:
  - "Version objects; compare returns -1/0/1; bump/replace return new Version"
exceptions:
  - "ValueError on invalid version strings"
defaults:
  - "minor/patch default 0; prerelease/build default None"
state_effects:
  - "immutable Version instances"
```

## upstream_mapping

```yaml
primary_symbols:
  - "semver.Version"
  - "semver.VersionInfo (compat alias if present)"
supporting_components:
semantic_delta:
  - "Package as featurelifted; keep semver public Version API subset"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Direct extract of Version parse/compare/bump.
```

## scope

```yaml
included:
  - "parse, compare, bump_major/minor/patch, replace, str formatting, ordering operators"
excluded:
  - "CLI entry points (semver.__main__ / console scripts)"
  - "file reading helpers"
  - "deprecated VersionInfo-only quirks beyond optional alias export"
```

## feasibility

```yaml
commit: "6adf8765f6e21910f1f0c13151ce84f32f8d431d"  # tag 3.0.4
license: "BSD-3-Clause"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "pure functions on strings"
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

- Staging path: `benchmark/staging/semver__version_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
