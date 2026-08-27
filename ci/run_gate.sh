#!/usr/bin/env bash
# What CI actually runs before data is published to users.
#
# kredme-data is public; the app repo is private, so CI cannot check the app out.
# That is why the second invocation has no category vocabulary — it is not an
# edge case, it is every scheduled run.
set -uo pipefail
cd "$(dirname "$0")/.."

echo "--- gate: local (app checkout available) ---"
python3 gate.py --quiet
echo "local exit: $?"

echo
echo "--- gate: CI (no app checkout) ---"
python3 gate.py --quiet --categories /does/not/exist.json
echo "ci exit: $?"
