from typing import Iterable, List, Set
from pathlib import Path

from nbconvert.exporters import get_exporter

from nbautoexport.utils import find_notebooks, JupyterNotebook
from nbautoexport.sentinel import (
    ExportFormat,
    NbAutoexportConfig,
    OrganizeBy,
    SAVE_PROGRESS_INDICATOR_FILE,
)

FORMATS_WITH_IMAGE_DIR = [
    ExportFormat.asciidoc,
    ExportFormat.latex,
    ExportFormat.markdown,
    ExportFormat.rst,
]


def get_extension(notebook: JupyterNotebook, export_format: ExportFormat) -> str:
    """Given a notebook and export format, return expected export file extension.

    Args:
        notebook (JupyterNotebook): notebook to determine extension for
        export_format (str): export format name

    Returns:
        str: file extension, e.g., '.py'
    """
    # Script format needs notebook to determine appropriate language's extension
    if ExportFormat(export_format) == ExportFormat.script:
        return notebook.get_script_extension()

    exporter = get_exporter(ExportFormat(export_format).value)

    if ExportFormat(export_format) == ExportFormat.notebook:
        return f".nbconvert{exporter().file_extension}"
    return exporter().file_extension


def notebook_exports_generator(
    notebook: JupyterNotebook, export_format: ExportFormat, organize_by: OrganizeBy
) -> Iterable[Path]:
    """Generator that yields paths of expected exports for a notebook given an export_format and
    an organize_by setting.

    Args:
        notebook (JupyterNotebook): notebook to get export paths for
        export_format (ExportFormat): export format
        organize_by (OrganizeBy): type of subfolder approach

    Yields:
        Path: expected export paths given notebook and configuration options
    """
    if organize_by == OrganizeBy.notebook:
        subfolder = notebook.path.parent / notebook.name
    elif organize_by == OrganizeBy.extension:
        subfolder = notebook.path.parent / export_format.value
    yield subfolder
    yield subfolder / f"{notebook.name}{get_extension(notebook, export_format)}"
    if export_format in FORMATS_WITH_IMAGE_DIR:
        image_dir = subfolder / f"{notebook.name}_files"
        if image_dir.exists():
            yield image_dir
            yield from image_dir.iterdir()


def get_expected_exports(
    notebooks: Iterable[JupyterNotebook], config: NbAutoexportConfig
) -> List[Path]:
    """Given an iterable of Jupyter notebooks, return list of paths of files that nbautoexport
    would be expected to export to given this configuration.

    Args:
        notebooks (Iterable[JupyterNotebooks]): iterable of notebooks

    Returns:
        List[Path]: list of expected nbautoexport output files, relative to notebook files
    """

    export_paths: Set[Path] = set()
    for notebook in notebooks:
        for export_format in config.export_formats:
            export_paths.update(
                notebook_exports_generator(notebook, export_format, config.organize_by)
            )
    return sorted(export_paths)


def globs(directory: Path, patterns: Iterable[str]) -> Iterable[Path]:
    """Generator that yields paths matching glob-style patterns relative to directory.

    Args:
        directory (Path): a directory
        patterns (Iterable[str]): glob-style patterns relative to directory

    Yields:
        Path: paths matching provided patterns relative to directory
    """
    for pattern in patterns:
        yield from directory.glob(pattern)


def find_files_to_clean(directory: Path, config: NbAutoexportConfig) -> List[Path]:
    """Given path to a notebooks directory watched by nbautoexport, find all files that are not
    expected exports by current nbautoexport configuration and existing notebooks, or other
    expected Jupyter or nbautoexport files.

    Args:
        directory (Path): notebooks directory to find files to clean up

    Returns:
        List[Path]: list of files to clean up
    """
    notebooks: List[JupyterNotebook] = find_notebooks(directory)
    expected_exports: List[Path] = get_expected_exports(notebooks, config)
    checkpoints = (f for f in directory.glob(".ipynb_checkpoints/*") if f.is_file())
    sentinel_path = directory / SAVE_PROGRESS_INDICATOR_FILE

    subfiles = (f for f in directory.glob("**/*") if f.is_file())

    to_clean = (
        set(subfiles)
        .difference(nb.path for nb in notebooks)
        .difference(expected_exports)
        .difference(globs(directory=directory, patterns=config.clean.exclude))
        .difference(checkpoints)
        .difference([sentinel_path])
    )
    return sorted(to_clean)
