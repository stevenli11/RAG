#!/usr/bin/env python3
"""Quantitative + golden-query regression harness for RAG_local backend.

Runs every YAML case against ``/chat/turn`` and emits BOTH:
  1. The legacy boolean checks (skill hit / instruction regex / dedup /
     citation alignment) — for hard regression gates in CI.
  2. The new quantitative metrics (Recall@K, MRR@K, Hit@K, subq F1,
     coverage rate, faithfulness, latency) — for tracking gradual quality
     improvements across retrieval/prompt changes.

Output is a markdown report with overall + per-bucket aggregations, plus
an optional JSON dump for CI plotting.

Usage:
  python scripts/eval_harness.py --api-url http://127.0.0.1:8001 \
                                 --cases scripts/eval_cases.yaml \
                                 --report eval_report.md \
                                 --save-json eval_report.json
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

import requests
import yaml

# Make ``rag_app`` importable when running this script directly from repo root.
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from rag_app.eval import compute_all  # noqa: E402


# ---------------------------------------------------------------------------
# Legacy boolean checks (kept verbatim from the previous harness — they
# protect against retrieval/prompt regressions that the quantitative metrics
# might smooth over).
# ---------------------------------------------------------------------------


def _norm_title(title: str) -> str:
    return re.sub(r"\s+", " ", (title or "").strip().lower()).rstrip(".")


def _post_json(
    base_url: str,
    route: str,
    payload: Dict[str, Any],
    timeout: int,
    retries: int = 0,
) -> Dict[str, Any]:
    url = f"{base_url.rstrip('/')}{route}"
    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            resp = requests.post(url, json=payload, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except (requests.Timeout, requests.ConnectionError) as e:
            last_exc = e
            if attempt < retries:
                time.sleep(0.25 * (attempt + 1))
                continue
            raise
        except requests.HTTPError as e:
            status = getattr(e.response, "status_code", 0)
            if 500 <= status < 600 and attempt < retries:
                last_exc = e
                time.sleep(0.25 * (attempt + 1))
                continue
            raise
    if last_exc:
        raise last_exc
    raise RuntimeError("unreachable")


def _load_cases(path: Path) -> List[Dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        cases = data.get("cases", [])
    elif isinstance(data, list):
        cases = data
    else:
        cases = []
    if not isinstance(cases, list):
        raise ValueError("golden cases must be a list or {cases: [...]} structure")
    return [c for c in cases if isinstance(c, dict)]


def _skill_hit_ok(debug_resp: Dict[str, Any], patterns: List[str]) -> Tuple[bool, str]:
    if not patterns:
        return True, "no expected_skill_patterns configured"
    hay = [*(debug_resp.get("protocol_skill_files") or []), *(debug_resp.get("source_labels") or [])]
    low_hay = [h.lower() for h in hay]
    misses = [p for p in patterns if not any(p.lower().strip() in h for h in low_hay)]
    if misses:
        return False, f"missing expected skill/source patterns: {misses}"
    return True, "expected skill/source patterns matched"


def _instructions_ok(debug_resp: Dict[str, Any], regex_list: List[str]) -> Tuple[bool, str]:
    if not regex_list:
        return True, "no instruction_regex configured"
    text = str(debug_resp.get("instructions") or "")
    misses = [pat for pat in regex_list if not re.search(pat, text, flags=re.IGNORECASE | re.MULTILINE)]
    if misses:
        return False, f"instructions missing regex: {misses}"
    return True, "instruction regex matched"


def _pubmed_dedup_ok(debug_resp: Dict[str, Any]) -> Tuple[bool, str]:
    titles = [str(t or "") for t in (debug_resp.get("pubmed_titles") or []) if str(t or "").strip()]
    norm = [_norm_title(t) for t in titles]
    uniq = set(norm)
    if len(uniq) == len(norm):
        return True, f"dedup ok ({len(norm)} unique titles)"
    return False, f"dedup failed ({len(norm) - len(uniq)} duplicate title(s))"


def _citation_pmid_ok(chat_resp: Dict[str, Any], require_citations: bool) -> Tuple[bool, str]:
    refs_all = chat_resp.get("references_all") or []
    refs_used = chat_resp.get("references_used") or []
    all_pmids = {str(a.get("pmid") or "").strip() for a in refs_all if str(a.get("pmid") or "").strip()}
    used_pmids = {str(a.get("pmid") or "").strip() for a in refs_used if str(a.get("pmid") or "").strip()}
    if require_citations and not used_pmids:
        return False, "no cited PMID in answer while require_citations=true"
    rogue = sorted(p for p in used_pmids if p not in all_pmids)
    if rogue:
        return False, f"cited PMID not in retrieved top-K: {rogue}"
    return True, f"citation PMID alignment ok (used={len(used_pmids)}, retrieved={len(all_pmids)})"


# ---------------------------------------------------------------------------
# Per-case execution
# ---------------------------------------------------------------------------


def run_case(
    base_url: str,
    case: Dict[str, Any],
    timeout: int,
    retries: int = 0,
    k_retrieval: int = 10,
) -> Dict[str, Any]:
    q = str(case.get("query") or case.get("question") or "").strip()
    if not q:
        return {
            "id": case.get("id", "unknown"),
            "pass": False,
            "checks": [{"name": "query", "ok": False, "detail": "empty query"}],
            "metrics": {},
        }

    retrieval_k = int(case.get("retrieval_k", 12))
    pubmed_max = int(case.get("pubmed_max_results", 20))
    max_chars = int(case.get("max_context_chars", 8000))

    # Hit /debug/retrieval first to grab skill/instruction state for the
    # legacy boolean checks; then /chat/turn for the answer + metrics.
    debug_payload = {
        "question": q,
        "retrieval_k": retrieval_k,
        "pubmed_max_results": pubmed_max,
        "max_context_chars": max_chars,
    }
    try:
        debug_resp = _post_json(base_url, "/debug/retrieval", debug_payload, timeout=timeout, retries=retries)
    except Exception as e:
        debug_resp = {"_debug_error": str(e)}

    chat_payload = {
        "question": q,
        "chat_history": [],
        "retrieval_k": retrieval_k,
        "pubmed_max_results": pubmed_max,
        "max_context_chars": max_chars,
        "generate_followups": False,
    }
    chat_resp = _post_json(base_url, "/chat/turn", chat_payload, timeout=timeout, retries=retries)

    # ---- Legacy boolean checks ---------------------------------------
    checks: List[Dict[str, Any]] = []
    if "_debug_error" not in debug_resp:
        ok1, d1 = _skill_hit_ok(debug_resp, list(case.get("expected_skill_patterns") or []))
        checks.append({"name": "expected_skill_hit", "ok": ok1, "detail": d1})
        ok2, d2 = _instructions_ok(debug_resp, list(case.get("instruction_regex") or []))
        checks.append({"name": "instruction_regex", "ok": ok2, "detail": d2})
        ok3, d3 = _pubmed_dedup_ok(debug_resp)
        checks.append({"name": "pubmed_dedup", "ok": ok3, "detail": d3})
    ok4, d4 = _citation_pmid_ok(chat_resp, bool(case.get("require_citations", False)))
    checks.append({"name": "citation_pmid_alignment", "ok": ok4, "detail": d4})

    case_pass = all(c["ok"] for c in checks)

    # ---- Quantitative metrics ----------------------------------------
    metrics = compute_all(case=case, response=chat_resp, k_retrieval=k_retrieval)

    return {
        "id": case.get("id", q[:50]),
        "tier": case.get("tier", "uncategorized"),
        "bucket": case.get("bucket", "uncategorized"),
        "query": q,
        "pass": case_pass,
        "checks": checks,
        "metrics": metrics,
        "intent": chat_resp.get("intent"),
        "rewritten": chat_resp.get("rewritten_question", ""),
        "subquestions": chat_resp.get("subquestions") or [],
        "protocol_skill_files": chat_resp.get("protocol_skill_files") or [],
        "rerank_status": chat_resp.get("rerank_status") or {},
        "cited_count": len(chat_resp.get("references_used") or []),
        "retrieved_count": len(chat_resp.get("references_all") or []),
    }


# ---------------------------------------------------------------------------
# Aggregation + report rendering
# ---------------------------------------------------------------------------


def _aggregate_metrics(results: List[Dict[str, Any]]) -> Dict[str, float]:
    """Mean across cases for each metric key. Empty dict on no results."""
    if not results:
        return {}
    keys: set[str] = set()
    for r in results:
        keys.update((r.get("metrics") or {}).keys())
    out: Dict[str, float] = {}
    for k in sorted(keys):
        vals = [float((r.get("metrics") or {}).get(k) or 0.0) for r in results]
        out[k] = statistics.mean(vals) if vals else 0.0
    # Add p95 latency (more useful than mean for tails).
    lat = [float((r.get("metrics") or {}).get("latency_total") or 0.0) for r in results]
    lat_sorted = sorted(lat)
    if len(lat_sorted) >= 1:
        idx = max(0, int(len(lat_sorted) * 0.95) - 1) if len(lat_sorted) >= 20 else len(lat_sorted) - 1
        out["latency_p95"] = lat_sorted[idx]
    return out


def _render_markdown_report(
    results: List[Dict[str, Any]],
    overall: Dict[str, float],
    per_bucket: Dict[str, Dict[str, float]],
    per_tier: Dict[str, Dict[str, float]] | None = None,
) -> str:
    lines: List[str] = []
    lines.append("# RAG_local Eval Report")
    lines.append("")
    lines.append(f"_Generated at {time.strftime('%Y-%m-%d %H:%M:%S')}_  ")
    lines.append(f"_Cases: {len(results)}_")
    lines.append("")

    # Overall metrics
    lines.append("## Overall metrics")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    for k, v in overall.items():
        if "latency" in k:
            lines.append(f"| {k} | {v:.2f}s |")
        else:
            lines.append(f"| {k} | {v:.3f} |")
    lines.append("")

    # Per-tier metrics (more important than per-bucket — separates the
    # "actively-optimized methods" from "skill exists but not optimized").
    if per_tier:
        lines.append("## Per-tier metrics")
        lines.append("")
        tier_names = sorted(per_tier.keys())
        all_keys = sorted({k for t in per_tier.values() for k in t.keys()})
        header = "| Metric | " + " | ".join(tier_names) + " |"
        sep = "|---|" + "---|" * len(tier_names)
        lines.append(header)
        lines.append(sep)
        for k in all_keys:
            row = [k]
            for t in tier_names:
                v = per_tier[t].get(k, 0.0)
                row.append(f"{v:.2f}s" if "latency" in k else f"{v:.3f}")
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")

    # Per-bucket metrics
    if per_bucket:
        lines.append("## Per-bucket metrics")
        lines.append("")
        bucket_names = sorted(per_bucket.keys())
        all_keys = sorted({k for b in per_bucket.values() for k in b.keys()})
        header = "| Metric | " + " | ".join(bucket_names) + " |"
        sep = "|---|" + "---|" * len(bucket_names)
        lines.append(header)
        lines.append(sep)
        for k in all_keys:
            row = [k]
            for b in bucket_names:
                v = per_bucket[b].get(k, 0.0)
                row.append(f"{v:.2f}s" if "latency" in k else f"{v:.3f}")
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")

    # Runtime errors first — these are NOT quality regressions, they're plumbing
    # bugs. Surfacing them at the top of the report so they don't get buried
    # under 'failed boolean checks' (which conflates "answer was wrong" with
    # "case never even ran").
    error_cases = [r for r in results if r.get("runtime_error")]
    if error_cases:
        lines.append(f"## ⚠️ Runtime errors: {len(error_cases)}/{len(results)} cases never completed")
        lines.append("")
        # Group by error type for quick triage.
        from collections import Counter as _Counter
        error_types = _Counter(
            (r.get("runtime_error") or "").split(":", 1)[0]
            for r in error_cases
        )
        lines.append("Error type distribution:")
        for et, n in error_types.most_common():
            lines.append(f"- `{et}`: {n}")
        lines.append("")
        lines.append("Per-case detail:")
        for r in error_cases:
            lines.append(f"- **{r['id']}** ({r.get('tier', '?')}/{r.get('bucket', '?')}): `{(r.get('runtime_error') or '')[:200]}`")
        lines.append("")

    # Boolean check pass rate
    passed = sum(1 for r in results if r.get("pass"))
    total = len(results)
    lines.append(f"## Boolean checks: {passed}/{total} cases pass all gates")
    lines.append("")
    failed = [r for r in results if not r.get("pass")]
    if failed:
        lines.append("### Failures")
        for r in failed:
            lines.append(f"- **{r['id']}** ({r.get('bucket', '?')}) — `{r.get('query', '')[:80]}`")
            for chk in r.get("checks", []):
                if not chk.get("ok"):
                    lines.append(f"  - ✗ {chk['name']}: {chk['detail']}")
        lines.append("")

    # Per-case summary table
    lines.append("## Per-case summary")
    lines.append("")
    lines.append("| ID | Tier | Bucket | Pass | Recall@10 | MRR@10 | Faithful | Subq F1 | Coverage | Lat |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for r in results:
        m = r.get("metrics") or {}
        lines.append(
            "| {id} | {t} | {b} | {p} | {recall:.2f} | {mrr:.2f} | {faith:.2f} | {f1:.2f} | {cov:.2f} | {lat:.1f}s |".format(
                id=r.get("id", "?"),
                t=r.get("tier", "?"),
                b=r.get("bucket", "?"),
                p="✓" if r.get("pass") else "✗",
                recall=m.get("recall@10", 0.0),
                mrr=m.get("mrr@10", 0.0),
                faith=m.get("faithfulness", 0.0),
                f1=m.get("subq_f1", 0.0),
                cov=m.get("coverage_rate", 0.0),
                lat=m.get("latency_total", 0.0),
            )
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run RAG_local quantitative eval harness against FastAPI backend.")
    parser.add_argument("--api-url", default="http://127.0.0.1:8001", help="FastAPI base URL")
    parser.add_argument(
        "--cases",
        default=str(Path(__file__).resolve().parent / "core_cases.yaml"),
        help="Path to golden cases YAML (default: core_cases.yaml — methods on the allow-list)",
    )
    parser.add_argument(
        "--cases-extra",
        default="",
        help="Optional second YAML file to merge in (typically extended_cases.yaml). "
             "Use this to also exercise methods that have skill files but are not yet "
             "on the protocol_retrieval allow-list.",
    )
    parser.add_argument("--timeout", type=int, default=180, help="Per-request timeout in seconds")
    parser.add_argument("--retries", type=int, default=1, help="Retry on read timeout / 5xx")
    parser.add_argument("--k", type=int, default=10, help="Cutoff K for Recall@K / MRR@K / Hit@K")
    parser.add_argument("--save-json", default="", help="Optional path to save full JSON report")
    parser.add_argument("--report", default="", help="Optional path to save markdown report")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any boolean check fails")
    parser.add_argument(
        "--only",
        default="",
        help="Comma-separated case IDs to run (filters to subset). Useful for re-running just the failed cases.",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop after the first 3 consecutive runtime errors (lets you investigate API/backend issues quickly).",
    )
    args = parser.parse_args()

    cases_path = Path(args.cases)
    if not cases_path.exists():
        print(f"[ERROR] Cases file not found: {cases_path}", file=sys.stderr)
        return 2

    cases = _load_cases(cases_path)
    print(f"[INFO] Loaded {len(cases)} case(s) from {cases_path.name}")

    if args.cases_extra:
        extra_path = Path(args.cases_extra)
        if not extra_path.exists():
            print(f"[ERROR] Extra cases file not found: {extra_path}", file=sys.stderr)
            return 2
        extra_cases = _load_cases(extra_path)
        # Dedup by id — primary file wins on collision so users can override
        # an extended case by copying it into core with edits.
        existing_ids = {c.get("id") for c in cases if c.get("id")}
        added = 0
        for c in extra_cases:
            if c.get("id") in existing_ids:
                continue
            cases.append(c)
            existing_ids.add(c.get("id"))
            added += 1
        print(f"[INFO] Merged {added} additional case(s) from {extra_path.name} (skipped {len(extra_cases) - added} duplicate id(s))")

    if not cases:
        print("[ERROR] No eval cases loaded.", file=sys.stderr)
        return 2

    if args.only:
        wanted = {x.strip() for x in args.only.split(",") if x.strip()}
        cases = [c for c in cases if str(c.get("id", "")) in wanted]
        if not cases:
            print(f"[ERROR] --only filter matched no cases: {sorted(wanted)}", file=sys.stderr)
            return 2
        print(f"[INFO] --only filter active: running {len(cases)} case(s): {sorted(wanted)}")

    results: List[Dict[str, Any]] = []
    consecutive_errors = 0
    for idx, case in enumerate(cases, start=1):
        cid = str(case.get("id") or f"case_{idx}")
        print(f"\n[{idx:02d}/{len(cases):02d}] {cid}")
        try:
            res = run_case(args.api_url, case, timeout=args.timeout, retries=args.retries, k_retrieval=args.k)
        except Exception as e:
            # Runtime errors (HTTP, schema validation, etc.) used to be silent —
            # we kept ``tier`` blank and never printed the exception, which made
            # 9 cases at a stretch silently flatline to 0 in the previous run
            # without any indication of whether it was a backend crash, a
            # rate-limit, or a per-case bug. Now: preserve tier/bucket from the
            # fixture and surface the exception type + truncated message both
            # to stdout AND into the per-case checks list so it shows up in
            # the markdown failure section.
            err_repr = f"{type(e).__name__}: {e}"
            res = {
                "id": cid,
                "tier": case.get("tier", "uncategorized"),
                "bucket": case.get("bucket", "uncategorized"),
                "pass": False,
                "checks": [{"name": "runtime", "ok": False, "detail": err_repr[:500]}],
                "metrics": {},
                "runtime_error": err_repr,
            }
        results.append(res)
        m = res.get("metrics") or {}
        status = "PASS" if res.get("pass") else "FAIL"
        if res.get("runtime_error"):
            # Prominent error line so a chain of failures is obvious in real time.
            print(f"  ERROR {res['runtime_error'][:200]}")
            consecutive_errors += 1
            if args.fail_fast and consecutive_errors >= 3:
                print(f"\n[FAIL-FAST] {consecutive_errors} consecutive runtime errors — aborting. "
                      f"Likely backend/API issue (rate-limit, timeout, schema mismatch). "
                      f"Investigate before re-running the full suite.", file=sys.stderr)
                break
        else:
            consecutive_errors = 0
            print(f"  {status}  R@{args.k}={m.get(f'recall@{args.k}', 0):.2f}  MRR={m.get(f'mrr@{args.k}', 0):.2f}  "
                  f"faith={m.get('faithfulness', 0):.2f}  cov={m.get('coverage_rate', 0):.2f}  "
                  f"lat={m.get('latency_total', 0):.1f}s")

    # Aggregate
    overall = _aggregate_metrics(results)
    per_bucket: Dict[str, Dict[str, float]] = {}
    by_bucket: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in results:
        by_bucket[r.get("bucket", "uncategorized")].append(r)
    for b, rs in by_bucket.items():
        per_bucket[b] = _aggregate_metrics(rs)

    per_tier: Dict[str, Dict[str, float]] = {}
    by_tier: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in results:
        by_tier[r.get("tier", "uncategorized")].append(r)
    for t, rs in by_tier.items():
        per_tier[t] = _aggregate_metrics(rs)

    print("\n=== Overall ===")
    for k, v in overall.items():
        print(f"  {k}: {v:.3f}" if "latency" not in k else f"  {k}: {v:.2f}s")

    if per_tier:
        print("\n=== Per-tier ===")
        for tier_name in sorted(per_tier.keys()):
            metrics = per_tier[tier_name]
            n = len(by_tier[tier_name])
            print(f"  [{tier_name}] (n={n})")
            for k in ("recall@10", "mrr@10", "faithfulness", "coverage_rate", "subq_f1", "latency_total"):
                v = metrics.get(k, 0.0)
                fmt = f"{v:.2f}s" if "latency" in k else f"{v:.3f}"
                print(f"    {k}: {fmt}")

    if args.report:
        md = _render_markdown_report(results, overall, per_bucket, per_tier=per_tier)
        Path(args.report).write_text(md, encoding="utf-8")
        print(f"\nMarkdown report → {args.report}")

    if args.save_json:
        payload = {
            "overall": overall,
            "per_tier": per_tier,
            "per_bucket": per_bucket,
            "results": results,
        }
        Path(args.save_json).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"JSON report → {args.save_json}")

    passed = sum(1 for r in results if r.get("pass"))
    total = len(results)
    runtime_errors = sum(1 for r in results if r.get("runtime_error"))
    print(f"\nBoolean checks: {passed}/{total} passed")
    if runtime_errors:
        # Distinguish "ran but answered poorly" from "never ran" so we don't
        # treat plumbing failures as quality regressions.
        print(f"⚠️  Runtime errors: {runtime_errors}/{total} cases (these are plumbing bugs, not quality regressions)")
        print("   Investigate before trusting overall metrics — error breakdown in markdown report.")
    if args.strict and passed < total:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
