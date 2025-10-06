#!/usr/bin/env bash
# Simple Linux runner that enforces offline mode and starts the API.
set -euo pipefail

# Move to repo root if invoked from scripts/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# Enforce offline mode for Hugging Face/Transformers and set a local cache dir
export HF_HUB_OFFLINE=${HF_HUB_OFFLINE:-1}
export TRANSFORMERS_OFFLINE=${TRANSFORMERS_OFFLINE:-1}
export HF_HOME="${HF_HOME:-$REPO_ROOT/.hf_cache}"

# Ensure src is on PYTHONPATH
export PYTHONPATH="$REPO_ROOT/src:${PYTHONPATH:-}"

# Prefer venv if present
PYTHON_BIN="python3"
if [[ -x "$REPO_ROOT/.venv/bin/python" ]]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
fi

exec "$PYTHON_BIN" -m uvicorn main:app --host 0.0.0.0 --port 8080
