#!/usr/bin/env bash
# Shared by orient.sh and verify.sh. Reads .context/tej-core.json without jq.
# Contract (written by /tej-core:init): flat JSON, every key and its whole value on ONE line.
#   "repos": ["C:/code/app", "C:/code/app-api"]     every repo whose specs this session shows
#   "never_touch": ["old-clone", "decoy-repo"]       folders a session must never read or edit
#   "source_extensions": "py|ts|tsx"                 files verify.sh judges
#   "fastfail_path_regex": "(/voice/|/stt/)"         paths where a retry or backoff is blocked
#   "forbid_project_memory": true                    durable facts belong in the repo, not memory

cfg_file=""

cfg_find() {
  # $1 = repo root. Sets cfg_file when the repo was initialized.
  cfg_file=""
  [ -f "$1/.context/tej-core.json" ] && cfg_file="$1/.context/tej-core.json"
  [ -n "$cfg_file" ]
}

cfg_str() {
  [ -n "$cfg_file" ] || return 0
  grep -m1 -E "\"$1\"[[:space:]]*:" "$cfg_file" 2>/dev/null \
    | sed -E "s/^[^:]*:[[:space:]]*\"(.*)\"[[:space:]]*,?[[:space:]]*$/\1/" \
    | sed -e 's/\\\\/\x01/g' -e 's/\\"/"/g' -e 's/\x01/\\/g'
}

cfg_list() {
  [ -n "$cfg_file" ] || return 0
  grep -m1 -E "\"$1\"[[:space:]]*:" "$cfg_file" 2>/dev/null \
    | sed -E 's/^[^:]*:[[:space:]]*\[(.*)\].*$/\1/' \
    | grep -oE '"[^"]*"' | sed -E 's/^"(.*)"$/\1/'
}

cfg_true() {
  [ -n "$cfg_file" ] || return 1
  grep -m1 -E "\"$1\"[[:space:]]*:[[:space:]]*true" "$cfg_file" >/dev/null 2>&1
}
