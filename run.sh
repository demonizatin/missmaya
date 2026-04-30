#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  python3 -m venv .venv
  ./.venv/bin/pip install -q --upgrade pip
  ./.venv/bin/pip install -q -r requirements.txt
fi

# Optional: load .env (used only if you want to override with an API key)
if [ -z "${ANTHROPIC_API_KEY:-}" ] && [ -f .env ]; then
  set -a; . ./.env; set +a
fi

if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
  if ! command -v claude >/dev/null 2>&1; then
    echo "ERROR: 'claude' CLI not found in PATH and ANTHROPIC_API_KEY not set."
    echo "Either install Claude Code (https://claude.com/code) or set ANTHROPIC_API_KEY."
    exit 1
  fi
fi

exec ./.venv/bin/python app.py
