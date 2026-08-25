---
name: verify-quantum-algorithm
description: Verify a QADL-IR candidate, quantum algorithm family, hybrid workflow, oracle contract, circuit implementation, compiler transformation, or resource claim using an evidence-graded ladder from schema checks and tests through machine-checked correctness, relational equivalence, symbolic resource bounds, and conditional physical estimates. Use when reviewing correctness, proof status, circuit equivalence, complexity, resources, implementation correspondence, or claimed quantum advantage. This skill distinguishes local validation and numeric checks from external proof-assistant certificates and never upgrades evidence automatically.
---

# Verify Quantum Algorithm

Verify the narrowest falsifiable obligations and report exactly which layer passed. A valid QADL
file, a successful simulation, and a resource estimate are different evidence classes.

## Required Reference

Read [verification-ladder.md](references/verification-ladder.md) before assigning a status or
selecting a backend. For advantage wording, also use the `audit-quantum-advantage` skill and its
claim ladder.

## Operating Rules

- Preserve the problem, access, output, accuracy, success, and baseline contracts during review.
- Treat QADL-IR as a typed contract/IR, not as a proof calculus.
- Never call the rendered formal contract machine checked.
- Never promote `tested` to `proved`, or a logical/physical estimate to a complexity theorem.
- Require an artifact, backend version, command, assumptions, and result before accepting a proof
  or estimate.
- Keep query, logical-circuit, fault-tolerant, and end-to-end conclusions separate.
- Mark each material conclusion `source_supported`, `model_inference`, `uncertain`, or
  `needs_human_check`.

## Verification Workflow

1. Freeze the verification target.
   - Name the candidate version, artifact hashes, exact obligation, parameters, assumptions, and
     acceptance criterion.
   - Split functional correctness, termination, safety, equivalence, resource bounds, access,
     robustness, implementation correspondence, and advantage into separate obligations.

2. Validate the QADL contract.
   - Prefer MCP tool `qadl_validate_candidate`.
   - Otherwise, from the plugin root run:

     ```bash
     python3 scripts/qad_cli.py validate candidate.qadl.json --out validation.json
     ```

   - A pass establishes schema and project cross-field consistency only.
   - Resolve errors before deeper verification; retain `unknown` warnings as open assumptions.

3. Render and inspect proof obligations.
   - Prefer MCP tool `qadl_render_formal_contract`, or run:

     ```bash
     python3 scripts/qad_cli.py formalize candidate.qadl.json --out formal-contract.md
     ```

   - Check that stage contracts compose, loop invariants cover all loops, error budgets sum under
     the stated rule, and every claimed resource has a corresponding obligation.

4. Establish executable sanity evidence.
   - Type-check and parse source artifacts.
   - Compare tractable instances with an independent reference, including edge and failure cases.
   - Use simulation or testing to find counterexamples. Record this layer as `tested`, not proved.
   - A qmd-prover handoff may protect statements, check citation wiring, and obtain independent AI
     review. Record that result as review/test evidence with its assumption footprint; it does not
     reach machine-checked V3.

5. Route formal correctness obligations.
   - Use Qbricks/Why3 for supported parametric circuit-building contracts and symbolic
     width/size/ancilla obligations.
   - Use SQIR/VOQC/Coq for matrix or density semantics, algorithm correctness, and verified
     circuit transformations.
   - Use QWIRE/Coq for linear wire typing and selected superoperator circuit proofs.
   - Use qRHL/qrhl-tool for relational, equivalence-style, and security properties of two programs.
   - Use Silq/SilVer only for the safety or behavioral fragment those tools actually cover.
   - Treat any unverified translation between QADL and a backend as a trusted assumption.
   - Never map qmd-prover `verified` directly to QADL `formally-verified`; require a proof-assistant
     artifact for that status.

6. Verify resource claims at the appropriate level.
   - Prove query bounds from named oracle-call recurrences and amplification/failure assumptions.
   - Prove gate/depth/width/ancilla bounds with a sound symbolic backend such as Qbricks or QuRA
     when its language covers the program.
   - Use Qualtran for compositional resource accounting and Microsoft QRE for conditional logical
     and physical estimates; do not call either a functional proof.
   - Prefer MCP tool `qadl_analyze_resources`, or use the CLI for explicit numeric points only:

     ```bash
     python3 scripts/qad_cli.py analyze candidate.qadl.json \
       --points points.json --out resource-samples.json
     ```

7. Check low-level correspondence.
   - Preserve the high-level obligation IDs and parameters through lowering.
   - Use OpenQASM/QIR as executable interchange artifacts.
   - Require a verified compiler pass, equivalence certificate, or explicit trusted boundary for
     every correctness-preserving lowering claim.

8. Audit any speedup or advantage statement.
   - Prefer MCP tool `qadl_audit_advantage`, or run:

     ```bash
     python3 scripts/qad_cli.py audit candidate.qadl.json --out advantage-audit.json
     ```

   - The audit returns evidence gates and never automatic certification. Run the dedicated
     advantage skill for a full baseline and benchmark review.

9. Reconcile statuses conservatively.
   - Keep the QADL status unchanged unless the exact current obligation is covered by the retained
     artifact.
   - Downgrade stale, mismatched, unverifiable, or assumption-breaking evidence.
   - Mark a counterexample `refuted` and stop dependent claims.

## Output Contract

Return a verification dossier with:

1. Frozen target and assumptions.
2. Obligation matrix with ladder level, backend, result, and provenance status.
3. Validation and test results.
4. Machine-proof or solver artifacts and trusted boundaries.
5. Symbolic resource proof results, separate from logical and physical estimates.
6. Low-level correspondence result.
7. Advantage-audit result when a speedup claim exists.
8. Final verdict: `verified_for_stated_scope`, `partially_verified`, `tested_only`, `refuted`, or
   `inconclusive`.

State the highest completed ladder level and the minimum missing artifact needed for the next
level. Never use the unqualified verdict `verified`.
