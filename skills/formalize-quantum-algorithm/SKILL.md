---
name: formalize-quantum-algorithm
description: Convert an informal quantum, classical-quantum, oracle, or circuit-family design into the project-local QADL-IR 0.1 typed contract; validate its problem, access, output, stage DAG, resource expressions, proof obligations, claims, and provenance; render reviewable Z-style classical-interface and quantum-proof scaffolds; and route obligations to appropriate external formal or resource backends. Use for formal specifications, machine-readable algorithm candidates, proof plans, complexity contracts, oracle contracts, hybrid workflow contracts, or backend handoffs. QADL-IR is an exchange IR, not a proved quantum language or proof calculus.
---

# Formalize Quantum Algorithm

Turn a proposed algorithm into a precise, reviewable contract without overstating what the local
IR or renderer proves.

## Required Reference

Read [qadl-and-backends.md](references/qadl-and-backends.md) before choosing a formal notation,
proof backend, or resource backend. Use its capability boundaries as hard constraints.

## Non-Negotiable Boundaries

- Call QADL-IR 0.1 a project-local typed contract and intermediate representation.
- Never call QADL-IR a theorem prover, verified language, quantum semantics, or complexity proof.
- Use Z-style notation only for classical state, input, output, and interface schemas.
- Express quantum correctness as explicit proof obligations, then map them to Qbricks/Why3,
  SQIR/VOQC/Coq, qRHL, or another suitable external backend.
- Use Qualtran for compositional algorithm representation and resource analysis, not formal proof.
- Treat OpenQASM and QIR as low-level interchange/execution formats, not correctness certificates.
- Label material claims `source_supported`, `model_inference`, `uncertain`, or
  `needs_human_check`; attach primary or official URLs to `source_supported` claims.

## Workflow

1. Freeze the problem contract.
   - State the task family, instance distribution, size parameters, promises, input
     representation, access model, preparation/oracle cost, output representation, accuracy,
     success probability, and readout cost.
   - Match every classical baseline to the same access and output contract.
   - Write `unknown` instead of inventing a missing cost.

2. Build the QADL stage DAG.
   - Give every stage a stable ID, domain, operation, dependencies, repetitions, resource
     expressions, and pre/postcondition.
   - Name a primitive for every quantum stage.
   - Separate classical control, quantum kernels, measurement, I/O, and postprocessing.
   - Keep oracle calls visible; do not collapse an oracle into one physical gate.

3. Declare resources by model.
   - Choose exactly one current model: `query`, `logical-circuit`, `fault-tolerant`, or
     `end-to-end`.
   - Record query counts by named oracle; gate basis; gate/T/Toffoli counts; depth and scheduling
     assumptions; peak logical qubits; clean, dirty, and borrowed ancillas; measurements;
     classical work; and precision/failure budgets when applicable.
   - Keep symbolic expressions over declared size parameters. Numeric samples are consistency
     checks only.

4. Create atomic proof obligations.
   - Split functional correctness, termination, relational equivalence, resource bounds, access
     construction, implementation correspondence, robustness, reproducibility, and advantage.
   - Initialize unsupported obligations as `open` or `proof-sketch`.
   - Use `proved` or `formally-verified` only when the candidate names a real artifact; local
     validation checks presence and consistency, not proof truth.

5. Record provenance and claims.
   - Preserve source URLs, generation method, timestamp, seed, and parent candidate IDs.
   - Keep query, logical, physical, and end-to-end claims distinct.
   - Leave advantage claims to the dedicated audit workflow after formalization.

6. Validate before rendering.
   - Prefer MCP tool `qadl_validate_candidate` when available.
   - Otherwise, from the plugin root run:

     ```bash
     python3 scripts/qad_cli.py validate candidate.qadl.json --out validation.json
     ```

   - Fix every validation error. Preserve warnings about `unknown` expressions as open work.

7. Render the proof scaffold.
   - Prefer MCP tool `qadl_render_formal_contract` when available.
   - Otherwise run:

     ```bash
     python3 scripts/qad_cli.py formalize candidate.qadl.json --out formal-contract.md
     ```

   - Treat the result as a human-reviewable scaffold. The MCP result explicitly reports
     `machine_checked: false`.

8. Route each obligation.
   - Select backends by obligation, not by language popularity.
   - Preserve QADL IDs and assumptions in generated backend files or handoff notes.
   - If a backend or adapter is unavailable, return an explicit handoff plan; do not synthesize a
     successful proof result.

9. Optionally evaluate declared expressions at explicit points.
   - Prefer MCP tool `qadl_analyze_resources`, or run:

     ```bash
     python3 scripts/qad_cli.py analyze candidate.qadl.json \
       --points assets/examples/resource-points.json --out resource-samples.json
     ```

   - Describe the result as numeric evaluation, never an asymptotic proof.

## Output Contract

Return or create, as requested:

1. A valid QADL-IR 0.1 candidate.
2. The validation report, including unresolved warnings.
3. The rendered formal contract with its non-proof disclaimer intact.
4. A backend routing table with obligation ID, target, expected artifact, assumptions, and status.
5. An unresolved-items list using provenance labels.

Do not silently change the problem, access model, output contract, baseline, or claim while fixing
formalization errors.
