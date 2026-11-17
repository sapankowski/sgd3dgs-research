#!/usr/bin/env bash
set -eu

repository_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
external_dir="$repository_root/.external"
mkdir -p "$external_dir"

clone_pinned() {
  name="$1"
  url="$2"
  commit="$3"
  target="$external_dir/$name"

  if [ -d "$target/.git" ]; then
    printf '%s already exists at %s; leaving it unchanged.\n' "$name" "$target"
    return
  fi
  if [ -e "$target" ]; then
    printf 'Refusing to overwrite non-Git path: %s\n' "$target" >&2
    exit 1
  fi

  printf 'Fetching %s...\n' "$name"
  git clone --filter=blob:none --no-checkout "$url" "$target"
  git -C "$target" checkout --detach "$commit"
  printf 'Pinned %s at %s\n' "$name" "$commit"
}

clone_pinned \
  gaussian-grouping \
  https://github.com/lkeab/gaussian-grouping.git \
  0ab60afed3385b717c985af1d30a20f7b0884c89

clone_pinned \
  saga \
  https://github.com/Jumpat/SegAnyGAussians.git \
  2d4c5d77c857c956d747e4775d3d72c4ec5dfe16

printf '\nUpstreams are available in %s.\n' "$external_dir"
printf 'They require separate legacy environments; do not install them into the base research venv.\n'
