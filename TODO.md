# SAM v0 — Implementation Backlog

Prioritized work to complete SAM v0.
Future chat sessions: read `DECISIONS.md` for rationale, `plans/README.md` for the spec, then pick up from the **Open work** section below. Completed history is archived at the bottom.

---

## Status key
- [ ] Not started
- [~] In progress
- [x] Done

---

# Open work

## Next — Quick polish

Small, prompt-and-script-only changes. No schema, routing, or config additions. Pick up when the current batch lands; not promised to a specific version.

- [ ] **`PM.AdvancePhase` should handle milestone closeout inline.** Today, when the current phase is the last in the milestone, `PM.AdvancePhase` does nothing structural and routes to `PM.MilestoneCloseout` — a tiny separate action. Let `PM.AdvancePhase` just *do* the closeout when that's the appropriate route, rather than bouncing to another action for a small task. (Feedback 2026-07-16.) Keep them able to coexist — closeout still exists as its own action for direct invocation — but AdvancePhase shouldn't punt when it's already the right actor. Touches: `PM_AdvancePhase.txt`, `PM_MilestoneCloseout.txt`, routing docs; confirm no double-closeout. Small-ish, but decide whether it's a merge or an inline call before doing it.

---

## Proposed — Design work

Items that need a small design pass before implementation. Not committed to a version or sequenced as a batch — each can move to Next independently once its shape is clear.

- [ ] **Buy-vs-build lens covers free / OSS / asset-library options, not just paid services.** Current v1.4.1 Principal "engineering judgment" lens nudges toward managed-service consideration, but the AI still defaults to building when the alternative is *free* (Kenney / OpenGameArt / itch.io for game assets, public APIs, free tiers, OSS libraries that solve large chunks of the problem). Update `Principal_BuildReview.txt`, `Principal_MilestonePlan.txt`, `Principal_AnswerQuestions.txt` to explicitly call out *free / public / community* options alongside paid services. Concrete examples in the prompt help (the asset-library case is a good one).
- [ ] **`Human.HumanOnlyPhase` (or guidance for `Human.ResolveBlocker` as full-phase scope).** When an entire phase is human work (Cloudflare account + R2 bucket + domain + token setup; substantial system provisioning; account/billing setup), the AI gets confused about routing around / after the human work. Two paths:
  - Add a new `Human.HumanOnlyPhase` task-action with explicit "this phase is entirely human work, here's what to do, here's when to come back" semantics.
  - Or document `Human.ResolveBlocker` as legitimately scope-able to a whole phase and fix the routing confusion in prompts.
  - The first is cleaner; the second is cheaper. Decide during design.
- [ ] **`Principal.AdhocReview` — model-up review escape hatch.** When the user is working in a constrained surface (Copilot in VS Code, no Opus access on their plan) and wants a higher-capability model to weigh in, give them a clean handoff: "Summarize this in `thread.md` and route to `Principal.AdhocReview`." The receiving session (run in a higher-tier surface) picks it up, reviews, writes findings back. Needs: registry entry, template, routing semantics (where it returns to), and a `context.notes` convention for the handoff summary. Distinct from `Principal.CodeReview` (which is in-flow) — this is on-demand.

- [ ] **Action naming once-over — several names don't say what they do.** (Feedback 2026-07-16 and 2026-08-09.) Do a single "what else doesn't make sense right now?" pass and rename as one atomic operation. Known offenders:
  - **`Human.*` approve-plan vs. approve-work.** `Human.ApproveBuild` / `Human.ApproveMilestone` approve **plans** (`BUILD.md` / `MILESTONE.md`), but `Human.PhaseApproval` approves the **completed work** of a phase. The `Approve{thing}` vs. `{thing}Approval` distinction is too subtle — someone new to SAM (or the AI mid-run) can't tell "approve the plan" from "approve the work" by name alone. Proposed convention: `Approve{thing}` = approve a plan; `{thing}Approval` = approve completed work (e.g. `Human.ImplementationApproval`) — or pick clearer names outright.
  - **`Staff.ImplementationExecution`** reads as redundant ("execution" adds nothing over "implementation").
  - **`Principal.BuildReview` vs. `Human.PhaseApproval`** — `BuildReview` reviews the `BUILD.md` *file*, while `PhaseApproval` approves finished *work*; the "Review"/"Approval" words don't consistently track file-vs-work.
  - **Larger-scale confusion risk, small implementation** (single user today), but a rename touches `state.schema.json` `action_id` enum, `registry.json`, every routing reference in templates, `README.md`, and helper scripts. Do it with no stale remnants; add a DECISION entry codifying the final naming convention.

- [ ] **Remove `STEP` from `state.json`.** A "chunk" of work should always be a **phase**, not a step. When a right-sized BUILD is used (e.g., `phase-only`), the process currently tries to execute STEPS as if they were PHASES, which defeats the point of right-sizing. (Feedback 2026-07-16.) Drop `step_id` from `state.json` / `state.schema.json` and rework any routing/vocabulary that treats a step as an executable unit. **Design pass needed:** steps still appear in `MILESTONE.md` as planning sub-bullets and in ID conventions (`B1-M2-P4-S2`) and commit messages (`commit.ps1`); decide whether steps survive as a *planning-only* concept (no state) or are removed entirely. Touches state schema, `commit.ps1`/`next.ps1`/`status.ps1`, FORMATS.md, README ID conventions, and several templates. Add a DECISION entry.

- [ ] **`context.notes` vs. `thread.md` — clarify or collapse the boundary.** Some SAM repos barely touch `state.json > context.notes`; others lean on it. Working mental model: `thread.md` = full conversation log, `notes` = "top of mind" highlights + routing hand-offs (e.g., "After ThreadMaintenance: proceed to X"). Is that distinction necessary, and is the boundary crisp enough to state? (Feedback 2026-07-16 — "is it fine? No strong feeling.") **Design pass:** either (a) document the boundary explicitly in FORMATS.md (notes = machine-relevant routing hand-offs + short-lived highlights; thread = human/AI narrative) and audit templates for misuse, or (b) collapse `context.notes` into thread.md if it earns its keep only as routing hand-offs (but those are structured and machine-read, which argues for keeping notes). Low urgency; decide direction first.

- [ ] **BUILD END / release-runner action.** Add a build-completion task that drafts a clear **deployment runner doc** so the human can execute it (preferred over actually running the deploy). Should cover, for all relevant repos (frontend + backend as appropriate): PRs to `main`, version bumps, git tags, CHANGELOG `Unreleased` → `Released` move (this is the "BUILD released" action foreshadowed in D-024), env var updates, deployment steps, migrations, smoke-test best practices, and rollback plans per deployed repo. (Feedback 2026-07-16.) **Design pass:** new registry entry + template + routing (reached from `PM.MilestoneCloseout` when the final milestone of the Build completes — ties into the D-024 "future `*.BuildRelease` action"). Decide role (`PM.*`? `Writer.*`? new `Product.*`?) and whether it also performs the Unreleased→Released CHANGELOG move or just documents it. Multi-root aware (per-repo runner sections).
  - **Preferred output shape (feedback 2026-08-09):** the runner should not live in `thread.md`. Instead, standardize a durable, per-repo `DEPLOYMENT.md` that the action simply *updates* for the specific deployment (version numbers, tags, env deltas, migration notes) rather than regenerating from scratch each time. First run scaffolds `DEPLOYMENT.md`; subsequent releases patch it. Decide whether it's a system-scaffolded instance file (like STATUS.md) or fully human/AI-owned. Multi-root: one `DEPLOYMENT.md` per deployed repo.

- [ ] **"Not a Build" mode — maintenance chores below the Build threshold.** (Feedback 2026-08-09.) Some work isn't a Build at all: "fix the Dependabot alerts," bump a dependency, apply a security patch. Today the smallest unit is a `step-only` Build with a B-number, which is heavier than the task deserves and pollutes Build numbering. Design a lightweight track — a template/action (or a distinct entry mode) for chores that carry **no BUILD number**: read the alert/chore, make the fix, log it, done. Roughly the `step-only` class but without the Build wrapper. **Design pass:** decide whether it's a new `action_id` (e.g. `Staff.Chore` / `Maintenance.*`), how it records in state.json (does `build_id` become nullable / a sentinel?), where it logs (CHANGELOG? a maintenance log?), and how `next.ps1` / `status.ps1` / `commit.ps1` render an ID with no B-number. Add a DECISION entry.

- [ ] **Configurable `PM.ThreadMaintenance` timing.** (Feedback 2026-08-09.) Add a config knob — `thread_maintenance: auto | every_milestone` (proposed **new default `every_milestone`**). `auto` preserves current mid-lifecycle prunability-gate behavior (D-026). Under `every_milestone`, maintenance runs *late* — right before `PM.AdvancePhase` / `PM.MilestoneCloseout` — instead of opportunistically mid-flight. **Sequencing note:** this interacts with the pending "AdvancePhase handles closeout inline" change and the closeout→ThreadMaintenance routing; settle those first (or design together) so the "run maintenance right before the transition" hook lands in the right place. Touches `config.schema.json`, `config.json`, `PM_StatusUpdate.txt` (routing gate), `PM_ThreadMaintenance.txt`, `PM_AdvancePhase.txt` / `PM_MilestoneCloseout.txt`, FORMATS.md, README Configuration table. Add a DECISION entry.

- [ ] **Right-size the implementation validation loop — iterative vs. checkpoint scope.** (Feedback 2026-09-01.) SAM currently nudges coding agents to run expensive validation too often: a tiny edit triggers the full test suite + repo-wide Ruff/Black/flake8, then another tiny edit repeats the whole cycle. In repos with multi-minute suites, a ~45s change becomes a 10+ min loop. Distinguish **iterative validation** (during implementation: narrowest relevant tests for the code being touched, rerun those after local fixes; broaden only when the change is cross-cutting or targeted tests can't give confidence) from **checkpoint/final validation** (at phase/milestone boundaries and before declaring done: full suite + required lint/format/type gates, resolve failures before completing). Goal is *not* less verification — it's moving expensive verification to where it buys confidence. Target loop: edit → targeted → edit/fix → targeted → final broader; not edit → full+lint → repeat. **Design pass:** first decide whether a general behavioral rule suffices (preferred — something like "use the narrowest validation scope that gives meaningful feedback for the current change; reserve full-suite/repo-wide validation for checkpoints, final verification, or genuinely cross-cutting changes") rather than adding config. Only if repos genuinely need different policies, consider a `testing: { iteration, checkpoint, final }` knob — don't add config merely for configurability. Touches `Staff_ImplementationExecution.txt`, `Staff_ReviewReconciliation.txt`, `Principal_CodeReview.txt`, `Human_PhaseApproval.txt`, FORMATS.md; possibly `config.schema.json`/`config.json`/README if config is chosen. Add a DECISION entry.

---

## PlanDiversion combined-approval path

- [ ] Fix double-approval routing when `Principal.PlanDiversion` touches both BUILD and MILESTONE. Today the human ends up approving twice with a confusing PM.StatusUpdate → MilestonePlan detour in the middle (where MilestonePlan reasons the milestone is already drafted and skips to ApproveMilestone, but the human thinks they already approved).
  - Two modes based on magnitude:
    - **Sequential** (large overhaul): ApproveBuild → StatusUpdate → MilestonePlan (re-plan, not skip) → ApproveMilestone. Needs `context.notes` annotation so MilestonePlan knows to re-plan and ApproveMilestone knows it's a fresh approval.
    - **Combined** (small build delta, substantive milestone): single approval gate covering both, one StatusUpdate, back to `Staff.DraftQuestions`. Likely a context flag on `Human.ApproveMilestone` rather than a new action — avoids template proliferation.
  - Touches: `Principal_PlanDiversion.txt`, `Human_ApproveBuild.txt`, `Human_ApproveMilestone.txt`, `PM_StatusUpdate.txt`, registry, possibly state schema for the flag.
  - Needs a DECISION entry.

---

## Deferred / Future

Items parked until a clear trigger or sufficient friction warrants action.

### Principal engineering-judgment lens — heavyweight version

- [ ] Revisit if the v1.4.1 prompt-only "lite" lens proves insufficient in practice
  - **Project posture config** — `config.json` knob like `project_posture: { current, target }` with values `prototype` / `mvp` / `production`. Drives both immediate Principal recommendations and long-term BACKLOG entries for one-way-door issues. ("We're scrappy now, but we want to be production — so flag the things that'll bite us later.")
  - **Foundation checklist** — Principal systematically considers analytics, auth, payments, email, observability, marketing, etc., scoped to posture. Most prototypes don't need most of these; the goal is *thinking about it*, not building it.
  - **Options-to-human flow** — for genuinely controversial or lock-in choices, Principal may present a slate rather than picking. Distinct from the lite version, which always picks and leaves a breadcrumb.
  - **Trigger to reconsider:** the lite version misses something important in real use — e.g., AI quietly picks a one-way-door without flagging, or human keeps having to back out of foundational decisions made too early.

### Cross-platform helper scripts (PowerShell vs. POSIX)

- [ ] `plans/*.ps1` were written Windows-first, but SAM's longer-term direction is dev-container-based development (Linux). Decide and commit to one of:
  - **Dual-track:** maintain a `.sh` sibling for each `.ps1` (`next.sh`, `status.sh`, `commit.sh`, `sam-update.py` is already cross-platform). Doubles maintenance surface.
  - **Port to Python** — `sam-update.py` is already stdlib-only Python; the other helpers are small enough to port. Single source, runs anywhere Python runs. Loses the "no install" charm only marginally (Python is everywhere).
  - **Commit to Linux + dev containers** — drop `.ps1`, write `.sh`, document that SAM assumes a dev container. Honest about the actual direction.
  - **Trigger:** once the dev-container workflow is real enough that the user notices the PowerShell scripts breaking under it. Until then, the `.ps1`s work where they need to.

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

---

# Completed

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

## v1.4.1 — Completed (quick polish)

Small, prompt-and-script-only changes. No schema, routing, or config additions.

- [x] `PM.MilestoneCloseout`: milestones are **completed**, not **released** — only BUILDs are released. Fix the template wording and grep the rest of `plans/` for stray "released" applied to milestones. Add a DECISION entry codifying the vocabulary (BUILDs released, MILESTONES completed, PHASES approved) so this doesn't recur.
- [x] `plans/next.ps1`: remove the `(last: {{state.last_action.summary}})` line — `plans/status.ps1` (v1.4.0) is the right place for that context; `next` should stay targeted.
- [x] `plans/status.ps1`: add git basics — current branch and ahead/behind vs. upstream. Must degrade gracefully on no upstream, detached HEAD, or no remote.
- [x] **Principal "engineering judgment" lens (lite)** — prompt-only additions to `Principal_BuildReview.txt`, `Principal_MilestonePlan.txt`, and `Principal_AnswerQuestions.txt`. Principal still picks the recommendation it would actually pick (no option-menu punt to human), but must leave one-line breadcrumbs when there's a meaningful alternative or risk:
  - **Buy vs. build** for non-trivial capabilities (auth, payments, email, analytics, search, file storage, observability, etc.) — if a managed service or established OSS option exists and you're choosing to build, note *why*.
  - **One-way doors** — flag choices hard to reverse (data model, vendor lock-in, license, platform).
  - **Industry-standard divergence** — if the recommendation departs from the common default, say so explicitly.
  - Framing: *"Hey boss, I'm handling it, but I want you to know XYZ came up."* Not a menu. Not noise on every trivial choice. Only when non-obvious, locking-in, or divergent.

---

## v1.6.0 — Completed (2026-07-16)

Two feedback-driven changes: a durable concept-brief seed file, and a prunability gate
so mid-lifecycle thread maintenance stops firing on no-op. See D-025 and D-026.

Also shipped: **Configurable planning depth** — BUILD.md frontmatter `size` field (`full` | `single-milestone` | `phase-only` | `step-only`), decided by `Product.ProductVision` with optional `thread.md` hint and human sign-off at `Human.ApproveBuild`. Caps milestone/phase/step counts downstream; `Principal.PlanDiversion` may resize mid-flight. See `plans/FORMATS.md` and `plans/README.md` "Build sizing" for details. (Originated as a "Proposed — Design work" item.)

### `plans/VISION.md` concept brief (D-025)

- [x] Created `plans/VISION.md` — human-authored concept brief; the durable, read-only seed for a Build. Actions read it but never modify it; it is not pruned like `thread.md`.
- [x] Added VISION.md section to `plans/FORMATS.md` with a VISION-vs-thread boundary note; updated the BUILD.md "Updated by" line and the size-hint source (now VISION.md).
- [x] Updated `Product_ProductVision.txt` (primary seed = VISION.md, thread.md fallback; read-only guard), `Principal_BuildReview.txt` (fidelity-to-concept-brief check), `Principal_MilestonePlan.txt` (consult original intent), `Staff_QuickImplement.txt` (VISION.md is the real spec for step-only) — all with explicit "do not modify VISION.md" constraints.
- [x] Added `plans/VISION.md` to those four actions' `registry.json` inputs and to `sync-manifest.json` `instance_files` (bumped manifest to 1.6.0).
- [x] Updated `plans/README.md` (instance-file list, sizing, lifecycle §1, quickstart step 3, thread management) and `plans/agent-instructions.md` (read-only exception in instance-file hygiene).
- [x] Backward compat: empty/absent VISION.md falls back to `thread.md`.

### Prunability gate before ThreadMaintenance (D-026)

- [x] `PM_StatusUpdate.txt`: replaced the naive "thread has grown long" trigger with a cursory prunability check — routes to `PM.ThreadMaintenance` only if, after applying `every_milestone` config gates and state, there is genuinely prunable/promotable content. When in doubt, skip (closeout always runs maintenance).
- [x] `PM_ThreadMaintenance.txt`: added a no-op guard so a manual or closeout-triggered invocation with nothing to do leaves files unchanged, sets `result = "ok"`, and routes onward instead of inventing pruning.
- [x] `plans/README.md`: documented the prunability gate in the Thread management section.

---

## v1.7.0 — Completed (2026-08-09)

Quick-polish batch (prompt/script/config only — no schema or routing-graph rework),
plus a `sam-update.py` output improvement. Manifest bumped to 1.7.0.

### Config defaults refresh + coupled milestone-scope fixes

- [x] `config.json` + `config.schema.json` defaults now `code_review=every_milestone`, `formal_approval=every_milestone`, `re_review_trigger=auto` (documentation_update/review_strictness/status_updates already at target). Descriptions + FORMATS.md and README config tables updated; the three template "if key absent, use default" fallbacks reconciled to match.
- [x] `Principal_CodeReview.txt`: reads `code_review` and reviews the WHOLE milestone (all phases since the last boundary) under `every_milestone`, not just the last phase.
- [x] `Human_PhaseApproval.txt`: reads `formal_approval` and assembles a milestone-scoped briefing ("Milestone Approval Required") under `every_milestone`. Pairs with the CodeReview fix so the new default gates aren't silently last-phase-only.

### thread.md entry-placement & structure canon

- [x] `plans/FORMATS.md` thread.md rules: new entries go at the **bottom**; no sub-sections / grouping / "Resolved" buckets; resolved content is **deleted** (durable bits promoted to DECISIONS/STANDARDS/CHANGELOG/README first), not archived in-file.
- [x] `PM_ThreadMaintenance.txt`: rewrote the prune step (was "resolved summary at the top") to delete + promote, leaving only still-active entries in chronological order.
- [x] Added "at the bottom" to every thread.md writer template (DraftQuestions, AnswerQuestions, ImplementationExecution, CodeReview, ReviewReconciliation, QuickImplement, BuildReview, PlanDiversion).

### `--AUTO-` prohibition

- [x] Promoted from footnote to the **first** commit-block instruction, with ✅/❌ contrast examples, in `Staff_ImplementationExecution.txt`, `Staff_ReviewReconciliation.txt`, `Human_PhaseApproval.txt`, and `Staff_QuickImplement.txt`.

### `last_action.summary` guidance

- [x] `plans/FORMATS.md` state.json section: `summary` states what was done and omits config-value citations for non-actions, "no X because…" explanations, and pause_type reasoning (with ✅/❌ example). Reminder added to `PM_StatusUpdate.txt`.

### Helper scripts

- [x] `plans/status.ps1`: added working-tree counts (staged / unstaged / untracked); moved the config block below the git block (action surface first, reference last).
- [x] `plans/sam-update.py`: copy-if-missing scaffolding — absent instance files are copied from the template (present ones never touched); verified `--apply` leaves an existing `config.json` byte-identical and re-runs are idempotent.
- [x] `plans/sam-update.py`: readable end-of-run SUMMARY block (unchanged / created / updated / scaffolded / skipped, with filenames for changed buckets) in both dry-run and `--apply`, replacing the single dense count line. (Feedback 2026-08-09.)

### Attribution

- [x] "An mjt.pub project" (linked) added near the top of root `README.md` and `plans/README.md`.
