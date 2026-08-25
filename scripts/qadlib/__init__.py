"""Deterministic support library for the Quantum Algorithm Designer plugin."""

from .audit import analyze_resources, audit_advantage
from .formal import render_formal_contract
from .qmd import render_qmd_handoff, write_qmd_handoff
from .search import search_candidates
from .validation import validate_candidate

__all__ = [
    "analyze_resources",
    "audit_advantage",
    "render_formal_contract",
    "render_qmd_handoff",
    "search_candidates",
    "validate_candidate",
    "write_qmd_handoff",
]
