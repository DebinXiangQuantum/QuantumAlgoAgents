# Scientific Claim Policy

This policy governs claims made by the project, its examples, generated design packets, documentation, issues, and pull requests. It exists to prevent a plausible candidate or favorable benchmark from being presented as a theorem or practical advantage.

## Interpretation table

| Tool result | It establishes | It does not establish |
| --- | --- | --- |
| `validate` reports `valid: true` | JSON Schema and implemented cross-field consistency checks passed. | Semantic correctness, theorem validity, or proof-artifact truth. |
| `analyze` reports numeric resources | Declared expressions evaluated at the supplied points. | Asymptotic complexity, scaling law, or physical feasibility. |
| `formalize` emits a document | A reviewable interface, stage contracts, recurrences, and proof obligations. | A machine-checked proof; the MCP result explicitly says `machine_checked: false`. |
| Search emits a feasible Pareto archive | Candidates satisfy declared hard constraints and are nondominated under declared metrics. | Correctness, novelty, generalization, optimality, or advantage. |
| PPO emits a policy or reward | Behavior under the declared finite environment and evaluator. | A theorem, scalable discovery, or scientific certification. |
| `audit` reports no blockers | The implemented evidence gates are satisfied. | Automatic certification, independent replication, or peer review. |

## Claim scopes

Every performance claim must name exactly what is being compared:

- **Query:** number of calls under a stated oracle or access model.
- **Logical circuit:** logical qubits, gates, depth, measurements, and success amplification.
- **Fault tolerant:** physical qubits, code distance, factories, routing, scheduling, and runtime.
- **Kernel wall clock:** execution time of a defined quantum kernel and its immediate control loop.
- **End to end:** input construction, state preparation, oracle/block encoding, quantum work, measurement, readout, classical optimization or decoding, communication, and output reconstruction.

A lower-scope result must not be worded as a higher-scope result. In particular, query advantage is conditional on its oracle and is not an end-to-end speedup.

## Matched-comparison requirements

A quantum/classical comparison must match:

1. instance distribution and problem promise;
2. input access and preprocessing privileges;
3. output contract and representation;
4. accuracy or approximation tolerance;
5. success probability and repetition/amplification policy;
6. resource scope and included costs;
7. hardware, parallelism, memory, and energy assumptions when claimed;
8. the best credible classical baselines available under the same contract.

Unknown costs remain unknown. They may support a conditional research question but are never charged as zero.

## Evidence vocabulary

- `source_supported`: a primary paper, specification, official repository, or official documentation directly supports the statement.
- `model_inference`: the architecture combines supported facts; the inference is labeled and reviewable.
- `uncertain`: available evidence is insufficient or does not generalize beyond a narrow experiment.
- `needs_human_check`: a proof, implementation, translation, or empirical record requires expert review.
- `refuted`: a counterexample or failed obligation invalidates the claim in its current form.

Every nontrivial scientific statement should link to a primary or official source. Secondary sources may orient a reader but cannot be the only support for a claim.

## Proof-status rules

- `open`: the obligation is specified but not discharged.
- `tested`: tests cover declared instances; no universal conclusion follows.
- `proof-sketch`: a reviewable argument exists but is not complete or mechanized.
- `proved`: a complete proof artifact is identified and has passed the project's stated review.
- `formally-verified`: a machine-checkable artifact is identified, its backend and assumptions are recorded, and the artifact has been checked.
- `refuted`: a counterexample or contradiction is recorded; dependent claims must stop.

The local validator checks that higher statuses name artifacts. It does not inspect or certify their mathematical content. Maintainers must never promote an obligation solely because an artifact path exists.

## Empirical evidence

An empirical advantage report must preserve:

- raw measurements and preprocessing steps;
- instance generation and seeds;
- hardware, simulator, compiler, and dependency versions;
- classical and quantum implementation provenance;
- uncertainty intervals and repeated-trial protocol;
- tuning budgets and stopping criteria;
- failures, excluded runs, and negative results;
- sufficient artifacts for independent reproduction.

Simulator output, successful hardware execution, fidelity, qubit count, gate count, or a favorable fitted slope alone does not establish advantage.

## Automated-search policy

Generators and search policies may optimize proposal quality. They must not train against a label that is presented as independent scientific validation when that label is produced by the same unreviewed system. The deterministic validator and claim auditor remain separate from the search policy.

Novelty is not inferred from embedding distance or absence in a small reference set. It requires a documented literature and prior-art review.

## Required review for stronger wording

The phrases `proved speedup`, `formally verified`, `practical quantum advantage`, and equivalent wording require:

1. all matched-comparison requirements above;
2. explicit proof or experiment artifacts;
3. a reviewer independent of the candidate generator;
4. no unresolved blocker in the relevant claim scope;
5. a public record of assumptions and limitations.

Automated tools may at most return `eligible_for_expert_review`. The final scientific conclusion belongs to accountable human reviewers and, for publication claims, normal peer review.
