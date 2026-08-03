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
source_dir=$(CDPATH= cd -- "$script_dir/../skills/walkie-talkie" && pwd)
source_skill="$source_dir/SKILL.md"

is_walkie_talkie_skill() {
  skill_file=$1
  [ -f "$skill_file" ] || return 1
  awk '
    NR == 1 {
      if ($0 != "---") exit 1
      next
    }
    $0 == "---" {
      closed = 1
      exit name_count == 1 ? 0 : 1
    }
    /^name:[[:space:]]*/ {
      if ($0 == "name: walkie-talkie") {
        name_count++
      } else {
        exit 1
      }
    }
    END {
      if (!closed) exit 1
    }
  ' "$skill_file"
}

if ! is_walkie_talkie_skill "$source_skill"; then
  echo "Error: the bundled walkie-talkie skill is missing or invalid." >&2
  exit 2
fi

destination_for() {
  agent=$1
  if [ "$scope" = "user" ]; then
    case "$agent" in
      codex) printf '%s\n' "$home_dir/.agents/skills/walkie-talkie" ;;
      claude) printf '%s\n' "$home_dir/.claude/skills/walkie-talkie" ;;
    esac
  else
    case "$agent" in
      codex) printf '%s\n' "$project_root/.agents/skills/walkie-talkie" ;;
      claude) printf '%s\n' "$project_root/.claude/skills/walkie-talkie" ;;
    esac
  fi
}

preflight() {
  dest=$1
  if [ ! -e "$dest" ]; then
    return 0
  fi
  if ! is_walkie_talkie_skill "$dest/SKILL.md"; then
    echo "Error: refusing to overwrite a different installation at: $dest" >&2
    return 4
  fi
  if [ "$update" != "true" ]; then
    echo "Error: walkie-talkie is already installed at: $dest" >&2
    echo "Re-run with --update to replace this same skill." >&2
    return 3
  fi
}

install_one() {
  agent=$1
  dest=$(destination_for "$agent")
  parent=$(dirname -- "$dest")
  mkdir -p -- "$parent"
  stage=$(mktemp -d "$parent/.walkie-talkie.install.XXXXXX") || return 1
  if ! cp -R "$source_dir/." "$stage/"; then
    rm -rf -- "$stage"
    return 1
  fi

  if [ -e "$dest" ]; then
    backup="$parent/.walkie-talkie.backup.$$"
    if [ -e "$backup" ]; then
      echo "Error: safe backup path already exists: $backup" >&2
      rm -rf -- "$stage"
      return 1
    fi
    if ! mv -- "$dest" "$backup"; then
      rm -rf -- "$stage"
      return 1
    fi
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
    codex) invocation='$walkie-talkie' ;;
    claude) invocation='/walkie-talkie' ;;
  esac
  echo "Installed walkie-talkie for $agent at: $dest"
  echo "Invoke it with: $invocation"
}

case "$target" in
  codex) agents="codex" ;;
  claude) agents="claude" ;;
  both) agents="codex claude" ;;
  *) echo "Error: target must be codex, claude, or both." >&2; usage >&2; exit 2 ;;
esac

for agent in $agents; do
  preflight "$(destination_for "$agent")"
done
for agent in $agents; do
  install_one "$agent"
done
