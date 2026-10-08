## SAM Workflow Instructions

This project uses the SAM micro-chunk workflow. All planning, routing, and execution
artifacts live in the `plans/` directory. Read `plans/README.md` for the full spec.

### When asked to "run the next step", "continue", or similar:

1. Read `plans/state.json` → get `next_action_id`
2. If `next_action_id` starts with `Human.*`: do NOT execute. Instead, read the
   corresponding template and prepare a briefing for the human per its instructions. Stop.
3. Read `plans/templates/registry.json` → find the action entry matching `next_action_id`
4. Read the template file at the action's `template_path` — this defines your role,
   task, constraints, and exact instructions
5. Read ALL files listed in the action's `inputs` — this is your full context
6. Execute exactly what the template instructs (bounded to that one task)
7. Update the files listed in `required_outputs`, following the template's exact
   instructions. Some writes — notably `plans/STATUS.md` — are config-gated, so do
   what the template says rather than treating any output as mandatory.
8. Update `plans/state.json` with `last_action`, `next_action_id`, and `pause_type`
   as specified by the template
9. Stop. You are done when state.json is updated and all required outputs are written.
   Do not continue to the next action.

### Out-of-band actions
Actions marked `"out_of_band": true` in `registry.json` (currently `Staff.Patch`) are
invoked **by name** — e.g., "Run Staff.Patch: fix the Dependabot alerts". Run them
regardless of `next_action_id`, and **do not modify `plans/state.json`**: they sit outside
the Build, consume no Build number, and leave an in-flight Build exactly where it was.

### Validation scope (tests, lint, type checks)
Verification is required; repeating it is not. Spend expensive checks where they buy
confidence.

- **Iterative validation** — while implementing or fixing, run the narrowest checks that
  give meaningful feedback on the code you are touching (targeted tests; lint/format on
  changed files). After a local fix, re-run only those. Broaden only when the change is
  cross-cutting or targeted checks can't give confidence.
- **Checkpoint validation** — once, before an action that changed code declares its work
  done: the full suite plus the lint/format/type gates the project requires. Fix failures
  before completing. If `plans/STANDARDS.md` names the commands, use them.
- **Record it once, reuse it.** The action that ran the checkpoint records a
  `Validation:` line in its thread.md entry — commands, result, and the commit it ran
  against. Later actions (review, approval, release) do **not** re-run checks on code that
  hasn't changed since that record.
- **"Changed" means code, not commits.** Decide whether a record still holds by looking at
  which files changed since its commit (`git diff --name-only <commit>` plus uncommitted
  changes). Ignore `plans/` and anything that can't affect the checks (SAM bookkeeping,
  docs-only edits). A new commit SHA by itself means nothing.
- **If code did change, or there is no record, run the checks yourself** — the narrowest
  ones that cover the change — rather than routing back to an earlier action just to get
  them run. Only a *failure* goes back through normal routing.

### Key files
- `plans/README.md` — full SAM system spec (vocabulary, lifecycle, pause model, etc.)
- `plans/FORMATS.md` — expected structure of all instance-level files — reference when creating or updating
- `plans/config.json` — project-level workflow configuration — consult for routing decisions
- `plans/state.json` — routing source of truth (what to do next)
- `plans/templates/registry.json` — machine-readable action catalog (inputs, outputs, gates)
- `plans/templates/*.txt` — individual action prompts
- `plans/STATUS.md` — human-readable project snapshot (updated every action)

### Valid `last_action.result` values
When updating `plans/state.json`, the `last_action.result` field MUST be one of these
schema-valid enum values — do NOT use "complete", "done", "success", or any other string:

| Value | When to use |
|-------|-------------|
| `ok` | Action completed successfully (default for most actions) |
| `approved` | Review/approval action approved the artifact |
| `changes_required` | Review found issues that must be addressed |
| `blocked` | Action cannot proceed; a blocker has been added |
| `error` | Unexpected failure occurred |
| `skipped` | Action was intentionally skipped |

### Instance file hygiene
When an action creates or overwrites an instance file (BUILD.md, MILESTONE.md, STATUS.md,
BACKLOG.md, CHANGELOG.md, DECISIONS.md, STANDARDS.md, thread.md), replace all
template/placeholder content with real content. Reference `plans/FORMATS.md` for the
expected structure of each file. Do not preserve explanatory preamble from template stubs.

`plans/VISION.md` is the exception: it is the human-authored **concept brief** (the seed
for the Build) and is **read-only to every action** — read it for original intent, never
write to it. See `plans/FORMATS.md` for details.

### Multi-root workspaces
If `plans/config.json` defines `workspace.shared_repos`, this is a multi-root project
and scope-of-change routing applies. Read `plans/FORMATS.md` ("workspace block" and
"Scope-of-change routing") for the full rules. Quick reference:

- **The primary repo owns `plans/`.** No shared repo ever gets a `plans/` directory.
- **Project scope** (everything not inside a `shared_repos[].path`) → writes go to the
  primary repo's `plans/` (BUILD/MILESTONE/STATUS/BACKLOG/CHANGELOG/DECISIONS/STANDARDS/thread).
- **Shared scope** (path matches a `shared_repos[].path`) → only code edits, that repo's
  `DEPLOYMENT.md` (written by `PM.BuildRelease`), and, with prior human approval via
  `PM.ThreadMaintenance`, that repo's own `STANDARDS.md` / `DECISIONS.md` (no `plans/`
  wrapper). Project-scoped decisions *about* shared code
  stay in the primary repo's `plans/DECISIONS.md`.
- **Detection:** path match against `shared_repos[].path`. SAM never falls back to cwd
  or `"."` to infer the primary repo — the config is authoritative.
- **Promotion** of a project decision to a shared standard is proposed by
  `PM.ThreadMaintenance`, approved by the human in chat, then executed on the next run.
