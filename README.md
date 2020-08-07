# nbautoexport

[![Docs Status](https://img.shields.io/badge/docs-latest-blueviolet)](https://nbautoexport.drivendata.org/)
[![PyPI](https://img.shields.io/pypi/v/nbautoexport.svg)](https://pypi.org/project/nbautoexport/)
[![conda-forge](https://img.shields.io/conda/vn/conda-forge/nbautoexport.svg)](https://anaconda.org/conda-forge/nbautoexport)
[![tests](https://github.com/drivendataorg/nbautoexport/workflows/tests/badge.svg?branch=master)](https://github.com/drivendataorg/nbautoexport/actions?query=workflow%3Atests+branch%3Amaster)
[![codecov](https://codecov.io/gh/drivendataorg/nbautoexport/branch/master/graph/badge.svg)](https://codecov.io/gh/drivendataorg/nbautoexport)

> Making it easier to code review Jupyter notebooks, one script at a time.

`nbautoexport` automatically exports Jupyter notebooks to various file formats (.py, .html, and more) upon save while using Jupyter. One great use case is to automatically have script versions of your notebooks to facilitate code review commenting.

## Installation

First, you will need to install `nbautoexport`. This should be installed in the same environment you are running Jupyter Notebook or Jupyter Lab from. `nbautoexport` is available either from [PyPI](https://pypi.org/project/nbautoexport/) via `pip` or from [conda-forge](https://github.com/conda-forge/nbautoexport-feedstock) via `conda`.

```bash
pip install nbautoexport
```

```bash
conda install nbautoexport --channel conda-forge
```

Then, to register `nbautoexport` to run automatically while using Jupyter Notebook or Jupyter Lab, run:

```bash
nbautoexport install
```

If you already have a Jupyter server running, you will need to restart it for this to take effect.

## Simple usage

Let's say you have a project and keep your notebooks in a `notebooks/` subdirectory.

To configure that directory for automatic exporting, run the following command:

```bash
nbautoexport configure notebooks
```

This will create a configuration file `notebooks/.nbautoexport`.

If you've set up `nbautoexport` to work with Jupyter (using the `install` command as detailed in the previous section), then any time you save a notebook in Jupyter, a hook will run that checks whether there is a `.nbautoexport` configuration file in the same directory as the notebook. If so, it will use the settings specified in that file to export your notebook. By default, it will generate a script version of your notebook named after the notebook (with the `.py` extension) and saved in the directory `notebooks/script`.

If everything is working, your notebooks directory should end up with files like the below example:

```text
notebooks
├──0.1-ejm-data-exploration.ipynb
├──0.2-ejm-feature-creation.ipynb
└── script
    └── 0.1-ejm-data-exploration.py
    └── 0.2-ejm-feature-creation.py
```

## Configuring export options

The default `.nbautoexport` configuration file looks like this:

```json
{
  "export_formats": [
    "script"
  ],
  "organize_by": "extension"
}
```

Upon save, this will lead to notebooks being exported to scripts which saved to the `notebooks/script` directory.

```text
notebooks
├──0.1-ejm-data-exploration.ipynb
├──0.2-ejm-feature-creation.ipynb
└── script
    └── 0.1-ejm-data-exploration.py
    └── 0.2-ejm-feature-creation.py
```

An alternative way to organize exported files is to create a directory for each notebook. This can be handy for matching both the notebook and subdirectory when tab-completing and then globbing with `*` after the part that completed.

```bash
nbautoexport configure notebooks --organize-by notebook
```

```text
notebooks
├── 0.1-ejm-data-exploration
│   └── 0.1-ejm-data-exploration.py
├── 0.2-ejm-feature-creation
│   └── 0.2-ejm-feature-creation.py
├──0.1-ejm-data-exploration.ipynb
└──0.2-ejm-feature-creation.ipynb
```

If you do not like the settings you selected, you can always change them by either 1) re-running the `nbautoexport` command with new arguments and the `--overwrite` flag, or 2) manually editing the `.nbautoexport` file.

You can also specify as many export formats as you'd like. We support most of the export formats available from [`nbconvert`](https://nbconvert.readthedocs.io/en/latest/), such as `html`, `md`, and `pdf`. To specify formats, use the `--export-format` for each format you want to include.


### Advanced example

```bash
nbautoexport configure sprint_one_notebooks -f script -f html --organize-by extension
```

Upon save, this creates `.py` and `.html` versions of the Jupyter notebooks in `sprint_one_notebooks` folder and results in the following organization:

```text
notebooks
├──0.1-ejm-data-exploration.ipynb
├──0.2-ejm-feature-creation.ipynb
├── script
│   └── 0.1-ejm-data-exploration.py
│   └── 0.1-ejm-features-creation.py
└── html
    └── 0.1-ejm-data-exploration.html
    └── 0.1-ejm-features-creation.html
```

## More functionality

The `nbautoexport` CLI has two additional commands:

- `export` is for ad hoc exporting of a notebook or directory of notebooks
- `clean` (EXPERIMENTAL) will delete files in a directory that are not generated by the current `.nbautoexport` configuration

Use the `--help` flag to see the documentation.

## Command-line help

```bash
nbautoexport --help
```

```text
Usage: nbautoexport [OPTIONS] COMMAND [ARGS]...

  Automatically export Jupyter notebooks to various file formats (.py,
  .html, and more) upon save. One great use case is to automatically have
  script versions of your notebooks to facilitate code review commenting.

  To set up, first use the 'install' command to register nbautoexport with
  Jupyter. If you already have a Jupyter server running, you will need to
  restart it.

  Next, you will need to use the 'configure' command to create a
  .nbautoexport configuration file in the same directory as the notebooks
  you want to have export automatically.

  Once nbautoexport is installed with the first step, exporting will run
  automatically when saving a notebook in Jupyter for any notebook where
  there is a .nbautoexport configuration file in the same directory.

Options:
  --version             Show nbautoexport version.
  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell, to copy it or
                        customize the installation.

  --help                Show this message and exit.

Commands:
  clean      (EXPERIMENTAL) Remove subfolders/files not matching...
  configure  Create a .nbautoexport configuration file in a directory.
  export     Manually export notebook or directory of notebooks.
  install    Register nbautoexport post-save hook with Jupyter.
```

---

This repository was initially created using [Cookiecutter](https://github.com/audreyr/cookiecutter) with [`audreyr/cookiecutter-pypackage`](https://github.com/audreyr/cookiecutter-pypackage).
