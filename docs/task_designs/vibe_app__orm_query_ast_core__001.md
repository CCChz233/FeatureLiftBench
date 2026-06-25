# Task Design: vibe_app__orm_query_ast_core__001

Status: oracle-verified

## Why This Task

Extract mini ORM query-to-SQL AST compilation from VibeShop where framework GLOBAL_STATE bookkeeping and duplicate utils shortcuts obscure the canonical compiler path.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| AST nodes | `orm_query/ast.py` | `test_build_ast_records_columns_and_predicates` (public) |
| Query builder | `orm_query/query.py` | `test_build_ast_tracks_global_state` |
| SQL compiler | `orm_query/compiler.py` | `test_join_and_multiple_predicates` |
