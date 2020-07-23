# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given. You can contribute in many ways:

## Types of Contributions

### Report Bugs

Report bugs at https://github.com/drivendata/nbautoexport/issues.

If you are reporting a bug, please include:

- Your operating system name and version.
- Any details about your local setup that might be helpful in troubleshooting.
- Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

### Write Documentation

nbautoexport could always use more documentation, whether as part of the official nbautoexport docs, in docstrings, or even on the web in blog posts, articles, and such.

### Submit Feedback

The best way to send feedback is to file an issue at https://github.com/drivendata/nbautoexport/issues.

If you are proposing a feature:

- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier to implement.
- Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

## Get Started!

Ready to contribute? Here's how to set up `nbautoexport` for local development.

1. Fork the `nbautoexport` repo on GitHub.
2. Clone your fork locally:

```bash
git clone https://github.com/YOUR_ACCOUNT_NAME/nbautoexport.git
```

3. Install your local copy into a virtual environment. Here's how to set one up with Python's built in `venv` module.

```bash
cd nbautoexport/
python -m venv ./.venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

4. Create a branch for local development:

```bash
git checkout -b name-of-your-bugfix-or-feature
```

Now you can make your changes locally.

5. When you're done making changes, check that your changes pass linting and the tests:

```bash
make lint
make test
```

6. Commit your changes and push your branch to GitHub:

```bash
git add .
git commit -m "Your detailed description of your changes."
git push origin name-of-your-bugfix-or-feature
```

7. Submit a pull request through the GitHub website.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, please ensure you have created appropriate documentation.
3. The pull request should work for Python 3.6, 3.7 and 3.8 and different operating systems. Check [GitHub Actions](https://github.com/drivendataorg/nbautoexport/actions?query=event%3Apull_request+workflow%3Atests) and make sure that the tests pass for all supported Python versions and environments.

## Tips

To run a subset of tests, for example:

```bash
pytest tests/test_export.py
```

## Release Instructions (for maintainers)

To release a new version of `nbautoexport`, create a new release using the [GitHub releases UI](https://github.com/drivendataorg/nbautoexport/releases/new). The tag version must have a prefix `v` and should have a semantic versioning format, e.g., `v0.1.0`.

On publishing of the release, the [`release`](https://github.com/drivendataorg/nbautoexport/blob/master/.github/workflows/release.yml) GitHub action workflow will be triggered. This workflow builds the package and publishes it to PyPI. You will be able to see the workflow status in the [Actions tab](https://github.com/drivendataorg/nbautoexport/actions?query=workflow%3Arelease).

The built package for `nbautoexport` will automatically match the created git tag via [versioneer](https://github.com/warner/python-versioneer).
