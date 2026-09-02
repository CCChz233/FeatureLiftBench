# Design card: cssselect__selector_xpath_core__001

**status:** `validated_staging`  
**wave:** W1  
**package:** `cssselect`  
**repository_url:** https://github.com/scrapy/cssselect  
**planned_lift_type:** Composite  
**final_lift_type:** Adapted  
**reclassification_reason:** Upstream GenericTranslator/HTMLTranslator already expose css→xpath as the documented primary surface; packaging parse + two translators + exceptions as one Required API is Adapted packaging, not a new multi-component Composite. Kept Adapted (not Direct) because HTMLTranslator vs GenericTranslator HTML-name differences and exception mapping must be declared in the contract.  
**feature_family:** parse_tokenize_decode  
**entanglement:** parser_state_coupling  
**feature_one_liner:** Parse CSS selectors + translate to XPath  
**lift_review_flag:** none  
**skim_status:** `pass` (2026-07-31)

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/archive/plans/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.parse(selector: str) -> SelectorGroup"
  - "featurelifted.GenericTranslator().css_to_xpath(selector: str, prefix: str = 'descendant-or-self::') -> str"
  - "featurelifted.HTMLTranslator().css_to_xpath(selector: str, prefix: str = 'descendant-or-self::') -> str"
  - "featurelifted.SelectorError"
  - "featurelifted.ExpressionError"
returns:
  - "css_to_xpath returns xpath string"
  - "parse returns selector AST objects; treat as opaque except that they are accepted by translators when constructed via parse"
exceptions:
  - "SelectorError on invalid selector syntax"
  - "ExpressionError on selectors that cannot be expressed in XPath"
defaults:
  - "prefix='descendant-or-self::'"
state_effects:
  - "translators are stateless"
```

## upstream_mapping

```yaml
primary_symbols:
  - "cssselect.parse"
  - "cssselect.GenericTranslator"
  - "cssselect.HTMLTranslator"
supporting_components:
  - "cssselect.xpath"
  - "cssselect.parser"
semantic_delta:
  - "Task-facing Required API lists translator methods + exceptions; no invented facade"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Single library cssselect translation surface.
```

## scope

```yaml
included:
  - "CSS3 subset supported by cssselect"
  - "GenericTranslator for XML-style element names (case-sensitive)"
  - "HTMLTranslator HTML name quirks: element names lowercased; checked cases include div/span, #id, .class, attribute selectors, :nth-child"
  - "invalid selector → SelectorError; unsupported expression → ExpressionError"
excluded:
  - "executing xpath against documents (lxml)"
  - "scrapy Selector integration"
  - "custom Translator subclasses beyond Generic/HTML"
```

## feasibility

```yaml
commit: "a5057bbf12ddc605354f5bee123ae79b9c980703"  # tag v1.5.0
license: "BSD-3-Clause"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "string selector → xpath only"
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

- Staging path: `benchmark/staging/cssselect__selector_xpath_core__001/`
- Skim passed as Adapted; pin commit before materialize.
- Do not promote to `benchmark/tasks/` in pilot wave.
