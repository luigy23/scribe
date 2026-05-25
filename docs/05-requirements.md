# 5. Requirements

## 5.1 Functional requirements

| ID | Title | Description | Priority |
|---|---|---|---|
| FR-01 | Analyze repository | Given an absolute or `~`-prefixed path, walk the directory and return a `RepoFacts` snapshot. Skip ignored folders (`.git`, `node_modules`, `.venv`, `dist`, `build`, etc.). | High |
| FR-02 | Detect primary language | Identify the most common non-trivial language by file count. Markdown, YAML, and TOML do not count as primary. | High |
| FR-03 | Detect frameworks | Inspect Python, JavaScript, Rust, and Go dependency manifests and surface known frameworks. | High |
| FR-04 | Extract scripts | Read `[project.scripts]` from `pyproject.toml` and `"scripts"` from `package.json`. | High |
| FR-05 | Build file tree | Render the top three directory levels into a human-readable text tree. | Medium |
| FR-06 | Detect project signals | Surface presence of tests directory, CI workflow, Dockerfile, Makefile, license, changelog, contributing guide. | Medium |
| FR-07 | Generate README | Produce a markdown README from `RepoFacts` using the configured local model. Eight default sections. | High |
| FR-08 | Section selection | Allow the user to generate a subset of sections via `--only`. | Medium |
| FR-09 | Stream output | When `--stream` is set, surface tokens to stdout (or the UI) as they arrive. | High |
| FR-10 | Write to file | When `--output PATH` is set, write the assembled README to that file. | High |
| FR-11 | Status check | Provide a `scribe status` command that verifies the Ollama server is reachable and the model is pulled. | High |
| FR-12 | Web UI | Launch a Streamlit UI from `scribe ui`. The UI must show the parsed facts, stream the generation, and allow downloading the result. | High |
| FR-13 | Configurable model | Accept `--model TAG` on the CLI and as an env var (`SCRIBE_MODEL`). | Medium |
| FR-14 | Configurable host | Accept `OLLAMA_HOST` env var to point at a non-default Ollama endpoint. | Low |

## 5.2 Non-functional requirements

| ID | Title | Description | Priority |
|---|---|---|---|
| NFR-01 | Local execution | The default model must run on the user's own machine via Ollama; no calls to external APIs. | High |
| NFR-02 | No code execution | The analyzer must not run any project code, install dependencies, or hit the network. Pure file reads only. | High |
| NFR-03 | Latency | A full README for a small repo (≤ 30 source files) with a warm model: ≤ 90 seconds. | High |
| NFR-04 | Privacy | Repository contents must not be persisted server-side anywhere. The Ollama process runs on the user's host. | High |
| NFR-05 | Determinism (analyzer) | Re-running the analyzer on the same repo, at the same git SHA, yields identical facts. | High |
| NFR-06 | Memory footprint | Default model ≤ 6 GB RAM. The analyzer itself must be O(files) and stream rather than load everything. | High |
| NFR-07 | Disk footprint | The Python package itself ≤ 5 MB. The model is the user's responsibility (~ 4.7 GB for the default). | Medium |
| NFR-08 | Cross-platform | Run on macOS (Apple Silicon, Intel) and Linux. Windows-untested but no Mac-specific calls. | Medium |
| NFR-09 | Language | All user-facing strings, docs, code comments, and commit messages: English. | High |
| NFR-10 | Code quality | Python passes `ruff check .`. Tests are required for new functionality. | High |
| NFR-11 | Test coverage | ≥ 70% line coverage on `src/scribe/`. | Medium |
| NFR-12 | Helpful errors | A failure of any kind must explain to the user what action to take (start Ollama, pull the model, fix the path, etc.). | High |

## 5.3 Constraints

- **Solo developer**, ~3 days of focused work.
- Apple Silicon M4 Air, 16 GB unified RAM. Runs `qwen2.5-coder:7b` comfortably.
- No paid services; everything free.
- The instructor confirmed that **IoT is not required** for this project.

## 5.4 Assumptions

- The user has Python 3.11+ and Node 20+ available (Node only needed if
  the future Vercel landing page is built locally).
- The user is comfortable running `brew install ollama` and `ollama pull`.
- The repos the user points Scribe at are well-structured (have at least
  a manifest file). Untyped piles of scripts will still work but will
  produce sparser READMEs.
- The user reads the generated README before committing; Scribe is a
  draft-writer, not a fact-checker.
