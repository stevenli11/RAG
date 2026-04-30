"""Citation parsing and PubMed link rendering."""

from __future__ import annotations

import re
from typing import Any, Dict, List


def linkify_citations(text: str, pubmed_articles: List[Dict[str, Any]]) -> str:
    """Convert [n], (n), [n-m], [n, m] to clickable PubMed links."""
    if not text:
        return text

    pmid_map = {}
    for i, art in enumerate(pubmed_articles or [], 1):
        pmid = art.get("pmid", "")
        if pmid:
            pmid_map[i] = str(pmid)

    def _make_link(num: int) -> str:
        pmid = pmid_map.get(num)
        if pmid:
            return f" [{num}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/) "
        return f" [{num}] "

    def _replace_multi(match: re.Match) -> str:
        inner = match.group(1)
        nums = [s.strip() for s in inner.split(",")]
        parts = []
        for n in nums:
            m_range = re.fullmatch(r"(\d+)\s*[-–—]\s*(\d+)", n)
            if m_range:
                a, b = int(m_range.group(1)), int(m_range.group(2))
                if a <= b and (b - a) <= 20:
                    parts.extend(_make_link(i) for i in range(a, b + 1))
                    continue
            if n.isdigit():
                parts.append(_make_link(int(n)))
            else:
                parts.append(n)
        return ", ".join(parts)

    def _replace_single(match: re.Match) -> str:
        return _make_link(int(match.group(1)))

    def _make_pmid_link(match: re.Match) -> str:
        pmid = match.group(1)
        return f" [PMID:{pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/) "

    text = re.sub(r"（(\d[\d\s,，、\-–—]+\d)）", r"(\1)", text)
    text = re.sub(r"(?<=\d)[，、](?=\s*\d)", ",", text)
    text = re.sub(r"(?<=\d)[–—](?=\d)", "-", text)
    text = re.sub(r"\((\d+(?:\s*(?:,|-)\s*\d+)+)\)", _replace_multi, text)
    text = re.sub(r"\[(\d+(?:\s*(?:,|-)\s*\d+)+)\]", _replace_multi, text)
    text = re.sub(r"(?<!\w)\((\d{1,2})\)(?!\()", _replace_single, text)
    text = re.sub(r"(?<!!)\[(\d{1,2})\](?!\()", _replace_single, text)
    text = re.sub(r"(?<!!)\[(\d{7,8})\](?!\()", _make_pmid_link, text)
    text = re.sub(r"(?<!\w)\((\d{7,8})\)(?!\()", _make_pmid_link, text)
    return text


def has_inline_citation_markers(text: str) -> bool:
    """Check if body contains numeric citation markers."""
    if not text:
        return False
    return bool(
        re.search(r"\[\d+(?:\s*(?:,|-|–|—)\s*\d+)*\]", text)
        or re.search(r"\((?:\d+(?:\s*(?:,|-|–|—)\s*\d+)*)\)", text)
    )


def extract_cited_reference_indices(text: str, max_index: int) -> List[int]:
    """Extract cited indices from body, including range groups."""
    if not text or max_index <= 0:
        return []
    cited = set()
    group_pattern = re.compile(r"[\[\(](\d+(?:\s*(?:,|-|–|—)\s*\d+)*)[\]\)]")
    for group in group_pattern.findall(text):
        norm = re.sub(r"[–—]", "-", group)
        for part in [p.strip() for p in norm.split(",") if p.strip()]:
            m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", part)
            if m:
                a, b = int(m.group(1)), int(m.group(2))
                if a > b:
                    a, b = b, a
                if (b - a) <= 50:
                    for i in range(a, b + 1):
                        if 1 <= i <= max_index:
                            cited.add(i)
                continue
            if part.isdigit():
                i = int(part)
                if 1 <= i <= max_index:
                    cited.add(i)
    return sorted(cited)

