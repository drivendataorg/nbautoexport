import logging
from nbautoexport._version import get_versions

logger = logging.getLogger("nbautoexport")
__version__ = get_versions()["version"]
