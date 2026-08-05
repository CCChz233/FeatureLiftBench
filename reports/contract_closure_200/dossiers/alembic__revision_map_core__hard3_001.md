# alembic__revision_map_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `10/36`

## Required API

- `featurelifted.Revision` (class) `(revision: 'str', down_revision: 'str | tuple[str, ...] | None' = None, dependencies: 'str | tuple[str, ...] | None' = None, branch_labels: 'set[str] | tuple[str, ...] | list[str] | None' = None) -> None`
- `featurelifted.RevisionMap` (class) `(revisions: 'Iterable[Revision]') -> 'None'`
- `featurelifted.RevisionMap.heads` (attribute)
- `featurelifted.RevisionMap.bases` (attribute)
- `featurelifted.RevisionMap.branch_labels` (attribute)
- `featurelifted.RevisionMap.get_revision` (method) `(self, identifier: 'str | None') -> 'Revision | None'`
- `featurelifted.RevisionMap.get_revisions` (method) `(self, identifiers) -> 'tuple[Revision | None, ...]'`
- `featurelifted.RevisionMap.get_heads` (method) `(self) -> 'list[str]'`
- `featurelifted.RevisionMap.get_current_head` (method) `(self, branch_label: 'str | None' = None) -> 'str'`
- `featurelifted.RevisionMap.ancestors` (method) `(self, revision_id: 'str', include_dependencies: 'bool' = True) -> 'set[str]'`
- `featurelifted.RevisionMap.iterate_revisions` (method) `(self, upper: 'str', lower: 'str | None' = None) -> 'list[Revision]'`
- `featurelifted.CycleDetected` (exception)
- `featurelifted.MissingRevision` (exception)
- `featurelifted.MultipleHeads` (exception)

## Public Behaviors

- **B001**: When Revision objects are created, scalar and iterable down revisions, branch labels, and dependencies are normalized without losing their distinct graph roles.
- **B002**: When RevisionMap is built from explicit revisions, it links versioned parents, dependency edges, and branch labels into a queryable graph.
- **B003**: For linear, branched, and merged revision graphs, RevisionMap reports the versioned bases and heads that have no versioned parent or child.
- **B004**: When a branch label is assigned, branch-label lookup resolves that revision and propagates the label to eligible descendants.
- **B005**: When ancestors are requested, dependency revisions are included only when dependency-aware traversal is enabled.
- **B006**: When symbolic identifiers such as head or base are requested, RevisionMap resolves them and rejects ambiguous heads.
- **B007**: Missing revisions, multiple-head requests, and revision cycles raise the declared explicit graph errors.
- **B008**: The package exposes the required task API paths `featurelifted.Revision`, `featurelifted.RevisionMap`, `featurelifted.RevisionMap.heads`, `featurelifted.RevisionMap.bases`, `featurelifted.RevisionMap.branch_labels`, `featurelifted.RevisionMap.get_revision`, `featurelifted.RevisionMap.get_revisions`, `featurelifted.RevisionMap.get_heads`, `featurelifted.RevisionMap.get_current_head`, `featurelifted.RevisionMap.ancestors`, `featurelifted.RevisionMap.iterate_revisions`, `featurelifted.CycleDetected`, and 2 listed members with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_heads_for_linear_revision_map`

- mapping: `B007`
- API: `featurelifted.Revision, featurelifted.RevisionMap`
- risk: `none`
- A001 `assert` L8: `revmap.get_current_head() == 'b'`
- A002 `assert` L9: `revmap.get_heads() == ['b']`
- A003 `assert` L10: `revmap.bases == ('a',)`
- A004 `assert` L11: `revmap.get_revision('a').revision == 'a'`

### `public_tests/test_public_contract.py::test_merge_revision_removes_branch_heads`

- mapping: `B007`
- API: `featurelifted.Revision, featurelifted.RevisionMap`
- risk: `none`
- A001 `assert` L23: `revmap.get_heads() == ['merge']`
- A002 `assert` L24: `revmap.get_revision('merge').is_merge_point`
- A003 `assert` L25: `revmap.get_revision('base').is_branch_point`

### `public_tests/test_public_contract.py::test_iterate_revisions_walks_down_revision_chain`

- mapping: `B001, B007`
- API: `featurelifted.Revision, featurelifted.RevisionMap`
- risk: `none`
- A001 `assert` L31: `[revision.revision for revision in revmap.iterate_revisions('c', 'a')] == ['c', 'b']`

### `hidden_tests/test_hidden_contract.py::test_branch_labels_resolve_and_multiple_heads_raise`

- mapping: `B004, B007`
- API: `featurelifted.MultipleHeads, featurelifted.Revision, featurelifted.RevisionMap`
- risk: `exception_semantics`
- A001 `assert` L14: `revmap.get_revision('feature').revision == 'left'`
- A002 `raises` L15: `pytest.raises(MultipleHeads)`

### `hidden_tests/test_hidden_contract.py::test_branch_label_propagates_to_branch_head`

- mapping: `B004`
- API: `featurelifted.Revision, featurelifted.RevisionMap`
- risk: `none`
- A001 `assert` L28: `revmap.get_current_head('feature') == 'left2'`
- A002 `assert` L29: `revmap.get_current_head('other') == 'right'`
- A003 `assert` L30: `revmap.branch_labels == {'feature': 'left', 'other': 'right'}`

### `hidden_tests/test_hidden_contract.py::test_dependencies_affect_ancestors_without_removing_versioned_head`

- mapping: `B003, B005`
- API: `featurelifted.Revision, featurelifted.RevisionMap`
- risk: `none`
- A001 `assert` L42: `revmap.get_heads() == ['feature_tip', 'main_tip']`
- A002 `assert` L43: `revmap.ancestors('main_tip') == {'base', 'feature_base'}`

### `hidden_tests/test_hidden_contract.py::test_missing_down_revision_raises`

- mapping: `B001, B002, B007`
- API: `featurelifted.MissingRevision, featurelifted.Revision, featurelifted.RevisionMap`
- risk: `exception_semantics`
- A001 `raises` L47: `pytest.raises(MissingRevision)`

### `hidden_tests/test_hidden_contract.py::test_cycle_detection_raises`

- mapping: `B007`
- API: `featurelifted.CycleDetected, featurelifted.Revision, featurelifted.RevisionMap`
- risk: `exception_semantics`
- A001 `raises` L52: `pytest.raises(CycleDetected)`

### `hidden_tests/test_hidden_contract.py::test_head_symbol_and_base_symbol_resolution`

- mapping: `B003, B006`
- API: `featurelifted.Revision, featurelifted.RevisionMap`
- risk: `none`
- A001 `assert` L59: `revmap.get_revision('head').revision == 'b'`
- A002 `assert` L60: `revmap.get_revision('base') is None`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B008`
- API: `featurelifted.CycleDetected, featurelifted.MissingRevision, featurelifted.MultipleHeads, featurelifted.Revision, featurelifted.RevisionMap`
- risk: `none`
- A001 `assert` L13: `isinstance(Revision, type)`
- A002 `assert` L14: `isinstance(RevisionMap, type)`
- A003 `assert` L15: `RevisionMap is not None`
- A004 `assert` L16: `RevisionMap is not None`
- A005 `assert` L17: `RevisionMap is not None`
- A006 `assert` L18: `hasattr(RevisionMap, 'get_revision')`
- A007 `assert` L19: `hasattr(RevisionMap, 'get_revisions')`
- A008 `assert` L20: `hasattr(RevisionMap, 'get_heads')`
- A009 `assert` L21: `hasattr(RevisionMap, 'get_current_head')`
- A010 `assert` L22: `hasattr(RevisionMap, 'ancestors')`
- A011 `assert` L23: `hasattr(RevisionMap, 'iterate_revisions')`
- A012 `assert` L24: `issubclass(CycleDetected, BaseException)`
- A013 `assert` L25: `issubclass(MissingRevision, BaseException)`
- A014 `assert` L26: `issubclass(MultipleHeads, BaseException)`
- A015 `assert` L28: `hasattr(revision_map, 'heads')`
- A016 `assert` L29: `hasattr(revision_map, 'bases')`
- A017 `assert` L30: `hasattr(revision_map, 'branch_labels')`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `alembic, sqlalchemy`
- source entrypoints: `alembic.script.revision.Revision, alembic.script.revision.RevisionMap, alembic.script.revision.MultipleHeads, alembic.script.revision.CycleDetected, alembic.script.revision.ResolutionError`
- oracle source files: `repo/alembic/script/revision.py, repo/alembic/script/base.py, repo/alembic/util/exc.py, repo/alembic/util/langhelpers.py, repo/pyproject.toml, repo/LICENSE`
- runtime dependencies: `none`
- oracle notes: Oracle evidence should inspect revision graph, branch-label, dependency, and error semantics without accepting runtime imports from Alembic or SQLAlchemy.
