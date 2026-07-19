"""Deterministic support library for the Quantum Algorithm Designer plugin."""

from .audit import analyze_resources, audit_advantage
from .formal import render_formal_contract
from .search import search_candidates
from .validation import validate_candidate

__all__ = [
    "analyze_resources",
    "audit_advantage",
    "render_formal_contract",
    "search_candidates",
    "validate_candidate",
]
