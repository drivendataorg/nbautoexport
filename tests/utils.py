from typing import Optional

import pytest


def caplog_contains(
    caplog: pytest.LogCaptureFixture,
    name: Optional[str] = None,
    level: Optional[int] = None,
    in_msg: Optional[str] = None,
):
    """Utility function to check whether caplog's records contain a particular log."""
    for record_tuple in caplog.record_tuples:
        name_match = name is None or record_tuple[0] == name
        level_match = level is None or record_tuple[1] == level
        in_msg_match = in_msg is None or in_msg in record_tuple[2]
        if name_match and level_match and in_msg_match:
            return True
    return False
