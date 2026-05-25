# Scribe landing page

Static site that explains what Scribe is and how to install it.
No build step. Deployable to Vercel, Netlify, or GitHub Pages as-is.

## Files

- `index.html` — single-page layout
- `styles.css` — sage-paper visual language (matches the slide deck)
- `vercel.json` — minimal Vercel config with security headers

## Deploy to Vercel

```bash
# Install once if needed
npm i -g vercel

cd landing
vercel deploy --prod
```

Vercel auto-detects this as a static site (no `package.json`) and serves
`index.html`.

## Deploy to GitHub Pages

In the repo settings → Pages → set source to `landing/` on the `main`
branch. Done.

## Local preview

```bash
cd landing
python3 -m http.server 8000
# visit http://localhost:8000
```
