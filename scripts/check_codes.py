#!/usr/bin/env python3
"""Checks that the LinkML schema can't express for tools/*.yaml.

- file name (without .yaml) equals `id`
- every use_cases[].code exists in the latest release of the pragmaticBIM reference
- `own: true` only in files changed by a maintainer (pull requests only)
- warning: `last_checked` older than 12 months

Environment:
  REFERENCE_DIR        use this reference checkout instead of downloading the release
  REFERENCE_CACHE_DIR  where the downloaded release is cached (default: .cache/reference)
  GITHUB_TOKEN         optional, avoids GitHub API rate limits
  PR_AUTHOR            pull request author login; enables the `own` check
  PR_BASE_SHA          base commit of the pull request; limits the `own` check to changed files
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REFERENCE_REPO = "pragmaticBIM/pragmaticbim-reference"
STALE_AFTER_DAYS = 365
IN_ACTIONS = os.environ.get("GITHUB_ACTIONS") == "true"


class Report:
    def __init__(self) -> None:
        self.errors = 0
        self.warnings = 0

    def error(self, path: Path | str, msg: str) -> None:
        self.errors += 1
        self._emit("error", path, msg)

    def warning(self, path: Path | str, msg: str) -> None:
        self.warnings += 1
        self._emit("warning", path, msg)

    @staticmethod
    def _emit(level: str, path: Path | str, msg: str) -> None:
        rel = Path(path).relative_to(ROOT) if Path(path).is_relative_to(ROOT) else Path(path)
        if IN_ACTIONS:
            print(f"::{level} file={rel}::{msg}")
        else:
            print(f"{rel}: {level}: {msg}")


def github_get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": "pragmaticbim-tools-check"})
    if token := os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def codes_from_dir(reference: Path) -> set[str]:
    codes = set()
    for path in (reference / "workflows").rglob("*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if isinstance(data, dict) and data.get("code"):
            codes.add(str(data["code"]))
    return codes


def reference_codes() -> tuple[str, set[str]]:
    if local := os.environ.get("REFERENCE_DIR"):
        return f"local checkout {local}", codes_from_dir(Path(local))

    release = json.loads(github_get(f"https://api.github.com/repos/{REFERENCE_REPO}/releases/latest"))
    tag = release["tag_name"]
    cache_dir = Path(os.environ.get("REFERENCE_CACHE_DIR", ROOT / ".cache" / "reference"))
    cache_file = cache_dir / f"codes-{tag}.json"
    if cache_file.exists():
        return tag, set(json.loads(cache_file.read_text()))

    codes = set()
    with tarfile.open(fileobj=io.BytesIO(github_get(release["tarball_url"])), mode="r:gz") as tar:
        for member in tar.getmembers():
            parts = member.name.split("/")
            if member.isfile() and len(parts) >= 3 and parts[1] == "workflows" and member.name.endswith(".yaml"):
                data = yaml.safe_load(tar.extractfile(member).read()) or {}
                if isinstance(data, dict) and data.get("code"):
                    codes.add(str(data["code"]))
    if not codes:
        raise RuntimeError(f"no use case codes found in {REFERENCE_REPO} release {tag}")
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(sorted(codes)))
    return tag, codes


def maintainers() -> set[str]:
    handles = set()
    path = ROOT / "MAINTAINERS"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if line:
                handles.add(line.lstrip("@").lower())
    codeowners = ROOT / ".github" / "CODEOWNERS"
    if codeowners.exists():
        for line in codeowners.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0]
            handles.update(h.lstrip("@").lower() for h in line.split()[1:] if h.startswith("@") and "/" not in h)
    return handles


def changed_files(base_sha: str) -> set[Path] | None:
    try:
        out = subprocess.run(["git", "diff", "--name-only", "--diff-filter=AMR", f"{base_sha}...HEAD"],
                             cwd=ROOT, check=True, capture_output=True, text=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return {(ROOT / line).resolve() for line in out.splitlines() if line}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="*", type=Path, help="tool files (default: tools/*.yaml)")
    args = parser.parse_args()

    files = [p.resolve() for p in args.files] or sorted((ROOT / "tools").glob("*.yaml"))
    report = Report()

    try:
        source, known_codes = reference_codes()
    except Exception as exc:  # network or API failure must fail the check, not pass silently
        report.error("scripts/check_codes.py", f"could not read use case codes from {REFERENCE_REPO}: {exc}")
        return 1
    print(f"Reference: {REFERENCE_REPO} {source} ({len(known_codes)} use case codes)")

    pr_author = (os.environ.get("PR_AUTHOR") or "").lower()
    allowed = maintainers()
    changed = changed_files(os.environ["PR_BASE_SHA"]) if os.environ.get("PR_BASE_SHA") else None
    today = dt.date.today()

    for path in files:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            report.error(path, f"invalid YAML: {exc}")
            continue
        if not isinstance(data, dict):
            report.error(path, "file must contain one tool mapping")
            continue

        if data.get("id") != path.stem:
            report.error(path, f"id '{data.get('id')}' must equal the file name '{path.stem}'")

        seen = set()
        for link in data.get("use_cases") or []:
            code = (link or {}).get("code")
            if code in seen:
                report.error(path, f"use case {code} is listed twice")
            seen.add(code)
            if code and code not in known_codes:
                report.error(path, f"use case code {code} does not exist in {REFERENCE_REPO} {source}")

        if data.get("own") is True and pr_author and (changed is None or path in changed):
            if pr_author not in allowed:
                report.error(path, f"own: true is reserved for abstract ag; @{pr_author} is not in MAINTAINERS")

        last_checked = data.get("last_checked")
        if isinstance(last_checked, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", last_checked):
            last_checked = dt.date.fromisoformat(last_checked)
        if isinstance(last_checked, dt.date) and (today - last_checked).days > STALE_AFTER_DAYS:
            report.warning(path, f"last_checked {last_checked} is older than 12 months; please re-check the entry")

    print(f"Checked {len(files)} files: {report.errors} errors, {report.warnings} warnings")
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
