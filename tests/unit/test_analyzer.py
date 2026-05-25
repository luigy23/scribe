"""Unit tests for the repo analyzer."""

from __future__ import annotations

from pathlib import Path

import pytest

from scribe.analyzer import RepoAnalyzer


def test_analyzer_detects_primary_language(fixture_repo: Path):
    facts = RepoAnalyzer(fixture_repo).analyze()
    assert facts.primary_language == "Python"


def test_analyzer_extracts_description_from_pyproject(fixture_repo: Path):
    facts = RepoAnalyzer(fixture_repo).analyze()
    assert facts.description == "A tiny demo project for tests."


def test_analyzer_detects_flask_framework(fixture_repo: Path):
    facts = RepoAnalyzer(fixture_repo).analyze()
    assert "Flask" in facts.frameworks


def test_analyzer_detects_signals(fixture_repo: Path):
    facts = RepoAnalyzer(fixture_repo).analyze()
    assert facts.has_tests is True
    assert facts.has_ci is True
    assert facts.has_dockerfile is True
    assert facts.has_license is True
    assert facts.license_name == "MIT"


def test_analyzer_extracts_python_scripts(fixture_repo: Path):
    facts = RepoAnalyzer(fixture_repo).analyze()
    assert "demo" in facts.python_scripts
    assert facts.python_scripts["demo"] == "demo.main:hello"
    assert "demo" in facts.entry_points


def test_analyzer_builds_file_tree(fixture_repo: Path):
    facts = RepoAnalyzer(fixture_repo).analyze()
    assert "src" in facts.file_tree
    assert "tests" in facts.file_tree


def test_analyzer_raises_on_missing_directory(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        RepoAnalyzer(tmp_path / "does-not-exist")


def test_analyzer_raises_on_file_path(tmp_path: Path):
    f = tmp_path / "a.txt"
    f.write_text("hi")
    with pytest.raises(NotADirectoryError):
        RepoAnalyzer(f)


def test_analyzer_ignores_node_modules_and_venv(tmp_path: Path):
    (tmp_path / "node_modules" / "junk").mkdir(parents=True)
    (tmp_path / "node_modules" / "junk" / "file.js").write_text("/* heavy */")
    (tmp_path / ".venv" / "bin").mkdir(parents=True)
    (tmp_path / ".venv" / "bin" / "python").write_text("")
    (tmp_path / "src.py").write_text("print('hi')\n")

    facts = RepoAnalyzer(tmp_path).analyze()
    # The venv binary and node_modules junk should not appear in the file tree.
    assert "node_modules" not in facts.file_tree
    assert ".venv" not in facts.file_tree
    # Languages should only count src.py
    assert facts.languages.get("Python", 0) == 1


def test_analyzer_truncates_long_readme(tmp_path: Path):
    huge = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 200
    (tmp_path / "README.md").write_text(huge)
    facts = RepoAnalyzer(tmp_path).analyze()
    assert facts.existing_readme is not None
    assert len(facts.existing_readme) <= RepoAnalyzer.MAX_README_CHARS
    assert facts.existing_readme_truncated is True
