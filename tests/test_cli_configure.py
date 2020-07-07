"""Tests for `nbautoexport` package."""

import json

from typer.testing import CliRunner

from nbautoexport.nbautoexport import app
from nbautoexport.sentinel import install_sentinel, NbAutoexportConfig


def test_invalid_export_format():
    runner = CliRunner()
    result = runner.invoke(app, ["install", "-f", "invalid-output-format"])
    assert result.exit_code == 2
    assert (
        "Error: Invalid value for '--export-format' / '-f': invalid choice: invalid-output-format"
        in result.output
    )


def test_invalid_organize_by():
    runner = CliRunner()
    result = runner.invoke(app, ["install", "-b", "invalid-organize-by"])
    assert result.exit_code == 2
    assert (
        "Invalid value for '--organize-by' / '-b': invalid choice: invalid-organize-by"
        in result.output
    )


def test_refuse_overwrite(tmp_path):
    (tmp_path / ".nbautoexport").touch()
    runner = CliRunner()
    result = runner.invoke(app, ["install", str(tmp_path)])
    assert result.exit_code == 1
    assert "Detected existing autoexport configuration at" in result.output


def test_force_overwrite(tmp_path):
    (tmp_path / ".nbautoexport").touch()
    runner = CliRunner()
    result = runner.invoke(
        app, ["install", str(tmp_path), "-o", "-f", "script", "-f", "html", "-b", "notebook"]
    )
    print(result.output)
    print(result.exit_code)
    assert result.exit_code == 0
    with (tmp_path / ".nbautoexport").open("r") as fp:
        config = json.load(fp)

    expected_config = NbAutoexportConfig(export_formats=["script", "html"], organize_by="notebook")
    assert config == expected_config


def test_install_sentinel(tmp_path):
    export_formats = ["script", "html"]
    install_sentinel(export_formats, organize_by="notebook", directory=tmp_path, overwrite=False)
    with (tmp_path / ".nbautoexport").open("r") as fp:
        config = json.load(fp)

    expected_config = NbAutoexportConfig(export_formats=export_formats, organize_by="notebook")
    assert config == expected_config
