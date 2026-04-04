# FORMATS — Instance File Reference

This is a **system-level** file. It defines the expected structure of every instance-level
file in `plans/`. Reference this when creating or updating instance files.

**Key rule:** When an action generates or updates an instance file, replace all
template/placeholder content with real content. Do not preserve "About this file",
"Purpose", "When to update", or other explanatory preamble from the template stubs.

---

## BUILD.md

**What it is:** The multi-milestone plan for the current Build — a Build is a major body of work on the product. Describes what is being built, why, scope boundaries, success criteria, and milestone breakdown.
**Updated by:** Created by `Product.ProductVision`; reviewed (not modified) by `Principal.BuildReview`; updated when Build-level scope changes.

```
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
- M2 — <goal>

## Risks / assumptions
- <item>
```

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
**Updated by:** Every action (mandatory). Must always reflect current Build/Milestone/Phase position.

```
# STATUS

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

---

## BACKLOG.md

**What it is:** Prioritized list of pending work, bugs, follow-ups, and tech debt.
**Updated by:** `PM.StatusUpdate`, `PM.MilestoneCloseout`, `Staff.ReviewReconciliation` (when logging tech debt); also when priorities change or new work is discovered.

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
**Updated by:** `PM.StatusUpdate` (per Phase), `PM.MilestoneCloseout` (moves Unreleased to dated release).

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

```
# DECISIONS

## Standing decisions
- <decision — "going forward, we will always…">

## Deprecated decisions
- <decision>
```

---

## STANDARDS.md

**What it is:** Team-level technical standards portable across projects — testing expectations, architecture rules, code style, quality bar. Keep concise and enforceable.
**Updated by:** `Principal.AnswerQuestions` and `PM.ThreadMaintenance` promote standards here; updated when project expectations change.

```
# STANDARDS

### Testing
- <standard>

### Code style / lint
- <standard>

### Architecture constraints
- <standard>

### Branching convention
- <standard>

### Documentation
- <standard>
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
