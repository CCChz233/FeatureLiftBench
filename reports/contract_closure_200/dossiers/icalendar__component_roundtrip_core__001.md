# icalendar__component_roundtrip_core__001

- release: `external50`
- lift: `Composite`
- coupling: `parser_state_coupling`
- strict validation: `PASS`
- tests/assertions: `6/13`

## Required API

- `featurelifted.Calendar` (class)
- `featurelifted.Calendar.from_ical` (method)
- `featurelifted.Calendar.to_ical` (method)
- `featurelifted.Calendar.add_component` (method)
- `featurelifted.Calendar.subcomponents` (attribute)
- `featurelifted.Calendar.from_ical` (method)
- `featurelifted.Calendar.to_ical` (method)
- `featurelifted.Event` (class)
- `featurelifted.Event.add` (method)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: build Calendar/Event and roundtrip ICS. Required observable cases include build and roundtrip.
- **B002**: The extracted feature must support this observable behavior: parse existing ICS strings. Required observable cases include parse existing ics.
- **B003**: The extracted feature must support this observable behavior: dtend and multiple events. Required observable cases include event dtend; multiple events.
- **B004**: to_ical returns bytes suitable for from_ical.
- **B005**: The package exposes Calendar/Event/from_ical/to_ical with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: icalendar.

## Tests

### `public_tests/test_public_api.py::test_build_and_roundtrip`

- mapping: `B001`
- API: `featurelifted.Calendar, featurelifted.Calendar.from_ical, featurelifted.Event`
- risk: `none`
- A001 `assert` L17: `ev['summary'].to_ical().decode() == 'Team sync'`

### `public_tests/test_public_api.py::test_parse_existing_ics`

- mapping: `B002`
- API: `featurelifted.Calendar, featurelifted.Calendar.from_ical`
- risk: `none`
- A001 `assert` L32: `cal['prodid'].to_ical().decode().startswith('-//')`

### `hidden_tests/test_hidden_behavior.py::test_event_dtend`

- mapping: `B001, B003, B004`
- API: `featurelifted.Calendar, featurelifted.Calendar.from_ical, featurelifted.Event`
- risk: `none`
- A001 `assert` L17: `'dtend' in ev`

### `hidden_tests/test_hidden_behavior.py::test_multiple_events`

- mapping: `B002`
- API: `featurelifted.Calendar, featurelifted.Calendar.from_ical, featurelifted.Event`
- risk: `none`
- A001 `assert` L28: `summaries == ['a', 'b']`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L42: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.Calendar, featurelifted.Calendar.add_component, featurelifted.Calendar.from_ical, featurelifted.Calendar.to_ical, featurelifted.Event, featurelifted.Event.add`
- risk: `none`
- A001 `assert` L5: `hasattr(featurelifted, 'Calendar')`
- A002 `assert` L6: `hasattr(featurelifted, 'Event')`
- A003 `assert` L7: `callable(featurelifted.Calendar.from_ical)`
- A004 `assert` L8: `callable(featurelifted.Calendar.to_ical)`
- A005 `assert` L9: `callable(featurelifted.Calendar.add_component)`
- A006 `assert` L10: `callable(featurelifted.Calendar.from_ical)`
- A007 `assert` L11: `callable(featurelifted.Calendar.to_ical)`
- A008 `assert` L12: `callable(featurelifted.Event.add)`

## Dependency / Oracle Evidence

- allowed dependencies: `python-dateutil, six, tzdata`
- forbidden imports: `icalendar`
- source entrypoints: `none`
- oracle source files: `src/icalendar/cal/calendar.py, src/icalendar/cal/event.py`
- runtime dependencies: `python-dateutil, six, tzdata`
- oracle notes: Composite Calendar.from_ical/to_ical + Event components.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
