import sys

import pytest

from nbautoexport.utils import cleared_argv


def test_cleared_argv(monkeypatch):
    """cleared_argv context manager clears sys.argv and restores it on exit
    """
    mocked_argv = ["nbautoexport", "convert", "the_notebook.ipynb", "-f", "script"]
    monkeypatch.setattr(sys, "argv", mocked_argv)

    assert sys.argv == mocked_argv

    with cleared_argv():
        assert sys.argv == mocked_argv[:1]

    assert sys.argv == mocked_argv


def test_cleared_argv_with_error(monkeypatch):
    """cleared_argv context manager restores sys.argv even with exception
    """
    mocked_argv = ["nbautoexport", "convert", "the_notebook.ipynb", "-f", "script"]
    monkeypatch.setattr(sys, "argv", mocked_argv)

    assert sys.argv == mocked_argv

    with pytest.raises(Exception):
        with cleared_argv():
            assert sys.argv == mocked_argv[:1]
            raise Exception

    assert sys.argv == mocked_argv
