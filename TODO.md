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

## v1.2.0 — Configurable process weight (D-021)

Add `plans/config.json` with 5 configurable knobs (4 routing, 2 gate strictness) plus Q&A self-skip logic. All changes are routing/behavioral — no schema or structural rework. See D-021 for full rationale.

### Phase A — Config infrastructure

- [ ] Create `plans/config.schema.json` — JSON Schema (draft-07) for all 5 config keys with enums, defaults, descriptions. Follow `state.schema.json` style.
- [ ] Create `plans/config.json` — instance file with `$schema` ref and all defaults:
  - `code_review`: `"every_phase"`
  - `formal_approval`: `"every_phase"`
  - `documentation_update`: `"every_milestone"`
  - `review_strictness`: `"balanced"`
  - `re_review_trigger`: `"required"`
- [ ] Update `plans/FORMATS.md` — add `config.json` section (what it is, who edits it, structure example). Mark as system-level: human-edited, never modified by actions.

### Phase B — System docs & registry (parallel with A)

- [ ] Update `plans/README.md`:
  - Add `plans/config.json` and `plans/config.schema.json` to the "System-level" file list
  - Add a "## Configuration" section after "Routing and state" explaining purpose, location, defaults table, and fail-open behavior
  - Annotate the Phase execution table noting which steps are configurable (reference Configuration section)
- [ ] Update `plans/copilot-instructions.md` — add `plans/config.json` to "Key files" list with one-line description
- [ ] Update `plans/templates/registry.json` — add `"plans/config.json"` to `inputs` for 5 actions:
  - `Staff.ImplementationExecution` (reads `code_review`)
  - `Staff.ReviewReconciliation` (reads `re_review_trigger`)
  - `PM.StatusUpdate` (reads `documentation_update`, `formal_approval`)
  - `Writer.DocumentationUpdate` (reads `formal_approval`)
  - `Principal.CodeReview` (reads `review_strictness`)

### Phase C — Routing template updates (depends on A+B)

- [ ] Update `Staff_ImplementationExecution.txt` — config-aware `code_review` routing:
  - `every_phase` → `Principal.CodeReview` (unchanged)
  - `every_milestone` + last phase → `Principal.CodeReview`; otherwise → `PM.StatusUpdate`
  - `never` → `PM.StatusUpdate`
  - Keep existing escape hatches (AnswerQuestions, ResolveBlocker) unchanged
- [ ] Update `PM_StatusUpdate.txt` — config-aware post-status routing (most complex change):
  - Replace ad-hoc Writer skip logic with explicit config-driven decision tree
  - Chain: StatusUpdate → [ThreadMaintenance?] → [Writer?] → [PhaseApproval?] → AdvancePhase
  - `documentation_update` × is-last-phase determines Writer routing
  - `formal_approval` × is-last-phase determines PhaseApproval routing
  - ThreadMaintenance "After TM: proceed to X" note must resolve X using same config logic
- [ ] Update `Writer_DocumentationUpdate.txt` — config-aware `formal_approval` routing:
  - `every_phase` → `Human.PhaseApproval` (unchanged)
  - `every_milestone` + last phase → `Human.PhaseApproval`; otherwise → `PM.AdvancePhase`
  - `never` → `PM.AdvancePhase`
  - Adjust `pause_type`: `"decision"` only when routing to Human.PhaseApproval
- [ ] Update `Staff_ReviewReconciliation.txt` — config-aware `re_review_trigger` routing:
  - `required` → `Principal.CodeReview` if any code changed (unchanged)
  - `auto` → AI judges whether changes warrant re-review; must document reasoning in thread entry

### Phase D — Behavioral template updates (parallel with C)

- [ ] Update `Principal_CodeReview.txt` — add `review_strictness` parameter:
  - `strict`: deviations from STANDARDS/DECISIONS are REQUIRED; best-practice violations are pushed harder (REQUIRED when clear, SUGGESTED with strong recommendation otherwise)
  - `balanced`: correctness + clear violations = REQUIRED; style preferences = SUGGESTED (current implicit behavior)
  - `pragmatic`: only correctness/security issues are REQUIRED; everything else = SUGGESTED
- [ ] Update `Staff_DraftQuestions.txt` — add self-skip logic (no config dependency):
  - If no meaningful questions exist: `result = "skipped"`, `next_action_id = Staff.ImplementationExecution`
  - Do not append empty entry to thread.md; note skip in STATUS.md
  - If questions exist: proceed as currently specified (→ Principal.AnswerQuestions)

### Verification

- [ ] Validate `config.json` against `config.schema.json`
- [ ] Walk through 3 routing scenarios to confirm no dead ends or infinite loops:
  - Full process (all defaults) — must produce current 9-step sequence
  - Minimal (`code_review=never`, `formal_approval=never`, `documentation_update=never`) — ~4 steps per phase
  - Milestone-gated (all `every_milestone`) — non-last phases get minimal path, last phase gets full
- [ ] Confirm DraftQuestions self-skip routes to valid `next_action_id` (already in schema enum)
- [ ] Confirm `re_review_trigger=auto` doesn't create dead ends
- [ ] Confirm every updated template says "if config.json missing or key absent, use default"
- [ ] Confirm registry.json has `plans/config.json` in all 5 action inputs
