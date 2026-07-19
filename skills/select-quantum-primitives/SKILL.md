---
name: select-quantum-primitives
description: Match a frozen problem contract and structural bottleneck to theorem-backed quantum primitives such as amplitude amplification or estimation, quantum walks, phase estimation, Hamiltonian simulation, block encoding, QSVT, linear-system methods, or variational kernels. Use to generate and filter algorithm-level building blocks before circuit synthesis or AI search.
---

# Select Quantum Primitives

Select primitives by theorem preconditions and information flow, not by keyword similarity or available SDK demos.

## Generate Candidates

1. Read the frozen problem contract and [primitive-catalog.md](references/primitive-catalog.md).
2. Identify the actual bottleneck: search, estimation, spectral transformation, walk/hitting process, simulation, linear solve, sampling, optimization, or state preparation.
3. Generate at least one classical-only control, one no-advantage/null candidate, and only the quantum candidates whose access and output contracts match.
4. For every quantum primitive, record theorem preconditions, input construction, output semantics, success amplification, asymptotic variables, and a primary source.
5. Compose primitives only when interface types and error budgets match. Create an obligation for every unproved composition step.
6. Reject candidates whose hidden costs dominate the proposed gain before spending search budget.

## Score Preconditions, Not Hype

Return a table with:

- primitive and algorithm role;
- matched bottleneck;
- satisfied and unsatisfied preconditions;
- access and output transformations;
- symbolic query, gate, qubit, depth, precision, and sample costs;
- strongest classical or dequantized attack;
- evidence status;
- keep, revise, or reject decision.

Do not lower to Qiskit, PennyLane, Cirq, OpenQASM, or QIR yet unless a small executable test is needed to falsify a candidate.

## Apply Hard Filters

- Reject amplitude amplification when no coherent verifier or inverse is constructible.
- Reject amplitude estimation when oracle depth and repeated coherent calls are unaffordable.
- Reject QLS/QSVT when block encoding, normalization, conditioning, precision, or useful readout is unspecified.
- Reject quantum-walk claims when preparation, update, checking, spectral gap, or hitting assumptions are missing.
- Reject VQA candidates that omit trainability, all shots/gradients/restarts, and matched classical solvers.
- Treat cutting, mitigation, routing, and compilation as execution transformations, not intrinsic algorithmic speedups.

## Return The Result

Return surviving primitive graphs and their open proof obligations in the user's language. Route candidates with significant classical/quantum boundaries to `$design-hybrid-quantum-workflow`; route formalizable candidates to `$formalize-quantum-algorithm`.
