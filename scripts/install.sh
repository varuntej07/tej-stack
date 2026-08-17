#!/usr/bin/env sh
set -eu

usage() {
  cat <<'EOF'
Usage: ./scripts/install.sh [codex|claude|both] [--user|--project] [--update]
       [--home PATH] [--project-root PATH]

Defaults: both --user
EOF
}

target="both"
scope="user"
update="false"
home_dir=${HOME:-}
project_root=$(pwd)

if [ "$#" -gt 0 ]; then
  case "$1" in
    codex|claude|both) target=$1; shift ;;
  esac
fi

while [ "$#" -gt 0 ]; do
  case "$1" in
    --user) scope="user" ;;
    --project) scope="project" ;;
    --update) update="true" ;;
    --home)
      [ "$#" -ge 2 ] || { echo "Error: --home requires a path." >&2; exit 2; }
      home_dir=$2
      shift
      ;;
    --project-root)
      [ "$#" -ge 2 ] || { echo "Error: --project-root requires a path." >&2; exit 2; }
      project_root=$2
      shift
      ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Error: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

if [ "$scope" = "user" ] && [ -z "$home_dir" ]; then
  echo "Error: no user home directory is available." >&2
  exit 2
fi

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
source_dir=$(CDPATH= cd -- "$script_dir/../plugins/tej-stack/skills" && pwd)

skill_names=""
for skill_dir in "$source_dir"/*; do
  [ -d "$skill_dir" ] || continue
  [ -f "$skill_dir/SKILL.md" ] || continue
  skill_name=$(basename -- "$skill_dir")
  skill_names="${skill_names}${skill_name}
"
done

[ -n "$skill_names" ] || { echo "Error: no bundled skills found." >&2; exit 2; }

is_expected_skill() {
  skill_file=$1
  expected=$2
  [ -f "$skill_file" ] || return 1
  awk -v expected="$expected" '
    NR == 1 { if ($0 != "---") exit 1; next }
    $0 == "---" { closed = 1; exit name_count == 1 ? 0 : 1 }
    /^name:[[:space:]]*/ {
      if ($0 == "name: " expected) name_count++
      else exit 1
    }
    END { if (!closed) exit 1 }
  ' "$skill_file"
}

destination_for() {
  agent=$1
  skill_name=$2
  if [ "$scope" = "user" ]; then
    case "$agent" in
      codex) printf '%s\n' "$home_dir/.codex/skills/$skill_name" ;;
      claude) printf '%s\n' "$home_dir/.claude/skills/$skill_name" ;;
    esac
  else
    case "$agent" in
      codex) printf '%s\n' "$project_root/.agents/skills/$skill_name" ;;
      claude) printf '%s\n' "$project_root/.claude/skills/$skill_name" ;;
    esac
  fi
}

preflight() {
  agent=$1
  skill_name=$2
  source_skill="$source_dir/$skill_name/SKILL.md"
  dest=$(destination_for "$agent" "$skill_name")

  if ! is_expected_skill "$source_skill" "$skill_name"; then
    echo "Error: bundled skill is missing or invalid: $skill_name" >&2
    return 2
  fi
  [ -e "$dest" ] || return 0
  if ! is_expected_skill "$dest/SKILL.md" "$skill_name"; then
    echo "Error: refusing to overwrite a different installation at: $dest" >&2
    return 4
  fi
  if [ "$update" != "true" ]; then
    echo "Error: $skill_name is already installed at: $dest" >&2
    echo "Re-run with --update to replace this same skill." >&2
    return 3
  fi
}

install_one() {
  agent=$1
  skill_name=$2
  source_skill_dir="$source_dir/$skill_name"
  dest=$(destination_for "$agent" "$skill_name")
  parent=$(dirname -- "$dest")
  mkdir -p -- "$parent"
  stage=$(mktemp -d "$parent/.tej-stack.install.XXXXXX") || return 1
  if ! cp -R "$source_skill_dir/." "$stage/"; then
    rm -rf -- "$stage"
    return 1
  fi

  if [ -e "$dest" ]; then
    backup="$parent/.tej-stack.backup.$$.$skill_name"
    [ ! -e "$backup" ] || { echo "Error: backup path exists: $backup" >&2; rm -rf -- "$stage"; return 1; }
    mv -- "$dest" "$backup"
    if mv -- "$stage" "$dest"; then
      rm -rf -- "$backup"
    else
      mv -- "$backup" "$dest" || true
      rm -rf -- "$stage"
      return 1
    fi
  else
    mv -- "$stage" "$dest"
  fi

  case "$agent" in
    codex) invocation="\$$skill_name" ;;
    claude) invocation="/$skill_name" ;;
  esac
  echo "Installed $skill_name for $agent at: $dest"
  echo "Invoke it with: $invocation"
}

case "$target" in
  codex) agents="codex" ;;
  claude) agents="claude" ;;
  both) agents="codex claude" ;;
  *) echo "Error: target must be codex, claude, or both." >&2; usage >&2; exit 2 ;;
esac

for agent in $agents; do
  printf '%s' "$skill_names" | while IFS= read -r skill_name; do
    [ -n "$skill_name" ] || continue
    preflight "$agent" "$skill_name"
  done
done

for agent in $agents; do
  printf '%s' "$skill_names" | while IFS= read -r skill_name; do
    [ -n "$skill_name" ] || continue
    install_one "$agent" "$skill_name"
  done
done
