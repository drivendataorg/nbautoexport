# History

## 0.3.0 (2021-02-18)

- Explicitly set all input and output file encodings to UTF-8, which fixes a bug with HTML exports on Windows with `nbconvert` v6.0. This version removes the version ceiling on <6. 
  - This is not expected to cause any backwards compatibility issues. However, in the _very_ unlikely instance that your `jupyter_notebook_config.py` file or your `nbautoexport.json` config file is Windows-1252-encoded _and_ contains non-ASCII characters, you will need to convert them to UTF-8. ([#57](https://github.com/drivendataorg/nbautoexport/issues/57), [#61](https://github.com/drivendataorg/nbautoexport/pull/61))

## 0.2.1 (2020-09-18)

 - `nbconvert` released version 6, which may break HTML exports on Windows. Pinning to `nbconvert<6` until we can address [#57](https://github.com/drivendataorg/nbautoexport/issues/57).

## 0.2.0 (2020-09-04)

- Add option to specify glob-style patterns to exclude files from deletion when using `clean`. See [documentation](https://nbautoexport.drivendata.org/cleaning/#excluding-files) for more details. ([#46](https://github.com/drivendataorg/nbautoexport/issues/46), [#54](https://github.com/drivendataorg/nbautoexport/pull/54))

## 0.1.1 (2020-08-06)

- Fixes missing `requirements.txt` bug when installing from source distribution. ([#50](https://github.com/drivendataorg/nbautoexport/issues/50), [#52](https://github.com/drivendataorg/nbautoexport/pull/52))

## 0.1.0 (2020-08-05)

- First release on PyPI.
