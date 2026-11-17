"""Small commands for research records; GPU methods remain external."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError
from rich.console import Console

from sgd3dgs_research.records import load_experiment

app = typer.Typer(no_args_is_help=True, help="SGD3DGS research-record utilities.")
console = Console()


@app.callback()
def main() -> None:
    """Validate and inspect method-neutral research records."""


@app.command()
def validate_experiment(
    path: Annotated[Path, typer.Argument(exists=True, dir_okay=False, readable=True)],
) -> None:
    """Validate a method-neutral experiment record."""
    try:
        record = load_experiment(path)
    except (ValidationError, ValueError, OSError) as validation_error:
        console.print("[red]Experiment validation failed.[/red]")
        console.print(validation_error)
        raise typer.Exit(code=1) from validation_error

    console.print(
        f"[green]Valid[/green] experiment={record.experiment_id} "
        f"status={record.status} method={record.method.name}"
    )
