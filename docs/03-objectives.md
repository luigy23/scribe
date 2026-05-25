# 3. Objectives

## General objective

Design and implement a small, locally-runnable tool that produces a polished
`README.md` for any code repository given only a path on disk, by combining
a deterministic repository analyzer with a locally-hosted large language
model.

## Specific objectives

1. **Build a deterministic repository analyzer.**
   Walk the directory, detect languages by file extension, parse the
   manifest files of the major package managers (`pyproject.toml`,
   `requirements.txt`, `package.json`, `Cargo.toml`, `go.mod`), surface
   entry-point scripts, and produce a structured `RepoFacts` snapshot
   suitable for prompt insertion.

2. **Integrate a local LLM through Ollama.**
   Use the official `ollama` Python client. Default to
   `qwen2.5-coder:7b`. Provide a `ready()` check that distinguishes
   "server not running" from "model not pulled" so error messages are
   actionable.

3. **Compose section-scoped prompts.**
   Avoid a single mega-prompt; instead, generate the README section by
   section so each call stays within the model's context window and the
   output is easier to validate. Cover at least eight standard sections:
   title, description, features, tech stack, installation, usage,
   development, license.

4. **Keep deterministic sections out of the LLM.**
   Render badges and the project file tree from the analyzer's facts
   directly, so those parts cannot hallucinate.

5. **Expose two interfaces.**
   A Typer CLI with Rich-formatted output for terminals and CI, and a
   Streamlit web UI for visual users — both backed by the same engine.

6. **Stream output to the user.**
   For interactive use, surface tokens as they arrive so a long
   generation feels responsive.

7. **Cover the system with automated tests.**
   Unit tests for the analyzer on synthetic fixture repos; integration
   tests for the generator using a stub LLM client; total ≥ 70% line
   coverage on the `scribe` package.

8. **Document the project in English.**
   Produce the full fourteen-section documentation set required by the
   course rubric.

9. **Ship a small landing page.**
   A static page on Vercel that explains what Scribe is and how to install
   it. The actual tool is local-only by design, so this landing page
   satisfies the cloud-deployment portion of the rubric without
   compromising the local-LLM constraint.

10. **Prepare an English presentation.**
    Twelve-slide deck for the in-class defense, plus a one-page cheat
    sheet of numbers and paths to use during Q&A.

## Success criteria

| Criterion | Target |
|---|---|
| Analyzer correctly identifies primary language on the LeafLens repo | matches "Python" |
| Analyzer detects ≥ 8 frameworks on the LeafLens repo | yes |
| Smoke test: generates a README for Scribe itself end-to-end | yes, ≥ 6 sections coherent |
| Unit + integration test coverage | ≥ 70% on `src/scribe/` |
| Latency for the full README on a small repo (≤ 30 files), warm model | ≤ 90 seconds |
| Documentation completeness | 14/14 sections |
| Working public landing page | one URL reachable |
| In-class demo runs without network access | yes (after pulling the model once) |
