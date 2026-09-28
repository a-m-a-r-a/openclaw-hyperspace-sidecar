# Operations

## Verification checklist

1. Build, unit tests and OpenClaw metadata validation pass.
2. `hyperspace_lab_status` reports `ok`, verified collection contract and
   `readback_available=true`. `write_verification=not_tested` is intentional:
   this status probe never claims an end-to-end write.
3. Add a clearly synthetic uniquely named canary, search it, replace it using exact
   old content, verify the replacement, remove it, and confirm it is absent. Use
   provenance identifying a deployment test. Track cleanup even after an error.
4. Run cognitive on existing owned records in caller order. Confirm scalar output,
   no raw vectors, correct point count and unchanged collection count.
5. Test unauthorized session exclusion with synthetic session contexts/unit tests;
   do not expose real memory to another person to test it.
6. If prefetch is enabled, verify an actual subsequent authorized user turn gets
   recalled evidence. Direct bridge tests do not prove the host hook executed.

Record provider **commit**, SDK version, plugin commit, OpenClaw version, results
and any incomplete verification. Health is not write proof; local tests are not CI.

## Update

Before switching, preserve the installed plugin, Python environment and exact
configuration privately. Take a consistent SQLite backup (SQLite backup API or
quiesce writes); protect the ledger and existing HMAC key. Never commit backups.

Review both changelogs. Install the exact provider pin into the plugin venv,
rebuild the TypeScript bundle and manifest, run tests, then activate through
supported host tooling. Do not widen the owner scope as part of an update.
Keep collection, profileScope, statePath, HMAC key and user identity unchanged.

For migration from the private predecessor, first materialize **all effective
settings**, including values inherited from its source-code defaults, into the
private host configuration. In particular, explicitly set `host`, `collection`,
`statePath` and `rpcTimeout`. Copying only previously authored configuration can
silently select the new localhost endpoint, a different collection or ledger.
Never put deployment-specific values into the public source tree. Compare the
effective old and new configuration before activation; candidate bridge tests
with manually supplemented settings do not verify the host's captured config.

A one-shot bridge imports Python dependencies on every call, so replacing its
provider package takes effect on the next invocation. New tool schemas, TypeScript
code and captured config still need plugin reload / controlled Gateway restart.
Avoid in-place code replacement while bridge calls are in flight; prefer staged
releases or a maintenance window for subsequent upgrades.

## Rollback

Stop/drain plugin work; restore the previous code and Python environment (or
reinstall its recorded pins) plus previous plugin configuration. Reload/restart
and rerun status and a bounded known-memory read. Restoring source alone cannot
roll back a captured host schema.

**Do not blindly restore an old ledger after successful new writes.** That can
separate the local ownership ledger from remote state. This update requires no
collection re-embedding or data rewrite; preserve current data unless a reviewed
migration/reconciliation procedure explicitly calls for restoration.

## Troubleshooting

- `GetPoints` NOT_FOUND while listing succeeds: confirm the key's actual tenant
  and user header. Do not interpret failure as a free point ID or bypass ownership.
- Vectorize UNIMPLEMENTED: server was built without embeddings. Enable/rebuild
  backend embedding support; this adapter cannot supply it.
- Long embedding ShapeError: keep short targeted queries; the byte budget is a
  workaround, not a tokenizer fix.
- Exact cognitive match fails: retrieve complete content; it may be truncated,
  excluded, duplicated or outside the bounded candidate set. Do not guess handles.
- No tools: verify agent ID, exact session allowlist, host tool policy and active
  generation. Empty allowlist deliberately denies all.
- Reload retained-work error: a failed reload is not activation. Use a controlled
  restart according to host policy and verify the resulting generation.
