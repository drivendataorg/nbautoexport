from pathlib import Path
import re

from nbconvert.nbconvertapp import NbConvertApp
from nbconvert.postprocessors.base import PostProcessorBase
from notebook.services.contents.filemanager import FileContentsManager

from nbautoexport.clean import FORMATS_WITH_IMAGE_DIR
from nbautoexport.sentinel import (
    ExportFormat,
    NbAutoexportConfig,
    SAVE_PROGRESS_INDICATOR_FILE,
)
from nbautoexport.utils import cleared_argv


class CopyToSubfolderPostProcessor(PostProcessorBase):
    def __init__(self, subfolder: str, export_format: ExportFormat):
        self.subfolder = subfolder
        self.export_format = export_format
        super(CopyToSubfolderPostProcessor, self).__init__()

    def postprocess(self, input: str):
        """ Save converted file to a separate directory, removing cell numbers."""
        if self.subfolder is None:
            return

        input: Path = Path(input)

        new_dir = input.parent / self.subfolder
        new_dir.mkdir(exist_ok=True)
        new_path = new_dir / input.name

        if self.export_format == ExportFormat.pdf:
            # Can't read pdf file as unicode, skip rest of postprocessing and just copy
            input.replace(new_path)
            return

        # Rewrite converted file to new path, removing cell numbers
        with input.open("r", encoding="utf-8") as f:
            text = f.read()
        with new_path.open("w", encoding="utf-8") as f:
            f.write(re.sub(r"\n#\sIn\[(([0-9]+)|(\s))\]:\n{2}", "", text))

        # For some formats, we also need to move the assets directory, for stuff like images
        if self.export_format in FORMATS_WITH_IMAGE_DIR:
            assets_dir = input.parent / f"{input.stem}_files"
            if assets_dir.exists() and assets_dir.is_dir():
                new_assets_dir = new_dir / f"{input.stem}_files"
                new_assets_dir.mkdir(exist_ok=True)
                for asset in assets_dir.iterdir():
                    asset.replace(new_assets_dir / asset.name)
                assets_dir.rmdir()

        input.unlink()


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
            path=save_progress_indicator, content_type="application/json", encoding="utf-8"
        )
        export_notebook(os_path, config=config)


def export_notebook(notebook_path: Path, config: NbAutoexportConfig):
    """Export a given notebook file given configuration.

    Args:
        notebook_path (Path): path to notebook to export with nbconvert
        config (NbAutoexportConfig): configuration
    """
    with cleared_argv():
        converter = NbConvertApp()

        for export_format in config.export_formats:
            if config.organize_by == "notebook":
                subfolder = notebook_path.stem
            elif config.organize_by == "extension":
                subfolder = export_format.value

            converter.postprocessor = CopyToSubfolderPostProcessor(
                subfolder=subfolder, export_format=export_format
            )
            converter.export_format = export_format.value
            converter.initialize()
            converter.notebooks = [str(notebook_path)]
            converter.convert_notebooks()
