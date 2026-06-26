cd backend_python
# brew install python@3.11
poetry env use /opt/homebrew/bin/python3.11

# Remove all Poetry caches
# poetry cache clear pypi --all


# Delete old lock file
# rm poetry.lock

# Regenerate lockfile
# poetry lock --no-cache --regenerate

PYTHONPATH=. pytest

# Install dependencies
poetry install -vvv
# OR
# poetry add openai python-dotenv

# Activate the peotry envionrment
poetry shell

# Verify it works
poetry run python --version
# poetry add --group dev pytest
poetry run pytest

poetry run uvicorn app.main:app --reload
