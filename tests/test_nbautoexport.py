"""Tests for `nbautoexport` package."""

from typer.testing import CliRunner
import json

from nbautoexport.nbautoexport import (
    app,
    install_sentinel,
)


def test_cli():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Exports Jupyter notebooks to various file formats" in result.output


def test_invalid_export_format():
    runner = CliRunner()
    result = runner.invoke(app, ["-f", "invalid-output-format"])
    assert result.exit_code == 2
    assert (
        "Error: Invalid value for '--export-format' / '-f': invalid choice: invalid-output-format"
        in result.output
    )


def test_invalid_organize_by():
    runner = CliRunner()
    result = runner.invoke(app, ["-b", "invalid-organize-by"])
    assert result.exit_code == 2
    assert (
        "Invalid value for '--organize-by' / '-b': invalid choice: invalid-organize-by"
        in result.output
    )


def test_refuse_overwrite(tmp_path_factory):
    directory = tmp_path_factory.mktemp("refuse_overwrite")
    (directory / ".nbautoexport").touch()
    runner = CliRunner()
    result = runner.invoke(app, ["-d", str(directory)])
    assert result.exit_code == 1
    assert "Detected existing autoexport configuration at" in result.output


def test_force_overwrite(tmp_path_factory):
    directory = tmp_path_factory.mktemp("force_overwrite")
    (directory / ".nbautoexport").touch()
    runner = CliRunner()
    result = runner.invoke(
        app, ["-d", str(directory), "-o", "-f", "script", "-f", "html", "-b", "notebook"]
    )
    print(result.output)
    print(result.exit_code)
    assert result.exit_code == 0
    with (directory / ".nbautoexport").open("r") as fp:
        config = json.load(fp)

    expected_config = {
        "export_formats": ["script", "html"],
        "organize_by": "notebook",
    }
    assert config == expected_config


def test_install_sentinel(tmp_path_factory):
    directory = tmp_path_factory.mktemp("install_sentinel")
    export_formats = ["script", "html"]
    install_sentinel(export_formats, organize_by="notebook", directory=directory, overwrite=False)
    with (directory / ".nbautoexport").open("r") as fp:
        config = json.load(fp)

    expected_config = {
        "export_formats": export_formats,
        "organize_by": "notebook",
    }
    assert config == expected_config
