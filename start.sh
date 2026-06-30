#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

HASH_FILE=".venv/.req_hash"
REQ_FILE="requirements.txt"

current_hash() {
  python3 -c "import hashlib; print(hashlib.sha256(open('$REQ_FILE','rb').read()).hexdigest())"
}

needs_install() {
  [ ! -d ".venv" ] && return 0
  [ ! -f "$HASH_FILE" ] && return 0
  [ "$(current_hash)" != "$(cat "$HASH_FILE")" ] && return 0
  return 1
}

if needs_install; then
  if [ ! -d ".venv" ]; then
    echo "First run: creating virtual environment..."
    python3 -m venv .venv
  else
    echo "requirements.txt changed — reinstalling dependencies..."
  fi
  .venv/bin/python -m pip install -q --upgrade pip
  .venv/bin/python -m pip install -q -r "$REQ_FILE"
  current_hash > "$HASH_FILE"
  echo "Dependencies ready."
fi

exec .venv/bin/python app.py
