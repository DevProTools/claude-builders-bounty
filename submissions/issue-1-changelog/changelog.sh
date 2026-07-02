#!/usr/bin/env bash
set -euo pipefail

# git-history CHANGELOG generator
# Usage: ./changelog.sh [--output CHANGELOG.md] [--since v1.0.0]

OUTPUT="CHANGELOG.md"
SINCE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output) OUTPUT="$2"; shift 2 ;;
    --since) SINCE="$2"; shift 2 ;;
    *) echo "Usage: $0 [--output FILE] [--since TAG]"; exit 1 ;;
  esac
done

if [ ! -d .git ]; then
  echo "Error: not a git repository"
  exit 1
fi

LOG_ARGS=("--format=- %s" "--no-merges")
if [ -n "$SINCE" ]; then
  LOG_ARGS+=("$SINCE..HEAD")
fi

COMMITS=$(git log "${LOG_ARGS[@]}")

CATEGORIES="feat|fix|docs|style|refactor|perf|test|chore|ci|build|revert"

declare -A SECTIONS
SECTIONS[feat]="## ✨ Features"
SECTIONS[fix]="## 🐛 Bug Fixes"
SECTIONS[docs]="## 📝 Documentation"
SECTIONS[style]="## 💄 Style"
SECTIONS[refactor]="## ♻️ Refactor"
SECTIONS[perf]="## ⚡ Performance"
SECTIONS[test]="## ✅ Tests"
SECTIONS[chore]="## 🔧 Chores"
SECTIONS[ci]="## 👷 CI/CD"
SECTIONS[build]="## 📦 Build"
SECTIONS[revert]="## ⏪ Reverts"

declare -A BODIES
for cat in "${!SECTIONS[@]}"; do
  BODIES["$cat"]=""
done

LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")

while IFS= read -r line; do
  MATCHED=false
  for cat in "${!SECTIONS[@]}"; do
    if [[ "$line" =~ ^-\ *($cat)(\(.*\))?:\ *(.*) ]]; then
      BODIES["$cat"]+="${line}$(echo -e '\n')"
      MATCHED=true
      break
    fi
  done
  if [ "$MATCHED" = false ] && [[ "$line" == -* ]]; then
    BODIES["misc"]+="${line}$(echo -e '\n')"
  fi
done <<< "$COMMITS"

{
  echo "# Changelog"
  echo ""
  if [ -n "$LAST_TAG" ]; then
    echo "## [$LAST_TAG] - $(date +%Y-%m-%d)"
  else
    echo "## [Unreleased] - $(date +%Y-%m-%d)"
  fi
  echo ""
  echo "### Highlights"
  echo "- $(echo "$COMMITS" | head -1 | sed 's/^- //')"
  echo ""
  for cat in feat fix docs style refactor perf test chore ci build revert; do
    if [ -n "${BODIES[$cat]}" ]; then
      echo "${SECTIONS[$cat]}"
      echo "${BODIES[$cat]}"
    fi
  done
  if [ -n "${BODIES[misc]}" ]; then
    echo "## 🔄 Miscellaneous"
    echo "${BODIES[misc]}"
  fi
} > "$OUTPUT"

echo "Generated $OUTPUT with $(echo "$COMMITS" | wc -l | tr -d ' ') commits"
