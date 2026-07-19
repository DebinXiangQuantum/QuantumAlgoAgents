# Decomposition And Costing Reference

## Contents

1. Problem contract
2. Workflow decomposition patterns
3. Boundary and encoding rules
4. End-to-end cost ledger
5. Domain-specific obligations
6. Resource and benchmark adapters
7. Evidence register

## 1. Problem Contract

Require the following fields before comparing designs:

```yaml
problem_family: string
instance_distribution: string
size_parameters: []
input_representation: string
input_access: explicit|stream|sample_query|sparse_oracle|qram|quantum_state
output_contract: full_object|sample|expectation|linear_functional|certificate
accuracy:
  metric: string
  epsilon: number_or_symbol
  confidence: number_or_symbol
success_criterion: string
classical_baseline_families: []
hardware_constraints: {}
```

Do not compare workflows with different outputs, accuracy, or success probability.
Treat an efficient oracle, QRAM, or prepared quantum state as an assumption until a
construction and cost are supplied.

## 2. Workflow Decomposition Patterns

| Problem family | Classical shell | Candidate quantum kernel | Necessary condition | Kill condition |
| --- | --- | --- | --- | --- |
| Search and Monte Carlo | Compile model, prepare randomness, aggregate estimate | Grover search, quantum walk, amplitude estimation | Reversible coherent oracle is cheap and output is small | Oracle or loading cost dominates the quadratic query gain |
| Linear systems and PDEs | Discretize, sparsify, precondition, allocate error | QLS, QSVT, observable estimation | Sparsity, condition number, block normalization, and output functional remain controlled | Full solution vector or tomography is required |
| Quantum simulation and chemistry | Select basis or active space, mean-field, low-rank factorization | VQE, QPE, LCU, qubitization, correlated fragment solver | Quantum node treats a classically hard correlated sector and returns few observables | Tensor networks, DMRG, QMC, or another structure-aware classical method remains efficient |
| Discrete optimization | Presolve, decompose, repair, verify | QAOA, annealing, Groverized subproblem | Quantum subproblem is an end-to-end bottleneck at matched target quality | Only brute force is used as baseline or embedding dominates |
| Variational workflow | Initialize, optimize, schedule evaluations | Expectation or gradient estimation | Training and measurement scale acceptably across held-out instances | Barren plateau, excessive restarts, or measurement budget erases utility |
| Circuit cutting | Partition, schedule fragments, reconstruct | Execute fragments on smaller devices | Cut count and quasiprobability norm stay small enough to reduce total failure or runtime | Shots or classical reconstruction grows exponentially with problem size |
| Annealing with minor embedding | Form QUBO, find embedding, set chains, repair | Anneal and sample | Embedding is reusable and chain overhead is controlled | Embedding time, physical-qubit expansion, or chain breaks dominate |

Generate a classical-only candidate first. Add a quantum node only when it targets a
specified bottleneck. Use Amdahl's law as a screening bound, not as proof:

```text
S_total <= 1 / ((1 - f_q) + f_q / S_q + overhead_fraction)
```

Label the numerical use of this bound `model_inference` unless all terms are measured.

## 3. Boundary And Encoding Rules

### Input Access

Record both the mathematical access model and its implementation:

- For arbitrary amplitude preparation, report gate count, depth, active spacetime,
  ancillas, and preparation error. Do not infer `polylog(N)` loading from `log(N)` qubits.
- For QRAM, report build assumptions, lookup depth, width, coherence requirements, and
  whether the same data structure gives a classical sample-query baseline.
- For sparse access, define row, column, value, and sparsity oracles and compile each one.
- For repeated inputs, state the amortization horizon and invalidate it when data changes.

Arbitrary state preparation can achieve logarithmic depth by spending linear spacetime;
do not hide that tradeoff. See [Gui et al.](https://arxiv.org/abs/2303.02131) and
[Clader et al.](https://arxiv.org/abs/2206.03505).

### Oracles

For every oracle, record:

```yaml
semantic_function: string
query_count: string
reversible_construction: string
ancillas_clean_and_dirty: string
gate_count_and_depth: string
uncomputation: string
precision_and_failure: string
```

Never model an application oracle as one unit-cost gate in an end-to-end claim. Full
Grover oracle implementations can materially change width, depth, and cost; see the
[AES and LowMC resource study](https://arxiv.org/abs/1910.01700).

### Block Encodings

Specify every block encoding as `(alpha, a, epsilon_BE)` and include:

- PREPARE and SELECT constructions;
- normalization `alpha` and success amplification;
- ancilla count `a`;
- block-encoding error `epsilon_BE`;
- calls, controlled calls, inverses, and reflections;
- gate synthesis and data-access costs.

QSVT complexity is conditional on access to the block encoding. Dense classical data can
still incur linear T-count or spacetime. See
[Gilyen et al.](https://arxiv.org/abs/1806.01838) and
[Clader et al.](https://arxiv.org/abs/2206.03505).

### Embeddings

Keep these transformations separate:

1. `data_embedding`: classical features to a quantum state;
2. `operator_embedding`: matrix or Hamiltonian to a unitary block;
3. `minor_embedding`: logical QUBO graph to annealer topology;
4. `layout_mapping`: logical qubits and gates to physical connectivity.

For minor embedding, report classical embedding time, success rate, physical qubits per
logical variable, maximum and mean chain length, chain strength search, broken-chain rate,
and repair cost. Use the official [minorminer](https://github.com/dwavesystems/minorminer)
and [dwave-system](https://github.com/dwavesystems/dwave-system) projects when applicable.

### Circuit Cutting

Report cut locations, cut type, fragment count and widths, quasiprobability coefficients,
sampling norm `gamma`, total shots, classical reconstruction time, memory, and error.
For quasiprobability sampling, use the generic scaling

```text
shots = O(gamma^2 * log(1/delta) / epsilon_sampling^2)
```

only when the chosen cutting theorem supports it. Do not assume `gamma` is constant.
Qiskit's official documentation states that shot overhead grows exponentially with the
number of cuts. See [Qiskit addon cutting](https://qiskit.github.io/qiskit-addon-cutting/)
and the [full-stack scalability study](https://arxiv.org/abs/2411.17756).

## 4. End-To-End Cost Ledger

Use this accounting identity as a checklist rather than a universal performance model:

```text
T_total =
  T_formulation
  + T_presolve
  + T_input_build
  + T_state_prep
  + T_compile
  + T_mapping_or_embedding
  + N_calls * (T_reset + T_qpu + T_readout + T_communication)
  + T_optimizer
  + T_cut_reconstruction
  + T_decode
  + T_verify
```

Report provider queue delay separately and also include it in user-observed service latency.
Do not use queue delay in algorithmic scaling fits.

Track at least:

- wall-clock time and QPU active time;
- cloud cost and energy when available;
- circuit count, shots, batches, iterations, gradients, and restarts;
- logical qubits, Clifford count and depth, T or Toffoli count and depth;
- rotation-synthesis precision and allocated error;
- code family, distance, logical failure, physical qubits, factories, cycle time, and decoder;
- input preparation, oracle, readout, reconstruction, and verification costs.

For fault-tolerant projections, sweep physical error, cycle time, code family, factory
allocation, synthesis error, and total failure budget. Reject a conclusion supported by only
one optimistic hardware point.

Use [Qualtran](https://github.com/quantumlib/Qualtran),
[Microsoft QDK Resource Estimator](https://github.com/microsoft/qsharp),
[pyLIQTR](https://github.com/isi-usc-edu/pyLIQTR),
[Bench-Q](https://github.com/isi-usc-edu/benchq), or
[FTCircuitBench](https://github.com/AdrianHarkness/FTCircuitBench) as adapters when their
algorithm and hardware models match the candidate.

## 5. Domain-Specific Obligations

### QLS And PDE

Report matrix dimension, sparsity, condition number, block normalization, discretization
order, mesh or basis size, right-hand-side preparation, preconditioner construction and
application, quantum output, and readout observable. Compare a linear functional with the
same classical linear functional, not with an explicit full-field output.

The relevant speedup can shrink from exponential to polynomial after accuracy is matched;
see [Montanaro and Pallister](https://arxiv.org/abs/1512.05903). High-precision PDE
algorithms still produce a quantum encoding and depend on bounded condition numbers; see
[Childs, Liu, and Ostrander](https://arxiv.org/abs/2002.07868) and the
[high-precision QLS algorithm](https://arxiv.org/abs/1511.02306).

### Variational Algorithms

Use the total evaluation model:

```text
N_circuits =
  restarts * optimizer_steps * evaluations_per_step
  * measurement_groups * gradient_multiplier
```

Multiply by shots and all mitigation factors. Report initialization, optimizer, parameter
transfer, stopping rule, failed runs, and held-out performance. Test gradient variance and
trainability as size increases. See the [VQA review](https://arxiv.org/abs/2012.09265),
[barren plateau result](https://arxiv.org/abs/1803.11173),
[training hardness result](https://arxiv.org/abs/2101.07267), and
[VQE measurement analysis](https://arxiv.org/abs/2012.04001).

Treat error mitigation as a sampling cost. Fundamental limits can force exponential or
superpolynomial samples in relevant regimes; see [Takagi et al.](https://arxiv.org/abs/2109.04457)
and [Quek et al.](https://arxiv.org/abs/2210.11505).

### Simulation And Chemistry

Compare against a portfolio selected by structure: optimized statevector simulation, tensor
networks, stabilizer or Pauli propagation, DMRG or selected-CI methods, and QMC when its
assumptions hold. Match basis, active space, physical observable, and error bar.

For qubitization or LCU, report Hamiltonian representation, coefficient norm, PREPARE,
SELECT, phase estimation or signal-processing precision, and state-overlap amplification.
The optimal query result remains conditional on its oracles; see
[Hamiltonian simulation by qubitization](https://arxiv.org/abs/1610.06546).

### Optimization And Annealing

Use application-specific formulations for every solver. Give classical exact solvers,
approximation algorithms, and tuned heuristics equal tuning budgets. Report target quality,
feasibility, embedding, chain handling, programming, annealing, readout, postprocessing, and
time to target. Follow the primary [robust benchmarking guidelines](https://arxiv.org/abs/2405.07624).

### Search And Monte Carlo

State whether the result is a query advantage or a gate-level advantage. Compile the
coherent sampler or predicate and its inverse. Report variance, target precision, success
amplification, depth, and fault-tolerant costs. The near-quadratic Monte Carlo result is a
query-model result; see [Montanaro](https://arxiv.org/abs/1504.06987).

## 6. Resource And Benchmark Adapters

Use application-level orchestration such as
[QUARK 3](https://github.com/QUARK-framework/QUARK-framework) as an architecture reference.
Use [QED-C application benchmarks](https://github.com/SRI-International/QC-App-Oriented-Benchmarks),
[MQT Bench](https://github.com/munich-quantum-toolkit/bench),
[QASMBench](https://github.com/pnnl/QASMBench),
[Benchpress](https://github.com/Qiskit/benchpress), and
[SupermarQ](https://github.com/Infleqtion/client-superstaq) only for the layers they measure.
Do not infer application advantage from a circuit, compiler, or device benchmark alone.

Select classical baselines by domain, including
[OR-Tools](https://github.com/google/or-tools),
[SCIP](https://github.com/scipopt/scip),
[HiGHS](https://github.com/ERGO-Code/HiGHS),
[PETSc](https://github.com/petsc/petsc),
[FEniCSx](https://github.com/FEniCS/dolfinx),
[qsim](https://github.com/quantumlib/qsim),
[Qiskit Aer](https://github.com/Qiskit/qiskit-aer),
[quimb](https://github.com/jcmgray/quimb), and
[ITensor](https://github.com/ITensor/ITensor).

## 7. Evidence Register

Use these labels exactly:

- `source_supported`: A cited primary source or official project directly supports the statement.
- `model_inference`: The statement is a design inference, extrapolation, heuristic, or protocol default.
- `uncertain`: Evidence is insufficient, conflicting, inaccessible, or sensitive to an unresolved assumption.

Record source fitness separately:

- `A`: peer-reviewed primary evidence or an official maintained repository for a direct capability claim;
- `B`: primary preprint, technical report, or official white paper;
- `C`: secondary material usable only to locate primary evidence.

Grant strong input access to the classical baseline when the quantum algorithm uses it.
Quantum-inspired algorithms can remove an apparent exponential advantage under comparable
sample-query access; see [Tang](https://arxiv.org/abs/1807.04271).

Use [Ronnow et al.](https://arxiv.org/abs/1401.2910) for speedup terminology,
[Hoefler, Haener, and Troyer](https://arxiv.org/abs/2307.00523) for practical I/O and
speedup screening, and [Beverland et al.](https://arxiv.org/abs/2211.07629) for
full-stack fault-tolerant resource estimation. These sources do not prove that a newly
generated workflow has quantum advantage.
