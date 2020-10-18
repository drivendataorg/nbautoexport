#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages
from pathlib import Path

import versioneer


def load_requirements(path: Path):
    requirements = []
    with path.open("r", encoding="utf-8") as fp:
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

setup(
    author="DrivenData",
    author_email="info@drivendata.org",
    python_requires=">=3.6",
    classifiers=[
        "Framework :: Jupyter",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description=(
        "Automatically export Jupyter notebooks to various file formats (.py, .html, and more) on "
        "save."
    ),
    entry_points={"console_scripts": ["nbautoexport=nbautoexport.nbautoexport:app"]},
    install_requires=requirements,
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords=["nbautoexport", "jupyter", "nbconvert"],
    name="nbautoexport",
    packages=find_packages(include=["nbautoexport", "nbautoexport.*"]),
    project_urls={
        "Bug Tracker": "https://github.com/drivendataorg/nbautoexport/issues",
        "Documentation": "https://nbautoexport.drivendata.org/",
        "Source Code": "https://github.com/drivendataorg/nbautoexport",
    },
    url="https://github.com/drivendataorg/nbautoexport",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    zip_safe=False,
)
