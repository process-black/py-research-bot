#!/usr/bin/env bash
set -euo pipefail

# Always run from the script's directory
cd "$(dirname "$0")"

VENV_DIR=".venv"

# Pick a Python
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "ERROR: Python not found on PATH." >&2
  exit 1
fi

# Create venv if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment in $VENV_DIR ..."
  "$PY" -m venv "$VENV_DIR"
fi

# Activate venv if not already active
if [ "${VIRTUAL_ENV:-}" != "$(cd "$VENV_DIR" && pwd)" ]; then
  # shellcheck source=/dev/null
  source "$VENV_DIR/bin/activate"
fi

# Find site-packages inside the venv (first match)
shopt -s nullglob
sp_candidates=("$VENV_DIR"/lib/python*/site-packages)
shopt -u nullglob
SITE_PACKAGES=""
if [ ${#sp_candidates[@]} -gt 0 ]; then
  SITE_PACKAGES="${sp_candidates[0]}"
fi

# Install dependencies iff requirements.txt is newer than site-packages
if [ -f "requirements.txt" ]; then
  if [ -z "$SITE_PACKAGES" ] || [ "requirements.txt" -nt "$SITE_PACKAGES" ]; then
    echo "Installing/updating dependencies from requirements.txt ..."
    pip install -r requirements.txt
    # Refresh SITE_PACKAGES in case it was just created
    if [ -z "$SITE_PACKAGES" ]; then
      shopt -s nullglob
      sp_candidates=("$VENV_DIR"/lib/python*/site-packages)
      shopt -u nullglob
      if [ ${#sp_candidates[@]} -gt 0 ]; then
        SITE_PACKAGES="${sp_candidates[0]}"
      fi
    fi
  else
    echo "Dependencies are up-to-date (requirements.txt not newer than site-packages)."
  fi
fi

# Ensure watchfiles is installed in the venv
python - <<'PYCHECK' || { echo "Installing watchfiles ..."; pip install watchfiles; }
try:
    import watchfiles  # noqa: F401
except Exception as e:
    raise SystemExit(1)
PYCHECK

echo "Starting app with watchfiles autoreload ..."
exec watchfiles "python app.py" .
