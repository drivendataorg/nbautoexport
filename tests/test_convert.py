import json
from pathlib import Path
import shutil
import sys

from nbautoexport.convert import post_save
from nbautoexport.sentinel import SAVE_PROGRESS_INDICATOR_FILE

NOTEBOOK_FILE = Path(__file__).parent / "assets" / "the_notebook.ipynb"


def test_post_save_no_sentinel(tmp_path):
    notebook_path = tmp_path / "the_notebook.ipynb"
    sentinel_path = tmp_path / SAVE_PROGRESS_INDICATOR_FILE
    shutil.copy(NOTEBOOK_FILE, notebook_path)

    assert notebook_path.exists()
    assert not sentinel_path.exists()
    post_save(model={"type": "notebook"}, os_path=str(notebook_path), contents_manager=None)
    assert set(tmp_path.iterdir()) == {notebook_path}


def test_post_save_organize_by_notebook(tmp_path, monkeypatch):
    notebook_path = tmp_path / "the_notebook.ipynb"
    sentinel_path = tmp_path / SAVE_PROGRESS_INDICATOR_FILE
    shutil.copy(NOTEBOOK_FILE, notebook_path)
    with sentinel_path.open("w") as fp:
        json.dump({"export_formats": ["script", "html"], "organize_by": "notebook"}, fp)

    monkeypatch.setattr(sys, "argv", [""])  # prevent pytest args from being passed to nbconvert

    assert notebook_path.exists()
    assert sentinel_path.exists()
    post_save(model={"type": "notebook"}, os_path=str(notebook_path), contents_manager=None)
    assert set(tmp_path.iterdir()) == {
        sentinel_path,  # sentinel file
        notebook_path,  # original ipynb
        tmp_path / "the_notebook",  # converted notebook directory
    }
    assert (tmp_path / "the_notebook").is_dir()
    assert (tmp_path / "the_notebook" / "the_notebook.py").exists()
    assert (tmp_path / "the_notebook" / "the_notebook.html").exists()


def test_post_save_organize_by_extension(tmp_path, monkeypatch):
    notebook_path = tmp_path / "the_notebook.ipynb"
    sentinel_path = tmp_path / SAVE_PROGRESS_INDICATOR_FILE
    shutil.copy(NOTEBOOK_FILE, notebook_path)
    with sentinel_path.open("w") as fp:
        json.dump({"export_formats": ["script", "html"], "organize_by": "extension"}, fp)

    monkeypatch.setattr(sys, "argv", [""])  # prevent pytest args from being passed to nbconvert

    assert notebook_path.exists()
    assert sentinel_path.exists()
    post_save(model={"type": "notebook"}, os_path=str(notebook_path), contents_manager=None)
    assert set(tmp_path.iterdir()) == {
        sentinel_path,  # sentinel file
        notebook_path,  # original ipynb
        tmp_path / "script",  # converted notebook directory
        tmp_path / "html",  # converted notebook directory
    }
    assert (tmp_path / "script").is_dir()
    assert (tmp_path / "html").is_dir()
    assert (tmp_path / "script" / "the_notebook.py").exists()
    assert (tmp_path / "html" / "the_notebook.html").exists()


def test_post_save_type_file(tmp_path, monkeypatch):
    notebook_path = tmp_path / "the_notebook.ipynb"
    sentinel_path = tmp_path / SAVE_PROGRESS_INDICATOR_FILE
    shutil.copy(NOTEBOOK_FILE, notebook_path)
    with sentinel_path.open("w") as fp:
        json.dump({"export_formats": ["script", "html"], "organize_by": "extension"}, fp)

    monkeypatch.setattr(sys, "argv", [""])  # prevent pytest args from being passed to nbconvert

    assert notebook_path.exists()
    assert sentinel_path.exists()
    post_save(model={"type": "file"}, os_path=str(notebook_path), contents_manager=None)
    assert set(tmp_path.iterdir()) == {
        sentinel_path,  # sentinel file
        notebook_path,  # original ipynb
    }


def test_post_save_type_directory(tmp_path, monkeypatch):
    notebook_path = tmp_path / "the_notebook.ipynb"
    sentinel_path = tmp_path / SAVE_PROGRESS_INDICATOR_FILE
    shutil.copy(NOTEBOOK_FILE, notebook_path)
    with sentinel_path.open("w") as fp:
        json.dump({"export_formats": ["script", "html"], "organize_by": "extension"}, fp)

    monkeypatch.setattr(sys, "argv", [""])  # prevent pytest args from being passed to nbconvert

    assert notebook_path.exists()
    assert sentinel_path.exists()
    post_save(model={"type": "directory"}, os_path=str(notebook_path), contents_manager=None)
    assert set(tmp_path.iterdir()) == {
        sentinel_path,  # sentinel file
        notebook_path,  # original ipynb
    }
