#!/usr/bin/env python3
"""claude-review: AI-powered PR review agent.

Usage:
    python claude_review.py --pr https://github.com/owner/repo/pull/123
    python claude_review.py --diff-file /path/to/diff.txt
    python claude_review.py --pr 123 --repo owner/repo
"""

import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import datetime


def parse_args():
    p = argparse.ArgumentParser(description="AI-powered PR review agent")
    p.add_argument("--pr", help="PR URL or number")
    p.add_argument("--repo", help="Repository (owner/repo)")
    p.add_argument("--diff-file", help="Path to diff file")
    p.add_argument("--github-token", help="GitHub token", default=os.getenv("GITHUB_TOKEN", ""))
    p.add_argument("--output", "-o", help="Output file (default: stdout)")
    p.add_argument("--format", choices=["markdown", "json"], default="markdown")
    return p.parse_args()


def fetch_pr_diff(repo, pr_num, token):
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_num}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3.diff",
        "User-Agent": "claude-review"
    })
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return resp.read().decode("utf-8")
    except Exception as e:
        print(f"Error fetching PR: {e}", file=sys.stderr)
        sys.exit(1)


def fetch_pr_metadata(repo, pr_num, token):
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_num}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}", "User-Agent": "claude-review"
    })
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read().decode())
    except:
        return {}


def analyze_diff(diff_text):
    files = re.split(r"^diff --git ", diff_text, flags=re.MULTILINE)
    files = [f for f in files if f.strip()]
    
    stats = {"files_changed": 0, "additions": 0, "deletions": 0, "file_types": {}}
    reviews = []
    
    for f in files:
        if not f.strip():
            continue
        stats["files_changed"] += 1
        header_match = re.search(r"a/(.+?) b/(.+?)$", f, re.MULTILINE)
        filename = header_match.group(2) if header_match else "unknown"
        ext = os.path.splitext(filename)[1].lower() or "no_ext"
        stats["file_types"][ext] = stats["file_types"].get(ext, 0) + 1
        
        # Count lines
        added = len(re.findall(r"^\+(?!\+)", f, re.MULTILINE))
        removed = len(re.findall(r"^-(?!-)", f, re.MULTILINE))
        stats["additions"] += added
        stats["deletions"] += removed
        
        # Security checks
        security_issues = []
        if re.search(r"shell=True|os\.system|subprocess\.call.*shell=True|eval\(|exec\(", f):
            security_issues.append("Command injection risk: shell=True or eval/exec detected")
        if re.search(r"\.innerHTML|\.outerHTML|dangerouslySetInnerHTML", f):
            security_issues.append("XSS risk: direct innerHTML assignment detected")
        if re.search(r"secret|password|api.?key|token|credential", f, re.I):
            security_issues.append("Sensitive data: potential secret in code (check for hardcoded credentials)")
        if re.search(r"SELECT.*FROM|INSERT INTO|DROP TABLE|DELETE FROM", f, re.I):
            security_issues.append("SQL query: verify parameterization (no string interpolation)")
        if re.search(r"yaml\.load\(|pickle\.loads\(|xml\.etree", f):
            security_issues.append("Insecure deserialization: use safe_load instead of load")
        
        if security_issues:
            reviews.append({
                "file": filename,
                "additions": added,
                "deletions": removed,
                "security_issues": security_issues
            })
    
    return stats, reviews


def generate_markdown_review(meta, diff_text, stats, reviews):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    title = meta.get("title", "PR Review")
    author = meta.get("user", {}).get("login", "unknown")
    pr_url = meta.get("html_url", "")
    
    md = []
    md.append(f"# 🔍 PR Review: {title}")
    md.append(f"")
    md.append(f"**Author:** @{author}  ")
    if pr_url:
        md.append(f"**PR:** [{pr_url}]({pr_url})  ")
    md.append(f"**Review generated:** {now}")
    md.append(f"")
    md.append("---")
    md.append(f"")
    md.append("## 📊 Summary")
    md.append(f"")
    md.append(f"| Metric | Value |")
    md.append(f"|---|---|")
    md.append(f"| Files changed | {stats['files_changed']} |")
    md.append(f"| Additions | {stats['additions']} |")
    md.append(f"| Deletions | {stats['deletions']} |")
    file_types = ", ".join(f"{k}: {v}" for k, v in sorted(stats["file_types"].items()))
    md.append(f"| File types | {file_types} |")
    md.append(f"")
    
    if reviews:
        md.append("## 🚨 Security Review")
        md.append(f"")
        for r in reviews:
            md.append(f"### 📁 `{r['file']}` (+{r['additions']}/-{r['deletions']})")
            md.append(f"")
            for issue in r["security_issues"]:
                md.append(f"- ⚠️ {issue}")
            md.append(f"")
    
    md.append("## ✅ Recommendations")
    md.append(f"")
    if stats["additions"] > 500:
        md.append(f"- Consider splitting this PR into smaller, focused changes (< 500 lines)")
    if stats["files_changed"] > 10:
        md.append(f"- High number of files changed ({stats['files_changed']}); verify scope is focused")
    md.append(f"- Ensure all new code has corresponding tests")
    md.append(f"- Verify the changes work in staging before production deployment")
    md.append(f"- Check for any hardcoded values that should be environment variables")
    md.append(f"")
    md.append("---")
    md.append(f"*Generated by claude-review · AI-powered PR review agent*")
    
    return "\n".join(md)


def post_review_comment(repo, pr_num, token, comment):
    url = f"https://api.github.com/repos/{repo}/issues/{pr_num}/comments"
    data = json.dumps({"body": comment}).encode()
    req = urllib.request.Request(url, data=data, method="POST", headers={
        "Authorization": f"Bearer {token}",
        "User-Agent": "claude-review",
        "Content-Type": "application/json"
    })
    try:
        urllib.request.urlopen(req, timeout=15)
        return True
    except Exception as e:
        print(f"Warning: Could not post comment: {e}", file=sys.stderr)
        return False


def main():
    args = parse_args()
    
    if args.diff_file:
        with open(args.diff_file) as f:
            diff_text = f.read()
        meta = {}
    elif args.pr:
        if "/" in args.pr:
            parts = args.pr.replace("https://github.com/", "").split("/pull/")
            repo = parts[0]
            pr_num = parts[1]
        elif args.repo:
            repo = args.repo
            pr_num = args.pr
        else:
            print("Error: --repo required when --pr is a number", file=sys.stderr)
            sys.exit(1)
        
        diff_text = fetch_pr_diff(repo, pr_num, args.github_token)
        meta = fetch_pr_metadata(repo, pr_num, args.github_token)
    else:
        print("Error: provide --pr or --diff-file", file=sys.stderr)
        sys.exit(1)
    
    stats, reviews = analyze_diff(diff_text)
    
    if args.format == "json":
        output = json.dumps({
            "metadata": meta,
            "stats": stats,
            "reviews": reviews,
            "generated_at": datetime.utcnow().isoformat()
        }, indent=2)
    else:
        output = generate_markdown_review(meta, diff_text, stats, reviews)
    
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Review written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
