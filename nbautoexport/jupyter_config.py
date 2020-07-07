from inspect import getsourcelines
from pathlib import Path
from pkg_resources import parse_version
import re
import textwrap
from typing import Optional

from jupyter_core.paths import jupyter_config_dir
from traitlets.config.loader import Config

from nbautoexport.utils import __version__, logger


def initialize_post_save_hook(c: Config):
    # >>> nbautoexport initialize, version=[{version}] >>>
    try:
        from nbautoexport import post_save

        if callable(c.FileContentsManager.post_save_hook):
            old_post_save = c.FileContentsManager.post_save_hook

            def _post_save(model, os_path, contents_manager):
                old_post_save(model=model, os_path=os_path, contents_manager=contents_manager)
                post_save(model=model, os_path=os_path, contents_manager=contents_manager)

            c.FileContentsManager.post_save_hook = _post_save
        else:
            c.FileContentsManager.post_save_hook = post_save
    except Exception:
        pass
    # <<< nbautoexport initialize <<<
    pass  # need this line for above comment to be included in function source


post_save_hook_initialize_block = textwrap.dedent(
    "".join(getsourcelines(initialize_post_save_hook)[0][1:-1]).format(version=__version__)
)

block_regex = re.compile(
    r"# >>> nbautoexport initialize.*# <<< nbautoexport initialize <<<\n?",
    re.DOTALL,  # dot matches newline
)
version_regex = re.compile(r"(?<=# >>> nbautoexport initialize, version=\[).*(?=\] >>>)")


def install_post_save_hook(config_file: Optional[Path] = None):
    """Splices the post save hook into the global Jupyter configuration file
    """
    if config_file is None:
        config_dir = jupyter_config_dir()
        config_file = Path(config_dir) / "jupyter_notebook_config.py"

    config_file = config_file.expanduser().resolve()

    if not config_file.exists():
        logger.debug(f"No existing Jupyter configuration detected at {config_file}. Creating...")
        config_file.parent.mkdir(exist_ok=True, parents=True)
        with config_file.open("w") as fp:
            fp.write(post_save_hook_initialize_block)
        logger.info("nbautoexport post-save hook installed.")
        return

    # If config exists, check for existing nbautoexport initialize block and install as appropriate
    logger.debug(f"Detected existing Jupyter configuration at {config_file}")

    with config_file.open("r") as fp:
        config = fp.read()

    if block_regex.search(config):
        logger.debug("Detected existing nbautoexport post-save hook.")

        version_match = version_regex.search(config)
        if version_match:
            existing_version = version_match.group()
            logger.debug(f"Existing post-save hook is version {existing_version}")
        else:
            existing_version = ""
            logger.debug("Existing post-save hook predates versioning.")

        if parse_version(existing_version) < parse_version(__version__):
            logger.info(f"Updating nbautoexport post-save hook with version {__version__}...")
            with config_file.open("w") as fp:
                # Open as w replaces existing file. We're replacing entire config.
                fp.write(block_regex.sub(post_save_hook_initialize_block, config))
        else:
            logger.debug("No changes made.")
            return
    else:
        logger.info("Installing post-save hook.")
        with config_file.open("a") as fp:
            # Open as a just appends. We append block at the end of existing file.
            fp.write("\n" + post_save_hook_initialize_block)

    logger.info("nbautoexport post-save hook installed.")
