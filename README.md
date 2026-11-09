# SAM (Structured AI Method) — Micro-Chunk Workflow Template

**An [mjt.pub](https://mjt.pub) project.**

SAM is a human-directed, AI-executed workflow for building software one small step at a time.

## Getting started

From your project's root (Python 3.9+, standard library only):

```bash
git clone https://github.com/michaeljthacker/sam-plans-template ../sam-plans-template
python ../sam-plans-template/plans/sam-install.py
```

Then read `plans/README.md` in your project — it's the full spec, quickstart, and reference.

SAM installs like a tool: the whole toolchain lands in your working tree, but your Git
history records only your plans. The installer writes a managed block in your `.gitignore`
so that only seven files in `plans/` are tracked — `BACKLOG.md`, `BUILD.md`, `CHANGELOG.md`,
`DECISIONS.md`, `MILESTONE.md`, `STANDARDS.md`, `VISION.md`. Everything else (prompts,
schemas, helpers, `state.json`, `thread.md`, `STATUS.md`, root `CLAUDE.md`,
`.github/copilot-instructions.md`) stays local. Rerun the installer any time; it never
overwrites your plans, state, or config. After a fresh clone of your project, run it
again to restore SAM. Later updates: `python plans/sam-update.py` (dry run) then `--apply`.

Upgrading a project from SAM 1.x: run the installer once (or `sam-update.py --apply`
twice). It offers to untrack the SAM files your repo used to commit — local copies are
kept, and history is not rewritten.

## What's in this repo

| Path | What it is |
|------|-----------|
| `plans/` | The SAM template source — installed into projects by `plans/sam-install.py` (this repo tracks all of it) |
| `tests/` | Tests for the installer/updater (`python -m unittest discover -s tests`); not installed |
| `example/` | A worked example showing SAM in use (WIP; frozen at v1.1.0–v1.2.1) |
| `DECISIONS.md` | Design decisions about SAM itself (not part of the template) |
| `TODO.md` | Development backlog for SAM itself (not part of the template) |
| `.sam-template-source` | Marker that stops the installer from ever targeting this repo |
