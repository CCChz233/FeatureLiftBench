from featurelifted import Query
from featurelifted import compile_query
from featurelifted.state import GLOBAL_STATE
from featurelifted.state import reset_state


def test_join_and_multiple_predicates() -> None:
    query = (
        Query()
        .select("orders.id", "customers.name")
        .from_table("orders")
        .join("customers", "orders.customer_id", "customers.id")
        .where("orders.total", "gte", 100)
        .where("customers.region", "eq", "west")
    )

    sql = compile_query(query)

    assert "INNER JOIN customers ON orders.customer_id = customers.id" in sql
    assert "orders.total >= 100" in sql
    assert "customers.region = 'west'" in sql


def test_build_ast_tracks_global_state() -> None:
    reset_state()
    query = Query().select("id").from_table("items").where("qty", "gt", 0)

    query.build_ast()

    assert len(GLOBAL_STATE["compiled_queries"]) == 1
    assert GLOBAL_STATE["compiled_queries"][0]["from"] == "items"


def test_compile_query_updates_last_sql() -> None:
    reset_state()
    query = Query().select("sku").from_table("inventory")

    compile_query(query)

    assert GLOBAL_STATE["last_compiled_sql"] == "SELECT sku FROM inventory"
