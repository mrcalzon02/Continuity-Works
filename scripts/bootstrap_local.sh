#!/usr/bin/env sh
set -eu
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
echo "Ready. Run: . .venv/bin/activate && structure-capability serve"
