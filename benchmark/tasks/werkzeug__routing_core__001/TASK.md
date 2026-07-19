# FeatureLift Task: URL routing map and adapter

Extract Werkzeug URL routing: Map, Rule, converters, match, and build.

## Target API

- Import: `from featurelifted.routing import Map, Rule, MapAdapter, Subdomain, Submount; from featurelifted.routing.exceptions import RequestRedirect`
- Callable: `featurelifted.routing.Map`
- Signature: `Map(rules=None, default_subdomain='', **options)`

## Excluded Behavior

- WSGI request/response wrappers
- development server and middleware
- form parsing and file uploads
- original project tests and CLI

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `werkzeug`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — define URL rules with converters and HTTP methods
- **B002** — match paths to endpoints with argument extraction
- **B003** — build URLs from endpoints and arguments
- **B004** — subdomain and submount rule factories
- **B005** — redirect and alias redirect exceptions on match
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: werkzeug
<!-- featureliftbench:behavior-clauses:end -->
