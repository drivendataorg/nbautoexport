import json

from nbconvert.exporters import get_export_names

from nbautoexport.clean import get_extension
from nbautoexport.sentinel import (
    ExportFormat,
    install_sentinel,
    NbAutoexportConfig,
    SAVE_PROGRESS_INDICATOR_FILE,
)


def test_export_format_compatibility():
    """Test that export formats are compatible with Jupyter nbautoconvert.
    """
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


def test_install_sentinel(tmp_path):
    export_formats = ["script", "html"]
    install_sentinel(
        directory=tmp_path, export_formats=export_formats, organize_by="notebook", overwrite=False
    )
    config = NbAutoexportConfig.parse_file(
        path=tmp_path / SAVE_PROGRESS_INDICATOR_FILE, content_type="application/json"
    )

    expected_config = NbAutoexportConfig(export_formats=export_formats, organize_by="notebook")
    assert config == expected_config
