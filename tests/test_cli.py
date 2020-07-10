import subprocess

from typer.testing import CliRunner

from nbautoexport.nbautoexport import app
from nbautoexport import __version__


def test_main():
    """Test the CLI main callback."""
    runner = CliRunner()
    result = runner.invoke(app)
    assert result.exit_code == 0
    assert "Automatically export Jupyter notebooks to various file formats" in result.output


def test_main_help():
    """Test the CLI main callback with --help flag."""
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Automatically export Jupyter notebooks to various file formats" in result.output


def test_version():
    """Test the CLI main callback with --version flag."""
    runner = CliRunner()
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.output.strip() == __version__


def test_main_python_m():
    result = subprocess.run(
        ["python", "-m", "nbautoexport"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    assert result.returncode == 0
    assert "Automatically export Jupyter notebooks to various file formats" in result.stdout
    assert result.stdout.startswith("Usage: python -m nbautoexport")
    assert "Usage: __main__.py" not in result.stdout


def test_version_python_m():
    result = subprocess.run(
        ["python", "-m", "nbautoexport", "--version"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == __version__
