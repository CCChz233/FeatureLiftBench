# faker__provider_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `4/20`

## Required API

- `featurelifted.Faker` (class) `(locale: 'str | Sequence[str] | dict[str, int | float] | None' = None, providers: 'list[str] | None' = None, generator: 'Generator | None' = None, includes: 'list[str] | None' = None, use_weighting: 'bool' = True, **config: 'Any') -> 'None'`
- `featurelifted.Faker.address` (method) `() -> str`
- `featurelifted.Faker.first_name` (method) `() -> str`
- `featurelifted.Faker.last_name` (method) `() -> str`
- `featurelifted.Faker.phone_number` (method) `() -> str`
- `featurelifted.Faker.seed_instance` (method) `(self, seed: 'SeedType | None' = None) -> 'None'`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: construct Faker with locale en_US and default person/address/phone providers. Required observable cases include en us person address and phone are seeded; only en us locale and provider formats; address contains city state zip pattern.
- **B002**: The extracted feature must support this observable behavior: generate deterministic fake names, addresses, and phone numbers with seed_instance. Required observable cases include only en us locale and provider formats.
- **B003**: The extracted feature must support this observable behavior: resolve localized provider modules and locale resource data. Required observable cases include only en us locale and provider formats.
- **B004**: The package exposes the required task API paths `featurelifted.Faker`, `featurelifted.Faker.address`, `featurelifted.Faker.first_name`, `featurelifted.Faker.last_name`, `featurelifted.Faker.phone_number`, `featurelifted.Faker.seed_instance` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_en_us_person_address_and_phone_are_seeded`

- mapping: `B001`
- API: `featurelifted.Faker`
- risk: `none`
- A001 `assert` L12: `isinstance(name, str) and ' ' in name`
- A002 `assert` L13: `isinstance(address, str) and '\n' in address`
- A003 `assert` L14: `phone.startswith('(') or phone[0].isdigit()`
- A004 `assert` L17: `fake.name() == name`
- A005 `assert` L18: `fake.address() == address`
- A006 `assert` L19: `fake.phone_number() == phone`

### `hidden_tests/test_hidden_behavior.py::test_only_en_us_locale_and_provider_formats`

- mapping: `B001, B002, B003`
- API: `featurelifted.Faker`
- risk: `none`
- A001 `assert` L12: `re.search('\\d{3}', phone)`
- A002 `assert` L13: `len(phone) >= 10`
- A003 `assert` L18: `first.isalpha()`
- A004 `assert` L19: `last.isalpha()`
- A005 `assert` L22: `fake.first_name() == first`
- A006 `assert` L23: `fake.last_name() == last`

### `hidden_tests/test_hidden_behavior.py::test_address_contains_city_state_zip_pattern`

- mapping: `B001`
- API: `featurelifted.Faker`
- risk: `state_mutation`
- A001 `assert` L31: `len(lines) >= 2`
- A002 `assert` L32: `any((char.isdigit() for char in lines[-1]))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.Faker`
- risk: `none`
- A001 `assert` L9: `isinstance(Faker, type)`
- A002 `assert` L10: `Faker is not None`
- A003 `assert` L11: `Faker is not None`
- A004 `assert` L12: `Faker is not None`
- A005 `assert` L13: `Faker is not None`
- A006 `assert` L14: `hasattr(Faker, 'seed_instance')`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `faker`
- source entrypoints: `faker.proxy.Faker, faker.factory.Factory.create, faker.providers.person.en_US, faker.providers.address.en_US, faker.providers.phone_number.en_US`
- oracle source files: `faker/__init__.py, faker/config.py, faker/exceptions.py, faker/factory.py, faker/generator.py, faker/proxy.py, faker/typing.py, faker/utils/__init__.py, faker/utils/checksums.py, faker/utils/datasets.py, faker/utils/decorators.py, faker/utils/distribution.py, faker/utils/loading.py, faker/utils/text.py, faker/providers/__init__.py, faker/providers/person/__init__.py, faker/providers/person/en/__init__.py, faker/providers/person/en_US/__init__.py, faker/providers/address/__init__.py, faker/providers/address/en/__init__.py, faker/providers/address/en_US/__init__.py, faker/providers/phone_number/__init__.py, faker/providers/phone_number/en_US/__init__.py, faker/providers/date_time/__init__.py`
- runtime dependencies: `none`
- oracle notes: Oracle closure limited to en_US person/address/phone_number providers plus factory core.
