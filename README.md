# auth [![Build Status](https://travis-ci.org/circle-app/auth.svg?branch=master)](https://travis-ci.org/circle-app/auth) [![](https://images.microbadger.com/badges/image/pando85/auth.svg)](https://microbadger.com/images/pando85/auth) [![](https://images.microbadger.com/badges/version/pando85/auth.svg)](https://microbadger.com/images/pando85/auth) [![License](https://img.shields.io/github/license/circle-app/auth.svg)](https://github.com/circle-app/auth/blob/master/LICENSE)

Auth microservice for circle.

## Lint

Lint: `make lint`

## Dev

Run app: `make run`

## Tests

Run tests: `make test`

### Production

**Warning**: aiohttp is [slower with gnunicorn](https://docs.aiohttp.org/en/stable/deployment.html#start-gunicorn). Basic `python -m my_app` execution is prefered.
