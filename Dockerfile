# Dockerfile
# Uses multi-stage builds requiring Docker 17.05 or higher
# See https://docs.docker.com/develop/develop-images/multistage-build/

# Creating a python base with shared environment variables
ARG PYTHON_VARIANT=3.11

FROM python:${PYTHON_VARIANT} as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PROJECT_PATH="/app" \
    VENV_PATH="/app/.venv" 


ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
ENV PYTHONPATH="$POETRY_HOME:$VENV_PATH:$PYTHONPATH"

# builder-base is used to build dependencies
FROM python-base as builder-base
RUN python -m pip install --upgrade pip
RUN pip install --upgrade setuptools wheel

# Install Poetry - respects $POETRY_VERSION & $POETRY_HOME
ENV POETRY_VERSION=1.5.1
RUN pip install "poetry==$POETRY_VERSION" -t $POETRY_HOME

# We copy our Python requirements here to cache them
# and install only runtime deps using poetry
WORKDIR $PROJECT_PATH
COPY ./poetry.lock ./pyproject.toml ./
RUN poetry install --no-root --only main
RUN pip install torch

# 'production' stage uses the clean 'python-base' stage and copyies
# in only our runtime deps that were installed in the 'builder-base'
FROM python-base as production

WORKDIR $PROJECT_PATH

COPY --from=builder-base $VENV_PATH $VENV_PATH
COPY --from=builder-base $POETRY_HOME $POETRY_HOME

COPY . .

# Expose port 8080 for uvicorn
EXPOSE 8080

CMD ["uvicorn", "service.app:app", "--host", "0.0.0.0", "--port", "8080"]
