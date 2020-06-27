import json
from pathlib import Path
import shutil

import pytest

from nbautoexport.export import export_notebook, post_save
from nbautoexport.sentinel import ExportFormat, NbAutoexportConfig, SAVE_PROGRESS_INDICATOR_FILE

NOTEBOOK_FILE = Path(__file__).parent / "assets" / "the_notebook.ipynb"


@pytest.fixture()
def notebooks_dir(tmp_path):
    shutil.copy(NOTEBOOK_FILE, tmp_path / "the_notebook.ipynb")
    return tmp_path


def test_export_notebook_by_extension(notebooks_dir):
    notebook_path = notebooks_dir / "the_notebook.ipynb"
    config = NbAutoexportConfig(
        export_formats=[fmt for fmt in ExportFormat], organize_by="extension"
    )
    export_notebook(notebook_path, config)

    expected_export_dirs = {notebooks_dir / fmt.value for fmt in ExportFormat}
    expected_export_files = {
        notebooks_dir
        / fmt.value
        / f"{notebook_path.stem}{ExportFormat.get_extension(fmt, language='python')}"
        for fmt in ExportFormat
    }
    all_expected = {notebook_path} | expected_export_dirs | expected_export_files
    assert all_expected.issubset(set(notebooks_dir.glob("**/*")))


def test_export_notebook_by_notebook(notebooks_dir):
    notebook_path = notebooks_dir / "the_notebook.ipynb"
    config = NbAutoexportConfig(
        export_formats=[fmt for fmt in ExportFormat], organize_by="notebook"
    )
    export_notebook(notebook_path, config)

    expected_export_dirs = {notebooks_dir / notebook_path.stem}
    expected_export_files = {
        notebooks_dir
        / notebook_path.stem
        / f"{notebook_path.stem}{ExportFormat.get_extension(fmt, language='python')}"
        for fmt in ExportFormat
    }
    all_expected = {notebook_path} | expected_export_dirs | expected_export_files
    assert all_expected.issubset(set(notebooks_dir.glob("**/*")))


def test_post_save_no_sentinel(notebooks_dir):
    """Test that post_save does nothing with no sentinel file.
    """
    notebook_path = notebooks_dir / "the_notebook.ipynb"
    sentinel_path = notebooks_dir / SAVE_PROGRESS_INDICATOR_FILE

    assert notebook_path.exists()
    assert not sentinel_path.exists()
    post_save(model={"type": "notebook"}, os_path=str(notebook_path), contents_manager=None)
    assert set(notebooks_dir.iterdir()) == {notebook_path}


def test_post_save_organize_by_notebook(notebooks_dir):
    notebook_path = notebooks_dir / "the_notebook.ipynb"
    sentinel_path = notebooks_dir / SAVE_PROGRESS_INDICATOR_FILE
    with sentinel_path.open("w") as fp:
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
    with sentinel_path.open("w") as fp:
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
    """Test that post_save should do nothing if model type is 'file'.
    """
    notebook_path = notebooks_dir / "the_notebook.ipynb"
    sentinel_path = notebooks_dir / SAVE_PROGRESS_INDICATOR_FILE
    with sentinel_path.open("w") as fp:
        json.dump(NbAutoexportConfig().dict(), fp)

    assert notebook_path.exists()
    assert sentinel_path.exists()
    post_save(model={"type": "file"}, os_path=str(notebook_path), contents_manager=None)
    assert set(notebooks_dir.iterdir()) == {
        sentinel_path,  # sentinel file
        notebook_path,  # original ipynb
    }


def test_post_save_type_directory(notebooks_dir):
    """Test that post_save should do nothing if model type is 'directory'.
    """
    notebook_path = notebooks_dir / "the_notebook.ipynb"
    sentinel_path = notebooks_dir / SAVE_PROGRESS_INDICATOR_FILE
    with sentinel_path.open("w") as fp:
        json.dump(NbAutoexportConfig().dict(), fp)

    assert notebook_path.exists()
    assert sentinel_path.exists()
    post_save(model={"type": "directory"}, os_path=str(notebook_path), contents_manager=None)
    assert set(notebooks_dir.iterdir()) == {
        sentinel_path,  # sentinel file
        notebook_path,  # original ipynb
    }


def test_post_save_clean(notebooks_dir):
    notebook_path = notebooks_dir / "the_notebook.ipynb"
    sentinel_path = notebooks_dir / SAVE_PROGRESS_INDICATOR_FILE
    with sentinel_path.open("w") as fp:
        json.dump(
            NbAutoexportConfig(
                export_formats=["script"], organize_by="extension", clean=True
            ).dict(),
            fp,
        )

    org_by_notebook_dir = notebooks_dir / "the_notebook"
    org_by_notebook_dir.mkdir()
    org_by_notebook_script = org_by_notebook_dir / "the_notebook.py"
    org_by_notebook_script.touch()
    html_dir = notebooks_dir / "html"
    html_dir.mkdir()
    html_file = html_dir / "the_notebook.html"
    html_file.touch()

    for path in [org_by_notebook_dir, org_by_notebook_script, html_dir, html_file]:
        assert path.exists()

    post_save(model={"type": "notebook"}, os_path=str(notebook_path), contents_manager=None)

    all_expected = {
        notebook_path,
        sentinel_path,
        notebooks_dir / "script",
        notebooks_dir / "script" / "the_notebook.py",
    }
    assert set(notebooks_dir.glob("**/*")) == all_expected
