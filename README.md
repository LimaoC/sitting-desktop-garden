# Sitting Desktop Garden

<center>
</center>

<p align="center" width="100%">
<img src="assets/logo.png" width="200">
</p>

The **Sitting Desktop Garden** (SDG) is a cute and customisable artificial potted plant for the home office desk. It monitors the user's posture, providing gentle reminders and gamified incentives to maintain a healthy sitting position as you work. Reminders are delivered through haptic feedback in a vibrating mousepad, which is non-intrusive to the user's workflow, and demonstrating consistently good posture unlocks more beautiful plant growth.

The SDG is controlled with a Raspberry Pi, which runs all machine learning models and stores all user data locally. No internet connection is required once the Raspberry Pi is set up.

We use a facial recognition system to facilitate user logins and registrations to allow for multiple users to share one SDG. This can be useful in shared workspaces and offices (hot desking). Once the user is logged in, the camera monitors user posture by tracking their body landmarks and determining their neck and hip angles.

Real-time feedback is delivered via a vibrating mousepad, which reminds the user to sit up straight if they are not sitting correctly. Current-session feedback can be viewed via the SDG's monitor to show the user how their posture has progressed over the current session, as well as via the physical growth of the potted plant.

For developers, see [Project Overview](#project-overview). For users setting up a Raspberry Pi for use in the SDG, see [Raspberry Pi Setup](#raspberry-pi-setup).

---

**Table of Contents**

- [Sitting Desktop Garden](#sitting-desktop-garden)
  - [Project Overview](#project-overview)
    - [Directory Structure](#directory-structure)
    - [Dependencies](#dependencies)
  - [Development](#development)
    - [Installation](#installation)
    - [Dependencies](#dependencies-1)
    - [Testing](#testing)
    - [Code Styling](#code-styling)
    - [Documentation](#documentation)
  - [Raspberry Pi Setup](#raspberry-pi-setup)
    - [Environment](#environment)
    - [Deployment](#deployment)

## Project Overview
### Directory Structure
```
.
├── client
│   ├── data: Data handling for sitting-desktop-garden. Includes user, posture and face id data.
│   ├── drivers: Control flow software for sitting-desktop-garden. Includes basic control flow and appropriate data structures.
│   └── models: Machine learning models (pose detection and face recognition).
├── docs: Project documentation.
├── notebooks: Demos for module use.
```

### Dependencies
The main project dependencies are specified in [pyproject.toml](./pyproject.toml). Notably:
- [mediapipe](https://ai.google.dev/edge/mediapipe/solutions/guide) provides the body landmark detection model.
- [piicodev](https://pypi.org/project/piicodev/) provides modules for interfacing with Raspberry Pi peripherals.
- [face-recognition](https://pypi.org/project/face-recognition/) provides the face rceognition model.

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


## Raspberry Pi Setup
### Environment
Flash up your Raspberry Pi Model 3 B with a fresh install of Raspberry Pi OS (64-bit). Turn on the Raspberry Pi and record its IP address `[Target IP]`.
On your personal machine, clone into this Git repository. From the base directory, run the following command. 
```bash
cd bootstrap && ./bootstrap.sh [Target IP] [Username]
```
This will install python3.10 to the Pi and the dependencies for the project.
### Deployment
To deploy a build to the Raspberry Pi, turn it on and run the `deploy.sh` script from your personal machine. This script will create a tarball of file listed in a text file, transfer it to
a specified hostname and untar it there.

To use the script execute it in the project's root directory with,
```bash
./deploy.sh [pathfile] [hostname] [username]
```
For example, to deploy the files listed in `deploypaths.txt` to the target IP `testpi` (using username raspberry) the command would be
```bash
./deploy.sh deploypaths.txt testpi raspberry
```
The pathname file should contain a path to a file or directory on each line. If a directory is listed `deploy.sh` will copy the entire contents over.
You can use the `#` character at the start of a line to leave comments.
