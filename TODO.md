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

- [ ] Sharpen DECISIONS vs. STANDARDS distinction with one-sentence heuristic in each template file
- [ ] Add STANDARDS.md placeholder section for branching convention
- [x] Add single-threaded execution statement to README
- [x] Note that `thread.md` is AI-readable, not machine-parseable (documented in README)
- [x] Clean up "TASK is reserved" vocabulary note (STEP replaces SUBTASK; README updated)
- [ ] Build a worked example in `example/` showing one full phase cycle with realistic file contents
