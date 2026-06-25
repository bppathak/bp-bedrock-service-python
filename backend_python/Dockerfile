#FROM python:3.11-slim
FROM registry.access.redhat.com/ubi9/python-311

WORKDIR /app

# Copy dependency files first (better caching)
COPY pyproject.toml poetry.lock ./
COPY requirements.txt ./

ENV HTTP_PROXY=http://10.210.195.1:8080
ENV HTTPS_PROXY=http://10.210.195.1:8080

# RUN dnf intall -y python3 python3-pip
# RUN python3 -m pip install --upgrade pip
# RUN pip3 install poetry
RUN python -m pip install --upgrade pip
RUN pip install poetry==2.2.1
RUN pip install -r requirements.txt

RUN export PATH="$HOME/.local/bin:$PATH"

# Install dependencies
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi --no-root

# Copy app code
COPY . .

# Start command (change for Flask/FastAPI/etc.)
# RUN cd backend_python && poetry run uvicorn app.main:app --host
# CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]