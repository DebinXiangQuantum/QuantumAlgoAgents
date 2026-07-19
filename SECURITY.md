# Security Policy

## Supported versions

The latest `0.1.x` release receives best-effort security fixes. Earlier research snapshots are unsupported. This policy will be revised when the project reaches a stable public release line.

## Reporting a vulnerability

Do not disclose a suspected vulnerability in a public issue, discussion, pull request, or design artifact.

Use the repository's GitHub private vulnerability reporting channel when it is available. If that channel has not yet been enabled, privately contact a current maintainer through the contact method published on their contributor profile. Include only enough information in an initial message to establish a private channel.

If neither private route is available, do not publish exploit details. Use GitHub's platform abuse/security reporting path to request help reaching the repository owner.

Please include:

- affected version or commit;
- impact and realistic threat model;
- reproduction steps or a minimal proof of concept;
- affected files, tools, or interfaces;
- suggested mitigation, if known;
- whether the issue has been disclosed elsewhere.

Maintainers will acknowledge reports and coordinate validation, remediation, advisory text, and disclosure on a best-effort basis. No response-time service-level agreement is currently promised.

## Security scope

Security-sensitive areas include:

- expression parsing or any path to arbitrary code execution;
- MCP request validation, process boundaries, and denial of service;
- path traversal or unsafe artifact access;
- search-budget bypasses or uncontrolled resource use;
- dependency and workflow supply-chain compromise;
- generated instructions that expose secrets or execute untrusted code;
- malicious proof, model, checkpoint, circuit, or dataset artifacts.

A mistaken complexity estimate or unsupported quantum-advantage claim is normally a scientific-integrity issue rather than a software vulnerability. Report it through the scientific claim issue template unless it also creates a security impact.

## Safe operation

- Treat all candidate JSON, expressions, proof artifacts, checkpoints, and external backend outputs as untrusted.
- Run optional training and third-party quantum tools in isolated environments.
- Never place secrets in QADL, prompts, examples, logs, or committed workflow files.
- Keep GitHub Actions permissions read-only by default and review dependency changes.
- Verify generated code and backend commands before execution.

The project does not claim OpenSSF certification. Its repository controls should be assessed again after publication.
