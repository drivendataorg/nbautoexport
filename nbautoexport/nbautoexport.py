import logging
from pathlib import Path
from typing import List, Optional

from jupyter_core.paths import jupyter_config_dir
from packaging.version import parse as parse_version
import typer

from nbautoexport.clean import find_files_to_clean
from nbautoexport.export import export_notebook
from nbautoexport.jupyter_config import block_regex, install_post_save_hook, version_regex
from nbautoexport.sentinel import (
    CleanConfig,
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
    """Automatically export Jupyter notebooks to various file formats (.py, .html, and more) upon
    save. One great use case is to automatically have script versions of your notebooks to
    facilitate code review commenting.

    To set up, first use the 'install' command to register nbautoexport with Jupyter. If you
    already have a Jupyter server running, you will need to restart it.

    Next, you will need to use the 'configure' command to create a .nbautoexport configuration file
    in the same directory as the notebooks you want to have export automatically.

    Once nbautoexport is installed with the first step, exporting will run automatically when
    saving a notebook in Jupyter for any notebook where there is a .nbautoexport configuration file
    in the same directory.
    """
    pass


@app.command()
def clean(
    directory: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        help=f"Directory to clean. Must have a {SAVE_PROGRESS_INDICATOR_FILE} config file.",
    ),
    exclude: List[str] = typer.Option(
        [],
        "--exclude",
        "-e",
        help=(
            "Glob-style patterns that designate files to exclude from deletion. Combined with any "
            f"patterns specified in {SAVE_PROGRESS_INDICATOR_FILE} config file."
        ),
    ),
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Assume 'yes' answer to confirmation prompt to delete files."
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show files that would be removed, without actually removing."
    ),
):
    """(EXPERIMENTAL) Remove subfolders/files not matching .nbautoexport configuration and
    existing notebooks.

    Known limitations:
    - Not able to correctly handle additional intended files, such as image assets or
      non-notebook-related files.
    """
    sentinel_path = directory / SAVE_PROGRESS_INDICATOR_FILE
    validate_sentinel_path(sentinel_path)

    config = NbAutoexportConfig.parse_file(
        path=sentinel_path, content_type="application/json", encoding="utf-8"
    )

    # Combine exclude patterns from config and command-line
    config.clean.exclude.extend(exclude)
    if len(config.clean.exclude) > 0:
        typer.echo("Excluding files from cleaning using the following patterns:")
        for pattern in config.clean.exclude:
            typer.echo(f"  {pattern}")

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
    export_formats: List[ExportFormat] = typer.Option(
        [],
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
        config = NbAutoexportConfig.parse_file(
            path=sentinel_path, content_type="application/json", encoding="utf-8"
        )

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
    jupyter_config: Optional[Path] = typer.Option(
        None,
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
        help=(
            "Path to config file. If not specified (default), will determine appropriate path "
            "used by Jupyter. You should only specify this option if you use a nonstandard config "
            "file path that you explicitly pass to Jupyter with the --config option at startup."
        ),
    )
):
    """Register nbautoexport post-save hook with Jupyter. Note that if you already have a Jupyter
    server running, you will need to restart in order for it to take effect. This is a one-time
    installation.

    This works by adding an initialization block in your Jupyter config file that will register
    nbautoexport's post-save function. If an nbautoexport initialization block already exists and
    is from an older version of nbautoexport, this command will replace it with an updated version.
    """
    install_post_save_hook(config_path=jupyter_config)

    typer.echo("nbautoexport post-save hook successfully installed with Jupyter.")
    typer.echo(
        "If a Jupyter server is already running, you will need to restart it for nbautoexport "
        "to work."
    )


@app.command()
def configure(
    directory: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        help="Path to directory of notebook files to configure with nbautoexport.",
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
    clean_exclude: List[str] = typer.Option(
        [],
        "--clean-exclude",
        "-e",
        show_default=True,
        help=(
            "Glob-style patterns that designate files to exclude from deletion when running clean "
            "command."
        ),
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
    Create a .nbautoexport configuration file in a directory. If nbautoexport has been installed
    with the 'install' command, then Jupyter will automatically export any notebooks on save that
    are in the same directory as the .nbautoexport file.

    An .nbautoexport configuration file only applies to that directory, nonrecursively. You must
    independently configure other directories containing notebooks.
    """
    if verbose:
        logging.basicConfig(level=logging.DEBUG)

    config = NbAutoexportConfig(
        export_formats=export_formats,
        organize_by=organize_by,
        clean=CleanConfig(exclude=clean_exclude),
    )
    try:
        install_sentinel(directory=directory, config=config, overwrite=overwrite)
    except FileExistsError as msg:
        typer.echo(msg)
        raise typer.Exit(code=1)

    # Check for installation in Jupyter config
    installed = False
    jupyter_config_file = (
        (Path(jupyter_config_dir()) / "jupyter_notebook_config.py").expanduser().resolve()
    )
    if jupyter_config_file.exists():
        with jupyter_config_file.open("r", encoding="utf-8") as fp:
            jupyter_config_text = fp.read()
        if block_regex.search(jupyter_config_text):
            installed = True
            version_match = version_regex.search(jupyter_config_text)
            if version_match:
                existing_version = version_match.group()
            else:
                existing_version = ""

            if parse_version(existing_version) < parse_version(__version__):
                typer.echo(
                    "Warning: nbautoexport initialize is an older version. "
                    "Please run 'install' command to update."
                )
    if not installed:
        typer.echo(
            "Warning: nbautoexport is not properly installed with Jupyter. "
            "Please run 'install' command."
        )
