from enum import Enum
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel

from nbautoexport.utils import JupyterNotebook, logger
from nbconvert.exporters import get_exporter


SAVE_PROGRESS_INDICATOR_FILE = ".nbautoexport"
DEFAULT_EXPORT_FORMATS = ["script"]
DEFAULT_ORGANIZE_BY = "extension"


class ExportFormat(str, Enum):
    asciidoc = "asciidoc"
    html = "html"
    latex = "latex"
    markdown = "markdown"
    notebook = "notebook"
    pdf = "pdf"
    rst = "rst"
    script = "script"
    slides = "slides"

    @classmethod
    def get_extension(cls, value: str, notebook: Optional[JupyterNotebook] = None) -> str:
        # Script format needs notebook to determine appropriate language's extension
        if cls(value) == cls.script and notebook is not None:
            return notebook.get_script_extension()

        exporter = get_exporter(cls(value).value)

        if cls(value) == cls.notebook:
            return f".nbconvert{exporter().file_extension}"
        return exporter().file_extension

    @classmethod
    def has_value(cls, value: str) -> bool:
        return any(level for level in cls if level.value == value)


class OrganizeBy(str, Enum):
    notebook = "notebook"
    extension = "extension"


class NbAutoexportConfig(BaseModel):
    export_formats: List[ExportFormat] = [ExportFormat(fmt) for fmt in DEFAULT_EXPORT_FORMATS]
    organize_by: OrganizeBy = OrganizeBy(DEFAULT_ORGANIZE_BY)
    clean: bool = False

    class Config:
        extra = "forbid"


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
        config = NbAutoexportConfig(export_formats=export_formats, organize_by=organize_by)

        logger.info(f"Creating configuration file at {sentinel_path}")
        logger.info(f"\n{config.json(indent=2)}")
        with sentinel_path.open("w") as fp:
            fp.write(config.json(indent=2))
