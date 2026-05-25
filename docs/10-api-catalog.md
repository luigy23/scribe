# 10. API Catalog

Scribe does not expose an HTTP API. Its "API" is the CLI command surface
and a small public Python API for embedding the analyzer or generator in
other tools.

## 10.1 CLI commands

| Command | Purpose |
|---|---|
| `scribe generate` | Analyze a repo and produce a README. |
| `scribe analyze`  | Print the structured facts without calling the LLM. |
| `scribe status`   | Check Ollama and the configured model. |
| `scribe ui`       | Launch the Streamlit web UI. |

### `scribe generate`

```
scribe generate PATH
                [--output FILE | -o FILE]       # default: stdout
                [--model TAG | -m TAG]          # default: qwen2.5-coder:7b
                [--stream | --no-stream]        # default: --stream
                [--only SECTION,SECTION ...]    # subset of sections
                [--temperature FLOAT | -t FLOAT]# default: 0.2
```

**Behavior**:

1. Resolve `PATH` (must be an existing directory).
2. Run the analyzer; build `RepoFacts`.
3. Call `OllamaClient.ready()`; exit with code 2 if not ready.
4. If `--output` and `--stream`: stream tokens to stderr (visual feedback)
   while writing the full README to the file.
5. If no `--output`: print the assembled README to stdout (suitable for
   piping into editors).
6. Exit codes: `0` on success, `2` on user-fixable error (model missing,
   server down, path missing).

**Examples**:

```bash
scribe generate ./my-repo
scribe generate ./my-repo --output README.md
scribe generate ./my-repo --only title,description --no-stream
scribe generate ./my-repo --model llama3.2:3b
```

### `scribe analyze`

```
scribe analyze PATH [--json]
```

**Behavior**:

- Without `--json`: prints Rich tables / panels for languages,
  frameworks, dependencies, entry points, and the file tree.
- With `--json`: prints a JSON-serializable representation of the full
  `RepoFacts`, suitable for `jq` or pasting into another tool.

### `scribe status`

```
scribe status [--model TAG]
```

Returns exit code 0 if Ollama is reachable AND the model exists locally.
Otherwise prints an actionable message and exits with code 2.

### `scribe ui`

```
scribe ui [--port PORT] [--open / --no-open]
```

Spawns `streamlit run src/scribe/ui.py` with sensible defaults. The
process inherits the user's environment so `SCRIBE_MODEL` and
`OLLAMA_HOST` continue to apply.

## 10.2 Python API (for embedding)

```python
from scribe import RepoAnalyzer, ReadmeGenerator, OllamaClient

facts = RepoAnalyzer("./my-repo").analyze()
print(facts.primary_language, facts.frameworks)

client = OllamaClient(model="qwen2.5-coder:7b")
gen = ReadmeGenerator(client)
readme = gen.generate(facts)
```

For streaming use:

```python
for event in gen.stream(facts):
    if event.status == "delta":
        sys.stdout.write(event.payload)
        sys.stdout.flush()
```

## 10.3 Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` | Where to find the Ollama server. |
| `SCRIBE_MODEL` | `qwen2.5-coder:7b` | Default model tag. |
| `LOG_LEVEL` | `INFO` | Logging verbosity. |
| `SCRIBE_DEFAULT_OUTPUT` | `README.generated.md` | Default output filename if the user omits `--output` in the UI. |

## 10.4 Exit codes

| Code | Meaning |
|---|---|
| 0 | Success. |
| 2 | Pre-flight failure (server down, model missing, path invalid). |
| 1 | Unexpected error (uncaught exception). |
