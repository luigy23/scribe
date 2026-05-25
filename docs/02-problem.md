# 2. Problem Statement

## The pain point

Three problems compound to make repository documentation worse than it
needs to be:

1. **Writing a good README is boring.** It requires recalling things the
   author already knows (the dependency list, the run command, the test
   command), and packaging them in a polite, structured form for readers
   who do not. Most authors triage it down to title + one paragraph and
   then never touch it again.

2. **Off-the-shelf README templates are too generic.** Tools like
   `npm init`, `cargo new`, and `cookiecutter` create READMEs from a
   template, but the template knows nothing specific about the project.
   It produces the same skeleton every time. The maintainer still has to
   fill in everything that matters.

3. **Cloud-based AI tools collect code.** Chat-based generators (ChatGPT,
   Cursor, GitHub Copilot) can write fine prose, but using them on a
   repository implies sending the project to a third party. For private
   codebases, regulated employers, or simply privacy-conscious developers,
   that's a non-starter.

## What is needed

A tool that, given any local code repository:

- Reads the repo deterministically (no LLM hallucinations about what files
  exist).
- Identifies the language, frameworks, dependencies, scripts, tests, CI,
  license, and project structure.
- Asks a **locally hosted** large language model to write a polished README
  grounded in those concrete facts.
- Exposes the workflow through both a terminal command (for power users
  and CI pipelines) and a graphical interface (for everyone else).
- Produces a result the user can ship as-is, or hand-edit further.

## Why local matters

Three reasons:

1. **Privacy.** Source code routinely contains identifying information —
   internal API endpoints, vendor names, comments revealing strategy. Many
   employers explicitly forbid sending private code to third-party
   services. A locally-hosted model removes that policy concern.
2. **Cost.** Cloud LLMs charge per token. A maintainer regenerating
   READMEs across a portfolio of repos pays each time. A local model is
   free after a one-time download.
3. **Reproducibility.** Cloud models change without notice. A local model
   pinned to a specific tag (`qwen2.5-coder:7b`) produces stable results
   over time.

## Why this is a fit for AI

The README-writing task lives in the sweet spot for generative models:

- It requires natural-language fluency, which is what LLMs do well.
- It is grounded — every claim should be supported by something the
  analyzer detected in the repo. Hallucinations are easy to detect because
  the truth is right there on disk.
- It is bounded — a README has well-known sections in a well-known order;
  prompts can be section-scoped rather than asking the model to write the
  whole document at once.
- It is forgiving — the output is text the user reviews before committing,
  not code that runs in production.

## Out of scope

Scribe deliberately does not:

- Document individual functions or classes (that's docstring territory).
- Generate API reference pages (that's Sphinx / TypeDoc / docusaurus).
- Translate existing READMEs between languages.
- Run code or install dependencies — the analyzer is read-only.
- Push commits or open pull requests automatically.

These are reasonable extensions but they are not the first thing to build.
