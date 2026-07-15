"""Pure column analysis — no I/O."""

from __future__ import annotations

from dataclasses import dataclass

_BOOL_VALUES = {"true", "false", "yes", "no", "0", "1"}


def is_int(s: str) -> bool:
    try:
        int(s)
        return True
    except ValueError:
        return False


def is_float(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def infer_type(values: list[str]) -> str:
    """Infer a column type from its non-empty string values."""
    non_empty = [v for v in values if v.strip() != ""]
    if not non_empty:
        return "empty"
    if all(is_int(v) for v in non_empty):
        return "int"
    if all(is_float(v) for v in non_empty):
        return "float"
    if all(v.strip().lower() in _BOOL_VALUES for v in non_empty):
        return "bool"
    return "str"


@dataclass
class ColumnStats:
    name: str
    type: str
    count: int
    nulls: int
    unique: int
    min: float | None = None
    max: float | None = None


def column_stats(name: str, values: list[str]) -> ColumnStats:
    """Compute type, null count, cardinality, and numeric range for one column."""
    non_empty = [v for v in values if v.strip() != ""]
    col_type = infer_type(values)
    lo = hi = None
    if col_type in ("int", "float"):
        nums = [float(v) for v in non_empty]
        if nums:
            lo, hi = min(nums), max(nums)
    return ColumnStats(
        name=name,
        type=col_type,
        count=len(values),
        nulls=len(values) - len(non_empty),
        unique=len(set(non_empty)),
        min=lo,
        max=hi,
    )


def columns_from_rows(rows: list[dict[str, str]], header: list[str]) -> dict[str, list[str]]:
    """Transpose row-dicts into per-column value lists (missing → '')."""
    return {h: [r.get(h, "") for r in rows] for h in header}
