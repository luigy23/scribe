# Scribe — HTML presentation

Reveal.js slide deck, ink-and-paper aesthetic. Open in any browser, no build.

## How to view

```bash
# Easiest:
open index.html

# Or serve locally (better for PDF export):
python3 -m http.server 8000
```

## Keyboard shortcuts

| Key | Action |
|---|---|
| `→` / `Space` | Next slide |
| `←` | Previous |
| `S` | Speaker notes window |
| `F` | Fullscreen |
| `Esc` | Overview |

## Export to PDF

1. Start a server: `python3 -m http.server 8000`
2. Open `http://localhost:8000/?print-pdf` in Chrome
3. ⌘P → Save as PDF · Landscape · No margins · Background graphics ON
