"""Prompt templates for the README generator.

Each section has a focused prompt that takes the `RepoFacts` snapshot and
returns one chunk of markdown. The system prompt is shared.
"""

from __future__ import annotations

from .analyzer import RepoFacts


SYSTEM_PROMPT = """\
You are a senior open-source maintainer writing a polished README.md.

Style rules:
- Output GitHub-flavored Markdown only — no surrounding code fences, no preamble,
  no "Here is the section" introductions.
- Write in confident, plain English. Short sentences. No marketing fluff.
- Be specific to the project facts you are given. Do NOT invent dependencies,
  files, badges, frameworks, or features that are not in the facts.
- When you don't know something, omit it. Never say "TBD" or "TODO".
- Code examples must be plausible based on the manifest data provided.
- Do NOT include slashes/links to fictional accounts (no "github.com/user/repo"
  unless that exact path appears in the facts).
- Do NOT repeat the project name or title in every section.
"""


def _facts_block(facts: RepoFacts) -> str:
    """Compact textual representation of the facts for prompt inclusion."""
    lines = [
        f"Name: {facts.name}",
        f"Path: {facts.path}",
    ]
    if facts.description:
        lines.append(f"Existing description: {facts.description}")
    if facts.primary_language:
        lines.append(f"Primary language: {facts.primary_language}")
    if facts.languages:
        lang_summary = ", ".join(f"{k} ({v})" for k, v in list(facts.languages.items())[:6])
        lines.append(f"Languages by file count: {lang_summary}")
    if facts.frameworks:
        lines.append(f"Frameworks detected: {', '.join(facts.frameworks)}")
    if facts.package_managers:
        lines.append(f"Package managers: {', '.join(facts.package_managers)}")
    if facts.dependencies:
        lines.append(f"Dependencies (top): {', '.join(facts.dependencies[:15])}")
    if facts.dev_dependencies:
        lines.append(f"Dev dependencies (top): {', '.join(facts.dev_dependencies[:10])}")
    if facts.entry_points:
        lines.append(f"Entry-point commands: {', '.join(facts.entry_points)}")
    if facts.npm_scripts:
        scripts_summary = ", ".join(f"{k}" for k in list(facts.npm_scripts)[:8])
        lines.append(f"npm scripts: {scripts_summary}")
    flags = []
    if facts.has_tests: flags.append("tests")
    if facts.has_ci: flags.append("CI")
    if facts.has_dockerfile: flags.append("Dockerfile")
    if facts.has_makefile: flags.append("Makefile")
    if facts.has_license: flags.append(f"license={facts.license_name or 'unknown'}")
    if flags:
        lines.append(f"Project signals: {', '.join(flags)}")
    if facts.total_files:
        lines.append(f"Total tracked files: {facts.total_files}")
    if facts.total_lines:
        lines.append(f"Total lines of code: {facts.total_lines}")
    if facts.existing_readme:
        truncated = " (truncated)" if facts.existing_readme_truncated else ""
        lines.append("--- EXISTING README" + truncated + " ---")
        lines.append(facts.existing_readme)
        lines.append("--- END EXISTING README ---")
    return "\n".join(lines)


# ----------------------------- section prompts ----------------------------- #


def prompt_title(facts: RepoFacts) -> str:
    return f"""\
Write the README title block.

Requirements:
- One H1 with the project name as it should be displayed (you may improve casing
  from "{facts.name}" if reasonable, but keep it recognizable).
- One short tagline (under 12 words) summarizing the project, on its own line
  immediately under the H1. The tagline must be a complete sentence in italics
  (Markdown emphasis with single asterisks).
- Do NOT add badges yet.

Project facts:
{_facts_block(facts)}
"""


def prompt_description(facts: RepoFacts) -> str:
    return f"""\
Write a short Description section.

Requirements:
- Start with an H2 heading: ## Overview
- 1 to 2 short paragraphs (max ~120 words total).
- Describe what the project does, who it's for, and what makes it specific.
- If an existing README description is provided, you may refine it for clarity
  but do not contradict it.

Project facts:
{_facts_block(facts)}
"""


def prompt_features(facts: RepoFacts) -> str:
    return f"""\
Write the Features section.

Requirements:
- Start with an H2 heading: ## Features
- 4 to 7 concise bullet points.
- Each bullet starts with a leading verb or a short label in **bold**.
- Base bullets on actual frameworks, dependencies, entry points, and project
  signals from the facts. If you can't see strong evidence for a feature, omit
  it rather than invent one.

Project facts:
{_facts_block(facts)}
"""


def prompt_tech_stack(facts: RepoFacts) -> str:
    return f"""\
Write the Tech stack section.

Requirements:
- Start with an H2 heading: ## Tech stack
- A simple unordered list of categories with concrete items.
- Examples of categories: "Language", "Backend", "Frontend", "AI / ML",
  "Database", "Testing", "Tooling", "Deployment".
- Only include categories you have evidence for. List 1 to 4 items per category.
- Do not invent libraries that are not present in the facts.

Project facts:
{_facts_block(facts)}
"""


def prompt_installation(facts: RepoFacts) -> str:
    return f"""\
Write the Installation section.

Requirements:
- Start with an H2 heading: ## Installation
- Provide copy-pasteable shell commands inside one or more fenced code blocks.
- Match the detected package managers in the facts (e.g. `pip install -r requirements.txt`
  for pip, `npm install` for npm, `cargo build` for cargo).
- Mention Python or Node version requirements if visible in the facts.
- Keep it under 12 lines of shell.

Project facts:
{_facts_block(facts)}
"""


def prompt_usage(facts: RepoFacts) -> str:
    return f"""\
Write the Usage / Quickstart section.

Requirements:
- Start with an H2 heading: ## Usage
- Show the user how to run the project once installed.
- Prefer concrete commands from the facts (entry-point commands, npm scripts).
- One or two short code blocks at most.
- Add a 1-line summary of what the user should see after running.

Project facts:
{_facts_block(facts)}
"""


def prompt_development(facts: RepoFacts) -> str:
    return f"""\
Write the Development section.

Requirements:
- Start with an H2 heading: ## Development
- Cover: running tests (if tests are present), linting/formatting tools
  visible in the facts, CI presence, and the structure of the repo at a
  high level (folders).
- Use short paragraphs and at most one short code block.
- Omit subsections you have no evidence for.

Project facts:
{_facts_block(facts)}
"""


def prompt_license(facts: RepoFacts) -> str:
    if facts.has_license and facts.license_name:
        return f"""\
Write the License section.

Requirements:
- Start with an H2 heading: ## License
- One short sentence stating: this project is licensed under {facts.license_name}.
- One line pointing readers to the LICENSE file in the repository.
- Nothing else.
"""
    return """\
Write the License section.

Requirements:
- Start with an H2 heading: ## License
- One short sentence stating that the license should be specified in a LICENSE file at the repo root.
- Nothing else.
"""


# ----------------------------- ordering --------------------------------- #


SECTION_ORDER: tuple[str, ...] = (
    "title",
    "description",
    "features",
    "tech_stack",
    "installation",
    "usage",
    "development",
    "license",
)


PROMPT_BY_SECTION = {
    "title": prompt_title,
    "description": prompt_description,
    "features": prompt_features,
    "tech_stack": prompt_tech_stack,
    "installation": prompt_installation,
    "usage": prompt_usage,
    "development": prompt_development,
    "license": prompt_license,
}
