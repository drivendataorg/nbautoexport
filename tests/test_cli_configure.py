"""Tests for `nbautoexport` package."""

import json

from typer.testing import CliRunner

from nbautoexport import jupyter_config
from nbautoexport.nbautoexport import app
from nbautoexport.sentinel import (
    CleanConfig,
    DEFAULT_EXPORT_FORMATS,
    DEFAULT_ORGANIZE_BY,
    NbAutoexportConfig,
    SAVE_PROGRESS_INDICATOR_FILE,
)


def test_configure_defaults(tmp_path):
    result = CliRunner().invoke(app, ["configure", str(tmp_path)])
    assert result.exit_code == 0

    config = NbAutoexportConfig.parse_file(
        path=tmp_path / SAVE_PROGRESS_INDICATOR_FILE,
        content_type="application/json",
        encoding="utf-8",
    )

    expected_config = NbAutoexportConfig()
    assert config == expected_config


def test_configure_specified(tmp_path):
    export_formats = ["script", "html"]
    organize_by = "notebook"
    clean_exclude = ["README.md", "images/*"]
    assert export_formats != DEFAULT_EXPORT_FORMATS
    assert organize_by != DEFAULT_ORGANIZE_BY

    cmd_list = ["configure", str(tmp_path)]
    for fmt in export_formats:
        cmd_list.extend(["-f", fmt])
    cmd_list.extend(["-b", organize_by])
    for excl in clean_exclude:
        cmd_list.extend(["-e", excl])

    result = CliRunner().invoke(app, cmd_list)
    assert result.exit_code == 0

    config = NbAutoexportConfig.parse_file(
        path=tmp_path / SAVE_PROGRESS_INDICATOR_FILE,
        content_type="application/json",
        encoding="utf-8",
    )

    expected_config = NbAutoexportConfig(
        export_formats=export_formats,
        organize_by=organize_by,
        clean=CleanConfig(exclude=clean_exclude),
    )
    assert config == expected_config


def test_invalid_export_format():
    runner = CliRunner()
    result = runner.invoke(app, ["configure", "-f", "invalid-output-format"])
    assert result.exit_code == 2
    assert (
        "Error: Invalid value for '--export-format' / '-f': invalid choice: invalid-output-format"
        in result.output
    )


def test_invalid_organize_by():
    runner = CliRunner()
    result = runner.invoke(app, ["configure", "-b", "invalid-organize-by"])
    assert result.exit_code == 2
    assert (
        "Invalid value for '--organize-by' / '-b': invalid choice: invalid-organize-by"
        in result.output
    )


def test_refuse_overwrite(tmp_path):
    (tmp_path / ".nbautoexport").touch()
    runner = CliRunner()
    result = runner.invoke(app, ["configure", str(tmp_path)])
    assert result.exit_code == 1
    assert "Detected existing autoexport configuration at" in result.output


def test_force_overwrite(tmp_path):
    (tmp_path / ".nbautoexport").touch()
    runner = CliRunner()
    result = runner.invoke(
        app, ["configure", str(tmp_path), "-o", "-f", "script", "-f", "html", "-b", "notebook"]
    )
    assert result.exit_code == 0
    with (tmp_path / ".nbautoexport").open("r", encoding="utf-8") as fp:
        config = json.load(fp)

    expected_config = NbAutoexportConfig(export_formats=["script", "html"], organize_by="notebook")
    assert config == expected_config


def test_configure_no_jupyter_config_warning(tmp_path, monkeypatch):
    monkeypatch.setenv("JUPYTER_CONFIG_DIR", str(tmp_path))

    result = CliRunner().invoke(app, ["configure", str(tmp_path)])
    assert result.exit_code == 0
    assert "Warning: nbautoexport is not properly installed with Jupyter." in result.output


def test_configure_no_initialize_warning(tmp_path, monkeypatch):
    monkeypatch.setenv("JUPYTER_CONFIG_DIR", str(tmp_path))

    (tmp_path / "jupyter_notebook_config.py").touch()

    result = CliRunner().invoke(app, ["configure", str(tmp_path)])
    assert result.exit_code == 0
    assert "Warning: nbautoexport is not properly installed with Jupyter." in result.output


def test_configure_oudated_initialize_warning(tmp_path, monkeypatch):
    monkeypatch.setenv("JUPYTER_CONFIG_DIR", str(tmp_path))

    jupyter_config_path = tmp_path / "jupyter_notebook_config.py"
    with jupyter_config_path.open("w", encoding="utf-8") as fp:
        initialize_block = jupyter_config.version_regex.sub(
            "0", jupyter_config.post_save_hook_initialize_block
        )
        fp.write(initialize_block)

    result = CliRunner().invoke(app, ["configure", str(tmp_path)])
    assert result.exit_code == 0
    assert "Warning: nbautoexport initialize is an older version." in result.output


def test_configure_no_warning(tmp_path, monkeypatch):
    monkeypatch.setenv("JUPYTER_CONFIG_DIR", str(tmp_path))

    jupyter_config.install_post_save_hook(tmp_path / "jupyter_notebook_config.py")

    result = CliRunner().invoke(app, ["configure", str(tmp_path)])
    assert result.exit_code == 0
    assert "Warning:" not in result.output


def test_configure_no_directory_error():
    result = CliRunner().invoke(app, ["configure"])

    assert result.exit_code == 2
    assert "Error: Missing argument 'DIRECTORY'." in result.stdout
