"""Render QADL proof obligations as a qmd-prover handoff project."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .validation import validate_candidate


HANDOFF_VERSION = "0.1"
_PLACEHOLDER = re.compile(r"\{\{([A-Za-z0-9][A-Za-z0-9._-]*)\}\}")


def render_qmd_handoff(candidate: dict[str, Any], proofs: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return deterministic qmd-prover source and provenance without claiming proof."""
    validation = validate_candidate(candidate)
    if not validation["valid"]:
        codes = ", ".join(item["code"] for item in validation["issues"] if item["severity"] == "error")
        raise ValueError(f"cannot export an invalid QADL candidate: {codes or 'validation failed'}")

    obligations = candidate.get("proof_obligations", [])
    obligation_ids = {item["id"] for item in obligations}
    proof_map = _normalize_proofs(proofs)
    unknown = sorted(set(proof_map) - obligation_ids)
    if unknown:
        raise ValueError(f"proof sidecar names unknown obligations: {', '.join(unknown)}")

    qmd_ids = {
        item["id"]: _qmd_id(candidate["candidate_id"], item["id"])
        for item in obligations
    }
    contract_qmd_id = _contract_qmd_id(candidate["candidate_id"])
    candidate_bytes = _canonical_json(candidate).encode("utf-8")
    candidate_sha256 = hashlib.sha256(candidate_bytes).hexdigest()
    proof_sha256 = hashlib.sha256(_canonical_json(proof_map).encode("utf-8")).hexdigest()
    introduced = str(candidate.get("provenance", {}).get("created_at", "1970-01-01")).split("T", 1)[0]

    document = _render_document(candidate, obligations, qmd_ids, contract_qmd_id, proof_map, introduced)
    manifest = {
        "handoff_version": HANDOFF_VERSION,
        "candidate_id": candidate["candidate_id"],
        "candidate_sha256": candidate_sha256,
        "proof_sidecar_sha256": proof_sha256,
        "machine_checked": False,
        "verifier_boundary": (
            "qmd-prover provides mechanical dependency checks and optional independent AI review; "
            "it is not a Lean/Coq-style formal proof certificate."
        ),
        "status_policy": "qmd-prover verdicts do not update QADL proof statuses automatically.",
        "qadl_contract_qmd_id": contract_qmd_id,
        "conditional_on_qadl_contract": True,
        "obligations": [
            {
                "qadl_id": item["id"],
                "qadl_kind": item["kind"],
                "qadl_status_at_export": item["status"],
                "qmd_id": qmd_ids[item["id"]],
                "proof_supplied": item["id"] in proof_map,
            }
            for item in obligations
        ],
    }
    return {
        "document": document,
        "manifest": manifest,
        "external_basis": _render_external_basis(candidate),
        "candidate_json": json.dumps(candidate, indent=2, ensure_ascii=False) + "\n",
        "machine_checked": False,
    }


def write_qmd_handoff(
    candidate: dict[str, Any],
    project: str | Path,
    proofs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Write a handoff into an existing qmd-prover project."""
    project_path = Path(project).resolve()
    agents_path = project_path / "AGENTS.md"
    config_path = project_path / ".qmd-prover" / "config.yml"
    if not agents_path.is_file() or not config_path.is_file():
        raise ValueError("target is not initialized; run `qmd-prover init` in an empty target directory first")
    agents = agents_path.read_text(encoding="utf-8")
    if "<!-- qmd-prover-contract:start" not in agents or "<!-- qmd-prover-contract:end -->" not in agents:
        raise ValueError("target AGENTS.md does not contain the qmd-prover managed contract")

    rendered = render_qmd_handoff(candidate, proofs)
    manifest_path = project_path / "qadl-handoff.json"
    index_path = project_path / "index.qmd"
    if index_path.exists() and not manifest_path.exists():
        raise ValueError("target index.qmd is not owned by a QADL handoff; choose a new qmd-prover project")
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        previous_hash = previous.get("candidate_sha256")
        current_hash = rendered["manifest"]["candidate_sha256"]
        if previous_hash != current_hash:
            raise ValueError("candidate changed; export to a new project so protected qmd statements are not overwritten")

    index_path.write_text(rendered["document"], encoding="utf-8")
    (project_path / "qadl-candidate.json").write_text(rendered["candidate_json"], encoding="utf-8")
    manifest_path.write_text(
        json.dumps(rendered["manifest"], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    external_path = project_path / ".qmd-prover" / ".external.qmd"
    external_basis_status = "preserved"
    if not external_path.exists():
        external_path.write_text(rendered["external_basis"], encoding="utf-8")
        external_basis_status = "created"
    quarto_chapter_status = _ensure_quarto_chapter(project_path / "_quarto.yml", "index.qmd")

    return {
        "exported": True,
        "project": str(project_path),
        "candidate_id": candidate["candidate_id"],
        "candidate_sha256": rendered["manifest"]["candidate_sha256"],
        "files_written": ["index.qmd", "qadl-candidate.json", "qadl-handoff.json"],
        "external_basis": external_basis_status,
        "quarto_chapter": quarto_chapter_status,
        "machine_checked": False,
        "next_command": "qmd-prover inspect project",
    }


def _normalize_proofs(proofs: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if proofs is None:
        return {}
    if not isinstance(proofs, dict):
        raise ValueError("proof sidecar must be a JSON object keyed by QADL obligation id")
    normalized: dict[str, dict[str, Any]] = {}
    for obligation_id, record in proofs.items():
        if not isinstance(obligation_id, str) or not isinstance(record, dict):
            raise ValueError("each proof sidecar entry must map an obligation id to an object")
        text = record.get("text")
        intent = record.get("intent", "proof")
        draft = record.get("draft", False)
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"proof sidecar entry {obligation_id} requires nonempty text")
        if intent not in {"proof", "refutation"}:
            raise ValueError(f"proof sidecar entry {obligation_id} has invalid intent: {intent}")
        if not isinstance(draft, bool):
            raise ValueError(f"proof sidecar entry {obligation_id} draft must be boolean")
        normalized[obligation_id] = {"text": text.strip(), "intent": intent, "draft": draft}
    return normalized


def _render_document(
    candidate: dict[str, Any],
    obligations: list[dict[str, Any]],
    qmd_ids: dict[str, str],
    contract_qmd_id: str,
    proof_map: dict[str, dict[str, Any]],
    introduced: str,
) -> str:
    title = candidate.get("title") or candidate["candidate_id"]
    lines = [
        "---",
        f"title: {json.dumps(f'QADL proof handoff: {title}', ensure_ascii=False)}",
        "---",
        "",
        f"# {title}",
        "",
        "> This file is a qmd-prover handoff for QADL proof obligations. Structural checks and",
        "> optional independent AI review are not Lean/Coq-style formal verification and do not",
        "> automatically change the source QADL evidence status.",
        "",
        "## Imported QADL contract",
        "",
        (
            f':::: {{#{contract_qmd_id} .definition .assumed name="Imported QADL candidate contract" '
            f'date="{introduced}"}}'
        ),
        _render_candidate_contract(candidate),
        "::::",
        "",
        "> This definition imports the candidate as data. It does not establish semantic correctness,",
        "> implementation correspondence, resource expressions, or quantum advantage.",
        "",
    ]
    for obligation in obligations:
        obligation_id = obligation["id"]
        qmd_id = qmd_ids[obligation_id]
        statement = obligation["statement"].strip()
        name = f"QADL {obligation_id} ({obligation['kind']})"
        fence = _fence(statement)
        lines.extend(
            [
                f"## {obligation_id}",
                "",
                f'{fence} {{#{qmd_id} .theorem .goal name={json.dumps(name)} date="{introduced}"}}',
                statement,
                fence,
                "",
                f"> Source QADL status: `{obligation['status']}`. Proposed method: {obligation.get('method') or 'unspecified'}",
                "",
            ]
        )
        proof = proof_map.get(obligation_id)
        if proof is None:
            continue
        references = {**qmd_ids, "qadl-contract": contract_qmd_id}
        proof_text = _replace_placeholders(proof["text"], references, obligation_id)
        if f"@{contract_qmd_id}" not in proof_text:
            raise ValueError(f"proof {obligation_id} must cite {{{{qadl-contract}}}} at its load-bearing use")
        classes = [".proof"]
        if proof["intent"] == "refutation":
            classes.append(".disproof")
        if proof["draft"]:
            classes.append(".draft")
        proof_fence = _fence(proof_text)
        lines.extend(
            [
                f'{proof_fence} {{{" ".join(classes)} of="{qmd_id}"}}',
                proof_text,
                proof_fence,
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _replace_placeholders(text: str, qmd_ids: dict[str, str], current: str) -> str:
    def replace(match: re.Match[str]) -> str:
        obligation_id = match.group(1)
        if obligation_id not in qmd_ids:
            raise ValueError(f"proof {current} cites unknown QADL obligation placeholder: {obligation_id}")
        if obligation_id == current:
            raise ValueError(f"proof {current} cannot cite itself")
        return f"@{qmd_ids[obligation_id]}"

    return _PLACEHOLDER.sub(replace, text)


def _render_external_basis(candidate: dict[str, Any]) -> str:
    sources: list[str] = []
    for baseline in candidate.get("problem", {}).get("classical_baselines", []):
        source = baseline.get("source", {})
        if source.get("url"):
            sources.append(source["url"])
    for source in candidate.get("claim", {}).get("evidence", []):
        if source.get("url"):
            sources.append(source["url"])
    for source in candidate.get("provenance", {}).get("sources", []):
        if source.get("url"):
            sources.append(source["url"])
    for obligation in candidate.get("proof_obligations", []):
        sources.extend(value for value in obligation.get("artifacts", []) if isinstance(value, str) and value)

    lines = [
        "# External mathematical basis for this QADL handoff",
        "",
        "Only results explicitly identified in the sources below may be imported as external premises.",
        "Each proof must state the result it uses and check that its hypotheses match the QADL contract.",
        "A URL or artifact entry is permission to consult a source, not an assertion that it proves the obligation.",
        "",
    ]
    for source in sorted(set(sources)):
        lines.append(f"- `{source}`")
    if not sources:
        lines.append("No external results are declared.")
    return "\n".join(lines) + "\n"


def _render_candidate_contract(candidate: dict[str, Any]) -> str:
    problem = candidate["problem"]
    algorithm = candidate["algorithm"]
    resources = candidate["resources"]
    input_contract = problem["input"]
    output_contract = problem["output"]
    correctness = algorithm["correctness_contract"]
    parameters = ", ".join(
        f'`{item["name"]}` in `{item["domain"]}` with lower bound {item.get("lower_bound", "unspecified")}'
        for item in problem["size_parameters"]
    )
    lines = [
        f'The term "the candidate algorithm" denotes QADL candidate `{candidate["candidate_id"]}`.',
        f'Its problem family is `{problem["family"]}` and its instance distribution is: {problem["instance_distribution"]}',
        f'Its size parameters are: {parameters}.',
        f'Its task is: {problem["task"]}',
        "Its promises are:",
    ]
    lines.extend(f"- {promise}" for promise in problem["promises"])
    lines.extend(
        [
            f'Its input access model is `{input_contract["access_model"]}` with representation: '
            f'{input_contract["representation"]}',
            f'Its declared input preparation cost is `{input_contract["preparation_cost"]}` and its oracle '
            f'construction cost is `{input_contract["oracle_construction_cost"]}`.',
            "Its input assumptions are:",
        ]
    )
    lines.extend(f"- {assumption}" for assumption in input_contract["assumptions"])
    lines.extend(
        [
            f'Its output contract is: {output_contract["contract"]}',
            f'Output representation is `{output_contract["representation"]}`, accuracy is '
            f'`{output_contract["accuracy"]}`, success probability is '
            f'`{output_contract["success_probability"]}`, and readout cost is '
            f'`{output_contract["readout_cost"]}`.',
            f'The algorithm correctness precondition is: {correctness["precondition"]}',
            f'The algorithm correctness postcondition is: {correctness["postcondition"]}',
            f'The declared failure probability is `{correctness["failure_probability"]}`.',
            "The matched classical baselines are:",
        ]
    )
    for baseline in problem["classical_baselines"]:
        baseline_resources = ", ".join(f"{name} = {value}" for name, value in baseline["resources"].items())
        lines.append(
            f'- `{baseline["id"]}` uses access `{baseline["access_model"]}`, returns '
            f'"{baseline["output_contract"]}", declares {baseline_resources}, and cites '
            f'`{baseline["source"]["url"]}`.'
        )
    lines.append("The declared stage sequence and resource entries are:")
    for stage in algorithm["stages"]:
        stage_resources = ", ".join(f"{name} = {value}" for name, value in stage["resources"].items()) or "none"
        lines.append(
            f'- `{stage["id"]}` ({stage["domain"]}): {stage["operation"]} '
            f'Repetitions = `{stage["repetitions"]}`; resources: {stage_resources}.'
        )
    totals = ", ".join(f"{name} = {value}" for name, value in resources["expressions"].items())
    error_budget = ", ".join(f"{name} = {value}" for name, value in resources["error_budget"].items())
    lines.extend(
        [
            f'The declared aggregate resource model is `{resources["model"]}` with expressions: {totals}.',
            f"Its declared error budget is: {error_budget}.",
            "Its resource-model assumptions are:",
        ]
    )
    lines.extend(f"- {assumption}" for assumption in resources["assumptions"])
    lines.extend(
        [
            "These are imported contract declarations. Any claim that they correspond to an executable",
            "implementation remains a separate QADL proof obligation.",
        ]
    )
    return "\n".join(lines)


def _qmd_id(candidate_id: str, obligation_id: str) -> str:
    candidate_slug = _slug(candidate_id)[:40]
    obligation_slug = _slug(obligation_id)[:40]
    digest = hashlib.sha256(f"{candidate_id}\0{obligation_id}".encode("utf-8")).hexdigest()[:8]
    return f"thm-main-qadl-{candidate_slug}-{obligation_slug}-{digest}"


def _contract_qmd_id(candidate_id: str) -> str:
    candidate_slug = _slug(candidate_id)[:56]
    digest = hashlib.sha256(candidate_id.encode("utf-8")).hexdigest()[:8]
    return f"def-qadl-contract-{candidate_slug}-{digest}"


def _ensure_quarto_chapter(config_path: Path, chapter: str) -> str:
    if not config_path.exists():
        return "config-missing"
    try:
        import yaml
    except ImportError as exc:
        raise ValueError("PyYAML is required to update the qmd-prover Quarto chapter list") from exc

    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("qmd-prover _quarto.yml must contain a YAML object")
    book = config.setdefault("book", {})
    if not isinstance(book, dict):
        raise ValueError("qmd-prover _quarto.yml book entry must be a YAML object")
    chapters = book.setdefault("chapters", [])
    if not isinstance(chapters, list):
        raise ValueError("qmd-prover _quarto.yml book.chapters must be a YAML list")
    if chapter in chapters:
        return "preserved"
    chapters.insert(0, chapter)
    config_path.write_text(
        yaml.safe_dump(config, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return "added"


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "item"


def _fence(text: str) -> str:
    longest = max((len(match.group(0)) for match in re.finditer(r"^:+$", text, re.MULTILINE)), default=0)
    return ":" * max(4, longest + 1)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
