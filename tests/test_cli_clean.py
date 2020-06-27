import shutil

import pytest
from typer.testing import CliRunner

from nbautoexport.clean import get_expected_exports, get_extension
from nbautoexport.nbautoexport import app
from nbautoexport.sentinel import ExportFormat, NbAutoexportConfig, SAVE_PROGRESS_INDICATOR_FILE
from nbautoexport.utils import JupyterNotebook

EXPECTED_NOTEBOOKS = [f"the_notebook_{n}" for n in range(3)]
UNEXPECTED_NOTEBOOK = "a_walk_to_remember"
EXPECTED_FORMATS = ["script", "html"]
UNEXPECTED_FORMAT = "latex"


@pytest.fixture()
def notebooks_dir(tmp_path, notebook_asset):
    notebooks = EXPECTED_NOTEBOOKS + [UNEXPECTED_NOTEBOOK]
    export_formats = [ExportFormat(fmt) for fmt in EXPECTED_FORMATS + [UNEXPECTED_FORMAT]]
    for nb_name in notebooks:
        shutil.copy(notebook_asset.path, tmp_path / f"{nb_name}.ipynb")
        nb = JupyterNotebook.from_file(tmp_path / f"{nb_name}.ipynb")

        # organize_by notebook
        nb_subfolder = tmp_path / nb.name
        nb_subfolder.mkdir()
        for fmt in export_formats:
            (nb_subfolder / f"{nb.name}{get_extension(nb, fmt)}").touch()

        # organize_by extension
        for fmt in export_formats:
            format_subfolder = tmp_path / fmt.value
            format_subfolder.mkdir(exist_ok=True)
            (format_subfolder / f"{nb.name}{get_extension(nb, fmt)}").touch()

        # add latex image dir
        (nb_subfolder / f"{nb.name}_files").mkdir()
        (nb_subfolder / f"{nb.name}_files" / f"{nb.name}_1_1.png").touch()
        (tmp_path / "latex" / f"{nb.name}_files").mkdir()
        (tmp_path / "latex" / f"{nb.name}_files" / f"{nb.name}_1_1.png").touch()

    (tmp_path / f"{UNEXPECTED_NOTEBOOK}.ipynb").unlink()

    return tmp_path


@pytest.mark.parametrize("need_confirmation", [True, False])
def test_clean_organize_by_extension(notebooks_dir, need_confirmation):
    sentinel_path = notebooks_dir / SAVE_PROGRESS_INDICATOR_FILE
    config = NbAutoexportConfig(export_formats=EXPECTED_FORMATS, organize_by="extension")
    with sentinel_path.open("w") as fp:
        fp.write(config.json())

    if need_confirmation:
        result = CliRunner().invoke(app, ["clean", str(notebooks_dir)], input="y")
    else:
        result = CliRunner().invoke(app, ["clean", str(notebooks_dir), "--yes"])
    assert result.exit_code == 0

    expected_notebooks = [
        JupyterNotebook.from_file(notebooks_dir / f"{nb}.ipynb") for nb in EXPECTED_NOTEBOOKS
    ]
    expected_exports = set(get_expected_exports(expected_notebooks, config))

    all_expected = {nb.path for nb in expected_notebooks} | expected_exports | {sentinel_path}
    assert set(notebooks_dir.glob("**/*")) == all_expected


@pytest.mark.parametrize("need_confirmation", [True, False])
def test_clean_organize_by_notebook(notebooks_dir, need_confirmation):
    sentinel_path = notebooks_dir / SAVE_PROGRESS_INDICATOR_FILE
    config = NbAutoexportConfig(export_formats=EXPECTED_FORMATS, organize_by="notebook")
    with sentinel_path.open("w") as fp:
        fp.write(config.json())

    if need_confirmation:
        result = CliRunner().invoke(app, ["clean", str(notebooks_dir)], input="y")
    else:
        result = CliRunner().invoke(app, ["clean", str(notebooks_dir), "--yes"])
    assert result.exit_code == 0

    expected_notebooks = [
        JupyterNotebook.from_file(notebooks_dir / f"{nb}.ipynb") for nb in EXPECTED_NOTEBOOKS
    ]
    expected_exports = set(get_expected_exports(expected_notebooks, config))

    all_expected = {nb.path for nb in expected_notebooks} | expected_exports | {sentinel_path}
    assert set(notebooks_dir.glob("**/*")) == all_expected


def test_clean_abort(notebooks_dir):
    sentinel_path = notebooks_dir / SAVE_PROGRESS_INDICATOR_FILE
    with sentinel_path.open("w") as fp:
        fp.write(NbAutoexportConfig(export_formats=EXPECTED_FORMATS).json())

    starting_files = set(notebooks_dir.glob("**/*"))

    result = CliRunner().invoke(app, ["clean", str(notebooks_dir)], input="n")
    assert result.exit_code == 1
    assert result.stdout.endswith("Aborted!\n")

    ending_files = set(notebooks_dir.glob("**/*"))

    # no files deleted
    assert starting_files == ending_files


def test_clean_dry_run(notebooks_dir):
    sentinel_path = notebooks_dir / SAVE_PROGRESS_INDICATOR_FILE
    with sentinel_path.open("w") as fp:
        fp.write(NbAutoexportConfig(export_formats=EXPECTED_FORMATS).json())

    starting_files = set(notebooks_dir.glob("**/*"))

    result = CliRunner().invoke(app, ["clean", str(notebooks_dir), "--dry-run"])
    assert result.exit_code == 0

    ending_files = set(notebooks_dir.glob("**/*"))

    # no files deleted
    assert starting_files == ending_files


def test_clean_no_directory_error():
    result = CliRunner().invoke(app, ["clean"])

    assert result.exit_code == 2
    assert "Error: Missing argument 'DIRECTORY'." in result.stdout


def test_clean_missing_config_error(notebooks_dir):
    sentinel_path = notebooks_dir / SAVE_PROGRESS_INDICATOR_FILE

    starting_files = set(notebooks_dir.glob("**/*"))

    result = CliRunner().invoke(app, ["clean", str(notebooks_dir)])
    assert result.exit_code == 1
    assert "Error: Missing expected nbautoexport config file" in result.stdout
    assert str(sentinel_path.resolve()) in result.stdout

    ending_files = set(notebooks_dir.glob("**/*"))

    # no files deleted
    assert starting_files == ending_files
