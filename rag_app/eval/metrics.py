"""Quantitative retrieval / answer-quality metrics for the eval harness.

Pure functions — no I/O, no LLM calls. Inputs are dicts shaped like the
``/chat/turn`` JSON response (post-Phase-0 schema, with ``subquestions``,
``citation_verdicts``, ``timings``, etc.) plus a golden case dict. Outputs
are floats / dicts so the runner can aggregate per-bucket and across the
whole set.

Glossary of expected keyword formats in golden cases (``expected_pmid_keywords``):

  expected_pmid_keywords:
    - ["stripping", "ph"]   # AND within sublist
    - ["glycine", "buffer"] # OR across sublists

A retrieved article "matches" if ANY sublist is fully contained in the
title+abstract (case-insensitive). This lets fixture authors express
"either of these concept clusters proves the article is relevant."
"""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Sequence, Tuple


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _article_text(article: Dict[str, Any]) -> str:
    """Concat title + abstract, lowercased, for keyword matching."""
    parts = [str(article.get("title") or ""), str(article.get("abstract") or "")]
    return " ".join(parts).lower()


def _matches_keyword_groups(
    text: str, keyword_groups: Sequence[Sequence[str]]
) -> bool:
    """Return True iff ANY group's keywords are ALL present in text."""
    if not keyword_groups:
        return False
    for group in keyword_groups:
        if not group:
            continue
        if all(kw.lower() in text for kw in group):
            return True
    return False


def _normalize_subq(s: str) -> set[str]:
    """Tokenize a subquestion to a content-word set for F1 comparison.

    Drops English/Chinese stop-ish particles plus very short tokens. The
    F1 here is loose by design — we don't want exact-phrase matches.
    """
    stop = {
        "the", "and", "for", "with", "from", "that", "this", "how", "what",
        "are", "is", "in", "of", "to", "on", "a", "an", "by", "or", "vs",
        "do", "does", "can", "should", "would", "be", "as", "at",
        "怎么", "如何", "什么", "为什么", "和", "与", "及", "的", "了",
    }
    s = s.lower()
    tokens = re.findall(r"[a-z0-9\-]{3,}|[一-鿿]{2,}", s)
    return {t for t in tokens if t not in stop}


# ---------------------------------------------------------------------------
# Retrieval metrics: Recall@K / MRR@K / Hit@K
# ---------------------------------------------------------------------------


def recall_at_k(
    articles: Sequence[Dict[str, Any]],
    keyword_groups: Sequence[Sequence[str]],
    k: int,
) -> float:
    """Fraction of keyword groups satisfied by at least one top-K article.

    A group is "satisfied" if at least one of the top-K articles contains
    ALL keywords in that group. This is the "concept coverage" recall —
    different from classical IR recall (which needs gold doc IDs we don't
    have for PubMed). Range [0, 1].
    """
    if not keyword_groups:
        return 1.0  # vacuously satisfied — no expectation to fail
    if not articles:
        return 0.0
    topk = list(articles[:k])
    hits = 0
    for group in keyword_groups:
        if not group:
            continue
        for art in topk:
            text = _article_text(art)
            if all(kw.lower() in text for kw in group):
                hits += 1
                break
    return hits / max(1, len(keyword_groups))


def mrr_at_k(
    articles: Sequence[Dict[str, Any]],
    keyword_groups: Sequence[Sequence[str]],
    k: int,
) -> float:
    """Mean reciprocal rank of the FIRST article matching ANY group.

    Returns 1/rank where rank is the position (1-indexed) of the earliest
    top-K article whose text contains all keywords from at least one group.
    Returns 0.0 when none match. Range [0, 1].
    """
    if not articles or not keyword_groups:
        return 0.0
    for idx, art in enumerate(articles[:k], start=1):
        text = _article_text(art)
        if _matches_keyword_groups(text, keyword_groups):
            return 1.0 / idx
    return 0.0


def hit_at_k(
    articles: Sequence[Dict[str, Any]],
    keyword_groups: Sequence[Sequence[str]],
    k: int,
) -> float:
    """Binary: at least one top-K article matches at least one group.

    Returns 1.0 / 0.0. Coarsest of the three retrieval metrics; useful
    for tracking "did we get anything relevant at all".
    """
    if not articles or not keyword_groups:
        return 0.0
    for art in articles[:k]:
        if _matches_keyword_groups(_article_text(art), keyword_groups):
            return 1.0
    return 0.0


# ---------------------------------------------------------------------------
# Decomposition metric: Subq F1
# ---------------------------------------------------------------------------


def subq_decomposition_f1(
    predicted: Sequence[str],
    expected: Sequence[str],
) -> float:
    """Token-level F1 between predicted and expected sub-questions.

    Strategy: tokenize each side via ``_normalize_subq`` and compute set-based
    precision/recall over the UNION of all sub-question tokens. This is
    deliberately loose — a perfect match isn't required, just thematic
    overlap. Both empty -> 1.0; one empty + one non-empty -> 0.0.
    """
    pred_tokens: set[str] = set()
    for s in predicted:
        pred_tokens |= _normalize_subq(s)
    exp_tokens: set[str] = set()
    for s in expected:
        exp_tokens |= _normalize_subq(s)
    if not pred_tokens and not exp_tokens:
        return 1.0
    if not pred_tokens or not exp_tokens:
        return 0.0
    tp = len(pred_tokens & exp_tokens)
    if tp == 0:
        return 0.0
    precision = tp / len(pred_tokens)
    recall = tp / len(exp_tokens)
    return 2 * precision * recall / (precision + recall)


# ---------------------------------------------------------------------------
# Coverage metric: per-subq citation coverage
# ---------------------------------------------------------------------------


def coverage_rate(
    answer_text: str,
    subquestions: Sequence[str],
    references_all: Sequence[Dict[str, Any]],
    min_per_subq: int = 2,
) -> float:
    """Fraction of sub-questions that have ≥ ``min_per_subq`` citations whose
    cited reference text overlaps with the sub-question's keywords.

    Process: for each sub-question, find the ``[N]`` citations that appear
    in the same paragraph/sentence as the sub-question's keywords, and check
    that the cited references' titles/abstracts also overlap with those
    keywords. Return ratio of well-covered sub-questions.

    When ``subquestions`` is empty, returns 1.0 (vacuously covered — atomic
    questions don't need this metric).
    """
    if not subquestions:
        return 1.0
    if not references_all:
        return 0.0

    cite_re = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")
    covered = 0
    for sq in subquestions:
        sq_tokens = _normalize_subq(sq)
        if not sq_tokens:
            continue
        # Find citations whose surrounding ~200-char window contains ≥1 sq token,
        # AND whose referenced article text also contains ≥1 sq token.
        good_cites = 0
        for m in cite_re.finditer(answer_text):
            window_start = max(0, m.start() - 200)
            window_end = min(len(answer_text), m.end() + 200)
            window_text = answer_text[window_start:window_end].lower()
            if not any(t in window_text for t in sq_tokens):
                continue
            try:
                nums = [int(x.strip()) for x in m.group(1).split(",")]
            except ValueError:
                continue
            for n in nums:
                if 1 <= n <= len(references_all):
                    ref_text = _article_text(references_all[n - 1])
                    if any(t in ref_text for t in sq_tokens):
                        good_cites += 1
        if good_cites >= min_per_subq:
            covered += 1
    return covered / len(subquestions)


# ---------------------------------------------------------------------------
# Faithfulness metric: directly from the verifier output
# ---------------------------------------------------------------------------


def faithfulness_rate(
    verdicts: Sequence[Dict[str, Any]],
    *,
    answer_text: str = "",
    require_citations: bool = False,
) -> float:
    """Fraction of citation verdicts that came back ``supported``.

    The verifier returns three labels (supported / partial / unsupported);
    we treat "partial" as 0.5 weight to differentiate it from outright
    wrong cites without rewarding it fully.

    Empty-verdict semantics (the trap previously hidden by this metric):
      - If ``require_citations`` is True AND the answer has no inline
        ``[N]`` cites, that's a faithfulness FAILURE, not a vacuous pass —
        we return 0.0. This caught a real regression where the LLM was
        emitting alphanumeric internal IDs (``[B-CC-021]``) instead of
        numeric cites; faithfulness silently stayed at 1.0 because the
        verifier had nothing to check.
      - Otherwise (no expectation of cites, or the answer is just empty),
        return 1.0 — no claims means no violations.
    """
    inline_cites = re.findall(r"\[\d+(?:\s*,\s*\d+)*\]", answer_text or "")
    if not verdicts:
        if require_citations and not inline_cites:
            return 0.0
        return 1.0
    score = 0.0
    for v in verdicts:
        status = str(v.get("status") or "").lower()
        if status == "supported":
            score += 1.0
        elif status == "partial":
            score += 0.5
    return score / len(verdicts)


def cite_rate(answer_text: str) -> float:
    """Returns 1.0 if the answer contains ≥1 numeric inline citation, else 0.0.

    A separate, simple, hard-to-game indicator that complements the
    faithfulness metric: catches the failure mode where the LLM emits
    NO ``[N]`` citations at all (regardless of evidence quality), which
    the verifier-based faithfulness metric misses by design.
    """
    if not answer_text:
        return 0.0
    return 1.0 if re.search(r"\[\d+(?:\s*,\s*\d+)*\]", answer_text) else 0.0


# ---------------------------------------------------------------------------
# Aggregation helpers (used by the harness for per-bucket / overall reports)
# ---------------------------------------------------------------------------


def aggregate(values: Iterable[float]) -> Dict[str, float]:
    """Return mean / p50 / p95 over a sequence of floats; empty -> zeros."""
    vals = sorted(v for v in values if v is not None)
    n = len(vals)
    if n == 0:
        return {"mean": 0.0, "p50": 0.0, "p95": 0.0, "n": 0}
    mean = sum(vals) / n
    p50 = vals[n // 2]
    p95 = vals[max(0, int(n * 0.95) - 1)] if n >= 20 else vals[-1]
    return {"mean": mean, "p50": p50, "p95": p95, "n": n}


def compute_all(
    *,
    case: Dict[str, Any],
    response: Dict[str, Any],
    k_retrieval: int = 10,
) -> Dict[str, float]:
    """Compute every metric for one (case, response) pair.

    Returns a flat dict like::

        {"recall@10": 0.5, "mrr@10": 0.33, "hit@10": 1.0,
         "subq_f1": 0.62, "coverage_rate": 0.5,
         "faithfulness": 0.83, "latency_total": 21.4}

    Missing fields default to neutral values (0 for retrieval metrics on
    empty result, 1 for "vacuously satisfied" cases — see each metric).
    """
    articles: List[Dict[str, Any]] = list(response.get("references_all") or [])
    answer = str(response.get("answer_markdown") or "")
    subqs = list(response.get("subquestions") or [])
    verdicts = list(response.get("citation_verdicts") or [])
    timings = response.get("timings") or {}

    expected_groups = list(case.get("expected_pmid_keywords") or [])
    expected_subqs = list(case.get("expected_subquestions") or [])

    require_cites = bool(case.get("require_citations", False))
    return {
        f"recall@{k_retrieval}": recall_at_k(articles, expected_groups, k_retrieval),
        f"mrr@{k_retrieval}": mrr_at_k(articles, expected_groups, k_retrieval),
        f"hit@{k_retrieval}": hit_at_k(articles, expected_groups, k_retrieval),
        "subq_f1": subq_decomposition_f1(subqs, expected_subqs),
        "coverage_rate": coverage_rate(answer, subqs, articles),
        "faithfulness": faithfulness_rate(verdicts, answer_text=answer, require_citations=require_cites),
        "cite_rate": cite_rate(answer),
        "latency_total": float(timings.get("total") or 0.0),
        "latency_generate": float(timings.get("generate") or 0.0),
        "latency_verify": float(timings.get("verify") or 0.0),
    }
