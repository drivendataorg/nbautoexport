import os
from pathlib import Path
import re
import shutil

from nbconvert.nbconvertapp import NbConvertApp
from nbconvert.postprocessors.base import PostProcessorBase
from notebook.services.contents.filemanager import FileContentsManager

from nbautoexport.sentinel import (
    find_unwanted_outputs,
    NbAutoexportConfig,
    SAVE_PROGRESS_INDICATOR_FILE,
)


class CopyToSubfolderPostProcessor(PostProcessorBase):
    def __init__(self, subfolder=None):
        self.subfolder = subfolder
        super(CopyToSubfolderPostProcessor, self).__init__()

    def postprocess(self, input: str):
        """ Save converted file to a separate directory. """
        if self.subfolder is None:
            return

        input = Path(input)

        new_dir = input.parent / self.subfolder
        new_dir.mkdir(new_dir, exist_ok=True)
        new_path = new_dir / input.name

        with input.open("r") as f:
            text = f.read()

        with new_path.open("w") as f:
            f.write(re.sub(r"\n#\sIn\[(([0-9]+)|(\s))\]:\n{2}", "", text))

        os.remove(input)


def post_save(model: dict, os_path: str, contents_manager: FileContentsManager):
    """Post-save hook for converting notebooks to other formats using Jupyter nbconvert and saving
    in a subfolder.

    The following arguments are standard for Jupyter post-save hooks. See [Jupyter Documentation](
    https://jupyter-notebook.readthedocs.io/en/stable/extending/savehooks.html).

    Args:
        model (dict): the model representing the file. See [Jupyter documentation](
        https://jupyter-notebook.readthedocs.io/en/stable/extending/contents.html#data-model).
        os_path (str): the filesystem path to the file just written
        contents_manager (FileContentsManager): FileContentsManager instance that hook is bound to
    """
    # only do this for notebooks
    if model["type"] != "notebook":
        return

    # only do this if we've added the special indicator file to the working directory
    os_path = Path(os_path)
    cwd = os_path.parent
    save_progress_indicator = cwd / SAVE_PROGRESS_INDICATOR_FILE
    should_convert = save_progress_indicator.exists()

    if should_convert:
        config = NbAutoexportConfig.parse_file(
            path=save_progress_indicator, content_type="application/json"
        )
        export_notebook(os_path, config=config)

        if config.clean:
            to_remove = find_unwanted_outputs(cwd, config)
            for path in to_remove:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    os.remove(path)


def export_notebook(notebook_path: Path, config: NbAutoexportConfig):
    converter = NbConvertApp()

    for export_format in config.export_formats:
        if config.subfolder_type == "notebook":
            subfolder = notebook_path.stem

        elif config.subfolder_type == "extension":
            subfolder = export_format

        converter.postprocessor = CopyToSubfolderPostProcessor(subfolder=subfolder)
        converter.export_format = export_format
        converter.initialize()
        converter.notebooks = [notebook_path]
        converter.convert_notebooks()
