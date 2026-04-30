import { NextRequest } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const DEFAULT_BACKEND = "http://127.0.0.1:8001";

export async function POST(req: NextRequest) {
  const backend = process.env.BACKEND_API_URL || DEFAULT_BACKEND;
  const body = await req.text();
  const upstream = await fetch(`${backend.replace(/\/$/, "")}/session/detach`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
    cache: "no-store"
  });
  const text = await upstream.text();
  return new Response(text, {
    status: upstream.status,
    headers: { "Content-Type": upstream.headers.get("content-type") || "application/json" }
  });
}
