#!/usr/bin/env bash
set -euo pipefail

# Run independent runtime Python with selected dependency venvs exposed.
# Usage: ./run_with_deps.sh dependency_a dependency_b -- app.py [args...]
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_PYTHON="${PROJECT_DIR}/.venvs/runtime/bin/python"
DEPENDENCY_ROOT="${PROJECT_DIR}/.venvs/dependencies"

if [[ ! -x "${RUNTIME_PYTHON}" ]]; then
  echo "Runtime venv is missing. Run ./create_venvs.sh first." >&2
  exit 1
fi

pythonpath=""
while [[ "$#" -gt 0 && "$1" != "--" ]]; do
  dependency="$1"
  shift
  if [[ ! "${dependency}" =~ ^[A-Za-z0-9._-]+$ ]]; then
    echo "Invalid dependency environment name: ${dependency}" >&2
    exit 2
  fi
  dependency_python=$(find "${DEPENDENCY_ROOT}/${dependency}/lib" -type d -path '*/site-packages' -print -quit 2>/dev/null || true)
  if [[ -z "${dependency_python}" ]]; then
    echo "Dependency venv not found: ${dependency}" >&2
    echo "Create it with: ./create_venvs.sh ${dependency}" >&2
    exit 3
  fi
  pythonpath="${pythonpath:+${pythonpath}:}${dependency_python}"
done

if [[ "$#" -eq 0 || "$1" != "--" ]]; then
  echo "Usage: $0 dependency... -- python-script-or-module [args...]" >&2
  exit 2
fi
shift
[[ "$#" -gt 0 ]] || { echo "Missing Python script or module." >&2; exit 2; }

if [[ -n "${pythonpath}" ]]; then
  PYTHONPATH="${pythonpath}${PYTHONPATH:+:${PYTHONPATH}}" exec "${RUNTIME_PYTHON}" "$@"
else
  exec "${RUNTIME_PYTHON}" "$@"
fi
