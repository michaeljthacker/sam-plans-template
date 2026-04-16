# Word Search Generator

A static, backend-free web app for creating word search puzzles — enter words, generate a 15×15 grid, and view the result instantly in the browser.

## What it does

Enter a list of words and an optional title, click **Generate**, and get a 15×15 word search puzzle with a word bank. The generator is deterministic: the same word list always produces the identical grid, powered by a seeded PRNG and a hash derived from the input.

## Current features

- **Create** — Enter words (one per line) with an optional title; click Generate
- **Display** — 15×15 grid of monospaced letter cells with a word bank listing all placed words
- **Deterministic output** — Same words always produce the same puzzle (seeded via input hash)
- **Input validation** — Rejects empty lists, words over 15 characters, non-alphabetic input, and banned words with user-facing error messages
- **Profanity filter** — Filler letters are checked so no banned words appear in any row, column, or diagonal

## Planned features

- Print layout (`@media print`)
- Share via URL (encode puzzle as a compact link that regenerates client-side)
- Interactive solve UI (click/drag highlighting, found-word tracking, solution reveal)

## Tech stack

- HTML / CSS / JavaScript (ES modules, no frameworks or build tools)
- Deterministic generator ported from the Python reference in `archive/`
- Seeded PRNG (Mulberry32) for repeatable grid generation
- Profanity filter using a curated word list

## Getting started

1. Clone the repository
2. Serve the project root with any static file server, e.g.:
   ```bash
   python -m http.server 3000
   ```
3. Open `http://localhost:3000` in a browser

No dependencies to install — the app is plain HTML/CSS/JS.

## Project structure

```
index.html          — Single-page entry point
css/style.css       — Layout and typography
js/app.js           — App entry point, wires form to generator and renderer
js/ui.js            — DOM helpers: renderPuzzle, showError, clearError
js/generator.js     — Deterministic word search engine (generate, hashWords)
```

## License

See [LICENSE](LICENSE).
