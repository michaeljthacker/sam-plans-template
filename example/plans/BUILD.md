# BUILD — B1

## Purpose
Build a fully functional, backend-free word search generator web app (wordsearch.mjt.pub). Users can create custom puzzles from a word list, view and print them, and share them via a compact URL that deterministically regenerates the same puzzle client-side.

## Scope

### In scope
- Word input UI (textarea, one word per line, optional title)
- Deterministic 15×15 grid generation (ported from Python reference in `archive/`)
- Weighted directional placement and profanity-filtered filler letters
- Grid + word bank display
- Clean print layout (`@media print`)
- Share link encoding/decoding (`/v1/<code>` routes)
- Shared-link route: decode → regenerate → render puzzle
- Interactive solve UI: click/drag to highlight words in the grid, confirm correct finds, cross off found words in the word bank, track solve progress
- Solution toggle (reveal all remaining word placements)
- Client-side routing (hash-based)
- Single-page static deployment (HTML/CSS/JS, no frameworks)

### Out of scope
- Backend / server-side storage
- User accounts or authentication
- Curated puzzle library (planned for a future build)
- Advanced sharing features / compression (future build)
- Mobile-native app
- Accessibility audit beyond basic semantic HTML (future build)

## Success criteria
- A user can enter words, generate a puzzle, and see it rendered in a grid with a word bank
- The same word list + seed produces the identical grid every time
- A user can print the puzzle with a clean layout
- A user can copy a share link; opening that link in another browser reproduces the exact puzzle
- A user can click/drag across grid letters to select a word; correct selections are confirmed and the word is crossed off the word bank
- Solve progress is tracked — the user can see which words remain
- The solution toggle correctly highlights all remaining placed words
- No profanity appears in filler letters
- The app runs entirely client-side with no backend dependency

## Milestones
- **M1** — Core generator & display: Port the Python generator to JS, build the grid renderer, and implement the create → generate → display flow
- **M2** — Print, share & solve: Add print stylesheet, URL encoding/decoding, shared-link routing, interactive solve UI (click/drag highlighting, found-word tracking), and solution toggle
- **M3** — Polish & deploy: Final styling, error handling, edge-case hardening, and deploy to wordsearch.mjt.pub

## Risks / assumptions
- The Python generator logic ports cleanly to JavaScript (the algorithm is straightforward; low risk)
- 15×15 grid with up to ~12 words will reliably place within retry limits in JS performance budget
- URL-encoded payloads stay within browser URL length limits for typical word lists (~10 words)
- Hash-based routing is sufficient for V1; no need for a build tool or server-side routing
- No framework dependency keeps bundle size trivial and deployment simple