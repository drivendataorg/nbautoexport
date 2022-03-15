# History

## 0.4.1 (2022-02-15)

This will be the last version of `nbautoexport` that will have been tested on and officially support Python 3.6.

- Adds dependency on `pywinpty` for Windows environments with a version ceiling on the last version that works with Python 3.6. ([Issue #90](https://github.com/drivendataorg/nbautoexport/issues/90), [PR #92](https://github.com/drivendataorg/nbautoexport/issues/92))

## 0.4.0 (2021-10-29)

- Logging improvements. ([Issue #74](https://github.com/drivendataorg/nbautoexport/issues/74), [PR #80](https://github.com/drivendataorg/nbautoexport/pull/80))
  - Adds additional log statements during post-save hook initialization and execution to facilitate debugging.
  - Changes runtime errors in post-save hook to be caught gracefully instead of interrupting user with an alert dialog in the Jupyter UI.
  - Adds logging integration with active Jupyter applications. Logs will use Jupyter formatting.
  - Changes `--verbose`/`-v` flag to work as a counter. `-v` will set log level to INFO, and `-vv` will set log level to `DEBUG`.

## 0.3.1 (2021-03-10)

- Remove extraneous dependency on `jupyter_contrib_nbextensions`. Add `traitlets`, `notebook`, `jupyter_core`, and `nbformat` as explicit dependencies; previously they were treated as transitive dependencies even though they are actually direct dependencies. ([Issue #68](https://github.com/drivendataorg/nbautoexport/issues/68))

## 0.3.0 (2021-02-18)

- Explicitly set all input and output file encodings to UTF-8, which fixes a bug with HTML exports on Windows with `nbconvert` v6.0. This version removes the version ceiling on <6.
  - This is not expected to cause any backwards compatibility issues. However, in the _very_ unlikely instance that your `jupyter_notebook_config.py` file or your `nbautoexport.json` config file is Windows-1252-encoded _and_ contains non-ASCII characters, you will need to convert them to UTF-8. ([Issue #57](https://github.com/drivendataorg/nbautoexport/issues/57), [PR #61](https://github.com/drivendataorg/nbautoexport/pull/61))

## 0.2.1 (2020-09-18)

- `nbconvert` released version 6, which may break HTML exports on Windows. Pinning to `nbconvert<6` until we can address [Issue #57](https://github.com/drivendataorg/nbautoexport/issues/57).

## 0.2.0 (2020-09-04)

- Add option to specify glob-style patterns to exclude files from deletion when using `clean`. See [documentation](https://nbautoexport.drivendata.org/stable/cleaning/#excluding-files) for more details. ([Issue #46](https://github.com/drivendataorg/nbautoexport/issues/46), [PR #54](https://github.com/drivendataorg/nbautoexport/pull/54))

## 0.1.1 (2020-08-06)

- Fixes missing `requirements.txt` bug when installing from source distribution. ([Issue #50](https://github.com/drivendataorg/nbautoexport/issues/50), [PR #52](https://github.com/drivendataorg/nbautoexport/pull/52))

## 0.1.0 (2020-08-05)

- First release on PyPI.
