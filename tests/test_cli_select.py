import csv

from typer.testing import CliRunner

from csvpeek.cli import app

runner = CliRunner()


def _write(tmp_path):
    f = tmp_path / "in.csv"
    with f.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "note", "flag"])
        w.writerow(["1", "hello, world", "ok"])
        w.writerow(["2", 'say "hi"', "ok"])
        w.writerow(["3", "=1+1", "ok"])
        w.writerow(["4", "line1\nline2", "ok"])
    return f


def _parse(output: str):
    return list(csv.reader(output.splitlines(keepends=True)))


def test_select_round_trips_special_characters(tmp_path):
    result = runner.invoke(app, ["select", str(_write(tmp_path)), "id,note"])
    assert result.exit_code == 0
    assert _parse(result.stdout) == [
        ["id", "note"],
        ["1", "hello, world"],
        ["2", 'say "hi"'],
        ["3", "=1+1"],
        ["4", "line1\nline2"],
    ]


def test_select_safe_prefixes_formulas_only_when_asked(tmp_path):
    f = str(_write(tmp_path))
    plain = runner.invoke(app, ["select", f, "note"])
    safe = runner.invoke(app, ["select", f, "note", "--safe"])
    assert ["=1+1"] in _parse(plain.stdout)
    assert ["'=1+1"] in _parse(safe.stdout)
