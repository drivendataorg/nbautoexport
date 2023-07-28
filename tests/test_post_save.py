import json
import logging
import shutil

import nbformat
from jupyter_server.services.contents.filemanager import FileContentsManager
import pytest
from traitlets.config import Config

from nbautoexport.jupyter_config import initialize_post_save_hook
from nbautoexport.sentinel import (
    ExportFormat,
    NbAutoexportConfig,
    OrganizeBy,
    SAVE_PROGRESS_INDICATOR_FILE,
)
from tests.utils import caplog_contains


@pytest.fixture()
def notebook_file(tmp_path, notebook_asset):
    nb_file = tmp_path / "the_notebook.ipynb"
    shutil.copy(notebook_asset.path, nb_file)
    return nb_file


@pytest.fixture()
def notebook_model(notebook_file):
    model = {
        "type": "notebook",
        "content": nbformat.read(str(notebook_file), as_version=nbformat.NO_CONVERT),
    }
    return model


@pytest.fixture()
def file_contents_manager(notebook_file):
    config = Config(FileContentsManager=FileContentsManager())
    config.FileContentsManager.root_dir = str(notebook_file.parent)
    initialize_post_save_hook(config)
    return config.FileContentsManager


def test_post_save(file_contents_manager, notebook_file, notebook_model, caplog):
    """Test that post_save function works when FileContentsManager saves based on config file."""
    caplog.set_level(logging.DEBUG)

    config = NbAutoexportConfig(
        export_formats=[ExportFormat.script], organize_by=OrganizeBy.extension
    )
    with (notebook_file.parent / SAVE_PROGRESS_INDICATOR_FILE).open("w", encoding="utf-8") as fp:
        fp.write(config.json())

    file_contents_manager.save(notebook_model, path=notebook_file.name)

    assert caplog_contains(
        caplog,
        level=logging.INFO,
        in_msg=f"nbautoexport | Exporting {notebook_file}",
    )
    caplog.clear()

    assert (notebook_file.parent / "script" / f"{notebook_file.stem}.py").exists()
    assert not (notebook_file.parent / notebook_file.stem / f"{notebook_file.stem}.html").exists()

    # Update config and check that output is different

    (notebook_file.parent / "script" / f"{notebook_file.stem}.py").unlink()

    config = NbAutoexportConfig(
        export_formats=[ExportFormat.html], organize_by=OrganizeBy.notebook
    )

    with (notebook_file.parent / SAVE_PROGRESS_INDICATOR_FILE).open("w", encoding="utf-8") as fp:
        fp.write(config.json())

    file_contents_manager.save(notebook_model, path=notebook_file.name)

    assert caplog_contains(
        caplog,
        level=logging.INFO,
        in_msg=f"nbautoexport | Exporting {notebook_file}",
    )
    caplog.clear()

    assert not (notebook_file.parent / "script" / f"{notebook_file.stem}.py").exists()
    assert (notebook_file.parent / notebook_file.stem / f"{notebook_file.stem}.html").exists()


def test_not_notebook(file_contents_manager, tmp_path):
    """Test that post_save function ignores non-notebook file when FileContentsManager saves."""
    config = NbAutoexportConfig(
        export_formats=[ExportFormat.script], organize_by=OrganizeBy.extension
    )
    with (tmp_path / SAVE_PROGRESS_INDICATOR_FILE).open("w", encoding="utf-8") as fp:
        fp.write(config.json())

    file_path = tmp_path / "journal.txt"
    with file_path.open("w", encoding="utf-8") as fp:
        fp.write("I'm a journal.")

    model = {
        "type": "file",
        "format": "text",
        "mimetype": "text/plain",
        "content": "I'm a journal.",
    }

    file_contents_manager.save(model, path=str(file_path.name))

    assert not (tmp_path / "script" / f"{file_path.stem}.py").exists()


def test_no_config(file_contents_manager, notebook_file, notebook_model):
    """Test that post_save function does nothing without nbautoexport config file when
    FileContentsManager saves."""
    file_contents_manager.save(notebook_model, path=notebook_file.name)

    assert set(notebook_file.parent.iterdir()) == {
        notebook_file.parent / ".ipynb_checkpoints",
        notebook_file,
    }


def test_invalid_config(file_contents_manager, notebook_file, notebook_model, caplog):
    """Test that post_save function gracefully logs errors."""
    config = NbAutoexportConfig(
        export_formats=[ExportFormat.script], organize_by=OrganizeBy.extension
    )
    invalid_config = json.loads(config.json())
    invalid_config["export_formats"] = ["triplicate"]
    with (notebook_file.parent / SAVE_PROGRESS_INDICATOR_FILE).open("w", encoding="utf-8") as fp:
        json.dump(invalid_config, fp)

    # Runs through, since error is caught
    file_contents_manager.save(notebook_model, path=notebook_file.name)

    assert caplog_contains(
        caplog,
        level=logging.ERROR,
        in_msg="nbautoexport | post_save failed due to ValidationError",
    )
    assert not (notebook_file.parent / "script" / f"{notebook_file.stem}.py").exists()
