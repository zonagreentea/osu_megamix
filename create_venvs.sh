#!/usr/bin/env bash
set -euo pipefail

# Keep the runtime independent and create each optional dependency in its own
# environment under .venvs/dependencies/<name>.
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_ROOT="${PROJECT_DIR}/.venvs"
DEPENDENCY_ROOT="${VENV_ROOT}/dependencies"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "Python executable not found: ${PYTHON_BIN}" >&2
  exit 1
fi

if [[ "$#" -eq 0 ]]; then
  set -- runtime
fi

mkdir -p "${VENV_ROOT}"

for dependency in "$@"; do
  if [[ ! "${dependency}" =~ ^[A-Za-z0-9._-]+$ ]]; then
    echo "Invalid environment name: ${dependency}" >&2
    exit 2
  fi

  if [[ "${dependency}" == "runtime" ]]; then
    target="${VENV_ROOT}/runtime"
  else
    target="${DEPENDENCY_ROOT}/${dependency}"
    mkdir -p "${DEPENDENCY_ROOT}"
  fi
  if [[ -x "${target}/bin/python" ]]; then
    echo "Already exists: ${target}"
  else
    echo "Creating: ${target}"
    "${PYTHON_BIN}" -m venv "${target}"
  fi

  "${target}/bin/python" -m pip --version
done

echo
echo "Environments are under ${VENV_ROOT}"
echo "Activate one with: source ${VENV_ROOT}/<name>/bin/activate"
