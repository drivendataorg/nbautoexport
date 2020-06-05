import pytest
from notebook.notebookapp import NotebookApp, list_running_servers, shutdown_server
from jupyterlab.labapp import LabApp
from multiprocessing import Process

from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "jupyter_notebook_config.py"
NOTEBOOK_DIR = Path(__file__).parent / "notebooks"


def launch_jupyter(app):
    return app.launch_instance(
        no_browser=True, config_file=str(CONFIG_PATH), notebook_dir=str(NOTEBOOK_DIR)
    )


@pytest.fixture()
def jupyter_notebook():
    p = Process(target=launch_jupyter, args=(NotebookApp,))
    p.start()
    yield
    print(list(list_running_servers()))
    this_server = [
        server
        for server in list_running_servers()
        if server["notebook_dir"] == str(NOTEBOOK_DIR.absolute)
    ][0]
    shutdown_server(this_server)


@pytest.fixture()
def juptyer_lab():
    p = Process(target=launch_jupyter, args=(LabApp,))
    p.start()
    yield
    shutdown_server(list(list_running_servers()))


def test_jupyter_notebook(jupyter_notebook):
    pass
