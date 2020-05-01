"""Tests for `nbautoexport` package."""

from click.testing import CliRunner
import json

from nbautoexport.nbautoexport import (
    install,
    install_sentinel,
)


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    help_result = runner.invoke(install, ["--help"])
    assert help_result.exit_code == 0
    assert "Exports Jupyter notebooks to various file formats" in help_result.output


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
