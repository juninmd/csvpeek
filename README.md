# 📊 csvpeek

Peek into CSV files from the terminal — **type inference**, **per-column stats**, **head**, **column select**, and **CSV→JSON**. No pandas, no fuss.

```bash
csvpeek info data.csv        # rows×cols + type/nulls/unique/range per column
csvpeek head data.csv -n 5   # first 5 rows, aligned
csvpeek select data.csv name,email   # project columns → CSV
csvpeek json data.csv | jq '.[0]'    # rows as JSON objects
```

## `info` output
```
data.csv  —  1200 rows × 4 cols
column          type    nulls   unique  range
id              int     0       1200    1 … 1200
age             int     3       61      18 … 79
name            str     0       1187
active          bool    0       2
```

## Dev
```bash
uv sync --group dev
uv run ruff check .
uv run pytest -q
```
Type inference and stats live in `csvpeek/core.py` (pure, unit-tested).

MIT.
