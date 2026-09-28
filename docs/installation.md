# Installation

## Prerequisites

- Linux/POSIX (`fcntl.flock` is used for write serialization), Python >=3.11,
  Node compatible with your OpenClaw release, git and npm.
- OpenClaw with `defineToolPlugin`, scoped tool factories and structured
  `before_prompt_build.currentUserMessage`. Development pin: 2026.9.6.
- Reachable HyperspaceDB with embeddings enabled and a **Lorentz 129D** collection.
  A healthy server without working Vectorize/GetPoints is insufficient.
- Private API key and a persistent, independent random ownership-HMAC key.

## 1. Install sources and pinned Python dependencies

```bash
git clone https://github.com/a-m-a-r-a/openclaw-hyperspace-sidecar.git
cd openclaw-hyperspace-sidecar
npm ci --ignore-scripts
npm run build
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
openclaw plugins build --root . --entry ./dist/index.js
openclaw plugins validate --root . --entry ./dist/index.js
```

Use a reviewed commit/tag for production and keep this checkout in a permanent
location. `requirements.txt` pins the cognitive provider fork, not upstream PyPI
with an indistinguishable version number. Do not install the latest provider
blindly. It is packaged as a standalone Python dependency; Hermes Agent need not
be running.

## 2. Create the private secret file

```bash
node scripts/init-secrets.mjs
```

This creates `~/.openclaw/secrets/hyperspace.env` with mode 0600 and a generated
HMAC key. It refuses to overwrite an existing file. Fill the empty API key locally
using a trusted editor or secret-management workflow. Never paste real keys into
OpenClaw config, shell arguments, issues or this repository.

```dotenv
HYPERSPACE_API_KEY=<backend-key>
HYPERSPACE_OWNERSHIP_HMAC_KEY=<persistent-random-secret>
```

Do not regenerate the HMAC key on update: it authenticates existing memory.

## 3. Configure the plugin

Merge [the example](../examples/openclaw-config.json) into existing OpenClaw
configuration using your release's config tooling. Do **not** replace the entire
configuration. Substitute the checkout path, exact owner session key, host and
collection. Paths can be absolute; `~/` is expanded for file paths. Empty
`pythonPath` selects `<plugin-checkout>/.venv/bin/python`.

The example is intentionally inert until `OWNER_SESSION_KEY` is replaced. Get the
exact session key from OpenClaw session diagnostics; do not infer a username or
allowlist all Telegram sessions. Reflection prefixes are optional and must identify
one chosen owner job. Their `:`-delimited child runs are admitted, not arbitrary
prefix matches. Keep the private session list out of public repositories.

`profileScope`, `statePath`, collection and HMAC key form a durable ownership
configuration. Set them once; changing them is a migration, not a cosmetic rename.
`userId` defaults empty. Use only the identity required by your actual backend;
a guessed header can make GetPoints see a different namespace from insertion.

Remote plaintext is disabled by default. If using a trusted, protected private
transport, explicitly opt into `allowInsecureRemote`; the setting is not encryption.
TLS endpoint support follows the pinned provider/SDK; verify your deployment.

## 4. Activate and verify

Build/validate metadata, load the plugin through `plugins.load.paths` (example),
and perform your OpenClaw release's capability review. Permit the four declared
tools only in the authorized agent/session policy. If enabling prompt recall,
allow the plugin's conversation access and prompt injection hooks in host policy
(`hooks.allowConversationAccess` and `hooks.allowPromptInjection` where supported).
Keep all unrelated policy unchanged.

Reload through supported OpenClaw plugin tooling. If retained active work prevents
reload, use a controlled Gateway restart after recording rollback state. A file
copy or successful build alone does not prove activation.

Run the [verification checklist](operations.md). Start with prefetch disabled;
enable it only after curated write/readback succeeds. Automatic recall is proven
on a subsequent user turn, not by a status response.

## Configuration reference

| Key | Default / meaning |
| --- | --- |
| `host` | `127.0.0.1:50051`; provider endpoint |
| `collection` | `openclaw-memory`; verified Lorentz 129D collection |
| `userId` | Empty; optional SDK identity header |
| `secretEnvFile` | `~/.openclaw/secrets/hyperspace.env`; mode 0600 |
| `statePath` | `~/.openclaw/data/hyperspace-sidecar/ledger.sqlite3` |
| `pythonPath` | Empty selects plugin-local `.venv/bin/python` |
| `rpcTimeout` | 120 seconds, range 1–300; process budget adds 15 seconds |
| `prefetchEnabled` | false; automatic recall is opt-in |
| `prefetchRpcTimeout` | 10 seconds, range 1–30; actual hook capped at 15 seconds |
| `prefetchMaxChars` | 3000, range 500–10000 |
| `prefetchTopK` | 5, range 1–20 |
| `prefetchDirectOnly` | true; legacy setting, never disables allowlist checks |
| `maxDistance` | Optional nonnegative retrieval cutoff |
| `agentId` | `main`; one authorized agent |
| `allowedSessionKeys` | Empty; exact private owner sessions |
| `reflectionSessionPrefixes` | Empty; explicit owner job roots and `:` child runs |
| `profileScope` | `openclaw-memory`; persistent ownership namespace |
| `curatorLabel` | `owner`; recorded write provenance |
| `allowInsecureRemote` | false; explicit transport-risk opt-in |
