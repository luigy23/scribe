# Scribe — Project Context

## What this is

Final project #2 for the Artificial Intelligence course (BEINSOF52, Universidad Surcolombiana, Prof. Juan Antonio Castro Silva).

**Goal**: A locally-runnable AI tool that generates polished README.md files from any code repository. The user points it at a folder; Scribe analyzes the code, identifies language, frameworks, scripts, dependencies, and project structure, then asks a local LLM (via Ollama) to write a complete README.md.

## Sister project

Project #1 lives at `~/Documents/GitHub/leaflens` — a houseplant identification CV web app. Same author, same course, same deadline. Scribe is independent and self-contained.

## Rubric (this project counts 50% of the final project grade)

| Weight | Item | Status / plan |
|---|---|---|
| 10% | Presentation in English | docs/15-presentation-outline.md + presentation/ |
| 40% | Documentation in English | docs/01–14 |
| 5% | AI model | Local LLM via Ollama (qwen2.5-coder:7b) — counts as the AI |
| 10% | Best practices | Tests, ≥3 prompt/template strategies compared, clean separation of analyzer / generator / CLI, ruff + pytest + CI |
| 10% | Backend | Optional Flask wrapper exposing the generator over HTTP for the Streamlit UI |
| 10% | Frontend | Streamlit web UI (counts) + CLI with Rich (also counts) |
| 5% | Cloud deployment | Static landing page on Vercel/Netlify; the actual tool is local-only by design |
| 10% | IoT | **NOT REQUIRED** (instructor confirmed for both final projects) |

> The "modelo local + interface + terminal" phrasing from the instructor means the
> LLM must run locally (no remote API like OpenAI). Ollama satisfies this.

## Constraints

- Solo developer, ~3-day timeline
- Apple Silicon M4 Air, 16 GB RAM — runs Ollama 7B models comfortably
- No GPU on cloud (Render free tier won't run Ollama), so the tool ships as
  install-locally. The cloud deploy is a marketing/landing site.

## Architecture (high-level)

```
                ┌──────────────────────────┐
                │   User runs: scribe gen  │
                │   ./my-repo              │
                └──────────────┬───────────┘
                               ▼
                ┌──────────────────────────┐
                │     RepoAnalyzer         │
                │  walks the repo, builds  │
                │  a structured RepoFacts  │
                │  (languages, deps,       │
                │   scripts, structure)    │
                └──────────────┬───────────┘
                               ▼
                ┌──────────────────────────┐
                │   ReadmeGenerator        │
                │  iterates section        │
                │  templates, calls        │
                │  Ollama once per section │
                └──────────────┬───────────┘
                               ▼
                ┌──────────────────────────┐
                │       Ollama             │
                │   qwen2.5-coder:7b       │
                │   localhost:11434        │
                └──────────────┬───────────┘
                               ▼
                ┌──────────────────────────┐
                │   README.generated.md    │
                │   (or stdout, or         │
                │    Streamlit preview)    │
                └──────────────────────────┘
```

## Stack decisions

- **Python 3.13** — same as LeafLens, lets us reuse the .venv if we want
- **Typer** for the CLI — modern, type-driven, plays well with Rich
- **Rich** for terminal output — colored progress, panel preview of generated sections
- **Ollama Python client** — official, simple HTTP wrapper
- **Streamlit** for the web UI — fastest path to a usable visual interface
- **No database** — Scribe is stateless

## Conventions

- All code, docstrings, comments, commits, and user-facing strings: **English**
- Code style: `black`/`ruff` for Python, `prettier` if any JS/TS appears
- Tests required: unit + integration (rubric requirement)
- Section templates live in `src/scribe/prompts.py` so we can A/B them later
- Generated READMEs go to `examples/output/` during testing (gitignored)

## What's intentionally *not* done

- No persistent database / no analytics
- No multi-user / no auth
- No IoT (confirmed exempt for both final projects)
- No cloud hosting of the LLM itself — Ollama runs on the user's machine
