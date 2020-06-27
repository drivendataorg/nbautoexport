from pathlib import Path

import pytest
from nbautoexport.utils import JupyterNotebook


@pytest.fixture(scope="session")
def notebook_asset():
    return JupyterNotebook.from_file(Path(__file__).parent / "assets" / "the_notebook.ipynb")
