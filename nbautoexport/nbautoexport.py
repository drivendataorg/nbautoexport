import logging
from pathlib import Path
from typing import List, Optional

import typer

from nbautoexport.clean import find_files_to_clean
from nbautoexport.export import export_notebook
from nbautoexport.jupyter_config import install_post_save_hook
from nbautoexport.sentinel import (
    DEFAULT_CLEAN,
    DEFAULT_EXPORT_FORMATS,
    DEFAULT_ORGANIZE_BY,
    ExportFormat,
    install_sentinel,
    NbAutoexportConfig,
    OrganizeBy,
    SAVE_PROGRESS_INDICATOR_FILE,
)
from nbautoexport.utils import __version__, find_notebooks

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
        ..., exists=True, file_okay=False, dir_okay=True, writable=True, help="Directory to clean."
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

    files_to_clean = find_files_to_clean(directory, config)

    if len(files_to_clean) == 0:
        typer.echo("No files identified for cleaning. Exiting.")
        raise typer.Exit(code=0)

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
        if path.is_file():
            path.unlink()

    # Remove empty subdirectories
    typer.echo("Removing empty subdirectories...")
    subfolders = (d for d in directory.iterdir() if d.is_dir())
    for subfolder in subfolders:
        for subsubfolder in subfolder.iterdir():
            if subsubfolder.is_dir() and not any(subsubfolder.iterdir()):
                typer.echo(f"  {subsubfolder}")
                subsubfolder.rmdir()
        if not any(subfolder.iterdir()):
            typer.echo(f"  {subfolder}")
            subfolder.rmdir()

    typer.echo("Cleaning complete.")


@app.command()
def export(
    input: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=True,
        writable=True,
        help="Path to notebook file or directory of notebook files to export.",
    ),
    export_formats: Optional[List[ExportFormat]] = typer.Option(
        None,
        "--export-format",
        "-f",
        show_default=True,
        help=(
            "File format(s) to save for each notebook. Multiple formats should be provided using "
            "multiple flags, e.g., '-f script -f html -f markdown'. Provided values will override "
            "existing .nbautoexport config files. If neither provided, defaults to "
            f"{DEFAULT_EXPORT_FORMATS}."
        ),
    ),
    organize_by: Optional[OrganizeBy] = typer.Option(
        None,
        "--organize-by",
        "-b",
        show_default=True,
        help=(
            "Whether to save exported file(s) in a subfolder per notebook or per export format. "
            "Provided values will override existing .nbautoexport config files. If neither "
            f"provided, defaults to '{DEFAULT_ORGANIZE_BY}'."
        ),
    ),
):
    """Manually export notebook or directory of notebooks.

    An .nbautoexport configuration file in same directory as notebook(s) will be used if it
    exists. Configuration options specified by command-line options will override configuration
    file. If no existing configuration option exists and no values are provided, default values
    will be used.

    The export command will not do cleaning, regardless of the 'clean' setting in an .nbautoexport
    configuration file.
    """
    if input.is_dir():
        sentinel_path = input / SAVE_PROGRESS_INDICATOR_FILE
        notebook_paths = [nb.path for nb in find_notebooks(input)]

        if len(notebook_paths) == 0:
            typer.echo(f"No notebooks found in directory [{input}]. Exiting.")
            raise typer.Exit(code=1)

    else:
        sentinel_path = input.parent / SAVE_PROGRESS_INDICATOR_FILE
        notebook_paths = [input]

    # Configuration: input options override existing sentinel file
    if sentinel_path.exists():
        typer.echo(f"Reading existing configuration file from {sentinel_path} ...")
        config = NbAutoexportConfig.parse_file(path=sentinel_path, content_type="application/json")

        # Overrides
        if len(export_formats) > 0:
            typer.echo(f"Overriding config with specified export formats: {export_formats}")
            config.export_formats = export_formats
        if organize_by is not None:
            typer.echo(f"Overriding config with specified organization strategy: {export_formats}")
            config.organize_by = organize_by
    else:
        typer.echo("No configuration found. Using command options as configuration ...")
        if len(export_formats) == 0:
            typer.echo(f"No export formats specified. Using default: {DEFAULT_EXPORT_FORMATS}")
            export_formats = DEFAULT_EXPORT_FORMATS
        if organize_by is None:
            typer.echo(f"No organize-by specified. Using default: {DEFAULT_ORGANIZE_BY}")
            organize_by = DEFAULT_ORGANIZE_BY
        config = NbAutoexportConfig(export_formats=export_formats, organize_by=organize_by)

    for notebook_path in notebook_paths:
        export_notebook(notebook_path, config=config)


@app.command()
def install(
    directory: Path = typer.Argument(
        "notebooks",
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        help="Path to directory of notebook files to watch with nbautoexport.",
    ),
    export_formats: List[ExportFormat] = typer.Option(
        DEFAULT_EXPORT_FORMATS,
        "--export-format",
        "-f",
        show_default=True,
        help=(
            "File format(s) to save for each notebook. Multiple formats should be provided using "
            "multiple flags, e.g., '-f script -f html -f markdown'."
        ),
    ),
    organize_by: OrganizeBy = typer.Option(
        DEFAULT_ORGANIZE_BY,
        "--organize-by",
        "-b",
        show_default=True,
        help=(
            "Whether to save exported file(s) in a subfolder per notebook or per export format. "
        ),
    ),
    clean: bool = typer.Option(
        DEFAULT_CLEAN,
        show_default=True,
        help="Whether to automatically delete files that don't match expected exports given "
        + "notebooks and configuration.",
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
