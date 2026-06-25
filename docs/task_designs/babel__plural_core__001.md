# Task Design: babel__plural_core__001

Status: oracle-verified

## Why This Task

Covers CLDR plural operands, rule parsing, and locale-data resource loading.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Plural parser | `plural.py` | `test_plural_rule_expression_edges` |
| Locale data | `locale-data/ru.dat` | `test_locale_plural_categories_multilingual` |
| Locale core | `core.py` | `test_plural_rule_and_english_locale` |
