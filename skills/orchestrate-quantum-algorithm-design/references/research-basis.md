# Research Basis And Architecture Decisions

Evidence snapshot: 2026-07-18. Prefer the linked paper, specification, official documentation, or original repository over summaries.

## Evidence Status

- `source_supported`: the linked primary source directly supports the statement.
- `model_inference`: the plugin architecture combines several supported facts.
- `uncertain`: evidence is insufficient or has not generalized beyond narrow experiments.
- `needs_human_check`: a proof, implementation, or empirical record needs expert review.

## Supported Foundations

| Capability | Primary source | Supported use | Important boundary |
| --- | --- | --- | --- |
| Algorithm-level representation and resources | [Qualtran paper](https://arxiv.org/abs/2409.04643), [official repository](https://github.com/quantumlib/Qualtran) | Compose reusable algorithmic `Bloq`s and estimate symbolic/logical/physical resources | Beta software; resource analysis is not a correctness proof |
| Parametric deductive verification | [Qbricks paper](https://arxiv.org/abs/2003.05841), [official site](https://qbricks.github.io/) | Verify supported circuit-building programs and resource specifications through Why3 obligations | Does not automatically verify arbitrary QADL candidates |
| Mechanized circuit semantics and optimization | [SQIR](https://github.com/inQWIRE/SQIR), [VOQC paper](https://arxiv.org/abs/1912.02250) | Prove circuit transformations in Coq | Circuit correctness is only one layer of algorithm correctness |
| Hardware-facing hybrid circuit IR | [OpenQASM 3 specification](https://openqasm.com/), [official repository](https://github.com/openqasm/openqasm) | Express gates, measurement, timing, and classical feed-forward | Designed as a lower-level compiler/hardware IR, not a complete algorithm theorem language |
| Query-level speedup | [Amplitude amplification](https://arxiv.org/abs/quant-ph/0005055), [quantum Monte Carlo](https://arxiv.org/abs/1504.06987) | Establish conditional query advantages under matched oracle access | Oracle construction, coherent depth, and I/O may erase practical gains |
| Speedup taxonomy and benchmarking | [Rønnow et al.](https://arxiv.org/abs/1401.2910), [Hoefler et al.](https://arxiv.org/abs/2307.00523) | Distinguish provable, strong, potential, and limited speedup; require end-to-end accounting | Small-scale slopes and suboptimal baselines can manufacture apparent speedup |
| Block-encoding and polynomial transforms | [QSVT](https://arxiv.org/abs/1806.01838), [qubitization](https://arxiv.org/abs/1610.06546) | Build linear-algebra and simulation candidates with explicit normalization and precision | PREPARE/SELECT, block-encoding error, state preparation, conditioning, and readout must be charged |
| Hybrid variational methods | [VQA review](https://arxiv.org/abs/2012.09265), [barren plateaus](https://arxiv.org/abs/1803.11173) | Define trainable hybrid templates and experiments | A VQA template has no automatic complexity advantage |
| Circuit cutting | [Qiskit addon cutting](https://qiskit.github.io/qiskit-addon-cutting/), [scalability study](https://arxiv.org/abs/2411.17756) | Extend executable capacity or trade width for sampling/postprocessing | Sampling and reconstruction can grow exponentially; capacity extension is not speedup |
| Automated circuit search | [QCD environment](https://arxiv.org/abs/2401.07054), [official code](https://github.com/philippaltmann/QCD) | Benchmark RL on small directed state-preparation/circuit tasks | Circuit synthesis evidence does not establish discovery of scalable algorithms |

## Architecture Decisions

1. `model_inference`: Keep QADL-IR above circuit IRs. Preserve problem promises, access, output, hybrid stages, resources, claims, provenance, and proof obligations through lowering.
2. `model_inference`: Separate the generator, deterministic validators, empirical evaluators, proof backends, and claim auditor. Do not train the claim auditor as the same policy that generates candidates.
3. `model_inference`: Use a Pareto archive for correctness, resource, robustness, and novelty dimensions. Scalar rewards remain optional policy-training signals, not scientific verdicts.
4. `model_inference`: Start with random/evolutionary and SB3-compatible baselines. Add distributed RL, quality-diversity, MCTS, or program evolution only after evaluator throughput and reward validity are measured.
5. `uncertain`: No general open system currently takes arbitrary problem statements, discovers a scalable quantum algorithm, proves its correctness, and proves an optimal classical lower bound. Treat that full objective as a research program, not a shipped claim.

## Existing Agent Skills Survey

The skills.sh directory contained Qiskit, Cirq, PennyLane, and Stable-Baselines3 skills at review time, but quantum-specific entries had low adoption or mixed provenance. Use them only as optional implementation references after reviewing their source. This plugin keeps its scientific contract independent of those third-party skills and relies on primary project documentation instead.
