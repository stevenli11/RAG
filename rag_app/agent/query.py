# Auto-extracted from original RAG/app.py for modular architecture

import json
import re
from typing import Any, Dict, List

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage

from rag_app.services.history_compress import render_compressed_history


# ---------------------------------------------------------------------------
# Method / cell-line / assay entities to keep alive across multi-turn chats.
# When the user asks a short follow-up like "should I dilute it further?"
# the rewriter often strips the method context, which makes downstream
# protocol_retrieval pick the wrong skill file. We detect these entities
# from the prior turns and inject them into the rewrite prompt as
# "ACTIVE EXPERIMENTAL CONTEXT" so they survive into the rewritten query.
# ---------------------------------------------------------------------------

# Lower-cased substring patterns. Keep this list tight — false positives
# that misclassify a knowledge question as method-anchored are worse than
# missing the rare uncommon assay name.
_METHOD_KEYWORDS = (
    # White-listed methods (highest priority — these have skill files)
    "western blot", "immunoblot", "blot", "wb",
    "phospho-akt", "phospho-", "phospho ",  # phospho with no dash + space
    "seahorse", "xf96", "xfe24", "extracellular flux", "mito stress",
    "glycolysis stress", "ocr", "ecar", "fccp", "oligomycin",
    "crispr", "cas9", "sgrna", "rnp nucleofection", "knockout", "knock-in",
    "hdr", "indel",
    # Common methods (no skill file but worth preserving for query)
    "facs", "flow cytometry", "ihc", "immunohistochemistry",
    "elisa", "rt-qpcr", "qpcr", "transfection", "lipofection",
    "lentiviral", "lentivirus", "emsa", "co-ip", "mass spec",
)

# Cell lines we want carried forward verbatim if mentioned.
_CELL_LINE_PATTERN = re.compile(
    r"\b(HEK\s*293T?|HepG2|HeLa|MCF[\-\s]?7|K562|A549|U87|U2OS|"
    r"BMDM|RAW\s*264\.?7|differentiated\s+myotubes?|primary\s+\w+)\b",
    re.IGNORECASE,
)


def _detect_active_method_context(chat_history: List[Dict[str, Any]] | None) -> Dict[str, List[str]]:
    """Extract carry-forward method / cell-line entities from prior turns.

    Returns ``{"methods": [...], "cell_lines": [...]}``. Empty lists when
    nothing to preserve.

    Scans the FULL chat history, not just the last few turns. Earlier we
    used ``chat_history[-3:]`` but that lost the method anchor on long
    troubleshoot sessions where the user mentions the method ONCE in
    turn 1 and never repeats it (e.g. "western blot" in turn 1, then
    short follow-ups in turns 2-5 like "should I dilute" / "give me a
    plan"). Without the anchor the rewrite drops the method, retrieval
    picks the wrong skill, and the answer drifts to a different method.
    """
    methods: List[str] = []
    cell_lines: List[str] = []
    if not chat_history:
        return {"methods": methods, "cell_lines": cell_lines}

    seen_m: set[str] = set()
    seen_c: set[str] = set()
    for turn in chat_history:
        # Only look at the user's words — assistant might mention many
        # methods incidentally (e.g. "as a sanity check, ELISA…") that
        # would over-anchor future turns if we treated them as carry-forward.
        user_text = str(turn.get("user") or "").lower()
        if not user_text:
            continue
        for kw in _METHOD_KEYWORDS:
            if kw in user_text and kw not in seen_m:
                methods.append(kw)
                seen_m.add(kw)
        for cm in _CELL_LINE_PATTERN.finditer(user_text):
            normalized = cm.group(0).strip()
            key = normalized.lower()
            if key not in seen_c:
                cell_lines.append(normalized)
                seen_c.add(key)

    return {"methods": methods[:6], "cell_lines": cell_lines[:4]}

# ---------------------------------------------------------------------------
# Prompt templates – single source of truth for output format
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are a biomedical research assistant. You answer questions based strictly on the provided evidence.

## Reasoning approach (READ THIS FIRST)

Before writing the answer, scan TWO sources for **specific experimental details the user has already provided**:
  (a) the current question, and
  (b) any `## User-provided experimental context` block at the top of the evidence — this is a document the user uploaded and is the **highest-priority context**. Always anchor the answer to its numbers and observations before falling back to PubMed or generic protocol advice.

Look for: numerical values (cell density, OCR/ECAR readings, protein amounts, concentrations, incubation times, plate formats), observations (signal patterns, unexpected trends, FCCP fold-change, band intensities), and experimental conditions (cell type, differentiation state, treatment). These are the anchor of your answer.

- If the user HAS provided specifics, your answer MUST reference their exact numbers/observations and interpret them directly. Explain why *their* 40-50 pmol/min basal OCR at 30,000 cells/well differentiated myotubes behaves the way it does — not what a generic Seahorse assay looks like. Compare their Exp A vs B vs C head-to-head when they set up that comparison. Generic SOP recitation is a failure mode — avoid it.
- **Adopt the user's own framing verbatim.** If the user-provided document contains named categories ("suppressed dynamic range", "most reliable system", "three regimes"), labelled experimental groups (Exp A / B / C), or cross-experiment synthesis, REUSE those exact labels and build your answer on top of their analysis. Do NOT re-derive conclusions the user has already drawn — their interpretation is a premise, not raw data to re-analyse from scratch. If they called Exp C "suppressed ceiling", say "suppressed ceiling"; if they assigned regimes, use the regime names.
- If the user did NOT provide specifics, then general recommendations are appropriate, and you may end by asking what they observed.
- Never restate the user's numbers back verbatim as a "summary" without interpretation. The value you add is analysis that extends the user's framing — not a ground-up re-explanation of what they already figured out.

## How to structure your answer

1. Open with 2-3 sentences that directly answer the question, giving the reader the key takeaway up front. Do NOT add a title or heading before this — just start answering.

2. Then break the details into numbered sections (## 1. , ## 2. , etc.) with descriptive headings. Choose the organization that matches the question's natural logic:
   - Clinical strata/thresholds (e.g., biomarker levels, disease stages) → one section per stratum
   - Comparing agents/regimens/methods → one section per option, with a comparison table
   - Mechanism/pathway → sections by steps or components
   - Topic review → sections by major themes
   Each section heading should be descriptive (e.g., "PD-L1 TPS ≥50%: Monotherapy Is Standard of Care"), not generic labels.

3. Within sections, use rich formatting where it helps:
   - **Markdown table** when comparing ≥3 items across ≥2 dimensions
   - **Text-based decision tree/flowchart** when the answer involves branching decisions
   - Bold, bullet points, and sub-headings for scannability
   - Use emoji sparingly to improve scannability: e.g., ✅ for recommendations, ⚠️ for warnings/caveats, 🔬 for experimental methods, 💊 for drugs/treatments, 📊 for data/statistics, 🧬 for molecular/genetic topics, 🔑 for key takeaways

4. End with a brief synthesis — a decision framework, summary table, or concluding paragraph depending on the question type.

5. If the answer could be more specific with additional details, close with one sentence suggesting what information the user could provide for a more precise answer. Only include this when genuinely useful.

## Rules
- ONLY use information from the provided evidence. Do not fabricate references.
- **Citation format: numeric only.** Use `[1]`, `[2]`, `[2, 3]` — the numbers must match the `[N]` labels in the "Ranked PubMed evidence" block. Cite every factual or scientific claim that a PubMed abstract supports. When multiple refs support the same claim, combine them as `[2, 5]`.
- **Do NOT write `[internal protocol]`, `[internal protocol; N]`, `[Retrieved protocol context #...]`, `[source]`, or any other non-numeric bracket tag.** Parameters quoted from internal protocols (pH, concentration, temperature, duration, buffer composition) should be integrated naturally into the prose without provenance markers. Provenance is tracked separately by the UI.
- **Two DIFFERENT citation systems — use both:**
  - **PubMed citations**: plain integers like `[1]`, `[2]`, `[2, 3]` indexing into the "Ranked PubMed evidence" block. Mandatory wherever an abstract genuinely supports the claim.
  - **Internal rule references**: when the evidence block or the OBJECTIVE DATA AUDIT block references a specific failure-mode rule by its ID — e.g. `[B-CC-021]`, `[B-DT-022]`, `[B-SI-001]`, `[DX-001]`, `[DX-004]`, `[RULE DX-003]` — **YOU SHOULD inline that rule's ID in your answer EXACTLY as written, in square brackets, right after the sentence that uses the corresponding failure mode.** The UI renders these as hover-tooltip pills showing the rule description; the user actively looks them up. This is how you make audit findings traceable.
  - **Where rule IDs come from**: scan the OBJECTIVE DATA AUDIT block's `invalidating_factors` for `skill_rule_ref` fields and the evidence text itself for any ``[X-XX-NNN]`` / ``[DX-NNN]`` / ``[RULE DX-NNN]`` tokens. Re-use those IDs verbatim — never invent new ones (e.g. `[B-XX-999]` you fabricated — the UI strips these as hallucinations).
  - The two systems never collide: PubMed cites are always pure digits inside brackets, rule refs always contain letters and hyphens. Both can coexist in one sentence: "phospho-protection failed [B-SI-001], degrading the readout [4]."
- **Citation is mandatory when evidence supports a claim.** For every factual or scientific statement in your answer, scan the provided PubMed abstracts: if any abstract genuinely supports that statement (even partially), attach a `[N]` citation. Do not skip citing just because the match isn't perfect — partial support still warrants a cite. The only valid reason to omit a citation is when NO retrieved abstract relates to the specific claim. A well-cited answer typically has 1-3 citations per major section.
- **CRITICAL: Decision trees and flowcharts must be 100% citation-free.** No (1), [1], PMID, or URLs inside ``` code blocks ```. Place all supporting citations in the explanatory paragraph BEFORE or AFTER the diagram. Example of WRONG: "├─ Yes → Monotherapy (1, 3)". Example of CORRECT: "├─ Yes → Monotherapy" with citations in surrounding text.
- Answer in the same language as the question.
- Be comprehensive but organized — depth within structure, not walls of text.
- Do NOT add a title/heading before the opening answer. Do NOT use generic labels like "Overview:", "Summary:", "Follow-up:".
- In follow-up conversations: read the previous conversation carefully. If the user has already told you what they want, DO NOT ask them again. Just do it directly. Never repeat questions the user has already answered.
{instructions}"""

HUMAN_TEMPLATE = """\
Evidence:
{evidence}

Question: {question}"""

def rewrite_query(question, chat_history=None, small_llm=None):
    """
    Rewrite user query to improve retrieval effectiveness.
    
    Functions:
    1. Handle coreference resolution (e.g., "it", "this method")
    2. Optimize query expression for better retrieval
    3. Expand query if needed (optional)
    
    Args:
        question: Current user question
        chat_history: List of previous conversation turns (optional)
        small_llm: Small LLM for query rewriting
    
    Returns:
        Rewritten query string
    """
    if not small_llm:
        # If no small_llm provided, return original question
        return question
    
    try:
        # Build context from chat history if available. For >3 turns,
        # ``render_compressed_history`` summarizes older turns via small_llm
        # so the user's earlier observations / ruled-out approaches survive
        # past the previous hard 3-turn truncation.
        history_context = render_compressed_history(
            chat_history or [], small_llm=small_llm, recent_n=3
        )

        rewrite_prompt = f"""{history_context}Current question: {question}

Please rewrite this question to be more effective for document retrieval. 
- If the question contains pronouns or references (like "it", "this", "that"), replace them with specific terms from the conversation context.
- Make the question more specific and clear for semantic search.
- Keep the core meaning unchanged.
- Return ONLY the rewritten question, no explanations."""

        response = small_llm.invoke([HumanMessage(content=rewrite_prompt)])
        
        # Extract rewritten query
        if hasattr(response, 'content'):
            rewritten = response.content.strip()
        else:
            rewritten = str(response).strip()
        
        # Remove quotes if present
        rewritten = rewritten.strip('"').strip("'").strip()
        
        # If rewriting failed or returned empty, use original
        if not rewritten or len(rewritten) < 3:
            return question
        
        return rewritten
    
    except Exception as e:
        # On error, return original question
        return question


def rewrite_query_with_pubmed(question, chat_history=None, small_llm=None, user_doc_condensed: str = "") -> dict:
    """One LLM call that produces BOTH the retrieval rewrite AND the PubMed query.

    Previously the pipeline made two separate ``small_llm`` calls on the
    critical path:

    1. ``rewrite_query`` — produces a coreference-resolved, retrieval-friendly
       rewrite of the user's question.
    2. ``build_pubmed_query`` (called inside ``pubmed_evidence`` skill) —
       produces a Boolean-style PubMed search query from that rewrite.

    Each costs ~1-2s on qwen-flash, and they're serial (the second reads the
    first's output). Merging them into a single JSON-mode prompt cuts one
    round-trip off the retrieve_and_fuse wall-clock.

    Returns a dict with keys:
      - ``rewritten``: str — retrieval-friendly rewrite (coreference resolved).
      - ``pubmed_query``: str — primary Boolean query (backward compat).
      - ``pubmed_queries``: list[str] — ALL Boolean queries (1 per subq for
        decomposed compound questions; 1-2 variants for simple questions).
      - ``subquestions``: list[str] — when the question is compound, the
        sub-questions to answer independently. Empty list for simple questions.

    On any parse or API failure, falls back to
    ``{"rewritten": question, "pubmed_query": "", "pubmed_queries": [],
    "subquestions": []}`` so downstream skills use their own fallback logic.
    """
    if not small_llm:
        return {"rewritten": question, "pubmed_query": "", "pubmed_queries": [], "subquestions": []}

    try:
        # Compress > 3-turn history into "summary + recent verbatim" so
        # confirmed observations / ruled-out paths survive past the previous
        # hard 3-turn truncation. Identical helper to ``rewrite_query``.
        history_context = render_compressed_history(
            chat_history or [], small_llm=small_llm, recent_n=3
        )

        # Detect carry-forward method / cell-line context from prior turns.
        # Without this, short follow-ups like "should I dilute it further?"
        # lose the western-blot / Seahorse anchor and protocol_retrieval picks
        # the wrong skill file. Surface this to the LLM as a hard constraint
        # in the rewrite — much more reliable than hoping the LLM infers it
        # from the chat-history block.
        active_ctx = _detect_active_method_context(chat_history)
        method_block = ""
        if active_ctx["methods"] or active_ctx["cell_lines"]:
            parts = []
            if active_ctx["methods"]:
                parts.append("methods/assays: " + ", ".join(active_ctx["methods"]))
            if active_ctx["cell_lines"]:
                parts.append("cell lines: " + ", ".join(active_ctx["cell_lines"]))
            method_block = (
                "ACTIVE EXPERIMENTAL CONTEXT (carry forward in the rewrite — "
                "the user is still discussing these even if the current question doesn't repeat them):\n"
                + "\n".join(f"  - {p}" for p in parts)
                + "\n\n"
            )

        user_doc_block = ""
        if user_doc_condensed and user_doc_condensed.strip():
            # Trim to avoid blowing up small_llm context; the condensed doc is
            # usually <1k tokens but cap defensively.
            doc_excerpt = user_doc_condensed.strip()[:3000]
            user_doc_block = (
                "User's uploaded document (extract specific biomedical keywords — "
                "mechanisms, reagents, assay readouts, named regimes — for PubMed search; "
                "avoid generic nouns like 'cell' or 'protein'):\n"
                f"<doc>\n{doc_excerpt}\n</doc>\n\n"
            )

        prompt = f"""{history_context}{method_block}{user_doc_block}Current question: {question}

Produce a single JSON object with FOUR fields describing how to retrieve evidence for this question:

1. "rewritten": A clear, specific restatement of the question for semantic
   search — resolve pronouns using the conversation above, make implied
   terms explicit, keep the core meaning unchanged. One sentence.

   CRITICAL — preserve the ACTIVE EXPERIMENTAL CONTEXT block above:
   - If the user has been discussing "western blot" (or "phospho-AKT",
     "Seahorse", "CRISPR", etc.) in prior turns, the rewrite MUST mention
     that method explicitly — even if the current short follow-up like
     "should I dilute it further?" or "give me a step-by-step plan" omits
     the method name. Without it, the downstream protocol retriever picks
     the WRONG skill file and the answer drifts to a different method.
   - Same for cell line: if HEK293T / HepG2 / etc. was mentioned earlier,
     keep it.
   - Example: "should I dilute it further?" with active method = "western
     blot, phospho-AKT" → rewrite to "Should I further dilute the secondary
     antibody for my phospho-AKT western blot, currently at 1:5000?"

2. "subquestions": A list of 0-3 atomic sub-questions IF the current question
   is COMPOUND (asks multiple distinct things, e.g. "compare A vs B AND what
   about C", "mechanism AND dosing AND toxicity"). Each sub-question should
   be independently answerable and retrieval-friendly. Return [] (empty list)
   if the question is already atomic — DO NOT invent sub-questions for
   simple questions. Rule of thumb: decompose only if the question has
   ≥2 distinct concepts joined by "and/与/以及/还有", OR asks for comparison
   across ≥3 items, OR has multiple question marks.

3. "pubmed_query": The primary PubMed Boolean query (for a simple question,
   this is THE query; for a compound question, this is the query for the
   FIRST sub-question).

4. "pubmed_queries": A list of Boolean PubMed queries — ONE PER SUB-QUESTION
   if you decomposed, OR 1-2 complementary variants of "pubmed_query" if the
   question is atomic (e.g. a mechanism-focused variant + a clinical-outcome
   variant). Always include at least one entry matching "pubmed_query".

   CRITICAL rules for every Boolean query (applies to pubmed_query AND every
   entry in pubmed_queries):

   STRUCTURE (most important):
   - MAX 2-3 AND clauses. More than 3 ANDs almost always returns 0 hits.
   - EVERY AND clause should be a parenthesized OR group of 2-4 synonyms,
     not a single term. PubMed abstracts use varied vocabulary — anchor on
     biological concepts, not on the user's exact wording.
   - Translate the user's wording into STANDARD biomedical terms before
     building the query. Specifically:
        * Method/instrument: expand to common synonyms.
            "Seahorse" → (Seahorse[tiab] OR "extracellular flux"[tiab] OR "XF analyzer"[tiab])
            "FACS" → (flow cytometry[tiab] OR "fluorescence activated cell sorting"[tiab])
            "western blot" → ("western blot"[tiab] OR immunoblot[tiab])
        * Drop instrument model qualifiers: "XF96" / "XF24" / "Mini" — too narrow.
        * Drop assay-protocol full names: "mito stress test" should become
          (mitochondrial respiration[tiab] OR OXPHOS[tiab]).
   - DO NOT use adjective-only OR groups: avoid (low[tiab] OR reduced[tiab]),
     (uniform[tiab] OR consistent[tiab]), (high[tiab] OR elevated[tiab]).
     These add no biological signal and over-restrict the query.

   CONCEPT IDENTIFICATION:
   - Identify the SPECIFIC biological action, mechanism, or failure mode
     being asked about — NOT the user's symptom adjective.
   - Include one method/tool concept + one biological-effect concept.

   EXAMPLES:

     Q: "Seahorse XF96 mito stress test basal OCR is uniformly low — diagnose"
       ✓ (Seahorse[tiab] OR "extracellular flux"[tiab]) AND
         (basal respiration[tiab] OR OCR[tiab] OR "oxygen consumption rate"[tiab]) AND
         (mitochondrial[tiab])
       ✗ Seahorse XF96 mito stress test[tiab] AND (basal OCR[tiab] OR
         oxygen consumption rate[tiab]) AND (low[tiab] OR reduced[tiab]) AND
         (uniform[tiab] OR consistent[tiab])
         # too literal, too many ANDs, adjective-only groups

     Q: "risks of low-pH stripping buffers on western blots"
       ✓ (stripping[tiab] OR strip[tiab]) AND
         (epitope[tiab] OR "protein loss"[tiab] OR denatur*[tiab]) AND
         ("western blot"[tiab] OR immunoblot[tiab])
       ✗ western blot AND antigen      # too broad — pulls IHC papers

     Q: "troubleshoot FACS low event count"
       ✓ ("flow cytometry"[tiab] OR FACS[tiab]) AND
         ("event rate"[tiab] OR clog*[tiab] OR "low count"[tiab])
       ✗ flow cytometry AND troubleshoot   # too vague

   FIELD-TAG / TRUNCATION RULES:
   - Prefer [tiab] field tags. Use truncation (word*) for morphological variants.
   - Avoid generic biology terms (cell, protein, antigen, gene) unless
     paired with a narrowing term — they pull thousands of irrelevant hits.
   - No surrounding quotes or explanation.

CRITICAL JSON FORMATTING RULE:
   - DO NOT put DOUBLE-QUOTED phrases inside the pubmed_query string. Either
     (a) write multi-word phrases as bare words connected by AND, e.g.
         oxygen consumption rate[tiab]
     or (b) join the words with hyphens/underscores so they remain a single
         token, e.g. low-oxygen-consumption[tiab]
   - This is because the JSON value for pubmed_query is itself a quoted
     string, and embedded double quotes break the JSON parser.
   - PubMed treats unquoted multi-word terms as a phrase by default in
     [tiab] anyway, so you do NOT need explicit quotes for phrase matching.

Respond with ONLY the JSON object, no prose, no code fences:
{{"rewritten": "...", "subquestions": [...], "pubmed_query": "...", "pubmed_queries": [...]}}"""

        # APP_DEBUG_QUERY=1 prints the small_llm raw response so we can tell
        # whether (a) the call succeeded but returned malformed JSON,
        # (b) the call returned something parseable but the Boolean query
        # was bad, or (c) the call silently failed and we fell back to the
        # raw user question.
        import os as _os
        _debug_query = _os.getenv("APP_DEBUG_QUERY", "0") == "1"

        response = small_llm.invoke([HumanMessage(content=prompt)])
        raw = response.content.strip() if hasattr(response, "content") else str(response).strip()

        if _debug_query:
            import sys as _sys
            print(f"[query-debug] small_llm raw response (first 600 chars):\n{raw[:600]}",
                  file=_sys.stderr, flush=True)

        # Strip code fences if the model added them despite instructions.
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()

        empty = {"rewritten": question, "pubmed_query": "", "pubmed_queries": [], "subquestions": []}

        def _try_parse(s: str):
            try:
                return json.loads(s)
            except json.JSONDecodeError:
                return None

        parsed = _try_parse(raw)
        if parsed is None:
            # Salvage attempt #1: grab the outermost {...} block.
            match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
            if match:
                parsed = _try_parse(match.group(0))

        if parsed is None:
            # Salvage attempt #2: LLMs (especially when generating PubMed
            # Boolean queries) frequently forget to escape inner double-quotes
            # in scalar JSON string values — e.g. ``"pubmed_query": "term1
            # AND \"phrase\"[tiab]"`` ends up as ``"pubmed_query": "term1
            # AND "phrase"[tiab]"``, which kills the parser.
            #
            # Fix: locate every ``"<key>": "..."`` pair on the same line and
            # escape any internal double-quotes (i.e. quotes that aren't the
            # outermost pair) before retrying. Specifically targets
            # pubmed_query / rewritten — fields that are most likely to
            # carry embedded quotes.
            def _escape_inner_quotes(field: str, blob: str) -> str:
                # Match ``"field": "<value>"`` where value may contain unescaped quotes.
                # Anchor on the next ", or "} or "\n which signal end-of-value.
                pattern = re.compile(
                    r'("' + re.escape(field) + r'"\s*:\s*")(.*?)(",\s*"|"\s*[,}])',
                    re.DOTALL,
                )

                def _fix(m: re.Match) -> str:
                    head, value, tail = m.group(1), m.group(2), m.group(3)
                    fixed_value = value.replace("\\\"", "\x00").replace('"', '\\"').replace("\x00", "\\\"")
                    return f"{head}{fixed_value}{tail}"

                return pattern.sub(_fix, blob, count=1)

            patched = raw
            for fld in ("pubmed_query", "rewritten"):
                patched = _escape_inner_quotes(fld, patched)
            parsed = _try_parse(patched)

        if parsed is None:
            return empty

        rewritten = str(parsed.get("rewritten") or "").strip().strip('"').strip("'").strip()
        pubmed_q = str(parsed.get("pubmed_query") or "").strip().strip('"').strip("'").strip()

        raw_subs = parsed.get("subquestions") or []
        subquestions: list[str] = []
        if isinstance(raw_subs, list):
            for s in raw_subs:
                s_clean = str(s or "").strip().strip('"').strip("'").strip()
                if s_clean and len(s_clean) >= 3:
                    subquestions.append(s_clean)
        subquestions = subquestions[:3]

        raw_qs = parsed.get("pubmed_queries") or []
        pubmed_queries: list[str] = []
        if isinstance(raw_qs, list):
            for q in raw_qs:
                q_clean = str(q or "").strip().strip('"').strip("'").strip()
                if q_clean and q_clean not in pubmed_queries:
                    pubmed_queries.append(q_clean)
        if pubmed_q and pubmed_q not in pubmed_queries:
            pubmed_queries.insert(0, pubmed_q)
        pubmed_queries = pubmed_queries[:4]

        if not rewritten or len(rewritten) < 3:
            rewritten = question
        return {
            "rewritten": rewritten,
            "pubmed_query": pubmed_q,
            "pubmed_queries": pubmed_queries,
            "subquestions": subquestions,
        }
    except Exception as _e:
        # Until now this except silently fell back to the raw question, which
        # masked auth failures and JSON-mode quirks. Surface the error type
        # under APP_DEBUG_QUERY=1 so we can tell when small_llm is broken vs
        # working-but-non-compliant.
        import os as _os
        if _os.getenv("APP_DEBUG_QUERY", "0") == "1":
            import sys as _sys
            print(f"[query-debug] rewrite_query_with_pubmed FAILED: {type(_e).__name__}: {_e}",
                  file=_sys.stderr, flush=True)
        return {"rewritten": question, "pubmed_query": "", "pubmed_queries": [], "subquestions": []}


def classify_question_type(question, small_llm):
    """Legacy classification — no longer used by create_rag_chain.

    Kept for any external callers; returns 'general' without an LLM call.
    """
    return "general"

def get_prompt_template(question_type=None, include_history=False):
    """Return the ChatPromptTemplate used by the RAG chain.

    ``question_type`` and ``include_history`` are accepted for backward
    compatibility but ignored — the prompt structure is now fixed via
    SYSTEM_PROMPT / HUMAN_TEMPLATE.
    """
    return ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", HUMAN_TEMPLATE),
    ])


def create_rag_chain(graph_llm, question=None, small_llm=None, chat_history=None):
    """Create RAG chain for answering questions.

    Args:
        graph_llm: LLM for generating answers (qwen-plus).
        question: User's question (unused, kept for API compat).
        small_llm: Small LLM (unused, kept for API compat).
        chat_history: Conversation history (unused, kept for API compat).

    Returns:
        A runnable chain expecting ``{"evidence": str, "instructions": str,
        "question": str}`` as input.

    .. note::
        Callers that previously passed ``{"context": ..., "question": ...}``
        must now pass ``{"evidence": ..., "instructions": ..., "question": ...}``.
        ``instructions`` can be an empty string when no skill directive applies.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", HUMAN_TEMPLATE),
    ])
    return prompt | graph_llm | StrOutputParser()
