from enum import Enum
import json
import logging
import os
from pathlib import Path
import re
from typing import List

from jupyter_core.paths import jupyter_config_dir
import typer

from nbconvert.nbconvertapp import NbConvertApp
from nbconvert.postprocessors.base import PostProcessorBase


logger = logging.getLogger(__name__)
app = typer.Typer()


class ExportFormat(str, Enum):
    html = "html"
    latex = "latex"
    pdf = "pdf"
    slides = "slides"
    markdown = "markdown"
    asciidoc = "asciidoc"
    script = "script"
    notebook = "notebook"


class OrganizeBy(str, Enum):
    notebook = "notebook"
    extension = "extension"


class CopyToSubfolderPostProcessor(PostProcessorBase):
    def __init__(self, subfolder=None):
        self.subfolder = subfolder
        super(CopyToSubfolderPostProcessor, self).__init__()

    def postprocess(self, input):
        """ Save converted file to a separate directory. """
        if self.subfolder is None:
            return

        dirname, filename = os.path.split(input)
        new_dir = os.path.join(dirname, self.subfolder)
        new_path = os.path.join(new_dir, filename)

        if not os.path.exists(new_dir):
            os.mkdir(new_dir)

        with open(input, "r") as f:
            text = f.read()

        with open(new_path, "w") as f:
            f.write(re.sub(r"\n#\sIn\[(([0-9]+)|(\s))\]:\n{2}", "", text))

        os.remove(input)


SAVE_PROGRESS_INDICATOR_FILE = ".nbautoexport"


def post_save(model, os_path, contents_manager):
    """post-save hook for converting notebooks to .py scripts and html
       in a separate folder with the same name
    """
    # only do this for notebooks
    if model["type"] != "notebook":
        return

    # only do this if we've added the special indicator file to the working directory
    cwd = os.path.dirname(os_path)
    save_progress_indicator = os.path.join(cwd, SAVE_PROGRESS_INDICATOR_FILE)
    should_convert = os.path.exists(save_progress_indicator)

    if should_convert:
        with open(save_progress_indicator, "r") as f:
            save_settings = f.read()
            if len(save_settings) > 0:
                save_settings = json.loads(save_settings)
            else:
                save_settings = {}

        subfolder_type = save_settings.get("organize_by", "notebook")
        export_formats = save_settings.get("export_formats", ["script"])
        converter = NbConvertApp()

        for export_format in export_formats:
            if subfolder_type == "notebook":
                d, fname = os.path.split(os_path)
                subfolder = os.path.splitext(fname)[0]

            elif subfolder_type == "extension":
                subfolder = export_format

            converter.postprocessor = CopyToSubfolderPostProcessor(subfolder=subfolder)
            converter.export_format = export_format
            converter.initialize()
            converter.notebooks = [os_path]
            converter.convert_notebooks()


def install_post_save_hook():
    """Splices the post save hook into the global Jupyter configuration file
    """
    command = """# >>> nbautoexport initialize >>>
try:
    from nbautoexport import post_save
    c.FileContentsManager.post_save_hook = post_save
except:
    pass
# <<< nbautoexport initialize <<<"""

    config_dir = jupyter_config_dir()
    config_path = (Path(config_dir) / "jupyter_notebook_config.py").expanduser().resolve()

    if config_path.exists():
        logger.debug(f"Detected existing Jupyter configuration at {config_path}")
    else:
        logger.debug(f"No existing Jupyter configuration detected at {config_path}. Creating.")
        config_path.touch(exist_ok=True)

    with config_path.open("r+") as fp:
        config = fp.read()

        if config.find(command) == -1:
            logger.info("Installing post-save hook.")
            fp.write(command)
        else:
            logger.info("Detected existing autoexport post-save hook. No changes made.")


def install_sentinel(
    export_formats: List[ExportFormat], organize_by: OrganizeBy, directory: Path, overwrite: bool
):
    """Writes the configuration file to a specified directory.

    Args:
        export_formats: A list of `nbconvert`-supported export formats to write on each save
        organize_by: Whether to organize exported files by notebook filename or in folders by extension
        directory: The directory containing the notebooks to monitor
        overwrite: Overwrite an existing sentinel file if one exists
    """
    sentinel_path = directory / SAVE_PROGRESS_INDICATOR_FILE

    if sentinel_path.exists() and (not overwrite):
        raise FileExistsError(
            f"""Detected existing autoexport configuration at {sentinel_path}. """
            """If you wish to overwrite, use the --overwrite flag."""
        )
    else:
        config = {
            "export_formats": export_formats,
            "organize_by": organize_by,
        }

        logger.info(f"Creating configuration file at {sentinel_path}")
        logger.info(f"\n{json.dumps(config, indent=2)}")
        with sentinel_path.open("w") as fp:
            json.dump(config, fp)


@app.command()
def install(
    directory: Path = typer.Argument(
        "notebooks", exists=True, file_okay=False, dir_okay=True, writable=True
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
    """Exports Jupyter notebooks to various file formats (.py, .html, and more) upon save,
    automatically.

    This command creates a .nbautoexport configuration file in DIRECTORY. Defaults to
    "./notebooks/"
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
