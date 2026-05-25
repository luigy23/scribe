# 4. State of the Art

## 4.1 README generation

The task of generating a README from a code repository has a long but
shallow history. Three eras are visible.

### Template era (≤ 2018)

`cookiecutter`, `yeoman`, `create-react-app`, `npm init`, `cargo new`, and
similar bootstrappers all ship README templates. The user fills in
placeholders. The result is uniform and brand-recognizable but obviously
generic.

Notable projects: **README-template** by Othneildrew (~115 k stars on
GitHub), **best-README-template**, **awesome-readme**. All static markdown
skeletons with placeholders.

### Static-analysis era (2018 – 2022)

Tools that crawl a repository and emit a partial README without an LLM.

- `gitsome` and `gh` extensions list maintainers, contributors, language
  breakdown, license badge.
- `shields.io` provides badge endpoints fed from registry metadata.
- `readme-md-generator` (npm, ~9 k stars) walks `package.json` and
  generates a wizard-driven README; no LLM involved, very strict in shape.

These tools are good at deterministic facts (license, language, badges)
but cannot write the prose sections (description, features, usage notes).

### LLM era (2022 – present)

ChatGPT and Copilot popularized using LLMs to draft READMEs. The
common pattern is "paste your codebase into a chat, ask for a README".
Variants:

- **Cursor / Cursor Composer** — IDE-integrated, can use the open
  workspace as context. Cloud-only.
- **GitHub Copilot Chat** — same pattern, integrated into VS Code. Cloud
  with privacy settings.
- **`auto-readme-ai`**, **`ReadmeAI`** (PyPI) — open-source CLIs that hit
  the OpenAI or Anthropic API to generate a README from a folder. The
  state-of-the-art commercial endpoint.
- **`continue.dev`**, **`aider`** — agentic coding assistants that can be
  asked to write a README; cloud or local depending on configuration.

The clear gap in this wave is **first-class local LLM support**. Most of
the above either default to cloud or treat local as a second-class option.
Scribe sits in this gap.

## 4.2 Local LLMs

The local-LLM landscape exploded in 2023–2024 with three runtimes that
matter:

- **Ollama** (Go, MIT) — the de-facto standard for laptop developers. One
  command pulls and serves a quantized model behind an HTTP API at
  `localhost:11434`. Wide model catalog (Llama, Qwen, Mistral, Phi,
  CodeLlama, DeepSeek-Coder, Gemma). Excellent macOS / Linux / Windows
  support.
- **llama.cpp** (C++, MIT) — the low-level runtime that powers most of the
  others. Manual to use directly.
- **LM Studio** (closed, GUI) — desktop app for non-developers. Less
  scriptable than Ollama.

For a code-aware tool, the model selection matters as much as the
runtime. Models that consistently score well on coding tasks at the 7 B
parameter scale (HumanEval, MBPP, CodeXGLUE):

| Model | Size | License | Notes |
|---|---|---|---|
| **Qwen2.5-Coder 7B** | 4.7 GB Q4 | Apache 2.0 | Excellent code generation, fast |
| DeepSeek-Coder 6.7B | 4.0 GB Q4 | Permissive | Strong on Python/JS |
| CodeLlama 7B | 3.8 GB Q4 | Meta | Older, decent fallback |
| Llama 3.1 8B | 4.7 GB Q4 | Meta | General-purpose, weaker on code |
| Phi-3.5 Mini | 2.3 GB Q4 | MIT | Tiny but capable |

Scribe defaults to `qwen2.5-coder:7b` based on informal evaluation against
the other candidates: it produces the most accurate descriptions of
detected frameworks and the most natural prose.

## 4.3 Repository introspection

Several libraries already do part of what Scribe's analyzer does:

- **`github-linguist`** (Ruby) — GitHub's own language detector. Powers
  the language bar on every repo page. Overkill for an offline tool.
- **`tokei`** (Rust) — fast line counter by language.
- **`cloc`** (Perl) — venerable line counter.
- **`pip-tools`, `npm ls`, `cargo metadata`** — dependency walkers per
  ecosystem.

Scribe re-implements a minimal version of these in pure Python so it has
no native dependencies and can ship as a single Python wheel.

## 4.4 Gap addressed by Scribe

Three things together are uncommon:

1. **Local LLM as the default.** Most open-source README generators
   either don't use LLMs or default to cloud APIs.
2. **Deterministic + generative split.** Most LLM tools throw everything
   at the model. Scribe keeps the facts (badges, file tree) out of the
   model so they're guaranteed correct.
3. **Dual interface (CLI + Streamlit) from one engine.** Most tools pick
   one and stay there.

This combination is what makes Scribe novel at academic-project scale.

## References

- Hugging Face. *Qwen2.5-Coder Technical Report.* 2024.
- Ollama Team. *Ollama: Build a chat with local LLMs.* Documentation, 2024.
- Roziere, B. et al. *Code Llama: Open Foundation Models for Code.* arXiv:2308.12950.
- DeepSeek-AI. *DeepSeek Coder.* 2024.
- GitHub Linguist project, https://github.com/github-linguist/linguist.
