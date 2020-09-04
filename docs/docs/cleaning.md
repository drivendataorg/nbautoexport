# Cleaning (Experimental)

While using `nbautoexport`, you may sometimes end up with leftover files you no longer want. Some ways this can happen are if you rename notebooks, or if you change your export configuration. The `nbautoexport` CLI has an experimental `clean` command to delete extraneous files.

**WARNING: the `clean` command can delete files irreversibly. Please use with care.**

## Basic usage

Let's say you have a project and keep your notebooks in a `notebooks/` subdirectory. You can clean it with:

```bash
nbautoexport clean notebooks/
```

Note that in order to use `clean`, this directory _must_ be configured with `nbautoexport`, i.e., you have a `notebooks/.nbautoexport` configuration file.

If you have some files that would be cleaned, you would see something that looks like this:

```text
Identified following files to clean up:
  notebooks/html/0.1-ejm-data-exploration.html
  notebooks/html/0.2-ejm-feature-creation.html
  notebooks/script/Untitled.py
Are you sure you want to delete these files? [y/N]: █
```

At this point, you can enter `y` to continue with the deletion or `n` to cancel the deletion. Alternatively, you can run the `clean` command with the `--dry-run` flag which will automatically exit at this point without performing any file deletion.

## How it works

Let's say you have the following files:

```text
notebooks/
├── .nbautoexport
├── 0.1-ejm-data-exploration.ipynb
├── 0.2-ejm-feature-creation.ipynb
├── html
│   ├── 0.1-ejm-data-exploration.html
│   └── 0.2-ejm-feature-creation.html
└── script
    ├── 0.1-ejm-data-exploration.py
    ├── 0.2-ejm-feature-creation.py
    └── Untitled.py
```

and you have the following `.nbautoexport` configuration:

```json
{
  "export_formats": [
    "script"
  ],
  "organize_by": "extension"
}
```

We have some extra files that we want to clean up:

- `html/` has some exports from when we earlier had `html` as an export format.
- `script/Untitled.py` got saved when we had an `Untitled.ipynb` notebook before it was renamed.

`nbautoexport`, based on the configuration file and the notebooks it finds, identifies which files are expected exports or other expected files based on normal `nbautoexport` and Jupyter usage. All other files found are marked for clean up.

```ShellSession
$ nbautoexport clean notebooks/

Identified following files to clean up:
  notebooks/html/0.1-ejm-data-exploration.html
  notebooks/html/0.2-ejm-feature-creation.html
  notebooks/script/Untitled.py
Are you sure you want to delete these files? [y/N]: y
Removing identified files...
Removing empty subdirectories...
  notebooks/html
Cleaning complete.
```

After running `clean`, we end up with the following files:

```text
notebooks/
├── .nbautoexport
├── 0.1-ejm-data-exploration.ipynb
├── 0.2-ejm-feature-creation.ipynb
└── script
    ├── 0.1-ejm-data-exploration.py
    └── 0.2-ejm-feature-creation.py
```

## Excluding files

Sometimes you may have additional files in the notebooks directory of your project that are intentional. You can use [glob-style patterns](https://docs.python.org/3/library/glob.html) indicate files to exclude from deletion.

Building on the previous example, let's say we have the following files:

```text
notebooks/
├── .nbautoexport
├── 0.1-ejm-data-exploration.ipynb
├── 0.2-ejm-feature-creation.ipynb
├── README.md
├── html
│   ├── 0.1-ejm-data-exploration.html
│   └── 0.2-ejm-feature-creation.html
├── images
│   └── diagram.png
└── script
    ├── 0.1-ejm-data-exploration.py
    ├── 0.2-ejm-feature-creation.py
    └── Untitled.py
```

We have additional files that we want to keep:

- `README.md`
- `images/diagram.png`

We can specify [glob-style patterns](https://docs.python.org/3/library/glob.html) to exclude from cleaning with the `--clean-exclude` flag in the `configure` command. Alternatively, we could also directly manually edit the `.nbautoexport` configuration file.

```bash
nbautoexport configure notebooks/ \
    --overwrite \
    --clean-exclude README.md \
    --clean-exclude images/*
```

```json
{
  "export_formats": [
    "script"
  ],
  "organize_by": "extension",
  "clean": {
    "exclude": [
      "README.md",
      "images/*"
    ]
  }
}
```

Then, running the `clean` command:

```ShellSession
$ nbautoexport clean notebooks/

Excluding files from cleaning using the following patterns:
  README.md
  images/*
Identified following files to clean up:
  notebooks/html/0.1-ejm-data-exploration.html
  notebooks/html/0.2-ejm-feature-creation.html
  notebooks/script/Untitled.py
Are you sure you want to delete these files? [y/N]: y
Removing identified files...
Removing empty subdirectories...
  notebooks/html
Cleaning complete.
```

We can see that `README.md` and `images/diagram.png` are left alone.

```text
notebooks/
├── .nbautoexport
├── 0.1-ejm-data-exploration.ipynb
├── 0.2-ejm-feature-creation.ipynb
├── README.md
├── images
│   └── diagram.png
└── script
    ├── 0.1-ejm-data-exploration.py
    └── 0.2-ejm-feature-creation.py
```

### `--exclude` flag

You can also provide patterns to exclude with the `--exclude` (`-e`) flag when calling `clean`.

```bash
nbautoexport clean notebooks/ \
    --exclude README.md \
    --exclude images/*
```

Any patterns specified this way will be used *in addition* to the patterns in the `.nbautoexport` configuration.

## Experimental status

The `clean` command is experimental. The logic for identifying files to delete may be in need of improvement. If you have any feedback from using the `clean` command, please let us know by [creating a GitHub issue](https://github.com/drivendataorg/nbautoexport/issues).
