"""Protocol retrieval skill: local protocol chunks + method-specific skill snippets."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .base import SkillContext


class ProtocolRetrievalSkill:
    name = "protocol_retrieval"

    # Explicit allow-list of protocol files currently in use. Any file on
    # disk not in this set is ignored by iteration, scoring, and the
    # vector-store allow-list filter (so stale LanceDB chunks from
    # previously-ingested files are suppressed too).
    _ALLOWED_FILES: Tuple[str, ...] = (
        "western_blot.risk_registry.md",
        "Seahorse Real-Time Cell Metabolic Analysis.skill.md",
        "CRISPR-Cas9.skill.md",
    )

    _METHOD_HINTS: Dict[str, Tuple[str, ...]] = {
        "western_blot": ("western blot", "immunoblot", "sds-page", "pvdf", "membrane", "stripping"),
        "crispr_cas9": ("crispr", "cas9", "sgrna", "knockout", "knock-in", "off-target", "guide rna", "hdr", "nhej"),
        "seahorse": ("seahorse", "oxygen consumption", "ocr", "ecar", "extracellular acidification", "mitochondrial respiration", "glycolysis", "metabolic flux"),
    }

    def __init__(self) -> None:
        project_root = Path(__file__).resolve().parents[2]
        # Historical convention uses ``protocols/latest/`` for versioned skill
        # bundles; RAG_local stores skills flat under ``protocols/`` so that
        # ingest (``scripts/ingest_protocols_lancedb.py``) and this skill
        # point at the same place. Fall back to ``protocols/`` when the
        # versioned subdir is absent, which has been silently breaking the
        # skill-file context path (45% of the evidence budget) since the
        # fork. Symptom: ``_build_protocol_skill_context`` returns ``("",
        # [])`` so the LLM never sees complete SOP text and has to rely on
        # chunk-level retrieval alone — which lops off reagent lines from
        # their section headers. See debug/turn_*.md for the evidence.
        versioned = project_root / "protocols" / "latest"
        flat = project_root / "protocols"
        self.protocols_dir = versioned if versioned.exists() else flat
        self._file_tokens_by_name: Dict[str, set[str]] = {}

    def _iter_protocol_skill_files(self) -> List[Path]:
        if not self.protocols_dir.exists():
            return []
        # Collect both *.skill.md and *.risk_registry.md, then keep only
        # those on the allow-list. This guarantees a single source of truth
        # even if new files are dropped into protocols/.
        candidates = list(self.protocols_dir.glob("*.skill.md")) + list(
            self.protocols_dir.glob("*.risk_registry.md")
        )
        allowed = {name for name in self._ALLOWED_FILES}
        return sorted(p for p in candidates if p.name in allowed)

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"\s+", " ", text.lower()).strip()

    def _score_file_for_query(self, file_path: Path, query: str) -> int:
        q = self._normalize(query)
        stem = self._normalize(file_path.stem.replace(".skill", ""))
        score = 0

        # Filename priors.
        for method, hints in self._METHOD_HINTS.items():
            if method.replace("_", " ") in stem:
                score += 1
            for h in hints:
                if h in q:
                    score += 2 if h in stem else 1

        # Token overlap.
        q_tokens = set(re.findall(r"[a-z0-9]{3,}", q))
        s_tokens = set(re.findall(r"[a-z0-9]{3,}", stem))
        score += len(q_tokens.intersection(s_tokens))
        # Front-matter tags / ids from skill file.
        meta_tokens = self._frontmatter_tokens(file_path)
        score += 2 * len(q_tokens.intersection(meta_tokens))
        return score

    def _frontmatter_dict(self, file_path: Path) -> Dict[str, str]:
        """Return raw key→value dict of YAML-ish frontmatter (string values).

        Lighter than the standard YAML parser; the frontmatter format here is
        flat key:value with occasional bracketed lists. We only need scalar
        fields (skill_name, description, method_family, tags-as-string) so a
        line-based parser is fine and avoids adding PyYAML to the runtime.
        """
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        m = re.match(r"(?s)\A---\n(.*?)\n---\n", text)
        if not m:
            return {}
        out: Dict[str, str] = {}
        for line in m.group(1).splitlines():
            if ":" not in line:
                continue
            field, value = line.split(":", 1)
            field = field.strip().lower()
            out[field] = value.strip().strip("\"'")
        return out

    # ------------------------------------------------------------------
    # Skill menu — for system prompts that need a "what's available" listing
    # ------------------------------------------------------------------

    def _menu_entry(self, file_path: Path) -> str:
        """One-line menu entry like::

            - western_blot — Western Blot Complete Workflow Skill (immunoblot, sds_page, transfer)

        Uses ``description:`` frontmatter when present; otherwise auto-derives
        from ``skill_name`` + the first ~3 ``tags`` so we don't need to hand-
        edit every skill file before the menu becomes useful.
        """
        fm = self._frontmatter_dict(file_path)
        stem = self._stem_from_filename(file_path.name)
        # Hand-written description wins.
        desc = fm.get("description", "").strip()
        if desc:
            return f"- {stem} — {desc}"
        # Auto-generate.
        skill_name = fm.get("skill_name", "").strip().strip(",")
        tags_raw = fm.get("tags", "")
        # Strip [...] and pick first 3 tag tokens.
        tag_tokens = re.findall(r"[a-z0-9_]{3,}", tags_raw.lower())[:3]
        tag_blurb = f" ({', '.join(tag_tokens)})" if tag_tokens else ""
        if skill_name:
            return f"- {stem} — {skill_name}{tag_blurb}"
        return f"- {stem}{tag_blurb}"

    def build_skill_menu(self) -> str:
        """Compact one-line-per-skill listing of every skill in the library.

        Cheap (filesystem read + regex over frontmatter only). Intended for
        injection into the answer-LLM system context so the model knows what
        other protocols exist beyond the 1-2 currently retrieved — useful
        when the user's question spans methods the router didn't pick.
        """
        files = self._iter_protocol_skill_files()
        if not files:
            return ""
        entries = [self._menu_entry(p) for p in files]
        return "Available protocol skills (full content loaded only when retrieved):\n" + "\n".join(entries)

    def _frontmatter_tokens(self, file_path: Path) -> set[str]:
        key = file_path.name
        if key in self._file_tokens_by_name:
            return self._file_tokens_by_name[key]

        text = file_path.read_text(encoding="utf-8", errors="ignore")
        m = re.match(r"(?s)\A---\n(.*?)\n---\n", text)
        if not m:
            tokens = set(re.findall(r"[a-z0-9_]{3,}", file_path.stem.lower()))
            self._file_tokens_by_name[key] = tokens
            return tokens

        tokens: set[str] = set(re.findall(r"[a-z0-9_]{3,}", file_path.stem.lower()))
        front = m.group(1)
        for line in front.splitlines():
            low = line.strip().lower()
            if ":" not in low:
                continue
            field, value = low.split(":", 1)
            field = field.strip()
            value = value.strip()
            # Keep only canonical method identity fields. ``tags`` / ``applies_to``
            # are too broad (e.g., CRISPR skill tags include western_blot for
            # downstream validation), which pollutes intent allow-list matching.
            if field in {"skill_id", "method_family", "skill_name"}:
                tokens.update(re.findall(r"[a-z0-9_]{3,}", value))
        self._file_tokens_by_name[key] = tokens
        return tokens

    @staticmethod
    def _stem_from_filename(name: str) -> str:
        return (
            name.lower()
            .replace(".risk_registry.md", "")
            .replace(".skill.md", "")
            .replace(".skill", "")
            .replace(".md", "")
            .strip()
        )

    def _select_skill_files_for_intent(self, query: str, intent: str) -> List[Path]:
        files = self._iter_protocol_skill_files()
        if not files:
            return []
        ql = self._normalize(query)
        compare_mode = any(k in ql for k in ("compare", "comparison", " versus ", " vs ", "difference"))
        # Keep tighter allow-list by default; expand only for explicit comparison queries.
        max_files = 2 if compare_mode else 1
        method = self._detect_primary_method(query)
        method_hints = tuple(self._METHOD_HINTS.get(method, ()))

        scored = sorted(
            ((self._score_file_for_query(p, query), p) for p in files),
            key=lambda x: x[0],
            reverse=True,
        )
        positive = [(s, p) for s, p in scored if s > 0]
        if not positive:
            return []

        # Explicit comparison queries should pull two distinct method families
        # when available (e.g., immunofluorescence vs flow cytometry).
        if compare_mode:
            method_scores: List[Tuple[int, str]] = []
            for m, hints in self._METHOD_HINTS.items():
                score = sum(1 for h in hints if h in ql)
                if m.replace("_", " ") in ql:
                    score += 2
                if score > 0:
                    method_scores.append((score, m))
            method_scores.sort(reverse=True)
            top_methods = [m for _, m in method_scores[:2]]
            if top_methods:
                selected: List[Path] = []
                seen_names = set()
                for m in top_methods:
                    m_name = m.replace("_", " ")
                    m_hints = tuple(self._METHOD_HINTS.get(m, ()))
                    for _score, p in positive:
                        stem = self._stem_from_filename(p.name)
                        tokens = self._frontmatter_tokens(p)
                        if (
                            m in stem
                            or m_name in stem
                            or m in tokens
                            or any(h.replace(" ", "_") in tokens for h in m_hints)
                        ):
                            if p.name not in seen_names:
                                selected.append(p)
                                seen_names.add(p.name)
                            break
                # Belt-and-suspenders: a comparison query should always surface
                # 2 distinct skill files when 2 methods were detected. If
                # strict method-to-file matching left us short (e.g. the
                # file's frontmatter tokens miss the intersection because of
                # underscore vs hyphen quirks), top up with the next-highest
                # positive files whose stems are distinct. Without this,
                # compare_if_vs_fc regresses to a single file.
                if len(selected) < min(2, len(top_methods)):
                    selected_stems = {self._stem_from_filename(p.name) for p in selected}
                    for _score, p in positive:
                        if p.name in seen_names:
                            continue
                        stem = self._stem_from_filename(p.name)
                        stem_tokens = set(re.findall(r"[a-z0-9]+", stem))
                        is_distinct = all(
                            not (stem_tokens & set(re.findall(r"[a-z0-9]+", s)))
                            for s in selected_stems
                        )
                        if not is_distinct:
                            continue
                        selected.append(p)
                        seen_names.add(p.name)
                        selected_stems.add(stem)
                        if len(selected) >= min(2, len(top_methods)):
                            break
                if selected:
                    return selected[:max_files]

        # Intent-aware + tag-aware gate: for protocol/hybrid/knowledge queries,
        # prefer files whose canonical method identity aligns with inferred method.
        if method and intent in {"protocol", "hybrid", "knowledge", "comparison"}:
            gated: List[Path] = []
            method_name = method.replace("_", " ")
            for _score, p in positive:
                stem = self._stem_from_filename(p.name)
                tokens = self._frontmatter_tokens(p)
                if (
                    method in stem
                    or method_name in stem
                    or method in tokens
                    or any(h.replace(" ", "_") in tokens for h in method_hints)
                ):
                    gated.append(p)
            if gated:
                # For comparison queries, try to include two distinct method families.
                if compare_mode and len(gated) > 1:
                    uniq = []
                    seen = set()
                    for p in gated:
                        stem = self._stem_from_filename(p.name)
                        fam = next((m for m in self._METHOD_HINTS if m in stem), stem)
                        if fam in seen:
                            continue
                        seen.add(fam)
                        uniq.append(p)
                    if uniq:
                        return uniq[:max_files]
                return gated[:max_files]

        return [p for _, p in positive[:max_files]]

    def _detect_primary_method(self, query: str) -> str:
        """Return the dominant method family inferred from query hints."""
        q = self._normalize(query)
        best_method = ""
        best_score = 0
        for method, hints in self._METHOD_HINTS.items():
            score = sum(1 for h in hints if h in q)
            if method.replace("_", " ") in q:
                score += 2
            if score > best_score:
                best_score = score
                best_method = method
        return best_method if best_score > 0 else ""

    @staticmethod
    def _doc_source_blob(doc: Any) -> str:
        meta = getattr(doc, "metadata", {}) or {}
        source = " ".join(
            str(meta.get(k, "") or "")
            for k in ("protocol_relpath", "source", "file_path", "path", "skill_id", "title")
        )
        text = (getattr(doc, "page_content", "") or "")[:400]
        return f"{source} {text}".lower()

    @staticmethod
    def _doc_source_name(doc: Any) -> str:
        meta = getattr(doc, "metadata", {}) or {}
        for key in ("protocol_relpath", "source", "file_path", "path", "title"):
            val = meta.get(key)
            if val:
                return str(val).lower()
        return ""

    def _apply_method_focus(self, query: str, docs: List[Any]) -> List[Any]:
        """Prefer chunks from the same method family to reduce cross-protocol contamination."""
        if not docs:
            return docs
        method = self._detect_primary_method(query)
        if not method:
            return docs

        target_hints = self._METHOD_HINTS.get(method, ())
        method_name = method.replace("_", " ")
        other_hints = tuple(
            h
            for m, hints in self._METHOD_HINTS.items()
            if m != method
            for h in hints
        )

        scored = []
        strict_source = []
        for i, doc in enumerate(docs):
            blob = self._doc_source_blob(doc)
            src = self._doc_source_name(doc)
            if method_name in src:
                strict_source.append((i, doc))
            target_hits = sum(1 for h in target_hints if h in blob)
            other_hits = sum(1 for h in other_hints if h in blob)
            source_target_hits = sum(1 for h in target_hints if h in src)
            source_other_hits = sum(1 for h in other_hints if h in src)
            scored.append((source_target_hits, target_hits, -source_other_hits, -other_hits, -i, doc))

        # Hard source guardrail: if any chunks are clearly from this method's file,
        # keep those first to avoid cross-protocol lexical contamination.
        if strict_source:
            strict_source.sort(key=lambda x: x[0])
            return [d for _, d in strict_source]

        # Prefer method-consistent sources; fall back to weaker lexical evidence only if needed.
        strong = [item for item in scored if item[0] > 0]
        if not strong:
            strong = [item for item in scored if item[1] > 0]
        if not strong:
            return docs

        strong.sort(reverse=True)
        return [item[5] for item in strong]

    # Metadata / boilerplate patterns we do NOT want to burn highlight slots on.
    # These match YAML-ish front-matter lines (``tags: [...]``, ``applies_to:
    # [...]``), enum cells in markdown parameter tables, and file-level prose
    # about "how do I run a western blot" — all of which trigger the numeric
    # regex but carry zero SOP-parameter value.
    _METADATA_LINE_PATTERNS = (
        re.compile(r"^\s*(tags|applies_to|does_not_apply_to|bsl_level|skill_id|"
                   r"skill_name|version|method_family|applies|requires)\s*:", re.IGNORECASE),
        re.compile(r"^\s*\|\s*\w+\s*\|\s*enum\s*:", re.IGNORECASE),  # table enum row
        re.compile(r"This skill is invoked when", re.IGNORECASE),
    )

    def _score_highlight_line(self, line: str, q_tokens: set) -> int:
        """Rank a parameter-bearing line by SOP specificity for the query.

        Higher = more likely to carry the concrete reagent/condition the
        user is asking about. Used in place of ``first-N-in-file-order`` so
        a 1000-line skill.md with 200 YAML/table rows at the top doesn't
        starve the truly specific lines further down.
        """
        low = line.lower()
        score = 0
        # Strong signals: co-occurrence of a specific reagent and a numeric
        # pH / concentration / temperature within the same line.
        reagent_hit = any(r in low for r in ("glycine", "tris", "mercaptoethanol", "sds", "edta", "dtt"))
        if reagent_hit:
            score += 3
        # pH + digit is almost always an SOP value, not metadata.
        if re.search(r"ph\s*\d", low):
            score += 3
        if "mm " in low or low.endswith("mm") or re.search(r"\d+\s*mm\b", low):
            score += 2
        if re.search(r"\d+\s*°c", low) or re.search(r"\d+\s*c\b", low):
            score += 1
        if re.search(r"\d+\s*(?:-\s*\d+)?\s*min\b", low):
            score += 1
        # Overlap with the user's query tokens (minus very short/common ones).
        meaningful_q = {t for t in q_tokens if len(t) >= 4 and t not in {"with", "from", "this", "that", "what", "does", "when", "should"}}
        score += sum(1 for t in meaningful_q if t in low)
        # Penalty for lines that look like YAML/table metadata or prose.
        if any(pat.search(line) for pat in self._METADATA_LINE_PATTERNS):
            score -= 5
        # Penalty for lines that are mostly comma-separated identifiers
        # (common in ``tags: [a, b, c, ...]`` continuations).
        if low.count(",") >= 5 and "buffer" not in low and "ph" not in low:
            score -= 2
        return score

    def _extract_skill_parameter_highlights(self, query: str, max_items: int = 8) -> List[str]:
        """Pull parameter-bearing lines from top protocol skill files.

        Strategy: collect every line that (a) looks like it carries a
        numeric protocol parameter *and* (b) is not obvious metadata, then
        rank by ``_score_highlight_line`` so reagent+pH+temp co-occurrences
        float to the top. Previously we returned the first ``max_items``
        hits in file order, which got saturated by the YAML front-matter
        before reaching the real SOP body — see debug/turn_*.md for the
        symptom where ``pH 2.0 / 25 mM glycine-HCl`` never made it into
        the LLM context.
        """
        files = self._iter_protocol_skill_files()
        if not files:
            return []
        scored_files = sorted(
            ((self._score_file_for_query(p, query), p) for p in files),
            key=lambda x: x[0],
            reverse=True,
        )
        selected = [p for s, p in scored_files if s > 0][:1]
        if not selected:
            return []

        q = self._normalize(query)
        q_tokens = set(re.findall(r"[a-z0-9\-]{3,}", q))
        param_pattern = re.compile(
            r"(?i)(pH\s*\d|mM|%|°C|incubat|min\b|glycine|tris|sds|mercaptoethanol|buffer)"
        )

        # Stage 1: collect all candidate lines (deduplicated) with their
        # specificity score.
        candidates: List[Tuple[int, str]] = []
        seen = set()
        for p in selected:
            text = p.read_text(encoding="utf-8", errors="ignore")
            for raw in text.splitlines():
                line = re.sub(r"\s+", " ", raw).strip(" -\t")
                if len(line) < 24:
                    continue
                if not param_pattern.search(line):
                    continue
                key = line.lower()[:180]
                if key in seen:
                    continue
                seen.add(key)
                score = self._score_highlight_line(line, q_tokens)
                if score <= 0:
                    # Drop metadata/noise outright.
                    continue
                candidates.append((score, line[:220]))

        # Stage 2: pick the top-N by score (ties broken by original order).
        candidates.sort(key=lambda x: x[0], reverse=True)
        return [line for _, line in candidates[:max_items]]

    @staticmethod
    def _extract_protocol_brief(text: str, max_chars: int) -> str:
        if max_chars <= 0:
            return ""

        # Keep frontmatter + key sections to minimize token usage.
        blocks: List[str] = []
        header_match = re.match(r"(?s)\A---\n.*?\n---\n", text)
        if header_match:
            blocks.append(header_match.group(0).strip())

        # Prefer key headings.
        key_sections = ("## 1. CONTEXT", "## 2. INPUTS", "## 3. WORKFLOW MODULES")
        for section in key_sections:
            idx = text.find(section)
            if idx >= 0:
                chunk = text[idx: idx + 2000]
                blocks.append(chunk.strip())

        # Pull safety-critical lines globally.
        critical_lines = []
        for line in text.splitlines():
            l = line.strip()
            if any(tag in l for tag in ("[CRITICAL]", "[DO NOT]", "[DECISION POINT]", "Exit Criteria")):
                critical_lines.append(l)
            if len(critical_lines) >= 25:
                break
        if critical_lines:
            blocks.append("## Critical Checks\n" + "\n".join(f"- {ln}" for ln in critical_lines))

        merged = "\n\n".join(b for b in blocks if b).strip()
        if not merged:
            merged = text[:max_chars]
        return merged[:max_chars].strip()

    def _extract_query_focused_brief(self, text: str, query: str, max_chars: int) -> str:
        """Extract query-neighbor lines so critical reagent/parameter facts survive truncation."""
        if max_chars <= 0:
            return ""
        q = self._normalize(query)
        q_tokens = [t for t in re.findall(r"[a-z0-9\-]{3,}", q) if t not in {"with", "from", "this", "that"}]
        lines = text.splitlines()
        if not lines:
            return ""

        hit_idx = []
        for i, ln in enumerate(lines):
            low = ln.lower()
            if any(tok in low for tok in q_tokens[:12]):
                hit_idx.append(i)

        if not hit_idx:
            return self._extract_protocol_brief(text, max_chars=max_chars)

        # Keep +/-2 lines around each hit and dedupe while preserving order.
        keep = set()
        for idx in hit_idx:
            for j in range(max(0, idx - 2), min(len(lines), idx + 3)):
                keep.add(j)
        ordered = [lines[i] for i in range(len(lines)) if i in keep]
        focused = "\n".join(ordered).strip()
        if len(focused) < max(400, max_chars // 3):
            # Fallback to default brief if focused extraction is too sparse.
            baseline = self._extract_protocol_brief(text, max_chars=max_chars)
            combined = f"{focused}\n\n{baseline}".strip() if focused else baseline
            return combined[:max_chars].strip()
        return focused[:max_chars].strip()

    def _build_protocol_skill_context(self, query: str, max_chars: int, intent: str) -> Tuple[str, List[str]]:
        files = self._select_skill_files_for_intent(query=query, intent=intent)
        if not files or max_chars <= 0:
            return "", []

        # Split budget across selected skills.
        per_file_budget = max(800, max_chars // max(1, len(files)))
        snippets = []
        selected_names = []
        for p in files:
            text = p.read_text(encoding="utf-8", errors="ignore")
            brief = self._extract_query_focused_brief(text, query=query, max_chars=per_file_budget)
            if not brief:
                continue
            selected_names.append(p.name)
            snippets.append(f"### Protocol Skill: {p.stem}\n{brief}")

        merged = "\n\n".join(snippets)[:max_chars].strip()
        return merged, selected_names

    @staticmethod
    def _dedupe_docs(docs: List[Any]) -> List[Any]:
        seen = set()
        uniq = []
        for doc in docs:
            text = (getattr(doc, "page_content", "") or "").strip()
            if not text:
                continue
            key = text[:200]
            if key in seen:
                continue
            seen.add(key)
            uniq.append(doc)
        return uniq

    @staticmethod
    def _extract_parameter_highlights(docs: List[Any], max_items: int = 6) -> List[str]:
        """Pull numeric/condition lines so LLM sees explicit protocol parameters first."""
        highlights: List[str] = []
        seen = set()
        param_pattern = re.compile(
            r"(?i)(pH\s*\d|mM|%|°C|incubat|min\b|glycine|tris|sds|mercaptoethanol|buffer)"
        )
        for doc in docs:
            text = (getattr(doc, "page_content", "") or "").strip()
            if not text:
                continue
            for raw in text.splitlines():
                line = re.sub(r"\s+", " ", raw).strip(" -\t")
                if len(line) < 20:
                    continue
                if not param_pattern.search(line):
                    continue
                key = line[:180].lower()
                if key in seen:
                    continue
                seen.add(key)
                highlights.append(line[:220])
                if len(highlights) >= max_items:
                    return highlights
        return highlights

    def _rerank_docs(self, ctx: SkillContext, query: str, docs: List[Any], top_n: int) -> List[Any]:
        if not docs:
            ctx.state["protocol_rerank"] = {"enabled": False, "applied": False, "reason": "no_docs"}
            return docs
        dashscope_key = str(ctx.config.get("dashscope_key") or "")
        rerank_model = str(ctx.config.get("rerank_model") or "qwen3-rerank")
        if not dashscope_key:
            ctx.state["protocol_rerank"] = {"enabled": False, "applied": False, "reason": "missing_dashscope_key"}
            return docs[:top_n]
        try:
            from langchain_community.document_compressors import DashScopeRerank

            reranker = DashScopeRerank(
                model=rerank_model,
                dashscope_api_key=dashscope_key,
                top_n=top_n,
            )
            reranked = reranker.compress_documents(documents=docs, query=query)
            if reranked:
                ctx.state["protocol_rerank"] = {
                    "enabled": True,
                    "applied": True,
                    "model": rerank_model,
                    "input_docs": len(docs),
                    "output_docs": min(len(reranked), top_n),
                }
                return list(reranked)[:top_n]
        except Exception as e:
            ctx.state["protocol_rerank"] = {
                "enabled": True,
                "applied": False,
                "model": rerank_model,
                "reason": f"error:{type(e).__name__}",
            }
            return docs[:top_n]
        ctx.state["protocol_rerank"] = {
            "enabled": True,
            "applied": False,
            "model": rerank_model,
            "reason": "empty_result",
        }
        return docs[:top_n]

    def _filter_docs_by_allow_list(self, docs: List[Any], allowed_skill_files: List[str]) -> List[Any]:
        if not docs or not allowed_skill_files:
            return docs
        allowed_stems = {self._stem_from_filename(name) for name in allowed_skill_files}
        kept: List[Any] = []
        for doc in docs:
            src = self._doc_source_name(doc)
            if not src:
                kept.append(doc)
                continue
            if any(stem in src for stem in allowed_stems):
                kept.append(doc)
        # Safety fallback: do not blank out retrieval if metadata is missing/mismatched.
        return kept if kept else docs

    def run(self, ctx: SkillContext, **kwargs: Any) -> Dict[str, Any]:
        vectorstore = kwargs.get("vectorstore")
        query = str(kwargs.get("query") or "")
        intent = str(kwargs.get("intent") or "hybrid")
        k = int(kwargs.get("k") or 8)
        max_context_chars = int(kwargs.get("max_context_chars") or 6000)
        # Extra per-subquestion queries for compound questions. When present,
        # we run one Milvus retrieval per subquery and union the candidate
        # pool BEFORE dedup + rerank — so a question like "compare A vs B AND
        # troubleshoot C" surfaces chunks for each sub-topic instead of only
        # the lexically dominant one.
        subqueries_raw = kwargs.get("subqueries") or []
        subqueries: List[str] = [
            str(s).strip() for s in subqueries_raw if str(s).strip()
        ]

        # Reserve budget for local protocol skill snippets.
        skill_budget = min(5000, max(1200, int(max_context_chars * 0.45)))
        doc_budget = max(0, max_context_chars - skill_budget)

        protocol_skill_context, protocol_skill_files = self._build_protocol_skill_context(
            query=query,
            intent=intent,
            max_chars=skill_budget,
        )

        if vectorstore is None:
            return {
                "docs": [],
                "local_context": protocol_skill_context[:max_context_chars],
                "protocol_skill_files": protocol_skill_files,
            }

        # Stage-1 retrieval: pull a wider candidate set from Milvus.
        candidate_k = max(k * 3, min(40, k + 8))
        search_kwargs = {"k": candidate_k}
        try:
            # If collection has protocol source_type metadata, filter to protocol chunks.
            search_kwargs["expr"] = 'source_type == "protocol_skill"'
            retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)
            docs = retriever.invoke(query)
        except Exception:
            retriever = vectorstore.as_retriever(search_kwargs={"k": candidate_k})
            docs = retriever.invoke(query)

        # Per-subquestion retrieval for compound questions — union into the
        # candidate pool. Bounded to avoid unbounded fan-out on pathological
        # inputs; rerank will whittle back down to top-k.
        if subqueries:
            for sq in subqueries[:3]:
                try:
                    sq_docs = retriever.invoke(sq)
                    if sq_docs:
                        docs = list(docs) + list(sq_docs[: max(4, k)])
                except Exception:
                    continue

        # Targeted fallback retrieval for parameter-heavy troubleshooting queries.
        ql = self._normalize(query)
        needs_param_fallback = any(t in ql for t in ("stripping", "buffer", "ph", "incubation", "temperature", "sds"))
        if needs_param_fallback:
            try:
                focus_query = f"{query} composition pH temperature duration glycine SDS Tris beta-mercaptoethanol"
                focused_docs = retriever.invoke(focus_query)
                if focused_docs:
                    docs = list(docs) + list(focused_docs[: max(4, k)])
            except Exception:
                pass

        docs = self._dedupe_docs(docs)
        docs = self._filter_docs_by_allow_list(docs=docs, allowed_skill_files=protocol_skill_files)
        docs = self._apply_method_focus(query=query, docs=docs)
        docs = self._rerank_docs(ctx=ctx, query=query, docs=docs, top_n=max(1, k))

        unique_texts = [(doc.page_content or "").strip() for doc in docs if (doc.page_content or "").strip()]
        doc_param_highlights = self._extract_parameter_highlights(docs)
        skill_param_highlights = self._extract_skill_parameter_highlights(query=query)
        param_highlights = []
        seen_h = set()
        for line in doc_param_highlights + skill_param_highlights:
            key = line.lower()[:180]
            if key in seen_h:
                continue
            seen_h.add(key)
            param_highlights.append(line)

        local_doc_context = "\n\n".join(unique_texts)[:doc_budget]
        pieces = []
        if param_highlights:
            pieces.append(
                "Internal parameter highlights (quote directly when relevant):\n"
                + "\n".join(f"- {line}" for line in param_highlights)
            )
        if protocol_skill_context:
            pieces.append("Protocol skills (method-specific):\n" + protocol_skill_context)
        if local_doc_context:
            pieces.append("Retrieved protocol context:\n" + local_doc_context)

        # Append the skill menu at the END so the LLM is aware of what other
        # protocol skills exist in the library — useful for "I don't have X
        # in my skill library" calibration without inflating the primary
        # evidence slot. Capped to ~600 chars; only added if there's spare
        # budget after the main pieces.
        try:
            menu_text = self.build_skill_menu()
        except Exception:
            menu_text = ""
        if menu_text:
            current_len = sum(len(p) for p in pieces) + 8 * len(pieces)
            menu_budget = max(0, max_context_chars - current_len - 100)
            if menu_budget >= 200:  # only include when there's real room
                pieces.append(menu_text[:menu_budget])
        local_context = "\n\n".join(pieces)[:max(0, max_context_chars)]

        return {
            "docs": docs,
            "local_context": local_context,
            "protocol_skill_files": protocol_skill_files,
        }
