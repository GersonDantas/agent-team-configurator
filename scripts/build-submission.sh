#!/bin/sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
plugin_root="$repo_root/plugins/executor-consultor"
output="$repo_root/dist/executor-consultor-0.2.0.zip"

mkdir -p "$repo_root/dist"
rm -f "$output"
cd "$plugin_root"
zip -qr "$output" . -x '.DS_Store' '*.pyc' '*__pycache__*' '*executor-consultor-state.json'
printf '%s\n' "$output"
