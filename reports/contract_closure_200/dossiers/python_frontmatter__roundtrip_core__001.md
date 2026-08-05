# python_frontmatter__roundtrip_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `14/44`

## Required API

- `featurelifted.Post` (class) `(content: 'str', handler: 'BaseHandler | None' = None, **metadata: 'object') -> 'None'`
- `featurelifted.Post.content` (attribute)
- `featurelifted.Post.metadata` (attribute)
- `featurelifted.Post.to_dict` (method) `(self) -> 'dict[str, object]'`
- `featurelifted.parse` (function) `(text: 'str', encoding: 'str' = 'utf-8', handler: 'BaseHandler | None' = None, **defaults: 'object') -> 'tuple[dict[str, object], str]'`
- `featurelifted.load` (function) `(fd: 'str | io.IOBase | pathlib.Path', encoding: 'str' = 'utf-8', handler: 'BaseHandler | None' = None, **defaults: 'object') -> 'Post'`
- `featurelifted.loads` (function) `(text: 'str', encoding: 'str' = 'utf-8', handler: 'BaseHandler | None' = None, **defaults: 'object') -> 'Post'`
- `featurelifted.dump` (function) `(post: 'Post', fd: 'str | PathLike[str] | TextIO', encoding: 'str' = 'utf-8', handler: 'BaseHandler | None' = None, **kwargs: 'object') -> 'None'`
- `featurelifted.dumps` (function) `(post: 'Post', handler: 'BaseHandler | None' = None, **kwargs: 'object') -> 'str'`
- `featurelifted.checks` (function) `(text: 'str', encoding: 'str' = 'utf-8') -> 'bool'`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse and loads YAML front matter delimited by --- lines. Required observable cases include loads yaml frontmatter; parse returns metadata and content; empty frontmatter block.
- **B002**: The extracted feature must support this observable behavior: dump and dumps serialize Post metadata and markdown body. Required observable cases include dumps roundtrip metadata and body; no frontmatter returns empty metadata; unicode metadata roundtrip; custom dump delimiters.
- **B003**: The extracted feature must support this observable behavior: detect delimiter lines with optional trailing whitespace. Required observable cases include extra space after opening delimiter; checks detects frontmatter.
- **B004**: The extracted feature must support this observable behavior: normalize CRLF input and merge parse defaults. Required observable cases include parse returns metadata and content; crlf bytes normalize; parse defaults merge.
- **B005**: The extracted feature must support this observable behavior: Post dict-like metadata access and to_dict export. Required observable cases include no frontmatter returns empty metadata; unicode metadata roundtrip; post to dict.
- **B006**: The package exposes the required task API paths `featurelifted.Post`, `featurelifted.Post.content`, `featurelifted.Post.metadata`, `featurelifted.Post.to_dict`, `featurelifted.parse`, `featurelifted.load`, `featurelifted.loads`, `featurelifted.dump`, `featurelifted.dumps`, `featurelifted.checks` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_loads_yaml_frontmatter`

- mapping: `B001`
- API: `featurelifted.loads`
- risk: `none`
- A001 `assert` L9: `post['title'] == 'Hello'`
- A002 `assert` L10: `post['layout'] == 'post'`
- A003 `assert` L11: `post.content.strip() == 'Body here.'`

### `public_tests/test_public_api.py::test_dumps_roundtrip_metadata_and_body`

- mapping: `B002`
- API: `featurelifted.dumps, featurelifted.loads`
- risk: `none`
- A001 `assert` L18: `roundtrip.metadata == post.metadata`
- A002 `assert` L19: `roundtrip.content == post.content`

### `public_tests/test_public_api.py::test_parse_returns_metadata_and_content`

- mapping: `B001, B004`
- API: `featurelifted.parse`
- risk: `none`
- A001 `assert` L25: `metadata['count'] == 1`
- A002 `assert` L26: `content.strip() == 'content block'`

### `hidden_tests/test_hidden_behavior.py::test_extra_space_after_opening_delimiter`

- mapping: `B003`
- API: `featurelifted.loads`
- risk: `none`
- A001 `assert` L19: `post['test'] == 'tester'`
- A002 `assert` L20: `post['something'] == 'else'`
- A003 `assert` L21: `'extra space' in post.content`

### `hidden_tests/test_hidden_behavior.py::test_crlf_bytes_normalize`

- mapping: `B004`
- API: `featurelifted.loads`
- risk: `none`
- A001 `assert` L30: `loaded['title'] == 'my title'`
- A002 `assert` L31: `loaded.content.strip() == 'write your content in markdown here'`

### `hidden_tests/test_hidden_behavior.py::test_no_frontmatter_returns_empty_metadata`

- mapping: `B002, B005`
- API: `featurelifted.loads`
- risk: `none`
- A001 `assert` L37: `post.metadata == {}`
- A002 `assert` L38: `post.content == text`

### `hidden_tests/test_hidden_behavior.py::test_empty_frontmatter_block`

- mapping: `B001`
- API: `featurelifted.loads`
- risk: `none`
- A001 `assert` L44: `post.metadata == {}`
- A002 `assert` L45: `post.content == 'I have frontmatter but no metadata.'`

### `hidden_tests/test_hidden_behavior.py::test_unicode_metadata_roundtrip`

- mapping: `B002, B005`
- API: `featurelifted.dumps, featurelifted.loads`
- risk: `none`
- A001 `assert` L59: `'中文' in output`
- A002 `assert` L61: `repost['language'] == '中文'`
- A003 `assert` L62: `repost.content == post.content`

### `hidden_tests/test_hidden_behavior.py::test_parse_defaults_merge`

- mapping: `B004`
- API: `featurelifted.parse`
- risk: `none`
- A001 `assert` L68: `metadata['author'] == 'bob'`
- A002 `assert` L69: `metadata['site'] == 'default-site'`
- A003 `assert` L70: `content.strip() == 'Hello'`
- A004 `assert` L73: `plain_metadata == {'site': 'default-site'}`
- A005 `assert` L74: `plain_content == 'plain body only'`

### `hidden_tests/test_hidden_behavior.py::test_post_to_dict`

- mapping: `B005`
- API: `featurelifted.loads`
- risk: `none`
- A001 `assert` L80: `payload['title'] == 'X'`
- A002 `assert` L81: `payload['content'] == 'body'`

### `hidden_tests/test_hidden_behavior.py::test_checks_detects_frontmatter`

- mapping: `B003`
- API: `featurelifted.checks`
- risk: `none`
- A001 `assert` L85: `checks('---\nx: 1\n---\n\nbody') is True`
- A002 `assert` L86: `checks('plain text without frontmatter') is False`
- A003 `assert` L87: `checks('---\n---\n\nempty metadata block') is True`

### `hidden_tests/test_hidden_behavior.py::test_custom_dump_delimiters`

- mapping: `B002`
- API: `featurelifted.dumps, featurelifted.loads`
- risk: `none`
- A001 `assert` L93: `dump.startswith('+++')`
- A002 `assert` L94: `dump.count('+++') >= 2`
- A003 `assert` L95: `'title: Hi' in dump`
- A004 `assert` L96: `dump.strip().endswith('body')`

### `hidden_tests/test_hidden_behavior.py::test_no_frontmatter_import_surface`

- mapping: `B007`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L109: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.Post, featurelifted.checks, featurelifted.dump, featurelifted.dumps, featurelifted.load, featurelifted.loads, featurelifted.parse`
- risk: `none`
- A001 `assert` L15: `isinstance(Post, type)`
- A002 `assert` L16: `Post is not None`
- A003 `assert` L17: `Post is not None`
- A004 `assert` L18: `hasattr(Post, 'to_dict')`
- A005 `assert` L19: `callable(parse)`
- A006 `assert` L20: `callable(load)`
- A007 `assert` L21: `callable(loads)`
- A008 `assert` L22: `callable(dump)`
- A009 `assert` L23: `callable(dumps)`
- A010 `assert` L24: `callable(checks)`

## Dependency / Oracle Evidence

- allowed dependencies: `PyYAML`
- forbidden imports: `frontmatter`
- source entrypoints: `frontmatter.parse, frontmatter.load, frontmatter.loads, frontmatter.dump, frontmatter.dumps, frontmatter.checks, frontmatter.Post, frontmatter.default_handlers.YAMLHandler`
- oracle source files: `frontmatter/__init__.py, frontmatter/default_handlers.py, frontmatter/util.py, frontmatter/py.typed`
- runtime dependencies: `PyYAML`
- oracle notes: Oracle copies YAML front matter runtime only; PyYAML is pinned in requirements.lock for Docker eval.
