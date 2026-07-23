"""Python Tree-sitter adapter for definitions, dependencies, calls, and risk cues."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from ...models import EdgeSpec, NodeSpec, ParsedFile
from ...parsing.base import LanguageAdapter, LanguageCapability
from ...parsing.tree_sitter_backend import TreeSitterBackend
from ..common import (
    first_string_literal,
    load_query,
    nearest_ancestor,
    node_key,
    node_text,
    query_pack_hash,
    source_span,
)
from .resolver import PythonResolver


class PythonAdapter(LanguageAdapter):
    language = "python"
    extensions = (".py", ".pyi")
    version = "python-adapter-v1"
    capability = LanguageCapability(
        language="python",
        node_kinds=(
            "class",
            "dependency",
            "environment_variable",
            "file",
            "function",
            "global_state",
            "method",
            "module",
            "resource",
            "working_directory",
        ),
        edge_kinds=(
            "CALLS",
            "DECORATED_BY",
            "DEFINES",
            "DYNAMIC_GETATTR",
            "DYNAMIC_IMPORT",
            "INHERITS",
            "LOADS_RESOURCE",
            "MODULE_STATE",
            "MUTABLE_GLOBAL",
            "READS_CWD",
            "READS_ENV",
            "REGISTERS",
            "WRITES_CWD",
        ),
        limitations=("no type inference", "dynamic dispatch remains candidate/unresolved"),
    )

    def __init__(self) -> None:
        self.query_dir = Path(__file__).with_name("queries")

    def query_pack_hash(self) -> str:
        return query_pack_hash(self.query_dir)

    def resolver(self) -> PythonResolver:
        return PythonResolver()

    def parse(
        self,
        *,
        path: Path,
        relative_path: str,
        source: bytes,
        backend: TreeSitterBackend,
    ) -> ParsedFile:
        tree = backend.parse(self.language, source)
        root = tree.root_node
        module_name = self._module_name(relative_path)
        file_id = f"file:{relative_path}:file"
        module_id = f"python:{module_name}:module"
        parsed = ParsedFile(
            nodes=[
                NodeSpec(
                    stable_id=file_id,
                    kind="file",
                    name=Path(relative_path).name,
                    qualified_name=relative_path,
                    language=self.language,
                    span=source_span(root, relative_path),
                    attributes={"source_bytes": len(source), "parse_error": root.has_error},
                ),
                NodeSpec(
                    stable_id=module_id,
                    kind="module",
                    name=module_name.rsplit(".", 1)[-1],
                    qualified_name=module_name,
                    language=self.language,
                    span=source_span(root, relative_path),
                ),
            ],
            edges=[
                EdgeSpec(file_id, module_id, "DEFINES", "exact", self.version),
            ],
            metadata={"language": self.language, "module": module_name, "parse_error": root.has_error},
        )

        captures = backend.captures(
            self.language,
            load_query(self.query_dir, "symbols.scm"),
            root,
        )
        definitions: list[tuple[Any, str]] = []
        definitions.extend((node, "class") for node in captures.get("class.definition", []))
        definitions.extend((node, "function") for node in captures.get("function.definition", []))
        definitions.sort(key=lambda item: (item[0].start_byte, -item[0].end_byte, item[1]))
        definition_keys = {node_key(node) for node, _kind in definitions}
        stable_by_key: dict[tuple[int, int, str], str] = {}
        kind_by_key: dict[tuple[int, int, str], str] = {}
        ordinal: defaultdict[str, int] = defaultdict(int)

        for definition, raw_kind in definitions:
            name_node = definition.child_by_field_name("name")
            if name_node is None:
                continue
            name = node_text(name_node, source)
            parent_key = nearest_ancestor(definition, definition_keys)
            parent_stable = stable_by_key.get(parent_key) if parent_key else None
            parent_kind = kind_by_key.get(parent_key) if parent_key else None
            if parent_stable:
                parent_qualified = next(
                    node.qualified_name for node in parsed.nodes if node.stable_id == parent_stable
                )
                qualified = f"{parent_qualified}.{name}"
            else:
                qualified = f"{module_name}.{name}"
            kind = "method" if raw_kind == "function" and parent_kind == "class" else raw_kind
            base_id = f"python:{qualified}:{kind}"
            definition_ordinal = ordinal[base_id]
            ordinal[base_id] += 1
            stable_id = base_id if definition_ordinal == 0 else f"{base_id}#{definition_ordinal}"
            first_line = node_text(definition, source).splitlines()[0].strip()
            parsed.nodes.append(
                NodeSpec(
                    stable_id=stable_id,
                    kind=kind,
                    name=name,
                    qualified_name=qualified,
                    language=self.language,
                    span=source_span(definition, relative_path),
                    attributes={
                        "module": module_name,
                        "signature": first_line,
                        "definition_ordinal": definition_ordinal,
                    },
                )
            )
            owner = parent_stable or module_id
            parsed.edges.append(EdgeSpec(owner, stable_id, "DEFINES", "exact", self.version))
            if raw_kind == "class":
                superclasses = definition.child_by_field_name("superclasses")
                if superclasses is not None:
                    for superclass in superclasses.named_children:
                        expression = "".join(node_text(superclass, source).split())
                        if expression:
                            parsed.edges.append(
                                EdgeSpec(
                                    stable_id,
                                    None,
                                    "INHERITS",
                                    "unresolved",
                                    self.version,
                                    {
                                        "target_expression": expression[:300],
                                        "module": module_name,
                                        "scope_qualified": qualified,
                                    },
                                )
                            )
            key = node_key(definition)
            stable_by_key[key] = stable_id
            kind_by_key[key] = raw_kind

        self._add_imports(
            parsed,
            backend,
            root,
            source,
            module_id,
            module_name,
            relative_path,
        )
        self._add_globals(parsed, backend, root, source, module_id, module_name, relative_path)
        self._add_calls_and_risks(
            parsed,
            backend,
            root,
            source,
            module_id,
            module_name,
            relative_path,
            definition_keys,
            stable_by_key,
        )
        self._add_environment_reads(
            parsed,
            backend,
            root,
            source,
            module_id,
            module_name,
            relative_path,
            definition_keys,
            stable_by_key,
        )
        self._add_file_context_reads(
            parsed,
            backend,
            root,
            source,
            module_id,
            module_name,
            relative_path,
            definition_keys,
            stable_by_key,
        )
        self._add_decorators(
            parsed,
            backend,
            root,
            source,
            definition_keys,
            stable_by_key,
        )
        return parsed

    @staticmethod
    def _module_name(relative_path: str) -> str:
        parts = list(Path(relative_path).with_suffix("").parts)
        if parts and parts[0] in {"src", "lib"}:
            parts.pop(0)
        if parts and parts[-1] == "__init__":
            parts.pop()
        return ".".join(parts) or Path(relative_path).parent.name or "__root__"

    def _add_imports(
        self,
        parsed: ParsedFile,
        backend: TreeSitterBackend,
        root: Any,
        source: bytes,
        module_id: str,
        module_name: str,
        relative_path: str,
    ) -> None:
        captures = backend.captures(
            self.language,
            load_query(self.query_dir, "imports.scm"),
            root,
        )
        seen: set[tuple[str, int]] = set()
        for statement in sorted(captures.get("import.statement", []), key=lambda node: node.start_byte):
            text = node_text(statement, source)
            modules: list[str] = []
            if statement.type == "future_import_statement":
                modules.append("__future__")
            elif statement.type == "import_from_statement":
                module_node = statement.child_by_field_name("module_name")
                if module_node is not None:
                    modules.append(node_text(module_node, source))
            else:
                body = text.strip()[len("import ") :]
                modules.extend(part.strip().split(" as ", 1)[0] for part in body.split(","))
            for imported in modules:
                imported = imported.strip()
                if not imported or (imported, statement.start_byte) in seen:
                    continue
                seen.add((imported, statement.start_byte))
                dependency_id = f"python:{imported}:dependency"
                parsed.nodes.append(
                    NodeSpec(
                        stable_id=dependency_id,
                        kind="dependency",
                        name=imported.rsplit(".", 1)[-1],
                        qualified_name=imported,
                        language=self.language,
                        attributes={"declared_by": module_name},
                    )
                )
                parsed.edges.append(
                    EdgeSpec(
                        module_id,
                        dependency_id,
                        "IMPORTS_MODULE",
                        "exact",
                        self.version,
                        {
                            "target_module": imported,
                            "statement": " ".join(text.split())[:300],
                            "path": relative_path,
                            "line": statement.start_point[0] + 1,
                        },
                    )
                )

    def _add_globals(
        self,
        parsed: ParsedFile,
        backend: TreeSitterBackend,
        root: Any,
        source: bytes,
        module_id: str,
        module_name: str,
        relative_path: str,
    ) -> None:
        captures = backend.captures(
            self.language,
            load_query(self.query_dir, "state.scm"),
            root,
        )
        for assignment in captures.get("module.assignment", []):
            if assignment.parent is None or assignment.parent.type not in {"module", "expression_statement"}:
                continue
            if assignment.parent.type == "expression_statement" and assignment.parent.parent != root:
                continue
            left = assignment.child_by_field_name("left")
            if left is None or left.type != "identifier":
                continue
            name = node_text(left, source)
            right = assignment.child_by_field_name("right")
            initializer_kind = right.type if right is not None else "unknown"
            is_mutable = initializer_kind in {
                "dictionary",
                "dictionary_comprehension",
                "list",
                "list_comprehension",
                "set",
                "set_comprehension",
            }
            lowered_name = name.casefold()
            state_cue = initializer_kind == "call" or any(
                cue in lowered_name for cue in ("cache", "registry", "state", "singleton", "pool")
            )
            stable_id = f"python:{module_name}.{name}:global_state"
            parsed.nodes.append(
                NodeSpec(
                    stable_id=stable_id,
                    kind="global_state",
                    name=name,
                    qualified_name=f"{module_name}.{name}",
                    language=self.language,
                    span=source_span(assignment, relative_path),
                    attributes={
                        "mutable": is_mutable,
                        "initializer_kind": initializer_kind,
                        "state_cue": state_cue,
                        **({"risk_category": "parser_state_coupling"} if is_mutable or state_cue else {}),
                    },
                )
            )
            parsed.edges.append(EdgeSpec(module_id, stable_id, "DEFINES", "exact", self.version))
            if is_mutable:
                parsed.edges.append(
                    EdgeSpec(
                        module_id,
                        stable_id,
                        "MUTABLE_GLOBAL",
                        "exact",
                        self.version,
                        {"risk_category": "parser_state_coupling"},
                    )
                )
            elif state_cue:
                parsed.edges.append(
                    EdgeSpec(
                        module_id,
                        stable_id,
                        "MODULE_STATE",
                        "candidate",
                        self.version,
                        {"risk_category": "parser_state_coupling"},
                    )
                )

    def _add_calls_and_risks(
        self,
        parsed: ParsedFile,
        backend: TreeSitterBackend,
        root: Any,
        source: bytes,
        module_id: str,
        module_name: str,
        relative_path: str,
        definition_keys: set[tuple[int, int, str]],
        stable_by_key: dict[tuple[int, int, str], str],
    ) -> None:
        captures = backend.captures(
            self.language,
            load_query(self.query_dir, "calls.scm"),
            root,
        )
        for call in sorted(captures.get("call.expression", []), key=lambda node: node.start_byte):
            function = call.child_by_field_name("function")
            if function is None:
                continue
            expression = "".join(node_text(function, source).split())
            ancestor_key = nearest_ancestor(call, definition_keys)
            source_id = stable_by_key.get(ancestor_key, module_id)
            scope = next(
                (node.qualified_name for node in parsed.nodes if node.stable_id == source_id),
                module_name,
            )
            kind = "CALLS"
            attributes: dict[str, Any] = {
                "target_expression": expression[:300],
                "module": module_name,
                "scope_qualified": scope,
                "path": relative_path,
                "line": call.start_point[0] + 1,
            }
            target_id: str | None = None
            resolution = "unresolved"
            lowered = expression.lower()
            literal = first_string_literal(node_text(call, source))
            if expression in {"getattr", "setattr", "hasattr"} or lowered.endswith(
                (".getattr", ".setattr", ".hasattr")
            ):
                kind = "DYNAMIC_GETATTR" if "getattr" in lowered or "hasattr" in lowered else "DYNAMIC_SETATTR"
                attributes["risk_category"] = "reflection"
            elif expression in {"__import__", "importlib.import_module"} or lowered.endswith(
                ".import_module"
            ):
                kind = "DYNAMIC_IMPORT"
                attributes["risk_category"] = "import_side_effect"
            elif expression in {"os.getenv", "os.environ.get"} or lowered.endswith(".getenv"):
                kind = "READS_ENV"
                attributes["risk_category"] = "config_environment_coupling"
                if literal:
                    target_id = f"env:{literal}:environment_variable"
                    parsed.nodes.append(
                        NodeSpec(target_id, "environment_variable", literal, literal, attributes={})
                    )
                    resolution = "exact"
            elif expression in {"os.getcwd", "pathlib.Path.cwd", "Path.cwd"} or lowered.endswith(
                ".getcwd"
            ):
                kind = "READS_CWD"
                target_id = "environment:cwd:working_directory"
                parsed.nodes.append(
                    NodeSpec(target_id, "working_directory", "cwd", "current working directory")
                )
                resolution = "exact"
                attributes["risk_category"] = "config_environment_coupling"
            elif expression == "os.chdir" or lowered.endswith(".chdir"):
                kind = "WRITES_CWD"
                target_id = "environment:cwd:working_directory"
                parsed.nodes.append(
                    NodeSpec(target_id, "working_directory", "cwd", "current working directory")
                )
                resolution = "exact"
                attributes["risk_category"] = "config_environment_coupling"
            elif any(token in lowered for token in ("importlib.resources", "pkgutil.get_data")):
                kind = "LOADS_RESOURCE"
                attributes["risk_category"] = "resource_coupling"
                if literal:
                    target_id = f"resource:{module_name}:{literal}:resource"
                    parsed.nodes.append(
                        NodeSpec(target_id, "resource", Path(literal).name, literal, self.language)
                    )
                    resolution = "candidate"
            elif literal and (
                expression in {"open", "Path", "pathlib.Path"}
                or lowered.endswith((".open", ".read_text", ".read_bytes"))
            ):
                kind = "LOADS_RESOURCE"
                target_id = f"resource:{module_name}:{literal}:resource"
                parsed.nodes.append(
                    NodeSpec(target_id, "resource", Path(literal).name, literal, self.language)
                )
                resolution = "candidate"
                attributes["risk_category"] = "resource_coupling"
            elif lowered.endswith((".register", ".subscribe", ".connect")):
                kind = "REGISTERS"
                attributes["risk_category"] = "framework_coupling"
            elif source_id == module_id:
                kind = "IMPORT_TIME_CALL"
                attributes["risk_category"] = "import_side_effect"
            parsed.edges.append(
                EdgeSpec(source_id, target_id, kind, resolution, self.version, attributes)
            )

    def _add_file_context_reads(
        self,
        parsed: ParsedFile,
        backend: TreeSitterBackend,
        root: Any,
        source: bytes,
        module_id: str,
        module_name: str,
        relative_path: str,
        definition_keys: set[tuple[int, int, str]],
        stable_by_key: dict[tuple[int, int, str], str],
    ) -> None:
        captures = backend.captures(
            self.language,
            load_query(self.query_dir, "file_context.scm"),
            root,
        )
        for identifier in captures.get("file.identifier", []):
            if node_text(identifier, source) != "__file__":
                continue
            parent = identifier.parent
            if parent is not None and parent.type == "attribute":
                attribute_field = parent.child_by_field_name("attribute")
                if attribute_field is not None and node_key(attribute_field) == node_key(identifier):
                    continue
            if parent is not None and parent.type == "assignment":
                left = parent.child_by_field_name("left")
                if left is not None and node_key(left) == node_key(identifier):
                    continue
            ancestor_key = nearest_ancestor(identifier, definition_keys)
            source_id = stable_by_key.get(ancestor_key, module_id)
            resource_id = f"resource:{module_name}:__file__:resource"
            parsed.nodes.append(
                NodeSpec(
                    resource_id,
                    "resource",
                    "__file__",
                    relative_path,
                    self.language,
                    attributes={"source_relative": True},
                )
            )
            parsed.edges.append(
                EdgeSpec(
                    source_id,
                    resource_id,
                    "LOADS_RESOURCE",
                    "exact",
                    self.version,
                    {
                        "risk_category": "resource_coupling",
                        "target_expression": "__file__",
                        "path": relative_path,
                        "line": identifier.start_point[0] + 1,
                    },
                )
            )

    def _add_environment_reads(
        self,
        parsed: ParsedFile,
        backend: TreeSitterBackend,
        root: Any,
        source: bytes,
        module_id: str,
        module_name: str,
        relative_path: str,
        definition_keys: set[tuple[int, int, str]],
        stable_by_key: dict[tuple[int, int, str], str],
    ) -> None:
        captures = backend.captures(
            self.language,
            load_query(self.query_dir, "environment.scm"),
            root,
        )
        for attribute in captures.get("environment.attribute", []):
            if "".join(node_text(attribute, source).split()) != "os.environ":
                continue
            # os.environ.get(...) is already represented by the call detector.
            if attribute.parent is not None and attribute.parent.type in {"attribute", "call"}:
                continue
            context = attribute.parent if attribute.parent is not None else attribute
            literal = first_string_literal(node_text(context, source))
            target_id = None
            resolution = "unresolved"
            if literal:
                target_id = f"env:{literal}:environment_variable"
                parsed.nodes.append(
                    NodeSpec(target_id, "environment_variable", literal, literal, attributes={})
                )
                resolution = "exact"
            ancestor_key = nearest_ancestor(attribute, definition_keys)
            source_id = stable_by_key.get(ancestor_key, module_id)
            scope = next(
                (node.qualified_name for node in parsed.nodes if node.stable_id == source_id),
                module_name,
            )
            parsed.edges.append(
                EdgeSpec(
                    source_id,
                    target_id,
                    "READS_ENV",
                    resolution,
                    self.version,
                    {
                        "target_expression": "os.environ",
                        "risk_category": "config_environment_coupling",
                        "module": module_name,
                        "scope_qualified": scope,
                        "path": relative_path,
                        "line": attribute.start_point[0] + 1,
                    },
                )
            )

    def _add_decorators(
        self,
        parsed: ParsedFile,
        backend: TreeSitterBackend,
        root: Any,
        source: bytes,
        definition_keys: set[tuple[int, int, str]],
        stable_by_key: dict[tuple[int, int, str], str],
    ) -> None:
        captures = backend.captures(
            self.language,
            load_query(self.query_dir, "decorators.scm"),
            root,
        )
        for decorator in captures.get("decorator.expression", []):
            parent = decorator.parent
            definition = None
            if parent is not None:
                definition = next(
                    (child for child in parent.named_children if node_key(child) in definition_keys),
                    None,
                )
            if definition is None:
                continue
            source_id = stable_by_key.get(node_key(definition))
            if source_id is None:
                continue
            expression = node_text(decorator, source).lstrip("@").strip()
            attributes = {"target_expression": expression[:300]}
            if any(token in expression.lower() for token in ("register", "route", "plugin", "hook")):
                attributes["risk_category"] = "framework_coupling"
            elif any(token in expression.lower() for token in ("cache", "memo", "singleton")):
                attributes["risk_category"] = "parser_state_coupling"
            parsed.edges.append(
                EdgeSpec(source_id, None, "DECORATED_BY", "unresolved", self.version, attributes)
            )
