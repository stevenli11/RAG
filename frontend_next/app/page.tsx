"use client";

import {
  FormEvent,
  KeyboardEvent,
  ReactNode,
  startTransition,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

type RefItem = {
  pmid?: string;
  title?: string;
  abstract?: string;
  journal?: string;
  year?: string;
  authors?: string[];
};

type Turn = {
  user: string;
  answer: string;
  intent?: string;
  rewritten?: string;
  subquestions: string[];
  sourcesTopK: string[];
  protocolSkillFiles: string[];
  qualityCounts: Record<string, number>;
  rerankStatus: Record<string, unknown>;
  referencesUsed: RefItem[];
  referencesAll: RefItem[];
  citationVerdicts: CiteVerdict[];
  followups: string[];
  error?: string;
};

type CiteVerdict = {
  n: number;
  status: "supported" | "partial" | "unsupported";
  reason: string;
  claim: string;
};

type InlineCtx = {
  numberedRefMap: Map<number, RefItem>;
  verdictMap?: Map<number, CiteVerdict["status"]>;
  verdictReasonMap?: Map<number, string>;
};

type AttachedDoc = {
  session_id: string;
  filename: string;
  token_estimate: number;
  condensed_preview: string;
};

const STORAGE_KEYS = {
  history: "rag.chat_history.v1",
  doc: "rag.attached_doc.v1",
} as const;

const SAMPLE_PROMPTS = [
  "How should I troubleshoot unexpectedly high fluorescence after transfection?",
  "What controls do I need to validate a new flow cytometry gating strategy?",
  "Compare lentiviral and AAV delivery for stable neuronal expression.",
  "How would you structure a CRISPR knockout workflow for TP53 in HeLa cells?",
];

const STAGE_COPY: Record<string, string> = {
  ready: "Ready",
  connecting: "Connecting",
  routing: "Interpreting question",
  retrieving: "Retrieving evidence",
  generating: "Drafting answer",
  done: "Answer complete",
  error: "Run interrupted",
};

function IconFlask() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 3h6" />
      <path d="M10 3v5l-5.5 9.7A2 2 0 0 0 6.24 21h11.52a2 2 0 0 0 1.74-3.03L14 8V3" />
      <path d="M8.8 14h6.4" />
    </svg>
  );
}

function IconSend() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 2 11 13" />
      <path d="m22 2-7 20-4-9-9-4Z" />
    </svg>
  );
}

function IconAttach() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
      <path d="m21.44 11.05-8.49 8.49a6 6 0 0 1-8.49-8.49l9.19-9.2a4 4 0 1 1 5.66 5.66l-9.2 9.2a2 2 0 1 1-2.83-2.83l8.49-8.48" />
    </svg>
  );
}

function IconArrowUpRight() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M7 17 17 7" />
      <path d="M7 7h10v10" />
    </svg>
  );
}

function IconPulse() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 12h-4l-3 7-4-14-3 7H2" />
    </svg>
  );
}

function IconFile() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <path d="M14 2v6h6" />
    </svg>
  );
}

function parseSseFrame(frame: string): { event: string; data: unknown } | null {
  const lines = frame.split(/\r?\n/);
  let event = "message";
  const dataLines: string[] = [];

  for (const raw of lines) {
    const line = raw.trimEnd();
    if (!line || line.startsWith(":")) continue;
    if (line.startsWith("event:")) event = line.slice(6).trim();
    if (line.startsWith("data:")) dataLines.push(line.slice(5).trim());
  }

  if (dataLines.length === 0) return null;

  try {
    return { event, data: JSON.parse(dataLines.join("\n")) };
  } catch {
    return { event, data: dataLines.join("\n") };
  }
}

function renderInline(text: string, ctx: InlineCtx): ReactNode[] {
  const nodes: ReactNode[] = [];
  const tokenRe = /(\[internal protocol(?:[;:]?\s*\d+(?:\s*,\s*\d+)*)?\]|\[\d+(?:\s*,\s*\d+)*\]|PMID[:\s]*\d+|\*\*[^*]+\*\*|`[^`]+`)/g;
  let last = 0;
  let key = 0;

  const pushPlain = (value: string) => {
    if (!value) return;
    nodes.push(<span key={`plain-${key++}`}>{value}</span>);
  };

  let match = tokenRe.exec(text);
  while (match) {
    const [token] = match;
    const start = match.index;
    pushPlain(text.slice(last, start));

    if (/^\[internal protocol[;:\s\d,]*\]$/i.test(token)) {
      const nums = token.match(/\d+/g) || [];
      nodes.push(
        <span key={`prov-${key++}`} className="cite-internal" title="Internal protocol">
          [internal protocol]
        </span>,
      );
      for (const nStr of nums) {
        const n = Number(nStr);
        const ref = ctx.numberedRefMap.get(n);
        nodes.push(
          ref?.pmid ? (
            <span key={`cite-embed-${key++}`} className={`cite-wrap cite-${ctx.verdictMap?.get(n) || "unverified"}`}>
              <a
                href={`https://pubmed.ncbi.nlm.nih.gov/${ref.pmid}/`}
                target="_blank"
                rel="noreferrer"
                className="cite-link"
                tabIndex={0}
              >
                [{n}]
              </a>
              <span role="tooltip" className="cite-pop">
                <strong>{ref.title || `PMID ${ref.pmid}`}</strong>
                {ref.abstract && <em>{ref.abstract.slice(0, 180)}{ref.abstract.length > 180 ? "…" : ""}</em>}
                <small>{[ref.journal, ref.year].filter(Boolean).join(" · ")}</small>
                {ctx.verdictMap?.get(n) && (
                  <small className={`cite-verdict cite-verdict-${ctx.verdictMap.get(n)}`}>
                    {verdictLabel(ctx.verdictMap.get(n)!)}
                    {ctx.verdictReasonMap?.get(n) ? ` · ${ctx.verdictReasonMap.get(n)}` : ""}
                  </small>
                )}
              </span>
            </span>
          ) : (
            <span key={`cite-miss-${key++}`} className="cite-missing">
              [{n}]
            </span>
          ),
        );
      }
    } else if (/^\[\d+(?:\s*,\s*\d+)*\]$/.test(token)) {
      const nums = (token.match(/\d+/g) || []).map(Number);
      nums.forEach((n, idx) => {
        const ref = ctx.numberedRefMap.get(n);
        const textChunk = `${idx === 0 ? "[" : ""}${n}${idx === nums.length - 1 ? "]" : ", "}`;
        nodes.push(
          ref?.pmid ? (
            <span key={`cite-${key++}`} className={`cite-wrap cite-${ctx.verdictMap?.get(n) || "unverified"}`}>
              <a
                href={`https://pubmed.ncbi.nlm.nih.gov/${ref.pmid}/`}
                target="_blank"
                rel="noreferrer"
                className="cite-link"
                tabIndex={0}
              >
                {textChunk}
              </a>
              <span role="tooltip" className="cite-pop">
                <strong>{ref.title || `PMID ${ref.pmid}`}</strong>
                {ref.abstract && <em>{ref.abstract.slice(0, 180)}{ref.abstract.length > 180 ? "…" : ""}</em>}
                <small>{[ref.journal, ref.year].filter(Boolean).join(" · ")}</small>
                {ctx.verdictMap?.get(n) && (
                  <small className={`cite-verdict cite-verdict-${ctx.verdictMap.get(n)}`}>
                    {verdictLabel(ctx.verdictMap.get(n)!)}
                    {ctx.verdictReasonMap?.get(n) ? ` · ${ctx.verdictReasonMap.get(n)}` : ""}
                  </small>
                )}
              </span>
            </span>
          ) : (
            <span key={`cite-missing-${key++}`} className="cite-missing">
              {textChunk}
            </span>
          ),
        );
      });
    } else if (/^PMID[:\s]*\d+$/i.test(token)) {
      const pmid = token.replace(/\D+/g, "");
      nodes.push(
        <a
          key={`pmid-${key++}`}
          href={`https://pubmed.ncbi.nlm.nih.gov/${pmid}/`}
          target="_blank"
          rel="noreferrer"
          className="cite-link"
        >
          {token}
        </a>,
      );
    } else if (/^\*\*[^*]+\*\*$/.test(token)) {
      nodes.push(<strong key={`bold-${key++}`}>{token.slice(2, -2)}</strong>);
    } else if (/^`[^`]+`$/.test(token)) {
      nodes.push(<code key={`code-${key++}`}>{token.slice(1, -1)}</code>);
    } else {
      pushPlain(token);
    }

    last = start + token.length;
    match = tokenRe.exec(text);
  }

  pushPlain(text.slice(last));
  return nodes;
}

function renderAnswerBlocks(answer: string, ctx: InlineCtx): ReactNode {
  if (!answer.trim()) return null;
  const lines = answer.replace(/\r/g, "").split("\n");
  const blocks: ReactNode[] = [];
  let i = 0;

  while (i < lines.length) {
    const raw = lines[i] ?? "";
    const trimmed = raw.trim();

    if (!trimmed) {
      i++;
      continue;
    }

    if (trimmed.startsWith("```")) {
      i++;
      const code: string[] = [];
      while (i < lines.length && !lines[i].trim().startsWith("```")) {
        code.push(lines[i]);
        i++;
      }
      if (i < lines.length) i++;
      blocks.push(
        <pre key={`code-${i}`}>
          <code>{code.join("\n")}</code>
        </pre>,
      );
      continue;
    }

    if (/^#{1,3}\s+/.test(trimmed)) {
      const level = Math.min(3, trimmed.match(/^#+/)?.[0].length ?? 1);
      const content = trimmed.replace(/^#{1,3}\s+/, "");
      if (level === 1) blocks.push(<h2 key={`h-${i}`}>{renderInline(content, ctx)}</h2>);
      if (level === 2) blocks.push(<h3 key={`h-${i}`}>{renderInline(content, ctx)}</h3>);
      if (level === 3) blocks.push(<h4 key={`h-${i}`}>{renderInline(content, ctx)}</h4>);
      i++;
      continue;
    }

    if (trimmed.startsWith("|") && trimmed.endsWith("|") && i + 1 < lines.length) {
      const nextLine = (lines[i + 1] ?? "").trim();
      const isSeparator = /^\|[\s:|\-]+\|$/.test(nextLine) && nextLine.includes("-");
      if (isSeparator) {
        const splitRow = (row: string) => row.replace(/^\||\|$/g, "").split("|").map((cell) => cell.trim());
        const headers = splitRow(trimmed);
        i += 2;
        const bodyRows: string[][] = [];
        while (i < lines.length) {
          const rowTrim = lines[i].trim();
          if (!rowTrim.startsWith("|") || !rowTrim.endsWith("|")) break;
          bodyRows.push(splitRow(rowTrim));
          i++;
        }
        blocks.push(
          <div key={`tbl-${i}`} className="md-table-wrap">
            <table className="md-table">
              <thead>
                <tr>
                  {headers.map((header, idx) => (
                    <th key={`th-${idx}`}>{renderInline(header, ctx)}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {bodyRows.map((row, rowIdx) => (
                  <tr key={`tr-${rowIdx}`}>
                    {row.map((cell, cellIdx) => (
                      <td key={`td-${rowIdx}-${cellIdx}`}>{renderInline(cell, ctx)}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>,
        );
        continue;
      }
    }

    if (/^\d+\.\s+/.test(trimmed)) {
      const items: string[] = [];
      const firstMatch = trimmed.match(/^(\d+)\.\s+/);
      const startNum = firstMatch ? Number(firstMatch[1]) : 1;
      while (i < lines.length) {
        const current = lines[i].trim();
        if (/^\d+\.\s+/.test(current)) {
          items.push(current.replace(/^\d+\.\s+/, ""));
          i++;
          continue;
        }
        if (current === "") {
          let j = i + 1;
          while (j < lines.length && lines[j].trim() === "") j++;
          if (j < lines.length && /^\d+\.\s+/.test(lines[j].trim())) {
            i = j;
            continue;
          }
        }
        break;
      }
      blocks.push(
        <ol key={`ol-${i}`} start={startNum}>
          {items.map((item, idx) => (
            <li key={`oli-${idx}`}>{renderInline(item, ctx)}</li>
          ))}
        </ol>,
      );
      continue;
    }

    if (/^[-*]\s+/.test(trimmed)) {
      const items: string[] = [];
      while (i < lines.length && /^[-*]\s+/.test(lines[i].trim())) {
        items.push(lines[i].trim().replace(/^[-*]\s+/, ""));
        i++;
      }
      blocks.push(
        <ul key={`ul-${i}`}>
          {items.map((item, idx) => (
            <li key={`uli-${idx}`}>{renderInline(item, ctx)}</li>
          ))}
        </ul>,
      );
      continue;
    }

    blocks.push(<p key={`p-${i}`}>{renderInline(trimmed, ctx)}</p>);
    i++;
  }

  return <>{blocks}</>;
}

function firstLine(text: string, max = 48): string {
  const value = text.replace(/\s+/g, " ").trim();
  return value.length <= max ? value : `${value.slice(0, max)}…`;
}

function shortSourceName(path: string): string {
  const base = path.split("/").pop() || path;
  return base.length > 26 ? `${base.slice(0, 24)}…` : base;
}

function verdictLabel(status: CiteVerdict["status"]): string {
  switch (status) {
    case "supported":
      return "✓ Supported";
    case "partial":
      return "△ Partial";
    case "unsupported":
      return "✗ Unsupported";
  }
}

function intentTone(intent?: string): string {
  switch ((intent || "").toLowerCase()) {
    case "wet-lab":
      return "wetlab";
    case "clinical":
      return "clinical";
    case "hybrid":
      return "hybrid";
    default:
      return "general";
  }
}

export default function Page() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<Turn[]>([]);
  const [status, setStatus] = useState("ready");
  const [backendStatus, setBackendStatus] = useState<"checking" | "ok" | "down">("checking");
  const [activeTurn, setActiveTurn] = useState<number>(-1);
  const [showEvidencePanel, setShowEvidencePanel] = useState(true);
  const [attachedDoc, setAttachedDoc] = useState<AttachedDoc | null>(null);
  const [attachLoading, setAttachLoading] = useState(false);
  const [attachError, setAttachError] = useState<string | null>(null);
  const [hydrated, setHydrated] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const currentTurn = activeTurn >= 0 ? history[activeTurn] : undefined;
  const statusLabel = STAGE_COPY[status] ?? status;
  const retrievedSourcesCount = currentTurn?.sourcesTopK.length ?? 0;
  const citedCount = currentTurn?.referencesUsed.length ?? 0;
  const totalRefs = currentTurn?.referencesAll.length ?? 0;

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      const rawHist = window.localStorage.getItem(STORAGE_KEYS.history);
      if (rawHist) {
        const parsed = JSON.parse(rawHist) as Turn[];
        if (Array.isArray(parsed) && parsed.length > 0) {
          setHistory(parsed);
          setActiveTurn(parsed.length - 1);
        }
      }
      const rawDoc = window.localStorage.getItem(STORAGE_KEYS.doc);
      if (rawDoc) {
        const parsedDoc = JSON.parse(rawDoc) as AttachedDoc;
        if (parsedDoc && parsedDoc.session_id) setAttachedDoc(parsedDoc);
      }
    } catch {
      // corrupt storage — ignore
    }
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (!hydrated || typeof window === "undefined") return;
    try {
      window.localStorage.setItem(STORAGE_KEYS.history, JSON.stringify(history));
    } catch {}
  }, [history, hydrated]);

  useEffect(() => {
    if (!hydrated || typeof window === "undefined") return;
    try {
      if (attachedDoc) {
        window.localStorage.setItem(STORAGE_KEYS.doc, JSON.stringify(attachedDoc));
      } else {
        window.localStorage.removeItem(STORAGE_KEYS.doc);
      }
    } catch {}
  }, [attachedDoc, hydrated]);

  function clearConversation() {
    setHistory([]);
    setActiveTurn(-1);
    setStatus("ready");
    setAttachedDoc(null);
    setAttachError(null);
    if (typeof window !== "undefined") {
      try {
        window.localStorage.removeItem(STORAGE_KEYS.history);
        window.localStorage.removeItem(STORAGE_KEYS.doc);
      } catch {}
    }
  }

  useEffect(() => {
    let cancelled = false;

    async function checkHealth() {
      try {
        const resp = await fetch("/api/healthz", { cache: "no-store" });
        if (!cancelled) setBackendStatus(resp.ok ? "ok" : "down");
      } catch {
        if (!cancelled) setBackendStatus("down");
      }
    }

    checkHealth();
    const timer = setInterval(checkHealth, 15000);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, []);

  function autoResizeTextarea() {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 220)}px`;
  }

  function pushTurnPatch(patch: (turn: Turn) => Turn) {
    startTransition(() => {
      setHistory((prev) => {
        if (prev.length === 0) return prev;
        const next = [...prev];
        next[next.length - 1] = patch(next[next.length - 1]);
        return next;
      });
    });
  }

  async function runStream(input: string) {
    setLoading(true);
    setStatus("connecting");

    const nextTurn: Turn = {
      user: input,
      answer: "",
      subquestions: [],
      sourcesTopK: [],
      protocolSkillFiles: [],
      qualityCounts: {},
      rerankStatus: {},
      referencesUsed: [],
      referencesAll: [],
      citationVerdicts: [],
      followups: [],
    };

    setHistory((prev) => {
      const next = [...prev, nextTurn];
      startTransition(() => setActiveTurn(next.length - 1));
      return next;
    });

    try {
      const priorTurns = history
        .filter((turn) => turn.answer && !turn.error)
        .slice(-5)
        .map((turn) => ({ user: turn.user, assistant: turn.answer }));

      const resp = await fetch("/api/chat/turn/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: input,
          chat_history: priorTurns,
          retrieval_k: 12,
          pubmed_max_results: 20,
          max_context_chars: 8000,
          generate_followups: true,
          session_id: attachedDoc?.session_id ?? null,
        }),
      });

      if (!resp.ok || !resp.body) throw new Error(`HTTP ${resp.status}`);

      const reader = resp.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";
      let done = false;
      let seenAnyEvent = false;
      const startedAt = Date.now();

      while (!done) {
        const chunk = await reader.read();
        done = chunk.done;
        buffer += decoder.decode(chunk.value || new Uint8Array(), { stream: !done });

        const frameSep = /\r?\n\r?\n/g;
        let match = frameSep.exec(buffer);
        while (match) {
          const cut = match.index;
          const sepLen = match[0].length;
          const frame = buffer.slice(0, cut);
          buffer = buffer.slice(cut + sepLen);
          frameSep.lastIndex = 0;

          const evt = parseSseFrame(frame);
          if (evt) {
            seenAnyEvent = true;
            const payload = (evt.data || {}) as Record<string, unknown>;
            switch (evt.event) {
              case "router":
                setStatus("routing");
                pushTurnPatch((turn) => ({
                  ...turn,
                  intent: String(payload.intent || ""),
                  rewritten: String(payload.rewritten || ""),
                  subquestions: Array.isArray(payload.subquestions)
                    ? (payload.subquestions as string[])
                    : [],
                }));
                break;
              case "retrieval":
                setStatus("retrieving");
                pushTurnPatch((turn) => ({
                  ...turn,
                  protocolSkillFiles: (payload.protocol_skill_files as string[]) || [],
                  sourcesTopK: (payload.sources_topk as string[]) || [],
                  qualityCounts: (payload.quality_counts as Record<string, number>) || {},
                  rerankStatus: (payload.rerank_status as Record<string, unknown>) || {},
                }));
                break;
              case "token":
                setStatus("generating");
                pushTurnPatch((turn) => ({
                  ...turn,
                  answer: turn.answer + String(payload.text || ""),
                }));
                break;
              case "references":
                pushTurnPatch((turn) => ({
                  ...turn,
                  referencesUsed: (payload.references_used as RefItem[]) || [],
                  referencesAll: (payload.references_all as RefItem[]) || [],
                }));
                break;
              case "citations":
                pushTurnPatch((turn) => ({
                  ...turn,
                  citationVerdicts: Array.isArray(payload.verdicts)
                    ? (payload.verdicts as CiteVerdict[])
                    : [],
                }));
                break;
              case "followups":
                pushTurnPatch((turn) => ({
                  ...turn,
                  followups: (payload.questions as string[]) || [],
                }));
                break;
              case "error":
                setStatus("error");
                pushTurnPatch((turn) => ({
                  ...turn,
                  error: String(payload.message || "unknown error"),
                }));
                break;
              case "done":
                setStatus("done");
                break;
            }
          }
          match = frameSep.exec(buffer);
        }

        if (!seenAnyEvent && Date.now() - startedAt > 15000) {
          throw new Error("No SSE events within 15s — check backend URL.");
        }
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      setStatus("error");
      pushTurnPatch((turn) => ({ ...turn, error: message }));
    } finally {
      setLoading(false);
    }
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!question.trim() || loading) return;
    const value = question.trim();
    setQuestion("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
    await runStream(value);
  }

  async function handleFileUpload(file: File) {
    setAttachLoading(true);
    setAttachError(null);
    try {
      const form = new FormData();
      form.append("file", file);
      const resp = await fetch("/api/session/attach", { method: "POST", body: form });
      if (!resp.ok) {
        const detail = await resp.text().catch(() => "");
        throw new Error(detail || `HTTP ${resp.status}`);
      }
      const data = await resp.json();
      setAttachedDoc({
        session_id: data.session_id,
        filename: data.filename,
        token_estimate: data.token_estimate,
        condensed_preview: data.condensed_preview ?? "",
      });
    } catch (err) {
      setAttachError(err instanceof Error ? err.message : String(err));
    } finally {
      setAttachLoading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  async function handleDetach() {
    if (!attachedDoc) return;
    const sessionId = attachedDoc.session_id;
    setAttachedDoc(null);
    setAttachError(null);
    try {
      await fetch("/api/session/detach", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }),
      });
    } catch {
      // Best effort only.
    }
  }

  function onKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void onSubmit(event as unknown as FormEvent);
    }
  }

  async function onFollowupAsk(value: string) {
    if (loading) return;
    setQuestion("");
    await runStream(value);
  }

  return (
    <main className="shell">
      <aside className="left-rail">
        <div className="rail-card rail-brand">
          <div className="brand-mark">
            <IconFlask />
          </div>
          <div>
            <div className="eyebrow">Method-aware RAG</div>
            <h1>Lab Evidence Copilot</h1>
            <p>Protocol reasoning, PubMed grounding, and wet-lab decision support in one surface.</p>
          </div>
        </div>

        <div className="rail-card rail-status">
          <div className="rail-card-head">
            <span>System state</span>
            <span className={`server-dot ${backendStatus}`} />
          </div>
          <div className="status-grid">
            <div>
              <label>Backend</label>
              <strong>{backendStatus === "checking" ? "Checking" : backendStatus.toUpperCase()}</strong>
            </div>
            <div>
              <label>Run state</label>
              <strong>{statusLabel}</strong>
            </div>
            <div>
              <label>Turns</label>
              <strong>{history.length}</strong>
            </div>
          </div>
        </div>

        <div className="rail-card rail-sessions">
          <div className="rail-card-head">
            <span>Sessions</span>
            <button
              type="button"
              className="ghost-button"
              onClick={clearConversation}
              disabled={loading || (history.length === 0 && !attachedDoc)}
              title="Clear conversation history and detach document"
            >
              Clear
            </button>
          </div>
          <div className="session-list">
            {history.length === 0 ? (
              <div className="session-empty">No conversation history yet.</div>
            ) : (
              history.map((turn, idx) => (
                <button
                  key={`${idx}-${turn.user}`}
                  type="button"
                  className={`session-row ${idx === activeTurn ? "active" : ""}`}
                  onClick={() => setActiveTurn(idx)}
                >
                  <span className="session-index">{String(idx + 1).padStart(2, "0")}</span>
                  <span className="session-copy">
                    <strong>{firstLine(turn.user, 34)}</strong>
                    <small>{turn.intent || "Question submitted"}</small>
                  </span>
                </button>
              ))
            )}
          </div>
        </div>
      </aside>

      <section className="workspace">
        <header className="hero">
          <div>
            <div className="eyebrow">Method-aware literature assistant</div>
            <h2>Ask better wet-lab questions.</h2>
          </div>
          <div className="hero-badges">
            <span className={`hero-badge ${status}`}>
              <IconPulse />
              {statusLabel}
            </span>
            <button
              type="button"
              className="hero-toggle"
              onClick={() => setShowEvidencePanel((value) => !value)}
            >
              {showEvidencePanel ? "Hide inspector" : "Show inspector"}
            </button>
          </div>
        </header>

        <div className="conversation">
          {history.length === 0 ? (
            <section className="welcome-card">
              <div className="welcome-copy">
                <div className="eyebrow">Start here</div>
                <h3>Search literature, use protocol memory, and optionally attach your own notes.</h3>
                <p>
                  Ask a question below or start from one of these prompts.
                </p>
              </div>

              <div className="prompt-grid">
                {SAMPLE_PROMPTS.map((prompt) => (
                  <button
                    key={prompt}
                    type="button"
                    className="prompt-chip"
                    onClick={() => {
                      setQuestion(prompt);
                      textareaRef.current?.focus();
                    }}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </section>
          ) : (
            history.map((turn, idx) => {
              const isLastTurn = idx === history.length - 1;
              const isStreaming = isLastTurn && loading;
              const isFocused = idx === activeTurn;
              const refMap = new Map<number, RefItem>();
              (turn.referencesAll.length > 0 ? turn.referencesAll : turn.referencesUsed).forEach((ref, refIdx) => {
                refMap.set(refIdx + 1, ref);
              });
              const verdictMap = new Map<number, CiteVerdict["status"]>();
              const verdictReasonMap = new Map<number, string>();
              for (const v of turn.citationVerdicts || []) {
                // If the same ref is verified multiple times across the
                // answer, prefer the worst verdict so the UI flags risk
                // rather than masking it.
                const prev = verdictMap.get(v.n);
                const rank = (s: CiteVerdict["status"]) =>
                  s === "unsupported" ? 2 : s === "partial" ? 1 : 0;
                if (!prev || rank(v.status) > rank(prev)) {
                  verdictMap.set(v.n, v.status);
                  verdictReasonMap.set(v.n, v.reason);
                }
              }

              return (
                <article key={`${idx}-${turn.user}`} className={`turn-card ${isFocused ? "focus" : ""}`} onClick={() => setActiveTurn(idx)}>
                  <div className="turn-meta">
                    <span className="turn-number">Turn {idx + 1}</span>
                    {turn.intent && <span className={`intent-pill ${intentTone(turn.intent)}`}>{turn.intent}</span>}
                    {isStreaming && <span className="streaming-pill">{statusLabel}</span>}
                  </div>

                  <div className="message message-user">
                    <div className="message-label">Research prompt</div>
                    <div className="message-body">{turn.user}</div>
                  </div>

                  <div className="message message-assistant">
                    <div className="message-label">Assistant synthesis</div>
                    {isStreaming && !turn.answer && (
                      <div className="stage-panel">
                        <span className="stage-spinner" />
                        <span>{status === "routing" ? "Classifying question and rewriting query…" : status === "retrieving" ? "Searching PubMed and protocol memory…" : "Initializing stream…"}</span>
                      </div>
                    )}
                    {turn.answer && <div className="answer-body">{renderAnswerBlocks(turn.answer, { numberedRefMap: refMap, verdictMap, verdictReasonMap })}</div>}
                    {turn.error && <div className="error-banner">{turn.error}</div>}

                    {(turn.sourcesTopK.length > 0 || turn.referencesAll.length > 0) && (
                      <div className="artifact-row">
                        {turn.sourcesTopK.map((source, sourceIdx) => (
                          <span key={`${source}-${sourceIdx}`} className="artifact-pill">
                            <IconFile />
                            {shortSourceName(source)}
                          </span>
                        ))}
                        {turn.referencesAll.length > 0 && <span className="artifact-pill pubmed">{turn.referencesAll.length} PubMed refs</span>}
                      </div>
                    )}

                    {turn.referencesAll.length > 0 && !isStreaming && (
                      <details className="reference-block" open>
                        <summary>
                          Reference ledger
                          <span>{turn.referencesUsed.length} cited / {turn.referencesAll.length} retrieved</span>
                        </summary>
                        <ol>
                          {turn.referencesAll.map((ref, refIdx) => {
                            const authors = ref.authors && ref.authors.length > 0
                              ? ref.authors.length > 3
                                ? `${ref.authors.slice(0, 3).join(", ")}, et al.`
                                : ref.authors.join(", ")
                              : "";
                            return (
                              <li key={`ref-${ref.pmid || refIdx}`}>
                                <div className="ref-title">{ref.title || "Untitled"}</div>
                                <div className="ref-meta">
                                  {[ref.journal, ref.year, authors].filter(Boolean).join(" · ")}
                                </div>
                                {ref.pmid && (
                                  <a href={`https://pubmed.ncbi.nlm.nih.gov/${ref.pmid}/`} target="_blank" rel="noreferrer">
                                    PubMed
                                    <IconArrowUpRight />
                                  </a>
                                )}
                              </li>
                            );
                          })}
                        </ol>
                      </details>
                    )}

                    {turn.followups.length > 0 && !isStreaming && (
                      <div className="followup-row">
                        <label>Next questions</label>
                        <div className="followup-grid">
                          {turn.followups.map((followup, followupIdx) => (
                            <button
                              key={`${followup}-${followupIdx}`}
                              type="button"
                              className="followup-chip"
                              onClick={(event) => {
                                event.stopPropagation();
                                void onFollowupAsk(followup);
                              }}
                            >
                              {followup}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </article>
              );
            })
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="composer-shell">
          {(attachedDoc || attachLoading || attachError) && (
            <div className="attachment-banner" title={attachedDoc?.condensed_preview || ""}>
              {attachLoading && <span className="attachment-chip loading">Condensing attached document…</span>}
              {!attachLoading && attachedDoc && (
                <span className="attachment-chip">
                  <IconAttach />
                  <strong>{attachedDoc.filename}</strong>
                  <small>~{attachedDoc.token_estimate} tokens</small>
                  <button type="button" onClick={handleDetach} aria-label="Remove attachment">
                    ×
                  </button>
                </span>
              )}
              {!attachLoading && attachError && <span className="attachment-chip error">{attachError}</span>}
            </div>
          )}

          <form className="composer" onSubmit={onSubmit}>
            <input
              ref={fileInputRef}
              type="file"
              accept=".docx,.pdf,.md,.markdown,.txt"
              hidden
              onChange={(event) => {
                const file = event.target.files?.[0];
                if (file) void handleFileUpload(file);
              }}
            />
            <button
              type="button"
              className="icon-button"
              onClick={() => fileInputRef.current?.click()}
              disabled={attachLoading}
              aria-label="Attach document"
              title="Attach document"
            >
              <IconAttach />
            </button>

            <textarea
              ref={textareaRef}
              value={question}
              onChange={(event) => {
                setQuestion(event.target.value);
                autoResizeTextarea();
              }}
              onKeyDown={onKeyDown}
              placeholder="Ask about controls, troubleshooting, assay design, vector choice, or mechanistic interpretation…"
              rows={1}
            />

            <button type="submit" className="send-button" disabled={loading || !question.trim()}>
              <IconSend />
              <span>Send</span>
            </button>
          </form>
        </div>
      </section>

      {showEvidencePanel && (
        <aside className="inspector">
          <div className="inspector-card">
            <div className="inspector-head">
              <div>
                <div className="eyebrow">Evidence inspector</div>
                <h3>{currentTurn ? `Turn ${activeTurn + 1}` : "No turn selected"}</h3>
              </div>
              <span className="inspector-count">{totalRefs} refs</span>
            </div>

            {!currentTurn ? (
              <p className="inspector-empty">
                Select a turn to inspect rewritten query, retrieved sources, citation counts, and protocol metadata.
              </p>
            ) : (
              <div className="inspector-stack">
                <section className="metric-ribbon">
                  <div>
                    <label>Cited</label>
                    <strong>{citedCount}</strong>
                  </div>
                  <div>
                    <label>Retrieved</label>
                    <strong>{totalRefs}</strong>
                  </div>
                  <div>
                    <label>Local sources</label>
                    <strong>{retrievedSourcesCount}</strong>
                  </div>
                </section>

                {currentTurn.intent && (
                  <section className="inspector-panel">
                    <label>Intent</label>
                    <div className={`intent-pill ${intentTone(currentTurn.intent)}`}>{currentTurn.intent}</div>
                  </section>
                )}

                {currentTurn.rewritten && (
                  <section className="inspector-panel">
                    <label>Rewritten query</label>
                    <p>{currentTurn.rewritten}</p>
                  </section>
                )}

                {currentTurn.subquestions && currentTurn.subquestions.length > 0 && (
                  <section className="inspector-panel">
                    <label>Sub-questions detected</label>
                    <ol className="subquestion-list">
                      {currentTurn.subquestions.map((sq, idx) => (
                        <li key={`${idx}-${sq.slice(0, 40)}`}>{sq}</li>
                      ))}
                    </ol>
                  </section>
                )}

                {currentTurn.protocolSkillFiles.length > 0 && (
                  <section className="inspector-panel">
                    <label>Protocol skills</label>
                    <div className="tag-grid">
                      {currentTurn.protocolSkillFiles.map((item) => (
                        <span key={item} className="tag">
                          {item}
                        </span>
                      ))}
                    </div>
                  </section>
                )}

                {currentTurn.sourcesTopK.length > 0 && (
                  <section className="inspector-panel">
                    <label>Retrieved local sources</label>
                    <div className="source-list">
                      {currentTurn.sourcesTopK.map((item) => (
                        <div key={item} className="source-row">
                          <IconFile />
                          <span>{item}</span>
                        </div>
                      ))}
                    </div>
                  </section>
                )}

                {currentTurn.referencesUsed.length > 0 && (
                  <section className="inspector-panel">
                    <label>Cited papers</label>
                    <div className="paper-list">
                      {currentTurn.referencesUsed.map((ref, idx) => (
                        <article key={`${ref.pmid || idx}`} className="paper-card">
                          <strong>{ref.title || "Untitled"}</strong>
                          <p>{[ref.journal, ref.year].filter(Boolean).join(" · ") || "Metadata unavailable"}</p>
                          {ref.pmid && (
                            <a href={`https://pubmed.ncbi.nlm.nih.gov/${ref.pmid}/`} target="_blank" rel="noreferrer">
                              PMID {ref.pmid}
                              <IconArrowUpRight />
                            </a>
                          )}
                        </article>
                      ))}
                    </div>
                  </section>
                )}
              </div>
            )}
          </div>
        </aside>
      )}
    </main>
  );
}
