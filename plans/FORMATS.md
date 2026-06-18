# FORMATS — Instance File Reference

This is a **system-level** file. It defines the expected structure of every instance-level
file in `plans/`. Reference this when creating or updating instance files.

**Key rule:** When an action generates or updates an instance file, replace all
template/placeholder content with real content. Do not preserve "About this file",
"Purpose", "When to update", or other explanatory preamble from the template stubs.

---

## BUILD.md

**What it is:** The multi-milestone plan for the current Build — a Build is a major body of work on the product. Describes what is being built, why, scope boundaries, success criteria, and milestone breakdown.
**Updated by:** Created by `Product.ProductVision`; reviewed (not modified) by `Principal.BuildReview`; updated when Build-level scope changes (including resize via `Principal.PlanDiversion`).

```
---
size: full | single-milestone | phase-only | step-only
---
# BUILD — <Build ID>

## Purpose
<What is being built and why — 2-4 sentences>

## Scope
### In scope
- <item>

### Out of scope
- <item>

## Success criteria
- <measurable outcome>

## Milestones
- M1 — <goal>
- M2 — <goal>   <!-- only for size: full -->

## Risks / assumptions
- <item>
```

### Size

The `size` frontmatter field is **required** and selects the planning depth for this build. It is chosen by `Product.ProductVision` (using any hint the human left in `thread.md`, or inferred from scope) and validated by `Principal.BuildReview` against the milestone breakdown. The four values:

| `size` | Milestones | Phases per M | Steps per P | Use case |
|---|---|---|---|---|
| `full` | 2+ (typical 3+) | 2+ | 2+ | Full prototype / major feature. Default ceremony. |
| `single-milestone` | exactly 1 | 2+ | 2+ | Substantial feature on an existing product. |
| `phase-only` | exactly 1 | exactly 1 | 2+ | Small feature; one cohesive chunk of work. |
| `step-only` | exactly 1 | exactly 1 | 1–3 | **Not a build** — cursory look, brief human check, implement. Use when the build process would cost more than the work itself (patches, dependency bumps, mechanical edits, well-scoped small fixes). Chosen by intent/risk, not step count. |

`step-only` uses a **carve-out route**: `Product.ProductVision` → `Human.ApproveBuild` (the one mandatory human touchpoint) → `Staff.QuickImplement` → done. It skips `Principal.BuildReview`, `Principal.MilestonePlan`, `Human.ApproveMilestone`, the Q&A loop, standalone `Principal.CodeReview` / `Staff.ReviewReconciliation`, `Writer.DocumentationUpdate`, `Human.PhaseApproval`, `PM.AdvancePhase`, and `PM.MilestoneCloseout`. Verification still happens — `Staff.QuickImplement` self-verifies — only the formal review *actions* are cut.

The other three sizes share the standard action chain (DraftQuestions → … → PhaseApproval). `size` only caps the number of milestones, phases, and steps that downstream actions may plan, independent of all `config.json` knobs. `phase-only` has exactly one phase, so `Writer.DocumentationUpdate` is skipped (`PM.AdvancePhase` short-circuits to `PM.MilestoneCloseout` and there is nothing to document yet at that point — closeout's CHANGELOG entry covers it).

### Prose depth scales with size

Artifacts (`BUILD.md`, `MILESTONE.md`, plans, reviews, documentation updates) **MUST** match prose depth to the declared `size`. An over-detailed artifact for a small size is a defect, not thoroughness — `Principal.BuildReview` flags size↔depth mismatches alongside size↔milestone-count mismatches.

- `step-only` — title + one-line goal + `size` frontmatter. Skip Scope / Success / Risks / Milestones sections unless something is genuinely non-obvious. Reviews and notes are a few bullets, not pages.
- `phase-only` — terse: a short paragraph (or a few bullets) per section. Only the one milestone / one phase that exists.
- `single-milestone` — current depth, but scoped to the one milestone.
- `full` — current depth.

Rule of thumb: the document's length should embarrass you if it doesn't match the size. If a `step-only` `BUILD.md` reads like a `full` one, trim it.

`Principal.PlanDiversion` may resize a build mid-flight; growing past the current size's caps requires the diversion to update `size` and re-route through `Human.ApproveBuild`.

**Missing frontmatter (legacy builds):** If `size` is absent from BUILD.md frontmatter (e.g., a pre-sizing Build that wasn't backfilled), downstream actions MUST treat the build as `size: full`. `Principal.BuildReview` should also flag the missing frontmatter as REQUIRED so the human can backfill an explicit value.

---

## MILESTONE.md

**What it is:** The multi-phase implementation plan for the current Milestone — a Milestone is one step in the Build's implementation. Contains phases, acceptance criteria, and technical approach.
**Updated by:** Created by `Principal.MilestonePlan`; replaced when switching to a new milestone; updated when phase definitions or acceptance criteria change.

```
# MILESTONE — <Build ID>-<Milestone ID>

## Goal
<One-sentence milestone goal>

## Phases

### P1 — <name>
**What:** <description of the work>
**Acceptance:**
- [ ] <testable criterion>

### P2 — <name>
**What:** <description>
**Acceptance:**
- [ ] <testable criterion>

## Notes / Dependencies
- <item>
```

---

## STATUS.md

**What it is:** The tactical snapshot of the repo right now — human-readable complement to `state.json` (the routing source of truth).
**Updated by:** Update frequency is configurable via `status_updates` in `config.json` (see below). By default (`pm_only`), only `PM.StatusUpdate` writes to STATUS.md; routing inserts `PM.StatusUpdate` after build/milestone approvals and plan diversions so major transitions are still captured. The one unconditional write is `Product.ProductVision`, which creates the file. Under `never`, STATUS.md is a frozen disabled-stub.

```
# STATUS

**Update configuration:** `status_updates=<value>`

## Now
- Build: <Build ID>
- Milestone: <Milestone ID>
- Phase: <Phase ID or "n/a">

## Blockers
- <brief bullet, or "None">

## Recent
- <what changed in the last action>

## Next
- <high-level next steps — routing detail is in state.json>
```

The `Update configuration` line shows the `status_updates` value at the time of the most recent write. It tells the reader the cadence STATUS is being kept at, which explains any apparent staleness (e.g., a one-phase lag is expected under `pm_only`/`every_milestone`). Every action that writes STATUS must refresh this line from `config.json`.

**Disabled stub** (used when `status_updates=never`):

```
# STATUS

_(STATUS updates disabled via config: status_updates=never)_
```

---

## BACKLOG.md

**What it is:** Prioritized list of pending work, bugs, follow-ups, and tech debt.
**Updated by:** `PM.StatusUpdate`, `PM.MilestoneCloseout`, `Staff.ReviewReconciliation` (when logging tech debt); also when priorities change or new work is discovered.

**Key rule:** BACKLOG tracks **future work items only**. Do not use BACKLOG for in-progress status, remaining tasks in the current phase, or implementation details. Those belong in `state.json` (e.g., `context.notes`) and `thread.md` respectively.

```
# BACKLOG

## P0 (do next)
- <item>

## P1
- <item>

## P2
- <item>
```

---

## CHANGELOG.md

**What it is:** Human-readable record of changes, including brief rationale for notable decisions.
**Updated by:** `PM.StatusUpdate` (per Phase), `PM.MilestoneCloseout` (appends milestone-complete entry under Unreleased). The "Unreleased" → "Released" move belongs to BUILD release, not milestone closeout — milestones are *completed*, not released.

```
# CHANGELOG

## Unreleased
- <item>

## Released
### YYYY-MM-DD
- <item>
```

---

## DECISIONS.md

**What it is:** Standing forward-looking decisions ("going forward, we will always…"). Durable project-specific choices that persist beyond the current milestone.
**Updated by:** `Principal.AnswerQuestions` and `PM.ThreadMaintenance` promote decisions here.

**Recording rule:** Record only if future work would benefit from knowing the rationale. If there is no meaningful rationale to preserve, don't log it.

**Record:** architectural patterns, data model constraints, API design principles, cross-cutting policies, decisions whose reasoning isn't obvious from the code.
**Don't record:** one-off implementation details, local code structure choices, temporary tradeoffs with no long-term relevance, decisions whose rationale is already self-evident in the code or commit message.

### Entry format

Every entry MUST include a `**Why this matters long-term:**` line. If you can't write a meaningful one, the entry doesn't belong here.

```
# DECISIONS

## Standing decisions
- **<short title>.** <decision — "going forward, we will always…"> (YYYY-MM-DD)
  **Why this matters long-term:** <the rationale a future contributor needs to make sense of this — the constraint, tradeoff, or context that justifies the choice>

## Deprecated decisions
- **<short title>.** <decision> (YYYY-MM-DD)
  **Why this matters long-term:** <why it was once true and why it no longer applies>
```

---

## STANDARDS.md

**What it is:** Team-level technical standards portable across projects — testing expectations, architecture rules, code style, quality bar. Keep concise and enforceable.
**Updated by:** `Principal.AnswerQuestions` and `PM.ThreadMaintenance` promote standards here; updated when project expectations change.

**Recording rule:** Record only if future work would benefit from knowing the rationale. If there is no meaningful rationale to preserve, don't log it.

**Record:** testing expectations, lint/style conventions, architecture rules, branching conventions, documentation expectations — rules that should apply across features and across projects.
**Don't record:** local code structure choices, one-off implementation details, project-specific decisions (those go in DECISIONS.md), guidance whose rationale is already self-evident in the code.

### Entry format

Every entry MUST include a `**Why this matters long-term:**` line. If you can't write a meaningful one, the entry doesn't belong here.

```
# STANDARDS

### Testing
- <standard>
  **Why this matters long-term:** <the rationale — quality bar, past incident, portability concern>

### Code style / lint
- <standard>
  **Why this matters long-term:** <rationale>

### Architecture constraints
- <standard>
  **Why this matters long-term:** <rationale>

### Branching convention
- <standard>
  **Why this matters long-term:** <rationale>

### Documentation
- <standard>
  **Why this matters long-term:** <rationale>
```

---

## thread.md — Append-Only Protocol

**What it is:** Active working memory for the project — a chronological log of questions, answers, review requests, feedback, and decisions. AI-readable, not machine-parseable.
**Updated by:** Most actions append to it; only `PM.ThreadMaintenance` may prune or restructure.

`thread.md` is an **append-only chronological log**. It is not a structured document
with permanent sections. Each action that writes to `thread.md` appends a new entry
at the end.

### Entry format

```
---
### [Action.ID] — YYYY-MM-DD
<content>
```

### Rules

1. **Append only.** Never delete, modify, or reorder existing entries.
2. **PM.ThreadMaintenance is the sole exception.** It may prune resolved content,
   compress verbose back-and-forth into brief summaries, and promote durable decisions
   to DECISIONS.md or STANDARDS.md.
3. **Use Q-### IDs for questions** (e.g., Q-001). Reference them by ID when answering.
4. **Review Requests and review feedback are separate entries.** Staff appends the
   request; Principal appends the feedback as the next entry, referencing the request.
5. **Keep entries concise and actionable.** The thread will be pruned periodically,
   but shorter entries delay the need for maintenance.

---

## config.json

**What it is:** Project-level workflow configuration — tunes process weight (which steps run, how strict reviews are) without changing the state machine or artifact contracts.
**Updated by:** Human only (manually edited). Never modified by any action. Missing file or missing key = default behavior (full process).

```
{
  "$schema": "config.schema.json",
  "code_review": "every_phase",
  "formal_approval": "every_phase",
  "documentation_update": "every_milestone",
  "review_strictness": "balanced",
  "re_review_trigger": "required",
  "status_updates": "pm_only",
  "workspace": {
    "primary_repo": {
      "name": "primary",
      "path": ".",
      "owns_plans": true
    },
    "shared_repos": []
  }
}
```

### Keys

| Key | Options | Default | Effect |
|-----|---------|---------|--------|
| `code_review` | `every_phase` \| `every_milestone` \| `never` | `every_phase` | When Principal.CodeReview runs after implementation |
| `formal_approval` | `every_phase` \| `every_milestone` \| `never` | `every_phase` | When Human.PhaseApproval runs |
| `documentation_update` | `every_phase` \| `every_milestone` \| `never` | `every_milestone` | When Writer.DocumentationUpdate runs |
| `review_strictness` | `strict` \| `balanced` \| `pragmatic` | `balanced` | Threshold for REQUIRED vs. SUGGESTED in code review |
| `re_review_trigger` | `required` \| `auto` | `required` | Whether code changes in reconciliation always trigger re-review |
| `status_updates` | `every_action` \| `pm_only` \| `every_milestone` \| `never` | `pm_only` | How often STATUS.md is written. `pm_only` and below write only via `PM.StatusUpdate` (routing fans approvals/diversions through it so major transitions are still captured) |
| `workspace` | object | single-repo placeholder | Multi-root workspace definition (primary repo + shared repos) |

For `every_milestone` options: the step runs only on the last phase of each milestone.
Templates consult this file when making routing decisions. See `config.schema.json` for full descriptions.

### `workspace` block

Defines the repos that participate in the workspace and how SAM routes artifact writes
across them. The block has two parts:

- `primary_repo` (required) — the repo that owns `plans/`. Exactly one per workspace.
  - `name` — human-readable name
  - `path` — absolute or workspace-relative path to the repo root
  - `owns_plans` — must be `true`
- `shared_repos` (optional, default `[]`) — repos that may receive code edits and
  `STANDARDS.md` / `DECISIONS.md` updates without their own `plans/` wrapper.
  - `name` / `path` / `role` — name, root path, and a brief description of the repo's role

**Explicit-identification rule:** SAM never infers the primary repo from cwd or `"."`.
If you use multi-root, set real workspace-relative paths for both `primary_repo.path`
and every `shared_repos[].path`. Single-repo projects can leave the placeholder defaults
(the `shared_repos` array is empty, so nothing matches shared scope and all writes go
to `primary_repo/plans/`).

### Scope-of-change routing

When an action edits files or records knowledge, classify the scope of each write and
route it accordingly. There are two scopes:

- **Project scope** — writes go to `primary_repo/plans/`. This is the default.
- **Shared scope** — writes go to a `shared_repos[]` location, with a *narrow* surface:
  - Code under `shared_repos[].path`
  - `shared_repos[].path/STANDARDS.md`
  - `shared_repos[].path/DECISIONS.md`
  - **No `plans/` wrapper** — shared repos never receive a `plans/` directory.

**Detection rule:** scope is determined by **path match**. If an edit's path is inside
any `shared_repos[].path`, that edit is shared scope. Everything else is project scope.
The `.code-workspace` file may inform context but is **not authoritative**.

**Project-scoped decisions about shared code stay in `primary_repo/plans/DECISIONS.md`.**
A decision affects shared scope only when its rationale is platform-wide (would apply to
any project using that shared code). Promotion from project DECISIONS/STANDARDS to a
shared repo's DECISIONS/STANDARDS is handled by `PM.ThreadMaintenance` with explicit
human approval — see `PM_ThreadMaintenance.txt` for the proposal/approval protocol.

---

## state.json

**What it is:** Routing source of truth — tracks the current position in the BUILD → MILESTONE → PHASE → STEP hierarchy and determines which action runs next. Validated by `state.schema.json`.
**Updated by:** Every action (mandatory). Must always reflect what just happened and what should happen next.

### `last_action.result` values

The `result` field MUST be one of these schema-valid enum values. Do NOT use "complete", "done", "success", or any other string.

| Value | When to use |
|-------|-------------|
| `ok` | Action completed successfully. Default for most actions (ProductVision, MilestonePlan, DraftQuestions, AnswerQuestions, ImplementationExecution, ReviewReconciliation, StatusUpdate, DocumentationUpdate, AdvancePhase, MilestoneCloseout, ThreadMaintenance, ResolveBlocker). |
| `approved` | A review or approval action approved the artifact (BuildReview, CodeReview, PhaseApproval, ApproveMilestone). |
| `changes_required` | A review found issues that must be addressed before proceeding (BuildReview, CodeReview). |
| `blocked` | Action cannot proceed; a blocker has been added to `blockers[]`. |
| `error` | Unexpected failure occurred; `Human.ResolveBlocker` is next. |
| `skipped` | Action was intentionally skipped (e.g., DraftQuestions self-skip when path is clear, DocumentationUpdate when no doc changes needed). |