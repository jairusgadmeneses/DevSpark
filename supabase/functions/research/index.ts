import "jsr:@supabase/functions-js/edge-runtime.d.ts";

// ===========================================================================
// DevSpark — Guided Engineering Research Edge Function
// Ported from backend/main.py (POST /api/research). Behavior, request payloads,
// response JSON structure, and fallback/error handling are preserved. Bright
// Data credentials are read from Supabase Secret Manager and never exposed to
// the browser. verify_jwt is disabled because the original public backend had
// no authentication and the browser frontend sends no JWT.
// ===========================================================================

// ---------------------------------------------------------------------------
// CORS — mirrors the wide-open policy of the original backend.
// ---------------------------------------------------------------------------
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

function jsonResponse(body: unknown, status: number): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
}

// ---------------------------------------------------------------------------
// Environment — server-side secrets only (Supabase Secret Manager)
// ---------------------------------------------------------------------------
const BRIGHTDATA_API_KEY = Deno.env.get("BRIGHTDATA_API_KEY") || "";
const BRIGHTDATA_ZONE = Deno.env.get("BRIGHTDATA_ZONE") || "";

// ---------------------------------------------------------------------------
// Bright Data → ResearchResource transformation — mirrors backend/main.py
// ---------------------------------------------------------------------------
function buildGoogleSearchUrl(query: string): string {
  return `https://www.google.com/search?q=${encodeURIComponent(query).replace(/%20/g, "+")}`;
}

function extractSearchResultTitle(url: string): string {
  try {
    const parsed = new URL(url);
    let domain = parsed.hostname.toLowerCase();
    if (domain.startsWith("www.")) domain = domain.slice(4);
    return domain || "Search Result";
  } catch {
    return "Search Result";
  }
}

function transformBrightdataResponse(
  body: unknown,
  _query: string,
): Record<string, unknown>[] {
  const results: Record<string, unknown>[] = [];

  // Bright Data's parsed_light structure often wraps the actual data in a
  // top-level list or a specific results key. Handle both common patterns.
  let dataSource: unknown = body;
  if (typeof body === "object" && body !== null && !Array.isArray(body)) {
    const b = body as Record<string, unknown>;
    dataSource = b.results ?? b.organic ?? b.data ?? body;
  }

  if (Array.isArray(dataSource)) {
    for (const item of dataSource.slice(0, 5)) {
      if (typeof item !== "object" || item === null) continue;
      const r = item as Record<string, unknown>;
      const url = typeof r.link === "string"
        ? r.link
        : typeof r.url === "string"
        ? r.url
        : typeof r.href === "string"
        ? r.href
        : null;
      const title = typeof r.title === "string"
        ? r.title
        : typeof r.name === "string"
        ? r.name
        : extractSearchResultTitle(url ?? "");
      const description = typeof r.description === "string"
        ? r.description
        : typeof r.snippet === "string"
        ? r.snippet
        : typeof r.summary === "string"
        ? r.summary
        : "";

      if (url) {
        results.push({
          title,
          url,
          description: String(description).slice(0, 240),
          type: "docs",
        });
      }
    }
  }

  if (results.length > 0) return results;

  // Fallback: if body has an explicit 'url', treat it as a single result.
  if (typeof body === "object" && body !== null && typeof (body as Record<string, unknown>).url === "string") {
    const u = (body as Record<string, unknown>).url as string;
    return [{
      title: extractSearchResultTitle(u),
      url: u,
      description: "Bright Data returned this resource for your query.",
      type: "docs",
    }];
  }

  return [];
}

// ---------------------------------------------------------------------------
// Handler — POST /research (mirrors POST /api/research in main.py)
// ---------------------------------------------------------------------------
Deno.serve(async (req) => {
  // CORS preflight
  if (req.method === "OPTIONS") {
    return new Response("ok", { status: 200, headers: corsHeaders });
  }
  if (req.method !== "POST") {
    return jsonResponse({ detail: "Method not allowed" }, 405);
  }

  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return jsonResponse({ detail: "Request body must be valid JSON" }, 422);
  }

  const query = typeof (body as Record<string, unknown>)?.query === "string"
    ? ((body as Record<string, unknown>).query as string).trim()
    : "";
  if (!query) {
    return jsonResponse({ detail: "query must not be empty" }, 422);
  }
  if (query.length < 3) {
    return jsonResponse({ detail: "query must be at least 3 characters" }, 422);
  }

  // Mirrors main.py: 503 when Bright Data is not configured.
  if (!BRIGHTDATA_API_KEY || BRIGHTDATA_API_KEY === "your_brightdata_api_key_here") {
    return jsonResponse(
      { detail: "Bright Data API key is not configured. Set BRIGHTDATA_API_KEY." },
      503,
    );
  }
  if (!BRIGHTDATA_ZONE || BRIGHTDATA_ZONE === "your_brightdata_zone_name_here") {
    return jsonResponse(
      { detail: "Bright Data zone is not configured. Set BRIGHTDATA_ZONE." },
      503,
    );
  }

  const searchUrl = buildGoogleSearchUrl(query);
  const payload = {
    zone: BRIGHTDATA_ZONE,
    url: searchUrl,
    format: "json",
    data_format: "parsed_light",
  };

  let bdResponse: Response;
  try {
    bdResponse = await fetch("https://api.brightdata.com/request", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${BRIGHTDATA_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(30_000),
    });
  } catch {
    return jsonResponse(
      { detail: "Could not reach the research provider. Please try again later." },
      502,
    );
  }

  if (!bdResponse.ok) {
    return jsonResponse(
      { detail: "Could not retrieve resources from Bright Data. Please try again later." },
      502,
    );
  }

  let data: unknown;
  try {
    data = await bdResponse.json();
  } catch {
    return jsonResponse(
      { detail: "Could not retrieve resources from Bright Data. Please try again later." },
      502,
    );
  }

  // Bright Data sometimes nests the parsed result in body["body"]. Safely
  // unwrap it: use dict/list directly, parse JSON strings, or fall back on
  // error/missing key (mirrors main.py).
  if (typeof data === "object" && data !== null && "body" in (data as Record<string, unknown>)) {
    const nested = (data as Record<string, unknown>).body;
    if (typeof nested === "object" && nested !== null) {
      data = nested;
    } else if (typeof nested === "string") {
      try {
        data = JSON.parse(nested);
      } catch {
        data = {};
      }
    }
  }

  let resources = transformBrightdataResponse(data, query);

  // Always ensure we have at least a safe fallback so the frontend never hangs.
  if (resources.length === 0) {
    resources = [{
      title: "Search results",
      url: searchUrl,
      description: "View the raw search results for this topic.",
      type: "docs",
    }];
  }

  return jsonResponse({ resources }, 200);
});
