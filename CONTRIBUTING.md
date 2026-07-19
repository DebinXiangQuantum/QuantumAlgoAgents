# Contributing

Thank you for improving Quantum Algorithm Designer. Contributions are welcome in code, schemas, skills, examples, documentation, experiments, and scientific review.

## Before opening a change

- Search existing issues and pull requests.
- Open a design issue before changing QADL semantics, evidence statuses, claim scopes, public interfaces, or governance.
- Use a security report rather than a public issue for vulnerabilities.
- Use primary papers, specifications, or official repositories for scientific claims.
- Read `docs/SCIENTIFIC_CLAIMS.md`; proposed wording must stay within its evidence boundaries.

## Development setup

Quantum Algorithm Designer requires Python 3.10 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r scripts/requirements-core.txt
python3 -m unittest discover -s tests -v
```

For changes to the learning environment or training script:

```bash
python3 -m pip install -r scripts/requirements-search.txt
python3 scripts/train_sb3.py \
  assets/examples/grover-resource-tradeoff.search.json \
  --algorithm maskable-ppo --steps 64 --seed 11 \
  --model-out /tmp/qadl-ppo-smoke \
  --candidate-out /tmp/qadl-ppo-smoke.json
```

Do not commit virtual environments, model checkpoints, local result files, caches, or `.DS_Store` files.

## Change requirements

### Code and schemas

- Keep deterministic validation and claim gates independent of search policies.
- Treat candidate data as untrusted; never evaluate it through unrestricted Python execution.
- Fail closed when a dependency is required for a validity decision.
- Add or update tests for behavior changes and regressions.
- A QADL contract change requires a versioning and migration decision in `docs/QADL_IR.md`.
- Preserve meaningful errors at the CLI and MCP boundaries.

### Skills

- Make theorem preconditions and rejection criteria explicit.
- Keep a clear boundary between sourced facts, model inference, uncertainty, and human review.
- Do not instruct Codex to promote simulator output, reward, or a proof sketch into a certified claim.
- Prefer references under each skill over duplicating large bodies of background text.

### Scientific evidence

A contribution that asserts correctness, complexity, novelty, or advantage must include:

- the exact claim and scope;
- problem promise, access model, and output contract;
- matched classical baselines;
- assumptions and hidden costs;
- source, proof, or experiment artifacts;
- limitations and known counterevidence;
- enough metadata to reproduce any empirical result.

Negative and refuting results are valid contributions. Mark a refuted claim explicitly and stop dependent claims.

### Brand assets

Edit the SVG sources in `assets/brand/`. Preserve the no-text, flat-color, strong-silhouette design and verify light, dark, and 32 px rendering. Do not add third-party marks or unlicensed assets.

## Pull requests

Keep pull requests focused. Complete the repository pull request template and include:

- a user-visible change summary;
- tests run and their environment;
- documentation and changelog updates when behavior changes;
- scientific sources and claim-scope changes, if any;
- security implications and external trust-boundary changes.

At least one maintainer review is required. Changes to scientific claim gates, schema semantics, security boundaries, or governance also require the relevant domain reviewer described in `GOVERNANCE.md`.

## Versioning

The plugin follows Semantic Versioning for its public behavior. QADL and search-space versions are separate data-contract versions. Codex local-development cachebuster suffixes are not release versions and must not be committed to the public source.

## Licensing contributions

Unless explicitly marked otherwise, contributions intentionally submitted for inclusion are licensed under Apache-2.0 under section 5 of that license. No contributor license agreement is currently required. Contributors must have the right to submit all code, text, data, and assets they provide.

Participation is subject to `CODE_OF_CONDUCT.md`.
