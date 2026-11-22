"""Verify the public CLI behavior without a database."""

import os
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path

import pytest

from dbkeel.cli import main


@pytest.mark.parametrize("entry", ["script", "module"])
@pytest.mark.parametrize(
    ("args", "exit_code", "message", "stream"),
    [
        (["--help"], 0, "--version", "stdout"),
        (["--version"], 0, f"dbkeel {version('dbkeel')}\n", "stdout"),
        ([], 2, "Usage:", "stdout"),
        (["--unknown-option"], 2, "No such option", "stderr"),
        (["unknown-command"], 2, "No such command", "stderr"),
    ],
)
def test_cli(
    entry: str, args: list[str], exit_code: int, message: str, stream: str
) -> None:
    command = (
        [str(Path(sys.executable).with_name("dbkeel"))]
        if entry == "script"
        else [sys.executable, "-m", "dbkeel"]
    )
    result = subprocess.run(
        [*command, *args],
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "NO_COLOR": "1", "TERM": "dumb"},
        timeout=10,
    )

    assert result.returncode == exit_code, result.stdout + result.stderr
    assert message in getattr(result, stream)
    if args == ["--version"]:
        assert result.stdout == message
        assert result.stderr == ""


def test_missing_cli_dependency(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setitem(sys.modules, "typer", None)

    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 1
    output = capsys.readouterr()
    assert output.out == ""
    assert 'pip install "dbkeel[cli]"' in output.err
    assert "Traceback" not in output.err


def test_library_import_without_optional_dependencies() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                "sys.modules.update(typer=None, psycopg=None, psycopg_pool=None); "
                "import dbkeel; import dbkeel.cli; import dbkeel.postgres"
            ),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0, result.stderr
