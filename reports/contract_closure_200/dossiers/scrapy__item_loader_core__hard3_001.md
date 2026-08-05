# scrapy__item_loader_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `4/14`

## Required API

- `featurelifted.Item` (class) `(*args, **kwargs)`
- `featurelifted.Field` (class) `(*args, **kwargs)`
- `featurelifted.ItemLoader` (class) `(item: 'type[Item] | Item | None' = None, parent: "'ItemLoader | None'" = None, **context)`
- `featurelifted.ItemLoader.__init__` (method) `(self, item: 'type[Item] | Item | None' = None, parent: "'ItemLoader | None'" = None, **context)`
- `featurelifted.ItemLoader.add_value` (method) `(self, field_name: 'str', value: 'Any') -> 'None'`
- `featurelifted.ItemLoader.load_item` (method) `(self) -> 'Item'`
- `featurelifted.ItemLoader.default_output_processor` (attribute)
- `featurelifted.Compose` (function) `(*processors: 'Callable') -> 'Callable'`
- `featurelifted.TakeFirst` (function) `()`

## Public Behaviors

- **B001**: When an Item declares Field metadata with input or output processors, those processors are attached to the field definition.
- **B002**: When ItemLoader.add_value runs input processors and load_item runs output processors, the resulting item values reflect the processor pipeline.
- **B003**: When a nested ItemLoader is created with parent=..., it inherits the parent default processor types.
- **B004**: The package exposes the required task API paths `featurelifted.Item`, `featurelifted.Field`, `featurelifted.ItemLoader`, `featurelifted.ItemLoader.__init__`, `featurelifted.ItemLoader.add_value`, `featurelifted.ItemLoader.load_item`, `featurelifted.ItemLoader.default_output_processor`, `featurelifted.Compose`, `featurelifted.TakeFirst` with the kinds and callable signatures listed in this contract.
- **B006**: When add_value is called for an undefined field name, ItemLoader raises KeyError.

## Tests

### `public_tests/test_public_contract.py::test_item_loader_applies_processors`

- mapping: `B002, B003`
- API: `featurelifted.ItemLoader`
- risk: `none`
- A001 `assert` L15: `item['name'] == '  hat '`
- A002 `assert` L16: `item['price'] == '9'`

### `hidden_tests/test_hidden_contract.py::test_compose_output_processor_and_parent_defaults`

- mapping: `B001, B002, B003`
- API: `featurelifted.ItemLoader`
- risk: `none`
- A001 `assert` L17: `item['tags'] == ['A', 'B']`
- A002 `assert` L19: `type(child.default_output_processor) is type(loader.default_output_processor)`

### `hidden_tests/test_hidden_contract.py::test_missing_field_raises`

- mapping: `B006`
- API: `featurelifted.ItemLoader`
- risk: `exception_semantics`
- A001 `raises` L24: `pytest.raises(KeyError)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.Compose, featurelifted.Field, featurelifted.Item, featurelifted.ItemLoader, featurelifted.TakeFirst`
- risk: `none`
- A001 `assert` L13: `isinstance(Item, type)`
- A002 `assert` L14: `isinstance(Field, type)`
- A003 `assert` L15: `isinstance(ItemLoader, type)`
- A004 `assert` L16: `hasattr(ItemLoader, '__init__')`
- A005 `assert` L17: `hasattr(ItemLoader, 'add_value')`
- A006 `assert` L18: `hasattr(ItemLoader, 'load_item')`
- A007 `assert` L19: `ItemLoader is not None`
- A008 `assert` L20: `callable(Compose)`
- A009 `assert` L21: `callable(TakeFirst)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `scrapy`
- source entrypoints: `scrapy.loader.ItemLoader, scrapy.item.Item`
- oracle source files: `repo/scrapy/item.py, repo/scrapy/loader/__init__.py`
- runtime dependencies: `none`
- oracle notes: ItemLoader subset without selector/response/downloader code.
