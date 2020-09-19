from itertools import chain, product
from pathlib import Path
import shutil

import pytest
from typer.testing import CliRunner

from nbautoexport.clean import get_expected_exports
from nbautoexport.nbautoexport import app
from nbautoexport.sentinel import (
    NbAutoexportConfig,
    DEFAULT_EXPORT_FORMATS,
    SAVE_PROGRESS_INDICATOR_FILE,
)
from nbautoexport.utils import find_notebooks, working_directory

EXPECTED_NOTEBOOKS = [f"the_notebook_{n}" for n in range(3)]
EXPECTED_FORMATS = ["script", "html"]


@pytest.fixture()
def notebooks_dir(tmp_path, notebook_asset):
    notebooks = EXPECTED_NOTEBOOKS
    for nb in notebooks:
        shutil.copy(notebook_asset.path, tmp_path / f"{nb}.ipynb")
    return tmp_path


@pytest.mark.parametrize("input_type", ["dir", "notebook"])
def test_export_no_config_no_cli_opts(notebooks_dir, input_type):
    """Test export command with no config file and no CLI options. Should use default options."""
    expected_notebooks = find_notebooks(notebooks_dir)
    assert len(expected_notebooks) == len(EXPECTED_NOTEBOOKS)

    if input_type == "dir":
        expected_to_convert = expected_notebooks
        input_path = str(notebooks_dir)
    elif input_type == "notebook":
        expected_to_convert = expected_notebooks[:1]
        input_path = str(expected_notebooks[0].path)

    result = CliRunner().invoke(app, ["export", input_path])
    assert result.exit_code == 0

    expected_notebook_files = {nb.path for nb in expected_notebooks}
    expected_exports = set(get_expected_exports(expected_to_convert, NbAutoexportConfig()))

    all_expected = expected_notebook_files | expected_exports
    assert set(notebooks_dir.glob("**/*")) == all_expected


@pytest.mark.parametrize(
    "input_type, organize_by", product(["dir", "notebook"], ["extension", "notebook"])
)
def test_export_no_config_with_cli_opts(notebooks_dir, input_type, organize_by):
    """Test export command with no config file and CLI options. Should use CLI options."""
    expected_notebooks = find_notebooks(notebooks_dir)
    assert len(expected_notebooks) == len(EXPECTED_NOTEBOOKS)

    if input_type == "dir":
        expected_to_convert = expected_notebooks
        input_path = str(notebooks_dir)
    elif input_type == "notebook":
        expected_to_convert = expected_notebooks[:1]
        input_path = str(expected_notebooks[0].path)

    flags = list(chain(["-b", organize_by], *(["-f", fmt] for fmt in EXPECTED_FORMATS)))
    result = CliRunner().invoke(app, ["export", input_path] + flags)
    assert result.exit_code == 0

    assert set(EXPECTED_FORMATS) != set(DEFAULT_EXPORT_FORMATS)  # make sure test is meaningful

    expected_config = NbAutoexportConfig(export_formats=EXPECTED_FORMATS, organize_by=organize_by)
    expected_notebook_files = {nb.path for nb in expected_notebooks}
    expected_exports = set(get_expected_exports(expected_to_convert, expected_config))

    all_expected = expected_notebook_files | expected_exports
    assert set(notebooks_dir.glob("**/*")) == all_expected


@pytest.mark.parametrize(
    "input_type, organize_by", product(["dir", "notebook"], ["extension", "notebook"])
)
def test_export_with_config_no_cli_opts(notebooks_dir, input_type, organize_by):
    """Test that export works with a config and no CLI options. Should use config options."""
    expected_notebooks = find_notebooks(notebooks_dir)
    assert len(expected_notebooks) == len(EXPECTED_NOTEBOOKS)

    if input_type == "dir":
        expected_to_convert = expected_notebooks
        input_path = str(notebooks_dir)
    elif input_type == "notebook":
        expected_to_convert = expected_notebooks[:1]
        input_path = str(expected_notebooks[0].path)

    sentinel_path = notebooks_dir / SAVE_PROGRESS_INDICATOR_FILE
    config = NbAutoexportConfig(export_formats=EXPECTED_FORMATS, organize_by=organize_by)
    with sentinel_path.open("w", encoding="utf-8") as fp:
        fp.write(config.json())

    result = CliRunner().invoke(app, ["export", input_path])
    assert result.exit_code == 0

    expected_notebook_files = {nb.path for nb in expected_notebooks}
    expected_exports = set(get_expected_exports(expected_to_convert, config))

    all_expected = expected_notebook_files | expected_exports | {sentinel_path}
    assert set(notebooks_dir.glob("**/*")) == all_expected


@pytest.mark.parametrize(
    "input_type, organize_by", product(["dir", "notebook"], ["extension", "notebook"])
)
def test_export_with_config_with_cli_opts(notebooks_dir, input_type, organize_by):
    """Test that export works with both config and CLI options. CLI options should overide config."""
    expected_notebooks = find_notebooks(notebooks_dir)
    assert len(expected_notebooks) == len(EXPECTED_NOTEBOOKS)

    if input_type == "dir":
        expected_to_convert = expected_notebooks
        input_path = str(notebooks_dir)
    elif input_type == "notebook":
        expected_to_convert = expected_notebooks[:1]
        input_path = str(expected_notebooks[0].path)

    sentinel_path = notebooks_dir / SAVE_PROGRESS_INDICATOR_FILE
    written_config = NbAutoexportConfig()
    with sentinel_path.open("w", encoding="utf-8") as fp:
        fp.write(written_config.json())

    expected_config = NbAutoexportConfig(export_formats=EXPECTED_FORMATS, organize_by=organize_by)
    assert expected_config != written_config

    flags = list(chain(["-b", organize_by], *(["-f", fmt] for fmt in EXPECTED_FORMATS)))
    result = CliRunner().invoke(app, ["export", input_path] + flags)
    assert result.exit_code == 0

    expected_notebook_files = {nb.path for nb in expected_notebooks}
    expected_exports = set(get_expected_exports(expected_to_convert, expected_config))

    expected_exports_from_written = set(get_expected_exports(expected_to_convert, written_config))
    assert expected_exports != expected_exports_from_written

    all_expected = expected_notebook_files | expected_exports | {sentinel_path}
    assert set(notebooks_dir.glob("**/*")) == all_expected


@pytest.mark.parametrize(
    "input_type, organize_by", product(["dir", "notebook"], ["extension", "notebook"])
)
def test_export_relative(notebooks_dir, input_type, organize_by):
    """Test that export works relative to current working directory."""
    with working_directory(notebooks_dir):
        expected_notebooks = find_notebooks(Path())
        assert len(expected_notebooks) == len(EXPECTED_NOTEBOOKS)

        sentinel_path = Path(SAVE_PROGRESS_INDICATOR_FILE)
        config = NbAutoexportConfig(export_formats=EXPECTED_FORMATS, organize_by=organize_by)
        with sentinel_path.open("w", encoding="utf-8") as fp:
            fp.write(config.json())

        if input_type == "dir":
            expected_to_convert = expected_notebooks
            input_path = "."
        elif input_type == "notebook":
            expected_to_convert = expected_notebooks[:1]
            input_path = f"{expected_notebooks[0].path.name}"

        result = CliRunner().invoke(app, ["export", input_path])
        assert result.exit_code == 0

        expected_notebook_files = {nb.path for nb in expected_notebooks}
        expected_exports = set(get_expected_exports(expected_to_convert, config))

        all_expected = expected_notebook_files | expected_exports | {sentinel_path}
        assert set(Path().glob("**/*")) == all_expected


@pytest.mark.parametrize(
    "input_type, organize_by", product(["dir", "notebook"], ["extension", "notebook"])
)
def test_clean_relative_subdirectory(notebooks_dir, input_type, organize_by):
    """Test that export works for subdirectory relative to current working directory."""
    with working_directory(notebooks_dir):
        # Set up subdirectory
        subdir = Path("subdir")
        subdir.mkdir()
        for subfile in Path().iterdir():
            shutil.move(str(subfile), str(subdir))

        sentinel_path = subdir / SAVE_PROGRESS_INDICATOR_FILE
        config = NbAutoexportConfig(export_formats=EXPECTED_FORMATS, organize_by=organize_by)
        with sentinel_path.open("w", encoding="utf-8") as fp:
            fp.write(config.json())

        expected_notebooks = find_notebooks(subdir)
        assert len(expected_notebooks) == len(EXPECTED_NOTEBOOKS)

        if input_type == "dir":
            expected_to_convert = expected_notebooks
            input_path = "subdir"
        elif input_type == "notebook":
            expected_to_convert = expected_notebooks[:1]
            input_path = str(subdir / f"{expected_notebooks[0].path.name}")

        result = CliRunner().invoke(app, ["export", input_path])
        assert result.exit_code == 0

        expected_notebook_files = {nb.path for nb in expected_notebooks}
        expected_exports = set(get_expected_exports(expected_to_convert, config))

        all_expected = expected_notebook_files | expected_exports | {sentinel_path}
        assert set(subdir.glob("**/*")) == all_expected


def test_export_dir_no_notebooks_error(tmp_path):
    assert len(list(tmp_path.iterdir())) == 0
    result = CliRunner().invoke(app, ["export", str(tmp_path)])
    assert result.exit_code == 1
    assert result.stdout.startswith("No notebooks found in directory")


def test_export_notebook_doesnt_exist_error(tmp_path):
    nonexistent_notebook = tmp_path / "anne_hughes_diary.ipynb"
    assert not nonexistent_notebook.exists()
    result = CliRunner().invoke(app, ["export", str(nonexistent_notebook)])
    assert result.exit_code == 2
    assert "does not exist" in result.stdout


def test_export_no_input_error():
    result = CliRunner().invoke(app, ["export"])

    assert result.exit_code == 2
    assert "Error: Missing argument 'INPUT'." in result.stdout
