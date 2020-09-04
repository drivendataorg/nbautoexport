from nbconvert.exporters import get_export_names

from nbautoexport.clean import get_extension
from nbautoexport.sentinel import ExportFormat


def test_export_format_compatibility():
    """Test that export formats are compatible with Jupyter nbautoconvert."""
    nbconvert_export_names = get_export_names()
    for export_format in ExportFormat:
        assert export_format.value in nbconvert_export_names


def test_export_format_extensions(notebook_asset):
    for level in ExportFormat:
        extension = get_extension(notebook_asset, level)
        assert isinstance(extension, str)
        assert extension.startswith(".")
        assert len(extension) > 1


def test_export_format_has_value():
    for level in ExportFormat:
        assert ExportFormat.has_value(level.value)

    assert not ExportFormat.has_value("paper")
