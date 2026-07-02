# CHANGELOG Generator — Claude Code Skill

## Description
Generates a structured `CHANGELOG.md` from git history using Conventional Commits.

## Usage
```bash
# In any git repo:
./submissions/issue-1-changelog/changelog.sh

# Custom output file:
./submissions/issue-1-changelog/changelog.sh --output docs/CHANGELOG.md

# From a specific tag:
./submissions/issue-1-changelog/changelog.sh --since v1.0.0
```

## Features
- Parses Conventional Commits (feat, fix, docs, style, refactor, perf, test, chore, ci, build, revert)
- Groups commits by category with emoji headers
- Handles scoped commits (e.g., `feat(auth): add login`)
- Last tag detection for version headers
- Exit on error, safe for CI pipelines
- No external dependencies (pure bash)

## Output Example
```markdown
# Changelog

## [Unreleased] - 2026-07-01

### Highlights
- feat: add user authentication with OAuth

## ✨ Features
- feat: add user authentication with OAuth
- feat(api): add rate limiting middleware

## 🐛 Bug Fixes
- fix: resolve login redirect loop
```
