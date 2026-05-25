"""Shared pytest fixtures."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from scribe.analyzer import RepoFacts
from scribe.llm import ChatMessage


# --------------------------------------------------------------------------
# Fixture repo factory
# --------------------------------------------------------------------------


@pytest.fixture
def fixture_repo(tmp_path: Path) -> Path:
    """Return a tmp path that looks like a small Python project."""
    (tmp_path / "src" / "demo").mkdir(parents=True)
    (tmp_path / "src" / "demo" / "__init__.py").write_text("")
    (tmp_path / "src" / "demo" / "main.py").write_text(
        "def hello():\n    return 'hi'\n"
    )
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_main.py").write_text(
        "def test_hello():\n    pass\n"
    )
    (tmp_path / "pyproject.toml").write_text(textwrap.dedent("""\
        [project]
        name = "demo"
        version = "0.1.0"
        description = "A tiny demo project for tests."
        requires-python = ">=3.11"
        dependencies = ["flask>=3.0", "rich>=13"]

        [project.scripts]
        demo = "demo.main:hello"
    """))
    (tmp_path / "requirements.txt").write_text("flask>=3.0\nrich>=13\n")
    (tmp_path / "README.md").write_text("# Demo\n\nThis is a demo project for testing.\n")
    (tmp_path / "LICENSE").write_text("MIT License\n\nCopyright (c) 2026\n")
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text("name: CI\n")
    (tmp_path / "Dockerfile").write_text("FROM python:3.13-slim\n")
    return tmp_path


# --------------------------------------------------------------------------
# Stub LLM
# --------------------------------------------------------------------------


class StubOllamaClient:
    """Deterministic Ollama replacement used in tests."""

    model = "stub-model"
    host = "http://stub:11434"

    def __init__(self):
        self.calls: list[list[ChatMessage]] = []

    def ready(self) -> tuple[bool, str]:
        return True, "stub ready"

    def chat(self, messages, temperature: float = 0.2) -> str:
        self.calls.append(list(messages))
        # The system+user prompt mentions the section name; we echo it.
        user = next((m for m in messages if m.role == "user"), None)
        if user and "title block" in user.content[:200]:
            return "# Demo\n\n*A tiny demo project.*"
        if user and "Overview" in user.content[:200]:
            return "## Overview\n\nThis project does nothing but exist for the test suite."
        if user and "Features" in user.content[:200]:
            return "## Features\n\n- Just a fixture."
        if user and "Tech stack" in user.content[:200]:
            return "## Tech stack\n\n- Language: Python\n- Backend: Flask"
        if user and "Installation" in user.content[:200]:
            return "## Installation\n\n```bash\npip install -e .\n```"
        if user and "Usage" in user.content[:200]:
            return "## Usage\n\n```bash\ndemo\n```"
        if user and "Development" in user.content[:200]:
            return "## Development\n\nRun `pytest` to execute the test suite."
        if user and "License" in user.content[:200]:
            return "## License\n\nThis project is licensed under MIT."
        return "## Section\n\nStub output."

    def stream_chat(self, messages, temperature: float = 0.2):
        full = self.chat(messages, temperature=temperature)
        # Yield 2 chunks so streaming tests see >1 delta event.
        midpoint = len(full) // 2
        yield full[:midpoint]
        yield full[midpoint:]


@pytest.fixture
def stub_client() -> StubOllamaClient:
    return StubOllamaClient()


@pytest.fixture
def example_facts() -> RepoFacts:
    return RepoFacts(
        path="/tmp/demo",
        name="demo",
        description="A tiny demo project.",
        languages={"Python": 5, "Markdown": 1},
        primary_language="Python",
        total_files=7,
        total_lines=42,
        frameworks=["Flask"],
        package_managers=["pip"],
        dependencies=["flask", "rich"],
        dev_dependencies=["pytest"],
        has_tests=True,
        has_ci=True,
        has_dockerfile=True,
        has_license=True,
        license_name="MIT",
        entry_points=["demo"],
        python_scripts={"demo": "demo.main:hello"},
        file_tree="📁 src\n  📁 demo\n📁 tests\n· pyproject.toml",
    )
