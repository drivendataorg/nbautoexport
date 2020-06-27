from pathlib import Path
import shutil

import pytest
from typer.testing import CliRunner

from nbautoexport.nbautoexport import app
from nbautoexport.sentinel import ExportFormat

NOTEBOOK_FILE = Path(__file__).parent / "assets" / "the_notebook.ipynb"

EXPECTED_NOTEBOOKS = [f"the_notebook_{n}" for n in range(3)]
EXPECTED_FORMATS = ["script", "html"]


@pytest.fixture()
def notebooks_dir(tmp_path):
    notebooks = EXPECTED_NOTEBOOKS
    for nb in notebooks:
        shutil.copy(NOTEBOOK_FILE, tmp_path / f"{nb}.ipynb")
    return tmp_path


def test_convert_dir_organize_by_extension(notebooks_dir):
    cmd_list = ["convert", str(notebooks_dir), "-b", "extension"]
    for fmt in EXPECTED_FORMATS:
        cmd_list.append("-f")
        cmd_list.append(fmt)
    result = CliRunner().invoke(app, cmd_list)
    assert result.exit_code == 0

    expected_notebooks = {notebooks_dir / f"{nb}.ipynb" for nb in EXPECTED_NOTEBOOKS}
    expected_export_dirs = {notebooks_dir / fmt for fmt in EXPECTED_FORMATS}
    expected_export_files = {
        notebooks_dir / fmt / f"{nb}{ExportFormat.get_extension(fmt, language='python')}"
        for nb in EXPECTED_NOTEBOOKS
        for fmt in EXPECTED_FORMATS
    }

    all_expected = expected_notebooks | expected_export_dirs | expected_export_files
    assert set(notebooks_dir.glob("**/*")) == all_expected


def test_convert_dir_organize_by_notebook(notebooks_dir):
    cmd_list = ["convert", str(notebooks_dir), "-b", "notebook"]
    for fmt in EXPECTED_FORMATS:
        cmd_list.append("-f")
        cmd_list.append(fmt)
    result = CliRunner().invoke(app, cmd_list)
    assert result.exit_code == 0

    expected_notebooks = {notebooks_dir / f"{nb}.ipynb" for nb in EXPECTED_NOTEBOOKS}
    expected_export_dirs = {notebooks_dir / nb for nb in EXPECTED_NOTEBOOKS}
    expected_export_files = {
        notebooks_dir / nb / f"{nb}{ExportFormat.get_extension(fmt, language='python')}"
        for nb in EXPECTED_NOTEBOOKS
        for fmt in EXPECTED_FORMATS
    }

    all_expected = expected_notebooks | expected_export_dirs | expected_export_files
    assert set(notebooks_dir.glob("**/*")) == all_expected


def test_convert_single_organize_by_extension(notebooks_dir):
    nb = EXPECTED_NOTEBOOKS[0]
    cmd_list = ["convert", str(notebooks_dir / f"{nb}.ipynb"), "-b", "extension"]
    for fmt in EXPECTED_FORMATS:
        cmd_list.append("-f")
        cmd_list.append(fmt)
    result = CliRunner().invoke(app, cmd_list)
    assert result.exit_code == 0

    expected_notebooks = {notebooks_dir / f"{nb_}.ipynb" for nb_ in EXPECTED_NOTEBOOKS}
    expected_export_dirs = {notebooks_dir / fmt for fmt in EXPECTED_FORMATS}
    expected_export_files = {
        notebooks_dir / fmt / f"{nb}{ExportFormat.get_extension(fmt, language='python')}"
        for fmt in EXPECTED_FORMATS
    }

    all_expected = expected_notebooks | expected_export_dirs | expected_export_files
    assert set(notebooks_dir.glob("**/*")) == all_expected


def test_convert_single_organize_by_notebook(notebooks_dir):
    nb = EXPECTED_NOTEBOOKS[0]
    cmd_list = ["convert", str(notebooks_dir / f"{nb}.ipynb"), "-b", "notebook"]
    for fmt in EXPECTED_FORMATS:
        cmd_list.append("-f")
        cmd_list.append(fmt)
    result = CliRunner().invoke(app, cmd_list)
    assert result.exit_code == 0

    expected_notebooks = {notebooks_dir / f"{nb_}.ipynb" for nb_ in EXPECTED_NOTEBOOKS}
    expected_export_dirs = {notebooks_dir / nb}
    expected_export_files = {
        notebooks_dir / nb / f"{nb}{ExportFormat.get_extension(fmt, language='python')}"
        for fmt in EXPECTED_FORMATS
    }

    all_expected = expected_notebooks | expected_export_dirs | expected_export_files
    assert set(notebooks_dir.glob("**/*")) == all_expected


def test_convert_no_input():
    result = CliRunner().invoke(app, ["convert"])

    assert result.exit_code == 2
    assert "Error: Missing argument 'INPUT'." in result.stdout
