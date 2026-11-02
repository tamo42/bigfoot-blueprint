#!/usr/bin/env python3
"""Scan the lines a working tree adds for leaked credentials.

Usage:
    python -I scripts/secret_scan.py <repo> [<repo> ...]
    python -I scripts/secret_scan.py --self-test

Scans, per repo, `git diff HEAD -U0` (added lines) plus untracked files that are
not git-ignored. Also fails if a changed path is a real `.env` file.
Exit 0 = clean, 1 = at least one HIT, 2 = usage or git error.
Hits print as `HIT file:line kind match3...` (match cut to its first 3 characters).
"""
import re
import subprocess
import sys
from pathlib import Path

PATTERNS = [
    ("aws-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("openai-key", re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}\b")),
    ("apify-token", re.compile(r"\bapify_api_[A-Za-z0-9]{20,}\b")),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b")),
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("db-url-password", re.compile(r"\bpostgres(?:ql)?://[^:\s/@]+:[^@\s]+@")),
    ("assigned-secret", re.compile(
        r"""(?ix)\b(?:api[_-]?key|secret|token|password|passwd|service[_-]?role|anon[_-]?key)\w*
            \s*[:=]\s*['"]([^'"\s]{12,})['"]""")),
]
# A match is inert (a placeholder, not a real secret) when it contains one of these.
INERT = re.compile(r"(?i)(your[_-]|<[^>]+>|example|xxxx|changeme|placeholder|dummy|redacted|\*{4}|\.\.\.)")
SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".sqlite",
                 ".db", ".mp4", ".mov", ".woff", ".woff2", ".lock"}
SELF = Path(__file__).name


def run_git(repo, *args):
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed in {repo}: {p.stderr.strip()}")
    return p.stdout


def added_lines_from_diff(diff):
    """Yield (path, line_no, text) for each added line of a `-U0` diff."""
    path, line_no = None, 0
    for raw in diff.splitlines():
        if raw.startswith("+++ "):
            path = raw[6:] if raw.startswith("+++ b/") else None
        elif raw.startswith("@@"):
            m = re.search(r"\+(\d+)", raw)
            line_no = int(m.group(1)) - 1 if m else 0
        elif raw.startswith("+") and not raw.startswith("+++"):
            line_no += 1
            if path:
                yield path, line_no, raw[1:]


def scan_text(path, line_no, text):
    hits = []
    for kind, rx in PATTERNS:
        for m in rx.finditer(text):
            token = m.group(1) if m.groups() else m.group(0)
            if INERT.search(token) or INERT.search(m.group(0)):
                continue
            hits.append((path, line_no, kind, token[:3]))
    return hits


def is_env_file(path):
    name = Path(path).name
    return name == ".env" or (name.startswith(".env.") and name not in {".env.example", ".env.sample", ".env.template"})


def scan_repo(repo):
    hits, inert = [], 0
    changed = set(run_git(repo, "diff", "HEAD", "--name-only").splitlines())
    untracked = [u for u in run_git(repo, "ls-files", "--others", "--exclude-standard").splitlines() if u]
    for path in sorted(changed | set(untracked)):
        if is_env_file(path):
            hits.append((path, 0, "env-file", ".en"))
    for path, line_no, text in added_lines_from_diff(run_git(repo, "diff", "HEAD", "-U0", "--no-color")):
        if Path(path).suffix.lower() in SKIP_SUFFIXES or Path(path).name == SELF:
            continue
        hits += scan_text(path, line_no, text)
    for path in untracked:
        p = Path(repo) / path
        if p.suffix.lower() in SKIP_SUFFIXES or p.name == SELF or not p.is_file():
            continue
        try:
            for i, text in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                hits += scan_text(path, i, text)
        except OSError:
            continue
    return hits, inert


def self_test():
    bad = [
        'const k = "AKIAABCDEFGHIJKLMNOP";',
        'key: "AIzaSyA1234567890abcdefghijklmnopqrstuv"',
        "OPENAI=sk-abcdefghijklmnopqrstuvwx",
        'apify = "apify_api_abcdefghijklmnopqrstu"',
        "t = ghp_abcdefghijklmnopqrstuvwxyz0123456789ab",
        "j = eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoic2VydmljZSJ9.abcdefghijklmnop",
        "-----BEGIN PRIVATE KEY-----",
        "DATABASE_URL=postgresql://admin:hunter2pass@db.host.co:5432/x",
        'const service_role = "abcd1234efgh5678ijkl";',
    ]
    good = [
        'const api_key = "YOUR_API_KEY_HERE";',
        "DATABASE_URL=postgresql://user:<password>@host/db",
        'password = "changeme-changeme"',
        "const slug = 'contractors/abc';",
        'token: "xxxxxxxxxxxxxxxx"',
        "Set GEMINI_API_KEY in your local .env file.",
    ]
    ok = 0
    for s in bad:
        ok += bool(scan_text("t", 1, s))
    for s in good:
        ok += not scan_text("t", 1, s)
    ok += is_env_file("site/.env") and is_env_file(".env.local") and not is_env_file(".env.example")
    total = len(bad) + len(good) + 1
    print(f"{ok} of {total} ok")
    return 0 if ok == total else 1


def main(argv):
    if argv == ["--self-test"]:
        return self_test()
    if not argv or argv[0].startswith("-"):
        print(__doc__)
        return 2
    total_hits = 0
    try:
        for repo in argv:
            hits, _ = scan_repo(repo)
            for path, line_no, kind, m3 in hits:
                print(f"HIT {repo}:{path}:{line_no} {kind} {m3}...")
            total_hits += len(hits)
    except RuntimeError as e:
        print(f"ERROR {e}")
        return 2
    print(f"SUMMARY hits={total_hits}")
    return 1 if total_hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
