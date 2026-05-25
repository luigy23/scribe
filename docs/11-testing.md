# 11. Testing

Scribe is covered by two layers of automated tests: **unit** tests for the
analyzer and the prompt/template modules, and **integration** tests for the
generator orchestrator that exercise the full section-assembly path with a
stub LLM client.

## 11.1 Strategy

| Layer | Verifies | Tooling | Location |
|---|---|---|---|
| Unit | Analyzer on synthetic fixture repos; prompt rendering; deterministic templates | pytest | `tests/unit/` |
| Integration | `ReadmeGenerator.generate()` and `.stream()` end-to-end with a `StubOllamaClient` | pytest | `tests/integration/` |

We deliberately do **not** exercise the real Ollama server in CI because
the model is gigabytes and the network is unreliable. The stub client is
the contract boundary.

Target coverage: **≥ 70% line coverage** on the `scribe` package, measured
with `pytest --cov=src/scribe`. Current measured coverage (after 22 tests):
≥ 78%.

## 11.2 Test inventory

### `tests/unit/test_analyzer.py`

- Primary-language detection on a Python fixture.
- Description extraction from `pyproject.toml`.
- Framework detection (Flask).
- Project signal detection (tests, CI, Docker, license).
- Python script entry-point extraction.
- File-tree rendering.
- Error path: missing directory.
- Error path: target is a file, not a directory.
- Ignore behavior: `node_modules` and `.venv` are skipped.
- README truncation when input is huge.

### `tests/unit/test_prompts.py`

- `SECTION_ORDER` is complete (all eight sections present).
- Each section prompt mentions the relevant facts.
- License-section branch toggles based on `has_license`.

### `tests/unit/test_templates.py`

- Badge rendering with a populated `RepoFacts`.
- Badge rendering returns an empty string when no signals are present.
- Project-structure rendering wraps the analyzer's tree in a fenced block.

### `tests/integration/test_generator.py`

- Generating all sections produces a markdown string starting with the
  title and containing every standard section heading.
- The subset path (`sections=["title", "features"]`) returns only those
  sections.
- Streaming emits `start`, `delta`, and `done` events in order, and the
  concatenation of `delta` payloads matches the final string.

## 11.3 Fixtures

`tests/conftest.py` defines:

- `fixture_repo` — a tmp_path containing a small Python project with
  `pyproject.toml`, a test directory, a CI workflow, a Dockerfile, and a
  short README.
- `example_facts` — a hand-crafted `RepoFacts` instance for prompt and
  template tests.
- `stub_client` — a `StubOllamaClient` that returns deterministic strings
  per section so the integration tests are fully offline.

## 11.4 Continuous integration

A GitHub Actions workflow at `.github/workflows/ci.yml` runs on every push
and pull request:

1. Set up Python 3.13.
2. Install Scribe in editable mode (`pip install -e .`) and dev deps.
3. Run `ruff check .`.
4. Run `pytest --cov=src/scribe --cov-report=xml`.
5. Upload coverage XML as an artifact.

## 11.5 Manual smoke tests (pre-defense checklist)

Some checks are easier to do by hand than to automate:

- `scribe status` returns OK after starting Ollama.
- `scribe analyze ~/Documents/GitHub/leaflens --json` returns valid JSON
  including `primary_language: "Python"` and frameworks including
  `"Flask"` and `"PyTorch"`.
- `scribe generate ./examples/tiny-flask-app --output /tmp/r.md` finishes
  in under 90 seconds with a warm model on the M4 Air.
- `scribe ui` opens the Streamlit page at `localhost:8501` and the
  download button delivers a file.
- Pulling the network cable does not affect any of the above (after the
  model is pulled).

## 11.6 Linting

`ruff` is the single source of truth for style. Configuration lives in
`pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP", "B"]
```

Run locally with `ruff check src tests` and `ruff format src tests`.
