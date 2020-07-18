from contextlib import contextmanager
import logging
import os
from pathlib import Path
import sys
from typing import List
from warnings import warn

from pydantic import BaseModel
from nbconvert.exporters import get_export_names, get_exporter
import nbformat

from nbautoexport._version import get_versions

logger = logging.getLogger("nbautoexport")
__version__ = get_versions()["version"]


class JupyterNotebook(BaseModel):
    path: Path
    metadata: nbformat.notebooknode.NotebookNode

    def get_script_extension(self):
        # Match logic of nbconvert.exporters.script.ScriptExporter
        # Order of precedence is: nb_convert_exporter, language, file_extension, .txt
        lang_info = self.metadata.get("language_info", {})
        if "nbconvert_exporter" in lang_info:
            return get_exporter(lang_info.nbconvert_exporter)().file_extension
        if "name" in lang_info and lang_info.name in get_export_names():
            return get_exporter(lang_info.name)().file_extension
        return lang_info.get("file_extension", ".txt")

    @property
    def name(self):
        return self.path.stem

    @classmethod
    def from_file(cls, path):
        notebook = nbformat.read(path, as_version=nbformat.NO_CONVERT)
        nbformat.validate(notebook)
        return cls(path=path, metadata=notebook.metadata)

    def __hash__(self):
        return hash(self.json())


def find_notebooks(directory: Path) -> List[JupyterNotebook]:
    """Finds Jupyter notebooks in a directory. Not recursive.

    Args:
        directory (Path): directory to search for notebook files

    Returns:
        List[JupyterNotebook]: notebooks found
    """
    notebooks = []
    for subfile in directory.iterdir():
        if subfile.is_file() and subfile.name:
            try:
                notebook = nbformat.read(str(subfile), as_version=nbformat.NO_CONVERT)
                nbformat.validate(notebook)
                notebooks.append(JupyterNotebook(path=subfile, metadata=notebook.metadata))
            except Exception as e:
                if subfile.suffix.lower() == ".ipynb":
                    warn(
                        f"Error reading {subfile.resolve()} as Jupyter Notebook: "
                        + f"[{type(e).__name__}] {e}"
                    )
    return notebooks


@contextmanager
def cleared_argv():
    """Context manager that temporarily clears sys.argv. Useful for wrapping nbconvert so
    unexpected arguments from outer program (e.g., nbautoexport) aren't passed to nbconvert.
    """
    prev_argv = [arg for arg in sys.argv]
    sys.argv = [sys.argv[0]]
    try:
        yield
    finally:
        sys.argv = prev_argv


@contextmanager
def working_directory(directory: Path):
    """Changes working directory and returns to previous on exit."""
    prev_cwd = Path.cwd()
    os.chdir(directory)
    try:
        yield
    finally:
        os.chdir(prev_cwd)
