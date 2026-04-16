# MILESTONE — B1-M2

## Goal
Add print support, shareable URL encoding/decoding with hash-based routing, interactive solve mode (click/drag highlighting, found-word tracking), and a solution toggle.

## Phases

### P1 — Print stylesheet
**What:** Add `@media print` CSS rules to `css/style.css` for a clean printed puzzle. Hide the input form, error messages, and any interactive buttons. Show only the title, grid, and word bank. Ensure the grid fits on a single page with appropriate margins and font sizing.
**Acceptance:**
- [ ] Browser print preview shows only the puzzle title, grid, and word bank — form and buttons are hidden
- [ ] Grid table fits on a single printed page without clipping or overflow
- [ ] Printed grid cells are legible (monospace, sufficient size) and grid lines are visible

### P2 — Share URL encoding & hash routing
**What:** Implement share-link encoding and decoding using hash-based routing (`#/v1/<encoded>`). Encode the word list and optional title into a compact URL-safe string (Base64 of JSON payload). Add a "Copy Share Link" button to the puzzle output. On page load, detect a hash route, decode the payload, regenerate the puzzle deterministically, and render it. Resolve BACKLOG P0 (hash-based routing chosen over `/v1/` paths since no server-side routing is available for a static site).
**Acceptance:**
- [ ] After generating a puzzle, a "Copy Share Link" button is visible in the puzzle output section
- [ ] Clicking the button copies a URL of the form `<origin>/#/v1/<base64>` to the clipboard
- [ ] Opening that URL in a new browser tab decodes the payload, regenerates the identical puzzle, and renders it automatically
- [ ] If the hash payload is malformed or missing, a user-friendly error is displayed instead of a blank page
- [ ] The input form is still accessible when arriving via a share link (user can create a new puzzle)

### P3 — Interactive solve UI
**What:** Add a solve mode to the rendered puzzle. Users click a starting cell then click an ending cell (or drag) to select a straight-line sequence of letters. If the selected letters match a placed word, highlight those cells as "found" and cross off the word in the word bank. Track solve progress (e.g., "3 of 8 words found"). The grid should visually distinguish found cells from unselected cells.
**Acceptance:**
- [ ] Clicking a start cell and an end cell selects all cells along the straight line between them
- [ ] Only valid straight lines are selectable (horizontal, vertical, or diagonal — matching the 8 directions)
- [ ] A correct selection highlights the cells with a persistent "found" style and crosses off the word in the word bank
- [ ] An incorrect selection (letters don't match any remaining word) is visually rejected (selection clears, no highlight persists)
- [ ] A progress indicator shows how many words have been found out of the total (e.g., "3 / 8 found")
- [ ] All found-word state is visual only (no persistence across page reload required)

### P4 — Solution toggle
**What:** Add a "Show Solution" / "Hide Solution" toggle button below the puzzle. When activated, highlight all cells belonging to placed words that have not yet been found by the solver. When deactivated, remove the solution highlights (found-word highlights remain). If all words are already found, the button should indicate that.
**Acceptance:**
- [ ] A "Show Solution" button appears below the puzzle output after generation
- [ ] Toggling it on highlights all unfound word placements with a distinct style (different from the "found" highlight)
- [ ] Toggling it off removes solution highlights; found-word highlights remain intact
- [ ] If all words have been found, the button text updates to indicate completion (e.g., "All words found!")
- [ ] Solution toggle works correctly whether invoked before or after partial solving

## Notes / Dependencies
- Hash-based routing chosen over path-based `/v1/<code>` because the app is a static site with no server-side routing — this resolves BACKLOG P0
- The existing `hashWords()` in `app.js` ensures the same word list always produces the same seed, so share links only need to encode the word list and title
- P3 depends on `placements` data from the generator (which includes word, row, col, direction) to validate selections
- Duplicate-word handling (BACKLOG P1) and URL-length documentation (BACKLOG P2) remain deferred to M3