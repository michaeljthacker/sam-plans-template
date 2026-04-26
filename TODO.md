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

## v1.4.0 — Completed (2026-04-26)

Five feature areas land together: multi-root workspace support, two new lifecycle
actions (build approval gate + plan diversion), configurable STATUS.md update
frequency, structural DECISIONS/STANDARDS discipline, and a helper-script
ecosystem (status, commit, sync). All changes are additive or backward-compatible
via config; no schema breaking changes. Architectural milestones (CLI rewrite,
modular workflow) remain parked at v3+/v4+.

### Multi-root workspace awareness

Foundational support for SAM operating across multiple repos in a VS Code multi-root
workspace. Primary repo owns `plans/`; shared repos receive durable, platform-level
artifact updates (code, `STANDARDS.md`, `DECISIONS.md`) without a `plans/` wrapper.

- [x] Added `workspace` block to `plans/config.schema.json` — `primary_repo: { name, path, owns_plans: true }`, `shared_repos[]: [{ name, path, role }]`. Paths absolute or workspace-relative; SAM never infers from cwd. Single-repo projects omit `shared_repos`
- [x] Updated `plans/config.json` with default `workspace` block (primary only); documented in `plans/FORMATS.md`
- [x] Documented scope-of-change routing: project artifacts default to `primary_repo/plans/`; shared-repo writes limited to code under `shared_repos[].path` plus that repo's `STANDARDS.md` / `DECISIONS.md` (no `plans/` wrapper). Detection by path match against `shared_repos[].path` — not `.code-workspace`
- [x] Escalation: `PM.ThreadMaintenance` proposes promotion candidates inline during pruning; human approves/rejects in chat, ThreadMaintenance carries out the shared-repo write — all within one action. No automatic promotion, no new actions
- [x] Updated DECISIONS/STANDARDS-touching prompts (`Principal.AnswerQuestions`, `PM.ThreadMaintenance`, `Staff.ReviewReconciliation`) to consult `workspace.shared_repos` and route by scope; `Staff.ImplementationExecution` flags shared-repo edits with explicit "shared scope" note
- [x] Updated `plans/agent-instructions.md` (canonical source) with multi-root rules and the "primary repo owns `plans/`" invariant — flows through to `plans/copilot-instructions.md`, `plans/CLAUDE.md`, and the deployed `.github/copilot-instructions.md` / root `CLAUDE.md`
- [x] Added "Multi-root workspaces" section to `plans/README.md` (chose a section over a separate `WORKSPACE.md` to keep SAM's doc surface inside `plans/`); quickstart references the workspace config
- [x] Verified with ajv-cli (draft-07): default and realistic multi-root configs pass; rejects `owns_plans: false`, empty `path`, additionalProperties. Walked end-to-end implementation and escalation scenarios (project DECISIONS for project-scoped findings; shared DECISIONS only after promotion + approval)

### DECISIONS / STANDARDS discipline

Tighten what gets recorded. Every entry now requires a `**Why this matters long-term:**` line — if rationale is weak, the entry shouldn't exist. Stops low-signal entries from drowning out durable rationale.

- [x] Added recording rule to FORMATS.md DECISIONS/STANDARDS sections: "Record only if future work would benefit from knowing the rationale." Included positive examples (architectural patterns, testing standards, API design principles) and negative examples (one-off implementation details, local code structure choices)
- [x] Updated DECISIONS.md and STANDARDS.md entry formats in FORMATS.md to require `**Why this matters long-term:**`; updated placeholders in `plans/DECISIONS.md` and `plans/STANDARDS.md`
- [x] Embedded classification heuristic ("will this matter in 3 months? does it affect multiple features? is there a non-obvious rationale?") and three-bucket framing (`implementation detail` / `project decision` / `shared/platform standard`) in `Principal.AnswerQuestions`, `PM.ThreadMaintenance`, `Staff.ReviewReconciliation`. Behavior, not file metadata — labels never written into the .md files
- [x] Resolved as **do not update**: `example/plans/DECISIONS.md` / `STANDARDS.md`. `example/` is a frozen v1.1.0–v1.2.1 snapshot from a real project; updating to match newer conventions would destroy its authenticity. See D-023

### Build approval gate & plan diversion

Two new lifecycle actions: human-approval gate before milestone planning, and a formal mid-flight re-planning path so BACKLOG stops becoming a junk drawer.

- [x] `Human.ApproveBuild` — runs after `Principal.BuildReview`, before `Principal.MilestonePlan`. Human reviews `plans/BUILD.md` for scope, goals, milestone breakdown. Approve → `Principal.MilestonePlan`; changes requested → back to `Product.ProductVision` or `Principal.BuildReview` (human specifies). Pause type: `decision`. Quickstart now has 4 build-init steps instead of 3
- [x] `Principal.PlanDiversion` — human-initiated re-planning. Principal assesses scope (new milestone / new phase / extra steps / note-only) and proposes changes interactively before files are modified. Updates BUILD.md (if milestones change), MILESTONE.md (if phases change), DECISIONS.md (rationale), thread.md (log), state.json (resume point). Routes based on artifact edited: BUILD.md → `Human.ApproveBuild`; MILESTONE.md → `Human.ApproveMilestone`; new steps only → `Staff.DraftQuestions`; minor → resume. Pause type: `decision`
- [x] Both actions added to `registry.json` (inputs, outputs, gates) and `state.schema.json` `action_id` enum
- [x] `Principal_BuildReview.txt` routing updated to `Human.ApproveBuild` (was `Principal.MilestonePlan`); README lifecycle docs and action catalog updated

### STATUS.md update frequency

STATUS.md was being written by every action — largely duplicating state.json. Now configurable via `status_updates`, defaulting to `pm_only`.

- [x] Added `status_updates` to `config.schema.json` — enum: `every_action` | `pm_only` | `every_milestone` | `never`, default **`pm_only`**:
  - `every_action` — prior behavior preserved as opt-in
  - `pm_only` (new default) — only `PM.StatusUpdate` writes STATUS.md. Routing inserts it after `Human.ApproveBuild`, `Human.ApproveMilestone`, and `Principal.PlanDiversion` (note-only / new-steps scopes) so transitions are still captured. `Human.PhaseApproval` doesn't reroute — the pre-approval `PM.StatusUpdate` already covers phase end
  - `every_milestone` — last phase of each milestone only
  - `never` — `Product.ProductVision` writes a disabled stub on first run; `PM.StatusUpdate` normalizes any non-stub file back to the stub
- [x] Updated `plans/config.json` with new key; `PM_StatusUpdate.txt` handles phase-end and hand-off invocations (via `context.notes` "After StatusUpdate: proceed to <X>"), applies the `every_milestone` last-phase gate and `never` stub-normalization
- [x] Updated 16 action templates to check `status_updates` before writing: `Product_ProductVision` (always creates STATUS, with stub under `never`), `Principal_BuildReview`, `Principal_MilestonePlan`, `Staff_DraftQuestions`, `Principal_AnswerQuestions`, `Staff_ImplementationExecution`, `Principal_CodeReview`, `Staff_ReviewReconciliation`, `Writer_DocumentationUpdate`, `Human_ApproveBuild` (+ reroute), `Human_ApproveMilestone` (+ reroute), `Human_PhaseApproval`, `PM_AdvancePhase`, `PM_MilestoneCloseout`, `PM_ThreadMaintenance`, `Principal_PlanDiversion` (+ reroute for scopes a/b)
- [x] Updated `plans/FORMATS.md` (Updated by line, snapshot template's `Update configuration:` line, config table row, disabled-stub format), `plans/README.md` (Configuration table, "STATUS.md updates" subsection, softened "STATUS.md is authoritative" language, Configurable? column for `PM.StatusUpdate`), and `plans/agent-instructions.md` step 7
- [x] Added `plans/config.json` to registry.json inputs for the 9 actions that didn't already list it

### Helper scripts & sync tooling

Zero-install helpers (`plans/*.ps1`, plus one stdlib-only Python script). CLI upgrade to `sam <command>` deferred to v3+.

- [x] `plans/status.ps1` — formatted one-screen summary from `state.json` + `config.json`: position (`B1-M2-P3-S2`), pause_type, last_action, next_action_id, active blockers, non-default config values. Deliberately ignores `STATUS.md` — STATUS is human prose and lags under the `pm_only` default; using it would make the script lie. No clipboard copy (that's `next.ps1`'s job)
- [x] `plans/commit.ps1` — runs `git add -A; git commit -m "<msg>"` with `--AUTO-{build_id}-{milestone_id}-{phase_id}-{Role.Task}: {last_action.summary}` (pre-phase actions drop the phase segment). The `--AUTO-` prefix marks SAM-automated commits. Updated the three templates that instruct organic commits (`Staff_ImplementationExecution`, `Staff_ReviewReconciliation`, `Human_PhaseApproval`) to forbid `--AUTO-` in manual messages
- [x] `plans/sam-update.py` + `plans/sync-manifest.json` — manifest-driven sync of SAM system files into target projects without overwriting instance files. Manifest declares `system_files` (always synced), `instance_files` (never touched), `deploy_mappings` (system files that land outside `plans/`, e.g., `plans/copilot-instructions.md` → `.github/copilot-instructions.md`). Dry-run default; `--apply` writes files and stamps `plans/.sam-version`. Hand-rolled top-level config validator (~30 lines, zero deps — preserves the "just copy `plans/`" promise) audits user's `config.json` post-sync and reports REQUIRED / ERROR / WARN drift; exit code `2` for CI; never blocks the sync (chicken-and-egg). Invocation: `python plans/sam-update.py [path]`, falls back to `SAM_TEMPLATE_PATH` env var. Both files are themselves system-level so they self-update — bootstrapping is the only manual copy

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