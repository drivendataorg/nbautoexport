import logging
import os
from pathlib import Path
import shutil
from typing import List

import typer

from nbautoexport.jupyter_config import install_post_save_hook
from nbautoexport.convert import export_notebook
from nbautoexport.sentinel import (
    ExportFormat,
    find_unwanted_outputs,
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
    )
):
    """Remove subfolders/files not matching .nbautoconvert configuration.
    """
    sentinel_path = directory / SAVE_PROGRESS_INDICATOR_FILE
    config = NbAutoexportConfig.parse_file(path=sentinel_path, content_type="application/json")

    to_remove = find_unwanted_outputs(directory, config)

    typer.echo("Removing following files:")
    for path in to_remove:
        typer.echo("  " + path)
        if path.is_dir():
            for subpath in path.iterdir():
                typer.echo("  " + subpath)

    delete = typer.confirm("Are you sure you want to delete these files?")
    if not delete:
        typer.echo("Not deleting")
        raise typer.Abort()

    for path in to_remove:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            os.remove(path)
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


if __name__ == "__main__":
    app()
