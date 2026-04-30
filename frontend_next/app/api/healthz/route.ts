const DEFAULT_BACKEND = "http://127.0.0.1:8001";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  const backend = process.env.BACKEND_API_URL || DEFAULT_BACKEND;
  try {
    const resp = await fetch(`${backend.replace(/\/$/, "")}/healthz`, { cache: "no-store" });
    const text = await resp.text();
    return new Response(text, {
      status: resp.status,
      headers: { "Content-Type": "application/json" }
    });
  } catch (e) {
    return new Response(JSON.stringify({ status: "error", detail: String(e) }), {
      status: 502,
      headers: { "Content-Type": "application/json" }
    });
  }
}

