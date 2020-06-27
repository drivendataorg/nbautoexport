import logging
import os
from pathlib import Path
from typing import List

import typer

from nbautoexport.jupyter_config import install_post_save_hook
from nbautoexport.export import export_notebook
from nbautoexport.sentinel import (
    DEFAULT_EXPORT_FORMATS,
    DEFAULT_ORGANIZE_BY,
    ExportFormat,
    install_sentinel,
    NbAutoexportConfig,
    OrganizeBy,
    SAVE_PROGRESS_INDICATOR_FILE,
)
from nbautoexport.utils import __version__

app = typer.Typer()


def validate_sentinel_path(path: Path):
    if not path.exists():
        typer.echo(f"Error: Missing expected nbautoexport config file [{path.resolve()}].")
        raise typer.Exit(code=1)


def version_callback(value: bool):
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show nbautoexport version.",
    ),
):
    """Exports Jupyter notebooks to various file formats (.py, .html, and more) upon save,
    automatically.

    Use the install command to configure a notebooks directory to be watched.
    """
    pass


@app.command()
def clean(
    directory: Path = typer.Argument(
        ..., exists=True, file_okay=False, dir_okay=True, writable=True
    ),
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Assume 'yes' answer to confirmation prompt to delete files."
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show files that would be removed, without actually removing."
    ),
):
    """Remove subfolders/files not matching .nbautoconvert configuration and existing notebooks.
    """
    sentinel_path = directory / SAVE_PROGRESS_INDICATOR_FILE
    validate_sentinel_path(sentinel_path)

    config = NbAutoexportConfig.parse_file(path=sentinel_path, content_type="application/json")

    files_to_clean = config.files_to_clean(directory)

    typer.echo("Identified following files to clean up:")
    for path in sorted(files_to_clean):
        typer.echo(f"  {path}")

    if dry_run:
        typer.echo("Dry run completed. Exiting.")
        raise typer.Exit(code=0)

    if not yes:
        typer.confirm("Are you sure you want to delete these files?", abort=True)

    typer.echo("Removing identified files...")
    for path in files_to_clean:
        os.remove(path)

    # Remove empty subdirectories
    typer.echo("Removing empty subdirectories...")
    subfolders = (d for d in directory.iterdir() if d.is_dir())
    for subfolder in subfolders:
        if not any(subfolder.iterdir()):
            typer.echo(f"  {subfolder}")
            subfolder.rmdir()

    typer.echo("Cleaning complete.")


@app.command()
def convert(
    input: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=True, writable=True),
    export_formats: List[ExportFormat] = typer.Option(
        DEFAULT_EXPORT_FORMATS,
        "--export-format",
        "-f",
        show_default=True,
        help=(
            """File format(s) to save for each notebook. Options are 'script', 'html', 'markdown', """
            """and 'rst'. Multiple formats should be provided using multiple flags, e.g., '-f """
            """script-f html -f markdown'."""
        ),
    ),
    organize_by: OrganizeBy = typer.Option(
        DEFAULT_ORGANIZE_BY,
        "--organize-by",
        "-b",
        show_default=True,
        help=(
            """Whether to save exported file(s) in a folder per notebook or a folder per extension. """
            """Options are 'notebook' or 'extension'."""
        ),
    ),
):
    """Convert notebook(s) using specified configuration options.

    INPUT is the path to a notebook to be converted, or a directory containing notebooks to be
    converted.
    """
    config = NbAutoexportConfig(export_formats=export_formats, organize_by=organize_by)
    if input.is_dir():
        for notebook_path in input.glob("*.ipynb"):
            export_notebook(notebook_path, config=config)
    else:
        export_notebook(input, config=config)


@app.command()
def export(
    input: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=True, writable=True)
):
    """Convert notebook(s) using existing configuration file.

    INPUT is the path to a notebook to be converted, or a directory containing notebooks to be
    converted.

    A .nbautoconvert configuration file is required to be in the same directory as the notebook(s).
    """
    if input.is_dir():
        sentinel_path = input / SAVE_PROGRESS_INDICATOR_FILE
        notebook_paths = input.glob("*.ipynb")
    else:
        sentinel_path = input.parent / SAVE_PROGRESS_INDICATOR_FILE
        notebook_paths = [input]

    validate_sentinel_path(sentinel_path)
    for notebook_path in notebook_paths:
        config = NbAutoexportConfig.parse_file(path=sentinel_path, content_type="application/json")
        export_notebook(notebook_path, config=config)


@app.command()
def install(
    directory: Path = typer.Argument(
        "extension", exists=True, file_okay=False, dir_okay=True, writable=True
    ),
    export_formats: List[ExportFormat] = typer.Option(
        DEFAULT_EXPORT_FORMATS,
        "--export-format",
        "-f",
        show_default=True,
        help=(
            """File format(s) to save for each notebook. Options are 'script', 'html', 'markdown', """
            """and 'rst'. Multiple formats should be provided using multiple flags, e.g., '-f """
            """script-f html -f markdown'."""
        ),
    ),
    organize_by: OrganizeBy = typer.Option(
        DEFAULT_ORGANIZE_BY,
        "--organize-by",
        "-b",
        show_default=True,
        help=(
            """Whether to save exported file(s) in a folder per notebook or a folder per extension. """
            """Options are 'notebook' or 'extension'."""
        ),
    ),
    clean: bool = typer.Option(
        False,
        show_default=True,
        help="Whether to automatically delete files in subfolders that don't match configuration.",
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        "-o",
        is_flag=True,
        show_default=True,
        help="Overwrite existing configuration, if one is detected.",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", is_flag=True, show_default=True, help="Verbose mode"
    ),
):
    """
    Create a .nbautoexport configuration file in DIRECTORY. Defaults to "./notebooks/"
    """
    if verbose:
        logging.basicConfig(level=logging.DEBUG)

    try:
        install_sentinel(export_formats, organize_by, directory, overwrite)
    except FileExistsError as msg:
        typer.echo(msg)
        raise typer.Exit(code=1)

    install_post_save_hook()
