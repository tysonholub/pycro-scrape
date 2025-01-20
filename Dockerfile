#############
# BASE BUILD
#############
FROM python:3.12-slim as base

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN adduser --disabled-password --gecos '' --uid 1000 worker

ENV APP_ROOT=/app
ENV VIRTUAL_ENV=$APP_ROOT/.venv
ENV PIP_DEFAULT_TIMEOUT=100
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1

RUN set -ex \
    && pip install --no-cache-dir --upgrade pip \
    && apt-get update \
    && apt-get upgrade -y \
    && apt-get install curl -y \
    && apt-get clean

###############
# POETRY BUILD
###############
FROM base as poetry

# Install python package build dependencies here. Ex:
# RUN apt-get install libkafka-dev -y

RUN pip install poetry~=1.8

RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY poetry.lock pyproject.toml ./

ARG POETRY_DEPENDENCY_INSTALLS="--without dev"

RUN poetry install --no-interaction ${POETRY_DEPENDENCY_INSTALLS} --no-root

##############
# FINAL BUILD
##############
FROM base as final

# Set the working directory in the container to APP_ROOT
WORKDIR ${APP_ROOT}

# Install python package runtime dependencies here. Ex:
RUN apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libexpat1 \
    libxkbcommon0 \
    libatspi2.0-0

COPY --from=poetry $VIRTUAL_ENV $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONPATH="$APP_ROOT/pysrc:$PATH"

COPY --chmod=665 entrypoint.sh entrypoint.sh
COPY --chmod=665 healthcheck.sh healthcheck.sh
COPY pysrc pysrc

USER worker

RUN playwright install chromium-headless-shell

ENTRYPOINT ["./entrypoint.sh"]
