from typer.testing import CliRunner

from nbautoexport.nbautoexport import app
from nbautoexport import jupyter_config


def test_install_new_config(tmp_path, monkeypatch):
    def mock_jupyter_config_dir():
        return str(tmp_path)

    monkeypatch.setattr(jupyter_config, "jupyter_config_dir", mock_jupyter_config_dir)

    config_path = tmp_path / "jupyter_notebook_config.py"

    result = CliRunner().invoke(app, ["install"])
    assert result.exit_code == 0
    assert config_path.exists()

    with config_path.open("r") as fp:
        config = fp.read()
    assert config == jupyter_config.post_save_hook_initialize_block


def test_install_existing_config(tmp_path, monkeypatch):
    def mock_jupyter_config_dir():
        return str(tmp_path)

    monkeypatch.setattr(jupyter_config, "jupyter_config_dir", mock_jupyter_config_dir)

    config_path = tmp_path / "jupyter_notebook_config.py"

    with config_path.open("w") as fp:
        fp.write("print('hello world!')")
    assert config_path.exists()

    result = CliRunner().invoke(app, ["install"])
    assert result.exit_code == 0
    assert config_path.exists()

    with config_path.open("r") as fp:
        config = fp.read()
    assert config == (
        "print('hello world!')" + "\n" + jupyter_config.post_save_hook_initialize_block
    )


def test_install_new_config_with_path(tmp_path):
    config_path = tmp_path / "nonstandard_config.py"

    result = CliRunner().invoke(app, ["install", "--jupyter-config", str(config_path)])
    assert result.exit_code == 0
    assert config_path.exists()

    with config_path.open("r") as fp:
        config = fp.read()
    assert config == jupyter_config.post_save_hook_initialize_block


def test_install_existing_config_with_path(tmp_path):
    config_path = tmp_path / "nonstandard_config.py"

    with config_path.open("w") as fp:
        fp.write("print('hello world!')")
    assert config_path.exists()

    result = CliRunner().invoke(app, ["install", "--jupyter-config", str(config_path)])
    assert result.exit_code == 0
    assert config_path.exists()

    with config_path.open("r") as fp:
        config = fp.read()
    assert config == (
        "print('hello world!')" + "\n" + jupyter_config.post_save_hook_initialize_block
    )
