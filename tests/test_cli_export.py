from pathlib import Path
import shutil

import pytest
from typer.testing import CliRunner

from nbautoexport.nbautoexport import app
from nbautoexport.sentinel import (
    ExportFormat,
    NbAutoexportConfig,
    SAVE_PROGRESS_INDICATOR_FILE,
)

NOTEBOOK_FILE = Path(__file__).parent / "assets" / "the_notebook.ipynb"

EXPECTED_NOTEBOOKS = [f"the_notebook_{n}" for n in range(3)]
EXPECTED_FORMATS = ["script", "html"]


@pytest.fixture()
def notebooks_dir(tmp_path):
    notebooks = EXPECTED_NOTEBOOKS
    for nb in notebooks:
        shutil.copy(NOTEBOOK_FILE, tmp_path / f"{nb}.ipynb")
    return tmp_path


def test_export_dir_organize_by_extension(notebooks_dir):
    sentinel_path = notebooks_dir / SAVE_PROGRESS_INDICATOR_FILE
    with sentinel_path.open("w") as fp:
        fp.write(
            NbAutoexportConfig(export_formats=EXPECTED_FORMATS, organize_by="extension").json()
        )

    result = CliRunner().invoke(app, ["export", str(notebooks_dir)])
    assert result.exit_code == 0

    expected_notebooks = {notebooks_dir / f"{nb}.ipynb" for nb in EXPECTED_NOTEBOOKS}
    expected_export_dirs = {notebooks_dir / fmt for fmt in EXPECTED_FORMATS}
    expected_export_files = {
        notebooks_dir / fmt / f"{nb}{ExportFormat.get_extension(fmt, language='python')}"
        for nb in EXPECTED_NOTEBOOKS
        for fmt in EXPECTED_FORMATS
    }

    all_expected = (
        expected_notebooks | expected_export_dirs | expected_export_files | {sentinel_path}
    )
    assert set(notebooks_dir.glob("**/*")) == all_expected


def test_export_dir_organize_by_notebook(notebooks_dir):
    sentinel_path = notebooks_dir / SAVE_PROGRESS_INDICATOR_FILE
    with sentinel_path.open("w") as fp:
        fp.write(
            NbAutoexportConfig(export_formats=EXPECTED_FORMATS, organize_by="notebook").json()
        )

    result = CliRunner().invoke(app, ["export", str(notebooks_dir)])
    assert result.exit_code == 0

    expected_notebooks = {notebooks_dir / f"{nb}.ipynb" for nb in EXPECTED_NOTEBOOKS}
    expected_export_dirs = {notebooks_dir / nb for nb in EXPECTED_NOTEBOOKS}
    expected_export_files = {
        notebooks_dir / nb / f"{nb}{ExportFormat.get_extension(fmt, language='python')}"
        for nb in EXPECTED_NOTEBOOKS
        for fmt in EXPECTED_FORMATS
    }

    all_expected = (
        expected_notebooks | expected_export_dirs | expected_export_files | {sentinel_path}
    )
    assert set(notebooks_dir.glob("**/*")) == all_expected


def test_export_single_organize_by_extension(notebooks_dir):
    nb = EXPECTED_NOTEBOOKS[0]
    sentinel_path = notebooks_dir / SAVE_PROGRESS_INDICATOR_FILE
    with sentinel_path.open("w") as fp:
        fp.write(
            NbAutoexportConfig(export_formats=EXPECTED_FORMATS, organize_by="extension").json()
        )

    result = CliRunner().invoke(app, ["export", str(notebooks_dir / f"{nb}.ipynb")])
    assert result.exit_code == 0

    expected_notebooks = {notebooks_dir / f"{nb_}.ipynb" for nb_ in EXPECTED_NOTEBOOKS}
    expected_export_dirs = {notebooks_dir / fmt for fmt in EXPECTED_FORMATS}
    expected_export_files = {
        notebooks_dir / fmt / f"{nb}{ExportFormat.get_extension(fmt, language='python')}"
        for fmt in EXPECTED_FORMATS
    }

    all_expected = (
        expected_notebooks | expected_export_dirs | expected_export_files | {sentinel_path}
    )
    assert set(notebooks_dir.glob("**/*")) == all_expected


def test_export_single_organize_by_notebook(notebooks_dir):
    nb = EXPECTED_NOTEBOOKS[0]
    sentinel_path = notebooks_dir / SAVE_PROGRESS_INDICATOR_FILE
    with sentinel_path.open("w") as fp:
        fp.write(
            NbAutoexportConfig(export_formats=EXPECTED_FORMATS, organize_by="notebook").json()
        )

    result = CliRunner().invoke(app, ["export", str(notebooks_dir / f"{nb}.ipynb")])
    assert result.exit_code == 0

    expected_notebooks = {notebooks_dir / f"{nb_}.ipynb" for nb_ in EXPECTED_NOTEBOOKS}
    expected_export_dirs = {notebooks_dir / nb}
    expected_export_files = {
        notebooks_dir / nb / f"{nb}{ExportFormat.get_extension(fmt, language='python')}"
        for fmt in EXPECTED_FORMATS
    }

    all_expected = (
        expected_notebooks | expected_export_dirs | expected_export_files | {sentinel_path}
    )
    assert set(notebooks_dir.glob("**/*")) == all_expected


def test_export_no_input():
    result = CliRunner().invoke(app, ["export"])

    assert result.exit_code == 2
    assert "Error: Missing argument 'INPUT'." in result.stdout


def test_export_missing_config_error(notebooks_dir):
    sentinel_path = notebooks_dir / SAVE_PROGRESS_INDICATOR_FILE

    starting_files = set(notebooks_dir.glob("**/*"))

    result = CliRunner().invoke(app, ["export", str(notebooks_dir)])
    assert result.exit_code == 1
    assert "Error: Missing expected nbautoexport config file" in result.stdout
    assert str(sentinel_path.resolve()) in result.stdout

    ending_files = set(notebooks_dir.glob("**/*"))

    # no files deleted
    assert starting_files == ending_files
