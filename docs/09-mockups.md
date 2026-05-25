# 9. GUI Mockups

Two interfaces ship with Scribe: a terminal interface (Typer + Rich) and a
web UI (Streamlit). Mockups for both are described in ASCII for portability.

## 9.1 Terminal UI — `scribe generate`

```
$ scribe generate ./my-project --output README.md
▸ title
# My Project

*A small utility for parsing CSV files into JSON.*

▸ badges
<div align="center">
 ![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB)
 ![License](https://img.shields.io/badge/License-MIT-blue)
</div>

▸ description
## Overview

My Project is a small utility for parsing CSV files into JSON. It targets
data engineers who need to ingest legacy reports into modern pipelines
without writing one-off parsers.

▸ features
## Features

- **Streaming reads** — handles files larger than RAM.
- **Type inference** — numbers, dates, and booleans recognised automatically.
- ...

✓ README written to README.md
```

Rich highlighting in real life: section headers in cyan, the markdown body
in the terminal default, the final checkmark in green.

## 9.2 Terminal UI — `scribe analyze`

```
$ scribe analyze .
╭─ Repository ──────────────────╮
│ Name: my-project              │
│ Path: /Users/me/code/my-project │
╰───────────────────────────────╯

┌─ Languages (by file count) ───┐
│ Language     │ Files          │
├──────────────┼────────────────┤
│ Python       │      14        │
│ Markdown     │       3        │
│ YAML         │       2        │
└──────────────┴────────────────┘

╭─ Frameworks ──────────────────╮
│ Flask, pytest, Pydantic       │
╰───────────────────────────────╯

╭─ Dependencies ────────────────╮
│ flask, pydantic, click, ...    │
╰───────────────────────────────╯

╭─ File tree ───────────────────╮
│  📁 src                       │
│    📁 my_project              │
│      · __init__.py            │
│      · main.py                │
│    📁 tests                   │
│      · test_main.py           │
│  · pyproject.toml             │
╰───────────────────────────────╯
```

## 9.3 Web UI — landing state

```
+---------------------------+----------------------------------------------+
|                           |                                              |
| 📝 Scribe                 |   📝 Scribe                                  |
| ─────────────────         |   *Drop a local repository path, get a       |
| Local LLM · Ollama        |    polished README.md back. The model runs   |
|                           |    on your own machine through Ollama.*      |
| Model:                    |                                              |
| [qwen2.5-coder:7b______]  |   Repository path                            |
|                           |   [ /Users/luigy/Documents/GitHub        ]   |
| Temperature: ──○─────     |                                              |
|              0.20         |   ╔══════════════════════╗                   |
|                           |   ║   Generate README    ║                   |
| Sections:                 |   ╚══════════════════════╝                   |
| [✓] title                 |                                              |
| [✓] description           |   ℹ Enter a path on the left and click       |
| [✓] features              |     Generate README.                         |
| [✓] tech_stack            |                                              |
| [✓] installation          |                                              |
| [✓] usage                 |   Scribe runs locally — your code does not   |
| [✓] development           |   leave this machine.                        |
| [✓] license               |                                              |
|                           |                                              |
| ── Status ──              |                                              |
| ✓ OK — qwen2.5-coder:7b   |                                              |
|   ready                   |                                              |
+---------------------------+----------------------------------------------+
```

## 9.4 Web UI — generating state

```
+---------------------------+----------------------------------------------+
|                           |   📝 Scribe                                  |
|  [ sidebar same ]         |                                              |
|                           |   ┌─ Repo facts ────────┐                    |
|                           |   │ Languages   12       │  ┌─ Generated ──┐ |
|                           |   │ Files       137      │  │              │ |
|                           |   │ Frameworks  5        │  │ # My Project │ |
|                           |   │                      │  │              │ |
|                           |   │ [▶ Full facts]       │  │ *A small     │ |
|                           |   └──────────────────────┘  │  utility …* │ |
|                           |                              │              │ |
|                           |   Progress: ███████░░░ 7/8   │ ## Overview  │ |
|                           |                              │              │ |
|                           |   Generating: development…   │ ...          │ |
|                           |                              │              │ |
+---------------------------+   --------------------       └──────────────┘ +
```

## 9.5 Web UI — final state

```
                              ┌─ Generated README ──────────┐
                              │                             │
                              │ # My Project                │
                              │ *A small utility for ...*   │
                              │                             │
                              │ ## Overview                 │
                              │ My Project is a small ...   │
                              │                             │
                              │ ## Features                 │
                              │ - Streaming reads ...       │
                              │                             │
                              │ ... full content ...        │
                              │                             │
                              └─────────────────────────────┘
                              ╔════════════════════════╗
                              ║  Download README.md    ║
                              ╚════════════════════════╝
```
