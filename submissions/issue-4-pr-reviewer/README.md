# 🚀 claude-review — AI PR Review Agent

**Bounty #4** — $150

A lightweight, dependency-light AI pull-request reviewer that analyzes diffs
for security issues, code quality, and provides structured Markdown feedback.

## Quick Start

```bash
# Analyze a PR by URL
python claude_review.py --pr https://github.com/owner/repo/pull/123
```

```bash
# Analyze a local diff file
python claude_review.py --diff-file /path/to/pr.diff
```

## Features

- **Security analysis** — Detects command injection, XSS, hardcoded secrets,
  SQL injection, insecure deserialization, and more
- **Diff statistics** — Files changed, additions/deletions, file type breakdown
- **Markdown output** — Clean, structured review formatted for PR comments
- **GitHub Action** — Auto-comment on new PRs (drop in the workflow file)

## GitHub Action

Add `.github/workflows/claude-review.yml` to your repo. It runs on every
new or updated PR and posts a review comment automatically.

## Output Example

```markdown
# 🔍 PR Review: Add authentication middleware

**Author:** @johndoe
**Files changed:** 5 | **Additions:** 120 | **Deletions:** 30

## 🚨 Security Review
- ⚠️ Command injection risk: shell=True detected in deploy.sh
- ⚠️ SQL query: verify parameterization in user query

## ✅ Recommendations
- Consider splitting this PR into smaller changes
- Ensure all new code has tests
```

## No Dependencies

Python 3.8+ only — no pip install required. Uses only the standard library.
