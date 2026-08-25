#!/usr/bin/env python3
"""Command-line access to QADL validation, analysis, search, and formalization."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from qadlib import (
    analyze_resources,
    audit_advantage,
    render_formal_contract,
    search_candidates,
    validate_candidate,
    write_qmd_handoff,
)


def load_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_output(value: Any, output: str | None, as_text: bool = False) -> None:
    text = value if as_text else json.dumps(value, indent=2, ensure_ascii=False)
    if output:
        Path(output).write_text(f"{text}\n", encoding="utf-8")
    else:
        print(text)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Quantum Algorithm Design Language tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate a QADL candidate")
    validate.add_argument("candidate")
    validate.add_argument("--out")

    analyze = subparsers.add_parser("analyze", help="evaluate resource expressions at explicit points")
    analyze.add_argument("candidate")
    analyze.add_argument("--points", required=True, help="JSON file containing an array of parameter objects")
    analyze.add_argument("--out")

    audit = subparsers.add_parser("audit", help="audit a quantum-advantage claim")
    audit.add_argument("candidate")
    audit.add_argument("--out")

    formalize = subparsers.add_parser("formalize", help="render Z-style and quantum Hoare proof obligations")
    formalize.add_argument("candidate")
    formalize.add_argument("--out")

    export_qmd = subparsers.add_parser("export-qmd", help="export proof obligations to an initialized qmd-prover project")
    export_qmd.add_argument("candidate")
    export_qmd.add_argument("--project", required=True, help="directory previously initialized with qmd-prover init")
    export_qmd.add_argument("--proofs", help="optional JSON proof sidecar keyed by QADL obligation id")
    export_qmd.add_argument("--out")

    search = subparsers.add_parser("search", help="run random or evolutionary search")
    search.add_argument("search_space")
    search.add_argument("--method", choices=("random", "evolutionary"), default="evolutionary")
    search.add_argument("--budget", type=int, default=64)
    search.add_argument("--population-size", type=int, default=16)
    search.add_argument("--seed", type=int, default=0)
    search.add_argument("--out")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "validate":
            result = validate_candidate(load_json(args.candidate))
            write_output(result, args.out)
            return 0 if result["valid"] else 1
        if args.command == "analyze":
            points = load_json(args.points)
            if not isinstance(points, list):
                raise ValueError("--points must contain a JSON array")
            result = analyze_resources(load_json(args.candidate), points)
            write_output(result, args.out)
            return 0 if not any(item["severity"] == "error" for item in result["issues"]) else 1
        if args.command == "audit":
            result = audit_advantage(load_json(args.candidate))
            write_output(result, args.out)
            return 0 if result["blocker_count"] == 0 else 2
        if args.command == "formalize":
            write_output(render_formal_contract(load_json(args.candidate)), args.out, as_text=True)
            return 0
        if args.command == "export-qmd":
            proofs = load_json(args.proofs) if args.proofs else None
            result = write_qmd_handoff(load_json(args.candidate), args.project, proofs)
            write_output(result, args.out)
            return 0
        if args.command == "search":
            result = search_candidates(
                load_json(args.search_space),
                method=args.method,
                budget=args.budget,
                seed=args.seed,
                population_size=args.population_size,
            )
            write_output(result, args.out)
            return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
