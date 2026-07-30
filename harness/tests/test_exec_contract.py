"""Unit tests for Execution-Guided Contract helpers."""

from __future__ import annotations

import json
import tempfile
import textwrap
import unittest
from pathlib import Path

from featureliftbench.ablation import AblationOptions
from featureliftbench.ablation import resolve_ablation_options
from featureliftbench.exec_contract.audit import compute_contract_gate_ok
from featureliftbench.exec_contract.common import flatten_required_api
from featureliftbench.exec_contract.common import keywords_from_public_spec
from featureliftbench.exec_contract.select_tests import select_upstream_tests
from featureliftbench.exec_contract.synthesize import infer_api_from_upstream
from featureliftbench.exec_contract.synthesize import synthesize_contracts
from featureliftbench.exec_contract.workspace import install_exec_contract_workspace


class ExecContractAblationTests(unittest.TestCase):
    def test_arm_name(self) -> None:
        self.assertEqual(
            AblationOptions(exec_contract=True).ablation_arm, "exec_contract"
        )

    def test_mutually_exclusive_with_td(self) -> None:
        with self.assertRaises(ValueError):
            AblationOptions(td_cognition=True, exec_contract=True)

    def test_resolve_from_profile(self) -> None:
        options = resolve_ablation_options(profile={"exec_contract": True})
        self.assertTrue(options.exec_contract)
        self.assertEqual(options.ablation_arm, "exec_contract")


class ExecContractSelectSynthesizeTests(unittest.TestCase):
    def test_keywords_strip_stopwords(self) -> None:
        keys = keywords_from_public_spec(
            {
                "title": "LazyCommandCollection",
                "required_api": [
                    {
                        "path": "featurelifted.LazyCommandCollection",
                        "kind": "class",
                        "members": [
                            {
                                "path": "featurelifted.LazyCommandCollection.resolve",
                                "kind": "method",
                            }
                        ],
                    }
                ],
                "behaviors": [
                    {
                        "id": "B001",
                        "text": "When a command name is requested, the package returns it.",
                    }
                ],
            }
        )
        self.assertIn("lazycommandcollection", keys)
        self.assertNotIn("when", keys)
        self.assertNotIn("the", keys)
        self.assertNotIn("api", keys)

    def test_select_demotes_db_backends(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            tests = repo / "tests"
            tests.mkdir(parents=True)
            (tests / "test_revision.py").write_text(
                "def test_revision_map():\n    assert True\n",
                encoding="utf-8",
            )
            (tests / "test_mysql.py").write_text(
                "def test_mysql_revision():\n    assert True\n",
                encoding="utf-8",
            )
            public_spec = {
                "title": "RevisionMap",
                "source_entrypoints": ["alembic.ddl.RevisionMap"],
                "required_api": [
                    {"path": "featurelifted.RevisionMap", "kind": "class"}
                ],
            }
            selected = select_upstream_tests(repo, public_spec, max_files=2)
            self.assertTrue(any("revision" in s for s in selected))
            self.assertFalse(any("mysql" in s for s in selected))

    def test_infer_invoke_from_upstream_ast(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pkg = root / "click"
            pkg.mkdir()
            (pkg / "__init__.py").write_text("", encoding="utf-8")
            (pkg / "core.py").write_text(
                textwrap.dedent(
                    """
                    class Context:
                        default_map = None
                        auto_envvar_prefix = None

                    class LazyCommandCollection:
                        def __init__(self, sources, envvar=None):
                            pass
                        def get_command(self, name):
                            pass
                        def resolve(self, argv):
                            pass
                        def invoke(self, args):
                            pass
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            public_spec = {
                "title": "LazyCommandCollection",
                "source_entrypoints": ["click.core.LazyCommandCollection"],
                "required_api": [
                    {
                        "path": "featurelifted.LazyCommandCollection",
                        "kind": "class",
                        "members": [
                            {
                                "path": "featurelifted.LazyCommandCollection.resolve",
                                "kind": "method",
                            }
                        ],
                    }
                ],
            }
            inferred = infer_api_from_upstream(root, public_spec)
            self.assertIn("invoke", inferred["methods"])
            paths = {a["path"] for a in inferred["api"]}
            self.assertIn("featurelifted.LazyCommandCollection.invoke", paths)

    def test_infer_lazy_alias_and_inherited_invoke(self) -> None:
        """Frozen click may only have CommandCollection; invoke lives on Group."""

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pkg = root / "click"
            pkg.mkdir()
            (pkg / "__init__.py").write_text("", encoding="utf-8")
            (pkg / "core.py").write_text(
                textwrap.dedent(
                    """
                    class Context:
                        default_map = None

                    class Command:
                        def invoke(self, ctx):
                            return "ok"

                    class Group(Command):
                        def get_command(self, ctx, name):
                            pass

                    class CommandCollection(Group):
                        def list_commands(self, ctx):
                            return []
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            public_spec = {
                "title": "LazyCommandCollection",
                "source_entrypoints": ["click.core.LazyCommandCollection"],
                "required_api": [
                    {
                        "path": "featurelifted.LazyCommandCollection",
                        "kind": "class",
                        "members": [
                            {
                                "path": "featurelifted.LazyCommandCollection.get_command",
                                "kind": "method",
                            }
                        ],
                    }
                ],
            }
            inferred = infer_api_from_upstream(root, public_spec)
            self.assertIn("invoke", inferred["methods"])
            self.assertIn("get_command", inferred["methods"])
            paths = {a["path"] for a in inferred["api"]}
            self.assertIn("featurelifted.LazyCommandCollection.invoke", paths)
            self.assertIn("featurelifted.LazyCommandCollection.get_command", paths)

    def test_synthesize_scenarios_not_assert_true(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            tests = repo / "tests"
            tests.mkdir(parents=True)
            (tests / "test_evict.py").write_text(
                "def test_evict():\n    assert True\n",
                encoding="utf-8",
            )
            click = repo / "click"
            click.mkdir()
            (click / "__init__.py").write_text("", encoding="utf-8")
            (click / "core.py").write_text(
                textwrap.dedent(
                    """
                    class Context:
                        default_map = None

                    class LazyCommandCollection:
                        def get_command(self, name):
                            pass
                        def resolve(self, argv):
                            pass
                        def invoke(self, args):
                            pass
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            public_spec = {
                "title": "LazyCommandCollection",
                "source_entrypoints": ["click.core.LazyCommandCollection"],
                "required_api": [
                    {
                        "path": "featurelifted.LazyCommandCollection",
                        "kind": "class",
                        "members": [
                            {
                                "path": "featurelifted.LazyCommandCollection.get_command",
                                "kind": "method",
                            },
                            {
                                "path": "featurelifted.LazyCommandCollection.resolve",
                                "kind": "method",
                            },
                        ],
                    },
                    {"path": "featurelifted.Command", "kind": "class"},
                ],
                "behaviors": [
                    {
                        "id": "B002",
                        "text": "When a context is created, envvar settings are propagated.",
                    }
                ],
            }
            install_exec_contract_workspace(root)
            (root / "runtime_traces").mkdir(exist_ok=True)
            (root / "runtime_traces" / "traces.jsonl").write_text("", encoding="utf-8")
            meta = synthesize_contracts(
                root, public_spec, collect_meta={"trace_quality": "low"}
            )
            self.assertTrue(meta["contracts_substantive"])
            self.assertGreaterEqual(meta["scenario_assertions"], 2)
            scenario = (root / "contracts" / "test_behavior_scenarios.py").read_text(
                encoding="utf-8"
            )
            self.assertIn("invoke", scenario)
            self.assertIn("test_invoke_runs_callback_over_argv", scenario)
            self.assertIn("test_resolve_returns_context_command_and_remaining_argv", scenario)
            self.assertIn("FLB_FEATURE_DEFAULTS", scenario)
            surface = (root / "contracts" / "test_required_surface.py").read_text(
                encoding="utf-8"
            )
            self.assertNotIn("format_help", surface)
            # Must NOT leak benchmark failure strings / eval graphs.
            self.assertNotIn("no such command", scenario)
            self.assertNotIn("feature_tip", scenario)
            self.assertNotIn("FLB_CLICK_DEFAULTS", scenario)
            self.assertNotIn("assert True", scenario)
            checklist = (root / "contracts" / "test_behavior_checklist.py").read_text(
                encoding="utf-8"
            )
            self.assertNotIn("assert True", checklist)

    def test_synthesize_alembic_eval_blind_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            (repo / "tests").mkdir(parents=True)
            (repo / "tests" / "test_revision.py").write_text(
                "def test_revision():\n    assert True\n", encoding="utf-8"
            )
            alembic = repo / "alembic" / "script"
            alembic.mkdir(parents=True)
            (repo / "alembic" / "__init__.py").write_text("", encoding="utf-8")
            (alembic / "__init__.py").write_text("", encoding="utf-8")
            (alembic / "revision.py").write_text(
                textwrap.dedent(
                    """
                    class Revision:
                        pass

                    class RevisionMap:
                        def get_revision(self, id_):
                            pass
                        def get_heads(self):
                            pass
                        def ancestors(self, revision_id, include_dependencies=True):
                            pass
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            public_spec = {
                "title": "RevisionMap",
                "source_entrypoints": ["alembic.script.revision.RevisionMap"],
                "required_api": [
                    {
                        "path": "featurelifted.RevisionMap",
                        "kind": "class",
                        "members": [
                            {
                                "path": "featurelifted.RevisionMap.get_revision",
                                "kind": "method",
                            },
                            {
                                "path": "featurelifted.RevisionMap.ancestors",
                                "kind": "method",
                            },
                        ],
                    },
                    {"path": "featurelifted.Revision", "kind": "class"},
                    {"path": "featurelifted.MissingRevision", "kind": "exception"},
                ],
                "behaviors": [],
            }
            install_exec_contract_workspace(root)
            (root / "runtime_traces").mkdir(exist_ok=True)
            (root / "runtime_traces" / "traces.jsonl").write_text("", encoding="utf-8")
            meta = synthesize_contracts(
                root, public_spec, collect_meta={"trace_quality": "medium"}
            )
            self.assertTrue(meta["contracts_substantive"])
            self.assertGreaterEqual(meta["scenario_assertions"], 2)
            scenario = (root / "contracts" / "test_behavior_scenarios.py").read_text(
                encoding="utf-8"
            )
            self.assertIn("MissingRevision", scenario)
            self.assertIn("test_ancestors_excludes_self_on_linear_chain", scenario)
            self.assertIn("test_revision_down_revision_defaults_to_none", scenario)
            self.assertIn("test_merge_graph_heads_and_branch_point", scenario)
            self.assertIn("test_symbolic_head_and_base_via_get_revision", scenario)
            # Leaky eval-graph scenarios must be gone.
            self.assertNotIn("test_heads_order_with_dependency_branch", scenario)
            self.assertNotIn("feature_tip", scenario)
            self.assertNotIn("test_literal_revision_id_base", scenario)
            self.assertNotIn("assert True", scenario)

    def test_gate_rejects_vacuous_green(self) -> None:
        self.assertFalse(
            compute_contract_gate_ok(
                collect_meta={"trace_quality": "medium"},
                synthesize_meta={"contracts_substantive": False, "scenario_assertions": 0},
                verify_final={"ok": True},
            )
        )
        self.assertFalse(
            compute_contract_gate_ok(
                collect_meta={"trace_quality": "medium"},
                synthesize_meta={"contracts_substantive": True, "scenario_assertions": 1},
                verify_final={"ok": True},
            )
        )
        self.assertTrue(
            compute_contract_gate_ok(
                collect_meta={"trace_quality": "medium"},
                synthesize_meta={"contracts_substantive": True, "scenario_assertions": 2},
                verify_final={"ok": True, "stdout_tail": "5 passed in 0.01s"},
            )
        )
        self.assertFalse(
            compute_contract_gate_ok(
                collect_meta={"trace_quality": "medium"},
                synthesize_meta={"contracts_substantive": True, "scenario_assertions": 2},
                verify_final={"ok": True, "stdout_tail": "3 passed, 9 skipped in 0.01s"},
            )
        )


if __name__ == "__main__":
    unittest.main()
