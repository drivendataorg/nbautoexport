from contextlib import contextmanager
import logging
import sys

from nbautoexport._version import get_versions

logger = logging.getLogger("nbautoexport")
__version__ = get_versions()["version"]


@contextmanager
def cleared_argv():
    prev_argv = [arg for arg in sys.argv]
    sys.argv = [sys.argv[0]]
    try:
        yield
    finally:
        sys.argv = prev_argv
