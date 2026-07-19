# Quantum Primitive Selection Catalog

This is a routing catalog, not a theorem database. Re-open the primary source and verify the exact bound before using it in a claim.

| Primitive family | Bottleneck shape | Required contract | Typical useful output | Costs that must remain visible | Common failure |
| --- | --- | --- | --- | --- | --- |
| Amplitude amplification / Grover search | Coherent predicate with marked fraction | Reversible verifier, state preparation and inverses | Marked item or success event | Oracle construction, reflections, solution fraction, repetitions | Counting an application oracle as one free gate |
| Amplitude estimation / quantum Monte Carlo | Estimate an expectation or probability | Coherent sampler and marking/rotation oracle | Scalar estimate | Coherent depth, precision, confidence, synthesis, FT cost | Comparing query count with classical wall clock |
| Quantum walks | Search, hitting, element distinctness, Markov-chain structure | Efficient prepare/update/check and favorable gap/hitting parameters | Marked state, sample, or decision | Setup, update, check, spectral gap, marked fraction | Omitting walk data-structure costs |
| QFT / phase estimation | Eigenphase or periodic structure | Eigenstate overlap and controlled unitary powers | Phase bits or sampled period evidence | Controlled evolution, precision, success amplification | Assuming eigenstate preparation is free |
| Hamiltonian simulation / qubitization | Simulate local/sparse/LCU Hamiltonian dynamics | Explicit encoding or PREPARE/SELECT implementation | State evolution or observable | Normalization, time, error, oracle calls, logical/physical resources | Treating sparse access as a concrete circuit |
| Block encoding / QSVT | Polynomial transform of singular/eigenvalues | Block encoding with known `alpha`, ancillas and error | Transformed state or observable | Construction, polynomial degree, conditioning, precision, readout | Quoting only the transform theorem |
| Quantum linear systems | Solve for a state proportional to `A^-1 b` | Efficient access, state preparation, bounded conditioning, compatible output | Quantum solution state or few functionals | Sparsity, `kappa`, precision, preconditioning, state prep, tomography/readout | Comparing a scalar quantum output with a full classical vector |
| Quantum signal/mean estimation in hybrid loops | Expensive stochastic inner estimate | Repeatable coherent kernel and small classical output | Gradient, expectation, risk metric | Calls per outer iteration, optimizer/restarts, error allocation | Ignoring outer-loop convergence |
| Variational eigensolver / QAOA-style kernel | Low-depth parameterized experiment | Trainable ansatz, measurable cost, matched solver | Objective/energy and parameters | All shots, grouping, gradients, iterations, restarts, mitigation | Claiming advantage from statevector simulation |
| Adiabatic/annealing kernel | Structured energy landscape or sampling task | Embedding, schedule, fair TTS and output quality | Sample or candidate solution | Programming, embedding, chains, anneal, readout, repetitions, repair | Reporting anneal time alone |

## Primary Anchors

- Amplitude amplification and estimation: [Brassard et al.](https://arxiv.org/abs/quant-ph/0005055)
- Quantum Monte Carlo: [Montanaro](https://arxiv.org/abs/1504.06987)
- Quantum walk search framework: [Szegedy](https://arxiv.org/abs/quant-ph/0401053)
- Phase estimation/period finding foundations: [Kitaev](https://arxiv.org/abs/quant-ph/9511026)
- Qubitization: [Low and Chuang](https://arxiv.org/abs/1610.06546)
- QSVT and block-encoding framework: [Gilyen et al.](https://arxiv.org/abs/1806.01838)
- Precision-improved quantum linear systems: [Childs, Kothari, Somma](https://arxiv.org/abs/1511.02306)
- PDE/output and condition-number caveats: [Montanaro and Pallister](https://arxiv.org/abs/1512.05903)
- Variational-algorithm scope: [Cerezo et al.](https://arxiv.org/abs/2012.09265)
- Speedup taxonomy and annealing pitfalls: [Rønnow et al.](https://arxiv.org/abs/1401.2910)
- Dequantization under strong sample/query access: [Tang](https://arxiv.org/abs/1807.04271)

## Composition Checklist

Before connecting two primitives, require:

1. compatible classical/quantum types at the boundary;
2. a realizable inverse or controlled form when demanded;
3. a composed success and error calculation;
4. no duplicated or omitted preparation/readout cost;
5. a resource recurrence across nesting and repetitions;
6. a correctness obligation for the composition;
7. a baseline allowed the same structural information and access.
