import shutil

import pytest
from typer.testing import CliRunner

from nbautoexport.clean import get_expected_exports
from nbautoexport.nbautoexport import app
from nbautoexport.sentinel import NbAutoexportConfig
from nbautoexport.utils import find_notebooks


EXPECTED_NOTEBOOKS = [f"the_notebook_{n}" for n in range(3)]
EXPECTED_FORMATS = ["script", "html"]


@pytest.fixture()
def notebooks_dir(tmp_path, notebook_asset):
    notebooks = EXPECTED_NOTEBOOKS
    for nb in notebooks:
        shutil.copy(notebook_asset.path, tmp_path / f"{nb}.ipynb")
    return tmp_path


def test_convert_dir_organize_by_extension(notebooks_dir):
    cmd_list = ["convert", str(notebooks_dir), "-b", "extension"]
    for fmt in EXPECTED_FORMATS:
        cmd_list.append("-f")
        cmd_list.append(fmt)
    result = CliRunner().invoke(app, cmd_list)
    assert result.exit_code == 0

    expected_notebooks = find_notebooks(notebooks_dir)
    assert len(expected_notebooks) == len(EXPECTED_NOTEBOOKS)

    expected_notebook_files = {nb.path for nb in expected_notebooks}
    expected_exports = set(
        get_expected_exports(
            expected_notebooks,
            NbAutoexportConfig(export_formats=EXPECTED_FORMATS, organize_by="extension"),
        )
    )

    all_expected = expected_notebook_files | expected_exports

    assert set(notebooks_dir.glob("**/*")) == all_expected


def test_convert_dir_organize_by_notebook(notebooks_dir):
    cmd_list = ["convert", str(notebooks_dir), "-b", "notebook"]
    for fmt in EXPECTED_FORMATS:
        cmd_list.append("-f")
        cmd_list.append(fmt)
    result = CliRunner().invoke(app, cmd_list)
    assert result.exit_code == 0

    expected_notebooks = find_notebooks(notebooks_dir)
    assert len(expected_notebooks) == len(EXPECTED_NOTEBOOKS)

    expected_notebook_files = {nb.path for nb in expected_notebooks}
    expected_exports = set(
        get_expected_exports(
            expected_notebooks,
            NbAutoexportConfig(export_formats=EXPECTED_FORMATS, organize_by="notebook"),
        )
    )

    all_expected = expected_notebook_files | expected_exports
    assert set(notebooks_dir.glob("**/*")) == all_expected


def test_convert_single_organize_by_extension(notebooks_dir):
    expected_notebooks = find_notebooks(notebooks_dir)
    nb = expected_notebooks[0]

    cmd_list = ["convert", str(notebooks_dir / f"{nb.name}.ipynb"), "-b", "extension"]
    for fmt in EXPECTED_FORMATS:
        cmd_list.append("-f")
        cmd_list.append(fmt)
    result = CliRunner().invoke(app, cmd_list)
    assert result.exit_code == 0

    expected_notebook_files = {nb_.path for nb_ in expected_notebooks}
    expected_exports = set(
        get_expected_exports(
            [nb], NbAutoexportConfig(export_formats=EXPECTED_FORMATS, organize_by="extension"),
        )
    )

    all_expected = expected_notebook_files | expected_exports
    assert set(notebooks_dir.glob("**/*")) == all_expected


def test_convert_single_organize_by_notebook(notebooks_dir):
    expected_notebooks = find_notebooks(notebooks_dir)
    nb = expected_notebooks[0]

    cmd_list = ["convert", str(notebooks_dir / f"{nb.name}.ipynb"), "-b", "notebook"]
    for fmt in EXPECTED_FORMATS:
        cmd_list.append("-f")
        cmd_list.append(fmt)
    result = CliRunner().invoke(app, cmd_list)
    assert result.exit_code == 0

    expected_notebook_files = {nb_.path for nb_ in expected_notebooks}
    expected_exports = set(
        get_expected_exports(
            [nb], NbAutoexportConfig(export_formats=EXPECTED_FORMATS, organize_by="notebook"),
        )
    )

    all_expected = expected_notebook_files | expected_exports
    assert set(notebooks_dir.glob("**/*")) == all_expected


def test_convert_no_input():
    result = CliRunner().invoke(app, ["convert"])

    assert result.exit_code == 2
    assert "Error: Missing argument 'INPUT'." in result.stdout
