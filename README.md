Project formatting and pre-commit setup

This project uses `black` and `isort` for automatic formatting, and `ruff` for linting/fixes via `pre-commit` hooks.

Setup (recommended):

1. Create a virtual environment and install dev tools:

```
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install black isort ruff pre-commit
```

2. Install the git hooks:

```
pre-commit install
```

3. Run formatting and lint fixes on all files (one-time):

```
pre-commit run --all-files
```

Manual formatting commands:

```
black .
isort .
ruff --fix .
```

Notes:
- Configurations for `black` and `isort` are in `pyproject.toml`.
- The pre-commit configuration is stored in `.pre-commit-config.yaml`.
