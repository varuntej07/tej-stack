#!/usr/bin/env bash
# Tej Stack update check. Prints one STATUS line and always exits 0.
# Throttled to one network request per 24 hours via ~/.tej-stack/last-update-check.
# Output contract, read by skill preambles:
#   TEJ_STACK: UP_TO_DATE <version>
#   TEJ_STACK: UPGRADE_AVAILABLE <local> -> <remote>
#   TEJ_STACK: CHECK_SKIPPED <reason>

set -u

REMOTE_VERSION_URL="https://raw.githubusercontent.com/varuntej07/tej-stack/main/VERSION"
STATE_DIR="${HOME}/.tej-stack"
STATE_FILE="${STATE_DIR}/last-update-check"
THROTTLE_SECONDS=86400

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MANIFEST="${SCRIPT_DIR}/../.claude-plugin/plugin.json"

local_version=""
if [ -f "$MANIFEST" ]; then
  local_version=$(sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([0-9.]*\)".*/\1/p' "$MANIFEST" | head -1)
fi
if [ -z "$local_version" ]; then
  echo "TEJ_STACK: CHECK_SKIPPED no-local-version"
  exit 0
fi

# The state file caches the REMOTE version (epoch + version); the comparison
# against the local version is recomputed on every run so a fresh local
# install is reflected immediately.
now=$(date +%s 2>/dev/null || echo 0)
remote_version=""
if [ -f "$STATE_FILE" ]; then
  last_epoch=$(awk '{print $1}' "$STATE_FILE" 2>/dev/null)
  cached_remote=$(awk '{print $2}' "$STATE_FILE" 2>/dev/null)
  case "$last_epoch" in
    ''|*[!0-9]*) last_epoch=0 ;;
  esac
  if [ $((now - last_epoch)) -lt "$THROTTLE_SECONDS" ]; then
    remote_version="$cached_remote"
  fi
fi

if [ -z "$remote_version" ] && command -v curl >/dev/null 2>&1; then
  remote_version=$(curl -fsS --max-time 3 "$REMOTE_VERSION_URL" 2>/dev/null | tr -d '[:space:]')
  case "$remote_version" in
    [0-9]*.[0-9]*.[0-9]*)
      mkdir -p "$STATE_DIR" 2>/dev/null
      echo "$now $remote_version" > "$STATE_FILE" 2>/dev/null
      ;;
  esac
fi
case "$remote_version" in
  [0-9]*.[0-9]*.[0-9]*) ;;
  *) remote_version="" ;;
esac
if [ -z "$remote_version" ]; then
  echo "TEJ_STACK: CHECK_SKIPPED offline"
  exit 0
fi

if [ "$remote_version" = "$local_version" ]; then
  status="UP_TO_DATE $local_version"
else
  newest=$(printf '%s\n%s\n' "$local_version" "$remote_version" | sort -t. -k1,1n -k2,2n -k3,3n | tail -1)
  if [ "$newest" = "$remote_version" ]; then
    status="UPGRADE_AVAILABLE $local_version -> $remote_version"
  else
    status="UP_TO_DATE $local_version"
  fi
fi

echo "TEJ_STACK: $status"
exit 0
