#!/bin/sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
plugin_root="$repo_root/plugins/personal-agent-team-codex"
output="$repo_root/dist/personal-agent-team-codex-0.4.0.zip"

mkdir -p "$repo_root/dist"
rm -f "$output"
cd "$plugin_root"
zip -qr "$output" . -x '.DS_Store' '*.pyc' '*__pycache__*' '*executor-consultor-state.json' '*personal-agent-team-codex-state.json'
printf '%s\n' "$output"
