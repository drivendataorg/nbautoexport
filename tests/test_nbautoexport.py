"""Tests for `nbautoexport` package."""

import pytest
from typer.testing import CliRunner
import json

from nbautoexport.nbautoexport import (
    app,
    install_sentinel,
)


def test_cli():
    """Test the CLI."""
    runner = CliRunner()
    help_result = runner.invoke(app, ["--help"])
    assert help_result.exit_code == 0
    assert "Exports Jupyter notebooks to various file formats" in help_result.output


def test_invalid_export_format():
    runner = CliRunner()
    help_result = runner.invoke(app, ["-f", "invalid-output-format"])
    assert help_result.exit_code == 2
    assert (
        "Error: Invalid value for '--export_format' / '-f': invalid choice: invalid-output-format"
        in help_result.output
    )


def test_invalid_organize_by():
    runner = CliRunner()
    help_result = runner.invoke(app, ["-b", "invalid-organize-by"])
    assert help_result.exit_code == 2
    assert (
        "Invalid value for '--organize_by' / '-b': invalid choice: invalid-organize-by"
        in help_result.output
    )


def test_warn_overwrite(tmp_path_factory):
    directory = tmp_path_factory.mktemp("install_sentinel")
    (directory / ".nbautoexport").touch()
    runner = CliRunner()
    help_result = runner.invoke(app, ["-b", "invalid-organize-by"])
    assert help_result.exit_code == 2
    assert (
        "Invalid value for '--organize_by' / '-b': invalid choice: invalid-organize-by"
        in help_result.output
    )


def test_install_sentinel(tmp_path_factory):
    directory = tmp_path_factory.mktemp("install_sentinel")
    export_formats = ["script", "html"]
    install_sentinel(export_formats, organize_by="extension", directory=directory, overwrite=False)
    with (directory / ".nbautoexport").open("r") as fp:
        config = json.load(fp)

    expected_config = {
        "export_formats": export_formats,
        "organize_by": "extension",
    }
    assert config == expected_config
