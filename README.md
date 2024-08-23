# Sitting Desktop Garden
## Library Overview
```
.
├── client
│   ├── data: Data handling for sitting-desktop-garden. Includes user, posture and face id data.
│   ├── drivers: Control flow software for sitting-desktop-garden. Includes basic control flow and appropriate data structures.
│   └── models: Machine learning models (pose detection and face recognition).
├── docs: Project documentation.
├── notebooks: Demos for module use.
```

## Installation
**Important**: Make sure you have Python 3.10+ installed.

We use [Poetry](https://python-poetry.org/) for dependency management. The installation instructions can be found [here](https://python-poetry.org/docs/).  Once you have Poetry installed, you can install the project dependencies (and the `sitting-desktop-garden` package) with

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

to drop yourself in a nested shell which has the environment activated.

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

## Testing

We use [pytest](https://docs.pytest.org/en/stable/index.html) for testing. Tests are stored in `tests/`, and the tests for each file are prefixed with `test_`.

To run all tests, use

```bash
poetry run pytest
```

To run a specific test, say `test_dummy.py`, use
```bash
poetry run pytest tests/test_dummy.py
```

## Deployment
To deploy a build to the Raspberry Pi use the `deploy.sh` script. This script will create a tarball of file listed in a text file, transfer it to
a specified hostname and untar it there.

To use the script execute it in the project's root directory with,
```bash
./deploy.sh [pathfile] [username]@[hostname]
```
For example, to deploy the files listed in `deploypaths.txt` to `testpi` (using username raspberry) the command would be
```bash
./deploy.sh deploypaths.txt raspberry@testpi
```
The pathname file should contain a path to a file or directory on each line. If a directory is listed `deploy.sh` will copy the entire contents over.
You can use the `#` character at the start of a line to leave comments.

## Code Styling

We use [black](https://black.readthedocs.io/en/stable/) for automated code formatting. To run Black, run this command from the root of the repo:

```bash
poetry run black client
```

To style individual files, you can use

```bash
poetry run black client/models/pose_detection/classification.py
```

## Documentation

We use [Sphinx](https://www.sphinx-doc.org/) for documentation. To view the documentation locally, run the following command:
```bash
make docs-live
```
This spins up a local server which serves the documentation pages, and also hot-reloads and auto-rebuilds whenever code changes are made.

You can build the documentation (without spinning up a server) with `make docs`, and clean the documentation output with `make docs-clean`.

## Downloading ML Models
From top-level directory.
```bash
mkdir client/models/resources &&
curl -o client/models/resources/pose_landmarker_lite.task \
https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task
```
