# Changelog

## 0.2.0 — 2026-09-29

First public, configurable source distribution of the previously private adapter.

### Added

- `hyperspace_lab_cognitive`: exact-content retrieval and geometry within one
  provider lifecycle, preserving session-local capabilities and caller order.
- Configurable agent, exact owner sessions, reflection job prefixes, profile scope,
  curator label and explicit insecure-remote opt-in. Default owner scope is empty.
- Pinned provider fork and SDK requirements; no full Hermes install required.
- Installation, architecture, tool contracts, compatibility, verification, update
  and rollback documentation; generic configuration example.
- Cognitive order/read-only, missing/ambiguous-match, invalid-input and backend-error
  tests; authorization boundary tests.

### Changed

- Removed deployment-specific host, identity, filesystem and session constants.
- Bridge fallback diagnostics expose exception class, not backend payload text.
- Target development SDK moved to OpenClaw 2026.9.6.

### Preserved

- Existing plugin/tool IDs; bounded optional recall; owned-only HMAC validation.
- Curated synchronous add/replace/remove, exact old-content checks, write lock.
- 480-byte fact/query budgets, collection stats shim and readback prerequisite probe.

### Migration

Existing installations must explicitly configure their original profile scope,
curator label, owner sessions and transport choice. Preserve collection, ledger,
HMAC key and identity. Defaults are intentionally not a migration of private state.

## 0.1.0 — private predecessor

Three explicit memory tools and opt-in recall. Subsequent private revisions added
curated mutation, structured user-message recall and readback diagnostics. This
entry is historical context, not a separately published or reproducible release.
