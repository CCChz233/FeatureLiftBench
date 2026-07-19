# FeatureLift Task: Typed environment variable parsing

Extract environs Env typed parsers with marshmallow field deserialization, custom validators, list/dict subcasts, expand_vars, prefix, and deferred seal validation without importing environs or python-dotenv.

## Target API

- Import: `import featurelifted; from featurelifted import Env, EnvError, EnvValidationError, EnvSealedError, ParserConflictError, ValidationError, validate`
- Callable: `featurelifted.Env`
- Signature: `Env(*, eager=True, expand_vars=False, prefix=None)`

## Excluded Behavior

- read_env dotenv file loading and FileAwareEnv file indirection
- django URL parsers (dj_db_url, dj_email_url, dj_cache_url)
- module-level env singleton, upstream tests, docs, and packaging metadata
- original environs import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `environs`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — typed casting for int, bool, str with defaults and eager errors
- **B002** — marshmallow validate= callables and validators on parsed fields
- **B003** — list and dict env strings with delimiter/subcast preprocessing
- **B004** — expand_vars ${VAR:-default} substitution in env values
- **B005** — constructor and context-manager prefix for env key names
- **B006** — deferred validation via eager=False and seal() error aggregation
- **B007** — custom timedelta duration strings via fields.TimeDelta
- **B008** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B009** — the submitted package does not import forbidden upstream packages: environs
<!-- featureliftbench:behavior-clauses:end -->
