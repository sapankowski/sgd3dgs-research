#!/usr/bin/env bash
set -u

failures=0
notices=0

check_command() {
  command_name="$1"
  minimum_note="$2"
  if command -v "$command_name" >/dev/null 2>&1; then
    version="$($command_name --version 2>/dev/null | head -n 1)"
    printf 'OK      %-12s %s\n' "$command_name" "$version"
  else
    printf 'MISSING %-12s %s\n' "$command_name" "$minimum_note"
    failures=$((failures + 1))
  fi
}

printf 'SGD3DGS Research readiness check\n\n'
check_command git 'install Git 2.40 or newer'
check_command uv 'install from https://docs.astral.sh/uv/'
check_command python3 'uv will install the pinned Python 3.12 interpreter'

printf '\nOptional shared GPU worker checks\n'
if command -v nvidia-smi >/dev/null 2>&1; then
  printf 'OK      nvidia-smi   NVIDIA GPU is visible\n'
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>/dev/null || true
else
  printf 'NOTICE  nvidia-smi   expected only on the Linux GPU worker\n'
  notices=$((notices + 1))
fi

if command -v docker >/dev/null 2>&1; then
  printf 'OK      docker       %s\n' "$(docker --version)"
else
  printf 'NOTICE  docker       required when a baseline container is promoted\n'
  notices=$((notices + 1))
fi

printf '\nResult: %s required tool(s) missing, %s optional notice(s).\n' "$failures" "$notices"
if [ "$failures" -ne 0 ]; then
  exit 1
fi
