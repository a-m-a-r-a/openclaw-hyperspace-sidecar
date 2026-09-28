# Verification record — 2026-09-29

This is evidence for the initial 0.2.0 source release, not a guarantee for arbitrary
hosts or later dependency versions. No production data or credentials are included.

## Local checks

- TypeScript build: pass, development SDK OpenClaw 2026.9.6.
- TypeScript authorization / tool-schema tests: **4 passed**.
- Python bridge tests: **15 passed** (curated writes, query budget, readback,
  same-session cognitive selection/order, missing/ambiguous matches, backend errors).
- OpenClaw manifest build and validation: pass.
- Provider complete suite with real SDK 3.1.7 installed: **203 passed**. Provider
  unit fixtures still use synthetic/FakeClient data unless explicitly testing SDK
  import; this is not 203 live-backend tests.
- Production-dependency npm audit: 0 findings at the time checked. Full development
  tree had 2 moderate findings; no blind dependency upgrade was applied.

## Live backend via candidate bridge

With the pinned provider and SDK:

- Synthetic curated add -> search -> replace -> search -> remove -> absence: pass.
- Provider read-after-delete verification completed; local canary entries ended in
  replaced/removed states, not active memory.
- Stability, Gromov delta, momentum and relation: all four returned successful scalar
  diagnostics on existing owned records. Input was explicitly ordered.
- A separate cognitive-only before/after check left the collection counter unchanged.
- The backend ListCollections counter did not decrement after the two test inserts
  were deleted. Do not treat that field as a measured count of active retrievable
  memories, and do not claim a counter discrepancy proves failed deletion.

Host activation / subsequent-turn prompt recall are separate from these bridge
checks. Record those in the operator's private deployment log. There is no installed
GitHub Actions workflow for this adapter yet; [the example](ci-example.yml) requires
maintainer installation with workflow permission. Local results are not CI results.
