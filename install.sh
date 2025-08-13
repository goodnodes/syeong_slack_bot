#!/usr/bin/env bash
set -euo pipefail

# Python venv
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip

# Python deps
pip install -r requirements.txt

echo "✅ Installation complete. Activate venv with:  source .venv/bin/activate"