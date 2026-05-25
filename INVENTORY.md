# Scribe — Folder Inventory

Everything for the second final-project deliverable lives in this single
folder:

```
~/Documents/GitHub/scribe
```

The folder is **fully self-contained** — code, docs, tests, slides, landing
page. You can move it to an external drive, zip it, or share it.

---

## Top-level map

| Path | Size | What's in it |
|---|---|---|
| `README.md` | 5 KB | Public-facing readme with badges + quickstart |
| `INVENTORY.md` | this file | What lives where |
| `CLAUDE.md` | 3 KB | Engineering context (for future AI sessions) |
| `pyproject.toml` | 1 KB | Python package metadata (`scribe` command) |
| `requirements.txt` | <1 KB | Pinned dependencies |
| `Dockerfile` | absent | Not needed — Scribe is local-first |
| `.env.example`, `.python-version`, `.gitignore` | small | Config |
| `.github/workflows/ci.yml` | <1 KB | GitHub Actions (lint + tests) |
| **`src/scribe/`** | 40 KB | The whole Python package |
| **`docs/`** | 80 KB | 14-section English documentation + cheat sheet |
| **`tests/`** | 16 KB | Unit + integration tests |
| **`scripts/`** | 8 KB | setup.sh, dev.sh, cleanup.sh |
| **`presentation/html/`** | 30 KB | Reveal.js slide deck (ink + paper) |
| **`landing/`** | 18 KB | Static landing page (Vercel-deployable) |
| **`examples/`** | small | Generated example READMEs |
| **`.venv/`** | ~600 MB | Python virtualenv with all deps |

---

## Where each thing is

### 🧠 Source code

```
src/scribe/
├── __init__.py
├── analyzer.py     # RepoAnalyzer + RepoFacts dataclass
├── generator.py    # ReadmeGenerator orchestrator
├── prompts.py      # SYSTEM_PROMPT + per-section templates
├── templates.py    # Deterministic sections (badges, file tree)
├── llm.py          # OllamaClient wrapper
├── cli.py          # Typer commands: generate, analyze, status, ui
└── ui.py           # Streamlit web app
```

### 📚 Documentation (14 sections + cheat sheet, all English)

```
docs/
├── 01-introduction.md
├── 02-problem.md
├── 03-objectives.md
├── 04-state-of-the-art.md
├── 05-requirements.md
├── 06-use-cases.md
├── 07-data-model.md
├── 08-class-diagrams.md
├── 09-mockups.md
├── 10-api-catalog.md
├── 11-testing.md
├── 12-architecture.md
├── 13-results.md
├── 14-future-work.md
└── 15-presentation-cheatsheet.md
```

### 🧪 Tests (22 passing)

```
tests/
├── __init__.py
├── conftest.py                       # Fixtures + StubOllamaClient
├── unit/
│   ├── test_analyzer.py              # 10 tests
│   ├── test_prompts.py               # 5 tests
│   └── test_templates.py             # 4 tests
└── integration/
    └── test_generator.py             # 3 tests
```

### 🔧 Scripts

```
scripts/
├── setup.sh        # venv + deps + Ollama check + model pull
├── dev.sh          # ensure Ollama running, then open Streamlit UI
└── cleanup.sh      # remove venv / caches / outputs (--hard deletes the repo)
```

### 🎤 Presentation

```
presentation/html/
├── index.html      # 12 slides — reveal.js
├── styles.css      # ink + amber + paper palette
└── README.md       # how to run / export PDF
```

### 🌐 Landing page

```
landing/
├── index.html      # static one-page site
├── styles.css      # same palette as the slides
├── vercel.json     # minimal Vercel config
└── README.md       # deploy instructions
```

---

## Running the project

### First-time setup

```bash
cd ~/Documents/GitHub/scribe

# 1. Install Ollama if you don't have it
brew install ollama
ollama serve &
ollama pull qwen2.5-coder:7b

# 2. Set up Python + Scribe
./scripts/setup.sh
```

### Daily use

```bash
source .venv/bin/activate

# Generate a README from any local repo
scribe generate ~/projects/something --output README.md

# Or open the web UI
scribe ui
```

### Tests

```bash
source .venv/bin/activate
pytest                              # all 22 tests
pytest --cov=src/scribe -q          # with coverage
```

### Cleanup

```bash
./scripts/cleanup.sh           # removes venv + caches
./scripts/cleanup.sh --hard    # additionally deletes the entire repo
ollama rm qwen2.5-coder:7b     # remove the model (frees ~4.7 GB)
```

---

## Quick verification (defense backup)

| What | Where | Expected |
|---|---|---|
| Tests pass | `pytest` | `22 passed` |
| CLI installed | `scribe --help` | Lists 4 commands |
| Ollama status | `scribe status` | `✓ OK — qwen2.5-coder:7b ready at http://localhost:11434` |
| Analyzer works on LeafLens | `scribe analyze ~/Documents/GitHub/leaflens --json \| jq .primary_language` | `"Python"` |
| Generator works on small repo | `scribe generate ~/Documents/GitHub/scribe --only title,description` | Prints title + Overview to stdout in ~10 s |

---

## Sister project

Project #1 lives at `~/Documents/GitHub/leaflens` — a houseplant
identification CV web app. Same author, same course. Independent
codebases, shared documentation style.

---

**Public repository**: https://github.com/luigy23/scribe

The git remote contains everything in this folder *except* the
virtualenv, the Ollama model cache, and example output. All of those are
gitignored because they're either huge, machine-specific, or generated.
