# babel__plural_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `5/20`

## Required API

- `featurelifted.PluralRule` (class) `(rules)`
- `featurelifted.PluralRule.parse` (method) `(rules)`
- `featurelifted.Locale` (class) `(language, territory=None, script=None, variant=None)`
- `featurelifted.Locale.parse` (method) `(identifier, sep='_', resolve_likely_subtags=True)`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: evaluate PluralRule expressions for numeric operands. Required observable cases include plural rule string and float operands.
- **B002**: The extracted feature must support this observable behavior: resolve Locale plural categories for en, ru, fr, ja, and pl. Required observable cases include locale plural categories multilingual.
- **B003**: The extracted feature must support this observable behavior: load plural rules from packaged locale-data .dat resources. Required observable cases include plural rule and english locale; plural rule expression edges; plural rule string and float operands.
- **B004**: The package exposes the required task API paths `featurelifted.PluralRule`, `featurelifted.PluralRule.parse`, `featurelifted.Locale`, `featurelifted.Locale.parse` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_plural_rule_and_english_locale`

- mapping: `B003`
- API: `featurelifted.Locale, featurelifted.Locale.parse, featurelifted.PluralRule`
- risk: `none`
- A001 `assert` L8: `rule(1) == 'one'`
- A002 `assert` L9: `rule(5) == 'other'`
- A003 `assert` L12: `en.plural_form(1) == 'one'`
- A004 `assert` L13: `en.plural_form(0) == 'other'`

### `hidden_tests/test_hidden_behavior.py::test_plural_rule_expression_edges`

- mapping: `B003`
- API: `featurelifted.PluralRule`
- risk: `exception_semantics`
- A001 `assert` L10: `rule(1) == 'one'`
- A002 `assert` L11: `rule(3) == 'few'`
- A003 `assert` L12: `rule(5) == 'other'`
- A004 `raises` L14: `pytest.raises(ValueError)`

### `hidden_tests/test_hidden_behavior.py::test_locale_plural_categories_multilingual`

- mapping: `B002`
- API: `featurelifted.Locale, featurelifted.Locale.parse, featurelifted.Locale.plural_form`
- risk: `none`
- A001 `assert` L19: `Locale.parse('ru').plural_form(21) == 'one'`
- A002 `assert` L20: `Locale.parse('ru').plural_form(22) == 'few'`
- A003 `assert` L21: `Locale.parse('fr').plural_form(0) == 'one'`
- A004 `assert` L22: `Locale.parse('ja').plural_form(5) == 'other'`
- A005 `assert` L23: `Locale.parse('pl').plural_form(22) == 'few'`
- A006 `assert` L24: `Locale.parse('pl').plural_form(100) == 'many'`

### `hidden_tests/test_hidden_behavior.py::test_plural_rule_string_and_float_operands`

- mapping: `B001, B003`
- API: `featurelifted.PluralRule, featurelifted.PluralRule.parse`
- risk: `none`
- A001 `assert` L29: `rule(1) == 'one'`
- A002 `assert` L30: `rule(1.0) == 'one'`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.Locale, featurelifted.PluralRule`
- risk: `none`
- A001 `assert` L10: `isinstance(PluralRule, type)`
- A002 `assert` L11: `hasattr(PluralRule, 'parse')`
- A003 `assert` L12: `isinstance(Locale, type)`
- A004 `assert` L13: `hasattr(Locale, 'parse')`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `babel`
- source entrypoints: `babel.plural.PluralRule, babel.core.Locale, babel.core.Locale.plural_form, babel.localedata`
- oracle source files: `babel/__init__.py, babel/core.py, babel/plural.py, babel/localedata.py, babel/global.dat, babel/locale-data/root.dat, babel/locale-data/en.dat, babel/locale-data/ru.dat, babel/locale-data/fr.dat, babel/locale-data/ja.dat, babel/locale-data/pl.dat`
- runtime dependencies: `none`
- oracle notes: Plural subset with core/localedata/plural and six locale-data files.

## Machine Issues

- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.Locale.plural_form
