"""Ingest protocol markdown files into a local LanceDB table.

Usage:
    python scripts/ingest_protocols_lancedb.py \
        --protocols-dir ./protocols \
        --db-path ./data/lancedb \
        --table protocols

Reads every ``*.skill.md`` under ``--protocols-dir``, chunks it with the same
settings used for Milvus ingestion (size=250, overlap=30), embeds each chunk
with DashScope ``text-embedding-v4`` (matching the current stack), writes a
LanceDB table, and builds a BM25/FTS index on the ``text`` column.

The chunks are schema-compatible with the existing Milvus collection so the
LanceDB adapter can be swapped in without touching protocol_retrieval.py.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# Make ``rag_app`` importable when running this file directly from the
# repo root (which is how a dev would invoke it).
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def _load_embeddings(backend: str = None, model: str = None) -> Any:
    """Return an embedder via the shared factory.

    Respects ``--embedder`` / ``--model`` CLI args, then ``EMBEDDING_BACKEND``
    / ``EMBEDDING_MODEL`` env, then defaults (dashscope + text-embedding-v4).
    """
    from rag_app.core.embeddings import get_embeddings
    return get_embeddings(backend=backend, model=model)


def _load_protocol_files(protocols_dir: Path) -> List[Path]:
    if not protocols_dir.exists():
        raise SystemExit(f"Protocols directory not found: {protocols_dir}")
    # Single source of truth: reuse the runtime allow-list so ingest and
    # retrieval can never drift. Picks up both *.skill.md and
    # *.risk_registry.md per ProtocolRetrievalSkill._ALLOWED_FILES.
    from rag_app.skills.protocol_retrieval import ProtocolRetrievalSkill
    allowed = set(ProtocolRetrievalSkill._ALLOWED_FILES)
    candidates = list(protocols_dir.rglob("*.skill.md")) + list(
        protocols_dir.rglob("*.risk_registry.md")
    )
    return sorted(p for p in candidates if p.name in allowed)


def _chunk_documents(files: List[Path], protocols_dir: Path) -> List[Dict[str, Any]]:
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    # Same chunk settings as notebooks/vectorize_protocols_qwen.ipynb.
    splitter = RecursiveCharacterTextSplitter(chunk_size=250, chunk_overlap=30)

    rows: List[Dict[str, Any]] = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        if not text.strip():
            continue
        chunks = splitter.split_text(text)
        rel = path.relative_to(protocols_dir)
        for idx, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
            rows.append({
                "id": f"{rel}::{idx}",
                "text": chunk,
                "source": str(path),
                "protocol_file": path.name,
                "protocol_relpath": str(rel),
                "source_type": "protocol_skill",
            })
    return rows


def _embed_rows(rows: List[Dict[str, Any]], embeddings: Any, batch_size: int = 32) -> None:
    """Fill each row's ``vector`` field in place using batched embedding calls."""
    texts = [r["text"] for r in rows]
    vectors: List[List[float]] = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        vectors.extend(embeddings.embed_documents(batch))
        print(f"  embedded {min(start + batch_size, len(texts))}/{len(texts)}", flush=True)
    for row, vec in zip(rows, vectors):
        row["vector"] = vec


def _write_table(rows: List[Dict[str, Any]], db_path: Path, table_name: str) -> None:
    import lancedb

    db_path.mkdir(parents=True, exist_ok=True)
    db = lancedb.connect(str(db_path))

    # Normalise the result: newer lancedb's ``list_tables`` returns a
    # ``TableNamesResult`` (paginated, has a ``.tables`` attribute);
    # older versions + the legacy ``table_names`` alias return a plain list.
    if hasattr(db, "list_tables"):
        _raw = db.list_tables()
        existing = list(getattr(_raw, "tables", _raw))
    else:
        existing = list(db.table_names())
    if table_name in existing:
        # POC behaviour: wipe + recreate. Ingestion is cheap and this avoids
        # schema-drift surprises while we iterate.
        db.drop_table(table_name)

    table = db.create_table(table_name, data=rows)

    # Build the full-text (BM25) index on the text column. Requires the
    # ``tantivy`` Python package; LanceDB uses it under the hood.
    try:
        table.create_fts_index("text", replace=True)
    except Exception as e:  # pragma: no cover - depends on local env
        print(f"[warn] FTS index creation failed ({e}); hybrid search will fall back to vector-only.")

    # Vector index: for tables under ~100k rows the brute-force flat scan is
    # already fast, so we skip IVF/HNSW here. Add later if the corpus grows.


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--protocols-dir", default="./protocols", help="Root directory containing *.skill.md files")
    parser.add_argument("--db-path", default="./data/lancedb", help="LanceDB storage directory")
    parser.add_argument("--table", default="protocols", help="Table name")
    parser.add_argument("--dry-run", action="store_true", help="Chunk and count only; skip embedding + write")
    parser.add_argument(
        "--embedder",
        choices=["dashscope", "local"],
        default=None,
        help="Override EMBEDDING_BACKEND. 'local' uses BGE on-device (free, no API).",
    )
    parser.add_argument("--model", default=None, help="Override embedding model name")
    args = parser.parse_args()

    protocols_dir = Path(args.protocols_dir).resolve()
    db_path = Path(args.db_path).resolve()

    files = _load_protocol_files(protocols_dir)
    print(f"Found {len(files)} protocol files under {protocols_dir}")

    rows = _chunk_documents(files, protocols_dir)
    print(f"Produced {len(rows)} chunks")

    if args.dry_run:
        # Estimate embedding-token cost before you spend real quota.
        # DashScope text-embedding-v4 uses a BPE-ish tokenizer; 1 token ≈ 4 chars
        # for English prose, ≈ 1.5 chars for Chinese. We report both bounds.
        total_chars = sum(len(r["text"]) for r in rows)
        est_en = total_chars // 4
        est_cn = int(total_chars / 1.5)
        print(f"\nEstimated embedding tokens: {est_en:,} (English) — {est_cn:,} (Chinese)")
        print(f"Total chars to embed:       {total_chars:,}")
        print(f"Chunk count:                {len(rows)}\n")
        for row in rows[:5]:
            print(f"  - {row['protocol_relpath']} [{len(row['text'])} chars]")
        return 0

    if not rows:
        print("Nothing to ingest.")
        return 0

    embeddings = _load_embeddings(backend=args.embedder, model=args.model)
    print(f"Embedding chunks via {type(embeddings).__name__}...")
    _embed_rows(rows, embeddings)

    print(f"Writing {len(rows)} rows to LanceDB at {db_path} (table={args.table})...")
    _write_table(rows, db_path, args.table)
    print("Done. BM25 index built on `text`.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
