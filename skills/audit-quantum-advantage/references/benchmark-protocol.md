# End-To-End Quantum Benchmark Protocol

## Contents

1. Preregister the comparison
2. Build the classical portfolio
3. Separate execution surfaces
4. Measure the complete cost
5. Normalize success and quality
6. Test statistics and scaling
7. Audit fault-tolerant projections
8. Apply domain-specific checks
9. Enforce acceptance gates
10. Preserve reproducibility artifacts

## 1. Preregister The Comparison

Freeze this contract before running experiments:

```yaml
task: string
instance_distribution: string
size_parameters: []
train_tune_test_split: string
input_access: string
output_contract: string
quality_metric: string
target_quality: string
epsilon: number_or_symbol
confidence: number_or_symbol
success_probability_target: number
resource_budget: string
primary_metric: wall_clock|cost|energy|quality_at_time
secondary_metrics: []
```

Use identical instances and evaluation code. Prevent leakage from test instances into ansatz,
parameter, decomposition, compiler, or baseline tuning. Publish exclusions and failed runs.

## 2. Build The Classical Portfolio

Select baselines by problem structure, not convenience. Include applicable members of:

- best-known exact algorithms;
- approximation algorithms with known guarantees;
- tuned heuristics and metaheuristics;
- decomposition, presolve, and warm-start methods;
- structure-aware simulation or numerical methods;
- quantum-inspired algorithms under comparable data access.

Give all methods comparable engineering and tuning budgets. Record solver version, hardware,
threads, accelerators, memory, precision, stopping rule, tuning trials, and time limit. Do not
compare a production quantum stack with toy classical code.

For optimization, consider [OR-Tools](https://github.com/google/or-tools),
[SCIP](https://github.com/scipopt/scip), and [HiGHS](https://github.com/ERGO-Code/HiGHS).
For PDEs, consider [PETSc](https://github.com/petsc/petsc),
[hypre](https://github.com/hypre-space/hypre), and
[FEniCSx](https://github.com/FEniCS/dolfinx). For quantum-system or circuit simulation,
consider optimized statevector, tensor-network, stabilizer or Pauli, DMRG, selected-CI, and
QMC methods when their assumptions apply.

Follow the equal-effort principles in
[Towards Robust Benchmarking of Quantum Optimization Algorithms](https://arxiv.org/abs/2405.07624).

## 3. Separate Execution Surfaces

Report these surfaces independently:

1. `reference_simulation`: Validate correctness on tractable instances.
2. `noisy_simulation`: Study noise and mitigation, not quantum speedup.
3. `actual_qpu`: Measure current hardware behavior.
4. `logical_projection`: Count executable logical resources.
5. `physical_projection`: Apply QEC and hardware cost models.

Do not mix a measured classical time with an asymptotic quantum query count. Do not plot a
projected QPU time as if it were measured. Attach a provenance label to every data series.

## 4. Measure The Complete Cost

Record both a phase ledger and end-to-end wall clock:

```text
T_pipeline =
  T_formulation
  + T_presolve
  + T_input_build
  + T_state_prep
  + T_compile
  + T_mapping_or_embedding
  + N_calls * (T_reset + T_qpu + T_readout + T_communication)
  + T_optimizer
  + T_mitigation
  + T_cut_reconstruction
  + T_decode
  + T_verify
```

Measure cloud queue delay separately. Include it in user-observed service latency but exclude
it from algorithmic scaling fits. State whether setup and compilation are one-time, per batch,
per instance, or per iteration. Give an explicit amortization horizon.

Record at least:

- circuits, shots, batches, optimizer steps, gradient evaluations, restarts, and failures;
- CPU, GPU, memory, network, QPU active time, and concurrency;
- provider cost and energy when available;
- state-preparation and oracle construction resources;
- logical qubits, Clifford depth, T or Toffoli count and depth, and rotation precision;
- code distance, physical qubits, magic-state factories, cycle time, decoder, and logical failure;
- cut count, fragment count, sampling norm, reconstruction time, and memory;
- embedding time, physical expansion, chain statistics, and repair.

The need to include quantum-classical interaction is source-supported by
[Wack et al.](https://arxiv.org/abs/2110.14108). The exact phase decomposition above is a
`model_inference` protocol checklist.

## 5. Normalize Success And Quality

For independent stochastic runs with per-run success probability `s`, normalize to target
success probability `p_target`:

```text
R = ceil(log(1 - p_target) / log(1 - s))     for 0 < s < 1
R = 1                                        for s = 1
R = infinity                                 for s = 0
TTS = non_amortized_setup + R * per_run_cost
```

For approximate optimization, define success as reaching a preregistered objective threshold
with a feasible solution. Report time to target and quality at fixed time. Do not compare only
the best sample from unequal numbers of attempts.

For expectation estimation, match additive or relative error and confidence. For chemistry,
match basis, active space, observable, and physical accuracy. For PDEs, match the same output
functional. For sampling tasks, define a statistically testable distance or score and include
verification cost.

The TTS normalization and small-size pitfalls follow
[Ronnow et al.](https://arxiv.org/abs/1401.2910).

## 6. Test Statistics And Scaling

Use these defaults unless a preregistered power analysis justifies another design. Label the
defaults `model_inference`:

- Test at least 30 independent instances per size for stochastic claims.
- Test at least five problem sizes.
- Require at least three measured sizes beyond a claimed crossover before fitting post-crossover scaling.
- Use held-out instances for final evaluation.
- Report median, interquartile range, high quantiles, failures, and bootstrap 95% confidence intervals.
- Correct for multiple comparisons when searching many ansatzes, mappings, solvers, or instance subsets.
- Fit plausible competing models and inspect residuals; do not select a scaling law from visual slope alone.
- Propagate uncertainty from success probability, timing, calibration drift, and extrapolated hardware parameters.

Accept a narrow measured speedup only when the confidence interval for the matched end-to-end
ratio excludes one in the claimed direction. Accept a scaling advantage only when the fitted
scaling difference is robust to model choice, instance subsets, tuning, and removal of startup-
dominated points.

Optimize size-dependent runtime parameters for every method. A fixed, overly long annealing
time at small sizes can create a false scaling advantage; see
[Ronnow et al.](https://arxiv.org/abs/1401.2910).

Normalize growing parallel resources. Report single-resource, equal-budget, and best-practical
comparisons when possible. Do not call hardware parallelism a quantum algorithmic speedup.

## 7. Audit Fault-Tolerant Projections

Require an executable logical program and allocate total error across:

- modeling and discretization;
- state preparation and block encoding;
- algorithmic approximation;
- rotation synthesis;
- logical failure;
- sampling and readout.

Sweep at least physical error rate, cycle time, code family and distance, factory count,
decoder assumptions, synthesis precision, and target failure probability. Report logical and
physical qubits, runtime, space-time volume, factory utilization, and sensitivity. Do not use
one optimistic hardware point as evidence of a robust crossover.

Use [Qualtran](https://github.com/quantumlib/Qualtran),
[Microsoft QDK Resource Estimator](https://github.com/microsoft/qsharp),
[pyLIQTR](https://github.com/isi-usc-edu/pyLIQTR),
[Bench-Q](https://github.com/isi-usc-edu/benchq), or
[FTCircuitBench](https://github.com/AdrianHarkness/FTCircuitBench) when their models fit.
Cross-check at least one estimate analytically or with a second tool for high-stakes claims.

Treat all future-hardware conclusions as conditional projections. See
[Beverland et al.](https://arxiv.org/abs/2211.07629).

## 8. Apply Domain-Specific Checks

### QLS And PDE

Report dimension, sparsity, condition number, block normalization, preconditioner build and
application, discretization error, right-hand-side preparation, output observable, and readout.
Do not compare a quantum state or one functional with a full classical vector. See
[Montanaro and Pallister](https://arxiv.org/abs/1512.05903) and
[Childs, Liu, and Ostrander](https://arxiv.org/abs/2002.07868).

### Block Encoding And Oracle Algorithms

Report `(alpha, ancillas, epsilon_BE)`, PREPARE, SELECT, controlled calls, inverses,
reflections, success amplification, reversible arithmetic, and uncomputation. A query advantage
without these costs remains C1. See [Gilyen et al.](https://arxiv.org/abs/1806.01838),
[Clader et al.](https://arxiv.org/abs/2206.03505), and the
[AES oracle resource study](https://arxiv.org/abs/1910.01700).

### Circuit Cutting

Report cuts, fragments, widths, quasiprobability norm, shots, reconstruction, memory, and total
error. Compare with direct execution and the best classical simulation. Qiskit's official
[circuit cutting documentation](https://qiskit.github.io/qiskit-addon-cutting/) states that
shot overhead grows exponentially with the number of cuts.

### Variational Algorithms

Report initialization, ansatz selection budget, optimizer trials, objective evaluations,
measurement groups, shots, gradients, restarts, mitigation, convergence failures, and held-out
performance. Test gradient variance with scale. See the
[VQA review](https://arxiv.org/abs/2012.09265),
[barren plateau result](https://arxiv.org/abs/1803.11173),
[training hardness result](https://arxiv.org/abs/2101.07267), and
[VQE measurement analysis](https://arxiv.org/abs/2012.04001).

### Error Mitigation

Count every additional circuit and sample. Report bias, variance, noise model, calibration,
and failure modes. Do not extrapolate mitigation as constant overhead with depth or size. See
[Takagi et al.](https://arxiv.org/abs/2109.04457) and
[Quek et al.](https://arxiv.org/abs/2210.11505).

### Optimization And Annealing

Report formulation, presolve, embedding, parameter tuning, programming, annealing, readout,
feasibility repair, verification, target quality, and TTS. Give exact, approximate, and heuristic
classical methods equal tuning effort. Use both typical and hard-tail instance statistics.

### Quantum Simulation And Chemistry

Match Hamiltonian, basis, state, time, observable, precision, and confidence. Compare with
statevector, tensor-network, DMRG, selected-CI, stabilizer or Pauli, and QMC methods when
applicable. For LCU or qubitization, include coefficient normalization, PREPARE, SELECT, state
overlap, phase-estimation precision, and fault-tolerant costs.

## 9. Enforce Acceptance Gates

Mark each gate `pass`, `fail`, or `uncertain`:

1. `formal_contract`: Problem, distribution, access, output, accuracy, and success are fixed.
2. `correctness`: Independent reference checks pass at matched tolerance.
3. `baseline`: A credible tuned classical portfolio is present.
4. `access`: State preparation, QRAM, oracles, and block encodings are costed.
5. `full_cost`: No material execution or postprocessing phase is omitted.
6. `statistics`: Instance sampling, uncertainty, failures, and scaling tests are adequate.
7. `fault_tolerance`: Deep coherent algorithms have physical-resource sensitivity analysis.
8. `reproducibility`: Code, data, versions, configurations, seeds, and raw results are available.
9. `claim_wording`: The proposed wording does not exceed the evidence ladder.

Do not approve end-to-end practical advantage unless every gate passes. Report the claim as
`uncertain` when the missing evidence can change the verdict. Report it as `unsupported` when
required evidence is absent and no valid conditional statement remains.

## 10. Preserve Reproducibility Artifacts

Store or cite:

- problem generator and immutable instance set;
- train, tuning, and test split;
- source repository URLs and commit hashes;
- dependency lockfiles and container or environment specification;
- compiler, solver, runtime, backend, and firmware versions;
- hardware topology and calibration snapshot;
- random seeds and parameter search space;
- raw per-run timing, quality, failure, and resource records;
- analysis scripts, fit models, exclusions, and confidence intervals;
- a machine-readable claim and evidence matrix.

Use application-level frameworks such as
[QUARK 3](https://github.com/QUARK-framework/QUARK-framework) when helpful. Use
[QED-C](https://github.com/SRI-International/QC-App-Oriented-Benchmarks),
[MQT Bench](https://github.com/munich-quantum-toolkit/bench),
[QASMBench](https://github.com/pnnl/QASMBench),
[Benchpress](https://github.com/Qiskit/benchpress), and
[SupermarQ](https://github.com/Infleqtion/client-superstaq) only for the layers they actually
measure. A low-level benchmark cannot establish application advantage by itself.
