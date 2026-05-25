# 6. Use Cases & User Stories

## 6.1 Actors

| Actor | Role |
|---|---|
| **Developer (terminal)** | Comfortable with the shell. Invokes `scribe` from a terminal, often in CI. |
| **Developer (GUI)** | Prefers a graphical workflow. Drops a path into the Streamlit UI. |
| **Maintainer** | Pre-existing project owner who wants to refresh an outdated README. |
| **Job seeker** | Wants to backfill READMEs across a portfolio of repos for a recruiter. |
| **System** | The Scribe process itself: analyzer + generator + LLM. |

## 6.2 Use case diagram (textual)

```
                  +------------------------------+
                  |          Scribe              |
                  |                              |
   (Developer T) >|  UC1 Generate README (CLI)   |
                  |                              |
   (Developer G) >|  UC2 Generate README (UI)    |
                  |                              |
   (Anyone)     >|  UC3 Inspect repo facts       |
                  |                              |
   (Anyone)     >|  UC4 Check status             |
                  +--------------+---------------+
                                 |
                                 | <<includes>>
                                 v
                  +------------------------------+
                  | UC5 Analyze repo             |
                  | UC6 Render deterministic     |
                  | UC7 Call LLM (per section)   |
                  +------------------------------+
```

## 6.3 Use case details

### UC1 — Generate README (CLI)

| Field | Value |
|---|---|
| **Actor** | Developer (terminal) |
| **Goal** | Produce a `README.md` for a local repo without leaving the shell. |
| **Precondition** | Ollama server is running and the default model is pulled. |
| **Trigger** | User runs `scribe generate ./path --output README.md`. |
| **Main flow** | 1. Scribe analyzes the path. 2. Pre-flight: `OllamaClient.ready()` returns OK. 3. For each of the eight sections, Scribe calls the model and streams tokens to the terminal while assembling the buffer. 4. Deterministic blocks (badges, file tree) are inserted at fixed points. 5. The assembled markdown is written to the output file. |
| **Alternate flow A** | If Ollama is not running, exit code 2 with a message telling the user to run `ollama serve`. |
| **Alternate flow B** | If the configured model is not pulled, exit code 2 with a message telling the user to run `ollama pull <model>`. |
| **Postcondition** | `README.md` exists on disk; the user can open it in their editor. |

### UC2 — Generate README (UI)

| Field | Value |
|---|---|
| **Actor** | Developer (GUI) |
| **Goal** | Same as UC1 but through a browser. |
| **Trigger** | User runs `scribe ui` (or `./scripts/dev.sh`). |
| **Main flow** | 1. Streamlit opens at `localhost:8501`. 2. User types or pastes a repo path. 3. User clicks **Generate README**. 4. Scribe streams sections into a live markdown preview pane. 5. When complete, a **Download README.md** button appears. |
| **Postcondition** | User has the README in their downloads folder. |

### UC3 — Inspect repo facts

| Field | Value |
|---|---|
| **Actor** | Anyone debugging the analyzer. |
| **Goal** | See exactly what Scribe would tell the LLM about a repo. |
| **Trigger** | `scribe analyze ./path` or `scribe analyze ./path --json`. |
| **Main flow** | Print the `RepoFacts` snapshot as Rich-formatted tables (human mode) or JSON (machine mode). No LLM call. |
| **Postcondition** | Caller can pipe the JSON into other tools or eyeball the tables. |

### UC4 — Check status

| Field | Value |
|---|---|
| **Actor** | Anyone. |
| **Goal** | Verify the environment is ready to generate. |
| **Trigger** | `scribe status`. |
| **Main flow** | Hit Ollama, list installed models, print OK or actionable error. |
| **Postcondition** | Exit code 0 if ready, 2 otherwise. |

## 6.4 User stories

| ID | As a... | I want to... | So that... |
|---|---|---|---|
| US-01 | new maintainer | point Scribe at a freshly cloned repo and get a draft README | I have something polished to start editing instead of a blank file |
| US-02 | job seeker | refresh READMEs across my GitHub portfolio in an afternoon | recruiters see consistent, professional documentation |
| US-03 | privacy-conscious dev | use an AI that doesn't send my code over the wire | my employer's NDA isn't violated |
| US-04 | non-CLI user | use a visual interface | I don't have to memorize command flags |
| US-05 | CI engineer | call `scribe` from a GitHub Action that fails the build when the README is stale | docs stay in sync with code |
| US-06 | curious dev | see what Scribe would tell the LLM, without actually invoking it | I can debug bad outputs |
| US-07 | offline traveller | generate READMEs on a plane | I don't depend on internet access |
