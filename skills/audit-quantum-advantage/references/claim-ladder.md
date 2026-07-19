# Quantum Advantage Claim Ladder

## Contents

1. Provenance and source fitness
2. Speedup terminology
3. Evidence ladder
4. Verdicts and permitted wording
5. Mandatory downgrades
6. Counterexamples
7. Primary sources

## 1. Provenance And Source Fitness

Use one provenance label for every material statement:

- `source_supported`: A primary source or official project directly supports the statement.
- `model_inference`: The statement is an extrapolation, synthesis, design choice, heuristic, or protocol default.
- `uncertain`: Evidence is insufficient, conflicting, inaccessible, or depends on an unresolved assumption.

Do not label a statement `source_supported` merely because it has a citation. Verify that the
source contains the claim and that its method fits the claim.

Grade source fitness against the specific statement:

- `A`: peer-reviewed primary theorem or experiment; official maintained repository for a direct capability claim;
- `B`: primary preprint, technical report, official documentation, or official white paper;
- `C`: secondary summary used only to locate primary evidence;
- `unrated`: not yet checked.

Keep provenance separate from verdict. A source-supported statement can still fail to support
the user's broader claim.

## 2. Speedup Terminology

Use the taxonomy from
[Ronnow et al., Defining and detecting quantum speedup](https://arxiv.org/abs/1401.2910):

- `provable quantum speedup`: A proof shows that no classical algorithm can outperform the quantum algorithm under the stated model.
- `strong quantum speedup`: Compare against the best possible classical algorithm, whether or not it is currently known.
- `quantum speedup`: Compare against the best available classical algorithm, with the result contingent on current knowledge.
- `potential quantum speedup`: Compare against a named classical algorithm or finite set of algorithms.
- `limited quantum speedup`: Compare against classical algorithms implementing a corresponding algorithmic approach.

Do not call a comparison with a weak, untuned, or deliberately restricted baseline strong or
provable. Treat `strong quantum speedup` as unestablished unless the best possible classical
performance is justified. Treat future classical algorithm improvements as a standing risk for
best-available and potential speedup claims.

## 3. Evidence Ladder

Use this project ladder to control wording. The ladder is a `model_inference` policy derived
from the source taxonomy; it is not a theorem.

| Rung | Name | Complete requirement | Maximum permitted conclusion |
| --- | --- | --- | --- |
| C0 | Correctness demonstration | Matched reference output on a simulator or quantum device | The implementation reproduces the target result at the tested sizes |
| C1 | Conditional query or primitive advantage | A valid theorem under an explicit oracle, input, and output model | The primitive has the stated query advantage under named assumptions |
| C2 | Logical-resource projection | Executable logical circuit or algorithm with complete gate, depth, width, and error accounting | The design has the reported logical-resource estimate |
| C3 | Physical-resource projection | QEC, physical hardware, synthesis, factory, decoder, and failure models with sensitivity analysis | The design has a conditional physical cost or projected crossover |
| C4 | Limited or potential measured speedup | Matched output and full measured cost against explicitly named comparable baselines | The tested implementation outperforms those named baselines in the measured regime |
| C5 | Best-known empirical speedup | C4 plus a credible, tuned, structure-aware classical portfolio and robust scaling evidence | The tested implementation outperforms the evaluated best-known portfolio under the stated scope |
| C6 | End-to-end practical advantage | Actual quantum execution beats the credible classical portfolio in wall clock, cost, energy, or quality at the same contract, including the complete workflow | End-to-end practical advantage is demonstrated for the stated task, distribution, hardware, and date |

Keep `provable_speedup: true|false|uncertain` separate from C0-C6. Set it to `true` only when
a valid lower bound or equivalent theorem is supplied and its assumptions match the claim.

Do not promote a fault-tolerant estimate beyond C3. Do not promote a simulator beyond C0,
even when the simulated quantum algorithm has a source-supported C1 theorem.

## 4. Verdicts And Permitted Wording

Use these verdicts:

- `supported`: All requirements for the stated narrow claim are met.
- `conditionally_supported`: Evidence supports the claim only under explicit unresolved assumptions.
- `unsupported`: Required evidence is absent or does not establish the claim.
- `contradicted`: Reliable evidence directly conflicts with the claim.
- `uncertain`: Available evidence cannot determine the result.

Prefer precise wording:

| Evidence | Use | Avoid |
| --- | --- | --- |
| Simulator correctness | "The simulated circuit matches the reference on these instances." | "The quantum algorithm is faster." |
| Query theorem | "The method uses fewer oracle queries under access model X." | "The application has end-to-end quantum advantage." |
| Logical estimate | "The circuit requires the estimated logical resources." | "This runs practically on future hardware." |
| Physical projection | "Under hardware model H, the projected cost is X." | "Quantum advantage has been demonstrated." |
| Named-baseline experiment | "It outperforms baselines A and B at matched quality." | "It beats classical computing." |
| C6 evidence | "It demonstrates end-to-end advantage for task T, distribution D, contract O, and hardware H as of date Z." | An unscoped universal claim |

Reserve broad terms such as `quantum advantage`, `exponential speedup`, and `best classical`
for claims whose scope and evidence satisfy their literal meaning.

## 5. Mandatory Downgrades

Apply these rules without exception:

- Missing input-access model: cap at C0.
- Unimplemented oracle or block encoding: cap at C1 and mark the result conditional.
- Statevector, tensor-network, or noisy simulator only: cap at C0 for empirical claims.
- Logical gate counts without QEC: cap at C2.
- Physical-resource estimate without sensitivity analysis: cap at C3 and mark `uncertain`.
- Different output, accuracy, confidence, or success probability: assign `unsupported` to the comparison.
- Brute force as the sole classical baseline when stronger algorithms apply: do not exceed C4.
- Omitted training, shots, mitigation, cutting, embedding, readout, or postprocessing: do not accept end-to-end wording.
- Circuit cutting that only expands executable width: call it capacity extension, not speedup.
- Hardware fidelity or qubit count alone: cap at C0.
- One small problem size or a single favorable instance: do not accept a scaling claim.
- Quantum hardware using growing parallel resources against a fixed single-core baseline: require resource normalization before accepting speedup.

## 6. Counterexamples

Use these as regression cases for the auditor:

1. An HHL implementation cites `polylog(N)` but loads a dense classical vector and reads the full solution. Reject the end-to-end advantage claim.
2. A Grover design counts the predicate as one gate. Accept at most a conditional query claim until the reversible oracle is costed.
3. A cutting workflow runs a circuit wider than the device but incurs exponentially growing shots and reconstruction. Classify it as capacity extension.
4. VQE on a statevector simulator beats an untuned heuristic. Accept correctness only.
5. QAOA beats brute force but is not compared with CP-SAT, branch-and-cut, approximation algorithms, or tuned heuristics. Reject broad classical superiority.
6. A quantum annealer reports anneal time without embedding, programming, readout, chain repair, or parameter search. Reject end-to-end speedup.
7. A PDE algorithm returns one observable but compares with a classical solver producing the complete field. Reject the unmatched comparison.
8. Amplitude estimation counts coherent oracle calls but omits oracle depth and fault tolerance. Accept C1 only.
9. Error mitigation improves fidelity but excludes its additional samples. Reject the resource claim.
10. A simulation compares only against dense statevector evolution while ignoring tensor-network, DMRG, stabilizer, Pauli, or QMC structure. Mark the baseline audit incomplete.
11. A crossover is fitted entirely from startup-dominated sizes or fixed suboptimal annealing times. Reject the scaling claim.
12. A resource estimator uses one optimistic physical error rate and one factory configuration. Treat the projected crossover as `uncertain`.

## 7. Primary Sources

- Speedup definitions and benchmarking pitfalls: [Ronnow et al.](https://arxiv.org/abs/1401.2910)
- Practical I/O and speedup screening: [Hoefler, Haener, and Troyer](https://arxiv.org/abs/2307.00523)
- Full-stack fault-tolerant estimation: [Beverland et al.](https://arxiv.org/abs/2211.07629)
- Quantum-classical communication in system performance: [Wack et al.](https://arxiv.org/abs/2110.14108)
- QSVT and block-encoding assumptions: [Gilyen et al.](https://arxiv.org/abs/1806.01838)
- Concrete dense-data block-encoding resources: [Clader et al.](https://arxiv.org/abs/2206.03505)
- QLS output and precision model: [Childs, Kothari, and Somma](https://arxiv.org/abs/1511.02306)
- PDE end-to-end accuracy caveat: [Montanaro and Pallister](https://arxiv.org/abs/1512.05903)
- Cutting scalability: [Yang and Murali](https://arxiv.org/abs/2411.17756)
- VQE measurement cost: [Gonthier et al.](https://arxiv.org/abs/2012.04001)
- Error-mitigation limits: [Takagi et al.](https://arxiv.org/abs/2109.04457) and [Quek et al.](https://arxiv.org/abs/2210.11505)
- Quantum-inspired dequantization under comparable access: [Tang](https://arxiv.org/abs/1807.04271)

None of these sources proves that a newly generated workflow has quantum advantage.
