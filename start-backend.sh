cd backend_python
# brew install python@3.11
poetry env use /usr/bin/python3.11

# Remove all Poetry caches
poetry cache clear pypi --all


# Delete old lock file
rm poetry.lock

# Regenerate lockfile
poetry lock --no-cache --regenerate

PYTHONPATH=. pytest


# Verify it works
poetry run python --version
poetry run pytest

poetry run uvicorn app.main:app --reload