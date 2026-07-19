"""Reproducible discrete search and Pareto archiving for QADL candidates."""

from __future__ import annotations

import copy
import hashlib
import itertools
import json
import math
import random
from pathlib import Path
from typing import Any

from .audit import analyze_resources, audit_advantage
from .validation import validate_candidate


PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SEARCH_SCHEMA_PATH = PLUGIN_ROOT / "assets" / "schemas" / "search-space.schema.json"


class SearchSpaceError(ValueError):
    """Raised when a declarative search space is invalid."""


class SearchEvaluator:
    """Materialize genomes and score only declared, deterministic metrics."""

    def __init__(self, search_space: dict[str, Any], seed: int = 0):
        validate_search_space(search_space)
        self.search_space = search_space
        self.base = search_space["base_candidate"]
        self.choices = search_space["choices"]
        self.evaluation = search_space["evaluation"]
        self.seed = seed

    @property
    def dimensions(self) -> tuple[int, ...]:
        return tuple(len(choice["values"]) for choice in self.choices)

    @property
    def maximum_candidates(self) -> int:
        return math.prod(self.dimensions)

    def materialize(self, genome: tuple[int, ...]) -> dict[str, Any]:
        if len(genome) != len(self.choices):
            raise SearchSpaceError("genome dimensionality does not match choices")
        candidate = copy.deepcopy(self.base)
        selected = []
        for gene, choice in zip(genome, self.choices):
            values = choice["values"]
            if gene < 0 or gene >= len(values):
                raise SearchSpaceError(f"gene {gene} is outside its choice range")
            value = copy.deepcopy(values[gene])
            _set_json_pointer(candidate, choice["path"], value)
            selected.append({"path": choice["path"], "value": value})
        digest = hashlib.sha256(json.dumps(selected, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:12]
        base_id = str(self.base.get("candidate_id", "candidate"))
        candidate["candidate_id"] = f"{base_id}.{digest}"
        provenance = candidate.setdefault("provenance", {})
        provenance["random_seed"] = self.seed
        parent_ids = provenance.setdefault("parent_ids", [])
        if base_id not in parent_ids:
            parent_ids.append(base_id)
        return candidate

    def evaluate(self, genome: tuple[int, ...]) -> dict[str, Any]:
        candidate = self.materialize(genome)
        validation = validate_candidate(candidate)
        audit = audit_advantage(candidate)
        resource_report = analyze_resources(candidate, self.evaluation["parameter_points"])
        obligations = candidate.get("proof_obligations", [])
        closed = sum(
            isinstance(item, dict) and item.get("status") in {"tested", "proof-sketch", "proved", "formally-verified"}
            for item in obligations
        )
        metrics: dict[str, float] = {
            "validation_errors": float(validation["error_count"]),
            "validation_warnings": float(validation["warning_count"]),
            "claim_blockers": float(audit["blocker_count"]),
            "claim_warnings": float(audit["warning_count"]),
            "proof_coverage": float(closed / len(obligations)) if obligations else 0.0,
        }
        for name, summary in resource_report["summaries"].items():
            for statistic in ("min", "max", "mean", "last"):
                metrics[f"resource:{name}:{statistic}"] = float(summary[statistic])
        violations = _constraint_violations(metrics, self.evaluation["hard_constraints"])
        return {
            "genome": list(genome),
            "candidate_id": candidate["candidate_id"],
            "candidate": candidate,
            "metrics": metrics,
            "feasible": not violations,
            "constraint_violations": violations,
            "audit_verdict": audit["verdict"],
        }

    def scalar_score(self, record: dict[str, Any]) -> float:
        if record["constraint_violations"]:
            return -1_000_000.0 - 10_000.0 * len(record["constraint_violations"])
        score = 0.0
        for objective in self.evaluation["objectives"]:
            value = record["metrics"].get(objective["metric"])
            if value is None or not math.isfinite(value):
                return -1_000_000.0
            sign = -1.0 if objective["direction"] == "minimize" else 1.0
            score += sign * float(objective.get("weight", 1.0)) * value
        return score


def validate_search_space(search_space: Any) -> None:
    if not isinstance(search_space, dict):
        raise SearchSpaceError("search space must be a JSON object")
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        missing = {"search_space_version", "base_candidate", "choices", "evaluation"} - set(search_space)
        if missing:
            raise SearchSpaceError(f"missing search-space fields: {', '.join(sorted(missing))}")
        return
    schema = json.loads(SEARCH_SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(search_space), key=lambda item: list(item.absolute_path))
    if errors:
        details = "; ".join(f"/{'/'.join(map(str, item.absolute_path))}: {item.message}" for item in errors[:8])
        raise SearchSpaceError(details)
    for choice in search_space["choices"]:
        _get_json_pointer(search_space["base_candidate"], choice["path"])


def search_candidates(
    search_space: dict[str, Any],
    method: str = "evolutionary",
    budget: int = 64,
    seed: int = 0,
    population_size: int = 16,
) -> dict[str, Any]:
    """Search a finite declarative space and return its nondominated archive."""
    if method not in {"random", "evolutionary"}:
        raise SearchSpaceError("method must be random or evolutionary")
    if budget < 1:
        raise SearchSpaceError("budget must be positive")
    evaluator = SearchEvaluator(search_space, seed=seed)
    requested_budget = budget
    budget = min(budget, evaluator.maximum_candidates)
    rng = random.Random(seed)
    if method == "random":
        genomes = _random_genomes(evaluator.dimensions, budget, rng)
        records = [evaluator.evaluate(genome) for genome in genomes]
    else:
        records = _evolutionary_records(evaluator, budget, population_size, rng)
    archive = pareto_archive(records, evaluator.evaluation["objectives"])
    return {
        "method": method,
        "seed": seed,
        "budget_requested": requested_budget,
        "budget_effective": budget,
        "evaluated": len(records),
        "search_space_size": evaluator.maximum_candidates,
        "archive_size": len(archive),
        "archive": archive,
        "limitations": [
            "Built-in metrics validate contracts and declared resources; they do not prove semantic correctness.",
            "A reward or Pareto score cannot establish quantum advantage.",
        ],
    }


def pareto_archive(records: list[dict[str, Any]], objectives: list[dict[str, Any]]) -> list[dict[str, Any]]:
    feasible = [record for record in records if record["feasible"] and _has_metrics(record, objectives)]
    if not feasible:
        return sorted(records, key=lambda item: (len(item["constraint_violations"]), item["candidate_id"]))[:1]
    archive = []
    for candidate in feasible:
        if any(_dominates(other, candidate, objectives) for other in feasible if other is not candidate):
            continue
        archive.append(candidate)
    return sorted(archive, key=lambda item: item["candidate_id"])


def _evolutionary_records(
    evaluator: SearchEvaluator,
    budget: int,
    population_size: int,
    rng: random.Random,
) -> list[dict[str, Any]]:
    population_size = min(max(1, population_size), budget)
    initial = _random_genomes(evaluator.dimensions, population_size, rng)
    records = [evaluator.evaluate(genome) for genome in initial]
    seen = {tuple(record["genome"]) for record in records}
    attempts = 0
    while len(records) < budget and attempts < budget * 100:
        attempts += 1
        contestants = rng.sample(records, k=min(3, len(records)))
        parent = max(contestants, key=evaluator.scalar_score)
        genome = list(parent["genome"])
        dimension = rng.randrange(len(genome))
        if evaluator.dimensions[dimension] > 1:
            options = [index for index in range(evaluator.dimensions[dimension]) if index != genome[dimension]]
            genome[dimension] = rng.choice(options)
        child = tuple(genome)
        if child in seen:
            continue
        seen.add(child)
        records.append(evaluator.evaluate(child))
    if len(records) < budget:
        for genome in itertools.product(*(range(size) for size in evaluator.dimensions)):
            if genome not in seen:
                records.append(evaluator.evaluate(genome))
                seen.add(genome)
                if len(records) == budget:
                    break
    return records


def _random_genomes(dimensions: tuple[int, ...], count: int, rng: random.Random) -> list[tuple[int, ...]]:
    total = math.prod(dimensions)
    if total <= 100_000:
        genomes = list(itertools.product(*(range(size) for size in dimensions)))
        rng.shuffle(genomes)
        return genomes[:count]
    result: set[tuple[int, ...]] = set()
    while len(result) < count:
        result.add(tuple(rng.randrange(size) for size in dimensions))
    return list(result)


def _has_metrics(record: dict[str, Any], objectives: list[dict[str, Any]]) -> bool:
    return all(objective["metric"] in record["metrics"] for objective in objectives)


def _dominates(left: dict[str, Any], right: dict[str, Any], objectives: list[dict[str, Any]]) -> bool:
    no_worse = True
    strictly_better = False
    for objective in objectives:
        left_value = left["metrics"][objective["metric"]]
        right_value = right["metrics"][objective["metric"]]
        if objective["direction"] == "minimize":
            no_worse &= left_value <= right_value
            strictly_better |= left_value < right_value
        else:
            no_worse &= left_value >= right_value
            strictly_better |= left_value > right_value
    return no_worse and strictly_better


def _constraint_violations(metrics: dict[str, float], constraints: list[dict[str, Any]]) -> list[str]:
    operators = {
        "==": lambda left, right: left == right,
        "<=": lambda left, right: left <= right,
        ">=": lambda left, right: left >= right,
        "<": lambda left, right: left < right,
        ">": lambda left, right: left > right,
    }
    violations = []
    for constraint in constraints:
        metric = constraint["metric"]
        if metric not in metrics:
            violations.append(f"metric unavailable: {metric}")
            continue
        if not operators[constraint["op"]](metrics[metric], float(constraint["value"])):
            violations.append(f"{metric} {constraint['op']} {constraint['value']} failed (actual {metrics[metric]})")
    return violations


def _pointer_parts(pointer: str) -> list[str]:
    if not pointer.startswith("/"):
        raise SearchSpaceError(f"JSON pointer must start with '/': {pointer}")
    return [part.replace("~1", "/").replace("~0", "~") for part in pointer[1:].split("/")]


def _get_json_pointer(document: Any, pointer: str) -> Any:
    current = document
    for part in _pointer_parts(pointer):
        if isinstance(current, list):
            try:
                current = current[int(part)]
            except (ValueError, IndexError) as exc:
                raise SearchSpaceError(f"invalid list pointer segment {part!r} in {pointer}") from exc
        elif isinstance(current, dict) and part in current:
            current = current[part]
        else:
            raise SearchSpaceError(f"pointer does not exist in base candidate: {pointer}")
    return current


def _set_json_pointer(document: Any, pointer: str, value: Any) -> None:
    parts = _pointer_parts(pointer)
    if not parts:
        raise SearchSpaceError("cannot replace the candidate root")
    current = document
    for part in parts[:-1]:
        if isinstance(current, list):
            current = current[int(part)]
        else:
            current = current[part]
    final = parts[-1]
    if isinstance(current, list):
        current[int(final)] = value
    elif isinstance(current, dict) and final in current:
        current[final] = value
    else:
        raise SearchSpaceError(f"pointer does not exist in base candidate: {pointer}")
