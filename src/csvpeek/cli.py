"""csvpeek CLI."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import typer

from .core import column_stats, columns_from_rows

app = typer.Typer(add_completion=False, help="Peek into CSV files.")


_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def _neutralize(value: str) -> str:
    """Prefix spreadsheet-formula starters with ' so Excel/Sheets show them as text."""
    return f"'{value}" if value.startswith(_FORMULA_PREFIXES) else value


def _read(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        header = reader.fieldnames or []
        return list(header), list(reader)


@app.command()
def info(file: Path = typer.Argument(..., exists=True, dir_okay=False)) -> None:
    """Show rows/cols and per-column type, nulls, unique and numeric range."""
    header, rows = _read(file)
    cols = columns_from_rows(rows, header)
    title = f"{file}  —  {len(rows)} rows × {len(header)} cols"
    typer.secho(title, fg=typer.colors.CYAN, bold=True)
    typer.echo(f"{'column':<24}{'type':<8}{'nulls':<8}{'unique':<8}range")
    for name in header:
        s = column_stats(name, cols[name])
        rng = "" if s.min is None else f"{s.min:g} … {s.max:g}"
        typer.echo(f"{name[:23]:<24}{s.type:<8}{s.nulls:<8}{s.unique:<8}{rng}")


@app.command()
def head(
    file: Path = typer.Argument(..., exists=True, dir_okay=False),
    n: int = typer.Option(10, "-n", "--rows", help="rows to show"),
) -> None:
    """Print the first N rows as an aligned table."""
    header, rows = _read(file)
    shown = rows[:n]

    def _w(h: str) -> int:
        return max(len(h), *(len(r.get(h, "")) for r in shown)) if shown else len(h)

    widths = {h: _w(h) for h in header}
    typer.secho("  ".join(h.ljust(widths[h]) for h in header), bold=True)
    for r in shown:
        typer.echo("  ".join(r.get(h, "").ljust(widths[h]) for h in header))


@app.command()
def select(
    file: Path = typer.Argument(..., exists=True, dir_okay=False),
    columns: str = typer.Argument(..., help="comma-separated column names"),
    safe: bool = typer.Option(
        False, "--safe", help="prefix cells starting with = + - @ with ' (spreadsheet safety)"
    ),
) -> None:
    """Project a subset of columns and emit CSV to stdout."""
    header, rows = _read(file)
    want = [c.strip() for c in columns.split(",") if c.strip()]
    missing = [c for c in want if c not in header]
    if missing:
        typer.secho(f"unknown column(s): {', '.join(missing)}", fg=typer.colors.RED, err=True)
        raise typer.Exit(2)
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(want)
    fix = _neutralize if safe else (lambda v: v)
    for r in rows:
        writer.writerow([fix(r.get(c, "")) for c in want])


@app.command(name="json")
def to_json(file: Path = typer.Argument(..., exists=True, dir_okay=False)) -> None:
    """Convert the CSV into a JSON array of objects."""
    _, rows = _read(file)
    typer.echo(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    app()
