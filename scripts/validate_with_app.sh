#!/usr/bin/env bash
set -eu

if [ "$#" -ne 1 ]; then
  printf 'Usage: %s path/to/scene.json\n' "$0" >&2
  exit 2
fi

manifest_input="$1"
if [ ! -f "$manifest_input" ]; then
  printf 'Manifest does not exist: %s\n' "$manifest_input" >&2
  exit 1
fi

manifest_directory=$(CDPATH= cd -- "$(dirname -- "$manifest_input")" && pwd)
manifest_path="$manifest_directory/$(basename -- "$manifest_input")"
repository_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
application_root="${SGD3DGS_APP_DIR:-$repository_root/../sgd3dgs-app}"

if [ ! -x "$application_root/scripts/uv.sh" ]; then
  printf 'App repository not found at %s\n' "$application_root" >&2
  printf 'Set SGD3DGS_APP_DIR to the sgd3dgs-app checkout.\n' >&2
  exit 1
fi

cd "$application_root"
exec ./scripts/uv.sh run sgd3dgs validate --check-files "$manifest_path"
