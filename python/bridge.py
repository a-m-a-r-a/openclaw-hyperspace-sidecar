#!/usr/bin/env python3
"""One-shot JSON bridge from OpenClaw to the audited Hermes HyperspaceDB provider."""

from __future__ import annotations

import json
import io
import os
import sys
import uuid
import fcntl
from contextlib import redirect_stdout
from pathlib import Path

from hermes_hyperspacedb_provider import HyperspaceDBMemoryProvider
from hyperspace import HyperspaceClient
from recall_query import prepare_recall_query


def _collection_stats_from_listing(client: HyperspaceClient, name: str) -> dict:
    """Compatibility path for servers whose GetCollectionStats RPC is broken.

    ListCollections carries the schema and count needed by the provider's
    fail-closed collection contract verification.
    """
    for item in client.list_collections():
        if isinstance(item, dict) and item.get("name") == name:
            return {
                "count": int(item.get("count") or 0),
                "indexing_queue": 0,
                "disk_usage_bytes": 0,
                "ram_usage_bytes": 0,
                "active_tasks": 0,
                "schema": item.get("schema"),
            }
    return {}


def apply_curated_write(provider, args: dict, state_path: Path, curator_label="owner") -> dict:
    action = args.get("operation", "add")
    content = str(args.get("content") or "").strip()
    old = str(args.get("oldContent") or "").strip()
    if action not in {"add", "replace", "remove"}:
        raise ValueError("invalid operation")
    if action != "remove" and (not content or len(content.encode("utf-8")) > 480):
        raise ValueError("one nonempty curated fact must fit 480 UTF-8 bytes; split facts explicitly")
    if action != "add" and not old:
        raise ValueError("replace/remove require exact oldContent")
    metadata = dict(args.get("metadata") or {})
    metadata["curator"] = curator_label
    metadata["adapter"] = "openclaw-owner-curated"
    if old:
        metadata["old_text"] = old
    # Synchronous curated memory-event path: same ownership/HMAC,
    # correction and deletion checks as upstream on_memory_write.
    # No queue acknowledgement masquerading as a completed write.
    with open(str(state_path) + ".write.lock", "a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        provider._apply_memory_event(action, "openclaw-curated", content, metadata)
    return {"ok": True, "state": "APPLIED", "operation": action}


def probe_readback(provider, collection: str) -> dict:
    """Probe the write prerequisite without reading or mutating any point.

    Health/listing success does not prove that GetPoints resolves the same
    authenticated collection. Success here still is NOT an end-to-end write.
    """
    try:
        points = provider._call("get_points", [], collection=collection)
        if not isinstance(points, list) or points:
            raise ValueError("unexpected empty-ID readback response")
        return {"readback_available": True, "write_verification": "not_tested"}
    except Exception as exc:
        return {"readback_available": False, "write_verification": "blocked",
                "readback_error": type(exc).__name__}

def analyze_curated_memories(provider, args):
    """Reacquire capabilities and compute within ONE provider lifecycle; no writes."""
    operation = args.get("operation")
    minimum = {"analyze_thought_stability": 3, "analyze_geometry": 4,
               "predict_momentum": 2, "predict_relation": 2}.get(operation)
    memories = args.get("memories")
    if minimum is None or not isinstance(memories, list) or not minimum <= len(memories) <= 16:
        raise ValueError("invalid operation or number of memories")
    if operation in {"predict_momentum", "predict_relation"} and len(memories) != 2:
        raise ValueError("this operation requires exactly two memories")
    if "steps" in args and operation != "predict_momentum":
        raise ValueError("steps is only supported by predict_momentum")
    if any(not isinstance(m, str) or not m.strip() or len(m.encode("utf-8")) > 480 for m in memories):
        raise ValueError("each memory must be nonempty and fit 480 UTF-8 bytes")
    if len(set(memories)) != len(memories):
        raise ValueError("duplicate memories are not allowed")
    handles = []
    for content in memories:
        response = json.loads(provider.handle_tool_call("hyperspace_search", {"query": content, "limit": 50}))
        if not response.get("ok"):
            return response
        matches = [r for r in response.get("results", []) if r.get("content") == content
                   and not r.get("quarantined") and not r.get("truncated") and r.get("handle")]
        if len(matches) != 1:
            raise ValueError("memory must match exactly one owned, complete search result")
        handles.append(matches[0]["handle"])
    geometry_args = {"operation": operation, "handles": handles}
    if "steps" in args:
        geometry_args["steps"] = args["steps"]
    result = json.loads(provider.handle_tool_call("hyperspace_geometry", geometry_args))
    result["selection"] = "exact owned content; caller order; same-session capabilities"
    return result

def main() -> int:
    request = json.load(sys.stdin)
    tool_name = request["toolName"]
    args = dict(request.get("args") or {})
    query_info = None
    if tool_name in {"__prefetch__", "hyperspace_search"}:
        args["query"], query_info = prepare_recall_query(
            str(args.get("query") or ""), prefetch=tool_name == "__prefetch__"
        )
    config = request["config"]
    state_path = Path(config["statePath"]).expanduser()
    state_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)

    # HyperspaceDB 3.1.3 can list authenticated collections but returns
    # NOT_FOUND from GetCollectionStats for those same collections. Avoid that
    # inconsistent RPC and verify the schema from ListCollections instead.
    HyperspaceClient.get_collection_stats = _collection_stats_from_listing

    provider_config = {
        "host": config["host"],
        "collection": config["collection"],
        "metric": "lorentz",
        "expected_dimension": 129,
        "trust_mode": "owned_only",
        "auto_store": False,
        "top_k": int(config.get("prefetchTopK") or 5),
        "max_prefetch_chars": int(config.get("prefetchMaxChars") or 3000),
        "allow_insecure_remote": bool(config.get("allowInsecureRemote", False)),
        "rpc_timeout": float(config["rpcTimeout"]),
        "state_path": str(state_path),
        "profile_scope": config.get("profileScope", "openclaw-memory"),
        "api_key_env": "HYPERSPACE_API_KEY",
        "user_id_env": "HYPERSPACE_USER_ID",
        "ownership_hmac_key_env": "HYPERSPACE_OWNERSHIP_HMAC_KEY",
    }
    if config.get("maxDistance") is not None:
        provider_config["max_distance"] = float(config["maxDistance"])

    # The upstream SDK prints some RPC diagnostics to stdout. Keep stdout as a
    # strict one-JSON-message protocol for the Node wrapper.
    provider_stdout = io.StringIO()
    with redirect_stdout(provider_stdout):
        provider = HyperspaceDBMemoryProvider(provider_config)
        original_call = provider._call
        def traced_call(method, *values, **kwargs):
            try:
                return original_call(method, *values, **kwargs)
            except Exception as error:
                print(f"RPC operation {method} failed: {type(error).__name__}", file=sys.stderr)
                raise
        provider._call = traced_call
        provider.initialize(f"openclaw-{uuid.uuid4().hex}", agent_context="primary")
        try:
            if tool_name == "__curated_write__":
                result = apply_curated_write(provider, args, state_path, config.get("curatorLabel", "owner"))
            elif tool_name == "__cognitive__":
                result = analyze_curated_memories(provider, args)
            elif tool_name == "__prefetch__":
                result = {
                    "context": provider.prefetch(
                        str(args.get("query") or ""),
                        session_id=str(args.get("sessionId") or ""),
                    )
                }
            else:
                result = json.loads(
                    provider.handle_tool_call(tool_name, args)
                )
                if tool_name == "hyperspace_status":
                    result.update(probe_readback(provider, config["collection"]))
        finally:
            provider.shutdown()

    if query_info is not None:
        result["queryBudget"] = query_info
        if tool_name == "__prefetch__" and query_info["shortened"]:
            result["context"] = (
                "[HyperspaceDB recall query shortened to fit the embedding backend; "
                "recall may be incomplete.]\n" + result["context"]
            )

    json.dump(result, sys.stdout, ensure_ascii=False, separators=(",", ":"))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        # Provider error rendering already redacts credential-like material. This
        # fallback deliberately returns only the exception class and a bounded message.
        print(f"{type(exc).__name__}: bridge operation failed", file=sys.stderr)
        raise SystemExit(1)
