# QADL-IR And Formal Backend Guide

## Contents

1. QADL-IR contract
2. Resource semantics
3. Backend selection
4. Handoff contract
5. Local CLI and MCP surface
6. Evidence basis

## 1. QADL-IR Contract

QADL-IR 0.1 is this project's JSON intermediate representation for a parameterized algorithm
family. Its schema is `assets/schemas/qadl.schema.json`. It makes assumptions and proof debt
machine-readable; it does not supply quantum denotational semantics or discharge a theorem.

| QADL area | Required meaning | Frequent mistake |
| --- | --- | --- |
| `problem` | Same task, distribution, parameters, promises, access, output, accuracy, and success used throughout | Hiding QRAM, state preparation, or a weaker quantum output |
| `algorithm.stages` | Acyclic classical/quantum/measurement/control/I/O composition with local contracts | Treating prose or a flat QASM listing as an algorithm family |
| `resources` | Expressions under one declared fidelity model plus error and modeling assumptions | Mixing query counts, logical gates, and physical runtime in one number |
| `proof_obligations` | Atomic claims with honest status, method, and artifacts | Calling a generated scaffold or simulator run a proof |
| `claim` | Narrow comparison scope and matched baseline | Promoting query advantage to end-to-end advantage |
| `provenance` | Sources, generator, timestamp, seed, and ancestry | Losing the origin of generated candidates |

The renderer produces a Z-style classical problem schema, stage Hoare-shaped obligations,
resource recurrences, and a backend handoff. The generated document states that it is not
machine checked. Preserve that statement.

Z notation is useful for sets, relations, state invariants, and classical interfaces. It does not
natively provide density-operator semantics, measurement semantics, linear quantum data use, or a
proof of quantum-program correctness. Do not use a Z schema as the sole quantum proof artifact.

## 2. Resource Semantics

Every resource result needs a cost model and a parameterized family.

| Metric | Required declaration |
| --- | --- |
| Query | Named oracle, access contract, controlled/inverse calls, success amplification, and whether oracle construction is excluded |
| Gate count | Gate basis, decomposition level, rotation-synthesis tolerance, and whether routing is included |
| Depth | Parallelism, dependency and measurement-feedforward rules, connectivity, and scheduling policy |
| Width | Peak live data plus ancillas; distinguish logical and physical qubits |
| Ancilla | Clean, dirty, borrowed, returned-state requirement, and peak liveness |
| Precision | `epsilon`, confidence or `delta`, synthesis/model/discretization error allocation, and failure probability |
| Expected cost | Stopping rule, branch probabilities, restart policy, tail or worst-case bound |
| End-to-end | Input build, state preparation, compilation, calls/shots, readout, classical work, verification, and amortization |

Never infer asymptotic complexity from a finite list of compiled circuits. A fit or sampled
expression can find inconsistencies, but an asymptotic claim needs a theorem, recurrence proof, or
sound type/effect derivation under stated assumptions.

## 3. Backend Selection

| Backend | Use it for | It does not establish | Engineering status |
| --- | --- | --- | --- |
| Z-style schema | Classical input/output/state interface and invariant vocabulary | Quantum semantics, no-cloning, amplitudes, measurement correctness, or complexity | Local renderer emits a review scaffold only |
| Qbricks / Why3 | Parametric circuit-building programs; functional I/O contracts; symbolic `width`, `size`, and `ancillas` obligations using path sums and SMT-assisted Why3 proofs | Arbitrary hybrid workflows, all noise models, or every depth/precision metric | External tool; create a separate WhyML proof artifact |
| SQIR / VOQC / Coq | Matrix/density semantics, algorithm correctness, circuit equivalence, and correctness of verified optimization/mapping passes | Automatic discovery of invariants or an end-to-end speedup theorem | External Coq development; preserve source and compiled proof logs |
| QWIRE / Coq | Linear wire typing, superoperator denotation, circuit well-formedness, and selected circuit proofs | General classical control, automatic large-scale proof, or physical cost | External Coq development |
| qRHL / qrhl-tool | Relations between two interactive quantum programs, equivalence-style and quantum/post-quantum security arguments | Single-program gate optimization or general physical resource estimation | External Isabelle-backed interactive prover |
| Quantum Hoare logic | Partial/total correctness, weakest preconditions, and quantitative predicates at the semantic level | Automatic proof by itself | Theory; choose a mechanized implementation before claiming formal verification |
| qmd-prover | Protect QADL obligation statements, build citation-derived dependency graphs, run mechanical checks, and optionally obtain independent AI review | Formal verification, proof-assistant certificates, asymptotic derivation, or automatic QADL status promotion | Implemented review handoff; imported QADL contract remains an explicit assumption |
| Silq | High-level typing and safe automatic uncomputation in its supported language | User postconditions, asymptotic bounds, or general theorem proving | Type checker/interpreter; SilVer is a separate SMT prototype |
| Proto-Quipper-R / QuRA | Type/effect-derived symbolic upper bounds for width, gate/T count, depth/T-depth, qubits, and bits | Functional correctness of the quantum algorithm or physical FT cost | External active tool; emit its solver trace and source |
| Qualtran | Composable algorithm blocks, call graphs, architecture-independent resource tables, simulations, and downstream cost models | Machine-checked functional correctness or a complexity lower bound | Experimental resource-analysis library |
| Q# / QDK | Executable high-level hybrid programs, simulation, compilation, and input to resource estimation | A proof that the algorithm meets its mathematical postcondition | Execution and estimation frontend |
| Microsoft QRE | Concrete logical tracing and conditional physical qubit/runtime estimates under hardware, QEC, factory, and error-budget models | Parametric asymptotic proof or quantum advantage | Estimator; store every model input and version |
| OpenQASM 3 | Typed imperative low-level circuits with measurement and classical control | Algorithm-family proof, source-level contract, or certified optimization | Interchange/execution artifact |
| QIR | LLVM-based language/backend interoperability and target profiles | Source correctness, mathematical semantics proof, or resource theorem | Low-level interchange artifact |

Backend choice is compositional. A useful path is:

```text
QADL contract
  -> Qbricks or SQIR proof artifact
  -> verified or explicitly unverified lowering boundary
  -> OpenQASM/QIR executable artifact
  -> Qualtran/QuRA logical report or QRE physical estimate
```

Do not claim end-to-end verification unless every arrow is covered by a proof, a validated
translation, or an explicitly scoped trusted assumption.

## 4. Handoff Contract

Use one record per obligation/backend run:

```yaml
obligation_id: po-resource
backend: qbricks|sqir-voqc|qwire|qrhl|qura|qualtran|qre|other
backend_version: string
input_artifact: path-or-url
input_sha256: string
command: string
assumptions: []
result: pass|fail|inconclusive|not-run
evidence_kind: machine_proof|solver_derivation|test|logical_estimate|physical_projection
output_artifacts: []
provenance_status: source_supported|model_inference|uncertain|needs_human_check
notes: string
```

Only `machine_proof` with a successful trusted checker can justify updating an implementation
obligation to `formally-verified`. A successful SMT query may support that status only when it is
part of a sound proof-producing or deductive-verification chain and the generated obligations,
solver result, and trusted boundary are retained.

## 5. Local CLI And MCP Surface

Run commands from the plugin root.

| Intent | CLI | MCP tool | Boundary |
| --- | --- | --- | --- |
| Validate | `python3 scripts/qad_cli.py validate CANDIDATE` | `qadl_validate_candidate` | Schema, expressions, DAG, cross-field, and proof-artifact presence checks only |
| Render | `python3 scripts/qad_cli.py formalize CANDIDATE` | `qadl_render_formal_contract` | Generates a non-machine-checked document |
| qmd review handoff | `python3 scripts/qad_cli.py export-qmd CANDIDATE --project DIR` | `qadl_render_qmd_handoff` | Protected goals plus optional AI review; always `machine_checked: false` and conditional on the imported QADL contract |
| Sample resources | `python3 scripts/qad_cli.py analyze CANDIDATE --points POINTS` | `qadl_analyze_resources` | Numeric evaluation at explicit points, not asymptotic proof |
| Audit advantage | `python3 scripts/qad_cli.py audit CANDIDATE` | `qadl_audit_advantage` | Evidence gate; never automatic certification |

The plugin currently does not invoke Qbricks, Coq, Isabelle, QuRA, Qualtran, QRE, OpenQASM, or QIR
backends. Treat those as external handoffs until an adapter is implemented and validated. The
qmd-prover exporter is implemented, but qmd-prover's mechanical and independent-AI layers remain
review evidence rather than machine proof.

## 6. Evidence Basis

These are primary papers, official specifications, or original repositories. Capability statements
above are `source_supported`; the recommended composition and handoff schema are
`model_inference` engineering policy.

- Quantum Hoare logic, partial/total correctness and relative completeness (A):
  https://arxiv.org/abs/0906.4586
- Practical quantum Hoare logic with classical variables (B, theory without a production tool):
  https://arxiv.org/abs/2412.09869
- qRHL paper and original tool (A): https://arxiv.org/abs/1802.03188 and
  https://github.com/dominique-unruh/qrhl-tool
- QWIRE Coq embedding and repository (A): https://arxiv.org/abs/1803.00699 and
  https://github.com/inQWIRE/QWIRE
- SQIR/VOQC verified optimizer and repository (A): https://arxiv.org/abs/1912.02250 and
  https://github.com/inQWIRE/SQIR
- Qbricks parametric deductive verification (A): https://arxiv.org/abs/2003.05841 and
  https://github.com/Qbricks/qbricks.github.io
- Silq and SilVer (A for Silq type-safety claim; B for the small SMT prototype):
  https://doi.org/10.1145/3385412.3386007 and https://github.com/marco-lewis/silver
- Proto-Quipper-R/QuRA resource typing (A): https://arxiv.org/abs/2310.19096,
  https://arxiv.org/abs/2408.03121, and https://github.com/andreacolledan/qura
- Qualtran (B; official repository labels it experimental): https://arxiv.org/abs/2409.04643 and
  https://github.com/quantumlib/Qualtran
- OpenQASM 3.1 and QIR 2.1 official specifications (A for interchange capability):
  https://github.com/openqasm/openqasm and https://github.com/qir-alliance/qir-spec
- Microsoft QDK and Resource Estimator (A for documented implementation capability):
  https://github.com/microsoft/qdk and
  https://learn.microsoft.com/en-us/azure/quantum/intro-to-resource-estimation

The exact name `QCVerifier` had no identifiable canonical paper or original repository in exact-name
searches of arXiv, GitHub repositories, Crossref, and DBLP as of 2026-07-18. Treat it as
`uncertain` until a canonical URL or citation is supplied; do not substitute QCEC, SilVer, or another
verifier silently.
