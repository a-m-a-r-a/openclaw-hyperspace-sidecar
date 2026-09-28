# Architecture and contracts

## Responsibilities

| Layer | Owns | Does not own |
| --- | --- | --- |
| OpenClaw plugin | Tool schemas, agent/session scoping, optional prompt hook, private secret-file permissions, subprocess timeout | Database ownership rules or embedding model |
| Python bridge | One-request lifecycle, query budget, serialized curated mutation, same-session cognitive retrieval, compatibility probes | Global capability bypass or automatic ingestion |
| Hermes provider | HMAC provenance, owned-only retrieval, ledger, collection contract, capabilities, geometry | OpenClaw hooks or user/session authorization |
| SDK / server | RPC, vectorization, vector storage and search | Factual correctness of recalled text |

Each call starts a new provider with a fresh random session. Search handles are
therefore **not reusable across separate OpenClaw tool calls**. The cognitive tool
accepts exact complete memory contents instead; it reacquires handles with owned
retrieval and computes in the same provider lifecycle. No handle cache, raw IDs,
arbitrary vectors or relaxed ownership checks are introduced.

## Cognitive request

1. Search existing curated memory with `hyperspace_lab_search`.
2. Select complete, non-quarantined contents and put them in meaningful order.
3. Pass them as `memories` to `hyperspace_lab_cognitive`:

```json
{"operation":"analyze_thought_stability","memories":["<exact first memory>","<exact second memory>","<exact third memory>"]}
```

- Stability: 3–16 unique records; geometry: 4–16.
- Momentum and relation: exactly 2; only momentum accepts `steps` in (0,4].
- Each input fits 480 UTF-8 bytes. No truncation of supplied facts.
- Every item must match exactly one complete, non-quarantined result in a bounded
  search (limit 50). Missing, ambiguous or truncated results fail closed.
- Input order is preserved. Search rank and memory timestamp are not automatically
  interpreted as a reasoning trajectory.
- No points are inserted, changed or deleted. Invalid vectors may trigger the
  provider's existing backend re-vectorization of stored content for computation.
- Worst case: up to 16 searches plus geometry/readback in one subprocess. Its
  total timeout can fail before all per-RPC deadlines; no partial success claimed.

A stable-looking path can still contain false claims. The mean log step ratio
can telescope to the first and last step lengths; inspect individual distances.
Gromov delta describes the finite sample under the current metric only.

## Curated writes

`add`: nonempty `content`, optional string metadata including source/provenance.
`replace`: new `content` and exact `oldContent`.
`remove`: empty `content` and exact `oldContent`.

The bridge invokes the provider's private synchronous `_apply_memory_event` under
a cross-process file lock, preserving provider ownership and HMAC checks.
`APPLIED` is returned only after that call completes. `auto_store=False` disables
automatic event mirroring, not these explicit selected writes. A receipt alone
is not an independent readback: verify retrieval when testing deployment.

## Recall and security

Only configured private owner sessions receive prompt recall; reflection jobs can
have explicit tools but no automatic prompt recall. `prefetchDirectOnly` is kept
for compatibility; setting it false **never bypasses the exact allowlist or shared
session exclusion**. Only user-triggered turns use the structured current message.
There is no transcript scraping fallback when the field is unavailable.

Read queries are whitespace-normalized and bounded to 480 UTF-8 bytes. Explicit
search preserves beginning/end; recall preserves the tail. Shortening is reported
because it can lose intent. The hook treats retrieved content as untrusted data.
Hook failures skip recall with a warning, not a claim that no relevant memory exists.

Secrets are loaded from a mode-0600 file and passed to the child environment, not
command arguments. Generic exception class diagnostics avoid echoing backend
payloads. The ledger and HMAC key are private backup material. Filesystem access
by the same OS account is outside this isolation boundary.
