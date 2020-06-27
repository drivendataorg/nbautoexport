import shutil

import pytest
from typer.testing import CliRunner

from nbautoexport.clean import get_expected_exports
from nbautoexport.nbautoexport import app
from nbautoexport.sentinel import NbAutoexportConfig, SAVE_PROGRESS_INDICATOR_FILE
from nbautoexport.utils import find_notebooks

EXPECTED_NOTEBOOKS = [f"the_notebook_{n}" for n in range(3)]
EXPECTED_FORMATS = ["script", "html"]


@pytest.fixture()
def notebooks_dir(tmp_path, notebook_asset):
    notebooks = EXPECTED_NOTEBOOKS
    for nb in notebooks:
        shutil.copy(notebook_asset.path, tmp_path / f"{nb}.ipynb")
    return tmp_path


def test_export_dir_organize_by_extension(notebooks_dir):
    sentinel_path = notebooks_dir / SAVE_PROGRESS_INDICATOR_FILE
    config = NbAutoexportConfig(export_formats=EXPECTED_FORMATS, organize_by="extension")
    with sentinel_path.open("w") as fp:
        fp.write(config.json())

    result = CliRunner().invoke(app, ["export", str(notebooks_dir)])
    assert result.exit_code == 0

    expected_notebooks = find_notebooks(notebooks_dir)
    assert len(expected_notebooks) == len(EXPECTED_NOTEBOOKS)

    expected_notebook_files = {nb.path for nb in expected_notebooks}
    expected_exports = set(get_expected_exports(expected_notebooks, config))

    all_expected = expected_notebook_files | expected_exports | {sentinel_path}
    assert set(notebooks_dir.glob("**/*")) == all_expected


def test_export_dir_organize_by_notebook(notebooks_dir):
    sentinel_path = notebooks_dir / SAVE_PROGRESS_INDICATOR_FILE
    config = NbAutoexportConfig(export_formats=EXPECTED_FORMATS, organize_by="notebook")
    with sentinel_path.open("w") as fp:
        fp.write(config.json())

    result = CliRunner().invoke(app, ["export", str(notebooks_dir)])
    assert result.exit_code == 0

    expected_notebooks = find_notebooks(notebooks_dir)
    assert len(expected_notebooks) == len(EXPECTED_NOTEBOOKS)

    expected_notebook_files = {nb.path for nb in expected_notebooks}
    expected_exports = set(get_expected_exports(expected_notebooks, config))

    all_expected = expected_notebook_files | expected_exports | {sentinel_path}
    assert set(notebooks_dir.glob("**/*")) == all_expected


def test_export_single_organize_by_extension(notebooks_dir):
    expected_notebooks = find_notebooks(notebooks_dir)
    nb = expected_notebooks[0]

    sentinel_path = notebooks_dir / SAVE_PROGRESS_INDICATOR_FILE
    config = NbAutoexportConfig(export_formats=EXPECTED_FORMATS, organize_by="extension")
    with sentinel_path.open("w") as fp:
        fp.write(config.json())

    result = CliRunner().invoke(app, ["export", str(nb.path)])
    assert result.exit_code == 0

    expected_notebook_files = {nb_.path for nb_ in expected_notebooks}
    expected_exports = set(get_expected_exports([nb], config))

    all_expected = expected_notebook_files | expected_exports | {sentinel_path}
    assert set(notebooks_dir.glob("**/*")) == all_expected


def test_export_single_organize_by_notebook(notebooks_dir):
    expected_notebooks = find_notebooks(notebooks_dir)
    nb = expected_notebooks[0]

    sentinel_path = notebooks_dir / SAVE_PROGRESS_INDICATOR_FILE
    config = NbAutoexportConfig(export_formats=EXPECTED_FORMATS, organize_by="notebook")
    with sentinel_path.open("w") as fp:
        fp.write(config.json())

    result = CliRunner().invoke(app, ["export", str(nb.path)])
    assert result.exit_code == 0

    expected_notebook_files = {nb_.path for nb_ in expected_notebooks}
    expected_exports = set(get_expected_exports([nb], config))

    all_expected = expected_notebook_files | expected_exports | {sentinel_path}
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
