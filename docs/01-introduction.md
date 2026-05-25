# 1. Introduction

## Background

Every reasonable open-source project begins life with a `README.md`. The
README is the front door of a repository — the first thing a recruiter sees
when grading a portfolio submission, the first thing a teammate reads when
joining a project, the first thing a future you will read after six months
away from the code.

Despite that, writing a good README is a chronically deferred chore. The
typical maintainer fills in the title and a one-line description, drops a
`pip install` snippet, and then never returns. Tooling around READMEs has
mostly stagnated at the level of templates — generic skeletons the user
copy-pastes and only partially fills in. Nothing about a template knows what
your project actually is.

Meanwhile, large language models have become genuinely useful for technical
writing. Tools like ChatGPT, Cursor's Composer, and GitHub Copilot can
produce competent prose given a clear prompt. The catch: pushing your entire
codebase to a third-party API for a chat interaction is a privacy and
licensing concern many developers — and many employers — won't accept.

## Project overview

**Scribe** is a small Python application that closes that gap by combining
two ideas:

1. **A deterministic repository analyzer** that walks any local folder and
   builds a structured snapshot — language stats, frameworks, package
   managers, scripts, project signals (tests, CI, Docker, license), and the
   top of the file tree.
2. **A local large language model** running on the user's own machine via
   [Ollama](https://ollama.com). The default model is
   `qwen2.5-coder:7b` (≈ 4.7 GB), small enough to run on a recent laptop
   without a GPU and strong enough to write technically accurate prose.

The analyzer feeds the model a compact textual fact-sheet. The generator
then asks the model, one section at a time, to write a polished
`README.md`: title, badges, overview, features, tech stack, installation,
usage, development, license. Deterministic sections (badges, project tree)
are templated from the facts directly and never go through the model — that
keeps them factually correct.

Two interfaces are exposed over the same engine: a CLI driven by Typer +
Rich, and a Streamlit web UI for non-terminal users.

## Scope

This project is the second of two final deliverables for the Artificial
Intelligence course (BEINSOF52) at Universidad Surcolombiana. It satisfies
the second project track — "AI for Software Engineering" — and the explicit
constraints stated by the instructor:

- The model must run **locally**.
- The product must expose both a **terminal** interface and a **graphical**
  interface.
- IoT is not required.

## Sister project

Project #1 is **LeafLens** — a computer-vision houseplant identifier
deployed at `~/Documents/GitHub/leaflens` and on GitHub. Scribe is fully
independent of LeafLens; both projects share only the author and the course.

## Document structure

The remainder of this documentation set follows the rubric required by the
course, fourteen sections in English:

- **Section 2** states the problem in detail and the population it affects.
- **Section 3** enumerates the general and specific objectives.
- **Section 4** surveys the state of the art in README generation, local
  LLM tooling, and repository introspection.
- **Section 5** lists functional and non-functional requirements.
- **Section 6** describes the use cases and user stories.
- **Section 7** documents the (minimal) data model.
- **Section 8** presents the class diagrams.
- **Section 9** shows the GUI mockups.
- **Section 10** catalogs the CLI command surface (Scribe has no HTTP API).
- **Section 11** describes the testing strategy.
- **Section 12** depicts the system architecture.
- **Section 13** reports the results of running Scribe on real repositories.
- **Section 14** lists future work and recommendations.
