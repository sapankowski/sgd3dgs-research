#!/usr/bin/env bash
set -eu

repository_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
project_environment="${UV_PROJECT_ENVIRONMENT:-$repository_root/venv}"
export UV_PROJECT_ENVIRONMENT="$project_environment"

cd "$repository_root"
exec uv "$@"
