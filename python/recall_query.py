"""Conservative read-query budget for the deployed embedding backend.

This is a byte budget, not a claim about the server's tokenizer limit. Keep
writes intact: shortening stored content would corrupt the curated memory.
"""

QUERY_MAX_BYTES = 480


def prepare_recall_query(query: str, *, prefetch: bool = False) -> tuple[str, dict]:
    normalized = " ".join(query.split())
    raw = normalized.encode("utf-8")
    shortened = len(raw) > QUERY_MAX_BYTES
    if shortened:
        if prefetch:
            # OpenClaw's prompt includes earlier context before the current input.
            normalized = raw[-QUERY_MAX_BYTES:].decode("utf-8", errors="ignore")
        else:
            # Explicit queries may put their topic first and constraints last.
            half = (QUERY_MAX_BYTES - 5) // 2
            normalized = (raw[:half].decode("utf-8", errors="ignore") + " ... "
                          + raw[-half:].decode("utf-8", errors="ignore"))
    return normalized, {
        "shortened": shortened,
        "originalBytes": len(raw),
        "sentBytes": len(normalized.encode("utf-8")),
        "maxBytes": QUERY_MAX_BYTES,
    }
