---
name: design-hybrid-quantum-workflow
description: Design auditable quantum-classical workflows by partitioning a formal problem into classical, quantum, and I/O stages; specifying access models, oracles, block encodings, embeddings, cutting, variational loops, outputs, error budgets, and end-to-end costs. Use for hybrid algorithm architecture, quantum kernel selection, PDE or simulation workflows, optimization decomposition, and feasibility screening before implementation or advantage claims.
---

# Design Hybrid Quantum Workflow

Design a workflow, not merely a circuit. Preserve the problem contract across every
classical-quantum boundary and expose every assumption that can erase a proposed speedup.

## Operating Rules

- Respond in the user's language unless the user requests another language.
- Read [decomposition-and-costing.md](references/decomposition-and-costing.md) before selecting a decomposition or estimating resources.
- Prefer a classical-only design when no defensible quantum bottleneck exists.
- Treat a simulator as a correctness and exploration tool, never as evidence of quantum execution speedup.
- Never claim quantum advantage automatically. Hand every advantage statement to `audit-quantum-advantage`.
- Label each material statement as `source_supported`, `model_inference`, or `uncertain`.
- Attach a primary paper or official project URL to every `source_supported` statement.
- Keep query complexity, logical resources, physical resources, and measured wall-clock performance separate.

## Workflow

1. Normalize the problem contract.
   - Specify the instance family and distribution, size parameters, input representation, output object, accuracy metric, error tolerance, confidence, and success criterion.
   - Specify whether inputs arrive explicitly, as a stream, through sample-query access, through sparse oracles, through QRAM, or as quantum states.
   - Record missing information as explicit assumptions and label it `model_inference` or `uncertain`.

2. Establish the classical reference path.
   - Describe the best-known exact, approximate, heuristic, and structure-aware methods that apply.
   - Identify preprocessing, data movement, solution extraction, and verification costs.
   - Do not use brute force as the sole baseline when stronger classical methods exist.

3. Generate candidate workflow DAGs.
   - Generate a classical-only candidate and each technically plausible hybrid candidate.
   - Type every node as `classical`, `quantum`, or `io`.
   - Type every edge by data representation, size, accuracy, and direction.
   - Reject a hybrid candidate when the quantum node does not address the measured end-to-end bottleneck.

4. Specify each quantum node.
   - Name the primitive and its preconditions.
   - Define state preparation, oracle construction, block encoding, reflections, measurements, and postselection.
   - Distinguish data embedding, operator block encoding, QUBO minor embedding, and hardware layout or routing.
   - Define the output contract before choosing QLS, QSVT, amplitude estimation, VQE, QAOA, Hamiltonian simulation, or circuit cutting.

5. Allocate error and failure budgets.
   - Split the total tolerance across modeling, discretization, state preparation, block encoding, algorithmic approximation, rotation synthesis, noise, sampling, and classical postprocessing.
   - Require the composed error and failure probability to meet the original problem contract.

6. Build the end-to-end cost ledger.
   - Include formulation, preprocessing, loading, compilation, mapping or embedding, reset, execution, shots, readout, communication, optimization, cutting reconstruction, decoding, and verification.
   - Report query counts together with concrete oracle gate, depth, width, and synthesis costs.
   - Produce both logical-resource and physical fault-tolerant scenarios when a deep coherent circuit is required.

7. Apply kill criteria.
   - Reject candidates with unmatched outputs, hidden linear data loading, uncontrolled condition number, growing cutting overhead, untrainable variational loops, or a classical method that exploits the same structure efficiently.
   - Retain a conditional candidate only when its unsatisfied assumptions are explicit and testable.

8. Produce the design packet.
   - Rank candidates by evidence strength, feasibility, expected end-to-end cost, verification difficulty, and unresolved risk.
   - State the next falsification experiment for every retained hybrid candidate.
   - End with a claim boundary that says exactly what the design does and does not establish.

## Output Contract

Return these sections in order:

1. `Problem contract`
2. `Classical reference workflow`
3. `Candidate workflow DAGs`
4. `Quantum node contracts`
5. `Error and failure budget`
6. `End-to-end cost ledger`
7. `Rejected candidates and reasons`
8. `Recommended candidate and falsification tests`
9. `Evidence and uncertainty register`
10. `Claim boundary`

For each candidate, emit at least this schema:

```yaml
candidate_id: string
nodes:
  - owner: classical|quantum|io
    operation: string
    input_contract: string
    output_contract: string
    cost_expression: string
quantum_contract:
  primitive: string
  input_access: string
  state_preparation: string
  oracle_or_block_encoding: string
  measurements: string
  error_budget: string
resource_scenarios:
  query: string
  logical: string
  physical: string
evidence_status: source_supported|model_inference|uncertain
open_obligations: []
allowed_claim: string
```
