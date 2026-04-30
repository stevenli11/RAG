"""Demo / smoke-test for the LanceDB hybrid retrieval POC.

Run after ``scripts/ingest_protocols_lancedb.py`` has populated the table.

Usage:
    python scripts/demo_lancedb_retrieval.py \
        "How do I set up PD-L1 flow cytometry gating?"

Prints the top-K hits with their source file, rank, and score so you can
eyeball whether BM25+vector hybrid search is pulling the right chunks.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("query", nargs="+", help="Natural-language query")
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--db-path", default=None)
    parser.add_argument("--table", default=None)
    parser.add_argument("--filter", default=None, help="LanceDB SQL WHERE (e.g. \"source_type = 'protocol_skill'\")")
    parser.add_argument("--no-rrf", action="store_true", help="Use linear fusion instead of RRF")
    parser.add_argument(
        "--embedder",
        choices=["dashscope", "local"],
        default=None,
        help="Must match the backend used at ingest time.",
    )
    parser.add_argument("--model", default=None)
    args = parser.parse_args()

    query = " ".join(args.query)

    # Same embedder factory as ingest — the two MUST agree for search to work.
    from rag_app.core.embeddings import get_embeddings
    embeddings = get_embeddings(backend=args.embedder, model=args.model)

    from rag_app.data.lancedb_backend import load_lancedb_vectorstore
    store = load_lancedb_vectorstore(embeddings, db_path=args.db_path, table_name=args.table)
    if store is None:
        raise SystemExit("LanceDB table not found. Run scripts/ingest_protocols_lancedb.py first.")

    search_kwargs = {"k": args.k, "use_rrf": not args.no_rrf}
    if args.filter:
        search_kwargs["expr"] = args.filter

    retriever = store.as_retriever(search_kwargs=search_kwargs)

    start = time.perf_counter()
    docs = retriever.invoke(query)
    elapsed_ms = (time.perf_counter() - start) * 1000

    print(f"\nQuery:  {query}")
    print(f"Hits:   {len(docs)}   (latency {elapsed_ms:.0f} ms, fusion={'RRF' if not args.no_rrf else 'linear'})")
    print("-" * 72)
    for i, doc in enumerate(docs, 1):
        meta = doc.metadata or {}
        src = meta.get("protocol_relpath") or meta.get("protocol_file") or meta.get("source") or "?"
        score_bits = []
        if "_rrf_score" in meta:
            score_bits.append(f"rrf={meta['_rrf_score']:.4f}")
        if "_hybrid_score" in meta:
            score_bits.append(f"hybrid={meta['_hybrid_score']:.4f}")
        score_str = " ".join(score_bits) or "—"
        snippet = (doc.page_content or "").strip().replace("\n", " ")
        if len(snippet) > 180:
            snippet = snippet[:180] + "…"
        print(f"[{i:>2}] {src}   {score_str}")
        print(f"     {snippet}")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
