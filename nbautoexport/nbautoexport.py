import click
import click_log
import json
import logging
import os
from pathlib import Path
import re
import subprocess
from typing import Sequence

from nbconvert.nbconvertapp import NbConvertApp
from nbconvert.postprocessors.base import PostProcessorBase


logger = logging.getLogger(__name__)
click_log.basic_config(logger)


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


def get_jupyter_config_directory():
    output = subprocess.check_output(["jupyter", "--config-dir"])
    config_directory = output.strip(b"\n").decode("utf-8")
    return config_directory


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

    config_dir = get_jupyter_config_directory()
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


def install_sentinel(export_formats, organize_by, directory, overwrite):
    if not Path(directory).exists():
        raise FileNotFoundError

    sentinel_path = Path(directory) / SAVE_PROGRESS_INDICATOR_FILE

    if sentinel_path.exists() and (not overwrite):
        logger.warning(
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


@click.command("autoexport")
@click.option(
    "--export_format",
    "-f",
    "export_formats",
    multiple=True,
    default=["script"],
    help=(
        """File format(s) to save for each notebook. Options are 'script', 'html', 'markdown', """
        """and 'rst'. Multiple formats should be provided using multiple flags, e.g., '-f """
        """script-f html -f markdown'. Default is 'script'."""
    ),
)
@click.option(
    "--organize_by",
    "-b",
    default="notebook",
    help=(
        """Whether to save exported file(s) in a folder per notebook or a folder per extension. """
        """Options are 'notebook' or 'extension'. Default is 'notebook'."""
    ),
)
@click.option(
    "--directory",
    "-d",
    default="notebooks",
    help="Directory containing Jupyter notebooks to track. Default is notebooks.",
)
@click.option(
    "--overwrite", "-o", is_flag=True, help="Overwrite existing configuration, if one is detected."
)
@click.option(
    "--verbose", "-v", is_flag=True, help="Verbose mode.",
)
def install(
    export_formats: Sequence[str],
    organize_by: str,
    directory: str,
    overwrite: bool = False,
    verbose: bool = False,
):
    """Exports Jupyter notebooks to various file formats (.py, .html, and more) upon save."""

    if verbose:
        logging.basicConfig(level=logging.DEBUG)

    install_post_save_hook()
    try:
        install_sentinel(export_formats, organize_by, directory, overwrite)
    except FileNotFoundError:
        with click.get_current_context() as ctx:
            msg = (
                f"""{Path(directory).resolve()} does not exist. Either create this folder """
                """or specify a different directory.\n\n"""
            )
            raise click.ClickException(msg + ctx.get_help())


if __name__ == "__main__":
    install()
