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

---

## D-017 — ReviewReconciliation always runs after CodeReview
**Date:** 2026-04-04
**Decision:** `Principal.CodeReview` always routes to `Staff.ReviewReconciliation`, regardless of whether the outcome is APPROVED or CHANGES REQUIRED. Staff reads `last_action.result` to determine posture:
- `changes_required`: fix REQUIRED items + triage SUGGESTED items
- `approved`: triage SUGGESTED items only (implement quick/high-value ones; log the rest as tech debt in BACKLOG.md)

If any code was changed during reconciliation, routing goes back to `Principal.CodeReview` for a **targeted re-review** (scoped to reconciliation changes, not the full Phase). If no code was changed, routing proceeds to `PM.StatusUpdate`.

**Rationale:** The previous flow skipped ReviewReconciliation on APPROVED reviews, which meant SUGGESTED improvements were silently dropped. This change ensures every suggestion is explicitly triaged — implemented or logged — without adding a heavy re-review loop when no code changes were made.

**Supersedes:** APPROVED → PM.StatusUpdate (D-013 step 5 updated)

---

## D-018 — thread.md is an append-only log
**Date:** 2026-04-04
**Decision:** `thread.md` is a flat chronological log. Every action that writes to it appends a new dated entry at the end using the format:
```
---
### [Action.ID] — YYYY-MM-DD
<content>
```

No structured sections (Open Questions, Answers, Active Work, etc.). Only `PM.ThreadMaintenance` may delete, restructure, or compress content.

**Rationale:** Structured sections caused confusion in practice — unclear when content was "active," questions getting orphaned, answering actions unclear about whether to move/delete entries. An append-only model is simpler: each action just adds to the bottom, and periodic ThreadMaintenance cleans up. This matches how a real conversation thread works.

**Supersedes:** Structured-sections model in thread.md (D-009 clarified)

---

## D-019 — FORMATS.md as single source of truth for file structure
**Date:** 2026-04-04
**Decision:** A new system-level file `plans/FORMATS.md` defines the expected structure, purpose, and update-ownership of every instance-level file. Instance file stubs contain only section headings and a comment pointing to FORMATS.md — no inline "About this file" or "Purpose" prose.

**Rationale:** Instance files previously contained verbose explainer text that either persisted into generated content (confusing the AI about where to write real content) or got deleted and lost structural guidance. Moving all format/purpose documentation to a single reference file solves both problems.

---

## D-020 — PM.ThreadMaintenance triggered mid-lifecycle by PM.StatusUpdate
**Date:** 2026-04-04
**Decision:** `PM.StatusUpdate` (which runs after every Phase) conditionally routes to `PM.ThreadMaintenance` if the thread has grown long or contains substantial resolved content. It uses a `context.notes` entry ("After ThreadMaintenance: proceed to ...") to tell ThreadMaintenance where to route afterward.

**Rationale:** Previously ThreadMaintenance was only triggered by `PM.MilestoneCloseout`, so thread.md could grow noisy across many Phases within a milestone. This adds a natural pruning point without requiring it every time.

---

## D-021 — Configurable process weight via `plans/config.json`
**Date:** 2026-04-05
**Decision:** Introduce a new system-level `plans/config.json` (with `plans/config.schema.json`) that lets the human tune process weight without breaking the state machine. Six features across two classes — four routing knobs and two gate-strictness knobs:

| Config Key | Options | Default | Class |
|------------|---------|---------|-------|
| `code_review` | `every_phase` \| `every_milestone` \| `never` | `every_phase` | Routing |
| `formal_approval` | `every_phase` \| `every_milestone` \| `never` | `every_phase` | Routing |
| `documentation_update` | `every_phase` \| `every_milestone` \| `never` | `every_milestone` | Routing |
| `review_strictness` | `strict` \| `balanced` \| `pragmatic` | `balanced` | Gate strictness |
| `re_review_trigger` | `required` \| `auto` | `required` | Gate strictness |

Additionally, `Staff.DraftQuestions` gains self-skip logic (no config key): if the path forward is clear and no meaningful questions exist, it skips itself (`result = "skipped"`) and routes directly to `Staff.ImplementationExecution`.

Design principles:
- **All defaults = current full-process behavior** (except `documentation_update` which defaults to `every_milestone` — docs every phase was deemed excessive).
- **Missing config file or missing key = default.** The system fails open to the full process.
- **Config is human-edited, never modified by actions.** It is a system-level file.
- **`never` (not `skip`)** for frequency options — consistent with the other frequency values.
- **Routing changes only.** No schema changes to `state.json`. All `next_action_id` values already exist in the enum. Templates consult config when deciding where to route, but the action set, artifacts, and registry structure are unchanged.

Routing knob mechanics:
- `code_review`: `Staff.ImplementationExecution` checks config; `every_milestone` routes to review only on the last phase of the milestone; `never` routes straight to `PM.StatusUpdate`.
- `formal_approval`: `PM.StatusUpdate` and `Writer.DocumentationUpdate` check config; `every_milestone` routes to `Human.PhaseApproval` only on the last phase; `never` routes straight to `PM.AdvancePhase`.
- `documentation_update`: `PM.StatusUpdate` checks config; `every_milestone` routes to `Writer.DocumentationUpdate` only on the last phase; `never` always skips Writer.

Gate strictness mechanics:
- `review_strictness`: `Principal.CodeReview` consults config to set the threshold between REQUIRED and SUGGESTED findings. `strict` = any deviation is REQUIRED; `pragmatic` = only correctness/security issues are REQUIRED.
- `re_review_trigger`: `Staff.ReviewReconciliation` consults config; `required` always re-reviews if code changed (current behavior); `auto` lets the AI judge whether changes warrant re-review (must document reasoning in thread entry).

**Rationale:**
- The full 9-step phase cycle is heavier than many projects need, especially when the human is reviewing in real-time.
- Routing-only changes are safe — they skip steps but don't alter the state machine or artifact contracts.
- Granular knobs (no presets) force the human to consciously opt out of each safety gate rather than blindly picking a "lightweight" preset.
- The Q&A round is better handled as AI self-skip than a config knob — the AI is in the best position to judge whether it has questions, and the escape hatch (routing to `Principal.AnswerQuestions` mid-implementation) is always available.

**Supersedes:** N/A (additive)

### Rejected alternatives
- **Presets (light/standard/full):** Rejected. Granular-only forces explicit decisions about each gate.
- **Configurable Q&A round:** Rejected. Template-level self-skip is more adaptive than a static toggle.
- **`skip` terminology:** Rejected in favor of `never` for consistency with frequency-based sibling values.
- **`re_review_trigger: required_only`:** Rejected. Reframed as `required` vs. `auto` — even suggested changes may warrant review; the distinction is whether the AI judges or always triggers.
- **Thread verbosity config:** Rejected. "Be concise when possible" is good template practice, not a per-project knob.
- **Artifact granularity (disable CHANGELOG/BACKLOG):** Rejected. Low maintenance overhead, high audit value.
- **Role consolidation (inline PM/Writer):** Rejected. Requires template surgery, not just routing changes.
- **Getting-started setup prompt:** Rejected. Cold-start problem (no `.github/copilot-instructions.md` yet) limits its usefulness, and the quickstart section in README covers the manual path.

---

## D-022 — ThreadMaintenance must set pause_type based on next action
**Date:** 2026-04-05
**Decision:** `PM.ThreadMaintenance` must explicitly set `pause_type` based on who acts next:
- If `next_action_id` starts with `Human.*`: `pause_type = "decision"`
- Otherwise: `pause_type = "continue"`

Previously the template said "pause_type unchanged unless you discover an unhandled decision point." This was incorrect when `PM.StatusUpdate` routed through ThreadMaintenance to `Human.PhaseApproval` — the pause_type stayed `"continue"` (set for ThreadMaintenance) instead of becoming `"decision"` (needed for the Human action).

**Rationale:** Found during routing review for D-021 (configurable `formal_approval`). The bug was pre-existing but became more prominently exposed when config routing could send more paths through ThreadMaintenance → Human.PhaseApproval.

**Supersedes:** "pause_type unchanged" rule in PM.ThreadMaintenance template

---

## D-023 — `example/` is a frozen snapshot; never update it to match newer SAM
**Date:** 2026-04-25
**Decision:** The `example/` directory is a **frozen snapshot** of a real project (`mjt-wordsearch-ui`) captured mid-development at B1-M2-P2 against a mix of SAM v1.1.0, v1.2.0, and v1.2.1. When SAM evolves (new entry formats, new templates, renamed files, new conventions), **do NOT propagate those changes into `example/`**. The version mismatch is intentional and is documented in `example/README.md`.

This applies to every file under `example/` — `example/plans/*`, `example/ROOT_README.md`, anything else added later. The only legitimate reasons to edit `example/` are:
- Replacing the entire snapshot with a fresh capture (deliberate, human-initiated).
- Fixing a typo or factual error that was already present in the captured commit.

**Rationale:**
- The example's value is its **authenticity** — it shows real BUILD/MILESTONE/STATUS/thread/state evolution from a real project at a specific point in time. Continuously syncing it to current SAM would destroy that authenticity and turn it into a fabricated specimen, which D-016 explicitly rejected.
- It is normal and expected for the example to drift behind current SAM. `example/README.md` already discloses this with the version note.
- Multiple AI agents have made the mistake of "helpfully" updating `example/` files when extending SAM (e.g., adding the new `**Why this matters long-term:**` line format from the DECISIONS/STANDARDS discipline work). This decision exists specifically to prevent that mistake from recurring.

**How to apply (for AI working on SAM):** When a TODO or task involves changes to file formats, templates, or conventions, scope the change to `plans/` and root-level files only. Do not touch `example/` unless the human explicitly asks for a fresh snapshot. If a TODO item appears to ask for an `example/` update, treat it as suspect and confirm with the human before acting.

**Supersedes:** N/A (additive — clarifies and reinforces D-016)
