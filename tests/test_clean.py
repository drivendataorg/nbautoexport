import itertools
import shutil
import pytest

from nbautoexport.clean import notebook_exports_generator
from nbautoexport.export import export_notebook
from nbautoexport.sentinel import ExportFormat, NbAutoexportConfig, OrganizeBy
from nbautoexport.utils import find_notebooks

EXPORT_FORMATS_TO_TEST = [fmt for fmt in ExportFormat if fmt != ExportFormat.pdf]

EXPECTED_NOTEBOOKS = [f"the_notebook_{n}" for n in range(3)]


@pytest.fixture()
def notebooks_dir(tmp_path, notebook_asset):
    notebooks = EXPECTED_NOTEBOOKS
    for nb in notebooks:
        shutil.copy(notebook_asset.path, tmp_path / f"{nb}.ipynb")
    return tmp_path


@pytest.mark.parametrize(
    "export_format, organize_by", itertools.product(EXPORT_FORMATS_TO_TEST, OrganizeBy)
)
def test_notebook_exports_generator(notebooks_dir, export_format, organize_by):
    """Test that notebook_exports_generator matches what export_notebook produces."""
    notebook = find_notebooks(notebooks_dir)[0]
    notebook_files = {notebooks_dir / f"{nb}.ipynb" for nb in EXPECTED_NOTEBOOKS}

    config = NbAutoexportConfig(export_formats=[export_format], organize_by=organize_by)
    export_notebook(notebook.path, config)

    predicted_exports = set(notebook_exports_generator(notebook, export_format, organize_by))

    actual_exports = set(notebooks_dir.glob("**/*")).difference(notebook_files)
    assert predicted_exports == actual_exports
