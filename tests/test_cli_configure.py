"""Tests for `nbautoexport` package."""

import json

from typer.testing import CliRunner

from nbautoexport.nbautoexport import app
from nbautoexport.sentinel import NbAutoexportConfig


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
    print(result.output)
    print(result.exit_code)
    assert result.exit_code == 0
    with (tmp_path / ".nbautoexport").open("r") as fp:
        config = json.load(fp)

    expected_config = NbAutoexportConfig(export_formats=["script", "html"], organize_by="notebook")
    assert config == expected_config
