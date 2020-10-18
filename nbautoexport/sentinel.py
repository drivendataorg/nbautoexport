from enum import Enum
from pathlib import Path
from typing import List

from pydantic import BaseModel

from nbautoexport.utils import logger


SAVE_PROGRESS_INDICATOR_FILE = ".nbautoexport"


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
    def has_value(cls, value: str) -> bool:
        return any(level for level in cls if level.value == value)


class OrganizeBy(str, Enum):
    notebook = "notebook"
    extension = "extension"


DEFAULT_EXPORT_FORMATS = [ExportFormat.script]
DEFAULT_ORGANIZE_BY = OrganizeBy.extension


class CleanConfig(BaseModel):
    exclude: List[str] = []


class NbAutoexportConfig(BaseModel):
    export_formats: List[ExportFormat] = [ExportFormat(fmt) for fmt in DEFAULT_EXPORT_FORMATS]
    organize_by: OrganizeBy = OrganizeBy(DEFAULT_ORGANIZE_BY)
    clean: CleanConfig = CleanConfig()

    class Config:
        extra = "forbid"


def install_sentinel(directory: Path, config: NbAutoexportConfig, overwrite: bool):
    """Writes the configuration file to a specified directory."""
    sentinel_path = directory / SAVE_PROGRESS_INDICATOR_FILE

    if sentinel_path.exists() and (not overwrite):
        raise FileExistsError(
            f"""Detected existing autoexport configuration at {sentinel_path}. """
            """If you wish to overwrite, use the --overwrite flag."""
        )
    else:
        logger.info(f"Creating configuration file at {sentinel_path}")
        logger.info(f"\n{config.json(indent=2)}")
        with sentinel_path.open("w", encoding="utf-8") as fp:
            fp.write(config.json(indent=2))
