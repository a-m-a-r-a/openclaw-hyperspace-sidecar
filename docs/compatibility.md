# Compatibility and limitations

- OpenClaw development dependency: **2026.9.6**. The earlier private adapter was
  built with older SDK typings; that is not a promise of backward compatibility.
- Python >=3.11 on POSIX. Windows is not supported by the flock implementation.
- Provider pinned to fork commit `7e59e333622f4e6debe6acb9af44ef5f31f4c3d2`
  (package version 2.8.1). This version number is shared with upstream: use the pin.
- SDK pinned to **3.1.7**. Provider cognitive tests also covered SDK 3.1.3;
  this adapter release targets the pinned SDK, not every advertised MCP version.
- Backend deployment used a reported 3.1.4 build with embeddings. Capabilities
  (Vectorize, GetPoints, verified Lorentz 129D schema) matter more than version labels.
- The bridge retains a process-local GetCollectionStats compatibility shim using
  ListCollections. Only count/schema are substantive; disk/RAM/task fields are
  placeholders, not measured metrics. It does not patch the installed SDK files.
- Earlier GetPoints namespace and missing-embed failures were resolved in the
  deployment before this release. They are troubleshooting history, not a claim
  that every server is affected or a current unresolved blocker.
- Private provider APIs (`_apply_memory_event`, `_call`) require regression tests
  when upgrading. No stability guarantee across unreviewed provider updates.
- Not a Mem0 replacement, not the official 35-tool MCP, not a full graph/admin,
  DePIN, hybrid-search or consolidation interface. Those provider/SDK capabilities
  are not automatically exposed by installing this adapter.
- No hidden reasoning collection, autonomous trust gate, automatic whole-transcript
  ingestion or promise of factual truth. No UI/dashboard integration is included.
- Dependency installation may include development-only transitive audit findings;
  record/review them separately from runtime tests and do not run blind audit fixes.

## CI publication

[CI workflow example](ci-example.yml) is supplied as documentation. This repository
does not currently have an installed Actions workflow: the publishing credential
cannot create workflow files. Local checks are recorded separately; do not infer
green GitHub CI. A maintainer can install the example under `.github/workflows/`
using credentials with the appropriate workflow permission.
