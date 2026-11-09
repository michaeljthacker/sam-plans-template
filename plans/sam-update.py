#!/usr/bin/env python3
"""sam-update.py - update an installed SAM from a SAM template clone.

Usage (from the project root):
    python plans/sam-update.py [SOURCE_PATH] [--apply] [--untrack] [--force]

SOURCE_PATH falls back to the SAM_TEMPLATE_PATH environment variable, then to
the source_path recorded in plans/.sam-version by the last install/update.

Dry-run by default; --apply writes. The sync engine (plans/sam_sync.py) is
loaded from the SOURCE, so an update always runs the incoming logic rather
than this project's possibly older copy.

Behavior (see sam_sync.py for details):
- System files are refreshed (diffs shown); instance files (plans, state,
  config, thread) are scaffolded if absent and never overwritten.
- plans/.sam-version is stamped on --apply.
- The SAM-managed .gitignore block is reconciled with the manifest.
- Tracked files the policy now ignores are reported; on --apply you are
  offered to untrack them (index only - local files kept). Non-interactive
  runs need --untrack to do this.
- plans/config.json is audited against the incoming config.schema.json.

Exit codes: 0 success; 1 fatal error; 2 finished but needs attention
(config audit issues, ineffective ignore rules, or untrack failures).
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # keep the template clone free of __pycache__

VERSION_FILE_REL = "plans/.sam-version"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def resolve_source(arg_source: str | None, dst_root: Path) -> Path:
    src = arg_source or os.environ.get("SAM_TEMPLATE_PATH")
    origin = "argument" if arg_source else "SAM_TEMPLATE_PATH"
    if not src:
        version_file = dst_root / VERSION_FILE_REL
        if version_file.is_file():
            try:
                src = json.loads(version_file.read_text(encoding="utf-8")).get("source_path")
            except json.JSONDecodeError:
                src = None
            origin = VERSION_FILE_REL
    if not src:
        fail("no SAM source found. Pass the path to your sam-plans-template clone, "
             "or set SAM_TEMPLATE_PATH.")
    src_path = Path(src).expanduser().resolve()
    if not src_path.is_dir():
        fail(f"SAM source ({origin}) is not a directory: {src_path}. "
             "Pass the path to your sam-plans-template clone.")
    if not (src_path / "plans" / "sam_sync.py").is_file():
        fail(f"{src_path} has no plans/sam_sync.py - it is not a SAM template clone, or it "
             "predates SAM 2.0.0 (git pull it and rerun).")
    return src_path


def load_engine(src_root: Path):
    plans_dir = src_root / "plans"
    sys.path.insert(0, str(plans_dir))
    sys.modules.pop("sam_sync", None)
    engine = importlib.import_module("sam_sync")
    if Path(engine.__file__).resolve().parent != plans_dir.resolve():
        fail(f"loaded sam_sync from {engine.__file__}, expected {plans_dir}")
    return engine


def main() -> int:
    parser = argparse.ArgumentParser(description="Update SAM in the current project.")
    parser.add_argument("source", nargs="?", default=None,
                        help="Path to a SAM template clone (default: SAM_TEMPLATE_PATH, "
                             "then the path recorded in plans/.sam-version).")
    parser.add_argument("--apply", action="store_true",
                        help="Write changes. Without this flag, only preview.")
    parser.add_argument("--untrack", action="store_true",
                        help="With --apply: untrack SAM-local files from Git without prompting.")
    parser.add_argument("--force", action="store_true",
                        help="Replace custom root CLAUDE.md / .github/copilot-instructions.md.")
    args = parser.parse_args()

    dst_root = Path.cwd().resolve()
    src_root = resolve_source(args.source, dst_root)
    engine = load_engine(src_root)
    try:
        return engine.run(src_root, dst_root, mode="update", apply=args.apply,
                          untrack=args.untrack, force=args.force)
    except engine.SamError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
