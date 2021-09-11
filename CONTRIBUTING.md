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

## Documentation Website (for maintainers)

The documentation website is an mkdocs static site hosted on Netlify. The built website assets are typically first staged on the [`gh-pages` branch](https://github.com/drivendataorg/nbautoexport/tree/gh-pages) and then deployed to Netlify automatically using GitHub Actions workflows.

We use the [`mike` tool](https://github.com/jimporter/mike) to manage the documentation versions with the following conventions.
- We keep the docs of the latest patch of a `<major>.<minor>` version, e.g., `v0.2.1` is keyed as `"v0.2"` and titled as `"v0.2.1"`.
- The current stable version is tagged with the alias `"stable"` and has `"(stable)"` as part of the title.
- The head of the `master` branch is keyed as `"~latest"` and titled as `"latest"`

**To deploy the latest docs from the master branch, all you need to do is manually trigger the [`docs-master` GitHub Actions workflow](https://github.com/drivendataorg/nbautoexport/actions/workflows/docs-master.yml).**

**To manually deploy a previously released version, you will need to use `mike`. Follow the instructions in the following section.**

### Manual deploy

Note that `mike` needs to be run in the same direct as `mkdocs.yml`. To avoid changing directories all the time (since we keep it inside the `docs/` subdirectory), you can shadow the `mike` command with the following shell function:

```bash
# Put this in your .bash_profile or wherever you put aliases
mike() {
    if [[ -f mkdocs.yml ]]; then
        command mike "$@"
    else
        (cd docs && command mike "$@")
    fi
}
```

The general steps of deploying docs for a specific version involve:

1. Make sure your local `gh-pages` is up to date with GitHub, i.e., `git fetch origin && git checkout gh-pages && git pull origin gh-pages`
2. Switch to whatever commit you're intending to deploy from.
3. Run `make docs`. (This is necessary because of steps needed before running mkdocs things.)
4. Run whatever `mike` command (see below). If you include the `--push` flag, it will also directly push your changes to GitHub. If you don't, it will only commit to your local `gh-pages` and you'll need to then push that branch to GitHub.
5. Trigger the `docs-master` GitHub actions workflow, which will deploy the `gh-pages` branch to Netlify.

Staging the stable version will be something like this:

```bash
mike deploy v0.3 stable --title="v0.3.1 (stable)" --no-redirect --update-aliases
```

Staging an older version looks something like this:

```bash
mike deploy v0.2 --title="v0.2.1"
```
