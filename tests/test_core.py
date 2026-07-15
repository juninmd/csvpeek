from csvpeek.core import column_stats, columns_from_rows, infer_type


def test_infer_type():
    assert infer_type(["1", "2", "3"]) == "int"
    assert infer_type(["1.5", "2", "3"]) == "float"
    assert infer_type(["true", "false", "yes"]) == "bool"
    assert infer_type(["a", "1", "x"]) == "str"
    assert infer_type(["", "  ", ""]) == "empty"


def test_infer_type_ignores_blanks():
    assert infer_type(["1", "", "2"]) == "int"


def test_column_stats_numeric():
    s = column_stats("age", ["10", "20", "", "20"])
    assert s.type == "int"
    assert s.count == 4
    assert s.nulls == 1
    assert s.unique == 2  # {10, 20}
    assert s.min == 10.0
    assert s.max == 20.0


def test_column_stats_string_has_no_range():
    s = column_stats("name", ["a", "b", "b"])
    assert s.type == "str"
    assert s.unique == 2
    assert s.min is None and s.max is None


def test_columns_from_rows_transposes():
    rows = [{"a": "1", "b": "x"}, {"a": "2", "b": "y"}]
    cols = columns_from_rows(rows, ["a", "b"])
    assert cols == {"a": ["1", "2"], "b": ["x", "y"]}


def test_columns_from_rows_fills_missing():
    rows = [{"a": "1"}, {"a": "2", "b": "y"}]
    cols = columns_from_rows(rows, ["a", "b"])
    assert cols["b"] == ["", "y"]
