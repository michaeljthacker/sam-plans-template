"""sam_sync.py - shared engine behind plans/sam-install.py and plans/sam-update.py.

Not meant to be run directly. Both entry points import this module from the
SAM *source* (the template clone), so an install or update always runs the
incoming engine, never a stale copy in the target project.

What one run does, in order:
1. Sync every manifest entry (plans/sync-manifest.json `files`):
   - overwrite          system file, refreshed from the template
   - create_if_missing  instance file, scaffolded only when absent
   - stamp              plans/.sam-version, regenerated on apply
2. Write the SAM-managed block of the target's root .gitignore, derived from
   each entry's `gitignore` flag. Everything outside the block is preserved.
3. Check the effective ignore result with `git check-ignore`.
4. Find tracked files that the policy now ignores and (with consent) remove
   them from the Git index only - local files are never deleted.
5. Audit plans/config.json against plans/config.schema.json.

Standard library only.
"""

from __future__ import annotations

import datetime
import difflib
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MANIFEST_REL = "plans/sync-manifest.json"
CONFIG_REL = "plans/config.json"
SCHEMA_REL = "plans/config.schema.json"
VERSION_FILE_REL = "plans/.sam-version"
GITIGNORE_REL = ".gitignore"
TEMPLATE_MARKER_REL = ".sam-template-source"
POINTER_TEXT = "plans/agent-instructions.md"

BLOCK_BEGIN = "# BEGIN SAM MANAGED"
BLOCK_END = "# END SAM MANAGED"
SYNC_MODES = ("overwrite", "create_if_missing", "stamp")


class SamError(Exception):
    """A fatal, user-facing error. Entry points print it and exit 1."""


@dataclass(frozen=True)
class Entry:
    source: str | None
    target: str
    sync: str
    gitignore: bool
    root_bootstrap: bool = False


# --------------------------------------------------------------------------
# Manifest
# --------------------------------------------------------------------------

def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_manifest(src_root: Path) -> dict:
    path = src_root / MANIFEST_REL
    if not path.is_file():
        raise SamError(f"source is missing {MANIFEST_REL}: {src_root}")
    try:
        manifest = load_json(path)
    except json.JSONDecodeError as exc:
        raise SamError(f"{MANIFEST_REL} is not valid JSON: {exc}") from exc
    if "files" not in manifest:
        raise SamError(
            f"{MANIFEST_REL} has no `files` inventory - the source predates SAM 2.0.0. "
            "Update your SAM template clone (git pull) and rerun."
        )
    return manifest


def sam_version(manifest: dict) -> str:
    return str(manifest.get("sam_version", "unknown"))


def parse_entries(manifest: dict) -> list[Entry]:
    entries: list[Entry] = []
    seen: set[str] = set()
    for raw in manifest["files"]:
        target = raw.get("target")
        sync = raw.get("sync")
        if not isinstance(target, str) or not target:
            raise SamError(f"manifest entry has no target: {raw}")
        if target.startswith("/") or ".." in target.split("/") or "\\" in target:
            raise SamError(f"manifest target must be a relative POSIX path: {target}")
        if target in seen:
            raise SamError(f"manifest lists target twice: {target}")
        seen.add(target)
        if sync not in SYNC_MODES:
            raise SamError(f"manifest entry {target}: sync must be one of {SYNC_MODES}")
        if sync != "stamp" and not raw.get("source"):
            raise SamError(f"manifest entry {target}: sync={sync} needs a source")
        gitignore = raw.get("gitignore")
        if not isinstance(gitignore, bool):
            raise SamError(f"manifest entry {target}: gitignore must be true or false")
        if not gitignore and target.startswith("plans/") and "/" in target[len("plans/"):]:
            # `/plans/*` ignores subdirectories wholesale; Git cannot re-include
            # a file whose parent directory is excluded.
            raise SamError(
                f"manifest entry {target}: tracked plans/ files must sit directly in plans/"
            )
        entries.append(
            Entry(
                source=raw.get("source"),
                target=target,
                sync=sync,
                gitignore=gitignore,
                root_bootstrap=bool(raw.get("root_bootstrap", False)),
            )
        )
    return entries


def tracked_plan_targets(entries: list[Entry]) -> list[str]:
    """The plans/ files the policy leaves eligible for Git (the durable plans)."""
    return sorted(e.target for e in entries if not e.gitignore and e.target.startswith("plans/"))


# --------------------------------------------------------------------------
# Safety checks
# --------------------------------------------------------------------------

def check_roots(src_root: Path, dst_root: Path) -> None:
    if src_root == dst_root:
        raise SamError(
            "source and target are the same directory. Run SAM from your project root, "
            "pointing at a separate SAM template clone (an installed project's own "
            "plans/sam-install.py cannot install into itself - use the clone's copy)."
        )
    if dst_root.is_relative_to(src_root):
        raise SamError(f"target {dst_root} is inside the SAM template clone {src_root}.")
    if (dst_root / TEMPLATE_MARKER_REL).exists():
        raise SamError(
            f"target contains {TEMPLATE_MARKER_REL} - it is a SAM template source repo, "
            "which versions all SAM files and must not receive consumer ignore rules."
        )


# --------------------------------------------------------------------------
# File sync
# --------------------------------------------------------------------------

def show_diff(src_file: Path, dst_file: Path, label_src: str, label_dst: str) -> None:
    src_lines = src_file.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    dst_lines = dst_file.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    out = "".join(
        difflib.unified_diff(dst_lines, src_lines, fromfile=label_dst, tofile=label_src, n=2)
    )
    if out:
        sys.stdout.write(out if out.endswith("\n") else out + "\n")


def copy_file(src_file: Path, dst_file: Path) -> None:
    dst_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_file, dst_file)


def sync_entries(
    src_root: Path, dst_root: Path, entries: list[Entry], apply: bool, force: bool
) -> tuple[dict[str, list[str]], set[str]]:
    """Returns (summary buckets, targets kept as project-owned custom files)."""
    summary: dict[str, list[str]] = {
        k: []
        for k in ("unchanged", "created", "updated", "scaffolded", "preserved", "custom", "missing-in-source")
    }
    custom: set[str] = set()

    print("System files (refreshed from the template):")
    for e in entries:
        if e.sync != "overwrite":
            continue
        src_file, dst_file = src_root / e.source, dst_root / e.target
        if not src_file.is_file():
            print(f"  [missing in source] {e.target}")
            summary["missing-in-source"].append(e.target)
            continue
        if not dst_file.exists():
            status = "created"
        elif src_file.read_bytes() == dst_file.read_bytes():
            status = "unchanged"
        else:
            status = "updated"

        if status == "updated" and e.root_bootstrap and not force:
            # A differing root AI-instruction file may be the project's own.
            # Keep it, leave it tracked, and keep it out of the ignore block.
            text = dst_file.read_text(encoding="utf-8", errors="replace")
            hint = (
                "it already points to SAM"
                if POINTER_TEXT in text
                else f"add a line pointing the AI to {POINTER_TEXT}"
            )
            print(
                f"  [custom]    {e.target}  (differs from SAM's - kept, left tracked; "
                f"{hint}, or rerun with --force to replace it)"
            )
            summary["custom"].append(e.target)
            custom.add(e.target)
            continue

        label = {"created": "created", "updated": "updated", "unchanged": "unchanged"}[status]
        if not apply and status != "unchanged":
            label = "will create" if status == "created" else "will update"
        print(f"  [{label}] {e.target}")
        if status == "updated":
            show_diff(src_file, dst_file, f"source/{e.source}", f"target/{e.target}")
        if apply and status != "unchanged":
            copy_file(src_file, dst_file)
        summary[status].append(e.target)

    print("\nInstance files (scaffolded if absent, never overwritten):")
    for e in entries:
        if e.sync != "create_if_missing":
            continue
        dst_file = dst_root / e.target
        if dst_file.exists():
            print(f"  [preserved] {e.target}")
            summary["preserved"].append(e.target)
            continue
        src_file = src_root / e.source
        if not src_file.is_file():
            print(f"  [absent]    {e.target}  (not in template; created by SAM when needed)")
            continue
        print(f"  [{'scaffolded' if apply else 'will scaffold'}] {e.target}")
        if apply:
            copy_file(src_file, dst_file)
        summary["scaffolded"].append(e.target)

    return summary, custom


def stamp_version(dst_root: Path, manifest: dict, src_root: Path) -> None:
    payload = {
        "synced_at": datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(),
        "manifest_version": sam_version(manifest),
        "source_path": str(src_root),
    }
    path = dst_root / VERSION_FILE_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------
# .gitignore
# --------------------------------------------------------------------------

def ignored_targets(entries: list[Entry], custom: set[str]) -> list[str]:
    return [e.target for e in entries if e.gitignore and e.target not in custom]


def gitignore_block(entries: list[Entry], custom: set[str]) -> list[str]:
    lines = [BLOCK_BEGIN, "/plans/*"]
    lines += [f"!/{t}" for t in tracked_plan_targets(entries)]
    lines += [f"/{t}" for t in ignored_targets(entries, custom) if not t.startswith("plans/")]
    lines.append(BLOCK_END)
    return lines


def render_gitignore(existing: str | None, block: list[str]) -> str:
    """Return the new .gitignore text. An existing block is replaced in place
    (so its position stays stable); otherwise the block is appended at the end,
    where later-wins precedence keeps earlier project rules from defeating it.
    The file's existing newline style is preserved."""
    if not existing:
        return "\n".join(block) + "\n"
    nl = "\r\n" if "\r\n" in existing else "\n"
    lines = existing.splitlines()
    begins = [i for i, line in enumerate(lines) if line.strip() == BLOCK_BEGIN]
    ends = [i for i, line in enumerate(lines) if line.strip() == BLOCK_END]
    if len(begins) == 1 and len(ends) == 1 and begins[0] < ends[0]:
        lines[begins[0] : ends[0] + 1] = block
    elif not begins and not ends:
        if lines and lines[-1].strip():
            lines.append("")
        lines += block
    else:
        raise SamError(
            f"{GITIGNORE_REL} has malformed SAM markers (expected exactly one "
            f"'{BLOCK_BEGIN}' followed by one '{BLOCK_END}'). Fix or remove them and rerun."
        )
    return nl.join(lines) + nl


def update_gitignore(dst_root: Path, block: list[str], apply: bool) -> tuple[str, bool]:
    """Returns (status, on_disk_matches_policy)."""
    path = dst_root / GITIGNORE_REL
    existing = path.read_bytes().decode("utf-8") if path.is_file() else None
    rendered = render_gitignore(existing, block)
    print(f"\nGit ignore policy ({GITIGNORE_REL}, SAM-managed block only):")
    if existing == rendered:
        print("  [unchanged] SAM block is current")
        return "unchanged", True
    status = "created" if existing is None else "updated"
    verb = status if apply else ("will create" if existing is None else "will update")
    print(f"  [{verb}] {GITIGNORE_REL}")
    old = (existing or "").splitlines(keepends=False)
    diff = difflib.unified_diff(
        old, rendered.splitlines(), fromfile=f"target/{GITIGNORE_REL}", tofile="new", n=1, lineterm=""
    )
    for line in diff:
        print(f"    {line}")
    if apply:
        path.write_bytes(rendered.encode("utf-8"))
    return status, apply


# --------------------------------------------------------------------------
# Git index
# --------------------------------------------------------------------------

def git(dst_root: Path, *args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(dst_root), *args],
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def is_git_repo(dst_root: Path) -> bool:
    try:
        result = git(dst_root, "rev-parse", "--is-inside-work-tree")
    except FileNotFoundError:
        return False
    return result.returncode == 0 and result.stdout.strip() == "true"


def check_ignore_effective(dst_root: Path, entries: list[Entry], custom: set[str]) -> list[str]:
    """Ask Git whether each manifest target is ignored as the policy intends.
    Returns human-readable problems (empty = all good)."""
    should_ignore = set(ignored_targets(entries, custom))
    should_track = set(tracked_plan_targets(entries))
    paths = sorted(should_ignore | should_track)
    result = git(dst_root, "check-ignore", "--no-index", "-z", "--stdin", stdin="".join(p + "\0" for p in paths))
    if result.returncode not in (0, 1):
        return [f"git check-ignore failed: {result.stderr.strip()}"]
    ignored = {p for p in result.stdout.split("\0") if p}
    problems = [f"{p} should be ignored but is not" for p in sorted(should_ignore - ignored)]
    problems += [
        f"{p} should be trackable but an ignore rule matches it (check rules after the SAM block)"
        for p in sorted(should_track & ignored)
    ]
    return problems


def untrack_candidates(dst_root: Path, entries: list[Entry], custom: set[str]) -> list[str]:
    """Tracked paths that the policy classifies as ignored: anything under plans/
    except the durable plan files, plus ignored SAM targets outside plans/."""
    keep = set(tracked_plan_targets(entries))
    outside = [t for t in ignored_targets(entries, custom) if not t.startswith("plans/")]
    result = git(dst_root, "ls-files", "-z", "--", "plans", *outside)
    if result.returncode != 0:
        raise SamError(f"git ls-files failed: {result.stderr.strip()}")
    tracked = [p for p in result.stdout.split("\0") if p]
    return sorted(
        p for p in tracked if p in outside or (p.startswith("plans/") and p not in keep)
    )


def git_untrack(dst_root: Path, paths: list[str]) -> list[str]:
    """`git rm --cached` the given paths. Returns failure messages."""
    failures: list[str] = []
    for i in range(0, len(paths), 100):
        chunk = paths[i : i + 100]
        if git(dst_root, "rm", "--cached", "--quiet", "--", *chunk).returncode == 0:
            continue
        for p in chunk:  # retry one at a time to pinpoint what Git refused
            r = git(dst_root, "rm", "--cached", "--quiet", "--", p)
            if r.returncode != 0:
                reason = (r.stderr.strip().splitlines() or ["unknown error"])[0]
                failures.append(f"{p}: {reason}")
    return failures


def handle_index(
    dst_root: Path,
    entries: list[Entry],
    custom: set[str],
    gitignore_current: bool,
    apply: bool,
    untrack: bool,
) -> dict[str, Any]:
    info: dict[str, Any] = {"repo": False, "candidates": [], "untracked": [], "failures": [], "problems": []}
    print("\nGit index:")
    if not is_git_repo(dst_root):
        print("  not a Git repository (or git not installed) - policy written for future use; "
              "index migration skipped")
        return info
    info["repo"] = True

    if gitignore_current:
        problems = check_ignore_effective(dst_root, entries, custom)
        info["problems"] = problems
        if problems:
            print("  WARN ignore rules do not produce the intended result:")
            for p in problems:
                print(f"    - {p}")
        else:
            print("  ignore rules verified with git check-ignore")

    candidates = untrack_candidates(dst_root, entries, custom)
    info["candidates"] = candidates
    if not candidates:
        print("  no tracked SAM files need untracking")
        return info

    print(f"  {len(candidates)} tracked file(s) are now SAM-local and should leave the index:")
    for p in candidates:
        print(f"    {p}")

    if not apply:
        print("  (on apply you will be offered to untrack these; local files are kept)")
        return info

    proceed = untrack
    if not proceed and sys.stdin.isatty():
        answer = input(
            f"  Untrack these {len(candidates)} file(s)? Local copies are kept. [y/N] "
        ).strip().lower()
        proceed = answer in ("y", "yes")
    elif not proceed:
        print("  non-interactive run: index left unchanged. Rerun with --untrack to remove "
              "them from the index (local files are kept).")
        return info
    if not proceed:
        print("  skipped - index left unchanged (rerun with --untrack any time)")
        return info

    failures = git_untrack(dst_root, candidates)
    info["failures"] = failures
    info["untracked"] = [p for p in candidates if not any(f.startswith(p + ":") for f in failures)]
    print(f"  untracked {len(info['untracked'])} file(s); local copies kept. Nothing was committed -")
    print("  review `git status` and commit the removals together with .gitignore.")
    if failures:
        print("  WARN Git refused to untrack (resolve, then rerun with --untrack):")
        for f in failures:
            print(f"    - {f}")
    return info


# --------------------------------------------------------------------------
# Config audit
# --------------------------------------------------------------------------

def audit_config(config_path: Path, schema_path: Path) -> list[tuple[str, str]]:
    """Validate config.json against config.schema.json (top-level keys only).

    REQUIRED - schema marks key as required and it is missing
    ERROR    - value violates enum
    WARN     - new optional key (using default) or unknown key
    """
    if not schema_path.is_file():
        return [("ERROR", f"{SCHEMA_REL} not found")]
    if not config_path.is_file():
        return [("WARN", f"{CONFIG_REL} not found - SAM will use schema defaults.")]

    schema = load_json(schema_path)
    try:
        config = load_json(config_path)
    except json.JSONDecodeError as exc:
        return [("ERROR", f"{CONFIG_REL} is not valid JSON: {exc}")]

    issues: list[tuple[str, str]] = []
    props = schema.get("properties", {})
    keys = {k for k in config if k != "$schema"}

    for key in sorted(set(schema.get("required", [])) - keys):
        issues.append(("REQUIRED", f"missing required key '{key}'"))
    for key in sorted(props):
        if key == "$schema":
            continue
        prop = props[key]
        if key not in keys:
            default = prop.get("default")
            if default is None and prop.get("type") == "object":
                continue
            issues.append(("WARN", f"'{key}' missing - schema added this key (default: {default!r})"))
            continue
        enum = prop.get("enum")
        if enum is not None and config[key] not in enum:
            issues.append(("ERROR", f"'{key}' = {config[key]!r} - must be one of {enum}"))
    for key in sorted(keys - set(props)):
        issues.append(("WARN", f"unknown key '{key}' - schema no longer defines this"))
    return issues


def print_audit(issues: list[tuple[str, str]]) -> bool:
    print("\nConfig audit (plans/config.json vs plans/config.schema.json):")
    if not issues:
        print("  clean - no schema drift detected")
        return False
    width = max(len(s) for s, _ in issues)
    for severity, message in issues:
        print(f"  {severity.ljust(width)}  {message}")
    return True


# --------------------------------------------------------------------------
# Summary + orchestration
# --------------------------------------------------------------------------

def print_summary(summary: dict[str, list[str]], gi_status: str, index: dict[str, Any], apply: bool) -> None:
    label = {
        "unchanged": "unchanged",
        "created": "created" if apply else "will create",
        "updated": "updated" if apply else "will update",
        "scaffolded": "scaffolded" if apply else "will scaffold",
        "preserved": "preserved",
        "custom": "kept custom",
        "missing-in-source": "missing in source",
    }
    detailed = {"created", "updated", "scaffolded", "custom", "missing-in-source"}
    width = max(len(v) for v in label.values()) + 1
    print("\nSummary")
    for key, text in label.items():
        items = summary.get(key, [])
        if not items and key in ("custom", "missing-in-source"):
            continue
        line = f"  {(text + ':').ljust(width)} {len(items):>3}"
        if items and key in detailed:
            shown = ", ".join(items[:6]) + (f", +{len(items) - 6} more" if len(items) > 6 else "")
            line += f"   ({shown})"
        elif items and key == "preserved":
            line += "   (instance files, untouched)"
        print(line)
    gi_text = gi_status if (apply or gi_status == "unchanged") else f"will be {gi_status}"
    print(f"  {'.gitignore:'.ljust(width)} {gi_text}")
    if not index["repo"]:
        print(f"  {'git index:'.ljust(width)} skipped (not a Git repository)")
    elif index["untracked"] or index["failures"]:
        print(f"  {'git index:'.ljust(width)} untracked {len(index['untracked'])}, "
              f"failed {len(index['failures'])}")
    elif index["candidates"]:
        print(f"  {'git index:'.ljust(width)} {len(index['candidates'])} SAM file(s) still tracked")
    else:
        print(f"  {'git index:'.ljust(width)} clean")


def run(
    src_root: Path,
    dst_root: Path,
    *,
    mode: str,
    apply: bool,
    untrack: bool = False,
    force: bool = False,
) -> int:
    """Shared install/update flow. Exit codes:
    0 success; 2 finished but needs attention (config audit issues, ignore rules
    not effective, or files Git refused to untrack). Raises SamError on fatal errors."""
    # Diffs include non-ASCII text; never crash on a legacy console encoding (cp1252).
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")
    src_root, dst_root = src_root.resolve(), dst_root.resolve()
    check_roots(src_root, dst_root)
    manifest = load_manifest(src_root)
    entries = parse_entries(manifest)

    print(f"SAM {mode}")
    print(f"Source:  {src_root}")
    print(f"Target:  {dst_root}")
    print(f"Version: {sam_version(manifest)}")
    print(f"Mode:    {'APPLY' if apply else 'DRY-RUN'}\n")

    summary, custom = sync_entries(src_root, dst_root, entries, apply, force)

    for e in entries:
        if e.sync == "stamp":
            print(f"  [{'stamped' if apply else 'will stamp'}] {e.target}  (SAM {sam_version(manifest)})")
            if apply:
                stamp_version(dst_root, manifest, src_root)

    gi_status, gi_current = update_gitignore(dst_root, gitignore_block(entries, custom), apply)
    index = handle_index(dst_root, entries, custom, gi_current, apply, untrack)

    schema_root = dst_root if apply else src_root
    audit_issues = print_audit(audit_config(dst_root / CONFIG_REL, schema_root / SCHEMA_REL))

    print_summary(summary, gi_status, index, apply)
    if not apply:
        hint = "--apply" if mode == "update" else "without --dry-run"
        print(f"\n(dry run - rerun {hint} to write changes)")

    attention = audit_issues or index["problems"] or index["failures"]
    return 2 if attention else 0
