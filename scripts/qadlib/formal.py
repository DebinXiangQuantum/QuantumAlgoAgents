"""Render QADL into reviewable formal-specification obligations."""

from __future__ import annotations

from typing import Any


def render_formal_contract(candidate: dict[str, Any]) -> str:
    """Render a Z-style interface plus quantum Hoare and resource obligations."""
    problem = candidate.get("problem", {})
    algorithm = candidate.get("algorithm", {})
    resources = candidate.get("resources", {})
    lines = [
        f"# Formal contract: {candidate.get('title') or candidate.get('candidate_id', 'candidate')}",
        "",
        "> Generated proof scaffold only. QADL-IR and this document do not constitute a machine-checked proof.",
        "",
        "## Problem interface (Z-style)",
        "",
        "```latex",
        r"\begin{schema}{QuantumProblem}",
    ]
    parameters = problem.get("size_parameters", [])
    for parameter in parameters:
        if not isinstance(parameter, dict):
            continue
        lines.append(f"  {_latex(parameter.get('name', 'n'))}: {_z_domain(parameter.get('domain'))} " + r"\\")
    lines.extend(
        [
            r"  input: INPUT \\",
            r"  output: OUTPUT",
            r"\where",
            rf"  \text{{Input access: }} {_latex(problem.get('input', {}).get('access_model', 'unspecified'))} " + r"\\",
            rf"  \text{{Output contract: }} {_latex(problem.get('output', {}).get('contract', 'unspecified'))}",
        ]
    )
    for promise in problem.get("promises", []):
        lines.append(rf"  \land\; \text{{{_latex(promise)}}}")
    lines.extend([r"\end{schema}", "```", "", "## Stage contracts", ""])

    for stage in algorithm.get("stages", []):
        if not isinstance(stage, dict):
            continue
        contract = stage.get("contract", {})
        lines.extend(
            [
                f"### {stage.get('id', 'stage')}: {stage.get('operation', '')}",
                "",
                f"- Domain: `{stage.get('domain', 'unknown')}`",
                f"- Primitive: `{stage.get('primitive', 'not-applicable')}`",
                f"- Obligation: `{{{contract.get('precondition', '?')}}} {stage.get('id', 'S')} {{{contract.get('postcondition', '?')}}}`",
                f"- Repetitions: `{stage.get('repetitions', 'unknown')}`",
            ]
        )
        if contract.get("invariant"):
            lines.append(f"- Invariant: `{contract['invariant']}`")
        lines.append("")

    lines.extend(["## Resource recurrences", ""])
    for name, expression in resources.get("expressions", {}).items():
        lines.append(f"- `{name} = {expression}`")
    lines.extend(["", "## Proof obligations", ""])
    lines.append("| ID | Kind | Status | Statement | Artifact |")
    lines.append("| --- | --- | --- | --- | --- |")
    for obligation in candidate.get("proof_obligations", []):
        artifacts = ", ".join(obligation.get("artifacts", [])) or "none"
        lines.append(
            "| {id} | {kind} | {status} | {statement} | {artifacts} |".format(
                id=_table(obligation.get("id", "")),
                kind=_table(obligation.get("kind", "")),
                status=_table(obligation.get("status", "")),
                statement=_table(obligation.get("statement", "")),
                artifacts=_table(artifacts),
            )
        )
    lines.extend(
        [
            "",
            "## Backend handoff",
            "",
            "- Use Z notation for the classical problem/interface schema only.",
            "- Map circuit-building correctness and parametric resource obligations to Qbricks/Why3 when supported.",
            "- Map circuit semantics and verified transformations to SQIR/VOQC (Coq) when supported.",
            "- Map executable resource decompositions to Qualtran; use OpenQASM/QIR only after high-level obligations are retained.",
            "- Keep unsupported obligations open; never translate an absent proof into a verified status.",
            "",
        ]
    )
    return "\n".join(lines)


def _z_domain(domain: str | None) -> str:
    return {
        "positive-integer": r"\nat_1",
        "nonnegative-integer": r"\nat",
        "positive-real": r"\real_{>0}",
        "probability": r"[0,1]",
    }.get(domain or "", r"\mathbb{U}")


def _latex(value: Any) -> str:
    text = str(value)
    for source, replacement in (("\\", r"\textbackslash{}"), ("_", r"\_"), ("%", r"\%"), ("&", r"\&")):
        text = text.replace(source, replacement)
    return text


def _table(value: Any) -> str:
    return str(value).replace("|", r"\|").replace("\n", " ")
