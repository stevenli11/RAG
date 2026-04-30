import { NextRequest } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
// Parse + small_llm condense can take a few seconds for a 20-page doc.
export const maxDuration = 60;

const DEFAULT_BACKEND = "http://127.0.0.1:8001";

export async function POST(req: NextRequest) {
  const backend = process.env.BACKEND_API_URL || DEFAULT_BACKEND;
  // Forward the multipart body as-is. The browser sets the Content-Type
  // header (with boundary) automatically on FormData uploads.
  const ct = req.headers.get("content-type") || "multipart/form-data";
  const body = await req.arrayBuffer();

  const upstream = await fetch(`${backend.replace(/\/$/, "")}/session/attach`, {
    method: "POST",
    headers: { "Content-Type": ct },
    body,
    cache: "no-store"
  });

  const text = await upstream.text();
  return new Response(text, {
    status: upstream.status,
    headers: { "Content-Type": upstream.headers.get("content-type") || "application/json" }
  });
}
