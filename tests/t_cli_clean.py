import itertools
from pathlib import Path
import shutil

import pytest
from typer.testing import CliRunner

from nbautoexport.nbautoexport import app
from nbautoexport.sentinel import (
    ExportFormat,
    NbAutoexportConfig,
    SAVE_PROGRESS_INDICATOR_FILE,
    find_unwanted_outputs,
)

NOTEBOOK_FILE = Path(__file__).parent / "assets" / "the_notebook.ipynb"


@pytest.fixture()
def notebooks_dir(tmp_path):
    notebooks = [f"the_notebook_{n}" for n in range(3)]
    for nb in notebooks:
        shutil.copy(NOTEBOOK_FILE, tmp_path / f"{nb}.ipynb")

        # organize_by notebook
        nb_subfolder = tmp_path / nb
        nb_subfolder.mkdir()
        (nb_subfolder / f"{nb}.py").touch()

        # organize_by extension
        for export_format in ExportFormat:
            format_subfolder = tmp_path / export_format.value
            format_subfolder.mkdir(exist_ok=True)
            (format_subfolder / f"{nb}.ext").touch()

    return tmp_path


@pytest.mark.parametrize(
    "export_formats, organize_by",
    itertools.product([["script", "html"]], ["notebook", "extension"]),
)
def test_clean(notebooks_dir, export_formats, organize_by):
    sentinel_path = notebooks_dir / SAVE_PROGRESS_INDICATOR_FILE
    with sentinel_path.open("w") as fp:
        fp.write(NbAutoexportConfig(export_formats=export_formats, organize_by=organize_by).json())

    result = CliRunner().invoke(app, ["clean", str(notebooks_dir), "--yes"])
    print("---")
    print(result.stdout)
    print("---")
    assert result.exit_code == 0


def test_clean_no_directory():
    result = CliRunner().invoke(app, ["clean"])

    assert result.exit_code == 2
    assert "Error: Missing argument 'DIRECTORY'." in result.stdout


@pytest.mark.parametrize(
    "export_formats, organize_by",
    itertools.product([["script", "html"]], ["notebook", "extension"]),
)
def test_find(notebooks_dir, export_formats, organize_by):
    config = NbAutoexportConfig(export_formats=export_formats, organize_by=organize_by)
    result = find_unwanted_outputs(notebooks_dir, config)
