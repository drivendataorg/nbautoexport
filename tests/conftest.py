from pathlib import Path

from jupyter_core.application import JupyterApp
import pytest

from nbautoexport.utils import JupyterNotebook


@pytest.fixture(autouse=True)
def disable_typer_rich_colors(monkeypatch):
    # https://rich.readthedocs.io/en/stable/console.html#environment-variables
    monkeypatch.setenv("TERM", "unknown")


@pytest.fixture(scope="session")
def notebook_asset():
    return JupyterNotebook.from_file(Path(__file__).parent / "assets" / "the_notebook.ipynb")


@pytest.fixture
def jupyter_app(caplog):
    """Initialized (but unlaunched) Jupyter app."""
    app = JupyterApp.instance()
    app.log.addHandler(caplog.handler)
    yield app
    app.log.removeHandler(caplog.handler)
    app.clear_instance()
