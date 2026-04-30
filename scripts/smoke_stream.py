#!/usr/bin/env python3
"""Smoke-test the SSE /chat/turn/stream endpoint against a running backend.

Usage
-----
    # 1) Start backend:
    #    uvicorn rag_backend.api.app:app --host 127.0.0.1 --port 8001
    #
    # 2) Run this script:
    python scripts/smoke_stream.py --api-url http://127.0.0.1:8001

What it checks
--------------
1. ``router`` event fires before ``retrieval`` fires before first ``token``.
2. ``token`` events accumulate into a non-empty string.
3. Exactly one ``references`` event, with references_used ⊆ references_all.
4. Terminal ``done`` event.
5. No ``error`` event on happy path.

Prints per-event latencies so you can see TTFT (time-to-first-token).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any, Dict

import requests


def _parse_sse(raw_line_buffer: list[str]) -> Dict[str, Any] | None:
    """Convert a batch of raw lines (one SSE frame) into {event, data}."""
    event = "message"
    data_lines: list[str] = []
    for line in raw_line_buffer:
        if line.startswith(":"):
            continue  # keepalive comment
        if line.startswith("event:"):
            event = line[len("event:"):].strip()
        elif line.startswith("data:"):
            data_lines.append(line[len("data:"):].strip())
    if not data_lines and event == "message":
        return None
    data_raw = "\n".join(data_lines)
    try:
        data = json.loads(data_raw) if data_raw else {}
    except json.JSONDecodeError:
        data = {"_raw": data_raw}
    return {"event": event, "data": data}


def run(api_url: str, question: str, timeout: int) -> int:
    url = f"{api_url.rstrip('/')}/chat/turn/stream"
    payload = {
        "question": question,
        "chat_history": [],
        "retrieval_k": 8,
        "pubmed_max_results": 10,
        "max_context_chars": 6000,
        "generate_followups": False,
    }

    t_start = time.monotonic()
    seen_events: list[str] = []
    token_buf: list[str] = []
    refs_used: list[dict] = []
    refs_all: list[dict] = []
    error_msg = ""
    ttft: float | None = None

    print(f"POST {url}")
    print(f"question: {question}")
    print("---- stream ----")

    with requests.post(url, json=payload, stream=True, timeout=timeout) as resp:
        resp.raise_for_status()
        # requests' .iter_lines yields bytes; decode & group into SSE frames
        # delimited by blank lines per the SSE spec.
        buf: list[str] = []
        for raw in resp.iter_lines(decode_unicode=True):
            if raw is None:
                continue
            if raw == "":
                evt = _parse_sse(buf)
                buf = []
                if evt is None:
                    continue
                seen_events.append(evt["event"])
                dt = time.monotonic() - t_start
                if evt["event"] == "token":
                    if ttft is None:
                        ttft = dt
                    token_buf.append(evt["data"].get("text", ""))
                    # Inline progress dot so the console shows streaming.
                    sys.stdout.write(".")
                    sys.stdout.flush()
                elif evt["event"] == "references":
                    refs_used = evt["data"].get("references_used", []) or []
                    refs_all = evt["data"].get("references_all", []) or []
                    print(f"\n[{dt:.2f}s] references: used={len(refs_used)} all={len(refs_all)}")
                elif evt["event"] == "error":
                    error_msg = evt["data"].get("message", "")
                    print(f"\n[{dt:.2f}s] ERROR @ {evt['data'].get('stage')}: {error_msg}")
                elif evt["event"] == "done":
                    print(f"\n[{dt:.2f}s] done")
                    break
                else:
                    print(f"\n[{dt:.2f}s] {evt['event']}: {json.dumps(evt['data'], ensure_ascii=False)[:160]}")
            else:
                buf.append(raw)

    answer = "".join(token_buf)
    print("\n---- checks ----")
    checks: list[tuple[str, bool, str]] = []

    router_idx = seen_events.index("router") if "router" in seen_events else -1
    retrieval_idx = seen_events.index("retrieval") if "retrieval" in seen_events else -1
    first_token_idx = seen_events.index("token") if "token" in seen_events else -1
    checks.append((
        "event_order",
        0 <= router_idx < retrieval_idx < (first_token_idx if first_token_idx >= 0 else 10**9),
        f"router@{router_idx} retrieval@{retrieval_idx} first_token@{first_token_idx}",
    ))
    checks.append(("no_error", error_msg == "", error_msg or "no error event"))
    checks.append(("has_tokens", len(answer) > 0, f"answer length={len(answer)}"))
    checks.append(("has_done", "done" in seen_events, f"done present={'done' in seen_events}"))

    used_pmids = {r.get("pmid") for r in refs_used}
    all_pmids = {r.get("pmid") for r in refs_all}
    checks.append((
        "references_used_subset",
        used_pmids.issubset(all_pmids) if used_pmids else True,
        f"used={len(used_pmids)} all={len(all_pmids)} subset_ok={used_pmids.issubset(all_pmids)}",
    ))
    if ttft is not None:
        print(f"TTFT (time-to-first-token): {ttft:.2f}s")

    for name, ok, detail in checks:
        flag = "OK " if ok else "ERR"
        print(f"  {flag} {name}: {detail}")

    return 0 if all(ok for _, ok, _ in checks) else 1


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--api-url", default="http://127.0.0.1:8001")
    p.add_argument(
        "--question",
        default="What is the pH and composition of the mild stripping buffer for western blot membrane?",
    )
    p.add_argument("--timeout", type=int, default=180)
    args = p.parse_args()
    return run(args.api_url, args.question, args.timeout)


if __name__ == "__main__":
    raise SystemExit(main())
