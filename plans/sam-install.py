#!/usr/bin/env python3
"""sam-install.py - install (or reinstall) SAM into the current project.

Run from the TARGET project's root, using a cloned sam-plans-template as the
source. The source is located from this file's own path:

    git clone https://github.com/michaeljthacker/sam-plans-template ../sam-plans-template
    python ../sam-plans-template/plans/sam-install.py

Applies immediately (use --dry-run to preview). Safe to rerun: system files
are refreshed, missing instance files are scaffolded, and existing plans,
state, and config are never overwritten. Also writes the SAM-managed block of
the project's .gitignore and offers to untrack SAM files Git still tracks.

Options:
    --dry-run   preview only; write nothing
    --untrack   untrack SAM-local files without prompting (for scripts/CI)
    --force     replace a project's own root CLAUDE.md /
                .github/copilot-instructions.md with SAM's

Exit codes: 0 success; 1 fatal error; 2 finished but needs attention
(config audit issues, ineffective ignore rules, or untrack failures).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # keep the template clone free of __pycache__

SOURCE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SOURCE_ROOT / "plans"))

import sam_sync  # noqa: E402  (imported from this script's own SAM source)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install SAM into the current directory from this SAM template clone."
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview only; write nothing.")
    parser.add_argument("--untrack", action="store_true",
                        help="Untrack SAM-local files from Git without prompting.")
    parser.add_argument("--force", action="store_true",
                        help="Replace custom root CLAUDE.md / .github/copilot-instructions.md.")
    args = parser.parse_args()
    try:
        return sam_sync.run(
            SOURCE_ROOT,
            Path.cwd(),
            mode="install",
            apply=not args.dry_run,
            untrack=args.untrack,
            force=args.force,
        )
    except sam_sync.SamError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
