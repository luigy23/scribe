"""Repository analyzer.

Walks a directory and produces a structured `RepoFacts` snapshot that the
README generator can consume. The analyzer is deliberately lightweight — it
parses manifest files (`package.json`, `pyproject.toml`, `Cargo.toml`,
`go.mod`, `requirements.txt`) and looks at file extensions, but does NOT
run any code, install any dependencies, or hit the network.
"""

from __future__ import annotations

import json
import logging
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml

if sys.version_info >= (3, 11):
    import tomllib  # type: ignore[attr-defined]
else:  # pragma: no cover - we target 3.13
    import tomli as tomllib  # type: ignore[no-redef]

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------

LANGUAGE_BY_EXT: dict[str, str] = {
    ".py": "Python", ".pyi": "Python",
    ".js": "JavaScript", ".mjs": "JavaScript", ".cjs": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript",
    ".go": "Go",
    ".rs": "Rust",
    ".rb": "Ruby",
    ".java": "Java",
    ".kt": "Kotlin", ".kts": "Kotlin",
    ".swift": "Swift",
    ".m": "Objective-C", ".mm": "Objective-C",
    ".c": "C", ".h": "C",
    ".cpp": "C++", ".cc": "C++", ".hpp": "C++",
    ".cs": "C#",
    ".php": "PHP",
    ".sh": "Shell", ".bash": "Shell", ".zsh": "Shell",
    ".lua": "Lua",
    ".dart": "Dart",
    ".scala": "Scala",
    ".clj": "Clojure",
    ".html": "HTML", ".htm": "HTML",
    ".css": "CSS", ".scss": "SCSS", ".sass": "Sass", ".less": "Less",
    ".vue": "Vue",
    ".svelte": "Svelte",
    ".sql": "SQL",
    ".r": "R",
    ".jl": "Julia",
    ".md": "Markdown",
    ".yml": "YAML", ".yaml": "YAML",
    ".toml": "TOML",
    ".dockerfile": "Dockerfile",
}

# Files that count even without an extension
LANGUAGE_BY_NAME: dict[str, str] = {
    "Dockerfile": "Dockerfile",
    "Makefile": "Make",
    "Rakefile": "Ruby",
    "Gemfile": "Ruby",
    "BUILD": "Bazel",
    "WORKSPACE": "Bazel",
}

IGNORE_DIRS = {
    ".git", ".hg", ".svn",
    ".venv", "venv", "env", "__pycache__",
    "node_modules", ".pnpm-store",
    "dist", "build", "target", "out",
    ".next", ".nuxt", ".cache",
    ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".tox", ".coverage", "htmlcov",
    ".idea", ".vscode",
    ".DS_Store",
    ".github",  # handled separately
}

DOCUMENTATION_EXTENSIONS = {".md", ".rst", ".txt", ".adoc"}

# ---------------------------------------------------------------------------
# Framework heuristics
# ---------------------------------------------------------------------------

PYTHON_FRAMEWORKS = {
    "flask": "Flask",
    "fastapi": "FastAPI",
    "django": "Django",
    "starlette": "Starlette",
    "aiohttp": "aiohttp",
    "tornado": "Tornado",
    "streamlit": "Streamlit",
    "gradio": "Gradio",
    "typer": "Typer",
    "click": "Click",
    "pydantic": "Pydantic",
    "sqlalchemy": "SQLAlchemy",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "keras": "Keras",
    "scikit-learn": "scikit-learn",
    "pandas": "pandas",
    "numpy": "NumPy",
    "transformers": "Transformers",
    "huggingface-hub": "Hugging Face Hub",
    "ollama": "Ollama (client)",
    "anthropic": "Anthropic SDK",
    "openai": "OpenAI SDK",
}

JS_FRAMEWORKS = {
    "react": "React",
    "react-dom": "React",
    "next": "Next.js",
    "vue": "Vue",
    "nuxt": "Nuxt",
    "svelte": "Svelte",
    "@sveltejs/kit": "SvelteKit",
    "solid-js": "SolidJS",
    "angular": "Angular",
    "@angular/core": "Angular",
    "express": "Express",
    "fastify": "Fastify",
    "koa": "Koa",
    "hono": "Hono",
    "vite": "Vite",
    "webpack": "webpack",
    "esbuild": "esbuild",
    "rollup": "Rollup",
    "tailwindcss": "Tailwind CSS",
    "axios": "axios",
    "tanstack-query": "TanStack Query",
    "@tanstack/react-query": "TanStack Query",
    "zustand": "Zustand",
    "redux": "Redux",
}

# ---------------------------------------------------------------------------
# Facts
# ---------------------------------------------------------------------------


@dataclass
class RepoFacts:
    """Everything Scribe knows about the repo, ready for templating."""

    path: str
    name: str
    description: str | None = None

    # Language stats
    languages: dict[str, int] = field(default_factory=dict)  # file counts
    primary_language: str | None = None
    total_files: int = 0
    total_lines: int = 0

    # Frameworks / packages
    frameworks: list[str] = field(default_factory=list)
    package_managers: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    dev_dependencies: list[str] = field(default_factory=list)

    # Project signals
    has_tests: bool = False
    has_ci: bool = False
    has_dockerfile: bool = False
    has_makefile: bool = False
    has_license: bool = False
    license_name: str | None = None
    has_changelog: bool = False
    has_contributing: bool = False

    # Entry points (commands, scripts)
    entry_points: list[str] = field(default_factory=list)
    npm_scripts: dict[str, str] = field(default_factory=dict)
    python_scripts: dict[str, str] = field(default_factory=dict)

    # Structure
    file_tree: str = ""
    notable_files: list[str] = field(default_factory=list)

    # Existing prose we want to preserve
    existing_readme: str | None = None
    existing_readme_truncated: bool = False

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Analyzer
# ---------------------------------------------------------------------------


class RepoAnalyzer:
    MAX_README_CHARS = 6000
    FILE_TREE_DEPTH = 3
    FILE_TREE_MAX_ENTRIES = 80

    def __init__(self, repo_path: str | Path):
        self.path = Path(repo_path).expanduser().resolve()
        if not self.path.exists():
            raise FileNotFoundError(f"Repo path not found: {self.path}")
        if not self.path.is_dir():
            raise NotADirectoryError(f"Repo path is not a directory: {self.path}")

    # ------------------------------ public API ------------------------------ #

    def analyze(self) -> RepoFacts:
        facts = RepoFacts(path=str(self.path), name=self.path.name)
        self._scan_language_stats(facts)
        self._read_python_manifest(facts)
        self._read_npm_manifest(facts)
        self._read_cargo_manifest(facts)
        self._read_go_manifest(facts)
        self._detect_project_signals(facts)
        self._read_existing_readme(facts)
        self._build_file_tree(facts)
        self._derive_summary(facts)
        return facts

    # --------------------------- internal helpers --------------------------- #

    def _is_ignored(self, p: Path) -> bool:
        return any(part in IGNORE_DIRS for part in p.relative_to(self.path).parts)

    def _iter_files(self):
        for p in self.path.rglob("*"):
            if p.is_file() and not self._is_ignored(p):
                yield p

    def _scan_language_stats(self, facts: RepoFacts) -> None:
        counter: Counter[str] = Counter()
        total_lines = 0
        total_files = 0
        for p in self._iter_files():
            total_files += 1
            lang = LANGUAGE_BY_EXT.get(p.suffix.lower())
            if lang is None:
                lang = LANGUAGE_BY_NAME.get(p.name)
            if lang is None:
                continue
            counter[lang] += 1
            if lang not in {"Markdown", "YAML", "TOML"}:
                try:
                    total_lines += sum(1 for _ in p.open("rb"))
                except OSError:
                    pass
        facts.languages = dict(counter.most_common())
        facts.total_files = total_files
        facts.total_lines = total_lines

        # Pick a primary language: most common non-trivial language
        non_trivial = [
            lang
            for lang in facts.languages
            if lang not in {"Markdown", "YAML", "TOML", "Dockerfile"}
        ]
        if non_trivial:
            facts.primary_language = non_trivial[0]
        elif facts.languages:
            facts.primary_language = next(iter(facts.languages))

    # ----- Python ------------------------------------------------------------

    def _read_python_manifest(self, facts: RepoFacts) -> None:
        pyproject = self.path / "pyproject.toml"
        if pyproject.exists():
            facts.package_managers.append("pip / pyproject")
            try:
                data = tomllib.loads(pyproject.read_text())
            except (OSError, tomllib.TOMLDecodeError) as exc:
                log.warning("Could not parse pyproject.toml: %s", exc)
                data = {}
            project = data.get("project", {})
            if facts.description is None and project.get("description"):
                facts.description = project["description"]
            deps: list[str] = project.get("dependencies", []) or []
            facts.dependencies.extend(self._top_level_name(d) for d in deps)
            optional = project.get("optional-dependencies", {})
            for group_deps in optional.values():
                facts.dev_dependencies.extend(self._top_level_name(d) for d in group_deps)
            scripts = project.get("scripts", {})
            for cmd_name, target in scripts.items():
                facts.python_scripts[cmd_name] = target
                facts.entry_points.append(cmd_name)

        req = self.path / "requirements.txt"
        if req.exists():
            facts.package_managers.append("pip")
            for raw in req.read_text().splitlines():
                line = raw.strip()
                if not line or line.startswith(("#", "-")):
                    continue
                facts.dependencies.append(self._top_level_name(line))

        # Identify Python frameworks
        identifiers = {d.lower() for d in facts.dependencies + facts.dev_dependencies}
        for key, label in PYTHON_FRAMEWORKS.items():
            if key in identifiers:
                facts.frameworks.append(label)

    # ----- npm ---------------------------------------------------------------

    def _read_npm_manifest(self, facts: RepoFacts) -> None:
        # Look at top-level OR a frontend/ subfolder (common in our world).
        candidates = [self.path / "package.json", self.path / "frontend" / "package.json"]
        for pkg_path in candidates:
            if not pkg_path.exists():
                continue
            try:
                data = json.loads(pkg_path.read_text())
            except (OSError, json.JSONDecodeError) as exc:
                log.warning("Could not parse %s: %s", pkg_path, exc)
                continue
            facts.package_managers.append("npm")
            if facts.description is None and data.get("description"):
                facts.description = data["description"]
            deps = data.get("dependencies", {})
            dev = data.get("devDependencies", {})
            facts.dependencies.extend(deps.keys())
            facts.dev_dependencies.extend(dev.keys())
            for script_name, script_cmd in data.get("scripts", {}).items():
                facts.npm_scripts[script_name] = script_cmd
            identifiers = {d.lower() for d in list(deps) + list(dev)}
            for key, label in JS_FRAMEWORKS.items():
                if key in identifiers:
                    facts.frameworks.append(label)

    # ----- Cargo (Rust) ------------------------------------------------------

    def _read_cargo_manifest(self, facts: RepoFacts) -> None:
        cargo = self.path / "Cargo.toml"
        if not cargo.exists():
            return
        facts.package_managers.append("cargo")
        try:
            data = tomllib.loads(cargo.read_text())
        except (OSError, tomllib.TOMLDecodeError) as exc:
            log.warning("Could not parse Cargo.toml: %s", exc)
            return
        pkg = data.get("package", {})
        if facts.description is None and pkg.get("description"):
            facts.description = pkg["description"]
        deps = data.get("dependencies", {})
        facts.dependencies.extend(deps.keys())

    # ----- Go ----------------------------------------------------------------

    def _read_go_manifest(self, facts: RepoFacts) -> None:
        gomod = self.path / "go.mod"
        if not gomod.exists():
            return
        facts.package_managers.append("go modules")
        for line in gomod.read_text().splitlines():
            line = line.strip()
            if line.startswith("require ") and not line.startswith("require ("):
                facts.dependencies.append(line.split()[1])

    # ----- Project signals ---------------------------------------------------

    def _detect_project_signals(self, facts: RepoFacts) -> None:
        for top in self.path.iterdir():
            if not top.exists():
                continue
            name = top.name
            lower = name.lower()
            if lower == "dockerfile":
                facts.has_dockerfile = True
            elif lower == "makefile":
                facts.has_makefile = True
            elif lower.startswith("license"):
                facts.has_license = True
                facts.license_name = self._detect_license(top)
            elif lower.startswith("changelog"):
                facts.has_changelog = True
            elif lower.startswith("contributing"):
                facts.has_contributing = True

        # Tests
        for cand in ("tests", "test", "src/tests", "spec"):
            if (self.path / cand).is_dir():
                facts.has_tests = True
                break

        # CI
        if (self.path / ".github" / "workflows").is_dir():
            facts.has_ci = True
        if (self.path / ".gitlab-ci.yml").exists() or (self.path / ".circleci").is_dir():
            facts.has_ci = True

    @staticmethod
    def _detect_license(license_path: Path) -> str | None:
        try:
            head = license_path.read_text(errors="ignore")[:500].lower()
        except OSError:
            return None
        if "mit license" in head:
            return "MIT"
        if "apache license" in head:
            return "Apache-2.0"
        if "gnu general public license" in head:
            return "GPL"
        if "bsd " in head:
            return "BSD"
        if "mozilla public license" in head:
            return "MPL-2.0"
        return None

    # ----- Existing README ---------------------------------------------------

    def _read_existing_readme(self, facts: RepoFacts) -> None:
        for name in ("README.md", "README.rst", "README.txt", "README"):
            p = self.path / name
            if p.exists():
                try:
                    content = p.read_text(errors="ignore")
                except OSError:
                    continue
                if len(content) > self.MAX_README_CHARS:
                    facts.existing_readme = content[: self.MAX_README_CHARS]
                    facts.existing_readme_truncated = True
                else:
                    facts.existing_readme = content
                if facts.description is None:
                    facts.description = self._extract_first_paragraph(content)
                break

    @staticmethod
    def _extract_first_paragraph(markdown: str) -> str | None:
        body = re.sub(r"^#.*$", "", markdown, flags=re.MULTILINE)
        for chunk in body.split("\n\n"):
            stripped = chunk.strip()
            if stripped and not stripped.startswith(("![", "[!", "<")):
                cleaned = re.sub(r"\s+", " ", stripped)
                return cleaned[:280] + ("..." if len(cleaned) > 280 else "")
        return None

    # ----- File tree ---------------------------------------------------------

    def _build_file_tree(self, facts: RepoFacts) -> None:
        lines: list[str] = []
        entries = 0
        max_depth = self.FILE_TREE_DEPTH
        max_entries = self.FILE_TREE_MAX_ENTRIES

        def walk(dir_path: Path, depth: int):
            nonlocal entries
            if depth > max_depth or entries >= max_entries:
                return
            children = sorted(
                (
                    p
                    for p in dir_path.iterdir()
                    if not (p.is_dir() and p.name in IGNORE_DIRS)
                    and not p.name.startswith(".")
                ),
                key=lambda p: (not p.is_dir(), p.name.lower()),
            )
            for child in children:
                if entries >= max_entries:
                    lines.append(f"{'  ' * depth}...")
                    return
                indent = "  " * depth
                marker = "📁" if child.is_dir() else "·"
                lines.append(f"{indent}{marker} {child.name}")
                entries += 1
                if child.is_dir():
                    walk(child, depth + 1)

        walk(self.path, 0)
        facts.file_tree = "\n".join(lines)

    # ----- Derived summary ---------------------------------------------------

    def _derive_summary(self, facts: RepoFacts) -> None:
        # De-duplicate while preserving order
        facts.dependencies = list(dict.fromkeys(facts.dependencies))
        facts.dev_dependencies = list(dict.fromkeys(facts.dev_dependencies))
        facts.frameworks = list(dict.fromkeys(facts.frameworks))
        facts.package_managers = list(dict.fromkeys(facts.package_managers))
        facts.entry_points = list(dict.fromkeys(facts.entry_points))

        # Trim very long dependency lists
        if len(facts.dependencies) > 30:
            facts.dependencies = facts.dependencies[:30] + [f"... ({len(facts.dependencies) - 30} more)"]
        if len(facts.dev_dependencies) > 30:
            facts.dev_dependencies = facts.dev_dependencies[:30] + [
                f"... ({len(facts.dev_dependencies) - 30} more)"
            ]

    # ----- Helpers ----------------------------------------------------------

    @staticmethod
    def _top_level_name(spec: str) -> str:
        """`flask>=3.0` → `flask`, `git+https://...` → the URL, `package[extra]` → `package`."""
        spec = spec.strip().split(";")[0]  # drop environment markers
        match = re.match(r"^([A-Za-z0-9_.\-]+)", spec)
        return match.group(1) if match else spec
