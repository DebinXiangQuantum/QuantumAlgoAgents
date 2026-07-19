---
name: orchestrate-quantum-algorithm-design
description: Coordinate an evidence-gated workflow from problem framing through primitive selection, hybrid decomposition, QADL formalization, AI or evolutionary search, verification, and quantum-advantage audit. Use for end-to-end quantum algorithm design, automated candidate discovery, redesign of an existing algorithm, or any request that spans several Quantum Algorithm Designer skills.
---

# Orchestrate Quantum Algorithm Design

Treat algorithm discovery as a gated research workflow. Produce candidates and proof obligations; never turn a search score, simulator result, or circuit reduction into an advantage claim.

## Run The Workflow

1. Invoke `$frame-quantum-problem`. Freeze the problem family, instance distribution, access model, output contract, accuracy, success probability, and matched classical baselines.
2. Invoke `$select-quantum-primitives`. Match structural bottlenecks to theorem-backed primitives and record every unmet precondition.
3. Invoke `$design-hybrid-quantum-workflow`. Generate classical-only, quantum-only, and hybrid DAGs; charge all boundary and coupling costs.
4. Invoke `$formalize-quantum-algorithm`. Encode surviving candidates in QADL-IR and emit explicit correctness, access, resource, robustness, and advantage obligations.
5. Invoke `$search-quantum-algorithm-space` only after a typed search grammar and deterministic evaluator exist. Preserve seeds, parents, verifier traces, failures, and a Pareto archive.
6. Invoke `$verify-quantum-algorithm`. Move each obligation only as far as its evidence supports: open, tested, proof-sketch, proved, or formally-verified.
7. Invoke `$audit-quantum-advantage`. Compare matched access, output, accuracy, success probability, and full costs against a serious classical portfolio.
8. Loop failed candidates back to the earliest invalid assumption. Do not tune the claim wording around a failed gate.

## Enforce Stage Gates

- Stop primitive selection when the input or output contract is ambiguous.
- Stop search when correctness can only be rewarded by an unvalidated proxy.
- Stop a gate-level claim when oracle construction, state preparation, or readout is unknown.
- Stop an empirical claim when results come only from a statevector simulator.
- Stop an end-to-end claim when compilation, communication, repetitions, optimization, mitigation, cutting, decoding, or classical postprocessing is omitted.
- Keep `source_supported`, `model_inference`, `uncertain`, and `needs_human_check` distinct in every artifact.

## Use The Tools

Run deterministic checks from the plugin root:

```bash
python3 scripts/qad_cli.py validate candidate.qadl.json
python3 scripts/qad_cli.py formalize candidate.qadl.json --out formal-contract.md
python3 scripts/qad_cli.py audit candidate.qadl.json --out advantage-audit.json
```

Use the equivalent `qadl_*` MCP tools when available. Treat a zero exit code as passage of the implemented gate only, not as scientific certification.

## Return A Design Packet

Return, in the user's language:

- frozen problem and baseline contract;
- rejected and surviving primitive/hybrid candidates with reasons;
- QADL-IR candidate files and formal proof scaffolds;
- search configuration, budget, seed, verifier versions, and Pareto archive;
- verification ledger with open obligations;
- advantage-audit verdict and the narrowest defensible claim;
- next experiment or proof needed to advance the claim.

Read [research-basis.md](references/research-basis.md) before selecting formal, resource-estimation, search, or benchmark backends.
