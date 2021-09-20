from pathlib import Path

import pytest
from nbautoexport.utils import cleared_argv, JupyterNotebook
from traitlets.config.application import Application


@pytest.fixture(scope="session")
def notebook_asset():
    return JupyterNotebook.from_file(Path(__file__).parent / "assets" / "the_notebook.ipynb")


class MockJupyterApp(Application):
    pass


@pytest.fixture
def mock_jupyter_app(caplog):
    """Traitlets application that mocks an active Jupyter server."""
    with cleared_argv():
        MockJupyterApp.launch_instance()
    app = MockJupyterApp.instance()
    app.log.addHandler(caplog.handler)
    yield app
    app.log.removeHandler(caplog.handler)
    app.clear_instance()
