# FeatureLift Task: Multipart form-data parse core

Extract python-multipart streaming multipart/form-data parsing over offline byte buffers with Field/File storage, Content-Transfer-Encoding decoders, and header parsing without importing python_multipart or ASGI frameworks.

## Target API

- Import: `import featurelifted; from featurelifted import Field, File, FormParser, parse_form, create_form_parser, parse_options_header; from featurelifted.exceptions import FormParserError, MultipartParseError, FileError, DecodeError`
- Callable: `featurelifted.FormParser`
- Signature: `FormParser(content_type, on_field, on_file, on_end=None, boundary=None, file_name=None, config={})`

## Excluded Behavior

- application/x-www-form-urlencoded and application/octet-stream FormParser branches
- ASGI/Starlette/FastAPI request integration
- fuzz harness, upstream pytest suite, docs, and CI
- original python_multipart import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `python_multipart`, `multipart`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — incremental multipart/form-data parsing via FormParser.write/finalize
- **B002** — field and file parts with Content-Disposition, Content-Type, and filename
- **B003** — parse_options_header boundary extraction from Content-Type
- **B004** — base64 and quoted-printable Content-Transfer-Encoding
- **B005** — preamble before first boundary and epilogue after closing boundary
- **B006** — MAX_MEMORY_FILE_SIZE spill to disk and configurable upload directory
- **B007** — MAX_HEADER_COUNT and MAX_HEADER_SIZE enforcement
- **B008** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B009** — the submitted package does not import forbidden upstream packages: python_multipart, multipart
<!-- featureliftbench:behavior-clauses:end -->
