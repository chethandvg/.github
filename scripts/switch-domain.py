# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Chethan Dandebala Venkatarama
"""Rewrite old site links across every local repo after a domain switch.

    python scripts/switch-domain.py https://chethandvg.github.io https://example.org
    python scripts/switch-domain.py https://chethandvg.github.io https://example.org --apply

Without --apply it only reports what would change. With --apply it edits the
files on a new branch, `switch-domain`, and commits in each repo, then prints
the push commands. It never pushes. site.json in this repo is updated too,
with the old host added to previous_hosts so the site-url check keeps catching
stale links.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout


def rewrite(repo: Path, old: str, new: str, apply: bool) -> list[str]:
    changed = []
    for rel in filter(None, git(repo, "ls-files", "-z").split("\0")):
        path = repo / rel
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if old in text:
            changed.append(rel)
            if apply:
                path.write_text(text.replace(old, new), encoding="utf-8")
    return changed


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("old", help="current site URL, e.g. https://chethandvg.github.io")
    ap.add_argument("new", help="new site URL, e.g. https://example.org")
    ap.add_argument("--repos-dir", type=Path, default=HERE.parent, help="folder that holds the local repos")
    ap.add_argument("--apply", action="store_true", help="edit files and commit on a switch-domain branch")
    a = ap.parse_args()
    old, new = a.old.rstrip("/"), a.new.rstrip("/")

    if a.apply:
        site_file = HERE / "site.json"
        site = json.loads(site_file.read_text(encoding="utf-8"))
        old_host = old.split("://", 1)[-1]
        site["previous_hosts"] = sorted({*site.get("previous_hosts", []), old_host})
        site["site_url"] = new
        site_file.write_text(json.dumps(site, indent=2) + "\n", encoding="utf-8")

    registry = json.loads((HERE / "registry.json").read_text(encoding="utf-8"))
    pending = []
    for entry in registry["repos"]:
        repo = a.repos_dir / entry["name"]
        if not (repo / ".git").exists():
            continue
        if a.apply:
            git(repo, "switch", "-c", "switch-domain")
        files = rewrite(repo, old, new, a.apply)
        if files:
            print(f"{entry['name']}: {len(files)} file(s): {', '.join(files)}")
            if a.apply:
                git(repo, "commit", "-am", f"Move site links from {old} to {new}")
                pending.append(entry["name"])
        elif a.apply:
            git(repo, "switch", "-")
            git(repo, "branch", "-d", "switch-domain")
    if a.apply and pending:
        print("\nReview each branch, then push and open a pull request:")
        for name in pending:
            print(f"  git -C {a.repos_dir / name} push -u origin switch-domain && gh pr create --repo chethandvg/{name} --fill")
    return 0


if __name__ == "__main__":
    sys.exit(main())
