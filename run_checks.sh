#!/usr/bin/env bash
# Runs the same steps as ci/tests.yml (to become .github/workflows/tests.yml), locally.
# Any failing test, an invariant violation in a tournament, or total branch
# coverage below the gate stops the script with a non-zero exit code.
set -euo pipefail
cd "$(dirname "$0")"

echo "== Step 1: tests with branch coverage =="
python3 -m pytest --cov --cov-branch --cov-report=term-missing --cov-fail-under=70

echo "== Step 2: seeded bot-only tournaments =="
python3 simulate.py --seed 1 --tournaments 20

echo "== All checks passed =="
