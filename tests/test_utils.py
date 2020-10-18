import json
from pathlib import Path
import shutil
import sys

import pytest

from nbautoexport.sentinel import NbAutoexportConfig, SAVE_PROGRESS_INDICATOR_FILE
from nbautoexport.utils import JupyterNotebook, cleared_argv, find_notebooks, working_directory


def test_get_script_extensions(notebook_asset, monkeypatch):
    # get extension from metadata.language_info.nbconvert_exporter
    assert notebook_asset.get_script_extension() == ".py"

    # fall back to metadata.language_info.name
    monkeypatch.delitem(notebook_asset.metadata.language_info, "nbconvert_exporter")
    assert notebook_asset.get_script_extension() == ".py"

    # metadata.language_info.name isn't known, fall back to metadata.language_info.file_extension
    monkeypatch.setitem(notebook_asset.metadata.language_info, "name", "mongoose")
    assert notebook_asset.get_script_extension() == ".py"

    # metadata.language_info.name is missing, fall back to metadata.language_info.file_extension
    monkeypatch.delitem(notebook_asset.metadata.language_info, "name")
    assert notebook_asset.get_script_extension() == ".py"

    # metadata.language_info.file_extension is missing, fall back to ".txt"
    monkeypatch.delitem(notebook_asset.metadata.language_info, "file_extension")
    assert notebook_asset.get_script_extension() == ".txt"

    # metadata.language_info is missing, fall back to ".txt"
    monkeypatch.delitem(notebook_asset.metadata, "language_info")
    assert notebook_asset.get_script_extension() == ".txt"


def test_find_notebooks(tmp_path, notebook_asset):
    shutil.copy(notebook_asset.path, tmp_path / "the_notebook_0.ipynb")
    shutil.copy(notebook_asset.path, tmp_path / "the_notebook_1.ipynb")
    expected_notebooks = [
        JupyterNotebook.from_file(tmp_path / "the_notebook_0.ipynb"),
        JupyterNotebook.from_file(tmp_path / "the_notebook_1.ipynb"),
    ]

    # Non-notebook files
    (tmp_path / "the_journal.txt").touch()
    with (tmp_path / "the_log.json").open("w", encoding="utf-8") as fp:
        json.dump(
            {
                "LOG ENTRY: SOL 61": "How come Aquaman can control whales?",
                "LOG ENTRY: SOL 381": "That makes me a pirate! A space pirate!",
            },
            fp,
        )
    with (tmp_path / SAVE_PROGRESS_INDICATOR_FILE).open("w", encoding="utf-8") as fp:
        fp.write(NbAutoexportConfig().json())

    found_notebooks = find_notebooks(tmp_path)

    assert set(found_notebooks) == set(expected_notebooks)


def test_find_notebooks_warning(tmp_path):
    bad_notebook_path = tmp_path / "the_journal.ipynb"
    bad_notebook_path.touch()
    with pytest.warns(Warning, match="Error reading"):
        find_notebooks(tmp_path)


def test_cleared_argv(monkeypatch):
    """cleared_argv context manager clears sys.argv and restores it on exit"""
    mocked_argv = ["nbautoexport", "convert", "the_notebook.ipynb", "-f", "script"]
    monkeypatch.setattr(sys, "argv", mocked_argv)

    assert sys.argv == mocked_argv

    with cleared_argv():
        assert sys.argv == mocked_argv[:1]

    assert sys.argv == mocked_argv


def test_cleared_argv_with_error(monkeypatch):
    """cleared_argv context manager restores sys.argv even with exception"""
    mocked_argv = ["nbautoexport", "convert", "the_notebook.ipynb", "-f", "script"]
    monkeypatch.setattr(sys, "argv", mocked_argv)

    assert sys.argv == mocked_argv

    with pytest.raises(Exception):
        with cleared_argv():
            assert sys.argv == mocked_argv[:1]
            raise Exception

    assert sys.argv == mocked_argv


def test_working_directory(tmp_path):
    cwd = Path.cwd()
    assert cwd != tmp_path
    with working_directory(tmp_path):
        assert Path.cwd() == tmp_path
    assert Path.cwd() == cwd
