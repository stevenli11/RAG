"""PubMed evidence retrieval skill with fallback search strategy."""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict

from rag_app.services.pubmed import (
    build_pubmed_context,
    build_pubmed_query_candidates,
    search_pubmed,
)

from .base import SkillContext


class PubmedEvidenceSkill:
    name = "pubmed_evidence"

    @staticmethod
    def _content_dedup_key(art: dict[str, Any]) -> str:
        """Key for collapsing articles republished across sister journals.

        Current Protocols (and similar publishers) re-publish the same
        manuscript across 4 sister journals (immunology / protein science /
        cell biology / molecular biology) under distinct PMIDs. PMID-based
        dedup misses this, so the user sees 4 "references" that are
        actually one paper. We collapse by (normalized_title,
        first_author_last_name) so these fold to one entry.
        """
        raw_title = str(art.get("title") or "")
        # Normalize: lowercase, collapse whitespace, strip trailing period.
        title = re.sub(r"\s+", " ", raw_title.lower()).strip().rstrip(".")

        first_author = ""
        authors = art.get("authors") or []
        if isinstance(authors, list) and authors:
            first_author = str(authors[0]).lower()
        if not first_author:
            first_author = str(art.get("author") or "").lower()
        # Reduce to last-name token — robust to "Ni D" vs "Duojiao Ni" etc.
        parts = first_author.replace(",", " ").split()
        first_author_token = parts[-1] if parts else ""

        return f"{title}|{first_author_token}"

    def _dedupe_by_content(
        self, articles: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Collapse articles that share title + first-author across PMIDs."""
        seen: set[str] = set()
        out: list[dict[str, Any]] = []
        for art in articles:
            key = self._content_dedup_key(art)
            # Don't drop records with pathologically empty keys (e.g.,
            # missing title AND authors) — they're rare but real.
            if not key.strip("|"):
                out.append(art)
                continue
            if key in seen:
                continue
            seen.add(key)
            out.append(art)
        return out

    @staticmethod
    def _query_terms(text: str) -> set[str]:
        stop = {
            "the", "and", "for", "with", "from", "that", "this", "how", "what",
            "are", "is", "in", "of", "to", "on", "a", "an", "by", "or", "first",
            "line", "therapy", "treatment", "levels", "influence", "selection",
            "patients",
        }
        words = re.findall(r"[a-zA-Z0-9\\-\\+]+", text.lower())
        return {w for w in words if len(w) > 2 and w not in stop}

    def _filter_relevant(self, question: str, articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not articles:
            return articles
        terms = self._query_terms(question)
        if not terms:
            return articles

        scored: list[tuple[int, dict[str, Any]]] = []
        for art in articles:
            text = f"{art.get('title','')} {art.get('abstract','')}".lower()
            score = sum(1 for t in terms if t in text)
            # boost exact key biomedical phrases if present in the question
            if "pd-l1" in question.lower() and "pd-l1" in text:
                score += 2
            if "nsclc" in question.lower() and "nsclc" in text:
                score += 2
            scored.append((score, art))

        scored.sort(key=lambda x: x[0], reverse=True)
        # keep items with non-zero overlap; if too strict fallback to top half
        filtered = [a for s, a in scored if s > 0]
        if filtered:
            return filtered
        half = max(1, len(scored) // 2)
        return [a for _, a in scored[:half]]

    def run(self, ctx: SkillContext, **kwargs: Any) -> Dict[str, Any]:
        question = str(kwargs.get("question") or "")
        rewritten = str(kwargs.get("rewritten_question") or "")
        small_llm = kwargs.get("small_llm")
        max_results = int(kwargs.get("max_results") or 5)

        base_question = rewritten or question
        api_key = ctx.config.get("pubmed_api_key", "")

        # Reuse the Boolean query(ies) already produced by route_question (via
        # ``rewrite_query_with_pubmed``). The PLURAL hints list is populated
        # when the question was decomposed into sub-questions (one Boolean
        # query per sub-question), or when the LLM emitted complementary
        # variants for a single atomic question.
        pubmed_query_hint = str(ctx.state.get("_pubmed_query_hint") or "")
        pubmed_query_hints: list[str] = [
            str(h).strip() for h in (ctx.state.get("_pubmed_query_hints") or []) if str(h).strip()
        ]
        candidates = build_pubmed_query_candidates(
            base_question,
            small_llm=small_llm,
            llm_query_hint=pubmed_query_hint,
        )
        if not candidates:
            candidates = [base_question]
        # Merge additional per-subquestion Boolean queries as extra candidates
        # (deduped, preserving order). Each one expands the retrieval pool
        # with a distinct sub-topic so downstream rerank can pick the most
        # relevant abstracts across the full compound question.
        if pubmed_query_hints:
            seen_lc = {re.sub(r"\s+", " ", c).strip().lower() for c in candidates}
            for h in pubmed_query_hints:
                key = re.sub(r"\s+", " ", h).strip().lower()
                if key and key not in seen_lc:
                    candidates.append(h)
                    seen_lc.add(key)

        merged_by_pmid: Dict[str, dict[str, Any]] = {}
        ordered_hits: list[dict[str, Any]] = []
        query_used = candidates[0]

        # Multi-query retrieval in PARALLEL. Each search_pubmed call is 2
        # sequential HTTP round-trips (esearch + efetch) to NCBI, ~0.5-2s
        # each. Running 4 candidates serially gives 2-8s — parallelizing
        # drops this to max(candidate_times) ≈ 1-2s. Merge order still
        # follows the original candidate order so the primary/LLM-rewritten
        # queries still take priority when deduplicating by PMID.
        # Cap bumped from 4→6 so per-subquestion hints don't starve the
        # base-question variants; ThreadPoolExecutor parallelizes anyway.
        candidate_queries = candidates[:6]
        with ThreadPoolExecutor(max_workers=len(candidate_queries), thread_name_prefix="pubmed") as pool:
            futures = [
                pool.submit(search_pubmed, q, api_key=api_key, max_results=max_results)
                for q in candidate_queries
            ]
            results_by_candidate = []
            for q, fut in zip(candidate_queries, futures):
                try:
                    results_by_candidate.append((q, fut.result()))
                except Exception:
                    # search_pubmed already swallows exceptions internally,
                    # but belt-and-braces in case a future fails unexpectedly.
                    results_by_candidate.append((q, []))

        # ---- RRF fusion across candidate queries -----------------------
        # Previous behavior: PMID-first-wins dedup — kept the first occurrence
        # across candidate query results, throwing away the per-query rank
        # signal. Result: a paper that ranked #5 in one query and #6 in
        # another (likely highly relevant) ended up at the back of the merged
        # list, while a paper that ranked #1 in only ONE narrow query took
        # the top slot.
        #
        # New behavior: Reciprocal Rank Fusion (Cormack et al., 2009).
        # For each (query, paper, rank) triple:
        #     score(paper) += 1 / (RRF_K + rank)
        # Papers showing up in MORE candidate queries get a natural boost,
        # AND high-ranking papers in any single query still float up. The
        # constant RRF_K=60 is the well-known default that smooths out the
        # tail of long ranked lists.
        RRF_K = 60
        rrf_scores: Dict[str, float] = {}
        article_by_pmid: Dict[str, dict[str, Any]] = {}
        # Articles without a PMID (rare — usually "online ahead of print")
        # can't be cross-query-deduped; keep them with a synthetic key so
        # they still flow through the rest of the pipeline.
        synthetic_kv: list[tuple[str, dict[str, Any]]] = []
        winning_query_for_pmid: Dict[str, tuple[float, str]] = {}

        for q, hits in results_by_candidate:
            for rank_idx, art in enumerate(hits):
                pmid = str(art.get("pmid") or "").strip()
                contribution = 1.0 / (RRF_K + rank_idx + 1)  # rank is 1-indexed
                if pmid:
                    rrf_scores[pmid] = rrf_scores.get(pmid, 0.0) + contribution
                    if pmid not in article_by_pmid:
                        article_by_pmid[pmid] = art
                    # Track which candidate query "won" this paper (highest
                    # single-query rank) for telemetry/debug.
                    cur = winning_query_for_pmid.get(pmid)
                    if cur is None or contribution > cur[0]:
                        winning_query_for_pmid[pmid] = (contribution, q)
                else:
                    synthetic_kv.append((q, art))

        # Order by RRF score descending; stable on ties so PMID order is
        # at least deterministic.
        ranked_pmids = sorted(rrf_scores.keys(), key=lambda p: rrf_scores[p], reverse=True)
        ordered_hits = [article_by_pmid[p] for p in ranked_pmids]
        # Keep no-PMID articles at the tail (rare path, low priority).
        ordered_hits.extend(art for _q, art in synthetic_kv)

        # query_used: pick the candidate query that contributed the most
        # to the top-3 articles' RRF score. Better proxy for "which query
        # actually mattered" than the previous "first non-empty result".
        if ranked_pmids:
            top_winning_queries = [winning_query_for_pmid[p][1] for p in ranked_pmids[:3]]
            # Most common winning query among top-3.
            from collections import Counter as _Counter
            query_used = _Counter(top_winning_queries).most_common(1)[0][0]

        # Collapse Current-Protocols-style duplicates (same paper, different
        # PMIDs across sister journals) BEFORE relevance scoring so duplicates
        # don't monopolize the top-K slots.
        ordered_hits = self._dedupe_by_content(ordered_hits)

        # Stash RRF telemetry so the eval harness / debug route can see how
        # many distinct candidate queries each surviving article showed up in.
        ctx.state["pubmed_rrf"] = {
            "applied": True,
            "k_constant": RRF_K,
            "n_candidate_queries": len(candidate_queries),
            "n_unique_pmids": len(rrf_scores),
            "top_score": max(rrf_scores.values(), default=0.0),
        }

        articles = self._filter_relevant(question=question, articles=ordered_hits)
        articles = articles[:max_results]
        context, references = build_pubmed_context(articles)
        return {
            "query_used": query_used,
            "articles": articles,
            "context": context,
            "references": references,
        }
