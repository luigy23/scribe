"""Deterministic README sections — no LLM needed.

These render directly from the `RepoFacts`. Keeping them out of the LLM
guarantees they stay accurate.
"""

from __future__ import annotations

from .analyzer import RepoFacts


def render_badges(facts: RepoFacts) -> str:
    """Return a row of shields.io badges based on the detected stack."""
    badges: list[str] = []

    if "Python" in facts.languages:
        badges.append("![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)")
    if "TypeScript" in facts.languages:
        badges.append("![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)")
    elif "JavaScript" in facts.languages:
        badges.append("![JavaScript](https://img.shields.io/badge/JavaScript-ES2022-F7DF1E?logo=javascript&logoColor=black)")
    if "Go" in facts.languages:
        badges.append("![Go](https://img.shields.io/badge/Go-1.22-00ADD8?logo=go&logoColor=white)")
    if "Rust" in facts.languages:
        badges.append("![Rust](https://img.shields.io/badge/Rust-1.80-000000?logo=rust&logoColor=white)")

    for fw in facts.frameworks:
        if fw == "React":
            badges.append("![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)")
        elif fw == "Next.js":
            badges.append("![Next.js](https://img.shields.io/badge/Next.js-14-000?logo=next.js&logoColor=white)")
        elif fw == "Vue":
            badges.append("![Vue](https://img.shields.io/badge/Vue-3-4FC08D?logo=vue.js&logoColor=white)")
        elif fw == "Flask":
            badges.append("![Flask](https://img.shields.io/badge/Flask-3-000?logo=flask&logoColor=white)")
        elif fw == "FastAPI":
            badges.append("![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)")
        elif fw == "Django":
            badges.append("![Django](https://img.shields.io/badge/Django-5-092E20?logo=django&logoColor=white)")
        elif fw == "PyTorch":
            badges.append("![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?logo=pytorch&logoColor=white)")
        elif fw == "TensorFlow":
            badges.append("![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?logo=tensorflow&logoColor=white)")
        elif fw == "Streamlit":
            badges.append("![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)")

    if facts.has_ci:
        badges.append("![CI](https://img.shields.io/badge/CI-passing-brightgreen)")
    if facts.has_license and facts.license_name:
        badges.append(f"![License](https://img.shields.io/badge/License-{facts.license_name.replace('-', '--')}-blue)")
    if facts.has_dockerfile:
        badges.append("![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)")

    if not badges:
        return ""
    return " ".join(badges)


def render_project_structure(facts: RepoFacts) -> str:
    """Return the deterministic project-structure section."""
    if not facts.file_tree:
        return ""
    return (
        "## Project structure\n\n"
        "```\n"
        f"{facts.file_tree}\n"
        "```\n"
    )


def render_table_of_languages(facts: RepoFacts) -> str:
    """A small table of languages used, by file count."""
    if not facts.languages:
        return ""
    rows = ["| Language | Files |", "|---|---|"]
    for lang, count in list(facts.languages.items())[:8]:
        rows.append(f"| {lang} | {count} |")
    return "\n".join(rows)
