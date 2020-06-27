from contextlib import contextmanager
import logging
import sys

from nbautoexport._version import get_versions

logger = logging.getLogger("nbautoexport")
__version__ = get_versions()["version"]


@contextmanager
def cleared_argv():
    """Context manager that temporarily clears sys.argv. Useful for wrapping nbconvert so
    unexpected arguments from outer program (e.g., nbautoexport) aren't passed to nbconvert.
    """
    prev_argv = [arg for arg in sys.argv]
    sys.argv = [sys.argv[0]]
    try:
        yield
    finally:
        sys.argv = prev_argv
