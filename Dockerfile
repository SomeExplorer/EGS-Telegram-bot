FROM python:3.12-slim

ARG INSTALL_DEV=false
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=2.2.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

WORKDIR /app
COPY pyproject.toml poetry.lock ./

RUN if [ "$INSTALL_DEV" = "true" ] ; then  \
    poetry install --no-root ;  \
    else poetry install --no-root --only main ;  \
    fi

COPY . .
