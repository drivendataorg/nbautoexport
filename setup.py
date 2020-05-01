#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages
from pathlib import Path


def load_requirements(path: Path):
    requirements = []
    with path.open("r") as fp:
        for line in fp.readlines():
            if line.startswith("-r"):
                requirements += load_requirements(line.split(" ")[1].strip())
            else:
                requirement = line.strip()
                if requirement and not requirement.startswith("#"):
                    requirements.append(requirement)
    return requirements


readme = Path("README.md").read_text()
history = Path("HISTORY.md").read_text()

requirements = load_requirements(Path(__file__).parent / "requirements.txt")

setup_requirements = [
    "pytest-runner",
]

test_requirements = [
    "pytest>=3",
]

setup(
    author="DrivenData",
    author_email="info@drivendata.org",
    python_requires=">=3.5",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="Automatically export Jupyter notebooks to various file formats (.py, .html, and more) on save.",
    entry_points={"console_scripts": ["nbautoexport=nbautoexport.cli:main"]},
    install_requires=requirements,
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="nbautoexport",
    name="nbautoexport",
    packages=find_packages(include=["nbautoexport", "nbautoexport.*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/drivendata/nbautoexport",
    version="0.1.0",
    zip_safe=False,
)
