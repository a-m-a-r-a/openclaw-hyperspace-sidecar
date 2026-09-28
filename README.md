# OpenClaw Hyperspace Sidecar

An **OpenClaw adapter**, not another database or a replacement memory engine.
Connects OpenClaw to the [Hermes HyperspaceDB provider fork](https://github.com/a-m-a-r-a/hermes-hyperspacedb-provider), originally by [antydizajn](https://github.com/antydizajn/hermes-hyperspacedb-provider).

**Why a separate repository?** Provider geometry, ownership and ledger logic belong
in the Python provider. OpenClaw tool registration, session authorization, prompt
hooks, secret loading and process lifecycle belong here. No full Hermes runtime
or official MCP server is required for this adapter.

```text
OpenClaw scoped tools / optional prompt recall
  -> TypeScript plugin -> one-shot Python JSON bridge
  -> pinned Hermes provider -> HyperspaceDB Python SDK -> database
                         -> local SQLite ownership ledger
```

## Start here

- [Install and configure](docs/installation.md)
- [Architecture, trust boundaries and tool contracts](docs/architecture.md)
- [Operations, verification, upgrade and rollback](docs/operations.md)
- [Compatibility and known limitations](docs/compatibility.md)
- [Changelog](CHANGELOG.md)
- [Provider cognitive semantics](https://github.com/a-m-a-r-a/hermes-hyperspacedb-provider/blob/main/docs/cognitive.md)

## What is exposed

| OpenClaw tool | Function |
| --- | --- |
| `hyperspace_lab_status` | Health, collection contract and empty-ID readback probe |
| `hyperspace_lab_search` | Bounded semantic retrieval of owned curated memory |
| `hyperspace_lab_store` | Synchronous `add`, exact-content `replace` / `remove` |
| `hyperspace_lab_cognitive` | Read-only geometry of existing memories in explicit caller order |

The historical `hyperspace-lab-sidecar` plugin ID and `hyperspace_lab_*` names are
retained for compatibility; `lab` does not mean records expire automatically.
Optional automatic recall reads the structured current user message. **No full
conversation ingestion.** Writes are explicitly selected facts, max 480 UTF-8
bytes, with provenance. Recall is evidence, never instructions.

Cognitive includes step-distance trends, finite-sample Gromov delta and existing
momentum/relation summaries. **Not a truth score, Lyapunov exponent, calibrated
confidence or hallucination detector.** It does not capture hidden reasoning.

Default authorization is empty: configure exact private owner session keys before
use. Shared sessions remain excluded. Prefetch is off by default; insecure remote
transport requires explicit opt-in. This package does not grant tools globally.

## Status

Source integration, not an npm release. Requirements pin the provider commit and
SDK; OpenClaw development API is pinned in package.json. See compatibility notes
for the precise tested scope. This adapter uses private provider APIs for curated
writes, so update its pin only after contract tests and a real write/readback cycle.

## Development

```bash
npm ci --ignore-scripts
npm run build
npm test
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s python -p 'test_*.py'
openclaw plugins build --root . --entry ./dist/index.js
openclaw plugins validate --root . --entry ./dist/index.js
```

MIT. Provider and SDK retain their own licenses and attribution. No credentials,
production data, operator configuration or ledger files belong in this repository.
