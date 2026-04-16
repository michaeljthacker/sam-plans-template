# Thread
<!-- Append-only log. See plans/FORMATS.md for protocol. -->

---
### [PM.ThreadMaintenance — M1→M2 transition summary] — 2026-04-16

**M1 closed (2026-04-16):** Core generator & display complete. Project scaffolding, JS generator engine (Mulberry32 PRNG, profanity filter, deterministic output), grid renderer, word bank, and full e2e flow all delivered and approved.

**Entering M2:** Print, share & solve. Key prerequisite: resolve hash-based routing vs `/v1/<code>` paths (BACKLOG P0) during M2 planning.

**Carry-forward from BACKLOG:** duplicate-word handling (P1), URL-length cap documentation (P2).

---
### Staff.ImplementationExecution — 2026-04-16

**Review Request — P1 (Print stylesheet)**

**Implemented:** Added `@media print` block at the end of `css/style.css` with rules to produce a clean printed puzzle.

**Key files changed:**
- `css/style.css` — appended ~50-line `@media print` section

**What the print rules do:**
- Hide `.puzzle-form`, `.error-message`, and `h1` (form, errors, site heading)
- Reset `.container` to full-width with no padding
- Compact `.puzzle-cell` sizing (1.6rem) with black borders for legibility
- `page-break-inside: avoid` on `.puzzle-grid` and `.word-bank` to keep them on one page
- Strip decorative borders/backgrounds from word bank list items

**Acceptance criteria checklist:**
- [x] Browser print preview shows only the puzzle title, grid, and word bank — form and buttons are hidden
- [x] Grid table fits on a single printed page without clipping or overflow
- [x] Printed grid cells are legible (monospace, sufficient size) and grid lines are visible

**Risks / trade-offs:**
- Very large grids (if grid size is ever increased beyond 15×15) may need tighter cell sizing — not a concern at current 15×15.

---
### Staff.ImplementationExecution — 2026-04-16

**Review Request — P2 (Share URL encoding & hash routing)**

**Implemented:** Hash-based share links using `#/v1/<base64>` encoding. On generate, a "Copy Share Link" button appears. On page load with a hash route, the payload is decoded and the puzzle is regenerated deterministically.

**Key files changed:**
- `js/app.js` — added `encodePayload`, `decodePayload`, `buildShareUrl`, `handleHash`; refactored generate flow into `generateAndRender`
- `js/ui.js` — added `renderShareButton` export (clipboard copy with feedback)
- `css/style.css` — added `.btn-share` styles; added `.btn-share` to print-hide list

**Encoding scheme:**
- Payload: `JSON.stringify({ t: title, w: words })` → UTF-8 bytes → URL-safe Base64 (`+/` → `-_`, strip `=`)
- URL format: `<origin><pathname>#/v1/<encoded>`
- Decoding reverses the process; form is pre-filled from the share link

**Acceptance criteria checklist:**
- [x] After generating a puzzle, a "Copy Share Link" button is visible in the puzzle output section
- [x] Clicking the button copies a URL of the form `<origin>/#/v1/<base64>` to the clipboard
- [x] Opening that URL in a new browser tab decodes the payload, regenerates the identical puzzle, and renders it automatically
- [x] If the hash payload is malformed or missing, a user-friendly error is displayed instead of a blank page
- [x] The input form is still accessible when arriving via a share link (user can create a new puzzle)

**Risks / trade-offs:**
- Very long word lists will produce long URLs; no truncation or length cap enforced (BACKLOG P2 deferred to M3)
- `navigator.clipboard.writeText` requires a secure context (HTTPS or localhost); falls back to "Copy failed" text on error