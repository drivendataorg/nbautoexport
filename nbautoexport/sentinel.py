from enum import Enum
from pathlib import Path
from typing import Iterable, List, Optional

from pydantic import BaseModel

from nbautoexport.utils import logger
from nbconvert.exporters import get_exporter, PythonExporter


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
    def get_extension(cls, value: str, language: Optional[str] = None) -> str:
        if cls(value) == cls.script and language == "python":
            return PythonExporter().file_extension
        exporter = get_exporter(cls(value).value)
        if cls(value) == cls.notebook:
            return f".nbconvert{exporter().file_extension}"
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
    export_formats: List[ExportFormat] = [ExportFormat(fmt) for fmt in DEFAULT_EXPORT_FORMATS]
    organize_by: OrganizeBy = OrganizeBy(DEFAULT_ORGANIZE_BY)
    clean: bool = False

    def expected_exports(self, notebook_paths: Iterable[Path]) -> List[Path]:
        """Given paths to a set of notebook files, return list of paths of files that nbautoexport
        would be expected to export to given this configuration.

        Args:
            notebook_paths (Iterable[Path]): iterable of notebook file paths

        Returns:
            List[Path]: list of expected nbautoexport output files, relative to notebook files
        """
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

    def files_to_clean(self, directory: Path) -> List[Path]:
        """Given path to a notebooks directory watched by nbautoexport, find all files that are not
        expected exports by current nbautoexport configuration and existing notebooks, or other
        expected Jupyter or nbautoexport files.

        Args:
            directory (Path): notebooks directory to find files to clean up

        Returns:
            List[Path]: list of files to clean up
        """
        notebook_paths = list(directory.glob("*.ipynb"))
        expected_exports = [directory / export for export in self.expected_exports(notebook_paths)]
        subfiles = (f for f in directory.glob("**/*") if f.is_file())
        checkpoints = (f for f in directory.glob(".ipynb_checkpoints/*") if f.is_file())
        sentinel_path = directory / SAVE_PROGRESS_INDICATOR_FILE

        to_clean = (
            set(subfiles)
            .difference(notebook_paths)
            .difference(expected_exports)
            .difference(checkpoints)
            .difference([sentinel_path])
        )
        return sorted(to_clean)


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
