import json
import shutil

import pytest

from nbautoexport.clean import FORMATS_WITH_IMAGE_DIR, get_extension
from nbautoexport.export import export_notebook, post_save
from nbautoexport.sentinel import ExportFormat, NbAutoexportConfig, SAVE_PROGRESS_INDICATOR_FILE
from nbautoexport.utils import JupyterNotebook


EXPORT_FORMATS_TO_TEST = [fmt for fmt in ExportFormat if fmt != ExportFormat.pdf]


@pytest.fixture()
def notebooks_dir(tmp_path, notebook_asset):
    shutil.copy(notebook_asset.path, tmp_path / "the_notebook.ipynb")
    return tmp_path


@pytest.mark.parametrize("organize_by", ["extension", "notebook"])
def test_export_notebook(notebooks_dir, organize_by):
    """Test that export notebook works. Explicitly write out expected files, because tests for
    get_expected_exports will compare against export_notebook.
    """
    notebook = JupyterNotebook.from_file(notebooks_dir / "the_notebook.ipynb")
    config = NbAutoexportConfig(export_formats=EXPORT_FORMATS_TO_TEST, organize_by=organize_by)
    export_notebook(notebook.path, config)

    expected_exports = set()
    for fmt in EXPORT_FORMATS_TO_TEST:
        if organize_by == "extension":
            subfolder = notebooks_dir / fmt.value
        elif organize_by == "notebook":
            subfolder = notebooks_dir / notebook.name
        extension = get_extension(notebook, fmt)

        expected_exports.add(subfolder)  # subfolder
        expected_exports.add(subfolder / f"{notebook.name}{extension}")  # export file

        if fmt in FORMATS_WITH_IMAGE_DIR:
            image_subfolder = subfolder / f"{notebook.name}_files"

            expected_exports.add(image_subfolder)  # image subdir
            expected_exports.add(image_subfolder / f"{notebook.name}_1_1.png")  # image file

    all_expected = {notebook.path} | expected_exports
    assert all_expected.issubset(set(notebooks_dir.glob("**/*")))


def test_post_save_no_sentinel(notebooks_dir):
    """Test that post_save does nothing with no sentinel file."""
    notebook_path = notebooks_dir / "the_notebook.ipynb"
    sentinel_path = notebooks_dir / SAVE_PROGRESS_INDICATOR_FILE

    assert notebook_path.exists()
    assert not sentinel_path.exists()
    post_save(model={"type": "notebook"}, os_path=str(notebook_path), contents_manager=None)
    assert set(notebooks_dir.iterdir()) == {notebook_path}


def test_post_save_organize_by_notebook(notebooks_dir):
    notebook_path = notebooks_dir / "the_notebook.ipynb"
    sentinel_path = notebooks_dir / SAVE_PROGRESS_INDICATOR_FILE
    with sentinel_path.open("w", encoding="utf-8") as fp:
        json.dump(
            NbAutoexportConfig(export_formats=["script", "html"], organize_by="notebook").dict(),
            fp,
        )

    assert notebook_path.exists()
    assert sentinel_path.exists()
    post_save(model={"type": "notebook"}, os_path=str(notebook_path), contents_manager=None)
    assert set(notebooks_dir.iterdir()) == {
        sentinel_path,  # sentinel file
        notebook_path,  # original ipynb
        notebooks_dir / "the_notebook",  # converted notebook directory
    }
    assert (notebooks_dir / "the_notebook").is_dir()
    assert (notebooks_dir / "the_notebook" / "the_notebook.py").exists()
    assert (notebooks_dir / "the_notebook" / "the_notebook.html").exists()


def test_post_save_organize_by_extension(notebooks_dir):
    notebook_path = notebooks_dir / "the_notebook.ipynb"
    sentinel_path = notebooks_dir / SAVE_PROGRESS_INDICATOR_FILE
    with sentinel_path.open("w", encoding="utf-8") as fp:
        json.dump(
            NbAutoexportConfig(export_formats=["script", "html"], organize_by="extension").dict(),
            fp,
        )

    assert notebook_path.exists()
    assert sentinel_path.exists()
    post_save(model={"type": "notebook"}, os_path=str(notebook_path), contents_manager=None)
    assert set(notebooks_dir.iterdir()) == {
        sentinel_path,  # sentinel file
        notebook_path,  # original ipynb
        notebooks_dir / "script",  # converted notebook directory
        notebooks_dir / "html",  # converted notebook directory
    }
    assert (notebooks_dir / "script").is_dir()
    assert (notebooks_dir / "html").is_dir()
    assert (notebooks_dir / "script" / "the_notebook.py").exists()
    assert (notebooks_dir / "html" / "the_notebook.html").exists()


def test_post_save_type_file(notebooks_dir):
    """Test that post_save should do nothing if model type is 'file'."""
    notebook_path = notebooks_dir / "the_notebook.ipynb"
    sentinel_path = notebooks_dir / SAVE_PROGRESS_INDICATOR_FILE
    with sentinel_path.open("w", encoding="utf-8") as fp:
        json.dump(NbAutoexportConfig().dict(), fp)

    assert notebook_path.exists()
    assert sentinel_path.exists()
    post_save(model={"type": "file"}, os_path=str(notebook_path), contents_manager=None)
    assert set(notebooks_dir.iterdir()) == {
        sentinel_path,  # sentinel file
        notebook_path,  # original ipynb
    }


def test_post_save_type_directory(notebooks_dir):
    """Test that post_save should do nothing if model type is 'directory'."""
    notebook_path = notebooks_dir / "the_notebook.ipynb"
    sentinel_path = notebooks_dir / SAVE_PROGRESS_INDICATOR_FILE
    with sentinel_path.open("w", encoding="utf-8") as fp:
        json.dump(NbAutoexportConfig().dict(), fp)

    assert notebook_path.exists()
    assert sentinel_path.exists()
    post_save(model={"type": "directory"}, os_path=str(notebook_path), contents_manager=None)
    assert set(notebooks_dir.iterdir()) == {
        sentinel_path,  # sentinel file
        notebook_path,  # original ipynb
    }
