# 12. Architecture

## 12.1 Overview

Scribe is a small Python application that runs entirely on the user's
machine. The only "external" service is the local Ollama server, which
also runs on the same host. There is no database, no queue, no remote API.

```
┌─────────────────────────────────────────────────────────────────────┐
│                       User's machine                                │
│                                                                     │
│   ┌──────────────────────┐         ┌────────────────────────────┐   │
│   │      Scribe CLI      │         │    Scribe Streamlit UI     │   │
│   │  (Typer + Rich)      │         │    (localhost:8501)        │   │
│   └──────────┬───────────┘         └──────────────┬─────────────┘   │
│              │                                    │                 │
│              └──────────────┬─────────────────────┘                 │
│                             ▼                                       │
│       ┌──────────────────────────────────────────────────┐          │
│       │              src/scribe package                  │          │
│       │ ┌──────────────┐ ┌────────────────┐ ┌──────────┐ │          │
│       │ │ RepoAnalyzer │ │ ReadmeGenerator│ │ Prompts  │ │          │
│       │ └──────────────┘ └────────────────┘ └──────────┘ │          │
│       │ ┌──────────────────────────────┐                 │          │
│       │ │   OllamaClient (httpx)       │                 │          │
│       │ └──────────────┬───────────────┘                 │          │
│       └──────────────┬─┴───────────────────────────────┬─┘          │
│                      ▼                                 ▲            │
│         ┌─────────────────────────────┐                │            │
│         │  Ollama server (localhost   │                │            │
│         │  :11434) — qwen2.5-coder    │                │            │
│         └─────────────────────────────┘                │            │
│                                                                     │
│         ┌─────────────────────────────┐                │            │
│         │   User's repository on disk │ ◀── reads ─────┘            │
│         │   (~/projects/whatever)     │                              │
│         └─────────────────────────────┘                              │
└─────────────────────────────────────────────────────────────────────┘
```

## 12.2 Component responsibilities

### CLI (`src/scribe/cli.py`)

- Built on Typer; subcommands `generate`, `analyze`, `status`, `ui`.
- Reads arguments, calls the engine, formats output with Rich.
- Maps engine exceptions to actionable exit codes and stderr messages.

### Streamlit UI (`src/scribe/ui.py`)

- Single-page app with a sidebar for model/temperature/sections.
- Text input for the repository path.
- Live streaming preview while the LLM is generating.
- Download button delivers the final markdown.
- Status indicator shows whether Ollama is reachable.

### Engine layer

- `RepoAnalyzer` — walks the directory, parses manifests, builds a
  `RepoFacts` snapshot. Pure reads.
- `ReadmeGenerator` — iterates `SECTION_ORDER`, calls
  `OllamaClient.stream_chat()` per section, assembles markdown.
- `prompts` — section-scoped prompt templates.
- `templates` — deterministic sections (badges, project tree) that bypass
  the LLM entirely.

### LLM client (`src/scribe/llm.py`)

- Thin wrapper around the `ollama` Python package.
- Exposes `ready()`, `chat()`, `stream_chat()`.
- Translates underlying exceptions to two well-named errors:
  `OllamaUnavailableError` and `ModelNotPulledError`.

### Ollama server (out of process)

- Started independently with `ollama serve`.
- Holds the model in GPU/CPU memory between requests.
- Exposes an OpenAI-compatible HTTP API at `localhost:11434`.

## 12.3 Data flow (CLI generate, streaming)

```
1. User: scribe generate ./repo --output README.md
2. CLI resolves path, builds RepoAnalyzer.
3. RepoAnalyzer.analyze() returns RepoFacts.
4. CLI builds OllamaClient, calls ready().
5. CLI builds ReadmeGenerator(client).
6. For each section in SECTION_ORDER:
       a. prompts.<section>(facts) → string
       b. client.stream_chat([system, user]) yields tokens
       c. CLI prints tokens to stderr (live preview)
       d. CLI appends tokens to buffer
   After 'title': insert badges block (templates.render_badges)
   After 'development': insert project tree (templates.render_project_structure)
7. CLI writes buffer to --output and prints "✓ README written to ..."
```

## 12.4 Deployment topology

| Component | Location | Notes |
|---|---|---|
| Scribe package | User's `~/.local/lib/python3.13/site-packages/scribe` or `.venv` | Installed via `pip install scribe` (or `pip install -e .` from source). |
| Ollama server | User's machine | Started by `ollama serve`; or `./scripts/dev.sh` starts it. |
| Model weights | `~/.ollama/models/...` | ~4.7 GB for qwen2.5-coder:7b. |
| Streamlit UI | `localhost:8501` | Only reachable on the user's machine. |
| Landing page | https://scribe-luigy.vercel.app (planned) | Static HTML. No backend. |

The static landing page is the only piece that touches the network. The
actual tool is local-only by design.

## 12.5 Configuration

Two layers, in order of precedence (later wins):

1. CLI flags (`--model`, `--output`, `--port`).
2. Environment variables (`SCRIBE_MODEL`, `OLLAMA_HOST`, `LOG_LEVEL`).
3. Defaults baked into `src/scribe/llm.py` and `src/scribe/cli.py`.

No config file is read.

## 12.6 Scalability notes

Scalability is not a goal — Scribe is a personal tool. Concretely:

- Multiple concurrent generations on one machine are not supported (the
  Ollama server serializes requests anyway).
- Repos with tens of thousands of files take longer to analyze because the
  analyzer walks the whole tree. This is bounded by disk I/O, not CPU.
- The model context window (128 k for Qwen2.5-Coder) easily holds the
  per-section prompts; no chunking strategy is needed.

For a multi-user / multi-tenant deployment, the obvious move is to
package the engine as a Flask service in front of a cloud-hosted Ollama —
but that gives up the local-LLM property that is Scribe's main reason for
existing.
