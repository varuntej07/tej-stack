#!/usr/bin/env bash
# Stop: block the turn (exit 2) when THIS session's source edits break a tej-core rule.
# Read-only and fast: never builds, never runs tests.
# Runs only in repos set up by /tej-core:init, and judges only files modified since orient.sh
# stamped the session, so pre-existing uncommitted work never blocks a session that did not
# touch it, and a repo that never opted in is never blocked at all.
input="$(cat 2>/dev/null)"
here="$(cd "$(dirname "$0")" && pwd)"
. "$here/config.sh"

cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0
root="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
cd "$root" || exit 0
cfg_find "$root" || exit 0
stamp=".context/4-scratchpad/.session-start"
[ -f "$stamp" ] || exit 0

exts="$(cfg_str source_extensions)"
[ -z "$exts" ] && exts='py|rs|ts|tsx|js|jsx|go|java|kt|swift|dart|rb|cs'
fastfail_re="$(cfg_str fastfail_path_regex)"

problems=""
add() { problems="${problems}  - $1"$'\n'; }

changed="$( { git diff --name-only HEAD 2>/dev/null; git ls-files --others --exclude-standard 2>/dev/null; } \
  | grep -E "\.($exts)\$" | sort -u \
  | while IFS= read -r f; do [ -f "$f" ] && [ "$f" -nt "$stamp" ] && printf '%s\n' "$f"; done )"

while IFS= read -r f; do
  [ -n "$f" ] || continue
  if git ls-files --error-unmatch "$f" >/dev/null 2>&1; then
    added="$(git diff -U0 HEAD -- "$f" | grep -E '^\+' | grep -vE '^\+\+\+' | sed 's/^+//')"
  else
    added="$(cat "$f")"
  fi
  [ -z "$added" ] && continue

  hits="$(printf '%s\n' "$added" | awk '
    { line=$0 }
    line ~ /except[^:]*:[ \t]*pass[ \t]*$/ { print "silent except: pass" }
    prev ~ /^[ \t]*except[^:]*:[ \t]*$/ && line ~ /^[ \t]*pass[ \t]*$/ { print "silent except: pass" }
    line ~ /catch[ \t]*(\([^)]*\))?[ \t]*\{[ \t]*\}/ { print "empty catch {}" }
    line ~ /\.catch\([ \t]*\([^)]*\)[ \t]*=>[ \t]*\{[ \t]*\}[ \t]*\)/ { print "empty .catch(() => {})" }
    line ~ /Err\(_\)[ \t]*=>[ \t]*\{[ \t]*\}/ { print "swallowed Err(_) => {}" }
    line ~ /[A-Z][A-Z0-9_]*_ENABLED/ { print "*_ENABLED feature flag" }
    line ~ /Co-Authored-By:|Claude-Session|Generated with \[Claude Code\]/ { print "AI attribution trailer" }
    { prev = line }' | sort -u)"
  while IFS= read -r h; do [ -n "$h" ] && add "$f: $h"; done <<< "$hits"

  if [ -n "$fastfail_re" ] && printf '%s' "$f" | grep -qE "$fastfail_re"; then
    retry="$(printf '%s\n' "$added" \
      | grep -vE '^[[:space:]]*(#|//|\*|/\*)' \
      | grep -vE 'fastfail-exempt:|max_retries[[:space:]]*=[[:space:]]*0' \
      | grep -iE 'retry|retries|backoff|tenacity|max_attempts|for attempt in' | head -3)"
    [ -n "$retry" ] && add "$f: retry/backoff on a FastFail path (mark fastfail-exempt: <reason> only for a durable queue or device recovery): $(printf '%s' "$retry" | head -1 | cut -c1-120)"
  fi
done <<< "$changed"

for s in .context/2-specs/SPEC-*.md .context/2-specs/BUG-*.md; do
  [ -f "$s" ] || continue
  if grep -qE '^status:[[:space:]]*(closing|done)' "$s" && grep -q -- '- \[ \]' "$s"; then
    add "$s: marked closing/done with unchecked acceptance criteria"
  fi
done

if cfg_true forbid_project_memory; then
  slug="$(printf '%s' "${CLAUDE_PROJECT_DIR:-$root}" | sed 's/[^A-Za-z0-9]/-/g')"
  memdir="$HOME/.claude/projects/$slug/memory"
  if [ -d "$memdir" ]; then
    for m in "$memdir"/*; do
      [ -f "$m" ] || continue
      [ "$(basename "$m")" = "MEMORY.md" ] && continue
      [ "$m" -nt "$stamp" ] && add "stray memory file created this session: $m (durable facts belong in .context/ or .claude/rules/)"
    done
  fi
fi

[ -z "$problems" ] && exit 0
msg="tej-core verify blocked completion:"$'\n'"$problems""Fix these (or explain to the user why a rule does not apply) before finishing."
case "$input" in
  *'"stop_hook_active":true'*|*'"stop_hook_active": true'*)
    printf '%s\n(second stop attempt: not blocking again to avoid a loop; report these to the user)\n' "$msg" >&2
    exit 0 ;;
esac
printf '%s\n' "$msg" >&2
exit 2
