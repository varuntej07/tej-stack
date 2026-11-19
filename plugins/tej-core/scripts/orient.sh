#!/usr/bin/env bash
# SessionStart. Everything printed here becomes session context.
# 1. Always: the tej-core rules, plus the user's own ~/.claude/tej-core/rules.md if present.
# 2. In a repo set up by /tej-core:init: repo orientation, active specs, and the session stamp
#    verify.sh uses to tell this session's edits from work that was already there.
# Never fails the session: every missing piece is skipped and the script exits 0.
input="$(cat 2>/dev/null)"
here="$(cd "$(dirname "$0")" && pwd)"
. "$here/config.sh"

echo "tej-core rules (apply to this whole session):"
[ -f "$here/../rules/core.md" ] && cat "$here/../rules/core.md"
if [ -f "$HOME/.claude/tej-core/rules.md" ]; then
  echo
  echo "Your own rules (~/.claude/tej-core/rules.md):"
  cat "$HOME/.claude/tej-core/rules.md"
fi

cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0
root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# Spotlight recheck reminder. /tej-core:spotlight writes .context/spotlight.json
# ({"last_run": "YYYY-MM-DD", "site": "...", "recheck_days": 30}) after every run,
# in any repo, set up by init or not. Once the run is older than recheck_days,
# the agent is told to remind the user once.
spot="$root/.context/spotlight.json"
if [ -f "$spot" ]; then
  last="$(grep -m1 -oE '"last_run"[[:space:]]*:[[:space:]]*"[0-9]{4}-[0-9]{2}-[0-9]{2}"' "$spot" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}')"
  every="$(grep -m1 -oE '"recheck_days"[[:space:]]*:[[:space:]]*[0-9]+' "$spot" | grep -oE '[0-9]+$')"
  site="$(grep -m1 -oE '"site"[[:space:]]*:[[:space:]]*"[^"]*"' "$spot" | cut -d'"' -f4)"
  [ -n "$every" ] || every=30
  then_s="$(date -u -d "$last" +%s 2>/dev/null || date -u -j -f %Y-%m-%d "$last" +%s 2>/dev/null)"
  echo
  if [ -z "$last" ] || [ -z "$then_s" ]; then
    echo "tej-core: $spot has no readable \"last_run\" date, so the spotlight recheck reminder is off."
    echo "  Tell the user once, and fix the file on the next spotlight run."
  else
    age=$(( ( $(date -u +%s) - then_s ) / 86400 ))
    if [ "$age" -ge "$every" ]; then
      echo "tej-core: spotlight recheck is due for ${site:-this site} (last run $last, $age days ago; every $every days)."
      echo "  Start your first reply with one line telling the user, and offer to run /tej-core:spotlight recheck."
      echo "  Say it once per session, never again after they answer."
    else
      echo "tej-core: spotlight last ran $last; the next recheck is due in $(( every - age )) days. Do not mention it."
    fi
  fi
fi
if ! cfg_find "$root"; then
  echo
  echo "tej-core: this repo is not set up yet. Run /tej-core:init when the user wants specs,"
  echo "architecture docs and the evaluator gate here. Do not suggest it more than once."
  exit 0
fi

stamp="$root/.context/4-scratchpad/.session-start"
mkdir -p "$root/.context/4-scratchpad" 2>/dev/null
case "$input" in
  *'"source":"resume"'*|*'"source": "resume"'*|*'"source":"compact"'*|*'"source": "compact"'*)
    [ -f "$stamp" ] || touch "$stamp" ;;
  *) touch "$stamp" ;;
esac

echo
echo "tej-core orientation"
repos="$(cfg_list repos)"
[ -z "$repos" ] && repos="$root"
while IFS= read -r r; do [ -n "$r" ] && echo "  Repo         : $r"; done <<< "$repos"
never="$(cfg_list never_touch | paste -sd, - 2>/dev/null | sed 's/,/, /g')"
[ -n "$never" ] && echo "  Never touch  : $never"
echo "  Before editing a file, read its .context/1-docs/ARCH-*.md (lookup table in CLAUDE.md)."
echo "  Repo-specific steps for every tej-core skill: .claude/rules/project-workflow.md"

found=0
while IFS= read -r repo; do
  [ -n "$repo" ] || continue
  for f in "$repo"/.context/2-specs/SPEC-*.md "$repo"/.context/2-specs/BUG-*.md; do
    [ -f "$f" ] || continue
    status="$(grep -m1 -E '^status:' "$f" | sed -E 's/^status:[[:space:]]*([a-z_]+).*/\1/')"
    [ "$status" = "done" ] && continue
    open="$(grep -c -- '- \[ \]' "$f")"
    [ $found -eq 0 ] && echo "Active specs:"
    found=1
    echo "  [$status] $f ($open open criteria)"
  done
done <<< "$repos"
[ $found -eq 0 ] && echo "Active specs: none"
exit 0
