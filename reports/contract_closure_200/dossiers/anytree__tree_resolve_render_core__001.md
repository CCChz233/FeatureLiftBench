# anytree__tree_resolve_render_core__001

- release: `external50`
- lift: `Composite`
- coupling: `data_model_coupling`
- strict validation: `PASS`
- tests/assertions: `10/22`

## Required API

- `featurelifted.Node` (class)
- `featurelifted.Node.name` (attribute)
- `featurelifted.Node.parent` (attribute)
- `featurelifted.Node.children` (attribute)
- `featurelifted.Resolver` (class)
- `featurelifted.Resolver.get` (method)
- `featurelifted.RenderTree` (class)
- `featurelifted.RenderTree.__iter__` (method)
- `featurelifted.PreOrderIter` (function)
- `featurelifted.findall` (function)
- `featurelifted.ChildResolverError` (class)
- `featurelifted.ResolverError` (class)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: build parent/child trees and PreOrderIter. Required observable cases include build and preorder.
- **B002**: The extracted feature must support this observable behavior: Resolver path get and ChildResolverError. Required observable cases include resolver get.
- **B003**: The extracted feature must support this observable behavior: RenderTree yields Row(pre, fill, node) and findall filters. Required observable cases include render and findall.
- **B004**: parent assignment mutates children relationships.
- **B005**: The package exposes Node/Resolver/RenderTree/PreOrderIter/findall/ChildResolverError/ResolverError with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: anytree.

## Tests

### `public_tests/test_public_api.py::test_build_and_preorder`

- mapping: `B001`
- API: `featurelifted.Node, featurelifted.PreOrderIter`
- risk: `ordering_semantics`
- A001 `assert` L17: `[n.name for n in PreOrderIter(root)] == ['udo', 'marc', 'lian']`

### `public_tests/test_public_api.py::test_resolver_get`

- mapping: `B002`
- API: `featurelifted.ChildResolverError, featurelifted.Node, featurelifted.Resolver`
- risk: `none`
- A001 `assert` L25: `r.get(root, '/udo/marc/lian') is lian`
- A002 `assert` L28: `False`

### `public_tests/test_public_api.py::test_render_and_findall`

- mapping: `B003`
- API: `featurelifted.Node, featurelifted.RenderTree, featurelifted.findall`
- risk: `none`
- A001 `assert` L37: `lines[0] == 'udo'`
- A002 `assert` L38: `any(('marc' in line for line in lines))`
- A003 `assert` L40: `[n.name for n in found] == ['marc']`

### `hidden_tests/test_hidden_behavior.py::test_parent_children_mutation`

- mapping: `B001`
- API: `featurelifted.Node, featurelifted.PreOrderIter`
- risk: `state_mutation`
- A001 `assert` L20: `a in root.children`
- A002 `assert` L21: `list(PreOrderIter(root))[1] is a`

### `hidden_tests/test_hidden_behavior.py::test_resolver_relative_path`

- mapping: `B002`
- API: `featurelifted.Node, featurelifted.Resolver`
- risk: `filesystem_resource`
- A001 `assert` L29: `r.get(a, 'b') is b`

### `hidden_tests/test_hidden_behavior.py::test_render_row_fields`

- mapping: `B003`
- API: `featurelifted.Node, featurelifted.RenderTree`
- risk: `none`
- A001 `assert` L36: `hasattr(rows[0], 'pre') and hasattr(rows[0], 'fill') and hasattr(rows[0], 'node')`

### `hidden_tests/test_hidden_behavior.py::test_findall_empty`

- mapping: `B004`
- API: `featurelifted.Node, featurelifted.findall`
- risk: `none`
- A001 `assert` L41: `findall(root, filter_=lambda n: False) == ()`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L50: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_hidden_behavior.py::test_resolver_error_base`

- mapping: `B002`
- API: `featurelifted.ResolverError`
- risk: `none`
- A001 `assert` L54: `issubclass(ResolverError, Exception)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.RenderTree, featurelifted.RenderTree.__iter__, featurelifted.Resolver, featurelifted.Resolver.get`
- risk: `none`
- A001 `assert` L5: `hasattr(featurelifted, 'ChildResolverError')`
- A002 `assert` L6: `hasattr(featurelifted, 'Node')`
- A003 `assert` L7: `hasattr(featurelifted, 'PreOrderIter')`
- A004 `assert` L8: `hasattr(featurelifted, 'RenderTree')`
- A005 `assert` L9: `hasattr(featurelifted, 'Resolver')`
- A006 `assert` L10: `hasattr(featurelifted, 'ResolverError')`
- A007 `assert` L11: `hasattr(featurelifted, 'findall')`
- A008 `assert` L12: `callable(featurelifted.Resolver.get)`
- A009 `assert` L13: `callable(featurelifted.RenderTree.__iter__)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `anytree`
- source entrypoints: `none`
- oracle source files: `src/anytree/node/nodemixin.py, src/anytree/resolver.py, src/anytree/render.py`
- runtime dependencies: `none`
- oracle notes: Composite Node + Resolver + RenderTree + PreOrderIter/findall.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
