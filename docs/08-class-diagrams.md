# 8. Class Diagrams

Scribe is organized in three thin layers: an **analyzer**, a **generator**,
and a pair of **interfaces** (CLI and Streamlit UI). All three depend on a
shared **LLM client**. No domain entities, no ORM — see Section 7.

## 8.1 Core classes

```
+--------------------------+
|       RepoFacts          |  <<dataclass>>
+--------------------------+
| path: str                |
| name: str                |
| description: str | None  |
| languages: dict          |
| primary_language: str    |
| frameworks: list[str]    |
| package_managers: list   |
| dependencies: list[str]  |
| dev_dependencies: list   |
| has_tests: bool          |
| has_ci: bool             |
| has_dockerfile: bool     |
| has_makefile: bool       |
| has_license: bool        |
| license_name: str | None |
| entry_points: list[str]  |
| npm_scripts: dict        |
| python_scripts: dict     |
| file_tree: str           |
| existing_readme: str|None|
+--------------------------+
| to_dict() -> dict        |
| to_json() -> str         |
+--------------------------+
              ▲ produces
              |
+--------------------------+
|       RepoAnalyzer       |
+--------------------------+
| path: Path               |
+--------------------------+
| analyze() -> RepoFacts   |
| _scan_language_stats()   |
| _read_python_manifest()  |
| _read_npm_manifest()     |
| _read_cargo_manifest()   |
| _read_go_manifest()      |
| _detect_project_signals()|
| _read_existing_readme()  |
| _build_file_tree()       |
| _derive_summary()        |
+--------------------------+
```

```
+------------------------------+
|     OllamaClient             |
+------------------------------+
| model: str                   |
| host: str                    |
| timeout: float               |
+------------------------------+
| ready() -> (bool, str)       |
| chat(messages) -> str        |
| stream_chat(messages) -> Iter|
+------------------------------+
              ▲ uses
              |
+------------------------------+
|     ReadmeGenerator          |
+------------------------------+
| client: OllamaClient         |
+------------------------------+
| generate(facts,              |
|          sections,           |
|          on_progress,        |
|          temperature)        |
|     -> str                   |
| stream(facts, ...) -> Iter   |
| _render_section(...)         |
| _stream_section(...)         |
+------------------------------+
              ▲ depends on
              |
+------------------------------+
|     prompts.py (module)      |
+------------------------------+
| SYSTEM_PROMPT: str           |
| SECTION_ORDER: tuple         |
| PROMPT_BY_SECTION: dict      |
| prompt_title(facts)          |
| prompt_description(facts)    |
| prompt_features(facts)       |
| prompt_tech_stack(facts)     |
| prompt_installation(facts)   |
| prompt_usage(facts)          |
| prompt_development(facts)    |
| prompt_license(facts)        |
+------------------------------+

+------------------------------+
|     templates.py (module)    |
+------------------------------+
| render_badges(facts) -> str  |
| render_project_structure(...)|
| render_table_of_languages(...)|
+------------------------------+
```

## 8.2 Interfaces (CLI + Streamlit)

The two interfaces are independent entry points but share the engine.

```
                ┌────────────────────────────┐
                │     scribe.cli.app         │  <<typer.Typer>>
                ├────────────────────────────┤
                │ generate(path, output, ...)│
                │ analyze(path, json_out)    │
                │ status(model)              │
                │ ui(port, open_browser)     │
                └──────────────┬─────────────┘
                               │
                               ▼
        ┌─────────────────────────────────────┐
        │ shared engine layer                 │
        │   RepoAnalyzer + ReadmeGenerator    │
        │   + OllamaClient                    │
        └─────────────────────────────────────┘
                               ▲
                               │
                ┌────────────────────────────┐
                │     scribe.ui (Streamlit)  │
                ├────────────────────────────┤
                │ page layout + sidebar      │
                │ path input + Go button     │
                │ live streaming preview     │
                │ Download README button     │
                └────────────────────────────┘
```

## 8.3 Sequence — generating a README (CLI, streaming)

```
User             scribe.cli         RepoAnalyzer    ReadmeGenerator    OllamaClient    Ollama
 │ generate ./repo                   │                │                  │              │
 ├──────────────▶│ analyze(path)     │                │                  │              │
 │               ├──────────────────▶│                │                  │              │
 │               │                   │ walk + parse   │                  │              │
 │               │◀───── RepoFacts ──┤                │                  │              │
 │               │ client.ready()                     │                  │              │
 │               ├───────────────────────────────────▶│ HTTP GET /       ├─────────────▶│
 │               │                                    │◀─ alive ─────────┤              │
 │               │ for each section in SECTION_ORDER: │                  │              │
 │               │   generator.stream(...)            │                  │              │
 │               ├──────────────────────────────────▶│ build prompt     │              │
 │               │                                    ├─── chat(stream) ▶│              │
 │               │                                    │                  ├──── POST ───▶│
 │               │                                    │                  │◀── tokens ───┤
 │               │◀── GenerationEvent(delta, …) ──────┤                  │              │
 │ stdout token  │                                    │                  │              │
 │◀──────────────┤                                    │                  │              │
 │               │   ...                              │                  │              │
 │               │ writes file at --output            │                  │              │
 │◀── ✓ saved ───┤                                    │                  │              │
```
