# Search Backend Selection

Use this reference to choose a generator or optimizer. The built-in engine is the compatibility
baseline; every optional backend must emit a complete QADL candidate and pass the same evaluator.

## Decision Principles

1. Identify whether the search object is a scalable algorithm family, a hybrid workflow, a
   fixed-size circuit, or continuous parameters.
2. Measure the bottleneck: proposal quality, expensive evaluation, diversity collapse, continuous
   optimization, or distributed throughput.
3. Start with seeded random and evolutionary search. Add one backend at a time and compare it at
   equal candidate-evaluation cost.
4. Keep the evaluator independent from the proposal engine. A backend may propose candidates; it
   may not redefine correctness, hide invalid candidates, or certify its own advantage claim.
5. Pin versions and inspect current licenses before distributing an adapter or vendoring code.

## Supported And Optional Backends

| Backend | Plugin status | Best use | Do not use it to claim |
|---|---|---|---|
| Built-in random | Supported core | Coverage baseline, tiny finite spaces, regression tests | Search intelligence or proof |
| Built-in evolutionary | Supported core | Discrete QADL choices with cheap deterministic evaluation | Global optimality or semantic correctness |
| `sb3-contrib` MaskablePPO | Supported optional search extra; trainer default | Sequential dimension edits while masking current-value no-ops | That grammar-invalid or semantically invalid actions are masked |
| Stable-Baselines3 PPO | Supported optional search extra via `--algorithm ppo` | Unmasked RL control and ablation | Correctness, complexity, or advantage |
| OpenEvolve | Optional adapter | LLM-guided program/DSL evolution with an executable evaluator and sandbox | Determinism, safety, or proof from evaluator score |
| pyribs | Optional adapter | Quality-diversity archives over interpretable structural descriptors | That an archive cell denotes an algorithm family or speedup class |
| Ray RLlib | Optional distributed adapter | Large parallel environment workloads or distributed learners | Better sample efficiency merely from distribution |
| Optuna | Optional inner optimizer | Conditional hyperparameters, pruning, and continuous/discrete tuning | Structural algorithm discovery by itself |
| Nevergrad | Experimental inner optimizer | Noisy derivative-free continuous or mixed parameter tuning | A necessary dependency when Optuna or pyribs already suffices |
| DEAP | Experimental adapter | Custom genetic programming or NSGA-style operators | A low-friction core dependency without a license review |
| MCTS with progressive widening | Experimental adapter | Expensive, branching, sequential construction with useful partial-state bounds | Uniform-family correctness from fixed-size rollouts |
| GFlowNet / torchgfn | Research adapter | Sampling many diverse terminal objects proportional to a positive reward | Calibrated probabilities or quantum advantage without a validated reward model |
| CleanRL | Reference only | Reading compact PPO implementations and reproducing a research baseline | A reusable plugin library abstraction |

### Built-In Engine

`scripts/qadlib/search.py` is the normative implementation. It materializes finite genomes from
JSON Pointer choices, validates each candidate, audits its claim, evaluates declared resource
expressions, applies hard constraints, and returns a nondominated archive. It is deterministic for
a fixed input and seed. It does not compile circuits or prove semantic correctness.

Use the random method as a mandatory control. Use the evolutionary method when neighboring QADL
choices carry useful structure. If evolution does not outperform random over repeated equal-budget
runs, retain random or redesign the representation before adding a larger framework.

### Stable-Baselines3 And MaskablePPO

The shipped `scripts/train_sb3.py` defaults to `sb3_contrib.MaskablePPO("MlpPolicy", env)` and
supports Stable-Baselines3 `PPO("MlpPolicy", env)` through `--algorithm ppo` as an unmasked control.
`scripts/requirements-search.txt` installs Gymnasium, Stable-Baselines3, and `sb3-contrib`. These are
optional search dependencies; the core random and evolutionary search remains usable without them.

The environment observation combines normalized genes with validation errors, claim blockers,
validation warnings, and proof coverage. Its reward is the clipped delta in the evaluator's scalar
score. `QuantumDesignEnv.action_masks()` marks assignments to each dimension's current value as
false and keeps the explicit stop action true.

The trainer writes the entire `best_record` to `--candidate-out`; the QADL candidate is nested at
`candidate`. Preserve the record for provenance, but extract that nested object before invoking a
candidate validator or audit.

This is a baseline for sequential search, not evidence that reinforcement learning is required.
The current mask removes no-op assignments only; all other dimension/value assignments remain
available. It does not enforce a future AST grammar, dependency precondition, or semantic rule.
Extend and test the mask before making such a claim. Keep
[MaskablePPO](https://sb3-contrib.readthedocs.io/en/master/modules/ppo_mask.html), unmasked PPO, and
random/evolutionary controls under the same evaluation budget. Stable-Baselines3 is a modular
PyTorch implementation documented in its
[official repository](https://github.com/DLR-RM/stable-baselines3).

### OpenEvolve

[OpenEvolve](https://github.com/algorithmicsuperintelligence/openevolve) is an open evaluator-driven
program-evolution system with population, island, and MAP-Elites-style mechanisms. It is the
closest open adapter candidate for AlphaEvolve-like mutation of QADL-producing programs.

Use it only when:

- the mutable region is explicit and produces schema-valid QADL;
- generated code runs in a resource-limited sandbox without secrets or network authority;
- evaluator inputs and outputs are deterministic or their uncertainty is recorded;
- prompts, responses, parents, mutations, failures, and exact environment versions are archived.

Do not expose the verifier process itself as mutable code. Google's
[AlphaEvolve description](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/)
is architectural inspiration, not an installable or interchangeable open backend.

### pyribs Quality Diversity

[pyribs](https://github.com/icaros-usc/pyribs) provides archives, emitters, and schedulers for
quality-diversity optimization. Use it when the user needs several structurally different feasible
candidates, not only a single scalar winner or Pareto frontier.

Choose descriptors that are measured directly, such as oracle-query bucket, measurement rounds,
hybrid feedback depth, ancilla count, non-Clifford density, two-qubit-gate density, or motif depth.
Do not label a cell `quantum walk`, `amplitude amplification`, or another semantic family unless an
independent classifier or proof establishes that label. The direct quantum precedent
[QD for variational quantum circuits](https://arxiv.org/abs/2504.08459) and its
[reference implementation](https://github.com/m-zorn/qd4vqc) support QD as a circuit-level search
method; they do not establish general algorithm discovery.

### Ray RLlib

[Ray](https://github.com/ray-project/ray) combines distributed tasks and actors, Tune, and RLlib.
Use RLlib only after profiling shows that local PPO or evaluator throughput is the limiting factor.
For embarrassingly parallel deterministic verification, Ray Core workers may be sufficient without
moving policy training to RLlib.

An RLlib adapter must preserve candidate hashes, seeds, retry counts, duplicate suppression, and
evaluator version across workers. Count retried or failed evaluations in the budget report; do not
silently grant distributed search extra evaluations.

## Research Evidence And Scope

| Evidence | What it supports | Boundary for this plugin |
|---|---|---|
| [Automated quantum algorithm design with a DSL](https://link.springer.com/article/10.1140/epjqt/s40507-026-00472-4), [code](https://github.com/AmyRouillard/qalgosynth) | Scalable motifs and evolutionary mutations can rediscover known algorithms from small training sizes | Treat as a research reference; reproduce with held-out sizes and separate proofs |
| [AlphaTensor-Quantum](https://www.nature.com/articles/s42256-025-01001-1), [code](https://github.com/google-deepmind/alphatensor_quantum) | RL/MCTS and gadgets can optimize Clifford+T synthesis via tensor decomposition | Specialized fixed-size T-count synthesis, not general algorithm discovery |
| [RL discovery of QEC encoders](https://www.nature.com/articles/s41534-024-00920-y), [QDX](https://github.com/jolle-ag/qdx) | Vectorized PPO and verifier-shaped signals can discover useful structured circuits | Domain-specific QEC conditions; reward still requires independent validation |
| [Progressive-widening MCTS for QAS](https://advanced.onlinelibrary.wiley.com/doi/10.1002/qute.202500093), [code](https://github.com/VincenzoLipardi/MCTS-QAS) | MCTS can reduce evaluations for variational circuit architecture search | Fixed-scale PQC design; repository licensing must be verified before reuse |
| [GFlowNet foundations](https://www.jmlr.org/papers/v24/22-0364.html), [torchgfn](https://github.com/GFNOrg/torchgfn) | A framework for sampling diverse compositional objects from positive terminal rewards | No direct general quantum-algorithm-discovery validation; research phase only |
| [Multi-objective evolutionary quantum circuit discovery](https://arxiv.org/abs/1812.04458) | Pareto search can rediscover small known circuits while balancing objectives | Gate-level, fixed-size empirical discovery does not prove scalable complexity |
| [Learning Simon's algorithm](https://arxiv.org/abs/1806.10448) | Trainable quantum models can recover a known query advantage in a controlled setting | A task-specific experiment, not a reusable search engine |
| [RL adiabatic algorithm design](https://arxiv.org/abs/1812.10797) | RL can optimize an adiabatic schedule in specialized models | Schedule search does not generalize automatically to circuit or hybrid algorithms |

## Adjacent Tools

- [Qiskit](https://github.com/Qiskit/qiskit): circuit, operator, transpiler, quantum-information,
  and resource cross-check backend.
- [PennyLane](https://github.com/PennyLaneAI/pennylane): differentiable hybrid evaluation and
  parameter optimization backend.
- [Cirq](https://github.com/quantumlib/Cirq): optional independent simulator and noise-model adapter.
- [tket](https://github.com/Quantinuum/tket): optional compiler and cross-framework compilation check.
- [Quartz](https://github.com/quantum-compiler/quartz): equivalence-class rewrite and circuit-cost
  optimization reference; use for synthesis, not discovery claims.
- [Optuna](https://github.com/optuna/optuna): preferred optional study manager for conditional
  hyperparameters and pruning.
- [Nevergrad](https://github.com/facebookresearch/nevergrad): optional derivative-free optimizer.
- [DEAP](https://github.com/DEAP/deap): flexible genetic programming reference; review LGPL
  obligations before integration.
- [CleanRL](https://github.com/vwxyzjn/cleanrl): readable single-file RL reference, intentionally
  not the plugin's reusable training abstraction.
- [mctx](https://github.com/google-deepmind/mctx): JAX MCTS building blocks for a future specialized
  adapter.

## Backend Acceptance Checklist

A backend is ready for plugin integration only when all answers are yes:

- Does it consume or emit canonical QADL without weakening the problem contract?
- Does it call the same validation, audit, resource, and holdout evaluators as the core methods?
- Can it resume from a content-addressed archive without duplicating hidden evaluations?
- Are seeds, versions, prompts, policies, checkpoints, and candidate lineage recoverable?
- Are timeout, crash, NaN, duplicate, and infeasible-candidate outcomes counted explicitly?
- Does an equal-budget benchmark show a benefit over random and built-in evolution?
- Are sandbox, license, and dependency risks documented?
- Does its report state that score, reward, and Pareto rank are not proofs?
