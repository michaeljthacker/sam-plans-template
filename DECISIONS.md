# SAM System-Design Decisions

This file captures **rationale** for design choices made about SAM itself.
It is a project-level file for this repo — not part of the distributable `plans/` template.

When SAM is complete enough to self-host, this repo may graduate to using its own system.

---

## D-001 — Execution hierarchy vocabulary
**Date:** 2026-02-13
**Decision:** The fixed execution hierarchy is:

> BUILD → MILESTONE → PHASE → STEP → (commits happen)

**Rationale:**
- "SUBTASK" was previously used instead of "STEP" but collided with the reserved word "TASK" (see D-002). "STEP" is clearly subordinate to PHASE, clearly distinct from TASK, and natural in conversation.
- Commits are a side-effect of implementation, not a structural level. They happen during PHASE execution (≥1 per phase) but are not a planning unit.

**Supersedes:** SUBTASK

---

## D-002 — "TASK" is reserved for ROLE×TASK
**Date:** 2026-02-13
**Decision:** The word "TASK" refers exclusively to the action component of a ROLE×TASK pair (e.g., `Staff.DraftQuestions`). It is never used in the execution hierarchy.

**Rationale:** Avoids ambiguity now that SUBTASK has been renamed to STEP.

---

## D-003 — Two-segment action ID naming: `Role.Task`
**Date:** 2026-02-13
**Decision:** Action IDs use two dot-separated segments: `Role.Task`. Role names are collapsed to short labels. No underscores in IDs.

Role mapping:

| Full label | Collapsed role |
|------------|---------------|
| Engineer (Staff-level) | `Staff` |
| Engineer (Principal-level) | `Principal` |
| Project Manager | `PM` |
| Product Manager | `Product` |
| Tech Writer | `Writer` |
| Human | `Human` |

Examples: `Staff.DraftQuestions`, `Principal.CodeReview`, `PM.StatusUpdate`, `Human.ResolveBlocker`

Template filenames mirror action IDs with underscores: `Staff_DraftQuestions.txt`

**Rationale:**
- Previous convention (`Engineer_Staff.DraftQuestions`) used underscores within the role and a dot between role and task — fragile and inconsistent.
- Two-segment names are short, unambiguous, and map cleanly to filenames.

**Supersedes:** `Engineer_Staff.DraftQuestions` style naming

---

## D-004 — All roles are AI-executed except `Human.*`
**Date:** 2026-02-13
**Decision:** Every role (Staff, Principal, PM, Product, Writer) is played by AI. Only `Human.*` actions require a human.

Role names are persona labels that shape AI behavior, not team assignments.

**Rationale:** SAM is "a process for managing a large project entirely by AI/Copilot with intentional pausing and other patterns." The human provides the idea, reviews, confirms, tests manually, and makes decisions. The AI does the work.

---

## D-005 — `pause_type` replaces `needs_human`
**Date:** 2026-02-13
**Decision:** `state.json` uses `pause_type` instead of `needs_human`:

- `"continue"` — AI completed an action; human can review then proceed. The next action is an AI role.
- `"decision"` — A human decision is required. `next_action_id` will be `Human.*`.

**Rationale:**
- `needs_human` was redundant with `next_action_id`. If `next_action_id = "Human.ResolveBlocker"`, that already implies human attention.
- Every action pauses for human review regardless (prompts never chain automatically). The distinction is between "glance and go" vs. "you must actually decide something."

**Supersedes:** `needs_human: true/false`

---

## D-006 — Prompts never chain automatically
**Date:** 2026-02-13
**Decision:** Every ROLE×TASK completes, updates state, and stops. The human reviews, then opens a new chat and says "do the next thing based on state." A runner could automate the "read state → load template → execute" step but still performs exactly one action then stops.

**Rationale:** Preserves human review at every step. The human always has the chance to inspect, correct, or override before the next action.

---

## D-007 — Error handling → `Human.ResolveBlocker`
**Date:** 2026-02-13
**Decision:** Unexpected failures set `next_action_id = "Human.ResolveBlocker"` with a blocker entry describing the failure. Expected failures (e.g., failing tests during implementation) are handled within the action itself — Staff fixes them or escalates questions to Principal.

**Rationale:** The human is always the fallback for anything outside the normal flow. A runner's error path is: catch error → write blocker to state.json → stop.

---

## D-008 — DECISIONS.md vs. STANDARDS.md distinction
**Date:** 2026-02-13
**Decision:** Both files are kept separate in the template:

- **STANDARDS.md** = Team-level standards that survive across projects. Testing, linting, formatting, documentation, code style. "Even if we change to a new product, this TEAM has these standards."
- **DECISIONS.md** = Project-level architectural choices. "Multiple approaches may be defensible, but IN THIS PROJECT we will…"

For bootstrapping, STANDARDS gets seeded from team/personal defaults; DECISIONS starts empty and grows.

**Rationale:** The overlap is real ("always use strict TypeScript" could be either), but the heuristic is actionable: standards are portable across projects, decisions are project-specific.

---

## D-009 — `thread.md` is AI-readable, not machine-parseable
**Date:** 2026-02-13
**Decision:** `thread.md` is active working memory for AI to read. The runner may do simple checks ("was thread.md modified in the last commit?") but will not parse its content for structured elements.

**Rationale:** Keeps the format flexible. AI handles natural language well; enforcing a rigid schema on thread content adds complexity without value.

---

## D-010 — Branching strategy is project-level, not SAM-prescribed
**Date:** 2026-02-13
**Decision:** SAM does not prescribe a branching model. Projects record their branching convention in STANDARDS.md or their project README. The quickstart should mention: "decide your branching model and record it."

Common default: `prod`, `main` (default), `feat/...`, `bug/...`.

**Rationale:** Branching is a project decision, not a workflow decision. SAM is single-threaded — one phase at a time. Unplanned fixes (e.g., a bug in M1 found during M2) are handled inline and documented in CHANGELOG.

---

## D-011 — Single-threaded execution model
**Date:** 2026-02-13
**Decision:** SAM assumes single-threaded execution. One phase is active at a time. `state.json` tracks a single active `build_id`, `milestone_id`, and `phase_id`.

If a bug in a previous milestone is found, it is handled as an unplanned step in the current phase, documented in thread.md and CHANGELOG, and work resumes.

**Rationale:** The human operator is one person working with one AI at a time. There will never be two AI sessions working on the project simultaneously. Concurrency adds complexity without matching the use case.

---

## D-012 — BUILD.md and MILESTONE.md are generated by actions
**Date:** 2026-02-13
**Decision:** BUILD.md and MILESTONE.md are outputs of early-lifecycle actions (`Product.ProductVision`, `Principal.MilestonePlan`), not manual fill-in templates.

The template files in `plans/` still have placeholder structure, but the intended flow is:
1. Human provides a project idea
2. `Product.ProductVision` generates root README + BUILD.md
3. `Principal.MilestonePlan` generates MILESTONE.md

**Rationale:** The AI should generate its own planning artifacts via actions rather than requiring the human to fill in templates by hand. The human reviews and approves, but doesn't draft.

---

## D-013 — Phase execution loop sequence
**Date:** 2026-02-13
**Decision:** Each phase follows this sequence:

1. `Staff.DraftQuestions` — draft questions for the phase
2. `Principal.AnswerQuestions` — answer questions
3. `Staff.ImplementationExecution` — implement the phase
4. `Principal.CodeReview` — review the implementation
5. `Staff.ReviewReconciliation` — address required feedback (loop to 4 if needed)
6. `PM.StatusUpdate` — update STATUS/BACKLOG/CHANGELOG
7. `Writer.DocumentationUpdate` — update docs (optional/skippable)
8. `Human.PhaseApproval` — human confirms, triggers commit
9. `PM.AdvancePhase` — increment phase_id, set up next cycle

Steps 4-5 may loop if the review requires changes.

**Rationale:** Matches the proven pattern from personal Copilot experience. Each step is a bounded micro-chunk.

---

## D-014 — Quickstart belongs in `plans/README.md`
**Date:** 2026-02-13
**Decision:** `plans/README.md` includes a quickstart section showing the copy-and-go bootstrap sequence. This is part of the distributable template.

**Rationale:** The README is the entry point anyone sees when they copy `plans/` into their repo. A quickstart there makes the system immediately usable.

---

## D-015 — Root-level project files for SAM development
**Date:** 2026-02-14
**Decision:** This repo (the SAM template itself) uses root-level `DECISIONS.md` and `TODO.md` for its own development, separate from the `plans/` template contents.

**Rationale:** `plans/` is the distributable template — its DECISIONS.md must stay a blank template. This repo needs its own project-level records but can't fully dog-food SAM yet (SAM isn't done). When SAM is complete, this repo may self-host.

---

## D-016 — Example files sourced from a real project, not fabricated
**Date:** 2026-02-15
**Decision:** The `example/` directory will be populated by copying files from a real public project once that project reaches ~B1 M2 P3 S4 (i.e., partway through the second milestone). This replaces the original plan to synthesize example content.

**Rationale:**
- Fabricated examples risk being unrealistic or inconsistent with how the system actually evolves during use.
- By M2, the templates and workflow will have gone through at least one full milestone cycle, so any early kinks should be resolved.
- A real project provides authentic thread.md progression, realistic state.json transitions, and natural BUILD/MILESTONE/STATUS content.
- Waiting costs nothing — the template is usable without the example directory.
