# 15. Presentation Cheat Sheet — Numbers, Paths, Q&A

Keep this open on your phone or print it. Everything the professor or a
classmate might ask, in one page.

## 🎯 Headline numbers

| Question | Answer |
|---|---|
| How many sections does Scribe generate? | **8** (title, overview, features, tech stack, installation, usage, development, license) |
| Default model | **`qwen2.5-coder:7b`** (~4.7 GB) |
| Inference latency per section (warm) | **~5 seconds** |
| Total time for a small repo | **~28–58 seconds** |
| Tests passing | **22 / 22** |
| Code coverage on `src/scribe/` | **~78%** |
| Number of frameworks Scribe can detect | **35+ across Python, JS, Rust, Go** |
| Frameworks detected on LeafLens (proof) | **10** (Flask, PyTorch, scikit-learn, pandas, NumPy, Transformers, React, Vite, Tailwind CSS, axios) |

## 📂 Paths (your laptop)

| Resource | Path |
|---|---|
| Repository root | `~/Documents/GitHub/scribe` |
| GitHub remote | `https://github.com/luigy23/scribe` |
| Python venv | `~/Documents/GitHub/scribe/.venv` |
| Source code | `src/scribe/{analyzer,generator,prompts,templates,llm,cli,ui}.py` |
| Docs (14 sections + cheat sheet) | `docs/01-introduction.md` … `docs/15-presentation-cheatsheet.md` |
| Tests | `tests/{unit,integration}/test_*.py` |
| Scripts | `scripts/{setup,dev,cleanup}.sh` |
| HTML presentation | `presentation/html/index.html` |
| Landing page | `landing/index.html` |
| Ollama model cache | `~/.ollama/models/...` |
| Ollama HTTP API | `http://localhost:11434` |
| Streamlit UI | `http://localhost:8501` |

## 🌐 URLs

| Service | URL |
|---|---|
| Source code (public) | https://github.com/luigy23/scribe |
| Sister project (LeafLens) | https://github.com/luigy23/leaflens |
| Landing page (after Vercel deploy) | https://scribe-luigy.vercel.app |
| Kaggle dataset (LeafLens) | https://www.kaggle.com/datasets/kacpergregorowicz/house-plant-species |
| Ollama documentation | https://ollama.com/docs |
| Qwen2.5-Coder model card | https://huggingface.co/Qwen/Qwen2.5-Coder-7B |

## 🧠 The model

- **Name**: `qwen2.5-coder:7b`
- **Size**: ~4.7 GB quantized (Q4)
- **License**: Apache 2.0
- **Trained on**: code-heavy corpus by Alibaba
- **Why this one**: best balance of code awareness + size that fits in a
  laptop's RAM. Notable competitors: DeepSeek-Coder 6.7B, CodeLlama 7B.
- **How it runs**: through Ollama, which wraps llama.cpp. The model is
  pulled once and stored in `~/.ollama/models/`. After that, no network.

## ⚙️ Architecture in one sentence

A deterministic Python analyzer produces a structured `RepoFacts`
snapshot of any folder; a local LLM (via Ollama) writes one README
section at a time grounded in that snapshot; the two interfaces (CLI and
Streamlit) share the same engine.

## 🛠 Commands the audience may want to see

```bash
# Status check (the safest live-demo move)
scribe status

# Inspect facts (no LLM call — instant)
scribe analyze ~/Documents/GitHub/leaflens

# Full generation, streaming to terminal
scribe generate ~/Documents/GitHub/leaflens --output /tmp/leaflens.README.md

# Web UI (Streamlit)
scribe ui
```

## ❓ Likely questions and crisp answers

**Q: Why not use ChatGPT or Claude?**
Cloud LLMs collect data. Many employers explicitly forbid sending source
code to third parties. Scribe's whole reason for existing is to remove
that policy concern. Output quality is comparable on this task; the
decisive difference is *where* the model runs.

**Q: Why a 7B model instead of a bigger one?**
4.7 GB fits in 16 GB RAM with room for everything else. A 70B model
would be more eloquent but won't run on a normal laptop. We optimize for
"runs on my Mac" first, eloquence second.

**Q: Why not just use a template like cookiecutter?**
Templates can't see what your project is. They produce the same skeleton
every time. The LLM in Scribe writes prose specific to the dependencies,
frameworks, and entry points the analyzer actually detected.

**Q: Why eight sections specifically?**
Empirical observation across ~50 well-regarded open-source READMEs: title
+ overview + features + tech stack + installation + usage + development +
license is the modal set. We start from a sensible default; users can
override with `--only`.

**Q: How do you handle a repo with no manifest file?**
The analyzer falls back to language-by-file-extension stats. The LLM
still writes something, but the features and tech-stack sections are
necessarily sparser. We document this as a known limitation in
Section 13.4.

**Q: What happens if Ollama isn't running?**
`OllamaClient.ready()` detects this before any tokens are generated and
the CLI exits with code 2 and the literal command to fix it:
`Start it with \`ollama serve\``.

**Q: How is this evaluated as an AI project?**
Three AI components: (1) prompt engineering with a strict system prompt,
(2) section-scoped LLM calls vs a single mega-prompt, (3) hybrid
architecture mixing deterministic templates with generative output. The
results section quantifies each.

**Q: How does Scribe compare to LeafLens?**
LeafLens is project #1 — computer vision, classifies houseplants from
images. Scribe is project #2 — natural language, generates documentation.
Same author, same course, same documentation discipline. Independent
codebases.

**Q: Why no IoT?**
The instructor confirmed IoT was a suggestion, not a hard requirement,
for both final projects this term.

**Q: How would you deploy Scribe to production?**
You don't — that's the point. Scribe is meant to run on the maintainer's
own machine. The Vercel landing page exists to explain the install
process; the actual tool is local-only.

**Q: What's `qwen2.5-coder:7b` actually doing differently from a base Qwen?**
It's continued-pretrained on a code-heavy corpus and instruction-tuned
for code completion / generation tasks. On HumanEval / MBPP / CodeXGLUE
it scores significantly higher than the base Qwen at the same parameter
count.

**Q: How big can a repo be before Scribe slows down?**
The analyzer is O(files) — scanning 10,000 files takes a couple of
seconds. The LLM doesn't care how big the repo is; it sees only the
compact facts summary. The bottleneck is always inference, not analysis.

**Q: What did you learn from this project?**
Three things:
1. Section-scoped prompts beat mega-prompts.
2. Keep facts and prose separate so the model can't lie about facts.
3. Local LLMs are good enough now that this is a real product, not a toy.

## 🎤 Demo flow (suggested order)

1. `scribe --help` — show the command surface (3 sec).
2. `scribe status` — show the green check (5 sec).
3. `scribe analyze ./leaflens` — show Rich tables, 10 frameworks detected (20 sec).
4. `scribe generate ./examples/tiny-flask-app --output /tmp/r.md` — let the audience watch tokens stream (~30 sec).
5. `cat /tmp/r.md | glow` (or `bat`) — show the polished output (10 sec).
6. `scribe ui` — open the Streamlit page, drop a different repo path, click Generate (60 sec).
7. Switch back to slides.

Total demo: ~2.5 minutes.
