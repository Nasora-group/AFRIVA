#!/usr/bin/env bash
set -euo pipefail

: "${TEST_DATABASE_URL:?TEST_DATABASE_URL must point to a disposable PostgreSQL database}"
export SESSION_COOKIE_SECURE=false
pytest -v --cov=app --cov-report=term-missing --cov-fail-under=80
flake8 app tests
black --check app tests
isort --check-only app tests
