# Task Design: faker__provider_core__001

Status: oracle-verified

## Why This Task

Covers locale-scoped provider data and factory wiring without multi-locale proxy complexity.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| en_US person data | `providers/person/en_US/__init__.py` | `test_only_en_us_locale_and_provider_formats` |
| Factory wiring | `factory.py` | `test_en_us_person_address_and_phone_are_seeded` |
| Weighted sampling | `utils/distribution.py` | `test_address_contains_city_state_zip_pattern` |
