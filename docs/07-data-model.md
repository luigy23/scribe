# 7. Data Model

Scribe is a **stateless** tool. It does not own a database, does not
persist anything between invocations, and does not log analytics anywhere.
Its only "data model" is the in-memory snapshot the analyzer builds.

This is by design: every persistent store you add to a developer tool
becomes another thing the user must trust, back up, and clean up.

## 7.1 The `RepoFacts` snapshot

Conceptually, an immutable record produced once per `scribe` invocation.
Defined in `src/scribe/analyzer.py` as a frozen dataclass.

| Field | Type | Origin | Notes |
|---|---|---|---|
| `path` | str | argv | Absolute path of the repo on disk |
| `name` | str | directory name | Used as a fallback project title |
| `description` | str \| None | manifest or existing README | First non-trivial paragraph |
| `languages` | dict[str, int] | file extensions | Counts per language |
| `primary_language` | str \| None | derived | Most common non-trivial language |
| `total_files` | int | walk | Files visited (excluding ignored dirs) |
| `total_lines` | int | walk | Lines counted across source files |
| `frameworks` | list[str] | dependency match | e.g. `["Flask", "React"]` |
| `package_managers` | list[str] | manifest presence | `["pip", "npm", "cargo", ...]` |
| `dependencies` | list[str] | manifests | Truncated to 30 |
| `dev_dependencies` | list[str] | manifests | Truncated to 30 |
| `has_tests` | bool | `tests/` directory | |
| `has_ci` | bool | `.github/workflows/` etc. | |
| `has_dockerfile` | bool | `Dockerfile` at root | |
| `has_makefile` | bool | `Makefile` at root | |
| `has_license` | bool | `LICENSE*` at root | |
| `license_name` | str \| None | first 500 chars of LICENSE | MIT / Apache-2.0 / GPL / BSD |
| `has_changelog` | bool | `CHANGELOG*` at root | |
| `has_contributing` | bool | `CONTRIBUTING*` at root | |
| `entry_points` | list[str] | pyproject + npm | Names only |
| `npm_scripts` | dict[str, str] | `package.json` `"scripts"` | name → command |
| `python_scripts` | dict[str, str] | `pyproject.toml` `[project.scripts]` | name → target |
| `file_tree` | str | walk | Pre-rendered text tree, ≤ 80 entries |
| `notable_files` | list[str] | top-level inspection | Currently unused, reserved |
| `existing_readme` | str \| None | `README.*` if present | Truncated to 6000 chars |
| `existing_readme_truncated` | bool | derived | |

## 7.2 Transient data during a generation

The generator constructs short-lived objects that never escape the
process:

- `ChatMessage(role, content)` — a single message in an Ollama chat call.
- `GenerationEvent(section, status, payload)` — emitted by `stream()`
  during a generation; consumed by the CLI or UI for live preview.

None of these are written to disk.

## 7.3 What is intentionally NOT stored

| Concept | Status | Reason |
|---|---|---|
| Generated README history | Not stored | The user owns the file. |
| Prediction analytics | Not stored | Scribe has no telemetry. |
| User identity | None | Scribe is single-user, local. |
| Model output cache | None (yet) | Could be added — see Section 14. |
| Prompts archive | Source-controlled in `src/scribe/prompts.py` | Versioned in git, not in a DB. |

## 7.4 ER diagram (not applicable)

Because Scribe is stateless and has no persistent entities, there is no
entity-relationship diagram. The equivalent shape lives in the class
diagrams (Section 8).
