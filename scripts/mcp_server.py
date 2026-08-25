#!/usr/bin/env python3
"""SDK-free stdio MCP wrapper around the deterministic QADL tools."""

from __future__ import annotations

import json
import sys
from typing import Any, Callable

from qadlib import (
    analyze_resources,
    audit_advantage,
    render_formal_contract,
    render_qmd_handoff,
    search_candidates,
    validate_candidate,
)


SERVER_INFO = {"name": "quantum-algorithm-designer", "version": "0.1.1"}


def object_schema(properties: dict[str, Any], required: list[str]) -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": required,
    }


TOOLS = [
    {
        "name": "qadl_validate_candidate",
        "description": "Validate a QADL-IR candidate against its schema, expressions, DAG, and proof-status rules.",
        "inputSchema": object_schema({"candidate": {"type": "object"}}, ["candidate"]),
    },
    {
        "name": "qadl_analyze_resources",
        "description": "Evaluate declared resource expressions at explicit parameter points; this is not an asymptotic proof.",
        "inputSchema": object_schema(
            {
                "candidate": {"type": "object"},
                "parameter_points": {
                    "type": "array",
                    "items": {"type": "object", "additionalProperties": {"type": "number"}},
                },
            },
            ["candidate", "parameter_points"],
        ),
    },
    {
        "name": "qadl_audit_advantage",
        "description": "Gate a speedup claim on matched access, output, resources, baselines, and proof obligations.",
        "inputSchema": object_schema({"candidate": {"type": "object"}}, ["candidate"]),
    },
    {
        "name": "qadl_render_formal_contract",
        "description": "Render a Z-style classical interface plus quantum Hoare and resource proof obligations.",
        "inputSchema": object_schema({"candidate": {"type": "object"}}, ["candidate"]),
    },
    {
        "name": "qadl_render_qmd_handoff",
        "description": "Render QADL proof obligations as protected qmd-prover goals without claiming formal verification.",
        "inputSchema": object_schema(
            {
                "candidate": {"type": "object"},
                "proofs": {"type": "object", "additionalProperties": {"type": "object"}},
            },
            ["candidate"],
        ),
    },
    {
        "name": "qadl_search_candidates",
        "description": "Run bounded random or evolutionary search and return a Pareto archive without certifying correctness.",
        "inputSchema": object_schema(
            {
                "search_space": {"type": "object"},
                "method": {"type": "string", "enum": ["random", "evolutionary"]},
                "budget": {"type": "integer", "minimum": 1, "maximum": 500},
                "seed": {"type": "integer"},
                "population_size": {"type": "integer", "minimum": 2, "maximum": 100},
            },
            ["search_space"],
        ),
    },
]


def _validate(arguments: dict[str, Any]) -> Any:
    return validate_candidate(arguments["candidate"])


def _analyze(arguments: dict[str, Any]) -> Any:
    return analyze_resources(arguments["candidate"], arguments["parameter_points"])


def _audit(arguments: dict[str, Any]) -> Any:
    return audit_advantage(arguments["candidate"])


def _formalize(arguments: dict[str, Any]) -> Any:
    return {"document": render_formal_contract(arguments["candidate"]), "machine_checked": False}


def _qmd_handoff(arguments: dict[str, Any]) -> Any:
    return render_qmd_handoff(arguments["candidate"], arguments.get("proofs"))


def _search(arguments: dict[str, Any]) -> Any:
    budget = min(int(arguments.get("budget", 64)), 500)
    return search_candidates(
        arguments["search_space"],
        method=arguments.get("method", "evolutionary"),
        budget=budget,
        seed=int(arguments.get("seed", 0)),
        population_size=int(arguments.get("population_size", 16)),
    )


HANDLERS: dict[str, Callable[[dict[str, Any]], Any]] = {
    "qadl_validate_candidate": _validate,
    "qadl_analyze_resources": _analyze,
    "qadl_audit_advantage": _audit,
    "qadl_render_formal_contract": _formalize,
    "qadl_render_qmd_handoff": _qmd_handoff,
    "qadl_search_candidates": _search,
}


def success(request_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def failure(request_id: Any, message: str, code: int = -32603) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def dispatch(message: dict[str, Any]) -> dict[str, Any] | None:
    request_id = message.get("id")
    method = message.get("method")
    params = message.get("params") or {}
    if method == "initialize":
        return success(
            request_id,
            {"protocolVersion": "2025-06-18", "capabilities": {"tools": {}}, "serverInfo": SERVER_INFO},
        )
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return success(request_id, {"tools": TOOLS})
    if method == "resources/list":
        return success(request_id, {"resources": []})
    if method == "resources/templates/list":
        return success(request_id, {"resourceTemplates": []})
    if method == "ping":
        return success(request_id, {})
    if method == "tools/call":
        handler = HANDLERS.get(params.get("name"))
        if handler is None:
            return failure(request_id, f"unknown tool: {params.get('name')}", -32602)
        try:
            result = handler(params.get("arguments") or {})
            return success(request_id, {"content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]})
        except (KeyError, TypeError, ValueError) as exc:
            return failure(request_id, str(exc), -32602)
        except Exception as exc:  # Keep protocol errors structured at the process boundary.
            return failure(request_id, str(exc))
    if request_id is not None:
        return failure(request_id, f"method not found: {method}", -32601)
    return None


def main() -> int:
    for line in sys.stdin:
        try:
            response = dispatch(json.loads(line))
        except (json.JSONDecodeError, TypeError) as exc:
            response = failure(None, str(exc), -32700)
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
