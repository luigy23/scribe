"""Scribe — local-LLM-powered README generator."""

__version__ = "0.1.0"

from .analyzer import RepoAnalyzer, RepoFacts
from .generator import ReadmeGenerator
from .llm import OllamaClient

__all__ = ["RepoAnalyzer", "RepoFacts", "ReadmeGenerator", "OllamaClient", "__version__"]
