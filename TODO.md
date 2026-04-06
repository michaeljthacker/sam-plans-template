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
- [ ] Build a worked example in `example/` showing one full phase cycle with realistic file contents
  - **Deferred (D-016):** Copy from a real public project at ~B1 M2 P3 S4 rather than fabricating. Waiting for a suitable project.

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
