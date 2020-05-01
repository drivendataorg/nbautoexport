"""Tests for `nbautoexport` package."""

import pytest

from click.testing import CliRunner

from nbautoexport import nbautoexport


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    help_result = runner.invoke(nbautoexport.install, ["--help"])
    assert help_result.exit_code == 0
    assert "Exports Jupyter notebooks to various file formats" in help_result.output
