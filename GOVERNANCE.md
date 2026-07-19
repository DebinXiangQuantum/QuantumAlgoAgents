# Governance

Quantum Algorithm Designer is maintained as an open research software project. Governance prioritizes scientific traceability, conservative claims, secure execution, and reviewable decisions.

## Roles

- **Contributor:** proposes code, documentation, examples, evidence, reviews, or issue analysis.
- **Reviewer:** reviews changes in an area where they have demonstrated context.
- **Maintainer:** merges changes, manages releases, and keeps project infrastructure healthy.
- **Scientific reviewer:** reviews problem contracts, theorem assumptions, proof status, complexity, baselines, and advantage wording.
- **Security moderator:** receives private reports and coordinates remediation.
- **Community moderator:** applies the code of conduct and protects reporter confidentiality.

One person may hold several roles. Roles are earned through sustained, constructive contributions and sound judgment; they are not granted by automated activity volume.

## Decision process

Routine changes are accepted through reviewed pull requests. Maintainers seek consensus and record material tradeoffs in the issue or pull request. When consensus is not possible, maintainers decide based on project principles and document the reason.

The following changes require at least one maintainer plus a relevant domain review:

- QADL or search-space semantics;
- validation, audit, evidence, or claim-status rules;
- expression execution and other security boundaries;
- public CLI/MCP behavior;
- release, license, governance, or code-of-conduct policy;
- wording that upgrades correctness, complexity, novelty, or advantage status.

Maintainers must recuse themselves from final scientific validation of a candidate they generated when an independent reviewer is available.

## Merge standard

A change may merge when:

- required CI checks pass;
- relevant tests and documentation are updated;
- scientific statements have traceable sources and scope;
- security implications have been considered;
- requested reviews are resolved;
- the contribution is compatible with the project's license.

Maintainers may close changes that repeatedly ignore evidence rules, security boundaries, community standards, or project scope.

## Releases

Public releases use Semantic Versioning and a human-readable changelog. A release must keep the plugin manifest and MCP base version aligned, validate referenced assets, pass the core suite, and record known scientific and operational limitations.

Local Codex cachebuster suffixes are installation metadata and do not define a public release.

## Scientific disputes

Disagreement is resolved by narrowing the exact claim, assumptions, comparison contract, and evidence. Open obligations remain open when evidence is insufficient. A counterexample has priority over a popularity vote. The project may host competing candidate designs when their contracts and evidence states are explicit.

## Role changes and inactivity

Maintainers may invite contributors into review or maintenance roles after a public record of high-quality work. A role may be made inactive after prolonged absence or removed for security, conduct, or trust reasons through a documented maintainer decision, while protecting confidential details where necessary.

The project is published through the [DebinXiangQuantum organization](https://github.com/DebinXiangQuantum). Current maintainer identities and contact methods are taken from the repository's contributor and organization profiles; they are not inferred from commit metadata.
