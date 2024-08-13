# Sitting Desktop Garden

## Installation
We use [Poetry](https://python-poetry.org/) for dependency management. Once you have Poetry installed, you can install the dependencies (and the `sitting-desktop-garden` package) required with

```bash
poetry install
```

`poetry install` will use the exact versions found in `poetry.lock` so that the environment can be replicated exactly. This automatically creates a virtual environment for you (see `poetry env info`). To run commands within this virtual environment, you can either use

```bash
poetry run <command>
```

to run a single command within the environment (e.g. `poetry run python script.py`), or

```bash
poetry shell
```

to drop yourself in a nested shell which has the environment active.

You can check that the `sitting-desktop-garden` package has been installed correctly with this command:

```bash
poetry run pip list | grep sitting-desktop-garden
```

## Development

To add a new dependency to the package, use

```bash
poetry add <package-name>
```

To add a *dev* dependency to the package, use

```bash
poetry add <package-name> --group dev
```

Removing packages is done in the same way but with `remove` instead of `add`.

**Important**: If you make any changes to the dependencies, make sure to commit `poetry.lock`. This will ensure that others can reproduce your exact environment when they next run `poetry install`.

Note that both regular and dev dependencies will be installed with `poetry install`. To exclude the dev dependencies (e.g. when installing on the Raspberry Pi), use

```bash
poetry install --without dev
```

To see a list of installed packages, use `poetry show`, or `poetry show --tree` for a graphical view. You can also see a list of non-dev dependencies with `poetry show --only main` or `poetry show --without dev`.

## Downloading ML Models
From top-level directory.
```bash
mkdir client/models/resources &&
curl -o client/models/resources/pose_landmarker_lite.task \
https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task
```
