# Design card: icalendar__component_roundtrip_core__001

**status:** `design_card_ready`  
**wave:** W3  
**package:** `icalendar`  
**repository_url:** https://github.com/collective/icalendar  
**planned_lift_type:** Composite  
**final_lift_type:** Composite  
**reclassification_reason:** None  
**feature_family:** serialize_format_render  
**entanglement:** parser_state_coupling  
**feature_one_liner:** Parse ICS components + build Calendar/Event  
**lift_review_flag:** none

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.Calendar.from_ical(data: str|bytes)"
  - "featurelifted.Calendar.to_ical() -> bytes"
  - "featurelifted.Event / Todo property setters dtstart/dtend/summary"
  - "featurelifted.vDDDTypes / prop codecs as needed \u2014 minimize"
returns:
  - "Calendar; to_ical bytes"
exceptions:
  - "ValueError on bad ical"
defaults:
  - "declare"
state_effects:
  - "component graphs mutable"
```

## upstream_mapping

```yaml
primary_symbols:
  - "icalendar.Calendar"
  - "icalendar.Event"
supporting_components:
  - "icalendar.prop"
semantic_delta:
  - "parse + build components"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Round-trip ICS strings.
```

## scope

```yaml
included:
  - "parse calendar, create Event, serialize"
excluded:
  - "recurrence full RRULE engines beyond what is declared"
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
offline_resources: "ICS strings"
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

- Staging path: `benchmark/staging/icalendar__component_roundtrip_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
