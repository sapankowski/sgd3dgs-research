"""Small commands for research records; GPU methods remain external."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError
from rich.console import Console

from sgd3dgs_research.labels import LabelConversionError, convert_mask
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


@app.command("convert-mask")
def convert_mask_command(
    mask: Annotated[Path, typer.Option(exists=True, dir_okay=False, help="Boolean mask.npy")],
    source: Annotated[Path, typer.Option(exists=True, dir_okay=False, help="Source PLY")],
    manifest: Annotated[
        Path, typer.Option(exists=True, dir_okay=False, help="Scene manifest to extend")
    ],
    output: Annotated[Path, typer.Option(help="New package directory; must not exist")],
    object_id: Annotated[int, typer.Option(help="Value written for selected Gaussians")],
    object_name: Annotated[str, typer.Option(help="Object name recorded in scene.json")],
    method: Annotated[str, typer.Option(help="Producing method")],
    method_version: Annotated[str, typer.Option(help="Method commit, run ID or version")],
    run_report: Annotated[
        Path | None, typer.Option(exists=True, dir_okay=False, help="Optional run report.json")
    ] = None,
) -> None:
    """Convert a Boolean per-Gaussian mask into a canonical uint16 label package."""
    try:
        provenance = convert_mask(
            mask_path=mask,
            source_path=source,
            manifest_path=manifest,
            output_dir=output,
            object_id=object_id,
            object_name=object_name,
            method=method,
            method_version=method_version,
            run_report_path=run_report,
        )
    except LabelConversionError as conversion_error:
        console.print("[red]Conversion rejected; nothing was written.[/red]")
        console.print(conversion_error)
        raise typer.Exit(code=1) from conversion_error

    result = provenance["output"]
    console.print(
        f"[green]Converted[/green] object_id={result['object_id']} "
        f"selected={result['selected_count']} labels_sha256={result['labels_sha256']}"
    )
