"""Tests for `nbautoexport` package."""

import json

from typer.testing import CliRunner

from nbautoexport import jupyter_config, nbautoexport
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


def test_install_no_jupyter_config_warning(tmp_path, monkeypatch):
    def mock_jupyter_config_dir():
        return str(tmp_path)

    monkeypatch.setattr(jupyter_config, "jupyter_config_dir", mock_jupyter_config_dir)

    result = CliRunner().invoke(app, ["configure", str(tmp_path)])
    assert result.exit_code == 0
    assert "Warning: nbautoexport is not properly installed with Jupyter." in result.output


def test_install_no_initialize_warning(tmp_path, monkeypatch):
    def mock_jupyter_config_dir():
        return str(tmp_path)

    monkeypatch.setattr(jupyter_config, "jupyter_config_dir", mock_jupyter_config_dir)

    (tmp_path / "jupyter_notebook_config.py").touch()

    result = CliRunner().invoke(app, ["configure", str(tmp_path)])
    assert result.exit_code == 0
    assert "Warning: nbautoexport is not properly installed with Jupyter." in result.output


def test_install_oudated_initialize_warning(tmp_path, monkeypatch):
    def mock_jupyter_config_dir():
        return str(tmp_path)

    monkeypatch.setattr(nbautoexport, "jupyter_config_dir", mock_jupyter_config_dir)

    jupyter_config_path = tmp_path / "jupyter_notebook_config.py"
    with jupyter_config_path.open("w") as fp:
        initialize_block = jupyter_config.version_regex.sub(
            "0", jupyter_config.post_save_hook_initialize_block
        )
        fp.write(initialize_block)

    result = CliRunner().invoke(app, ["configure", str(tmp_path)])
    assert result.exit_code == 0
    assert "Warning: nbautoexport initialize is an older version." in result.output


def test_install_no_warning(tmp_path, monkeypatch):
    def mock_jupyter_config_dir():
        return str(tmp_path)

    monkeypatch.setattr(jupyter_config, "jupyter_config_dir", mock_jupyter_config_dir)
    monkeypatch.setattr(nbautoexport, "jupyter_config_dir", mock_jupyter_config_dir)

    jupyter_config.install_post_save_hook(tmp_path / "jupyter_notebook_config.py")

    result = CliRunner().invoke(app, ["configure", str(tmp_path)])
    assert result.exit_code == 0
    assert "Warning:" not in result.output
