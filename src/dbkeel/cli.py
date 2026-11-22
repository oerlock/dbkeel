"""Command-line entry point for dbkeel."""

import sys
from importlib.metadata import version
from typing import Annotated


def main() -> None:
    """Start the CLI, loading its optional dependency only when needed."""
    try:
        import typer
    except ModuleNotFoundError as exc:
        if exc.name != "typer":
            raise
        print(
            'The dbkeel CLI requires Typer. Install it with: pip install "dbkeel[cli]"',
            file=sys.stderr,
        )
        raise SystemExit(1) from None

    app = typer.Typer(no_args_is_help=True)

    def show_version(value: bool) -> None:
        if value:
            typer.echo(f"dbkeel {version('dbkeel')}")
            raise typer.Exit()

    @app.callback(invoke_without_command=True)
    def root(
        version: Annotated[
            bool,
            typer.Option(
                "--version",
                callback=show_version,
                is_eager=True,
                help="Show the installed version and exit.",
            ),
        ] = False,
    ) -> None:
        """Database tools for asynchronous Python applications."""

    app()
