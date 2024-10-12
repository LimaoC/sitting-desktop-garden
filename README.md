# Sitting Desktop Garden

**Table of Contents**

- [Sitting Desktop Garden](#sitting-desktop-garden)
  - [Library Overview](#library-overview)
  - [Development](#development)
    - [Installation](#installation)
    - [Dependencies](#dependencies)
    - [Testing](#testing)
    - [Code Styling](#code-styling)
    - [Documentation](#documentation)
  - [Deployment](#deployment)
    - [Single command all-in-one](#single-command-all-in-one)
    - [Pi Environment Set-up](#pi-environment-set-up)
    - [Deploy codebase](#deploy-codebase)
    - [Run Program](#run-program)

**Go straight to [the single command instructions](#single-command-all-in-one) if you want to run the project on your own Pi!**

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

## Development

### Installation
**Important**: Make sure you have Python 3.10 installed.

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

### Dependencies

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

### Testing

We use [pytest](https://docs.pytest.org/en/stable/index.html) for testing. Tests are stored in `tests/`, and the tests for each file are prefixed with `test_`.

To run all tests, use

```bash
poetry run pytest
```

To run a specific test, say `test_dummy.py`, use
```bash
poetry run pytest tests/test_dummy.py
```

### Code Styling

We use [black](https://black.readthedocs.io/en/stable/) for automated code formatting. To run Black, run this command from the root of the repo:

```bash
poetry run black client
```

To style individual files, you can use

```bash
poetry run black client/models/pose_detection/classification.py
```

### Documentation

We use [Sphinx](https://www.sphinx-doc.org/) for documentation. To view the documentation locally, run the following command:
```bash
make docs-live
```
This spins up a local server which serves the documentation pages, and also hot-reloads and auto-rebuilds whenever code changes are made.

You can build the documentation (without spinning up a server) with `make docs`, and clean the documentation output with `make docs-clean`.


## Deployment
### Single command all-in-one
To set up the Pi's environment, deploy the code base, and start the program follow the following steps.
1. Flash an SD card with a fresh installation of the 64bit Raspberry Pi OS using the [official imager](https://www.raspberrypi.com/software/). When imaging the SD card you must turn on the SSH connections in the edit OS settings menu.
2. Plug the SD card into the Pi and turn it on. Wait for the green light to stop flashing before going to step 3.
3. Clone this git directory to your computer.
4. From the base directory of the project run,
`
./run.sh [Pi Hostname/IP] [Pi Username]
`. If you do not have sshpass installed this may prompt for the Pi's password many times.
5. The above command will take a while.
### Pi Environment Set-up
You can set up the Pi's environment by following steps 1,2, and 3 of the above instructions. and then running.
```bash
scripts/bootstrap.sh [Pi Hostname/IP] [Pi Username]
```
### Deploy codebase
You can deploy the codebase by running 
```bash
cd scripts
./deploy.sh ../deploypaths.txt [Pi Hostname/IP] [Pi Username]
```

### Run Program
You can start up the program by running
```bash
cd scripts
./ssh [Pi Username]@[Pi Hostname/IP] 'bash -s' < run_garden.sh
```