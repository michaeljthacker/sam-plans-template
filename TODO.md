# SAM v0 — Implementation Backlog

Prioritized work to complete SAM v0.
Future chat sessions: read `DECISIONS.md` for rationale, `plans/README.md` for the spec, then pick up from here.

---

## Status key
- [ ] Not started
- [~] In progress
- [x] Done

---

## P0 — Must complete for a working v0

- [x] Create root `DECISIONS.md` capturing all system-design decisions
- [x] Create root `TODO.md` (this file)
- [x] Update `plans/README.md` to reflect all finalized decisions as the canonical spec
- [x] Rename SUBTASK → STEP in hierarchy, all files, and vocabulary section
- [x] Apply two-segment naming (`Staff.DraftQuestions`, `Principal.CodeReview`, etc.) across all files, templates, and registry
- [x] Define the complete v0 action set (16 actions — see `registry.json`):
  - **Build initialization:**
    - `Product.ProductVision` — generate root README + BUILD.md from human's idea
    - `Principal.BuildReview` — review BUILD.md for feasibility/constraints
  - **Milestone planning:**
    - `Principal.MilestonePlan` — draft MILESTONE.md with phases/steps/acceptance criteria
    - `Human.ApproveMilestone` — human reviews and approves scope
  - **Phase execution (inner loop):**
    - `Staff.DraftQuestions`
    - `Principal.AnswerQuestions`
    - `Staff.ImplementationExecution`
    - `Principal.CodeReview`
    - `Staff.ReviewReconciliation`
    - `PM.StatusUpdate` — update STATUS/BACKLOG/CHANGELOG
    - `Writer.DocumentationUpdate` — update docs (optional/skippable)
    - `Human.PhaseApproval` — human confirms phase, triggers commit + advance
  - **Transitions:**
    - `PM.AdvancePhase` — increment phase_id, set up next DraftQuestions cycle
    - `PM.MilestoneCloseout` — close milestone, update BACKLOG/CHANGELOG, trigger ThreadMaintenance
  - **Utilities:**
    - `PM.ThreadMaintenance`
    - `Human.ResolveBlocker`
- [x] Complete `registry.json` with all 16 actions, inputs, outputs, and gates (7 ready, 9 TODO templates)
- [x] Rename existing template files to two-segment naming (old `Engineer_*` / `ProjectManager_*` files removed)
- [x] Update existing template content with new naming convention and `pause_type`
- [x] Merge `PROMPTS.md` into `README.md` (eliminated redundant file)
- [x] Create `plans/copilot-instructions.md` — AI bootstrap so human can just say "run the next step"
- [x] Write missing templates for new actions (9 remaining):
  - `Product_ProductVision.txt`
  - `Principal_BuildReview.txt`
  - `Principal_MilestonePlan.txt`
  - `Human_ApproveMilestone.txt`
  - `PM_StatusUpdate.txt`
  - `Writer_DocumentationUpdate.txt`
  - `Human_PhaseApproval.txt`
  - `PM_AdvancePhase.txt`
  - `PM_MilestoneCloseout.txt`

## P1 — Important for usability

- [x] Replace `needs_human` with `pause_type: "continue" | "decision"` in state.json and all templates
- [x] Add quickstart/bootstrap section to `plans/README.md` showing the copy-and-go sequence
- [x] Document error semantics in README: unexpected failure → `Human.ResolveBlocker` + blocker entry; expected failures handled within the action
- [x] Make BUILD.md and MILESTONE.md outputs of early-lifecycle actions rather than manual fill-in templates (depends on `Product_ProductVision.txt` and `Principal_MilestonePlan.txt` being written)
- [x] Define `state.json` JSON Schema (required fields, valid values for `result`, `pause_type`, blocker structure, context structure)

## P2 — Polish and completeness

- [x] Sharpen DECISIONS vs. STANDARDS distinction with one-sentence heuristic in each template file
- [x] Add STANDARDS.md placeholder section for branching convention
- [x] Add single-threaded execution statement to README
- [x] Note that `thread.md` is AI-readable, not machine-parseable (documented in README)
- [x] Clean up "TASK is reserved" vocabulary note (STEP replaces SUBTASK; README updated)
- [x] Build a worked example in `example/` showing one full phase cycle with realistic file contents

## v1.1.0 — Completed (2026-04-04)

Based on feedback from initial usage. See D-017 through D-020.

- [x] Fix code review flow: ReviewReconciliation always runs after CodeReview (D-017)
  - Principal.CodeReview APPROVED now routes to Staff.ReviewReconciliation
  - Staff.ReviewReconciliation triages SUGGESTED items (implement or log to BACKLOG)
  - Targeted re-review if code was changed; straight to PM.StatusUpdate if not
- [x] thread.md is append-only log (D-018)
  - Removed structured sections; each action appends dated entry
  - Updated all templates that write to thread.md (DraftQuestions, AnswerQuestions, ImplementationExecution, CodeReview, ReviewReconciliation)
  - PM.ThreadMaintenance is sole pruner
- [x] Created plans/FORMATS.md (D-019)
  - Single source of truth for instance file structure, purpose, and ownership
  - Stripped verbose "About this file" preamble from all instance stubs
- [x] PM.ThreadMaintenance triggered mid-lifecycle (D-020)
  - PM.StatusUpdate conditionally routes to ThreadMaintenance via context.notes handoff
- [x] Moved bootstrap questions from thread.md to Product.ProductVision template
- [x] Updated registry.json (BACKLOG.md added to ReviewReconciliation inputs)
- [x] Updated plans/README.md (lifecycle table, thread management, system-level file list)
- [x] Updated plans/copilot-instructions.md (FORMATS.md reference, instance file hygiene rule)

---

## v1.2.0 — Completed (2026-04-05)

Configurable process weight via `plans/config.json`. 5 configurable knobs (4 routing, 2 gate strictness) plus Q&A self-skip logic. All changes are routing/behavioral — no schema or structural rework. See D-021 for full rationale.

### Phase A — Config infrastructure

- [x] Create `plans/config.schema.json` — JSON Schema (draft-07) for all 5 config keys with enums, defaults, descriptions
- [x] Create `plans/config.json` — instance file with `$schema` ref and all defaults
- [x] Update `plans/FORMATS.md` — add `config.json` section

### Phase B — System docs & registry

- [x] Update `plans/README.md` — config.json in instance-level list, config.schema.json in system-level list, Configuration section, Configurable? column in phase execution table
- [x] Update `plans/copilot-instructions.md` — add `plans/config.json` to "Key files"
- [x] Update `plans/templates/registry.json` — add `plans/config.json` to inputs for 5 actions; also removed `thread.md` from DraftQuestions `required_outputs` (self-skip compatibility)

### Phase C — Routing template updates

- [x] Update `Staff_ImplementationExecution.txt` — config-aware `code_review` routing
- [x] Update `PM_StatusUpdate.txt` — config-aware `documentation_update` + `formal_approval` decision tree
- [x] Update `Writer_DocumentationUpdate.txt` — config-aware `formal_approval` routing with `pause_type` adjustment
- [x] Update `Staff_ReviewReconciliation.txt` — config-aware `re_review_trigger` routing

### Phase D — Behavioral template updates

- [x] Update `Principal_CodeReview.txt` — `review_strictness` parameter (strict/balanced/pragmatic)
- [x] Update `Staff_DraftQuestions.txt` — self-skip logic when no meaningful questions

### Bug fixes found during review

- [x] Fix `PM_ThreadMaintenance.txt` — `pause_type` was "unchanged" which broke when routing through TM to `Human.PhaseApproval`; now explicitly sets based on whether next action is `Human.*` (D-022)
- [x] Fix `registry.json` — removed `thread.md` from `Staff.DraftQuestions` `required_outputs` since self-skip path doesn't write to it

### Verification

- [x] Validate `config.json` against `config.schema.json` (schema validation passes, additionalProperties blocks, enum validation blocks)
- [x] Routing scenario walk-through: full process, minimal, milestone-gated — no dead ends
- [x] DraftQuestions self-skip routes to valid `next_action_id` (in schema enum)
- [x] `re_review_trigger=auto` doesn't create dead ends
- [x] Every updated template specifies "if config.json missing or key absent, use default"
- [x] registry.json has `plans/config.json` in all 5 action inputs

---

## v1.2.1 — Completed (2026-04-09)

- [x] Added `plans/next.ps1` helper script — reads state.json, copies "Run the next action: B1-M1-P1 Action.ID" to clipboard for descriptive chat names

---

## v1.3.0 — Completed (2026-04-17)

Bug fixes and usability improvements surfaced by real-world usage (discussion-guide builder, wordsearch app).

### Bug: state.json `last_action.result` schema violations

- [x] Audit all templates for correct `last_action.result` values — AI keeps writing `complete` instead of the schema-valid enum (`ok`, `approved`, `changes_required`, `blocked`, `error`, `skipped`)
- [x] Add explicit reminder in `plans/copilot-instructions.md` listing valid `result` values
- [x] Add result-value guidance to the `state.json` section of `plans/FORMATS.md`

### Quickstart guide: clarify project idea goes in thread.md

- [x] Update quickstart in `plans/README.md` step 3: explicitly say "Write your project idea in `plans/thread.md`" (or provide a detailed description — whatever you have). Users keep putting descriptions in separate files because it's not obvious that `Product.ProductVision` reads from `thread.md`
- [x] Update `plans/README.md` "Expected lifecycle" section 1 — change "Human provides project idea" to "Human writes project idea in `plans/thread.md`"

### PM.ThreadMaintenance config-awareness audit

- [x] Audit `PM_ThreadMaintenance.txt` against `config.json` settings — ensure it doesn't prune content that's still needed (e.g., don't delete code review notes from phases 1–2 if `code_review=every_milestone` means the review hasn't happened yet)
- [x] Check other templates for similar config-timing mismatches introduced in v1.2.0

### BACKLOG hygiene

- [x] Add explicit rule to FORMATS.md: "BACKLOG tracks future work items only. Do not use BACKLOG for in-progress status, remaining tasks in the current phase, or implementation details. Those belong in state.json (e.g., `context.notes`) and thread.md respectively."
- [x] Review BACKLOG references in templates (PM.StatusUpdate, PM.MilestoneCloseout, Staff.ReviewReconciliation) to reinforce correct usage

---

## Multi-root workspace awareness — Planned

Foundational support for SAM operating across multiple repos in a VS Code multi-root
workspace (e.g., a frontend project repo plus a shared backend repo such as `mjt.pub`).
Only the primary repo owns `plans/`; shared repos receive durable, platform-level
artifact updates (code, `STANDARDS.md`, `DECISIONS.md`) without a `plans/` wrapper.

### Workspace config

- [x] Add a `workspace` block to `plans/config.schema.json`:
  - `primary_repo`: `{ name, path, owns_plans: true }` — the repo that owns `plans/`
  - `shared_repos[]`: `[{ name, path, role }]` — repos receiving code + standards/decisions updates
  - `path` accepts absolute or workspace-relative paths; SAM never infers the primary repo from cwd or `"."`
  - Single-repo projects omit `shared_repos`
- [x] Update `plans/config.json` with a default `workspace` block (primary only, empty `shared_repos`)
- [x] Update `plans/FORMATS.md` `config.json` section to document the new block and the explicit-identification rule

### Artifact routing

- [x] Document scope-of-change routing in `plans/FORMATS.md` and agent prompts:
  - Default: all planning artifacts go to `primary_repo/plans/`
  - Shared-repo writes are limited to: code under `shared_repos[].path`, plus
    `shared_repos[].path/STANDARDS.md` and `shared_repos[].path/DECISIONS.md` (no `plans/` wrapper)
  - Project-scoped decisions *about* shared code stay in `primary_repo/plans/DECISIONS.md`
- [x] Detection rule: scope is determined by path match against `shared_repos[].path`.
  Edits inside a shared-repo path are shared scope; everything else is project scope.
  `.code-workspace` may inform context but is not authoritative

### Escalation: project decision → shared standard

No automatic promotion and no new actions. `PM.ThreadMaintenance` proposes promotion
candidates inline during its normal pruning pass; the human approves (or rejects) in
the chat, and ThreadMaintenance carries out (or skips) the shared-repo write — all
within a single Role.Task action.

- [x] Update `PM_ThreadMaintenance.txt` so that when it encounters a primary-repo
  DECISIONS/STANDARDS entry whose rationale generalizes, it surfaces a promotion
  proposal in the chat (entry text + target shared repo + brief justification) and
  waits for human approval before writing to the shared repo
- [x] Spec the proposal payload (entry, source path, proposed target path, rationale)
  and the approval/rejection responses ThreadMaintenance must accept
- [x] On approval: ThreadMaintenance appends to the shared repo's `STANDARDS.md` /
  `DECISIONS.md` and removes/marks the source entry in the primary repo as appropriate.
  On rejection: the entry stays in the primary repo unchanged

### Templates and instructions

- [x] Update prompts that may write to DECISIONS/STANDARDS (`Principal.AnswerQuestions`,
  `PM.ThreadMaintenance`, `Staff.ReviewReconciliation`) to consult `workspace.shared_repos`,
  classify scope, and route writes accordingly
- [x] Update `Staff.ImplementationExecution` to flag shared-repo edits in `thread.md`
  with an explicit "shared scope" note
- [x] Update `plans/agent-instructions.md`, `plans/copilot-instructions.md`, root
  `.github/copilot-instructions.md`, and root `CLAUDE.md` with multi-root rules and
  the "primary repo owns `plans/`" invariant
  - Updated `plans/agent-instructions.md`. `plans/copilot-instructions.md` and
    `plans/CLAUDE.md` are one-line pointers to `agent-instructions.md`, so the rules
    flow through to the `.github/copilot-instructions.md` and root `CLAUDE.md` copies
    that quickstart deploys into target projects

### Documentation

- [x] Add a top-level `WORKSPACE.md` (or new section in `plans/README.md` — decide during
  implementation) explaining multi-root setup, config example, and routing rules
  - Chose a "Multi-root workspaces" section in `plans/README.md` over a separate file —
    keeps the SAM doc surface inside `plans/`
- [x] Update `plans/README.md` quickstart to mention workspace config for multi-root projects

### Verification

- [x] Validate updated `config.json` against schema for both single-repo and multi-root cases
  - Validated with ajv-cli (draft-07): shipped default and a realistic multi-root config
    both pass; confirmed rejections for `owns_plans: false`, empty `path`, and additional
    properties under `primary_repo`
- [x] Walk a multi-repo implementation scenario: a phase touches both repos — confirm
  artifact routing (project DECISIONS for project-scoped findings, shared DECISIONS only
  after escalation + approval)
- [x] Walk an escalation scenario end-to-end: AI proposes promotion → Human approves →
  entry lands in the shared repo's `STANDARDS.md` / `DECISIONS.md`

---

## DECISIONS / STANDARDS discipline — Planned

Tighten what gets recorded in `DECISIONS.md` / `STANDARDS.md`. Current behavior produces
low-signal entries (e.g., "we chose not to add a flag to this function") that drown out
durable rationale. Enforce structurally: every entry requires a "Why this matters
long-term" line; if rationale is weak or absent, the entry shouldn't exist.

### Recording rule

- [ ] Add the refined rule to the DECISIONS and STANDARDS sections of `plans/FORMATS.md`:
  > Record only if future work would benefit from knowing the rationale. If there is no
  > meaningful rationale to preserve, don't log it.
- [ ] In `FORMATS.md`, list positive examples (architectural patterns, testing standards,
  lint conventions, data model constraints, API design principles) and negative examples
  (one-off implementation details, local code structure choices, temporary tradeoffs with
  no long-term relevance)

### Structural enforcement

- [ ] Update the DECISIONS.md entry format in `FORMATS.md` to require a
  `**Why this matters long-term:**` line per entry
- [ ] Update the STANDARDS.md entry format the same way
- [ ] Update placeholders in `plans/DECISIONS.md` and `plans/STANDARDS.md` to show the
  new structure

### Agent heuristics (prompt-only, not file metadata)

- [ ] Embed the classification heuristic in prompts that may write entries
  (`Principal.AnswerQuestions`, `PM.ThreadMaintenance`, `Staff.ReviewReconciliation`):
  - "Will this matter in 3 months?"
  - "Does this affect multiple features or systems?"
  - "Is there a non-obvious rationale worth preserving?"
- [ ] Embed the three-bucket classification (`implementation detail` / `project decision` /
  `shared/platform standard`) in the same prompts as a decision-making heuristic.
  Do NOT write these labels into `DECISIONS.md` / `STANDARDS.md` files — behavior, not
  metadata clutter

### Worked example

- [ ] Update `example/plans/DECISIONS.md` and `example/plans/STANDARDS.md` to demonstrate
  the new structure with high-signal entries (each with a `Why this matters long-term` line)

---

## Build approval gate & plan diversion — Planned

New lifecycle actions: human build-approval gate and mid-flight re-planning.

### Human.ApproveBuild

Currently there's no human gate between `Principal.BuildReview` and `Principal.MilestonePlan`. The human should confirm build scope before planning begins. Named `Human.ApproveBuild` for consistency with `Human.ApproveMilestone`.

- [ ] Design `Human.ApproveBuild` action template
  - Runs after `Principal.BuildReview`, before `Principal.MilestonePlan`
  - Human reviews `plans/BUILD.md` for scope, goals, and milestone breakdown
  - On approval: routes to `Principal.MilestonePlan`
  - On changes requested: routes back to `Product.ProductVision` or `Principal.BuildReview` (human specifies)
  - Pause type: `decision`
- [ ] Add `Human.ApproveBuild` to registry.json (inputs, outputs, gates)
- [ ] Add `Human.ApproveBuild` to state.schema.json `action_id` enum
- [ ] Update `Principal_BuildReview.txt` routing — currently routes to `Principal.MilestonePlan`, should route to `Human.ApproveBuild`
- [ ] Update plans/README.md — lifecycle docs, action catalog, quickstart sequence (now 4 build-init steps instead of 3)

### Principal.PlanDiversion

SAM currently has no action that modifies the plan once execution begins. When reality diverges, BACKLOG becomes a junk drawer and there's no formal re-planning path.

- [ ] Design `Principal.PlanDiversion` action template
  - Human-initiated (user sets `next_action_id` or a helper triggers it)
  - Principal assesses scope: new milestone, new phase, extra steps, or just a note
  - Interactive: Principal proposes changes, user confirms before files are modified
  - Updates BUILD.md (if milestones change), MILESTONE.md (if phases change), DECISIONS.md (rationale), thread.md (log), state.json (resume point)
  - Routes based on which artifact was edited: `Human.ApproveBuild` (if BUILD.md changed — new/restructured milestones), `Human.ApproveMilestone` (if MILESTONE.md changed — new/restructured phases), `Staff.DraftQuestions` (new steps only), or resume previous position (minor change)
  - Pause type: `decision`
- [ ] Add `Principal.PlanDiversion` to registry.json (inputs, outputs, gates)
- [ ] Add `Principal.PlanDiversion` to state.schema.json `action_id` enum
- [ ] Update plans/README.md — add to action catalog and lifecycle docs

---

## STATUS.md update frequency — Planned

STATUS.md reduction. Currently every action must update STATUS.md, which largely duplicates state.json. Make update frequency configurable, defaulting to PM-only.

### STATUS.md config option

- [ ] Add `status_updates` key to `config.schema.json` — enum: `every_action` | `pm_only` | `every_milestone` | `never`, default: `pm_only`
  - `every_action` — current behavior; every action writes STATUS.md (backward compatible)
  - `pm_only` — only `PM.StatusUpdate` writes STATUS.md; all others skip it (new default — state.json + thread.md are sufficient for inter-action state)
  - `every_milestone` — STATUS.md updated only on the last phase of each milestone (by `PM.StatusUpdate`)
  - `never` — STATUS.md is not updated; state.json + thread.md are the sole records
- [ ] Update `plans/config.json` with new key (default `pm_only`)
- [ ] Update `PM_StatusUpdate.txt` — always writes STATUS.md regardless of config (it's the PM's primary job)
- [ ] Update all other action templates that currently mandate STATUS.md updates — check `status_updates` config before writing
- [ ] Update `plans/FORMATS.md` — note that STATUS.md update frequency is configurable
- [ ] Update `plans/README.md` — add `status_updates` to Configuration table, update "STATUS.md is authoritative for human-readable snapshot" language to reflect new default
- [ ] Update `plans/copilot-instructions.md` — adjust the "update STATUS.md every action" rule to reference config

---

## Helper scripts & sync tooling — Planned

Helper scripts and sync tooling. All helper scripts are `plans/*.ps1` for zero-install simplicity — just copy `plans/` and go. (CLI upgrade to `sam <command>` deferred to v3+.)

### plans/status.ps1

- [ ] Create `plans/status.ps1` — reads state.json and displays a formatted summary
  - Current position: build, milestone, phase, step
  - Last action: action_id, result, summary
  - Next action: next_action_id, pause_type
  - Active blockers (if any)
  - Config summary (non-default values only)
  - No clipboard copy (that's `next.ps1`'s job)

### plans/commit.ps1

- [ ] Create `plans/commit.ps1` — auto-commits with a SAM-formatted message
  - Runs `git add -A; git commit -m "{message}"`
  - Message format: `--AUTO-{build_id}-{milestone_id}-{phase_id}-{Role}.{Task}: {last_action.summary}` (all values from state.json)
  - The `--AUTO-` prefix distinguishes automated SAM commits from manual ones
  - **Template update:** Add instructions to all action templates that produce organic commits (e.g., `Staff.ImplementationExecution`) telling the AI to NOT use the `--AUTO-` prefix in manual commit messages, so automated vs. organic commits remain distinguishable
  - **Design note:** Keep as a standalone script (single-purpose). Could later add a `-Commit` switch to `next.ps1` as a convenience alias, but separate scripts are simpler and composable.

### plans/sam-update.py + sync-manifest.json

- [ ] Add `plans/sam-update.py` script and `plans/sync-manifest.json` for updating SAM system files across projects
  - **Problem:** When SAM system files or templates change, every project repo using SAM needs those updates — but only for system-level files. Instance-level files (BUILD.md, config.json, state.json, etc.) must never be overwritten.
  - **Approach:**
    - `sync-manifest.json` declares system-level files to copy and instance-level files to never touch (derived from the taxonomy in `plans/README.md`)
    - `sam-update.py` reads the manifest and copies system files from a source SAM repo into the target project, including `copilot-instructions.md` → `.github/copilot-instructions.md`
    - Dry-run by default; `--apply` flag to execute. Show diffs for files that already exist.
    - Optionally stamp `plans/.sam-version` for tracking which SAM version a project is running
  - **Invocation:** `python plans/sam-update.py [path/to/sam-template]` (path defaults to `SAM_TEMPLATE_PATH` env var if set)
  - **Rationale:** Git submodules/subtrees/symlinks don't fit the selective, in-place update need. A manifest-driven script is explicit, maintainable, and lets SAM own the sync rules.
  - **Note:** Both `sam-update.py` and `sync-manifest.json` are system-level files, so they get synced too — bootstrapping is the only manual copy.
  - **Note:** This is the one Python script in the toolbox. It stays Python because it's the most complex helper (diffing, manifest parsing, cross-platform potential) and is a natural seed for a future CLI if that path is pursued.

---

## Deferred / Future

Items parked until a clear trigger or sufficient friction warrants action.

### Folder reorganization

- [ ] Evaluate restructuring `plans/` to reduce top-level clutter
  - Currently everything except prompt templates lives flat under `plans/` — system docs, instance artifacts, schemas, config, helpers, and state all at the same level.
  - Possible directions: separate system files from instance files, or group by function (e.g., `plans/schemas/`, `plans/scripts/`).
  - **Constraints:** Every template hardcodes `plans/` paths — restructuring means updating all templates, registry.json, copilot-instructions.md, and the sync manifest. Instance-level files must remain easy for the AI to find.
  - **Trigger:** Reassess after v1.6.0 adds more scripts. If the file count still isn't causing friction, keep deferring.

### CLI tool — `sam <command>` (v3+)

- [ ] Evaluate upgrading `plans/*.ps1` scripts into a proper CLI tool (`sam next`, `sam commit`, `sam status`, `sam update`)
  - **Pros:** Clean UX, cross-platform (Python or Node), single entry point, could add features like `sam init` (scaffold plans/), `sam validate` (check state.json against schema), `sam log` (formatted thread.md viewer)
  - **Cons:** Requires install step (pip/npm), breaks the "just copy plans/" simplicity, adds a runtime dependency, distribution/versioning overhead
  - **Current position:** `plans/*.ps1` scripts are zero-install, single-purpose, and cover the core needs. The simplicity of "copy plans/ to your repo" is a major feature, not a limitation. Upgrade to CLI only if the script count or complexity outgrows the pattern.
  - **Note:** If pursued, `sam-update.py` is the natural starting point — it's already Python and the most complex helper.

### Modular / configurable workflow (v4+)

- [ ] Explore fully configurable workflow engine where users can: group multiple steps into one `plans/next` invocation (e.g., PM.StatusUpdate + PM.AdvancePhase), drop actions entirely, or define custom project-specific actions
  - Would require a workflow definition format, dynamic template loading, and significant registry/routing rework
  - The current `config.json` knobs (v1.2.0) handle ~80% of the process-weight need; this is the remaining 20% for power users
  - **Far-future vision** — park until config.json proves insufficient