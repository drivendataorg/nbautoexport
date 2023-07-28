import builtins
import logging
from pkg_resources import parse_version
from pkg_resources.extern.packaging.version import Version
import sys
import textwrap

from jupyter_server.services.contents.filemanager import FileContentsManager
from traitlets.config.loader import Config

from nbautoexport import __version__
import nbautoexport as nbautoexport_root
from nbautoexport import export, jupyter_config
from tests.utils import caplog_contains


def test_parse_version():
    """Test that current version is parsable by pkg_resources per PEP 440, so that it is properly
    sortable when we compare against previously installed initialize blocks.
    """
    version = parse_version(__version__)
    assert type(version) == Version


def test_initialize_block_content():
    init_block = jupyter_config.post_save_hook_initialize_block
    assert __version__ in init_block
    assert init_block.startswith("# >>> nbautoexport initialize")
    assert init_block.endswith("# <<< nbautoexport initialize <<<\n")


def test_initialize_block_regexes():
    config_no_nbautoexport = textwrap.dedent(
        """\
            print('hello world!')

            print('good night world!')
    """
    )
    assert jupyter_config.block_regex.search(config_no_nbautoexport) is None
    assert jupyter_config.version_regex.search(config_no_nbautoexport) is None

    config_no_version = textwrap.dedent(
        """\
            print('hello world!')

            # >>> nbautoexport initialize >>>
            old_and_tired()
            # <<< nbautoexport initialize <<<

            print('good night world!')
    """
    )

    assert jupyter_config.block_regex.search(config_no_version) is not None
    assert jupyter_config.version_regex.search(config_no_version) is None

    config_with_version = textwrap.dedent(
        """\
            print('hello world!')

            # >>> nbautoexport initialize, version=[old_and_tired] >>>
            old_and_tired()
            # <<< nbautoexport initialize <<<

            print('good night world!')
    """
    )
    assert jupyter_config.block_regex.search(config_with_version) is not None
    version_match = jupyter_config.version_regex.search(config_with_version)
    assert version_match is not None
    assert version_match.group() == "old_and_tired"


def test_install_hook_no_config(tmp_path, monkeypatch):
    def mock_jupyter_config_dir():
        return str(tmp_path)

    monkeypatch.setattr(jupyter_config, "jupyter_config_dir", mock_jupyter_config_dir)

    config_path = tmp_path / "jupyter_notebook_config.py"

    assert not config_path.exists()

    jupyter_config.install_post_save_hook()

    assert config_path.exists()

    with config_path.open("r", encoding="utf-8") as fp:
        config = fp.read()
    assert config == jupyter_config.post_save_hook_initialize_block


def test_install_hook_missing_config_dir(tmp_path, monkeypatch):
    config_dir = tmp_path / "not_yet_a_real_dir"

    def mock_jupyter_config_dir():
        return str(config_dir)

    monkeypatch.setattr(jupyter_config, "jupyter_config_dir", mock_jupyter_config_dir)

    config_path = config_dir / "jupyter_notebook_config.py"

    assert not config_dir.exists()
    assert not config_path.exists()

    jupyter_config.install_post_save_hook()

    assert config_dir.exists()
    assert config_path.exists()

    with config_path.open("r", encoding="utf-8") as fp:
        config = fp.read()
    assert config == jupyter_config.post_save_hook_initialize_block


def test_install_hook_existing_config_no_hook(tmp_path, monkeypatch):
    def mock_jupyter_config_dir():
        return str(tmp_path)

    monkeypatch.setattr(jupyter_config, "jupyter_config_dir", mock_jupyter_config_dir)

    config_path = tmp_path / "jupyter_notebook_config.py"

    with config_path.open("w", encoding="utf-8") as fp:
        fp.write("print('hello world!')")

    jupyter_config.install_post_save_hook()

    assert config_path.exists()

    with config_path.open("r", encoding="utf-8") as fp:
        config = fp.read()
    assert config == (
        "print('hello world!')" + "\n" + jupyter_config.post_save_hook_initialize_block
    )


def test_install_hook_replace_hook_no_version(tmp_path, monkeypatch):
    def mock_jupyter_config_dir():
        return str(tmp_path)

    monkeypatch.setattr(jupyter_config, "jupyter_config_dir", mock_jupyter_config_dir)

    config_path = tmp_path / "jupyter_notebook_config.py"

    old_config_text = """\
        print('hello world!')

        # >>> nbautoexport initialize >>>
        old_and_tired()
        # <<< nbautoexport initialize <<<

        print('good night world!')
    """

    with config_path.open("w", encoding="utf-8") as fp:
        fp.write(textwrap.dedent(old_config_text))

    jupyter_config.install_post_save_hook()

    assert config_path.exists()
    with config_path.open("r", encoding="utf-8") as fp:
        config = fp.read()
    assert config == (
        "print('hello world!')\n\n"
        + jupyter_config.post_save_hook_initialize_block
        + "\nprint('good night world!')\n"
    )
    assert "old_and_tired()" not in config
    assert f"version=[{__version__}]" in config


def test_install_hook_replace_hook_older_version(tmp_path, monkeypatch):
    def mock_jupyter_config_dir():
        return str(tmp_path)

    monkeypatch.setattr(jupyter_config, "jupyter_config_dir", mock_jupyter_config_dir)

    config_path = tmp_path / "jupyter_notebook_config.py"

    old_config_text = """\
        print('hello world!')

        # >>> nbautoexport initialize, version=[0] >>>
        old_and_tired()
        # <<< nbautoexport initialize <<<

        print('good night world!')
    """

    with config_path.open("w", encoding="utf-8") as fp:
        fp.write(textwrap.dedent(old_config_text))

    jupyter_config.install_post_save_hook()

    assert config_path.exists()
    with config_path.open("r", encoding="utf-8") as fp:
        config = fp.read()
    assert config == (
        "print('hello world!')\n\n"
        + jupyter_config.post_save_hook_initialize_block
        + "\nprint('good night world!')\n"
    )
    assert "old_and_tired()" not in config
    assert f"version=[{__version__}]" in config


def test_initialize_post_save_binding():
    """Test that post_save hook can be successfully bound to a Jupyter config."""
    jupyter_config_obj = Config(FileContentsManager=FileContentsManager())
    jupyter_config.initialize_post_save_hook(jupyter_config_obj)
    assert isinstance(jupyter_config_obj.FileContentsManager, FileContentsManager)
    assert jupyter_config_obj.FileContentsManager.post_save_hook is export.post_save


def test_initialize_post_save_execution(monkeypatch, caplog):
    """Test that post_save initialization works as expected and bound post_save executes."""
    caplog.set_level(logging.DEBUG)

    jupyter_config_obj = Config(FileContentsManager=FileContentsManager())

    def mocked_post_save(model, os_path, contents_manager):
        """Append a token to os_path to certify that function ran."""
        os_path.append("nbautoexport")

    monkeypatch.setattr(nbautoexport_root, "post_save", mocked_post_save)

    # Initialize post_save hook
    jupyter_config.initialize_post_save_hook(jupyter_config_obj)

    assert caplog_contains(
        caplog,
        level=logging.INFO,
        in_msg="nbautoexport | Successfully registered post-save hook",
    )
    assert isinstance(jupyter_config_obj.FileContentsManager, FileContentsManager)
    assert callable(jupyter_config_obj.FileContentsManager.post_save_hook)

    # Execute post_save hook
    os_path_list = []
    jupyter_config_obj.FileContentsManager.run_post_save_hook(model=None, os_path=os_path_list)
    assert os_path_list == ["nbautoexport"]


def test_initialize_post_save_existing(monkeypatch, caplog):
    """Test that handling of existing post_save hook works properly."""
    caplog.set_level(logging.DEBUG)

    jupyter_config_obj = Config(FileContentsManager=FileContentsManager())

    def old_post_save(model, os_path, contents_manager):
        """Append a token to os_path to certify that function ran."""
        os_path.append("old_post_save")

    jupyter_config_obj.FileContentsManager.post_save_hook = old_post_save

    def mocked_post_save(model, os_path, contents_manager):
        """Append a token to os_path to certify that function ran."""
        os_path.append("nbautoexport")

    monkeypatch.setattr(nbautoexport_root, "post_save", mocked_post_save)

    # Initialize post_save hook
    jupyter_config.initialize_post_save_hook(jupyter_config_obj)

    assert caplog_contains(
        caplog,
        level=logging.INFO,
        in_msg="nbautoexport | Existing post_save_hook found",
    )
    assert caplog_contains(
        caplog,
        level=logging.INFO,
        in_msg="nbautoexport | Successfully registered post-save hook",
    )
    assert isinstance(jupyter_config_obj.FileContentsManager, FileContentsManager)
    assert callable(jupyter_config_obj.FileContentsManager.post_save_hook)

    # Execute post_save hook
    os_path_list = []
    jupyter_config_obj.FileContentsManager.run_post_save_hook(model=None, os_path=os_path_list)
    assert os_path_list == ["old_post_save", "nbautoexport"]


def test_initialize_post_save_import_error_caught(monkeypatch, caplog, jupyter_app):
    """Test that missing nbautoexport error is caught and properly logged."""

    real_import = __builtins__["__import__"]

    def mock_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "nbautoexport":
            raise ModuleNotFoundError("No module named 'nbautoexport'")
        return real_import(
            name=name, globals=globals, locals=locals, fromlist=fromlist, level=level
        )

    monkeypatch.setattr(builtins, "__import__", mock_import)
    monkeypatch.delitem(sys.modules, "nbautoexport")

    jupyter_config_obj = Config(FileContentsManager=FileContentsManager())

    # Initialize post_save hook
    # Should run through since error is caught
    jupyter_config.initialize_post_save_hook(jupyter_config_obj)

    assert caplog_contains(
        caplog,
        name=jupyter_app.log.name,
        level=logging.ERROR,
        in_msg="ModuleNotFoundError: No module named 'nbautoexport'",
    )


def test_initialize_post_save_double_import_error_caught(monkeypatch, caplog, capsys, jupyter_app):
    """Test that both missing nbautoexport error and missing jupyer_core are caught and properly
    logged."""

    real_import = __builtins__["__import__"]

    def mock_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "nbautoexport":
            raise ModuleNotFoundError("No module named 'nbautoexport'")
        if name == "jupyter_core.application":
            raise ModuleNotFoundError("No module named 'jupyter_core.application'")
        return real_import(
            name=name, globals=globals, locals=locals, fromlist=fromlist, level=level
        )

    monkeypatch.setattr(builtins, "__import__", mock_import)
    monkeypatch.delitem(sys.modules, "nbautoexport")
    monkeypatch.delitem(sys.modules, "jupyter_core.application")

    jupyter_config_obj = Config(FileContentsManager=FileContentsManager())

    # Initialize post_save hook
    # Should run through since error is caught
    jupyter_config.initialize_post_save_hook(jupyter_config_obj)

    # Caplog should be empty, since logger didn't work
    assert len(caplog.record_tuples) == 0

    # Errors should be in stderr
    captured = capsys.readouterr()
    assert "ModuleNotFoundError: No module named 'jupyter_core.application'" in captured.err
    assert "ModuleNotFoundError: No module named 'nbautoexport'" in captured.err
