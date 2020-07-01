from pathlib import Path
import sys

import pytest

from nbautoexport.utils import cleared_argv, find_notebooks, working_directory


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


def test_find_notebooks_warning(tmp_path):
    bad_notebook_path = tmp_path / "the_journal.ipynb"
    bad_notebook_path.touch()
    with pytest.warns(Warning, match="Error reading"):
        find_notebooks(tmp_path)


def test_cleared_argv(monkeypatch):
    """cleared_argv context manager clears sys.argv and restores it on exit
    """
    mocked_argv = ["nbautoexport", "convert", "the_notebook.ipynb", "-f", "script"]
    monkeypatch.setattr(sys, "argv", mocked_argv)

    assert sys.argv == mocked_argv

    with cleared_argv():
        assert sys.argv == mocked_argv[:1]

    assert sys.argv == mocked_argv


def test_cleared_argv_with_error(monkeypatch):
    """cleared_argv context manager restores sys.argv even with exception
    """
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
