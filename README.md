<div align="center">

# 📝 Scribe

**Local-LLM-powered README generator for code repositories.**
Point it at any folder. Get a polished `README.md` back. No data leaves your machine.

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Ollama-local-000?logo=ollama&logoColor=white)](https://ollama.com/)
[![Typer](https://img.shields.io/badge/Typer-CLI-009688)](https://typer.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-Academic-blue)](#license)

</div>

---

## ✨ What it does

Scribe walks the directory you point at, identifies the language, frameworks, scripts,
dependencies, and structure, and then asks a **local large language model** (via Ollama)
to write a complete `README.md` — title, badges, description, features, installation,
usage, project structure, development notes, tests, license.

Two interfaces, same engine:

- 🧙‍♂️ **Terminal**: `scribe generate ./my-repo --output README.md`
- 🖥 **Web UI**: `scribe ui` opens a Streamlit app at `localhost:8501`

The model runs **on your own machine** through [Ollama](https://ollama.com).
No cloud, no API key, no data leaves the laptop.

---

## 🚀 Quickstart

```bash
# 1. Install Ollama and pull the model (one-time)
brew install ollama
ollama serve &              # start the local server
ollama pull qwen2.5-coder:7b

# 2. Install Scribe
git clone https://github.com/luigy23/scribe
cd scribe
./scripts/setup.sh

# 3. Generate a README for any repo on your machine
source .venv/bin/activate
scribe generate ~/projects/my-cool-project --output README.md

# 4. Or open the web UI
scribe ui
```

---

## 🧠 Why local?

Cloud LLMs (OpenAI, Anthropic, Google) are convenient but they require:
- An internet connection
- An API key with billing attached
- Sending your code to a third party

For a small developer tool, all three are friction. Ollama lets us run a strong
coding model (`qwen2.5-coder:7b`, ~4.7 GB) on a normal laptop with no setup beyond
`brew install ollama`. Scribe is built on top of that.

---

## 🏗️ Architecture

```
              ┌──────────────────────────┐
   user  ───▶ │      RepoAnalyzer        │   walks the repo, builds RepoFacts
              │  (languages, deps,       │   (a structured snapshot)
              │   scripts, structure)    │
              └────────────┬─────────────┘
                           ▼
              ┌──────────────────────────┐
              │    ReadmeGenerator       │   iterates section templates
              │  (deterministic facts +  │   and calls the LLM once per
              │   LLM-written prose)     │   section
              └────────────┬─────────────┘
                           ▼
              ┌──────────────────────────┐
              │    Ollama (local)        │   qwen2.5-coder:7b
              │    localhost:11434       │
              └────────────┬─────────────┘
                           ▼
              README.generated.md  ·  Streamlit preview  ·  stdout
```

Full architecture details: [`docs/12-architecture.md`](docs/12-architecture.md).

---

## 🧰 Tech stack

- **CLI**: Typer + Rich (colored output, live progress, section previews)
- **Web UI**: Streamlit (file picker, JSON-of-facts inspector, downloadable result)
- **LLM client**: `ollama` Python package (HTTP to `localhost:11434`)
- **Default model**: `qwen2.5-coder:7b` — picked for code-aware completions
- **Analyzer**: pure Python, parses `pyproject.toml`, `package.json`, `Cargo.toml`,
  `go.mod`, `requirements.txt`, `Dockerfile`, `.github/workflows/*`, etc.
- **Templating**: Jinja2 for deterministic sections (project tree, badges)

---

## 📁 Project structure

```
scribe/
├── src/scribe/         # main Python package
│   ├── analyzer.py     # RepoAnalyzer + RepoFacts dataclass
│   ├── generator.py    # ReadmeGenerator orchestrator
│   ├── prompts.py      # Section templates (system + user prompts)
│   ├── llm.py          # Ollama client wrapper
│   ├── templates.py    # Deterministic sections (tree, badges, etc.)
│   ├── cli.py          # Typer CLI entry point
│   └── ui.py           # Streamlit UI entry point
├── docs/               # 14-section English documentation set
├── tests/              # pytest unit + integration tests
├── scripts/            # setup, dev, cleanup
├── examples/           # Real READMEs generated from real repos
├── presentation/       # Slide deck (pptx + HTML)
└── landing/            # Static landing page (deployed to Vercel)
```

---

## 🛠️ Commands

```bash
# Generate a README from any repo
scribe generate ./path/to/repo --output README.md

# Stream the generation live to stdout instead of writing a file
scribe generate ./path/to/repo --stream

# Use a different local model
scribe generate ./path/to/repo --model llama3.2:3b

# Just inspect the facts the analyzer would extract (no LLM call)
scribe analyze ./path/to/repo

# Check the Ollama server and selected model are ready
scribe status

# Open the web UI
scribe ui
```

---

## 📚 Documentation

Full English documentation in [`docs/`](docs/):

1. [Introduction](docs/01-introduction.md)
2. [Problem](docs/02-problem.md)
3. [Objectives](docs/03-objectives.md)
4. [State of the Art](docs/04-state-of-the-art.md)
5. [Requirements](docs/05-requirements.md)
6. [Use Cases](docs/06-use-cases.md)
7. [Data Model](docs/07-data-model.md)
8. [Class Diagrams](docs/08-class-diagrams.md)
9. [GUI Mockups](docs/09-mockups.md)
10. [API Catalog](docs/10-api-catalog.md)
11. [Testing](docs/11-testing.md)
12. [Architecture](docs/12-architecture.md)
13. [Results & Discussion](docs/13-results.md)
14. [Future Work](docs/14-future-work.md)

---

## 🧹 Cleanup

```bash
./scripts/cleanup.sh           # removes venv, examples/output, caches
./scripts/cleanup.sh --hard    # additionally deletes the entire repo
```

To remove the Ollama model: `ollama rm qwen2.5-coder:7b`.

---

## License

Academic project for the **Artificial Intelligence** course (BEINSOF52) at
**Universidad Surcolombiana**, May 2026.

Author: **Luigy Leonardo** ([@luigy23](https://github.com/luigy23))
Instructor: **Juan Antonio Castro Silva**
