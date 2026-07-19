"""Resource evaluation and conservative quantum-advantage claim auditing."""

from __future__ import annotations

import statistics
from typing import Any

from .expressions import ExpressionError, evaluate_expression, is_unknown
from .validation import issue, validate_candidate


_MODEL_LEVEL = {"query": 1, "logical-circuit": 2, "fault-tolerant": 3, "end-to-end": 4}
_SCOPE_LEVEL = {
    "none": 0,
    "query": 1,
    "sample": 1,
    "logical": 2,
    "space": 2,
    "physical": 3,
    "kernel-wall-clock": 4,
    "end-to-end-wall-clock": 4,
}


def analyze_resources(candidate: dict[str, Any], parameter_points: list[dict[str, float]]) -> dict[str, Any]:
    """Evaluate declared expressions at explicit points; do not infer asymptotic proofs."""
    validation = validate_candidate(candidate)
    parameters = {
        item["name"]
        for item in candidate.get("problem", {}).get("size_parameters", [])
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }
    points: list[dict[str, Any]] = []
    issues: list[dict[str, str]] = []
    expressions = candidate.get("resources", {}).get("expressions", {})
    for index, raw_values in enumerate(parameter_points):
        values = {name: float(value) for name, value in raw_values.items()}
        missing = sorted(parameters - set(values))
        extra = sorted(set(values) - parameters)
        if missing:
            issues.append(issue("error", "resource.parameters", f"/parameter_points/{index}", f"missing parameters: {', '.join(missing)}"))
        if extra:
            issues.append(issue("warning", "resource.parameters", f"/parameter_points/{index}", f"undeclared parameters ignored by the contract: {', '.join(extra)}"))
        evaluated: dict[str, float | None] = {}
        if not missing:
            for name, expression in expressions.items():
                try:
                    evaluated[name] = evaluate_expression(expression, values)
                except (ExpressionError, ArithmeticError, ValueError) as exc:
                    evaluated[name] = None
                    issues.append(issue("error", "resource.evaluate", f"/resources/expressions/{name}", f"point {index}: {exc}"))
        points.append({"parameters": values, "resources": evaluated})

    summaries: dict[str, dict[str, float]] = {}
    for name in expressions:
        values = [point["resources"].get(name) for point in points]
        numeric = [value for value in values if isinstance(value, (int, float))]
        if numeric:
            summaries[name] = {
                "min": min(numeric),
                "max": max(numeric),
                "mean": statistics.fmean(numeric),
                "last": numeric[-1],
            }
    return {
        "note": "Numeric sampling is a consistency check, not an asymptotic proof.",
        "candidate_valid": validation["valid"],
        "points": points,
        "summaries": summaries,
        "issues": issues,
    }


def audit_advantage(candidate: dict[str, Any]) -> dict[str, Any]:
    """Apply evidence gates and return a verdict that never certifies advantage automatically."""
    validation = validate_candidate(candidate)
    findings: list[dict[str, str]] = list(validation["issues"])

    problem = candidate.get("problem", {})
    input_contract = problem.get("input", {})
    output_contract = problem.get("output", {})
    baselines = problem.get("classical_baselines", [])
    resources = candidate.get("resources", {})
    claim = candidate.get("claim", {})
    claim_type = claim.get("type", "none")

    if claim_type == "none":
        return {
            "verdict": "no-claim",
            "eligible_for_expert_review": validation["valid"],
            "automatic_certification": False,
            "claim_level": 0,
            "blocker_count": validation["error_count"],
            "warning_count": validation["warning_count"],
            "findings": findings,
        }

    baseline = next((item for item in baselines if item.get("id") == claim.get("baseline_id")), None)
    if baseline is None:
        findings.append(issue("error", "audit.baseline", "/claim/baseline_id", "claim baseline_id does not select a declared baseline"))
    else:
        if baseline.get("access_model") != input_contract.get("access_model"):
            findings.append(
                issue(
                    "error",
                    "audit.access-mismatch",
                    "/problem/classical_baselines",
                    "quantum and classical candidates use different access models",
                )
            )
        if baseline.get("output_contract") != output_contract.get("contract"):
            findings.append(
                issue(
                    "error",
                    "audit.output-mismatch",
                    "/problem/classical_baselines",
                    "quantum and classical outputs are not contract-equivalent",
                )
            )

    model_level = _MODEL_LEVEL.get(resources.get("model"), 0)
    required_model_level = _SCOPE_LEVEL.get(claim.get("scope"), 4)
    if model_level < required_model_level:
        findings.append(
            issue(
                "error",
                "audit.resource-level",
                "/resources/model",
                f"{claim_type} needs a higher-fidelity resource model",
            )
        )

    prep_cost = input_contract.get("preparation_cost", "unknown")
    oracle_cost = input_contract.get("oracle_construction_cost", "unknown")
    readout_cost = output_contract.get("readout_cost", "unknown")
    if required_model_level > 1:
        for path, value, label in (
            ("/problem/input/preparation_cost", prep_cost, "state/input preparation"),
            ("/problem/input/oracle_construction_cost", oracle_cost, "oracle or access construction"),
            ("/problem/output/readout_cost", readout_cost, "readout"),
        ):
            if is_unknown(value):
                findings.append(issue("error", "audit.missing-cost", path, f"{label} cost is unknown"))
    elif required_model_level == 1 and is_unknown(oracle_cost):
        findings.append(
            issue(
                "warning",
                "audit.conditional-oracle",
                "/problem/input/oracle_construction_cost",
                "query advantage is conditional on the stated oracle",
            )
        )

    if is_unknown(output_contract.get("accuracy")) or is_unknown(output_contract.get("success_probability")):
        findings.append(issue("error", "audit.output-quality", "/problem/output", "accuracy and success probability must be explicit"))

    expressions = resources.get("expressions", {})
    if claim.get("scope") == "end-to-end-wall-clock":
        required = {"total_time", "input_preparation", "readout", "classical_time"}
        missing = sorted(required - set(expressions))
        if missing:
            findings.append(issue("error", "audit.full-cost", "/resources/expressions", f"missing end-to-end terms: {', '.join(missing)}"))
    if claim.get("scope") == "physical" and resources.get("model") not in {"fault-tolerant", "end-to-end"}:
        findings.append(issue("error", "audit.physical", "/resources/model", "physical claims require a fault-tolerant or end-to-end model"))

    obligations = candidate.get("proof_obligations", [])
    by_kind: dict[str, list[dict[str, Any]]] = {}
    for obligation in obligations:
        if isinstance(obligation, dict):
            by_kind.setdefault(obligation.get("kind", ""), []).append(obligation)
    for kind in ("correctness", "resource", "advantage"):
        if not by_kind.get(kind):
            findings.append(issue("error", "audit.proof-obligation", "/proof_obligations", f"missing {kind} proof obligation"))

    if claim.get("status") == "formally-verified":
        for kind in ("correctness", "resource", "advantage"):
            statuses = {item.get("status") for item in by_kind.get(kind, [])}
            if not statuses.intersection({"proved", "formally-verified"}):
                findings.append(issue("error", "audit.formal-status", "/proof_obligations", f"{kind} is not proved"))
    if claim_type == "provable-speedup" and claim.get("status") != "formally-verified":
        findings.append(issue("error", "audit.provable-wording", "/claim/status", "provable speedup requires formal lower-bound evidence"))
    if claim.get("status") == "empirically-observed" and claim.get("scope") == "query":
        findings.append(issue("warning", "audit.empirical-query", "/claim", "empirical measurements do not establish a query-complexity theorem"))
    if not claim.get("evidence"):
        findings.append(issue("error", "audit.evidence", "/claim/evidence", "a speedup claim requires source or experiment evidence"))

    blockers = sum(item["severity"] == "error" for item in findings)
    warnings = sum(item["severity"] == "warning" for item in findings)
    if blockers:
        verdict = "blocked-insufficient-evidence"
    elif claim_type == "query-advantage":
        verdict = "conditional-query-advantage-ready-for-expert-review"
    else:
        verdict = "claim-ready-for-expert-review"
    return {
        "verdict": verdict,
        "eligible_for_expert_review": blockers == 0,
        "automatic_certification": False,
        "claim_level": required_model_level,
        "blocker_count": blockers,
        "warning_count": warnings,
        "findings": findings,
    }
