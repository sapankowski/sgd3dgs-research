#!/usr/bin/env bash
set -eu

repository_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repository_root"

printf 'Checking required research repository files...\n'
for required_path in \
  README.md \
  LICENSE \
  THIRD_PARTY.md \
  adapters/README.md \
  docs/EXPERIMENTS.md \
  experiments/templates/experiment.yaml \
  upstreams.lock.yaml \
  src/sgd3dgs_research/models.py; do
  if [ ! -f "$required_path" ]; then
    printf 'Missing required file: %s\n' "$required_path" >&2
    exit 1
  fi
done

if [ -d apps ] || [ -d schemas ] || [ -d services ]; then
  printf 'Application-owned directory found in research repository.\n' >&2
  exit 1
fi

printf 'Checking for accidentally tracked large or binary research artifacts...\n'
large_files=""
forbidden_files=""
while IFS= read -r -d '' path; do
  size=$(wc -c < "$path")
  if [ "$size" -gt 52428800 ]; then
    large_files="${large_files}${path}\n"
  fi
  case "$path" in
    *.ply|*.splat|*.ksplat|*.spz|*.sog|*.npy|*.npz|*.pt|*.pth|*.ckpt|*.safetensors|*.onnx)
      forbidden_files="${forbidden_files}${path}\n"
      ;;
  esac
done < <(git ls-files -z)

if [ -n "$large_files" ]; then
  printf 'Tracked files larger than 50 MB found:\n%b' "$large_files" >&2
  exit 1
fi
if [ -n "$forbidden_files" ]; then
  printf 'Tracked scene/model artifact found:\n%b' "$forbidden_files" >&2
  exit 1
fi

printf 'Research repository structure looks valid.\n'
