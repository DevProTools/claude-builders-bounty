#!/usr/bin/env bash
set -euo pipefail

# Git-history CHANGELOG generator
# Pure bash, zero dependencies.
# Usage: ./changelog.sh [--output CHANGELOG.md] [--since v1.0.0] [--to v2.0.0]

OUTPUT="CHANGELOG.md"
SINCE=""
UNTIL="HEAD"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output) OUTPUT="$2"; shift 2 ;;
    --since)  SINCE="$2";  shift 2 ;;
    --to)     UNTIL="$2";   shift 2 ;;
    -h|--help)
      echo "Usage: $0 [--output FILE] [--since TAG] [--to TAG]"
      echo ""
      echo "Generate a structured CHANGELOG.md from git history."
      echo ""
      echo "Options:"
      echo "  --output FILE  Output file (default: CHANGELOG.md)"
      echo "  --since TAG    Start from this tag (default: last tag)"
      echo "  --to TAG       End at this tag (default: HEAD)"
      exit 0 ;;
    *) echo "Unknown: $1"; exit 1 ;;
  esac
done

[ -d .git ] || { echo "Error: not a git repository"; exit 1; }

# Determine version range
if [ -z "$SINCE" ]; then
  SINCE=$(git describe --tags --abbrev=0 2>/dev/null || git rev-list --max-parents=0 HEAD)
fi
RANGE="$SINCE..$UNTIL"

COMMITS=$(git log --format="---%ncommit: %H%nsubject: %s%nbody: %b%n" --no-merges "$RANGE" 2>/dev/null)
[ -n "$COMMITS" ] || { echo "No commits found in range $RANGE"; exit 0; }

# Count total commits
TOTAL=$(echo "$COMMITS" | grep -c "^commit:")
# Get stats
ADDITIONS=$(git diff --shortstat "$RANGE" 2>/dev/null | awk '{print $4+0}')
DELETIONS=$(git diff --shortstat "$RANGE" 2>/dev/null | awk '{print $6+0}')
FILES=$(git diff --stat "$RANGE" 2>/dev/null | wc -l | tr -d ' ')
[ -z "$ADDITIONS" ] && ADDITIONS=0
[ -z "$DELETIONS" ] && DELETIONS=0

# Build scope tag from repo
REPO_URL=$(git remote get-url origin 2>/dev/null | sed 's/\.git$//' || echo "")
SHORT_URL=$(basename "$(pwd)")

# Parse commits into categories
declare -A SECTIONS
SECTIONS=(
  [feat]="✨ Features" [fix]="🐛 Bug Fixes" [docs]="📝 Documentation"
  [style]="💄 Style" [refactor]="♻️ Refactor" [perf]="⚡ Performance"
  [test]="✅ Tests" [chore]="🔧 Chores" [ci]="👷 CI/CD"
  [build]="📦 Build" [revert]="⏪ Reverts" [breaking]="💥 Breaking Changes"
)

declare -A BODIES
for k in "${!SECTIONS[@]}"; do BODIES["$k"]=""; done

while IFS= read -r line; do
  case "$line" in
    subject:\ *\!:*)
      msg="${line#subject: }"
      BODIES[breaking]+="- ${msg#\!: }"$'\n' ;;
    subject:\ (feat|fix|docs|style|refactor|perf|test|chore|ci|build|revert)(\(.*\))?:\ *)
      cat="${BASH_REMATCH[1]}"
      BODIES["$cat"]+="- ${BASH_REMATCH[0]#subject: }"$'\n' ;;
    subject:\ *)
      BODIES[misc]+="- ${line#subject: }"$'\n' ;;
  esac
done < <(echo "$COMMITS")

{
  echo "# Changelog"
  echo ""
  echo "## [$SINCE → $UNTIL] — $(date +%Y-%m-%d)"
  echo ""
  echo "### 📊 Overview"
  echo ""
  echo "| Metric | Value |"
  echo "|---|---|"
  echo "| Commits | $TOTAL |"
  echo "| Files changed | $FILES |"
  echo "| Additions | +$ADDITIONS |"
  echo "| Deletions | -$DELETIONS |"
  echo ""
  echo "### 📋 Changes"
  echo ""

  for section in breaking feat fix perf refactor docs style test chore ci build revert misc; do
    [ -n "${BODIES[$section]}" ] && echo "${SECTIONS[$section]:-🔄 Miscellaneous}" && echo "" && echo "${BODIES[$section]}" && echo ""
  done
} > "$OUTPUT"

echo "✓ Generated $OUTPUT ($TOTAL commits, +$ADDITION/-$DELETION, $FILES files)"
