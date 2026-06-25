from featurelifted import Query
from featurelifted import compile_query


def test_simple_select_where() -> None:
    query = (
        Query()
        .select("id", "name")
        .from_table("products")
        .where("active", "eq", True)
    )

    sql = compile_query(query)

    assert sql == "SELECT id, name FROM products WHERE active = TRUE"


def test_build_ast_records_columns_and_predicates() -> None:
    query = (
        Query()
        .select("total")
        .from_table("orders")
        .where("status", "eq", "paid")
    )

    ast = query.build_ast()

    assert ast.to_dict()["from"] == "orders"
    assert ast.to_dict()["columns"][0]["name"] == "total"
    assert ast.to_dict()["where"][0]["column"] == "status"
