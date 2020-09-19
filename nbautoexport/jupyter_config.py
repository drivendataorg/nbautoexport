from inspect import getsourcelines
from pathlib import Path
from packaging.version import parse as parse_version
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


def install_post_save_hook(config_path: Optional[Path] = None):
    """Splices the post save hook into the global Jupyter configuration file"""
    if config_path is None:
        config_dir = jupyter_config_dir()
        config_path = Path(config_dir) / "jupyter_notebook_config.py"

    config_path = config_path.expanduser().resolve()

    if not config_path.exists():
        logger.debug(f"No existing Jupyter configuration detected at {config_path}. Creating...")
        config_path.parent.mkdir(exist_ok=True, parents=True)
        with config_path.open("w", encoding="utf-8") as fp:
            fp.write(post_save_hook_initialize_block)
        logger.info("nbautoexport post-save hook installed.")
        return

    # If config exists, check for existing nbautoexport initialize block and install as appropriate
    logger.debug(f"Detected existing Jupyter configuration at {config_path}")

    with config_path.open("r", encoding="utf-8") as fp:
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
            with config_path.open("w", encoding="utf-8") as fp:
                # Open as w replaces existing file. We're replacing entire config.
                fp.write(block_regex.sub(post_save_hook_initialize_block, config))
        else:
            logger.debug("No changes made.")
            return
    else:
        logger.info("Installing post-save hook.")
        with config_path.open("a") as fp:
            # Open as a just appends. We append block at the end of existing file.
            fp.write("\n" + post_save_hook_initialize_block)

    logger.info("nbautoexport post-save hook installed.")
