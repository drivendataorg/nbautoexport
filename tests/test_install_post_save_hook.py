import textwrap

from nbautoexport import __version__
import nbautoexport.nbautoexport as nbautoexport


def test_initialize_block():
    init_block = nbautoexport.post_save_hook_initialize_block
    assert __version__ in init_block
    assert init_block.startswith("# >>> nbautoexport initialize")
    assert init_block.endswith("# <<< nbautoexport initialize <<<\n")


def test_initialize_block_detection():
    old_config_text_no_version = """\
        print('hello world!')

        # >>> nbautoexport initialize >>>
        old_and_tired()
        # <<< nbautoexport initialize <<<

        print('good night world!')
    """

    assert nbautoexport.block_regex.search(old_config_text_no_version) is not None
    assert nbautoexport.version_regex.search(old_config_text_no_version) is None

    old_config_text_with_version = """\
        print('hello world!')

        # >>> nbautoexport initialize, version=[old_and_tired] >>>
        old_and_tired()
        # <<< nbautoexport initialize <<<

        print('good night world!')
    """
    assert nbautoexport.block_regex.search(old_config_text_with_version) is not None
    version_match = nbautoexport.version_regex.search(old_config_text_with_version)
    assert version_match is not None
    assert version_match.group() == "old_and_tired"


def test_install_hook_no_config(tmp_path_factory, monkeypatch):
    directory = tmp_path_factory.mktemp("no_existing")

    def mock_jupyter_config_dir():
        return str(directory)

    monkeypatch.setattr(nbautoexport, "jupyter_config_dir", mock_jupyter_config_dir)

    config_path = directory / "jupyter_notebook_config.py"

    assert not config_path.exists()

    nbautoexport.install_post_save_hook()

    assert config_path.exists()

    with config_path.open("r") as fp:
        config = fp.read()
    assert config == nbautoexport.post_save_hook_initialize_block


def test_install_hook_missing_config_dir(tmp_path_factory, monkeypatch):
    directory = tmp_path_factory.mktemp("no_existing_missing_dir")
    config_dir = directory / "not_yet_a_real_dir"

    def mock_jupyter_config_dir():
        return str(config_dir)

    monkeypatch.setattr(nbautoexport, "jupyter_config_dir", mock_jupyter_config_dir)

    config_path = config_dir / "jupyter_notebook_config.py"

    assert not config_dir.exists()
    assert not config_path.exists()

    nbautoexport.install_post_save_hook()

    assert config_dir.exists()
    assert config_path.exists()

    with config_path.open("r") as fp:
        config = fp.read()
    assert config == nbautoexport.post_save_hook_initialize_block


def test_install_hook_existing_config_no_hook(tmp_path_factory, monkeypatch):
    directory = tmp_path_factory.mktemp("existing_no_hook")

    def mock_jupyter_config_dir():
        return str(directory)

    monkeypatch.setattr(nbautoexport, "jupyter_config_dir", mock_jupyter_config_dir)

    config_path = directory / "jupyter_notebook_config.py"

    with config_path.open("w") as fp:
        fp.write("print('hello world!')")

    nbautoexport.install_post_save_hook()

    assert config_path.exists()

    with config_path.open("r") as fp:
        config = fp.read()
    assert config == (
        "print('hello world!')" + "\n" + nbautoexport.post_save_hook_initialize_block
    )


def test_install_hook_replace_hook_no_version(tmp_path_factory, monkeypatch):
    directory = tmp_path_factory.mktemp("replace_hook_no_version")

    def mock_jupyter_config_dir():
        return str(directory)

    monkeypatch.setattr(nbautoexport, "jupyter_config_dir", mock_jupyter_config_dir)

    config_path = directory / "jupyter_notebook_config.py"

    old_config_text = """\
        print('hello world!')

        # >>> nbautoexport initialize >>>
        old_and_tired()
        # <<< nbautoexport initialize <<<

        print('good night world!')
    """

    with config_path.open("w") as fp:
        fp.write(textwrap.dedent(old_config_text))

    nbautoexport.install_post_save_hook()

    assert config_path.exists()
    with config_path.open("r") as fp:
        config = fp.read()
    assert config == (
        "print('hello world!')\n\n"
        + nbautoexport.post_save_hook_initialize_block
        + "\nprint('good night world!')\n"
    )
    assert "old_and_tired()" not in config
    assert f"version=[{__version__}]" in config


def test_install_hook_replace_hook_older_version(tmp_path_factory, monkeypatch):
    directory = tmp_path_factory.mktemp("replace_hook_with_version")

    def mock_jupyter_config_dir():
        return str(directory)

    monkeypatch.setattr(nbautoexport, "jupyter_config_dir", mock_jupyter_config_dir)

    config_path = directory / "jupyter_notebook_config.py"

    old_config_text = """\
        print('hello world!')

        # >>> nbautoexport initialize, version=[0] >>>
        old_and_tired()
        # <<< nbautoexport initialize <<<

        print('good night world!')
    """

    with config_path.open("w") as fp:
        fp.write(textwrap.dedent(old_config_text))

    nbautoexport.install_post_save_hook()

    assert config_path.exists()
    with config_path.open("r") as fp:
        config = fp.read()
    assert config == (
        "print('hello world!')\n\n"
        + nbautoexport.post_save_hook_initialize_block
        + "\nprint('good night world!')\n"
    )
    assert "old_and_tired()" not in config
    assert f"version=[{__version__}]" in config
