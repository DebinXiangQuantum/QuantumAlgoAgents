# QADL Problem Contract

Use `assets/schemas/qadl.schema.json` as the machine-readable authority. This reference explains the scientific intent behind its `problem` block.

## Minimum Fields

| Field | Question it freezes | Failure prevented |
| --- | --- | --- |
| `family`, `task` | What mathematical object or decision must be produced? | Solving a convenient surrogate |
| `instance_distribution` | Which inputs support the claim? | Moving between average and worst case |
| `size_parameters` | Which independent quantities grow? | Hiding precision, rank, sparsity, or conditioning in `N` |
| `promises` | Which structural assumptions are guaranteed? | Applying a theorem outside its domain |
| `input.representation` | What data or operator is supplied? | Comparing incompatible encodings |
| `input.access_model` | Which queries or coherent operations are available? | Giving the quantum side stronger access |
| `preparation_cost` | How is the input loaded or state prepared? | Free QRAM/state preparation |
| `oracle_construction_cost` | How is the oracle/block encoding built? | Treating a large reversible program as one gate |
| `output.contract` | What constitutes the same answer? | Quantum-state versus full-vector mismatch |
| `accuracy`, `success_probability` | At what quality and confidence? | Comparing unequal target quality |
| `readout_cost` | How is the useful classical result extracted? | Ignoring repetitions or tomography |
| `classical_baselines` | Which matched competitors must be beaten? | Comparing only with brute force or an untuned method |

## Access-Model Rules

- Give the classical baseline the closest meaningful analogue of the quantum access assumption.
- Label black-box query results as conditional on the oracle.
- For sparse access, expose sparsity and the cost of row/value queries.
- For block encodings, expose normalization `alpha`, ancillas, construction error, and PREPARE/SELECT costs.
- For QRAM, expose build, update, coherence, and query costs; search for dequantized algorithms under comparable sample/query access.
- For an input quantum state, state who prepares it and whether preparation is amortized.

## Output-Equivalence Rules

Treat these as different contracts unless a reduction and its cost are explicit:

- full vector versus one expectation or linear functional;
- exact optimum versus approximation ratio or heuristic objective;
- one sample versus a learned distribution;
- quantum state versus classical description;
- noiseless observable versus mitigated finite-shot estimate;
- success on one chosen instance versus an instance distribution.

## Error Ledger

Allocate a total error or failure budget across applicable terms:

```text
epsilon_total >= epsilon_model + epsilon_discretization + epsilon_encoding
              + epsilon_algorithm + epsilon_synthesis + epsilon_hardware
              + epsilon_measurement + epsilon_postprocess
```

Record amplification/repetition costs needed to reach the target success probability. Do not add errors blindly when a theorem requires a different composition rule; create a proof obligation for that composition.

## Baseline Portfolio

Include the strongest applicable categories, not every possible program:

- best-known exact and approximation algorithms;
- randomized and problem-structure-aware methods;
- mature optimization/HPC libraries for the domain;
- tensor-network, Monte Carlo, low-rank, sparse, or preconditioned methods when structure permits;
- quantum-inspired algorithms enabled by the same data-access assumptions.

Attach a primary paper or official repository to each baseline and mark unsupported complexity expressions `needs_human_check`.
