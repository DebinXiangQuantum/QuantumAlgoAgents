# Quantum Algorithm Verification Ladder

## Contents

1. Ladder levels
2. Status mapping
3. Obligation routing
4. Complexity and resource checks
5. Certificate requirements
6. Downgrade rules
7. Primary evidence

## 1. Ladder Levels

Report each obligation at the highest level it independently reaches. Levels are cumulative only
when the translation boundaries between them are covered.

| Level | Name | Required evidence | Permitted conclusion |
| --- | --- | --- | --- |
| V0 | Contract consistency | QADL schema, expressions, unique IDs, acyclic DAG, and cross-field checks pass | The project-local contract is structurally consistent |
| V1 | Executable sanity | Parser/type checker plus independent reference, edge, and negative tests at explicit instances | The tested artifact matches the reference on tested cases |
| V2 | Language safety | Sound type/linearity/uncomputation result for the exact source language and artifact | The covered safety property holds under that language's semantics |
| V3 | Functional correctness | Machine-checked pre/postcondition, denotational equivalence to a specification, or a checked semantic theorem | The algorithm implementation is correct for the proved family and assumptions |
| V4 | Relational or transformation correctness | Machine-checked relation between programs or proof that a compiler/optimizer transformation preserves semantics | The two covered programs are related/equivalent as stated |
| V5 | Symbolic resource bound | Sound parametric derivation for named query, gate, depth, width, ancilla, or precision metrics | The stated upper/equality bound holds under the declared cost model |
| V6 | Logical/physical estimate | Reproducible logical decomposition or FT estimate with complete hardware/QEC/error inputs | The artifact has the reported conditional estimate, not a complexity theorem |
| V7 | Matched advantage theorem/audit | Correctness plus matched access/output/baseline, appropriate upper/lower bounds, and evidence gates | Only the narrowly audited query, resource, or end-to-end claim is supported |

The ladder is a `model_inference` engineering policy. Individual backend capabilities are
`source_supported` by the primary sources in section 7.

V6 does not supersede V5: a concrete physical estimate can exist without a symbolic bound. V3 does
not imply V5: functional correctness does not count gates. V5 does not imply V3: a precisely
counted wrong program is still wrong.

## 2. Status Mapping

Use QADL statuses with these meanings:

| QADL status | Minimum evidence | Forbidden use |
| --- | --- | --- |
| `open` | Obligation is stated but unresolved | Do not imply evidence exists |
| `tested` | V1 evidence with commands, inputs, and outputs | Do not call it a proof |
| `proof-sketch` | Reviewable argument with explicit gaps and assumptions | Do not call it proved |
| `proved` | A complete mathematical theorem or derivation applies to the stated abstract obligation and has a retained source/artifact | Do not assume the current implementation corresponds to it |
| `formally-verified` | A trusted checker accepts a machine-readable proof for the exact artifact/obligation, with retained logs and versions | Do not assign from QADL validation, document rendering, sampling, or a bare SMT `sat/unsat` result |
| `refuted` | A valid counterexample or contradiction reaches the obligation's contract | Stop or revise dependent claims |

`qadl_validate_candidate` requires an artifact string for `proved` and `formally-verified`, but it
does not open, authenticate, or check that artifact. Human/backend verification remains mandatory.

## 3. Obligation Routing

| Obligation | Preferred evidence/backend | Key limitation |
| --- | --- | --- |
| Classical interface invariant | Z-style schema plus an actual Z/Why3/Coq proof when needed | The local Z-style renderer is only notation |
| Partial/total quantum correctness | Quantum Hoare logic implementation or Qbricks/Why3 | A logic paper alone does not check the candidate |
| Parametric circuit I/O correctness | Qbricks/Why3 path-sum contracts | Coverage is language and gate-fragment dependent |
| Matrix/density semantics | SQIR/Coq or QWIRE/Coq | Proof engineering is interactive and translation must be justified |
| Optimizer/compiler preservation | VOQC/SQIR/Coq | Only the verified passes and supported IR are covered |
| Two-program relation/security | qRHL/qrhl-tool | Not a general resource estimator |
| High-level no-cloning/uncomputation safety | Silq type system | Does not prove an arbitrary user postcondition |
| SMT behavior for supported Silq fragment | SilVer | Prototype depends on a Silq fork and its QRAM-style abstraction |
| Parametric width/gate/depth bound | Qbricks or Proto-Quipper-R/QuRA | Does not prove general algorithmic functional correctness |
| Algorithm call graph/resource table | Qualtran | Experimental analysis, not machine-checked correctness |
| Concrete FT physical cost | Microsoft QRE | Conditional model estimate, not asymptotic proof or advantage |
| Executable low-level program | OpenQASM/QIR | Representation is not a correctness certificate |

The exact identifier `QCVerifier` is `uncertain` absent a canonical citation or repository. Exact
searches found no canonical record as of 2026-07-18. Ask for the source rather than silently mapping
the name to QCEC, SilVer, SQIR, or another project.

## 4. Complexity And Resource Checks

### Query

- Name every oracle and its access contract.
- Count direct, controlled, inverse, reflection, PREPARE, SELECT, and amplification calls as the
  model requires.
- Separate query upper bounds from oracle construction and implementation cost.
- Require a matched classical lower bound before using `provable` query-speedup wording.

### Gates And Depth

- Fix the logical gate basis and rotation-synthesis tolerance.
- State whether routing, swaps, feed-forward, reset, and measurements are included.
- For depth, state the dependency, connectivity, parallelism, and scheduling model.
- Track T/Toffoli count and depth separately when fault tolerance is relevant.

### Width And Ancillas

- Report peak live logical qubits, not only input-register size.
- Separate data, clean ancilla, dirty ancilla, borrowed workspace, measurement bits, and physical
  qubits.
- State whether ancillas are returned to their required state.

### Precision And Failure

- Declare modeling/discretization, block-encoding, arithmetic, synthesis, phase-estimation,
  sampling, and logical-failure budgets when present.
- State additive versus relative error and confidence/success target.
- Include repetitions, restarts, and expected-versus-worst-case stopping rules.
- Prove or justify error composition; do not merely list budgets.

### Evidence Separation

| Result | Classify as |
| --- | --- |
| `qadl_analyze_resources` values at points | Numeric consistency check |
| Regression/fitted scaling from circuits | Empirical model inference |
| Qbricks/QuRA parametric derivation | Symbolic bound under backend assumptions |
| Qualtran call graph/count | Compositional logical estimate unless separately proved |
| QRE qubits/runtime | Conditional physical projection |
| OpenQASM/QIR instruction count | Count for that lowered artifact and basis only |

## 5. Certificate Requirements

Retain this record for every external run:

```yaml
obligation_id: string
candidate_id: string
candidate_sha256: string
backend: string
backend_version: string
source_artifact: string
source_sha256: string
command: string
environment_or_container: string
assumptions: []
trusted_boundaries: []
result: pass|fail|inconclusive
evidence_kind: machine_proof|solver_derivation|test|logical_estimate|physical_projection
output_artifacts: []
timestamp: RFC3339
```

For probabilistic or hardware evidence, also retain seeds, shots, backend/calibration identifiers,
raw per-run results, error bars, and failures. For physical projections, retain hardware, QEC,
factory, decoder, synthesis, and error-budget configurations.

A proof of source-level correctness plus an unverified compiler gives source-level V3 and an open
implementation-correspondence obligation. It does not give end-to-end V3 for the executable.

## 6. Downgrade Rules

- QADL validation or rendered Markdown only: cap at V0.
- Simulator/reference tests only: cap at V1.
- Type safety only: cap at V2 for that safety property.
- Paper theorem with mismatched promises, oracle, output, or implementation: mark `uncertain` or
  `needs_human_check` for the candidate.
- SMT result without retained obligations and a sound translation: do not use
  `formally-verified`.
- Finite numeric samples or fitted slopes: do not claim V5.
- Logical gate counts without basis/precision: mark the resource result incomplete.
- Physical estimate without complete model inputs or sensitivity: V6 may be `inconclusive` or
  `uncertain`.
- Verified source with unverified lowering: keep the lowering obligation open.
- Refuted premise, invariant, or output contract: refute dependent correctness and advantage
  claims.
- Missing matched classical access/output contract: do not accept V7.

## 7. Primary Evidence

- Quantum Hoare logic: https://arxiv.org/abs/0906.4586
- Quantum relational Hoare logic and tool: https://arxiv.org/abs/1802.03188 and
  https://github.com/dominique-unruh/qrhl-tool
- Complete quantitative qRHL theory: https://arxiv.org/abs/2501.15238
- QWIRE Coq semantics: https://arxiv.org/abs/1803.00699 and
  https://github.com/inQWIRE/QWIRE
- SQIR/VOQC correctness and verified transformations: https://arxiv.org/abs/1912.02250,
  https://arxiv.org/abs/2010.01240, and https://github.com/inQWIRE/SQIR
- Qbricks parametric deductive verification: https://arxiv.org/abs/2003.05841 and
  https://github.com/Qbricks/qbricks.github.io
- Silq and SilVer: https://doi.org/10.1145/3385412.3386007,
  https://arxiv.org/abs/2406.03119, and https://github.com/marco-lewis/silver
- Proto-Quipper-R and QuRA resource analysis: https://arxiv.org/abs/2310.19096,
  https://arxiv.org/abs/2408.03121, and https://github.com/andreacolledan/qura
- Qualtran resource analysis: https://arxiv.org/abs/2409.04643 and
  https://github.com/quantumlib/Qualtran
- OpenQASM and QIR specifications: https://github.com/openqasm/openqasm and
  https://github.com/qir-alliance/qir-spec
- Microsoft QDK Resource Estimator: https://github.com/microsoft/qdk and
  https://learn.microsoft.com/en-us/azure/quantum/intro-to-resource-estimation
