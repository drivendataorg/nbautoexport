# nbautoexport

[![Build Status](https://dev.azure.com/drivendataco/nbautoexport/_apis/build/status/drivendataorg.nbautoexport?branchName=master)](https://dev.azure.com/drivendataco/nbautoexport/_build/latest?definitionId=1&branchName=master)

> Making it easier to code review Jupyter notebooks, one script at a time.

nbautoexport automatically exports Jupyter notebooks to various file formats (.py, .html, and more) on save.

## Installation

```bash
pip install nbautoexport
```

## Simple usage

Before installing, you must [initialize a `jupyter_notebook_config.py`](https://jupyter-notebook.readthedocs.io/en/stable/config.html) file with the following command:

```bash
jupyter notebook --generate-config
```

To set up, run the following command from the root folder of your project:

```bash
nbautoexport [--directory/-d] [--export-format/-f] [--export-format/-f] [--organize-by/-b] [--overwrite/-o] [--verbose/-v]
```

Under the hood, this command performs two steps: 1) edits `jupyter_notebook_config.py` to add a post-save hook, and 2) creates a sentinel file `./notebooks/.nbautoexport`, a JSON file that contains the project-specific settings. Here is the default `.nbautoexport`:

```json
{
  "export_formats": ["script"],
  "organize_by": "notebook",
}
```

This will track Jupyter notebooks in your `notebooks` folder and upon save, generate a script which will live in a folder with the same name as the notebook.

```
notebooks
├── 0.1-ejm-data-exploration
│   └── 0.1-ejm-data-exploration.py
├── 0.2-ejm-feature-creation
│   └── 0.2-ejm-feature-creation.py
├──0.1-ejm-data-exploration.ipynb
└──0.2-ejm-feature-creation.ipynb
```

This default organization is handy for selecting the pair in git with just `*` at the end of the part that the tab completion matched. However, this can result in a large number of subfolders. You can put scripts in a single folder instead with

```bash
nbautoexport --organize_by extension
```

```
notebooks
├──0.1-ejm-data-exploration.ipynb
├──0.2-ejm-feature-creation.ipynb
└── script
    └── 0.1-ejm-data-exploration.py
    └── 0.2-ejm-feature-creation.py
```

If you do not like the settings you selected, you can always change them by either 1) re-running the `nbautoexport` command with new arguments and the `--overwrite` flag, or 2) manually editing the `.nbautoexport` file.

## Command line options

```
Usage: nbautoexport [OPTIONS]

  Exports Jupyter notebooks to various file formats (.py, .html, and more)
  upon save.

Options:
  -f, --export_format TEXT   File format(s) to save for each notebook. Options
                             are 'script', 'html', 'markdown', and 'rst'.
                             Multiple formats should be provided using
                             multiple flags, e.g., '-f script -f html -f
                             markdown'. Default is 'script'.

  -b, --organize_by TEXT     Whether to save exported file(s) in a folder per
                             notebook or a folder per extension. Options are
                             'notebook' or 'extension'. Default is 'notebook'.

  -d, --directory TEXT       Directory containing jupyter notebooks to track.
                             Default is 'notebooks'.

  -o, --overwrite            Overwrite existing configuration, if one is
                             detected.

  -v, --verbose              Verbose mode.
  --help                     Show this message and exit.
```

## Example

```bash
nbautoexport -f script -f html --organize_by extension --directory sprint_one_notebooks
```

Upon save, this creates `.py` and `.html` versions of the Jupyter notebooks in `sprint_one_notebooks` folder and results in the following organization:

```
sprint_one_notebooks
├──0.1-ejm-data-exploration.ipynb
├──0.2-ejm-feature-creation.ipynb
├── script
│   └── 0.1-ejm-data-exploration.py
│   └── 0.1-ejm-features-creation.py
└── html
    └── 0.1-ejm-data-exploration.html
    └── 0.1-ejm-features-creation.html
```


# Credits

- [Cookiecutter](https://github.com/audreyr/cookiecutter)
- [`audreyr/cookiecutter-pypackage`](https://github.com/audreyr/cookiecutter-pypackage)
