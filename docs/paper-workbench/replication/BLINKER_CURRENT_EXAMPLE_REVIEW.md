# Present-day Blinker contract/test inspection

Date: 2026-09-27. Reviewer: Codex (AI-assisted retrospective inspection).
This is not an historical author review, independent human review, or complete
assessment of every Blinker behavior.

The frozen task `blinker__signal_registry_core__001` is linked to the pinned
Blinker source snapshot and exposes `Signal`, `Namespace`, and `ANY` through the
new `featurelifted` package. `metadata.public_spec` contains stable public
clauses B001--B006. The generated `TASK.md` includes the required API,
sender-specific dispatch, weak receiver lifetime, namespace identity, declared
exclusions, and forbidden upstream imports.

Observed test-to-clause relationships from reading the included test bodies:

| Test node | Directly exercised public clauses |
| --- | --- |
| `public_tests/test_public_contract.py::test_sender_filtering_and_responses` | B001 (dispatch/responses), B002 (sender filtering) |
| `public_tests/test_public_contract.py::test_namespace_identity` | B004 (stable signal per name) |
| `hidden_tests/test_hidden_contract.py::test_weak_receiver_cleanup` | B003 (weak-receiver cleanup) |
| `hidden_tests/test_hidden_contract.py::test_connected_to_scope_and_disconnect` | B001 (connection scope/disconnect), B002 (sender filtering) |
| `hidden_tests/test_required_api_surface.py::test_required_api_surface` | B005 (declared API surface) |

B006 is enforced by the separate source-isolation configuration, rather than
one of these behavioral test nodes. The original `behavior_contract.json`
assigns B001--B004 to each of the four behavior tests. Those stored links are
structurally valid but broader than what each individual test body directly
checks. This present-day table is an interpretive refinement, not a mutation
of the historical mapping. The current structural validator passes the task,
but that pass alone does not certify the semantic precision of every mapping.

The saved reference-replay ledger records three passes for this frozen task.
The evidence bundle does not rerun them.
