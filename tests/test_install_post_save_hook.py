import textwrap

from nbautoexport import __version__
import nbautoexport.nbautoexport as nbautoexport


def test_initialize_block_content():
    init_block = nbautoexport.post_save_hook_initialize_block
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
    assert nbautoexport.block_regex.search(config_no_nbautoexport) is None
    assert nbautoexport.version_regex.search(config_no_nbautoexport) is None

    config_no_version = textwrap.dedent(
        """\
            print('hello world!')

            # >>> nbautoexport initialize >>>
            old_and_tired()
            # <<< nbautoexport initialize <<<

            print('good night world!')
    """
    )

    assert nbautoexport.block_regex.search(config_no_version) is not None
    assert nbautoexport.version_regex.search(config_no_version) is None

    config_with_version = textwrap.dedent(
        """\
            print('hello world!')

            # >>> nbautoexport initialize, version=[old_and_tired] >>>
            old_and_tired()
            # <<< nbautoexport initialize <<<

            print('good night world!')
    """
    )
    assert nbautoexport.block_regex.search(config_with_version) is not None
    version_match = nbautoexport.version_regex.search(config_with_version)
    assert version_match is not None
    assert version_match.group() == "old_and_tired"


def test_install_hook_no_config(tmp_path, monkeypatch):
    def mock_jupyter_config_dir():
        return str(tmp_path)

    monkeypatch.setattr(nbautoexport, "jupyter_config_dir", mock_jupyter_config_dir)

    config_path = tmp_path / "jupyter_notebook_config.py"

    assert not config_path.exists()

    nbautoexport.install_post_save_hook()

    assert config_path.exists()

    with config_path.open("r") as fp:
        config = fp.read()
    assert config == nbautoexport.post_save_hook_initialize_block


def test_install_hook_missing_config_dir(tmp_path, monkeypatch):
    config_dir = tmp_path / "not_yet_a_real_dir"

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


def test_install_hook_existing_config_no_hook(tmp_path, monkeypatch):
    def mock_jupyter_config_dir():
        return str(tmp_path)

    monkeypatch.setattr(nbautoexport, "jupyter_config_dir", mock_jupyter_config_dir)

    config_path = tmp_path / "jupyter_notebook_config.py"

    with config_path.open("w") as fp:
        fp.write("print('hello world!')")

    nbautoexport.install_post_save_hook()

    assert config_path.exists()

    with config_path.open("r") as fp:
        config = fp.read()
    assert config == (
        "print('hello world!')" + "\n" + nbautoexport.post_save_hook_initialize_block
    )


def test_install_hook_replace_hook_no_version(tmp_path, monkeypatch):
    def mock_jupyter_config_dir():
        return str(tmp_path)

    monkeypatch.setattr(nbautoexport, "jupyter_config_dir", mock_jupyter_config_dir)

    config_path = tmp_path / "jupyter_notebook_config.py"

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


def test_install_hook_replace_hook_older_version(tmp_path, monkeypatch):
    def mock_jupyter_config_dir():
        return str(tmp_path)

    monkeypatch.setattr(nbautoexport, "jupyter_config_dir", mock_jupyter_config_dir)

    config_path = tmp_path / "jupyter_notebook_config.py"

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
