import logging
import os
from pathlib import Path
from typing import List

import typer

from nbautoexport.jupyter_config import install_post_save_hook
from nbautoexport.convert import export_notebook
from nbautoexport.sentinel import (
    ExportFormat,
    install_sentinel,
    NbAutoexportConfig,
    OrganizeBy,
    SAVE_PROGRESS_INDICATOR_FILE,
)
from nbautoexport.utils import __version__

app = typer.Typer()


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
    config = NbAutoexportConfig.parse_file(path=sentinel_path, content_type="application/json")

    # Remove files that are not notebooks or expected files
    notebook_paths = sorted(directory.glob("*.ipynb"))
    expected_exports = [directory / export for export in config.expected_exports(notebook_paths)]
    subfiles = (f for f in directory.glob("**/*") if f.is_file())
    checkpoints = (f for f in directory.glob(".ipynb_checkpoints/*") if f.is_file())
    to_remove = (
        set(subfiles)
        .difference(notebook_paths)
        .difference(expected_exports)
        .difference(checkpoints)
        .difference([sentinel_path])
    )

    typer.echo("Removing following files:")
    for path in sorted(to_remove):
        typer.echo(f"  {path}")

    if dry_run:
        typer.echo("Dry run completed. Exiting...")
        typer.Exit()

    if not yes:
        typer.confirm("Are you sure you want to delete these files?", abort=True)

    for path in to_remove:
        os.remove(path)

    # Remove empty subdirectories
    subfolders = (d for d in directory.iterdir() if d.is_dir())
    for subfolder in subfolders:
        if not any(subfolder.iterdir()):
            subfolder.rmdir()
    typer.echo("Files deleted.")


@app.command()
def convert(
    input: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=True, writable=True),
    export_formats: List[ExportFormat] = typer.Option(
        ["script"],
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
        "extension",
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
        export_notebook(notebook_path, config=config)


@app.command()
def export(
    input: Path = typer.Argument(
        "extension", exists=True, file_okay=True, dir_okay=True, writable=True
    )
):
    """Convert notebook(s) using existing configuration file.

    INPUT is the path to a notebook to be converted, or a directory containing notebooks to be
    converted.

    A .nbautoconvert configuration file is required to be in the same directory as the notebook(s).
    """
    if input.is_dir():
        sentinel_path = input / SAVE_PROGRESS_INDICATOR_FILE
        config = NbAutoexportConfig.parse_file(path=sentinel_path, content_type="application/json")
        for notebook_path in input.glob("*.ipynb"):
            export_notebook(notebook_path, config=config)
    else:
        sentinel_path = input.parent / SAVE_PROGRESS_INDICATOR_FILE
        config = NbAutoexportConfig.parse_file(path=sentinel_path, content_type="application/json")
        export_notebook(notebook_path, config=config)


@app.command()
def install(
    directory: Path = typer.Argument(
        "extension", exists=True, file_okay=False, dir_okay=True, writable=True
    ),
    export_formats: List[ExportFormat] = typer.Option(
        ["script"],
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
        "notebook",
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
