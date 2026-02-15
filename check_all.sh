#!/usr/bin/env bash

# Check_all.sh - Run all code quality checks

set -e

# Activate virtual environment
source .venv/bin/activate

echo "=== Running ruff format ==="
ruff format .

echo "=== Running ruff check ==="
ruff check .

echo "=== Running mypy --strict ==="
mypy --strict .

echo "=== All checks passed! ==="
