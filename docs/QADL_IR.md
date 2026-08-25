# QADL-IR 0.1 Contract

Quantum Algorithm Design Language Intermediate Representation (QADL-IR) is the project's machine-readable exchange contract for quantum and quantum-classical algorithm candidates.

## Status

Version `0.1` is experimental. The normative structural contract is `assets/schemas/qadl.schema.json`; cross-field invariants are implemented in `scripts/qadlib/validation.py`. The schema identifier is the stable URN `urn:quantum-algorithm-designer:schema:qadl:0.1`.

QADL-IR is not a proof calculus, executable quantum semantics, or circuit interchange format. It preserves algorithm-level obligations so that specialized backends can be selected without discarding the original problem contract.

## Top-level objects

| Field | Purpose |
| --- | --- |
| `qadl_version` | Selects the data-contract version. |
| `candidate_id` | Gives the candidate a stable local identity. |
| `problem` | Records parameters, promises, access, output, and classical baselines. |
| `algorithm` | Describes the typed stage DAG and correctness contract. |
| `resources` | Declares model scope, resource expressions, and error budget. |
| `proof_obligations` | Tracks correctness, resource, and advantage obligations with evidence status. |
| `claim` | Records claim type, scope, selected baseline, status, and evidence. |
| `provenance` | Records sources, parents, generator, seed, and review state. |

## Stage DAG

Stages distinguish work domains such as classical preprocessing, quantum kernels, measurement, control, I/O, optimization, and decoding. Every stage has a unique ID and explicit dependencies. The graph must be acyclic, and quantum stages must name the primitive whose preconditions they rely on.

This boundary is intentional: moving work outside the quantum stage does not make its cost disappear.

## Expression language

Costs, probabilities, repetitions, and resource expressions use a restricted arithmetic language over declared size parameters. The evaluator accepts numeric constants, declared variables, and a small allowlist of mathematical functions and operators. It rejects attribute access, imports, comprehensions, arbitrary calls, and other executable Python constructs.

The literal `unknown` preserves an unresolved quantity. Unknown values generate warnings or claim blockers depending on scope; they are never evaluated as zero.

Numeric evaluation at chosen points is a consistency check. It is not an asymptotic proof.

## Compatibility

- A consumer must reject an unsupported `qadl_version` rather than guessing.
- Patch releases may strengthen validation without changing the `0.1` schema version when they only enforce an existing invariant.
- A structural or semantic contract change requires a new QADL version and migration notes.
- Unknown fields are rejected by the current schema to prevent silent loss across tools.
- Lowering to circuit or proof backends must retain a mapping to original stage IDs and proof obligations.

## Search-space contract

`assets/schemas/search-space.schema.json` defines search-space version `0.1` with URN `urn:quantum-algorithm-designer:schema:search-space:0.1`. A search space contains one base QADL candidate, finite JSON-pointer choices, evaluation parameter points, objectives, and hard constraints.

Search-space validation does not prove that a chosen dimension is scientifically meaningful. Reviewers must check that choices preserve the problem contract and do not give one candidate privileged access or a weaker output requirement.

## Backend handoff

QADL obligations may be routed to:

- Qbricks/Why3 for supported parametric circuit-building proofs;
- SQIR/VOQC for Coq circuit semantics and verified transformations;
- qRHL-style relational reasoning where supported;
- qmd-prover for protected proof-obligation graphs and independent AI review, explicitly not formal verification;
- Qualtran or dedicated estimators for executable resource decompositions;
- OpenQASM or QIR after algorithm-level obligations remain linked.

The qmd-prover renderer/exporter is built in as a review handoff; the other entries remain routing targets rather than built-in proof integrations. Unsupported obligations remain open, and no qmd-prover verdict automatically changes a QADL status.
