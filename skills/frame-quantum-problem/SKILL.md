---
name: frame-quantum-problem
description: Convert an informal computational problem into a falsifiable quantum-design contract with instance distribution, size parameters, promises, input access, output equivalence, accuracy, success probability, full boundary costs, and matched classical baselines. Use before proposing quantum primitives, hybrid decompositions, formal QADL files, or speedup claims.
---

# Frame Quantum Problem

Freeze what must be computed before choosing how to compute it. Ask only for information that cannot be recovered from the problem, data, code, or literature.

## Build The Contract

1. State the problem family and exact task: decision, function, search, sampling, estimation, optimization, linear algebra, simulation, or learning.
2. Define the instance distribution and every promise. Do not use worst-case language for average-case evidence.
3. Declare independent size parameters and their domains. Separate dimension, sparsity, condition number, rank, precision, confidence, time horizon, and solution count when they scale independently.
4. Select one input access model: explicit, stream, sample-query, black-box oracle, sparse oracle, QRAM, quantum state, Hamiltonian, or block encoding.
5. Charge input preparation and oracle construction. Use `unknown`, not zero, when no construction exists.
6. Specify an output contract, accuracy metric, target error, success probability, and readout cost. Distinguish a full classical object from a sample, expectation, scalar functional, certificate, or quantum state.
7. Declare classical baselines with the same access, output, accuracy, and success contract. Include structure-aware exact, approximate, randomized, and heuristic methods that are relevant.
8. Record source status for every theorem, benchmark, and assumption.

## Reject Contract Gaps

- Reject an HHL/QLS comparison that returns a quantum state while the classical baseline returns the full solution vector.
- Reject a QRAM or oracle assumption that is free only on the quantum side.
- Reject a PDE, simulation, or optimization comparison with unmatched error or target quality.
- Reject an empirical scaling claim without an instance distribution and per-size parameter tuning policy.
- Reject `polylog(N)` shorthand when hidden variables such as sparsity, conditioning, precision, normalization, or output samples are absent.

## Encode And Validate

Use [problem-contract.md](references/problem-contract.md) to map the contract into QADL-IR. Start from `assets/examples/grover-oracle-search.qadl.json` only as a structural example.

Run:

```bash
python3 scripts/qad_cli.py validate candidate.qadl.json
```

Keep warnings visible. A valid partial contract may still contain `unknown` costs, but such costs must block higher-level advantage claims later.

## Return The Result

Return the frozen contract, unresolved questions, excluded comparison classes, and the maximum claim scope currently supportable. Match the user's language.
