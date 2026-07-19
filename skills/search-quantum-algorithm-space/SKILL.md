---
name: search-quantum-algorithm-space
description: Search finite, typed QADL design spaces with reproducible random or evolutionary baselines, optional reinforcement-learning or quality-diversity backends, and a verifier-in-the-loop archive. Use when generating, ranking, or comparing quantum or quantum-classical algorithm candidates; defining discrete QADL choices and objectives; running qadl_search_candidates or train_sb3.py; or deciding whether a proposed search backend is appropriate. Do not use a search score as a correctness, complexity, or quantum-advantage proof.
---

# Search Quantum Algorithm Space

Explore algorithm families as formal, size-parameterized QADL candidates. Keep generation,
evaluation, verification, and claim auditing separate so that a useful heuristic cannot be
mistaken for a theorem.

## Operating Rules

- Respond in the user's language unless the user requests another language.
- Read [search-backends.md](references/search-backends.md) before selecting or adding a backend.
- Read [verifier-loop.md](references/verifier-loop.md) before defining objectives, rewards, or acceptance gates.
- Start with the built-in seeded `random` and `evolutionary` methods. Add an optional backend only when its extra complexity addresses a measured limitation.
- Search over typed QADL structure, declared resources, and hybrid partitions. Do not treat an unconstrained gate string as an algorithm specification.
- Distinguish **circuit synthesis** from **algorithm discovery**. Optimizing one fixed-size circuit can improve an implementation, but does not establish a uniform algorithm family or its asymptotic complexity.
- Treat every reward, fitness, Pareto rank, policy value, and sampled success rate as search evidence only. **Reward is not proof.**
- Preserve invalid and negative candidates in experiment records, but never present them as verified archive members.
- Record seeds, budgets, evaluator versions, search-space hashes, candidate lineage, and all train/holdout splits.

## Choose The Search Level

Select the highest-level representation that can express the proposed insight:

| Goal | Search object | Required evidence |
|---|---|---|
| Discover a scalable algorithm | Size-parameterized QADL stages, motifs, loops, oracle calls, measurements, and classical control | Held-out sizes plus open proof obligations for semantics and complexity |
| Design a quantum-classical workflow | QADL stage partition, data movement, feedback, stopping rules, and resource expressions | End-to-end contract and matched classical baseline |
| Refine an implementation | Compiler choices, decompositions, routing, ansatz blocks, or fixed-size circuits | Equivalence or task-level validation at the target size |
| Tune continuous parameters | Angles, schedules, penalties, optimizer settings | Held-out objective and uncertainty report |

If the request asks for a new quantum algorithm but supplies only a target unitary at one qubit
count, state that the current task is circuit synthesis. Promote it to algorithm discovery only
after defining a uniform construction over explicit size parameters.

## Build A Finite QADL Search Space

1. Start from a schema-valid `base_candidate` with a frozen problem contract, access model,
   output contract, classical baseline, algorithm stages, resource expressions, proof obligations,
   claim scope, and provenance.
2. Add one or more `choices`. Each choice contains a JSON Pointer `path` that already exists in
   the base candidate and a finite, non-empty `values` array.
3. Use choices that preserve type and contract meaning. Examples include a primitive, a stage
   decomposition, a resource implementation, a hybrid cut, or an error-allocation policy.
4. Put semantic prerequisites in `evaluation.hard_constraints`. At minimum require
   `validation_errors == 0`; require `claim_blockers == 0` only when the search is explicitly
   optimizing a claim-ready candidate.
5. Define multiple explicit `parameter_points`. Include more than one problem size whenever a
   candidate purports to scale.
6. Keep correctness constraints separate from cost objectives. Optimize resource metrics only
   after feasibility is established.

The built-in evaluator exposes these objective and constraint metrics:

- `validation_errors`, `validation_warnings`
- `claim_blockers`, `claim_warnings`
- `proof_coverage`
- `resource:<resource-name>:min|max|mean|last`

Use `assets/examples/grover-resource-tradeoff.search.json` as the executable format example and
`assets/schemas/search-space.schema.json` as the authoritative search-space schema.

## Run Reproducible Baselines

From the plugin root, run both methods under the same budget and several fixed seeds:

```bash
python3 scripts/qad_cli.py search assets/examples/grover-resource-tradeoff.search.json \
  --method random --budget 64 --seed 11 --out random-seed-11.json

python3 scripts/qad_cli.py search assets/examples/grover-resource-tradeoff.search.json \
  --method evolutionary --budget 64 --population-size 16 --seed 11 \
  --out evolutionary-seed-11.json
```

The effective budget is capped by the Cartesian search-space size. Compare methods using equal
effective evaluation counts, repeated seeds, feasible-candidate rate, hypervolume or objective
vectors, and verifier cost. Do not select a method from its single best run.

The equivalent MCP tool is `qadl_search_candidates` with:

```json
{
  "search_space": {"search_space_version": "0.1"},
  "method": "evolutionary",
  "budget": 64,
  "seed": 11,
  "population_size": 16
}
```

Pass the complete search-space object in `search_space`; the abbreviated object above only shows
the call shape. MCP accepts `random` or `evolutionary`, caps `budget` at 500, and returns the same
search report as the CLI.

## Interpret The Archive

Inspect these report fields before opening a candidate:

- `budget_requested`, `budget_effective`, `evaluated`, and `search_space_size`
- `archive_size` and each record's `candidate_id`, `genome`, and `candidate`
- `metrics`, `constraint_violations`, `feasible`, and `audit_verdict`
- `limitations`

When feasible records exist, `archive` contains the nondominated feasible set. When no candidate
is feasible, the implementation returns one least-violating fallback record so the caller can
diagnose the search space. Therefore, `archive_size > 0` does not imply success; require
`feasible: true` and inspect every constraint violation. Each archive item is a search record;
extract its nested `candidate` object before passing it to QADL candidate commands.

## Close The Verifier Loop

For each retained candidate:

```bash
python3 scripts/qad_cli.py validate candidate.json --out validation.json
python3 scripts/qad_cli.py analyze candidate.json --points held-out-points.json --out resources.json
python3 scripts/qad_cli.py formalize candidate.json --out obligations.md
python3 scripts/qad_cli.py audit candidate.json --out advantage-audit.json
```

Run search-time parameter points and held-out points as separate artifacts. Recompile or simulate
representative instances when semantic correctness is at issue. Cross-check high-value candidates
with an independent compiler or simulator when practical. Keep failed holdout results and reopen
the corresponding proof obligation. Follow the full gate sequence in
[verifier-loop.md](references/verifier-loop.md).

## Use Optional RL Search

The repository includes local MaskablePPO and PPO training over the finite QADL design space.
MaskablePPO is the default:

```bash
python3 -m pip install -r scripts/requirements-search.txt
python3 scripts/train_sb3.py search-space.json --algorithm maskable-ppo \
  --steps 5000 --seed 11 \
  --model-out qadl-ppo --candidate-out qadl-ppo-best.json
```

`QuantumDesignEnv` starts from a genome, changes one dimension/value per action, adds a stop
action, and rewards the clipped change in deterministic scalar score. Its `action_masks()` method
masks assignments that would repeat the current value and always permits stop. The RL path is
optional and should beat equal-budget random and evolutionary baselines before it is retained.

Despite the option name, `--candidate-out` contains the full `best_record`, including score,
metrics, feasibility, and a nested `candidate`. Extract that `candidate` object before calling
`validate`, `analyze`, `formalize`, or `audit`; the full record is not a QADL candidate.

`scripts/requirements-search.txt` includes `sb3-contrib`, and `scripts/train_sb3.py` selects
`sb3_contrib.MaskablePPO` by default. Use `--algorithm ppo` for an unmasked Stable-Baselines3 PPO
control. The current mask removes no-op assignments only; it does not encode future grammar,
dependency, or semantic preconditions. Extend and test `action_masks()` before relying on it for
those constraints.

OpenEvolve, pyribs, and RLlib are optional external adapters, not bundled backends:

- Use OpenEvolve for evaluator-driven program or DSL mutation when candidates can be sandboxed.
- Use pyribs when a structural quality-diversity archive is more valuable than one Pareto frontier.
- Use RLlib only when distributed environment throughput or multi-worker learning is the measured bottleneck.

Document adapter versions, serialization boundaries, evaluator parity, and failure handling. Never
let an optional backend bypass QADL validation, holdout evaluation, or advantage auditing.

## Output Contract

Return these sections in order:

1. `Search objective and level`
2. `Frozen problem and comparison contract`
3. `QADL search-space definition`
4. `Backend choice and rationale`
5. `Budget, seeds, and baselines`
6. `Verifier and holdout protocol`
7. `Feasible Pareto or diversity archive`
8. `Rejected candidates and failure modes`
9. `Open proof obligations`
10. `Permitted conclusion`

Use `candidate`, `empirically_validated`, `symbolically_checked`, `complexity_derived`, and
`advantage_supported` as progressively stronger reporting labels. Apply only the strongest label
whose verifier gate has actually passed. A search run by itself permits only `candidate`.
