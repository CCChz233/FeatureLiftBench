"""Authored scenario inputs. Expected outputs come from the pinned upstream only."""
from copy import deepcopy
from itertools import product


def case(name, args, behaviors, public=False, error=False):
    return dict(name=name, args=args, behavior_ids=behaviors, tier="public" if public else "hidden", error=error)


def pip_cases():
    def f(filename, **kw): return dict(filename=filename, **kw)
    out = [
        case("wheel_and_source", dict(project="demo", files=[f("demo-1.0.tar.gz"), f("demo-1.0-py3-none-any.whl")]), ["B001", "B002", "B006"], True),
        case("requires_python", dict(project="demo", files=[f("demo-2.0.tar.gz", requires_python=">=3.13"), f("demo-1.0.tar.gz")]), ["B003"], True),
        case("empty", dict(project="demo", files=[]), ["B001", "B004"]),
        case("no_applicable_version", dict(project="demo", files=[f("demo-1.0.tar.gz")], specifier=">=2"), ["B004"]),
        case("name_formats_and_tags", dict(project="Demo_Pkg", files=[f("demo_pkg-1.0-py3-none-any.whl"), f("demo-pkg-2.0.tar.gz"), f("other-9.0.tar.gz"), f("demo_pkg-3.0-cp311-cp311-win_amd64.whl"), f("bad.whl"), f("demo_pkg-4.0.exe")]), ["B001", "B002"]),
        case("compressed_tags", dict(project="demo", files=[f("demo-1.0-py2.py3-none-any.whl"), f("demo-2.0-py2-none-any.whl")]), ["B002"]),
        case("build_tag_priority", dict(project="demo", files=[f("demo-1.0-2z-py3-none-any.whl"), f("demo-1.0-10a-py3-none-any.whl"), f("demo-1.0-10b-py3-none-any.whl")]), ["B006"]),
        case("tag_priority", dict(project="demo", files=[f("demo-1.0-py3-none-any.whl"), f("demo-1.0-cp312-cp312-manylinux_2_17_x86_64.whl")], supported_tags=["cp312-cp312-manylinux_2_17_x86_64", "py3-none-any"]), ["B002", "B006"]),
        case("equal_keys_stable", dict(project="demo", files=[f("demo-1.0.zip"), f("demo-1.0.tar.gz")]), ["B001", "B006"]),
        case("invalid_python_requirement", dict(project="demo", files=[f("demo-2.0.tar.gz", requires_python="not a specifier"), f("demo-1.0.tar.gz")]), ["B003"]),
        case("ignore_python_requirement", dict(project="demo", files=[f("demo-2.0.tar.gz", requires_python=">=3.13"), f("demo-1.0.tar.gz")], ignore_requires_python=True), ["B003"]),
        case("explicit_prerelease_spec", dict(project="demo", files=[f("demo-2.0rc1.tar.gz"), f("demo-1.0.tar.gz")], specifier=">=2.0rc1"), ["B004"]),
        case("prerelease_only", dict(project="demo", files=[f("demo-2.0rc1.tar.gz")]), ["B004"]),
        case("source_only", dict(project="demo", files=[f("demo-2.0-py3-none-any.whl"), f("demo-1.0.tar.gz")], formats=["source"]), ["B002"]),
        case("binary_only", dict(project="demo", files=[f("demo-3.0.tar.gz"), f("demo-2.0-py3-none-any.whl")], formats=["binary"]), ["B002"]),
        case("hash_match_beats_newer", dict(project="demo", files=[f("demo-1.0.tar.gz", hashes={"sha256": "abc"}), f("demo-3.0.tar.gz"), f("demo-4.0.tar.gz", hashes={"sha256": "bad"})], allowed_hashes={"sha256": ["abc"]}), ["B005", "B006"], True),
        case("hash_no_match_retains", dict(project="demo", files=[f("demo-2.0.tar.gz", hashes={"sha256": "bad"}), f("demo-1.0.tar.gz")], allowed_hashes={"sha256": ["abc"]}), ["B005"]),
        case("hash_match_outside_specifier", dict(project="demo", files=[f("demo-1.0.tar.gz", hashes={"sha256": "abc"}), f("demo-2.0.tar.gz", hashes={"sha256": "bad"})], allowed_hashes={"sha256": ["abc"]}, specifier=">=2"), ["B004", "B005"]),
        case("hash_other_algorithm", dict(project="demo", files=[f("demo-1.0.tar.gz", hashes={"sha256": "bad", "sha512": "abc"}), f("demo-2.0.tar.gz")], allowed_hashes={"sha512": ["abc"]}), ["B005"]),
    ]
    for binary, pre, yank, hashes in product([False, True], repeat=4):
        out.append(case(f"preferences_{int(binary)}{int(pre)}{int(yank)}{int(hashes)}", dict(project="demo", files=[f("demo-1.0-py3-none-any.whl", yanked_reason="", hashes={"sha256": "abc"}), f("demo-2.0.tar.gz"), f("demo-3.0rc1.tar.gz"), f("demo-1.5-py3-none-any.whl", hashes={"sha256": "bad"})], prefer_binary=binary, allow_prereleases=pre, allow_yanked=yank, allowed_hashes={"sha256": ["abc"]} if hashes else None), ["B001", "B004", "B005", "B006"]))
    return out


def graph_nodes():
    return [
        dict(id="source.shop.raw", fqn=["shop", "raw"], resource_type="source", tags=["input"]),
        dict(id="model.shop.a", fqn=["shop", "staging", "a"], parents=["source.shop.raw"], tags=["nightly"]),
        dict(id="model.shop.b", fqn=["shop", "marts", "b"], parents=["model.shop.a"], tags=["nightly", "finance"]),
        dict(id="model.shop.c", fqn=["shop", "marts", "c"], parents=["source.shop.raw"], tags=["finance"]),
        dict(id="model.shop.d", fqn=["shop", "marts", "d"], parents=["model.shop.b", "model.shop.c"]),
        dict(id="test.shop.bc", fqn=["shop", "tests", "bc"], parents=["model.shop.b", "model.shop.c"], resource_type="test"),
        dict(id="test.shop.ab", fqn=["shop", "tests", "ab"], parents=["model.shop.a", "model.shop.b"], resource_type="test"),
        dict(id="model.other.a", fqn=["other", "a"], tags=["weekly"]),
    ]


def dbt_cases():
    nodes = graph_nodes()
    out = [case("single_model", dict(nodes=nodes, include=["b"], indirect_selection="empty"), ["B001", "B002"], True),
           case("bounded_ancestors", dict(nodes=nodes, include=["1+b"], indirect_selection="empty"), ["B003"], True),
           case("eager_test_selection", dict(nodes=nodes, include=["b"]), ["B004"], True)]
    expressions = ["b", "b c", "b,c", "tag:nightly,tag:finance", "+b", "b+1", "0+b+0", "@b", "shop.marts.*", "package:other", "tag:fin*", "bc", "unmatched", "+b,+c"]
    for mode in ["eager", "cautious", "buildable", "empty"]:
        for expr in expressions:
            out.append(case(f"{mode}_{expr}", dict(nodes=nodes, include=[expr], indirect_selection=mode), ["B001", "B002", "B003", "B004", "B005"]))
    out += [case("exclude_after_expansion", dict(nodes=nodes, include=["@b"], exclude=["tag:finance"], indirect_selection="cautious"), ["B002", "B003", "B005"]),
            case("resource_filter_after_test_expansion", dict(nodes=nodes, include=["b c"], indirect_selection="cautious", resource_types=["test"]), ["B004", "B005", "B006"]),
            case("pending_not_resource_filtered", dict(nodes=nodes, include=["b"], indirect_selection="cautious", resource_types=["source"]), ["B005", "B006"]),
            case("empty_include", dict(nodes=nodes, include=[]), ["B001", "B002"])]
    disabled = deepcopy(nodes)
    disabled[2]["enabled"] = False
    out.append(case("disabled_breaks_path", dict(nodes=disabled, include=["a+"], indirect_selection="empty"), ["B003", "B006"]))
    empty = deepcopy(nodes)
    empty[2]["empty"] = True
    out.append(case("empty_does_not_break_path", dict(nodes=empty, include=["shop.staging.a+"], indirect_selection="empty"), ["B003", "B006"]))
    for name, args in [
        ("bad_modifier", dict(nodes=nodes, include=["@b+"])),
        ("bad_method", dict(nodes=nodes, include=["not_a_method:b"])),
        ("bad_mode", dict(nodes=nodes, include=["b"], indirect_selection="unknown")),
        ("duplicate", dict(nodes=nodes + [nodes[0]], include=["b"])),
        ("missing_parent", dict(nodes=[dict(id="m.a", parents=["m.missing"])], include=["a"])),
        ("cycle", dict(nodes=[dict(id="m.a", parents=["m.b"]), dict(id="m.b", parents=["m.a"])], include=["a"])),
        ("short_fqn", dict(nodes=[dict(id="a")], include=["a"])),
    ]:
        out.append(case(name, args, ["B001", "B003"], error=True))
    return out


def sqlglot_cases():
    pairs = [
        ("direct", "x", "SELECT x FROM tbl", {}, ["B001", "B002"], True),
        ("computed_join", "total", "SELECT a.x + b.y AS total FROM a JOIN b ON a.id = b.id", {}, ["B002"], True),
        ("cte", "out", "WITH q AS (SELECT x AS value FROM raw) SELECT value AS out FROM q", {}, ["B003"], True),
        ("constant", "x", "SELECT 42 AS x", {}, ["B005"], False),
        ("quoted", "\"MiXeD\"", 'SELECT "Input" AS "MiXeD" FROM "Table"', {}, ["B002"], False),
        ("unquoted_case", "OUT", "SELECT INPUT AS OUT FROM DATA", {}, ["B002"], False),
        ("nested_cte", "z", "WITH first AS (SELECT x AS v FROM raw), second AS (SELECT v + 1 AS z FROM first) SELECT z FROM second", {}, ["B003"], False),
        ("derived", "z", "SELECT q.v AS z FROM (SELECT x AS v FROM raw) AS q", {}, ["B003"], False),
        ("union", "x", "SELECT a AS x FROM one UNION SELECT b AS x FROM two", {}, ["B003"], False),
        ("union_all_cte", "x", "WITH q AS (SELECT a AS x FROM one UNION ALL SELECT b AS x FROM two) SELECT x FROM q", {}, ["B003"], False),
        ("star_schema", "x", "SELECT * FROM raw", dict(schema={"raw": {"x": "INT", "y": "TEXT"}}), ["B004"], False),
        ("cte_star", "x", "WITH q AS (SELECT * FROM raw) SELECT q.x FROM q", dict(schema={"raw": {"x": "INT", "y": "INT"}}), ["B003", "B004"], False),
        ("qualified_star", "y", "SELECT q.* FROM (SELECT x, y FROM raw) q", dict(schema={"raw": {"x": "INT", "y": "INT"}}), ["B004"], False),
        ("source_expansion", "out", "SELECT x AS out FROM view_a", dict(sources={"view_a": "SELECT value AS x FROM base"}), ["B004"], False),
        ("source_star", "out", "SELECT x AS out FROM view_a", dict(sources={"view_a": "SELECT * FROM base"}, schema={"base": {"x": "INT"}}), ["B004"], False),
        ("coalesce", "out", "SELECT COALESCE(a.x, b.x) AS out FROM a LEFT JOIN b ON a.id = b.id", {}, ["B002"], False),
        ("nested_shadow", "x", "WITH q AS (SELECT a AS x FROM base) SELECT q.x FROM (WITH q AS (SELECT b AS x FROM other) SELECT x FROM q) q", {}, ["B003"], False),
        ("same_column_two_scopes", "out", "SELECT a.x + b.x AS out FROM (SELECT x FROM one) a JOIN (SELECT x FROM two) b ON TRUE", {}, ["B002", "B003"], False),
        ("external_column", "x", "SELECT other.x AS x FROM known", {}, ["B004"], False),
    ]
    out = [case(name, dict(column=column, sql=sql, **kw), ids, public) for name, column, sql, kw, ids, public in pairs]
    for name, sql, column in [("absent_output", "SELECT x FROM tbl", "missing"), ("invalid_sql", "SELECT FROM", "x"), ("not_query", "DELETE FROM tbl", "x")]:
        out.append(case(name, dict(column=column, sql=sql), ["B005"], error=True))
    return out


CASES = {"pip": pip_cases, "dbt-core": dbt_cases, "sqlglot": sqlglot_cases}
