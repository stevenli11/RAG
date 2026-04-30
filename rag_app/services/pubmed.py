import re
import os
import logging
from typing import List, Dict, Any
import requests
from langchain_core.messages import HumanMessage
from rag_app.utils.text_cleaning import clean_text


logger = logging.getLogger(__name__)


_PUBMED_TERM_EXPANSIONS: Dict[str, List[str]] = {
    "cell viability": ['"cell viability"[tiab]', '"cell survival"[tiab]'],
    "passage": ['passage[tiab]', 'subculture[tiab]'],
    "trypsin": ['trypsin[tiab]', '"trypsin-edta"[tiab]'],
    "mycoplasma": ['mycoplasma[tiab]', '"mycoplasma contamination"[tiab]'],
    "contamination": ['contamination[tiab]', '"microbial contamination"[tiab]'],
    "flow cytometry": ['"flow cytometry"[tiab]', '"fluorescence activated cell sorting"[tiab]'],
    "western blot": ['"western blot"[tiab]', 'immunoblot[tiab]'],
    "rt-qpcr": ['"rt-qpcr"[tiab]', '"real-time pcr"[tiab]', 'qPCR[tiab]'],
}

_MESH_HINTS: Dict[str, str] = {
    "cell viability": '"Cell Survival"[Mesh]',
    "mycoplasma": '"Mycoplasma"[Mesh]',
    "flow cytometry": '"Flow Cytometry"[Mesh]',
    "western blot": '"Blotting, Western"[Mesh]',
    "polymerase chain reaction": '"Polymerase Chain Reaction"[Mesh]',
}

def search_pubmed(query: str, api_key: str = "", max_results: int = 5, timeout: int = 10) -> List[Dict[str, Any]]:
    """
    Search PubMed using NCBI E-utilities and return basic article metadata.
    
    Returns a list of dicts with keys:
        pmid, title, abstract, journal, year, authors
    """
    if not query:
        return []
    
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results,
        "sort": "relevance",
    }
    if api_key:
        params["api_key"] = api_key
    
    debug_pubmed = os.getenv("APP_DEBUG_PUBMED", "0") == "1"
    try:
        # Step 1: esearch to get PMIDs
        esearch_url = f"{base_url}/esearch.fcgi"
        # Show the full URL when debugging. logger.info gets swallowed by the
        # default uvicorn log config (WARNING-level root); print to stderr so
        # the diagnostic line is unconditional and visible without log-level
        # juggling.
        try:
            preview = requests.Request("GET", esearch_url, params=params).prepare().url
            if debug_pubmed:
                import sys as _sys
                print(f"[pubmed-debug] ESearch URL: {preview}", file=_sys.stderr, flush=True)
        except Exception:
            pass

        esearch_resp = requests.get(esearch_url, params=params, timeout=timeout)
        esearch_resp.raise_for_status()
        esearch_data = esearch_resp.json()
        id_list = esearch_data.get("esearchresult", {}).get("idlist", [])
        if debug_pubmed:
            import sys as _sys
            print(f"[pubmed-debug] hits={len(id_list)} for term={params.get('term', '')[:120]}",
                  file=_sys.stderr, flush=True)
        if not id_list:
            return []
        
        # Step 2: efetch to get details
        # Use rettype=abstract, retmode=xml for structured data
        efetch_params = {
            "db": "pubmed",
            "id": ",".join(id_list),
            "rettype": "abstract",
            "retmode": "xml",
        }
        if api_key:
            efetch_params["api_key"] = api_key
        
        efetch_resp = requests.get(f"{base_url}/efetch.fcgi", params=efetch_params, timeout=timeout)
        efetch_resp.raise_for_status()
        xml_text = efetch_resp.text
        
        # Very lightweight XML parsing with regex to avoid extra dependencies
        # This is not a full PubMed XML parser, but enough to get title / abstract / journal / year / authors.
        articles: List[Dict[str, Any]] = []
        article_blocks = re.split(r"</PubmedArticle>", xml_text)
        for block in article_blocks:
            if "<PubmedArticle>" not in block:
                continue
            pmid_match = re.search(r"<PMID[^>]*>(\d+)</PMID>", block)
            title_match = re.search(r"<ArticleTitle>(.*?)</ArticleTitle>", block, flags=re.DOTALL)
            # Structured abstracts may include multiple AbstractText sections; concatenate them all.
            abstract_parts = []
            for abst_match in re.finditer(r"<AbstractText([^>]*)>(.*?)</AbstractText>", block, flags=re.DOTALL):
                attrs, inner = abst_match.group(1), clean_text(abst_match.group(2))
                if not inner:
                    continue
                label_match = re.search(r'Label="([^"]*)"', attrs)
                if label_match and label_match.group(1):
                    abstract_parts.append(f"**{label_match.group(1)}:** {inner}")
                else:
                    abstract_parts.append(inner)
            abstract = "\n\n".join(abstract_parts) if abstract_parts else ""
            journal_match = re.search(r"<Title>(.*?)</Title>", block, flags=re.DOTALL)
            year_match = re.search(r"<PubDate>.*?<Year>(\d{4})</Year>.*?</PubDate>", block, flags=re.DOTALL)
            
            authors = []
            # PubMed commonly uses tags like <Author ValidYN="Y">, so match attributes too.
            for author_block in re.findall(r"<Author\b[^>]*>(.*?)</Author>", block, flags=re.DOTALL):
                collective = re.search(r"<CollectiveName>(.*?)</CollectiveName>", author_block, flags=re.DOTALL)
                last = re.search(r"<LastName>(.*?)</LastName>", author_block)
                fore = re.search(r"<ForeName>(.*?)</ForeName>", author_block)
                initials = re.search(r"<Initials>(.*?)</Initials>", author_block)
                suffix = re.search(r"<Suffix>(.*?)</Suffix>", author_block)
                if collective:
                    name = clean_text(collective.group(1))
                    if name:
                        authors.append(name)
                    continue
                if last and fore:
                    full_name = f"{clean_text(fore.group(1))} {clean_text(last.group(1))}"
                    if suffix:
                        full_name += f" {clean_text(suffix.group(1))}"
                    authors.append(full_name)
                elif last and initials:
                    full_name = f"{clean_text(initials.group(1))} {clean_text(last.group(1))}"
                    if suffix:
                        full_name += f" {clean_text(suffix.group(1))}"
                    authors.append(full_name)
                elif last:
                    full_name = clean_text(last.group(1))
                    if suffix:
                        full_name += f" {clean_text(suffix.group(1))}"
                    authors.append(full_name)

            # Collect affiliations for downstream collaborator/network views.
            affs = []
            for aff_match in re.findall(r"<Affiliation>(.*?)</Affiliation>", block, flags=re.DOTALL):
                aff = clean_text(aff_match)
                if aff:
                    affs.append(aff)
            # De-duplicate while preserving order.
            seen_affs = set()
            affiliations = []
            for aff in affs:
                if aff in seen_affs:
                    continue
                seen_affs.add(aff)
                affiliations.append(aff)
            
            pmid = pmid_match.group(1) if pmid_match else ""
            title = clean_text(title_match.group(1)) if title_match else ""
            journal = clean_text(journal_match.group(1)) if journal_match else ""
            year = year_match.group(1) if year_match else ""
            
            if not pmid and not title:
                continue
            
            articles.append({
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "journal": journal,
                "year": year,
                "authors": authors,
                "affiliations": affiliations,
            })
        
        return articles
    except Exception as e:
        # Show PubMed call errors in the UI to aid diagnosis.
        logger.warning("PubMed search failed: %s", e)
        return []

def build_pubmed_context(articles: List[Dict[str, Any]]) -> (str, List[str]):
    """
    Build a text context block from PubMed articles plus a reference list.
    
    Returns:
        context_str: PubMed article context used in prompts (with [1], [2] numbering)
        references: Reference string list (also using [n] numbering)
    """
    if not articles:
        return "", []
    
    context_chunks = []
    references = []
    
    for idx, art in enumerate(articles, start=1):
        pmid = art.get("pmid", "")
        title = art.get("title", "")
        abstract = art.get("abstract", "")
        journal = art.get("journal", "")
        year = art.get("year", "")
        authors = art.get("authors", [])
        
        authors_str = ", ".join(authors[:3])
        if len(authors) > 3:
            authors_str += " et al."
        
        header_parts = []
        if authors_str:
            header_parts.append(authors_str)
        if year:
            header_parts.append(year)
        if journal:
            header_parts.append(journal)
        header = ", ".join(header_parts) if header_parts else ""
        
        chunk_lines = [f"[{idx}] {title}"]
        if header:
            chunk_lines.append(header)
        if abstract:
            chunk_lines.append(f"Abstract: {abstract}")
        if pmid:
            chunk_lines.append(f"PMID: {pmid}")
        
        context_chunks.append("\n".join(chunk_lines))
        
        ref_line = f"[{idx}] {title}"
        if header:
            ref_line += f", {header}"
        if pmid:
            ref_line += f", PMID: {pmid}"
        references.append(ref_line)
    
    context_str = "\n\n".join(context_chunks)
    return context_str, references

def add_pubmed_links_to_answer(answer: str, articles: List[Dict[str, Any]]) -> str:
    """
    Replace citation indices like [1], [2] in the answer with hyperlinks to PubMed pages.
    Example: [1] -> [1](https://pubmed.ncbi.nlm.nih.gov/PMID/)
    """
    if not answer or not articles:
        return answer
    
    # Keep this function for backward compatibility; use process_pubmed_citations for actual work.
    from warnings import warn
    warn("add_pubmed_links_to_answer is deprecated; use process_pubmed_citations instead.")
    return answer

def _format_authors_gbt7714(authors: List[str]) -> str:
    """
    Format the author list in an approximate GB/T 7714 style:
    - Last name first, then initials, e.g. "Shrestha L B"
    - When more than 3 authors exist, keep the first 3 and append "et al."
    """
    if not authors:
        return "Unknown author"
    
    formatted: List[str] = []
    max_list = 3
    for a in authors[:max_list]:
        parts = a.replace(",", " ").split()
        lower_a = a.lower()
        # Keep group/collaborative author names as-is.
        if any(k in lower_a for k in ["group", "consortium", "collaborative", "investigators", "team"]):
            formatted.append(a)
            continue
        if len(parts) >= 2:
            last = parts[-1]
            initials = " ".join(p[0].upper() for p in parts[:-1] if p)
            formatted.append(f"{last} {initials}")
        else:
            formatted.append(a)
    
    if len(authors) > max_list:
        formatted.append("et al.")
    
    return ", ".join(formatted)

def _article_relevance_score(question: str, article: Dict[str, Any]) -> float:
    """Compute a simple lexical relevance score between question and article metadata."""
    if not question:
        return 1.0

    q_tokens = set(re.findall(r"[a-z0-9\-]{3,}", question.lower()))
    if not q_tokens:
        return 1.0

    text = " ".join(
        [
            str(article.get("title", "")),
            str(article.get("abstract", ""))[:1200],
            str(article.get("journal", "")),
        ]
    ).lower()
    a_tokens = set(re.findall(r"[a-z0-9\-]{3,}", text))
    if not a_tokens:
        return 0.0

    overlap = q_tokens.intersection(a_tokens)
    # Weighted overlap: favor absolute overlap and ratio overlap.
    abs_score = min(1.0, len(overlap) / 4.0)
    rel_score = len(overlap) / max(1, len(q_tokens))
    return 0.65 * abs_score + 0.35 * rel_score


def _build_allowed_indices_for_citation(
    question: str,
    articles: List[Dict[str, Any]],
    min_keep: int = 2,
    threshold: float = 0.22,
) -> set[int]:
    """
    Return 1-based article indices allowed for citation after relevance gating.
    Always keeps at least `min_keep` highest-scoring items if articles exist.
    """
    if not articles:
        return set()
    if not question.strip():
        return set(range(1, len(articles) + 1))

    scored = []
    for i, art in enumerate(articles, start=1):
        scored.append((i, _article_relevance_score(question, art)))

    allowed = {i for i, s in scored if s >= threshold}
    if len(allowed) < min_keep:
        top = sorted(scored, key=lambda x: x[1], reverse=True)[:min(min_keep, len(scored))]
        allowed.update(i for i, _ in top)
    return allowed


def process_pubmed_citations(answer: str, articles: List[Dict[str, Any]], question: str = "") -> tuple:
    """
    Unified processing for PubMed citations:
    1) Remove bare PubMed URLs from the answer body;
    2) Renumber [2], [1, 3], etc. by first appearance into [1], [2], [3], ...;
    3) Add hyperlinks to matching PMIDs for each citation index;
    4) Build a GB/T 7714-style reference list sorted by new index (one paper per line).
    Returns: (linked_answer, apa_refs, ordered_old_ids), where ordered_old_ids
    is used for expanded PMID/title/abstract display below.
    """
    if not answer or not articles:
        return answer, [], []
    allowed_old_ids = _build_allowed_indices_for_citation(question, articles)
    
    # 1) Remove bare PubMed URLs.
    cleaned = re.sub(
        r"\s*\(?https://pubmed\.ncbi\.nlm\.nih\.gov/\d+/?\)?",
        "",
        answer,
        flags=re.IGNORECASE,
    )
    
    # 2) Scan and renumber.
    citation_pattern = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")
    old_to_new: Dict[int, int] = {}
    ordered_old_ids: List[int] = []
    next_id = 1
    
    def replace_match(m: re.Match) -> str:
        nonlocal next_id
        inner = m.group(1)
        claim = _claim_window(cleaned, m.start(), m.end())
        nums: List[int] = []
        for part in inner.split(","):
            part = part.strip()
            if not part:
                continue
            try:
                n = int(part)
                nums.append(n)
            except ValueError:
                continue
        # Normalize multi-citation groups:
        # - de-duplicate
        # - always render in ascending order (e.g., 3,4 not 4,3)
        nums = sorted(set(nums))
        if not nums:
            return m.group(0)
        
        linked_parts: List[str] = []
        for old_n in nums:
            if old_n not in allowed_old_ids:
                continue
            if not (1 <= old_n <= len(articles)):
                continue
            # Claim-to-citation alignment gate:
            # only keep citations that lexically support the local claim.
            support = _citation_support_score(claim, articles[old_n - 1])
            if support < 0.12:
                continue
            if old_n not in old_to_new and 1 <= old_n <= len(articles):
                old_to_new[old_n] = next_id
                ordered_old_ids.append(old_n)
                next_id += 1
            new_n = old_to_new.get(old_n)
            if new_n is None or not (1 <= old_n <= len(articles)):
                linked_parts.append(str(old_n))
                continue
            pmid = articles[old_n - 1].get("pmid")
            # Show clickable in-text citation numbers only.
            if pmid:
                linked_parts.append(f"[{new_n}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)")
            else:
                linked_parts.append(str(new_n))
        if not linked_parts:
            return ""
        return ", ".join(linked_parts)
    
    linked_answer = citation_pattern.sub(replace_match, cleaned)
    # Clean punctuation artifacts after citation removal.
    linked_answer = re.sub(r"\(\s*,\s*", "(", linked_answer)
    linked_answer = re.sub(r"\s+,", ",", linked_answer)
    linked_answer = re.sub(r",\s*,+", ", ", linked_answer)
    linked_answer = re.sub(r"\(\s*\)", "", linked_answer)
    linked_answer = re.sub(r"\s{2,}", " ", linked_answer).replace(" .", ".").strip()
    
    # 3) Build GB/T 7714-style references, one line per paper.
    apa_refs: List[str] = []
    for old_n in ordered_old_ids:
        new_n = old_to_new[old_n]
        art = articles[old_n - 1]
        title = art.get("title", "")
        journal = art.get("journal", "")
        year = art.get("year", "")
        pmid = art.get("pmid", "")
        authors = art.get("authors", [])
        
        authors_str = _format_authors_gbt7714(authors)
        # Approximate GB/T 7714 journal style: Author. Title[J]. Journal, Year.
        segments: List[str] = []
        segments.append(f"{authors_str}.")
        if title:
            segments.append(f"{title}[J].")
        if journal:
            segments.append(journal)
        if year:
            segments.append(str(year))
        ref_body = " ".join(segments).strip()
        # Keep PMID only in expanded UI details, not in the title line.
        apa_refs.append(f"[{new_n}] {ref_body}")
    
    return linked_answer, apa_refs, ordered_old_ids

def build_pubmed_query(question: str, small_llm=None) -> str:
    """
    Convert a natural-language question into a concise PubMed query
    (Boolean + field tags), to avoid over-constrained ESearch queries.
    """
    if not question:
        return ""
    if not small_llm:
        # Simple fallback: use the original question.
        return question
    
    prompt = f"""You are an expert PubMed search assistant.
Convert the following natural-language question into a short, effective PubMed search query.

Requirements:
- Use 2-5 key terms; avoid long AND chains that often return 0 results.
- Prefer simple terms and [tiab] when helpful (e.g. NSCLC[tiab], "PD-1"[tiab], "non-small cell lung cancer").
- Use AND only between clearly distinct concepts; use OR for synonyms if needed.
- Do NOT output quotes or explanations. Output ONLY the PubMed query string.

Question:
{question}
"""
    try:
        response = small_llm.invoke([HumanMessage(content=prompt)])
        if hasattr(response, "content"):
            q = response.content.strip()
        else:
            q = str(response).strip()
        # Prevent extra quotes added by the model.
        q = q.strip('"').strip("'").strip()
        return q or question
    except Exception:
        return question


def _expand_query_with_synonyms(question: str) -> str:
    """Build a conservative boolean query using known domain synonym expansions."""
    q = (question or "").lower()
    groups: List[str] = []
    for key, variants in _PUBMED_TERM_EXPANSIONS.items():
        if key in q:
            groups.append("(" + " OR ".join(variants) + ")")

    mesh_terms: List[str] = []
    for key, mesh in _MESH_HINTS.items():
        if key in q:
            mesh_terms.append(mesh)

    # If nothing matched, keep it minimal.
    if not groups and not mesh_terms:
        return question

    parts: List[str] = []
    if groups:
        parts.append(" AND ".join(groups[:3]))
    if mesh_terms:
        parts.append("(" + " OR ".join(mesh_terms[:2]) + ")")

    return " AND ".join(parts).strip() or question


def build_pubmed_query_candidates(
    question: str,
    small_llm=None,
    llm_query_hint: str = "",
) -> List[str]:
    """Return de-duplicated candidate PubMed queries for robust retrieval.

    ``llm_query_hint`` is an optional pre-built Boolean query (typically
    produced upstream by ``rewrite_query_with_pubmed``). When provided and
    non-empty, it is used directly instead of issuing another small_llm call
    via ``build_pubmed_query`` — that is, it short-circuits the LLM step in
    the multi-candidate chain. Saves one round-trip (~1-2s on qwen-flash)
    on the retrieve_and_fuse critical path.
    """
    base = (question or "").strip()
    if not base:
        return []

    candidates: List[str] = [base]
    if llm_query_hint and llm_query_hint.strip():
        # Reuse upstream-produced Boolean query — NO additional LLM call.
        candidates.append(llm_query_hint.strip())
    else:
        llm_q = build_pubmed_query(base, small_llm=small_llm) if small_llm is not None else base
        if llm_q:
            candidates.append(llm_q)
    expanded = _expand_query_with_synonyms(base)
    if expanded:
        candidates.append(expanded)
    simple = _simple_pubmed_keywords(base)
    if simple:
        candidates.append(simple)

    deduped: List[str] = []
    seen = set()
    for c in candidates:
        k = re.sub(r"\s+", " ", c).strip().lower()
        if not k or k in seen:
            continue
        seen.add(k)
        deduped.append(c.strip())
    return deduped

def _simple_pubmed_keywords(question: str, max_terms: int = 8) -> str:
    """
    Extract simple keywords from a natural language question for PubMed fallback.
    Use when both LLM-generated query and raw question return 0 hits.
    """
    if not question:
        return ""
    # Normalize: replace punctuation with space, keep alphanumeric and hyphens (e.g. PD-1)
    text = re.sub(r"[^\w\s\-]", " ", question, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    stop = {
        "how", "do", "does", "the", "a", "an", "in", "on", "for", "to", "of", "and", "or",
        "what", "which", "that", "this", "with", "by", "from", "is", "are", "can", "be",
        "affect", "selection", "levels", "expression", "patient", "treatment", "therapy",
    }
    words = [w for w in text.split() if w.lower() not in stop and len(w) > 1]
    # Prefer longer / technical-looking terms (e.g. NSCLC, PD-L1, non-small)
    seen = set()
    out = []
    for w in words:
        wl = w.lower()
        if wl in seen:
            continue
        seen.add(wl)
        out.append(w)
        if len(out) >= max_terms:
            break
    return " ".join(out) if out else question.strip()[:200]


def _claim_window(text: str, start: int, end: int) -> str:
    """Extract local sentence-like window around a citation marker."""
    left = max(text.rfind(".", 0, start), text.rfind("\n", 0, start))
    right_dot = text.find(".", end)
    right_nl = text.find("\n", end)
    candidates = [x for x in [right_dot, right_nl] if x >= 0]
    right = min(candidates) if candidates else len(text)
    s = text[(left + 1) if left >= 0 else 0 : right].strip()
    return s[:500]


def _citation_support_score(claim_text: str, article: Dict[str, Any]) -> float:
    """Lexical support score between local claim and article title/abstract."""
    if not claim_text:
        return 0.0
    stop = {
        "the", "and", "for", "with", "from", "that", "this", "are", "was", "were", "into",
        "have", "has", "had", "can", "may", "might", "does", "did", "not", "only", "than",
    }
    c_tokens = {t for t in re.findall(r"[a-z0-9\-]{3,}", claim_text.lower()) if t not in stop}
    if not c_tokens:
        return 0.0
    a_text = f"{article.get('title','')} {article.get('abstract','')}".lower()
    a_tokens = set(re.findall(r"[a-z0-9\-]{3,}", a_text))
    if not a_tokens:
        return 0.0
    overlap = c_tokens.intersection(a_tokens)
    return len(overlap) / max(1, min(len(c_tokens), 16))
