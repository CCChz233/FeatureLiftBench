# Repository Semantic Graph

This package builds a deterministic, language-neutral repository skeleton with
Tree-sitter. JSONL is the authoritative snapshot format; queries use an in-memory
index and return bounded JSON suitable for Agent tool calls.

Install the parser stack:

```bash
python -m pip install -e '.[repo-graph]'
```

Build and query a snapshot:

```bash
flb-rsg build --repo benchmark/tasks/sqlparse__token_tree_core__001/repo --output /tmp/sqlparse-rsg
flb-rsg self-check --graph /tmp/sqlparse-rsg
flb-rsg search --graph /tmp/sqlparse-rsg TokenList
flb-rsg inspect --graph /tmp/sqlparse-rsg python:sqlparse.sql.TokenList:class
flb-rsg closure --graph /tmp/sqlparse-rsg python:sqlparse.sql.TokenList:class
flb-rsg risks --graph /tmp/sqlparse-rsg
```

The same commands are available through
`python -m featureliftbench.repo_graph.cli`. Snapshots contain repository-relative
paths only. Unresolved dynamic calls remain `candidate`/`unresolved`; they are not
promoted to exact dependencies merely to increase recall.

Enable the run-local integration with an opt-in agent profile:

```toml
repo_graph_mode = "static"       # static | closure | evidence
repo_graph_transport = "cli"
repo_graph_fail_fast = true
repo_graph_bootstrap_max_nodes = 30
repo_graph_bootstrap_max_chars = 4096
repo_graph_query_max_chars = 12000
```

When enabled, the runner builds or loads a cache entry outside the Agent mount,
copies a private snapshot into `agent/state/repo_graph/base`, creates a task-only
overlay, appends one common bootstrap to `TASK.md`, and performs a post-run
submission comparison. Existing profiles remain disabled and produce no graph
files or prompt changes.

Inside a run, `--graph` is optional because the CLI resolves
`FEATURELIFTBENCH_REPO_GRAPH_ROOT`:

```bash
flb-rsg task-closure       # required once before broad source exploration
flb-rsg search Parser      # optional follow-up localization
flb-rsg submission-check  # required after the final submission change
```

Every successful or failed invocation is appended to
`agent/repo_graph_queries.jsonl` with bounded parameter metadata, submission
revision, response size, result digest, and error class. Response bodies and
credentials are not copied into this audit. The runner reports adoption
separately from evaluator correctness; missing RSG adoption never changes the
formal score.

Evidence mode adds append-only claims and bounded evidence summaries:

```bash
flb-rsg detectors
flb-rsg claim add --subject python:pkg.Symbol:function --predicate IMPLEMENTS_BEHAVIOR
flb-rsg evidence record --kind runtime_probe --probe-type representative_call \
  --evidence-class runtime --status supports --result-summary "probe passed"
flb-rsg freshness
flb-rsg stopping-check
```

OpenHands and mini-swe-agent receive these as advisory tools. FeatureLiftAgent also
exposes bounded graph-query/claim actions, automatically syncs after mutations,
records public/final verification evidence, and enforces the freshness stopping
guard. The two control regimes must be reported separately.

The 2026-07-23 clean OpenHands paid gate stopped after 2/12 cells because P3
called `submission-check` but skipped `task-closure`. Therefore the CLI
transport is not considered adoption-ready for the Pilot. A run-local native
OpenHands tool adapter is the next required mechanism gate; the remaining ten
cells must not run until a new real smoke observes both required calls.

Run the Python-150 offline audit with:

```bash
PYTHONPATH=harness python harness/scripts/audit_repo_graph_python150.py \
  --output reports/repo_graph_phase1/python150_audit.json
```

Phase 1 quality results remain in `reports/repo_graph_phase1`. Phase 2/3 integration
is covered by runner, Docker-path, revision, evidence, and stopping-guard tests; it
does not by itself establish a task-success or token-efficiency gain.
