# Verifier-In-The-Loop Search

The verifier loop prevents a proposal engine from becoming its own judge. Generation may be
stochastic; candidate identity, validation rules, evaluation budgets, and promotion gates must be
explicit and reproducible.

## Current Data Flow

```text
finite QADL search space
        |
        v
random / evolutionary / optional proposal backend
        |
        v
materialize genome -> canonical candidate id and provenance
        |
        v
schema + DAG validation -> advantage audit -> declared resource evaluation
        |
        v
hard constraints -> feasible records -> Pareto archive
        |
        v
held-out semantics + independent checks + proof obligations
        |
        v
permitted claim
```

`scripts/qadlib/search.py` computes a candidate ID from the selected JSON Pointer values and adds
the base candidate as a parent. Its search-time evaluator calls `validate_candidate`,
`audit_advantage`, and `analyze_resources`. This is a deterministic structural and declared-cost
loop. It does not execute a quantum circuit or discharge a proof automatically.

Both core archive entries and the SB3 `best_record` are wrapper records. Their QADL document is the
nested `candidate` object. Validate the nested object and retain the wrapper as search provenance.

## Promotion Gates

### Gate 0: Freeze The Contract

Before search, freeze:

- problem family and instance distribution;
- size parameters and promises;
- input representation, access model, and preparation assumptions;
- output representation, accuracy, confidence, and success probability;
- classical baseline contract;
- allowed quantum, classical, hybrid, oracle, measurement, and feedback operations;
- resource model and evaluator budget.

Changing any item creates a new experiment. Do not let search improve its score by weakening the
output contract, changing oracle access, deleting a baseline, or relaxing a promise.

### Gate 1: Parse, Type, And Validate

Require a complete QADL candidate and run:

```bash
python3 scripts/qad_cli.py validate candidate.json --out validation.json
```

Reject candidates with schema errors, invalid resource expressions, broken stage dependencies,
inconsistent contracts, or invalid proof-status transitions. A zero validation-error count means
the artifact is structurally admissible; it does not mean the algorithm is semantically correct.

### Gate 2: Evaluate Declared Resources

Run explicit parameter points:

```bash
python3 scripts/qad_cli.py analyze candidate.json --points train-points.json --out train-resources.json
```

The built-in summaries expose `min`, `max`, `mean`, and `last` for each declared expression. These
values are useful for constraints and ranking, but they merely evaluate the candidate's formulas.
They do not derive the formulas, prove asymptotic bounds, account for omitted costs, or validate a
circuit compiler.

Use correctness as a hard constraint whenever a semantic evaluator exists. Only then optimize
query count, logical qubits, depth, non-Clifford cost, measurements, shots, classical work, data
movement, or wall clock.

### Gate 3: Test Semantics On Held-Out Instances

Separate search instances from held-out instances by seed, structure, and problem size. Include:

- exact state, unitary, channel, distribution, or output-contract checks where tractable;
- adversarial and boundary instances, not only random samples;
- sizes smaller and larger than those used for proposal scoring;
- confidence intervals for sampled outputs and all failed runs;
- negative controls and deliberately invalid candidates to test evaluator sensitivity.

A candidate that succeeds at one fixed qubit count remains a circuit candidate. To support a
uniform algorithm family, instantiate the same size-parameterized QADL construction at multiple
unseen sizes without hand-editing its structure.

### Gate 4: Cross-Check Implementations

For high-value candidates, compile or simulate through an independent implementation when
practical. Qiskit and PennyLane are suitable primary adapters; Cirq or tket can provide another
cross-check. Compare global phase, register ordering, endianness, measurement semantics, noise
assumptions, precision, and compiler optimization settings.

For fixed-size synthesis, require equivalence to the target operation or the exact task-level
contract. Passing equivalence establishes an implementation fact at that size, not a scalable
algorithm or speedup.

### Gate 5: Discharge Formal And Complexity Obligations

Render the candidate's obligations:

```bash
python3 scripts/qad_cli.py formalize candidate.json --out obligations.md
```

The rendered Z-style and quantum-Hoare document is an obligation report. The current tool does not
machine-check it. Close correctness, termination, error, and resource obligations with explicit
proofs, verified reductions, trusted theorem-prover artifacts, or clearly scoped proof sketches.

Derive resource recurrences from the uniform construction and include oracle construction, state
preparation, amplification, precision, shots, readout, verification, classical optimization, and
data movement. A log-log fit or reward trend across small sizes is empirical evidence, not a
complexity proof.

### Gate 6: Audit Any Advantage Claim

Run:

```bash
python3 scripts/qad_cli.py audit candidate.json --out advantage-audit.json
```

Require matched access, output, accuracy, confidence, and total cost. Search-time
`claim_blockers == 0` only means the declared artifact passed the current audit rules. It does not
replace source review, formal lower or upper bounds, hardware evidence, or a best-known classical
baseline analysis.

## Search-Time Metrics

The current evaluator records:

| Metric | Meaning | Non-meaning |
|---|---|---|
| `validation_errors` | Count of structural validation errors | Semantic error probability |
| `validation_warnings` | Count of structural warnings | Confidence interval |
| `claim_blockers` | Count of audit blockers | Proof that no hidden assumption remains |
| `claim_warnings` | Count of audit warnings | Advantage probability |
| `proof_coverage` | Fraction of obligations marked tested, proof-sketch, proved, or formally-verified | Quality or validity of those artifacts |
| `resource:*:min|max|mean|last` | Numeric summaries at declared parameter points | Derived asymptotic complexity |

Treat `validation_errors == 0` as the normal feasibility floor. If no feasible record exists, the
core search returns one least-violating fallback for diagnosis. Check `feasible` and
`constraint_violations`; do not equate archive membership with acceptance.

## Reward Semantics

`SearchEvaluator.scalar_score` first assigns a large negative value to infeasible records. For a
feasible record it computes a weighted sum, negating metrics that are minimized. This scalar is
used for evolutionary parent selection and by `QuantumDesignEnv`.

The Gym environment:

- represents each action as one `(dimension, value)` assignment plus a stop action;
- exposes `action_masks()` that disables assignments equal to the current value and always enables stop;
- observes normalized genes, validation errors, claim blockers, validation warnings, and proof coverage;
- rewards `clip(current_score - previous_score, -100, 100)`;
- terminates on the stop action and truncates at `max_steps`;
- stores the highest scalar-score record in `best_record`.

`scripts/train_sb3.py` uses `sb3_contrib.MaskablePPO` by default, which consumes that mask. Passing
`--algorithm ppo` selects ordinary Stable-Baselines3 PPO and provides an unmasked control. The mask
only removes current-value no-ops; it does not validate grammar, dependencies, candidate semantics,
or proof obligations.

Consequences:

- weights affect behavior and must be versioned;
- metrics on different scales can dominate the sum;
- clipping erases large score differences;
- proof-coverage status can be gamed if artifact quality is not checked independently;
- the best RL record may be dominated under the original multi-objective view;
- MaskablePPO or PPO return is not candidate correctness, and reward is not proof.

Prefer hard semantic constraints plus a Pareto archive. Use scalar rewards only for proposal
guidance. After RL training, recompute every retained candidate with the standalone evaluator and
apply all promotion gates.

## Train, Holdout, And Certification Splits

Use three named splits:

| Split | Purpose | May influence search? |
|---|---|---|
| `train` | Cheap small-size and sampled feedback | Yes |
| `holdout` | Select among search runs and detect overfitting | No direct proposal updates |
| `certification` | Final independent semantic, resource, and claim checks | No |

If holdout results are repeatedly used to modify the representation or reward, they have become
training data. Create a new untouched certification set. Record generator versions and exact seeds
for all stochastic instances.

## Content-Addressed Experiment Record

Archive at least:

```yaml
experiment_id: string
search_space_hash: string
candidate_id: string
canonical_candidate_hash: string
parent_ids: []
proposal_backend: random|evolutionary|sb3_ppo|maskable_ppo|openevolve|pyribs|rllib|other
backend_version: string
evaluator_version: string
seed: integer
budget_requested: integer
budget_effective: integer
evaluation_count: integer
train_split_hash: string
holdout_split_hash: string
metrics: {}
constraint_violations: []
feasible: boolean
artifacts: []
open_proof_obligations: []
permitted_label: candidate|empirically_validated|symbolically_checked|complexity_derived|advantage_supported
```

Keep this record outside QADL if a field is not allowed by the current schema. Do not smuggle
backend-specific metadata into semantic algorithm fields.

## Minimum Comparative Experiment

For a new backend, run:

1. At least one exact-enumeration result when the search space is small enough.
2. Seeded random and built-in evolutionary baselines.
3. The proposed backend with the same effective evaluator budget.
4. Multiple seeds with confidence intervals or the full distribution of outcomes.
5. A holdout evaluation on unseen seeds, structures, and sizes.
6. Wall-clock, evaluator calls, failures, duplicates, and infeasible rates.
7. Ablations for shaped reward, macros or gadgets, and continuous inner optimization.

Benchmark rediscovery may include QFT, Deutsch-Jozsa, Grover, and Simon families. Also include a
QEC encoder task, a hybrid variational task, a fixed-target circuit-synthesis task, and a negative
control with no established quantum speedup. Report circuit-synthesis results separately from
algorithm-family results.

## Permitted Labels

- `candidate`: emitted and structurally recorded.
- `empirically_validated`: passed declared semantic tests on untouched instances with uncertainty reported.
- `symbolically_checked`: relevant symbolic or equivalence obligations were checked by a named method.
- `complexity_derived`: a uniform construction and complete cost model support the stated bound.
- `advantage_supported`: the separate advantage audit passed at a stated evidence level and scope.

Labels are cumulative only when all lower gates remain satisfied. A better reward, a larger Pareto
archive, or a successful fixed-size simulation never promotes a candidate by itself.
