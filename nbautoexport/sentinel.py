from enum import Enum
from pathlib import Path
from typing import Iterable, List

from pydantic import BaseModel

from nbautoexport.utils import logger
from nbconvert.exporters import get_exporter, PythonExporter

SAVE_PROGRESS_INDICATOR_FILE = ".nbautoexport"


class ExportFormat(str, Enum):
    html = "html"
    latex = "latex"
    pdf = "pdf"
    slides = "slides"
    markdown = "markdown"
    asciidoc = "asciidoc"
    script = "script"
    notebook = "notebook"

    @classmethod
    def get_extension(cls, value: str) -> str:
        exporter = get_exporter(cls(value).value)
        return exporter().file_extension

    @staticmethod
    def get_script_extensions() -> List[str]:
        return [exporter().file_extension for exporter in [PythonExporter]]

    @classmethod
    def has_value(cls, value: str) -> bool:
        return any(level for level in cls if level.value == value)


class OrganizeBy(str, Enum):
    notebook = "notebook"
    extension = "extension"


class NbAutoexportConfig(BaseModel):
    export_formats: List[ExportFormat] = [ExportFormat.script]
    organize_by: OrganizeBy = OrganizeBy.extension
    clean: bool = False

    def expected_exports(self, notebook_paths: Iterable[Path]) -> List[Path]:
        notebook_names: List[str] = [notebook.stem for notebook in notebook_paths]
        if self.organize_by == OrganizeBy.notebook:
            export_paths = [
                Path(notebook) / f"{notebook}{ExportFormat.get_extension(export_format)}"
                for notebook in notebook_names
                for export_format in self.export_formats
            ]
            # special case for script, since it depends on language
            if ExportFormat.script in self.export_formats:
                export_paths += [
                    Path(notebook) / f"{notebook}{extension}"
                    for notebook in notebook_names
                    for extension in ExportFormat.get_script_extensions()
                ]
        elif self.organize_by == OrganizeBy.extension:
            export_paths = [
                Path(export_format.value)
                / f"{notebook}{ExportFormat.get_extension(export_format)}"
                for notebook in notebook_names
                for export_format in self.export_formats
            ]
            # special case for script, since it depends on language
            if ExportFormat.script in self.export_formats:
                export_paths += [
                    Path(ExportFormat.script.value) / f"{notebook}{extension}"
                    for notebook in notebook_names
                    for extension in ExportFormat.get_script_extensions()
                ]
        return sorted(export_paths)


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
