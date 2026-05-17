#!/usr/bin/env bash
set -euo pipefail

# shellcheck source=/dev/null
source .venv/bin/activate

git diff --check
ruff check .
ruff format --check .
mypy app/
pytest -q
scripts/check_public_clean.sh
python scripts/validate_wallet_flow.py

if command -v shellcheck >/dev/null 2>&1; then
  shellcheck scripts/*.sh
else
  echo "SKIPPED shellcheck unavailable"
fi

if command -v bandit >/dev/null 2>&1; then
  bandit -r app
else
  echo "SKIPPED bandit unavailable"
fi

if command -v pip-audit >/dev/null 2>&1; then
  pip-audit
else
  echo "SKIPPED pip-audit unavailable"
fi

if command -v osv-scanner >/dev/null 2>&1; then
  osv-scanner scan source .
else
  echo "SKIPPED osv-scanner unavailable"
fi

if command -v gitleaks >/dev/null 2>&1; then
  gitleaks detect --source . --no-git
else
  echo "SKIPPED gitleaks unavailable"
fi
