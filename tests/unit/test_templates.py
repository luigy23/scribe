"""Unit tests for deterministic templates."""

from __future__ import annotations

from scribe.analyzer import RepoFacts
from scribe.templates import render_badges, render_project_structure


def test_render_badges_for_python_flask(example_facts: RepoFacts):
    badges = render_badges(example_facts)
    assert "Python" in badges
    assert "Flask" in badges
    assert "License" in badges
    assert "Docker" in badges
    assert "CI" in badges


def test_render_badges_for_empty_facts():
    empty = RepoFacts(path="/tmp", name="empty")
    assert render_badges(empty) == ""


def test_render_project_structure_wraps_tree(example_facts: RepoFacts):
    out = render_project_structure(example_facts)
    assert out.startswith("## Project structure")
    assert "```" in out
    assert example_facts.file_tree in out


def test_render_project_structure_empty():
    empty = RepoFacts(path="/tmp", name="empty", file_tree="")
    assert render_project_structure(empty) == ""
