"""Evidence grading skill for PubMed + local context."""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Tuple

from .base import SkillContext

logger = logging.getLogger(__name__)


class EvidenceGradingSkill:
    name = "evidence_grading"

    # Clinical-evidence hierarchy markers (RCTs, reviews, guidelines).
    _HIGH_QUALITY_HINTS = (
        "meta-analysis",
        "systematic review",
        "randomized",
        "phase iii",
        "phase 3",
        "guideline",
        "consensus",
        # Methods / protocol domain — review articles and validation papers
        # are the de-facto "high" tier for bench-science questions. Without
        # these markers, a western-blot or FACS question gets ALL abstracts
        # graded "low", which previously suppressed citations entirely.
        "review",
        "validated",
        "validation",
        "benchmark",
        "comparative analysis",
    )
    _MEDIUM_QUALITY_HINTS = (
        "phase ii",
        "phase 2",
        "cohort",
        "real-world",
        "retrospective",
        "prospective",
        # Methods-paper medium tier.
        "methods",
        "protocol",
        "optimized",
        "characterization",
        "technical note",
    )

    _RERANK_SCORE_THRESHOLD = 0.2

    # DashScopeRerank costs ~1-3s per call regardless of doc count. Previously
    # skipped for pools <=12 under the assumption keyword scoring is close
    # enough, but that left off-topic PubMed hits (broad "antigen" matches for
    # a western-blot stripping query) untouched — and they then cluttered the
    # Biomni-style inline references list even though the LLM correctly cited
    # only the one relevant paper. Dropping to 5 ensures even modest pools
    # get cross-encoder filtering; anything below that is usually signal-rich
    # enough that keyword order is fine.
    _RERANK_SKIP_BELOW = 3

    # ------------------------------------------------------------------
    # Quality labelling (kept as-is for quality_counts metadata)
    # ------------------------------------------------------------------

    def _quality_label(self, title: str, abstract: str) -> str:
        text = f"{title} {abstract}".lower()
        if any(k in text for k in self._HIGH_QUALITY_HINTS):
            return "high"
        if any(k in text for k in self._MEDIUM_QUALITY_HINTS):
            return "medium"
        return "low"

    # ------------------------------------------------------------------
    # Legacy keyword-based scoring (fallback only)
    # ------------------------------------------------------------------

    @staticmethod
    def _query_terms(text: str) -> set[str]:
        stop = {
            "the", "and", "for", "with", "from", "that", "this", "how", "what",
            "are", "is", "in", "of", "to", "on", "a", "an", "by", "or", "vs",
            "line", "first", "second", "patients", "patient", "treatment", "therapy",
        }
        words = re.findall(r"[a-zA-Z0-9\-\+]+", text.lower())
        return {w for w in words if len(w) > 2 and w not in stop}

    def _score_article(self, question: str, article: Dict[str, Any]) -> Tuple[int, str]:
        text = f"{article.get('title','')} {article.get('abstract','')}".lower()
        terms = self._query_terms(question)
        overlap = sum(1 for t in terms if t in text)

        score = overlap
        if "nsclc" in question.lower() and "nsclc" in text:
            score += 2
        if "pd-l1" in question.lower() and "pd-l1" in text:
            score += 2
        if "pembrolizumab" in question.lower() and "pembrolizumab" in text:
            score += 2

        quality = self._quality_label(article.get("title", ""), article.get("abstract", ""))
        if quality == "high":
            score += 3
        elif quality == "medium":
            score += 1

        return score, quality

    # ------------------------------------------------------------------
    # Cross-encoder reranking via DashScopeRerank
    # ------------------------------------------------------------------

    def _rerank_articles(
        self,
        ctx: SkillContext,
        question: str,
        articles: List[Dict[str, Any]],
        top_n: int,
    ) -> List[Tuple[float, str, Dict[str, Any]]] | None:
        """Rerank articles using DashScopeRerank.

        Returns a list of (relevance_score, quality_label, article) tuples
        sorted by relevance_score descending, or *None* if reranking failed
        so the caller can fall back to keyword scoring.
        """
        dashscope_key = str(ctx.config.get("dashscope_key") or "")
        if not dashscope_key:
            ctx.state["pubmed_rerank"] = {"enabled": False, "applied": False, "reason": "missing_dashscope_key"}
            return None

        rerank_model = str(ctx.config.get("rerank_model") or "qwen3-rerank")

        try:
            from langchain_community.document_compressors import DashScopeRerank
            from langchain_core.documents import Document
        except ImportError:
            logger.debug("DashScopeRerank or langchain_core not available; falling back to keyword scoring.")
            ctx.state["pubmed_rerank"] = {
                "enabled": True,
                "applied": False,
                "model": rerank_model,
                "reason": "missing_dependency",
            }
            return None

        # Build Document objects: page_content = title + abstract
        docs: List[Document] = []
        doc_to_article: Dict[int, Dict[str, Any]] = {}
        for idx, art in enumerate(articles):
            title = art.get("title", "") or ""
            abstract = art.get("abstract", "") or ""
            content = f"{title}\n{abstract}".strip()
            if not content:
                content = "(no content)"
            docs.append(Document(page_content=content, metadata={"_idx": idx}))
            doc_to_article[idx] = art

        try:
            reranker = DashScopeRerank(
                model=rerank_model,
                dashscope_api_key=dashscope_key,
                top_n=min(top_n, len(docs)),
            )
            reranked = reranker.compress_documents(documents=docs, query=question)
        except Exception:
            logger.warning("DashScopeRerank call failed; falling back to keyword scoring.", exc_info=True)
            ctx.state["pubmed_rerank"] = {
                "enabled": True,
                "applied": False,
                "model": rerank_model,
                "reason": "api_error",
            }
            return None

        if not reranked:
            ctx.state["pubmed_rerank"] = {
                "enabled": True,
                "applied": False,
                "model": rerank_model,
                "reason": "empty_result",
            }
            return None

        results: List[Tuple[float, str, Dict[str, Any]]] = []
        for doc in reranked:
            relevance_score = float(doc.metadata.get("relevance_score", 0.0))
            if relevance_score < self._RERANK_SCORE_THRESHOLD:
                continue
            orig_idx = doc.metadata.get("_idx")
            if orig_idx is None:
                for i, orig_doc in enumerate(docs):
                    if orig_doc.page_content[:200] == doc.page_content[:200]:
                        orig_idx = i
                        break
            if orig_idx is None:
                continue
            art = doc_to_article[orig_idx]
            quality = self._quality_label(art.get("title", ""), art.get("abstract", ""))
            results.append((relevance_score, quality, art))

        results.sort(key=lambda x: x[0], reverse=True)
        ctx.state["pubmed_rerank"] = {
            "enabled": True,
            "applied": True,
            "model": rerank_model,
            "input_docs": len(articles),
            "output_docs": len(results),
        }
        return results

    # ------------------------------------------------------------------
    # Context formatting
    # ------------------------------------------------------------------

    def _build_graded_context(self, ranked: List[Tuple[float, str, Dict[str, Any]]]) -> str:
        if not ranked:
            return ""

        lines: List[str] = []
        for idx, (score, quality, art) in enumerate(ranked, start=1):
            title = art.get("title", "")
            year = art.get("year", "")
            pmid = art.get("pmid", "")
            abstract = (art.get("abstract", "") or "").strip()
            snippet = abstract[:420].replace("\n", " ")
            if len(abstract) > 420:
                snippet += "..."

            # Derive key-findings hint from first sentence of abstract if short enough
            findings = ""
            if abstract:
                first_sent_match = re.match(r"^(.+?[.!?])\s", abstract)
                if first_sent_match and len(first_sent_match.group(1)) < 200:
                    findings = first_sent_match.group(1)

            quality_display = quality.capitalize()
            score_display = f"{score:.2f}" if isinstance(score, float) else str(score)

            block = (
                f"[{idx}] (Quality: {quality_display} | Relevance: {score_display})\n"
                f"Title: {title}\n"
                f"Abstract: {snippet}"
            )
            if findings:
                block += f"\nKey findings: {findings}"
            if year:
                block += f"\nYear: {year}"
            if pmid:
                block += f"\nPMID: {pmid}"

            lines.append(block)
        return "\n\n".join(lines)

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    # Coverage floor: when the question was decomposed, every sub-question
    # gets at least this many articles in the final ranked pool. Without
    # this, a small/niche sub-topic can be entirely starved by the global
    # rerank ordering — yielding "answered general" responses for that
    # specific sub-question.
    _MIN_PER_SUBQ = 2

    def _subq_coverage_promote(
        self,
        ranked: List[Tuple[float, str, Dict[str, Any]]],
        all_articles: List[Dict[str, Any]],
        subquestions: List[str],
        max_keep: int,
    ) -> List[Tuple[float, str, Dict[str, Any]]]:
        """Ensure each sub-question has ≥``_MIN_PER_SUBQ`` articles kept.

        Cheap keyword-overlap pass — no extra rerank API calls. For each
        sub-question, count how many ranked entries already cover it; if
        the count is below the floor, promote the best-overlapping
        articles from the full pool that aren't already in the ranked
        set. Promoted items get a synthetic score below the lowest real
        rerank score so they don't reorder strong matches.
        """
        if not subquestions or not ranked:
            return ranked

        ranked_pmids = {str(art.get("pmid") or "") for _, _, art in ranked}
        # Lowest score in the current ranked list — promotions go below it.
        try:
            min_score = min(s for s, _, _ in ranked)
        except ValueError:
            min_score = 0.0
        promotion_score = max(0.01, min_score - 0.05)

        for sq in subquestions:
            sq_terms = self._query_terms(sq)
            if not sq_terms:
                continue
            covered = 0
            for _score, _q, art in ranked:
                text = f"{art.get('title','')} {art.get('abstract','')}".lower()
                if any(t in text for t in sq_terms):
                    covered += 1
                if covered >= self._MIN_PER_SUBQ:
                    break
            if covered >= self._MIN_PER_SUBQ:
                continue

            # Find best-overlap articles from full pool not already kept.
            candidates: List[Tuple[int, Dict[str, Any]]] = []
            for art in all_articles:
                pmid = str(art.get("pmid") or "")
                if pmid and pmid in ranked_pmids:
                    continue
                text = f"{art.get('title','')} {art.get('abstract','')}".lower()
                overlap = sum(1 for t in sq_terms if t in text)
                if overlap > 0:
                    candidates.append((overlap, art))
            candidates.sort(key=lambda x: x[0], reverse=True)
            need = self._MIN_PER_SUBQ - covered
            for _overlap, art in candidates[:need]:
                quality = self._quality_label(art.get("title", ""), art.get("abstract", ""))
                ranked.append((promotion_score, quality, art))
                ranked_pmids.add(str(art.get("pmid") or ""))
                # Decay so successive promotions sort below earlier ones.
                promotion_score = max(0.005, promotion_score - 0.01)

        # Re-cap at max_keep but keep promoted entries (they're already at
        # the tail with lower scores, so the slice is safe).
        return ranked[: max(1, max_keep + len(subquestions) * self._MIN_PER_SUBQ)]

    def run(self, ctx: SkillContext, **kwargs: Any) -> Dict[str, Any]:
        question = str(kwargs.get("question") or "")
        articles = list(kwargs.get("articles") or [])
        max_keep = int(kwargs.get("max_keep") or 18)
        subquestions_raw = kwargs.get("subquestions") or []
        subquestions = [str(s).strip() for s in subquestions_raw if str(s).strip()]

        if not articles:
            return {
                "ranked_articles": [],
                "graded_pubmed_context": "",
                "evidence_summary": "No PubMed evidence available.",
                "quality_counts": {"high": 0, "medium": 0, "low": 0},
                "low_only_pubmed": False,
            }

        # --- Skip rerank for small candidate pools (fast-path) ---
        # Saves ~1-3s of DashScopeRerank API time when PubMed already cut the
        # set to a manageable size. The quality delta on <12-doc pools is
        # modest since keyword scoring + PubMed's own relevance sort capture
        # most of the signal.
        if len(articles) <= self._RERANK_SKIP_BELOW:
            reranked = None
            ctx.state["pubmed_rerank"] = {
                "enabled": True,
                "applied": False,
                "model": str(ctx.config.get("rerank_model") or "qwen3-rerank"),
                "reason": "pool_too_small",
                "input_docs": len(articles),
                "skip_threshold": self._RERANK_SKIP_BELOW,
            }
        else:
            reranked = self._rerank_articles(ctx, question, articles, top_n=max_keep)

        if reranked is not None:
            # Successfully reranked via DashScopeRerank
            ranked = reranked[:max(1, max_keep)]
        else:
            # Fallback: legacy keyword scoring (also the fast-path when the
            # candidate pool was too small to justify the rerank API call).
            keyword_ranked: List[Tuple[float, str, Dict[str, Any]]] = []
            for art in articles:
                score, quality = self._score_article(question, art)
                keyword_ranked.append((float(score), quality, art))
            keyword_ranked.sort(key=lambda x: x[0], reverse=True)
            ranked = keyword_ranked[:max(1, max_keep)]

        # Coverage保底: when the question decomposed, ensure each subq has
        # representation in the kept set.
        if subquestions:
            ranked = self._subq_coverage_promote(
                ranked=list(ranked),
                all_articles=articles,
                subquestions=subquestions,
                max_keep=max_keep,
            )

        high_n = sum(1 for _, q, _ in ranked if q == "high")
        med_n = sum(1 for _, q, _ in ranked if q == "medium")
        low_n = sum(1 for _, q, _ in ranked if q == "low")

        if high_n + med_n == 0:
            evidence_summary = ""
        else:
            evidence_summary = (
                f"Ranked {len(ranked)} PubMed studies (high={high_n}, medium={med_n}, low={low_n}). "
                "Prioritize high and medium evidence when making strong claims."
            )

        graded_context = self._build_graded_context(ranked)

        return {
            "ranked_articles": [art for _, _, art in ranked],
            "graded_pubmed_context": graded_context,
            "evidence_summary": evidence_summary,
            "quality_counts": {"high": high_n, "medium": med_n, "low": low_n},
            "low_only_pubmed": bool(low_n > 0 and high_n + med_n == 0),
        }
