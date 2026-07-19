"""Schema and cross-field validation for QADL candidates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .expressions import ExpressionError, is_unknown, validate_expression


PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = PLUGIN_ROOT / "assets" / "schemas" / "qadl.schema.json"


def issue(severity: str, code: str, path: str, message: str) -> dict[str, str]:
    return {"severity": severity, "code": code, "path": path, "message": message}


def validate_candidate(candidate: Any) -> dict[str, Any]:
    """Return schema errors, semantic errors, and evidence-quality warnings."""
    issues: list[dict[str, str]] = []
    if not isinstance(candidate, dict):
        issues.append(issue("error", "candidate.type", "/", "candidate must be a JSON object"))
        return _result(issues)

    issues.extend(_schema_issues(candidate))
    issues.extend(_cross_field_issues(candidate))
    issues.sort(key=lambda item: (item["severity"] != "error", item["path"], item["code"]))
    return _result(issues)


def _result(issues: list[dict[str, str]]) -> dict[str, Any]:
    errors = sum(item["severity"] == "error" for item in issues)
    warnings = sum(item["severity"] == "warning" for item in issues)
    return {
        "valid": errors == 0,
        "error_count": errors,
        "warning_count": warnings,
        "issues": issues,
    }


def _schema_issues(candidate: dict[str, Any]) -> list[dict[str, str]]:
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError:
        return [
            issue(
                "error",
                "schema.unavailable",
                "/",
                "jsonschema is required for complete QADL validation; install scripts/requirements-core.txt",
            )
        ]

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    result = []
    for error in sorted(validator.iter_errors(candidate), key=lambda item: list(item.absolute_path)):
        pointer = "/" + "/".join(str(part) for part in error.absolute_path)
        result.append(issue("error", "schema", pointer, error.message))
    return result


def _cross_field_issues(candidate: dict[str, Any]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    problem = candidate.get("problem") if isinstance(candidate.get("problem"), dict) else {}
    algorithm = candidate.get("algorithm") if isinstance(candidate.get("algorithm"), dict) else {}
    resources = candidate.get("resources") if isinstance(candidate.get("resources"), dict) else {}
    claim = candidate.get("claim") if isinstance(candidate.get("claim"), dict) else {}

    parameters = problem.get("size_parameters") if isinstance(problem.get("size_parameters"), list) else []
    names = [item.get("name") for item in parameters if isinstance(item, dict) and isinstance(item.get("name"), str)]
    if len(names) != len(set(names)):
        result.append(issue("error", "parameter.duplicate", "/problem/size_parameters", "size parameter names must be unique"))
    variables = set(names)

    expression_fields: list[tuple[str, Any]] = []
    input_contract = problem.get("input") if isinstance(problem.get("input"), dict) else {}
    output_contract = problem.get("output") if isinstance(problem.get("output"), dict) else {}
    for name in ("preparation_cost", "oracle_construction_cost"):
        expression_fields.append((f"/problem/input/{name}", input_contract.get(name)))
    for name in ("accuracy", "success_probability", "readout_cost"):
        expression_fields.append((f"/problem/output/{name}", output_contract.get(name)))
    for baseline_index, baseline in enumerate(problem.get("classical_baselines", [])):
        if isinstance(baseline, dict) and isinstance(baseline.get("resources"), dict):
            for name, expression in baseline["resources"].items():
                expression_fields.append((f"/problem/classical_baselines/{baseline_index}/resources/{name}", expression))

    stages = algorithm.get("stages") if isinstance(algorithm.get("stages"), list) else []
    stage_ids: list[str] = []
    dependencies: dict[str, list[str]] = {}
    for index, stage in enumerate(stages):
        if not isinstance(stage, dict):
            continue
        stage_id = stage.get("id")
        if isinstance(stage_id, str):
            stage_ids.append(stage_id)
            dependencies[stage_id] = [value for value in stage.get("depends_on", []) if isinstance(value, str)]
        if stage.get("domain") == "quantum" and not stage.get("primitive"):
            result.append(issue("error", "stage.primitive", f"/algorithm/stages/{index}", "quantum stages must name a primitive"))
        expression_fields.append((f"/algorithm/stages/{index}/repetitions", stage.get("repetitions")))
        if isinstance(stage.get("resources"), dict):
            for name, expression in stage["resources"].items():
                expression_fields.append((f"/algorithm/stages/{index}/resources/{name}", expression))
    if len(stage_ids) != len(set(stage_ids)):
        result.append(issue("error", "stage.duplicate", "/algorithm/stages", "stage ids must be unique"))
    known_stages = set(stage_ids)
    for stage_id, values in dependencies.items():
        for dependency in values:
            if dependency not in known_stages:
                result.append(issue("error", "stage.dependency", f"/algorithm/stages/{stage_id}", f"unknown dependency: {dependency}"))
    if _has_cycle(dependencies):
        result.append(issue("error", "stage.cycle", "/algorithm/stages", "stage dependency graph must be acyclic"))

    correctness = algorithm.get("correctness_contract") if isinstance(algorithm.get("correctness_contract"), dict) else {}
    expression_fields.append(("/algorithm/correctness_contract/failure_probability", correctness.get("failure_probability")))
    for group_name in ("expressions", "error_budget"):
        group = resources.get(group_name)
        if isinstance(group, dict):
            for name, expression in group.items():
                expression_fields.append((f"/resources/{group_name}/{name}", expression))
    for path, expression in expression_fields:
        if expression is None:
            continue
        if is_unknown(expression):
            result.append(issue("warning", "expression.unknown", path, "cost or accuracy remains unknown"))
            continue
        try:
            validate_expression(expression, variables)
        except ExpressionError as exc:
            result.append(issue("error", "expression.invalid", path, str(exc)))

    obligations = candidate.get("proof_obligations") if isinstance(candidate.get("proof_obligations"), list) else []
    obligation_ids = [item.get("id") for item in obligations if isinstance(item, dict)]
    if len(obligation_ids) != len(set(obligation_ids)):
        result.append(issue("error", "proof.duplicate", "/proof_obligations", "proof obligation ids must be unique"))
    for index, obligation in enumerate(obligations):
        if not isinstance(obligation, dict):
            continue
        if obligation.get("status") in {"proved", "formally-verified"} and not obligation.get("artifacts"):
            result.append(
                issue(
                    "error",
                    "proof.artifact",
                    f"/proof_obligations/{index}/artifacts",
                    "proved obligations require a proof or source artifact",
                )
            )

    claim_type = claim.get("type")
    if claim_type == "none" and claim.get("status") != "not-claimed":
        result.append(issue("error", "claim.consistency", "/claim/status", "a none claim must use status not-claimed"))
    if claim_type != "none" and claim.get("status") == "not-claimed":
        result.append(issue("error", "claim.consistency", "/claim/status", "an asserted claim cannot use status not-claimed"))
    if claim_type != "none" and not problem.get("classical_baselines"):
        result.append(issue("error", "claim.baseline", "/problem/classical_baselines", "a speedup claim requires at least one classical baseline"))
    return result


def _has_cycle(graph: dict[str, list[str]]) -> bool:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        for dependency in graph.get(node, []):
            if dependency in graph and visit(dependency):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in graph)
