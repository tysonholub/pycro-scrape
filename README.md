# pycro-scrape

## Overview

A Web Scraping Python microservice.

## Dev Prerequisites

-   python 3.12
-   [pipx](https://pypa.github.io/pipx/), an optional tool for prerequisite installs
-   [poetry](https://github.com/python-poetry/poetry) (install globally with `pipx install poetry`)
-   [flake8](https://github.com/PyCQA/flake8) (install globally with `pipx install flake8`)
    -   [flake8-bugbear](https://github.com/PyCQA/flake8-bugbear) extension (install with `pipx inject flake8 flake8-bugbear`)
    -   [flake8-naming](https://github.com/PyCQA/pep8-naming) extension (install with `pipx inject flake8 pep8-naming`)
-   [black](https://github.com/psf/black) (install globally with `pipx install black`)
-   [pre-commit](https://github.com/pre-commit/pre-commit) (install globally with `pipx install pre-commit`)
-   [just](https://github.com/casey/just), a Justfile command runner
-   [docker](https://docs.docker.com/engine/install/)
-   [docker-compose](https://docs.docker.com/compose/install/)

### Windows

Justfile support for Windows requires [cygwin](https://www.cygwin.com/). Once installed your `PATH` will need to be updated to resolve `cygpath.exe` (probably `C:\cygwin64\bin`). Justfile will forward any targets with shebangs starting with `/` to cygwin for execution.

## Updating python version:

-   Update python version in `Dev Prerequisites` above
-   Update \[tool.poetry.dependencies\] section of `pyproject.toml`
-   Update pyupgrade hook in `.pre-commit-config.yaml`

## Justfile Targets

-   `install`: installs poetry dependencies and pre-commit git hooks
-   `update_boilerplate`: fetches and applies updates from the boilerplate remote
-   `test`: runs pytest with test coverage report
-   `compose`: runs docker compose with the given arguments
-   `publish`: builds the pycro-scrape docker image and publishes to docker hub. Image will be tagged with current branch and short commit sha, and latest

## Usage

### Docker Image

A prebuilt docker image can be used to run pycro-scrape. It requires a running redis connection. To get started locally:

First create a pycro-scrape docker network

```bash
docker network create pycro-redis
```

Start a local redis container

```bash
docker run --rm -it \
    --hostname=pycro-redis \
    --network=pycro-scrape \
    redis
```

Then start the pycro-scrape container

```bash
docker run --rm -it \
    -e BASE_URL="http://localhost:5001" \
    -e PORT=5001 \
    -e REDIS_ENDPOINT=pycro-redis \
    -e REDIS_PORT=6379 \
    -e PYCRO_SCRAPE_SETTINGS_MODULE="pycro_scrape.config.production:settings" \
    -p 5001:5001 \
    --network=pycro-scrape \
    --hostname=pycro-scrape \
    pycro-scrape
```

With that done you should be able to access openapi docs at http://localhost:5001/api/docs

Start a new pycro-scrape browser session with POST request to http://localhost:5001/api/v1/sessions, with body

```
{
    "url": "https://www.reddit.com",
    "browser": "chrome"
}
```

A successful response will provide JSON with `html_response` key, and a `session` key. Use the `session.id` key to make subsequent fetch API requests against that browser session.

Send a POST request to http://localhost:5001/api/v1/sessions/{session.id}/fetch, with body

```
{
    "method": "post",
    "url": "https://search.api.com/v1/search",
    "headers": {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6InR5NW9uaDBsdWIiLCJpYXQiOjE1MTYyMzkwMjJ9.pnuDIvcSL0t2nIEXRDslglTU3KFsQMQopz98qXqT6KA",
        "Content-Type": "application/json"
    },
    "post_data": {
        "filters": "customer_id: 1462",
    }
}
```

A successful response will include a `fetch_response` key and an updated `session` key. A session expires after 1 hour of no use.

## Boilerplate

To support pulling updates from the [pyplate](git@github.com:tysonholub/pyplate.git) python boilerplate, add the `boilerplate` git remote:

```bash
git remote add boilerplate git@github.com:tysonholub/pyplate.git
```

Then moving forward, run `just update_boilerplate` to pull latest changes from the `boilerplate` remote. **NOTE**: you must keep the boilerplate remote history intact to successfully merge updates from the boilerplate remote.
