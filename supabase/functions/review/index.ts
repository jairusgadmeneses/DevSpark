import "jsr:@supabase/functions-js/edge-runtime.d.ts";

// ===========================================================================
// DevSpark — AI-Powered Code Review Edge Function
// Ported from backend/main.py (POST /api/review). Behavior, prompts, request
// payloads, response JSON structure, and fallback/error handling are preserved.
// Secrets (FEATHERLESS_API_KEY etc.) are read from Supabase Secret Manager and
// never exposed to the browser. verify_jwt is disabled because the original
// public backend had no authentication and the browser frontend sends no JWT.
//
// Provider: Featherless (https://api.featherless.ai/v1) — OpenAI-compatible
// chat completions for open-weight models. Defaults are verified non-gated
// models available on Featherless; override via the PRIMARY_MODEL / FALLBACK_MODEL
// secrets. Qwen/Qwen2.5-Coder-32B-Instruct is primary: it is purpose-built for
// code and answers directly (no thinking mode), keeping review latency low.
// ===========================================================================

// ---------------------------------------------------------------------------
// CORS — mirrors the wide-open policy of the original backend so the Vite
// frontend can call this function directly from any origin.
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
const API_KEY =
  Deno.env.get("FEATHERLESS_API_KEY") ||
  Deno.env.get("ZENMUX_API_KEY") ||
  Deno.env.get("OPENAI_API_KEY") ||
  "";
const BASE_URL = (
  Deno.env.get("FEATHERLESS_BASE_URL") ||
  Deno.env.get("ZENMUX_BASE_URL") ||
  "https://api.featherless.ai/v1"
).replace(/\/+$/, "");
// Featherless serves open-weight models; gpt-4o-mini is NOT available there.
// These defaults are verified non-gated models on Featherless.
const PRIMARY_MODEL = Deno.env.get("PRIMARY_MODEL") || "Qwen/Qwen2.5-Coder-32B-Instruct";
const FALLBACK_MODEL = Deno.env.get("FALLBACK_MODEL") || "Qwen/Qwen3-32B";

// ---------------------------------------------------------------------------
// Persona-aware system prompts — identical to backend/main.py
// ---------------------------------------------------------------------------
const SYSTEM_PROMPTS: Record<string, string> = {
  roast: "You are a brutally honest senior engineer with a sharp, humorous edge. "
    + "Your reviews are direct, memorable, and pull no punches — but always "
    + "constructive underneath the attitude. Use sarcasm and wit to make the "
    + "point stick. Never be mean without a reason; every jab must teach something.\n\n"
    + "You MUST respond with a single JSON object only. Do NOT include any text "
    + "outside the JSON. Follow the exact schema described below.",
  mentor: "You are a warm, patient, and supportive coding mentor. Your feedback "
    + "encourages growth and builds confidence. Explain concepts simply, celebrate "
    + "what the developer did well, and gently guide them toward improvement. "
    + "Assume the developer is still learning.\n\n"
    + "You MUST respond with a single JSON object only. Do NOT include any text "
    + "outside the JSON. Follow the exact schema described below.",
  professor: "You are a computer science professor providing a formal, academic code "
    + "review. Structure your feedback like a graded assignment: state the "
    + "evaluation criteria, assess each criterion, and provide a final letter-grade "
    + "equivalent alongside the numeric score. Use precise engineering terminology. "
    + "Reference established principles (DRY, SOLID, KISS, YAGNI, etc.) where "
    + "applicable.\n\n"
    + "You MUST respond with a single JSON object only. Do NOT include any text "
    + "outside the JSON. Follow the exact schema described below.",
  senior: "You are a senior staff engineer conducting an enterprise-grade code review "
    + "for a production system. Focus on: maintainability, scalability, testability, "
    + "security, performance, and clean architecture. Evaluate code as if it will "
    + "be read and maintained by a team of 10+ engineers over multiple years. "
    + "Reference specific design patterns and architectural principles.\n\n"
    + "You MUST respond with a single JSON object only. Do NOT include any text "
    + "outside the JSON. Follow the exact schema described below.",
};

// Shared instructions appended to every persona prompt — identical to main.py
const JSON_SCHEMA_INSTRUCTIONS = `\n\nReturn a single JSON object with exactly these top-level keys:
  - "summary": object with keys "overall_assessment" (string) and "key_takeaway" (string).
  - "critiques": array of objects, each with:
      - "line": integer or null (the line number, or null if not applicable)
      - "severity": string — one of "error", "warning", "info"
      - "explanation": string — what the issue is
      - "why_it_matters": string — why this issue impacts code quality
      - "suggested_improvement": string — how to fix it
      - "engineering_principle": string — the relevant principle (e.g. DRY, SOLID, KISS, single-responsibility)
  - "learning_report": object with:
      - "code_quality_score": integer (0–100)
      - "strengths": array of strings
      - "improvement_areas": array of strings
      - "engineering_concepts": array of strings (e.g. "Separation of Concerns", "Error Handling Patterns")
      - "personalized_recommendation": string (a single actionable next step)
  - "reflection": object with keys:
      - "prompt_1": string — a question prompting the developer to identify the most impactful issue
      - "prompt_2": string — a question asking them what they would improve before seeing the solution
  - "optimized_solution": string — the full corrected/optimised version of the submitted code. Include complete code, not just diffs. Use proper escaping for newlines.
  - "session_summary": object with keys:
      - "language": string (the programming language reviewed)
      - "persona": string (the reviewer persona used)
      - "total_issues": integer (number of critiques)
      - "overall_sentiment": string — one of "positive", "neutral", "critical"

Ensure the JSON is valid and contains every key listed above. `
  + "Do not include any explanatory text before or after the JSON.";

// ---------------------------------------------------------------------------
// Prompt builders
// ---------------------------------------------------------------------------
type ReviewRequest = { code: string; language: string; persona: string };

function buildSystemPrompt(persona: string): string {
  const base = SYSTEM_PROMPTS[persona] ?? SYSTEM_PROMPTS.mentor;
  return base + JSON_SCHEMA_INSTRUCTIONS;
}

function buildUserPrompt(request: ReviewRequest): string {
  return `Review the following ${request.language} code as a ${request.persona} reviewer.\n\n\`\`\`${request.language}\n${request.code}\n\`\`\``;
}

// ---------------------------------------------------------------------------
// Request validation — mirrors the Pydantic CodeRequest model
// ---------------------------------------------------------------------------
const ALLOWED_PERSONAS = ["roast", "mentor", "professor", "senior"];

function validateCodeRequest(
  body: unknown,
): { ok: true; value: ReviewRequest } | { ok: false; detail: string } {
  if (typeof body !== "object" || body === null) {
    return { ok: false, detail: "Request body must be a JSON object" };
  }
  const b = body as Record<string, unknown>;

  if (typeof b.code !== "string" || b.code.trim() === "") {
    return { ok: false, detail: "code must not be empty" };
  }
  if (typeof b.language !== "string" || b.language.trim() === "") {
    return { ok: false, detail: "language is required" };
  }
  const persona = typeof b.persona === "string" ? b.persona.toLowerCase() : "mentor";
  if (!ALLOWED_PERSONAS.includes(persona)) {
    return { ok: false, detail: `persona must be one of ${ALLOWED_PERSONAS.join(", ")}` };
  }

  return {
    ok: true,
    value: { code: b.code.trim(), language: b.language, persona },
  };
}

// ---------------------------------------------------------------------------
// LLM call with primary → fallback chain — mirrors backend/main.py
// ---------------------------------------------------------------------------
class LLMFailureError extends Error {}

async function callLLM(
  systemPrompt: string,
  userPrompt: string,
): Promise<Record<string, unknown>> {
  const models = [
    { model: PRIMARY_MODEL, label: "primary" },
    { model: FALLBACK_MODEL, label: "fallback" },
  ];

  let lastError: unknown = null;

  for (const { model, label } of models) {
    // main.py skips the fallback when it is the same model as the primary.
    if (label === "fallback" && model === PRIMARY_MODEL) continue;

    try {
      const res = await fetch(`${BASE_URL}/chat/completions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${API_KEY}`,
        },
        body: JSON.stringify({
          model,
          messages: [
            { role: "system", content: systemPrompt },
            { role: "user", content: userPrompt },
          ],
          response_format: { type: "json_object" },
          temperature: 0.4,
          max_tokens: 4096,
        }),
        signal: AbortSignal.timeout(60_000),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`${label} model HTTP ${res.status}: ${text.slice(0, 300)}`);
      }

      const data = await res.json();
      const raw = data?.choices?.[0]?.message?.content;
      if (!raw) {
        throw new Error("LLM returned empty content");
      }
      return JSON.parse(raw) as Record<string, unknown>;
    } catch (err) {
      lastError = err;
      // Small delay before fallback (mirrors main.py).
      await new Promise((resolve) => setTimeout(resolve, 500));
    }
  }

  throw new LLMFailureError(
    `Both primary and fallback models failed. Last error: ${String(lastError)}`,
  );
}

// ---------------------------------------------------------------------------
// Response builder — validates LLM output against the canonical schema
// ---------------------------------------------------------------------------
function buildResponse(
  parsed: Record<string, unknown>,
  request: ReviewRequest,
): Record<string, unknown> {
  const critiquesRaw = Array.isArray(parsed.critiques) ? parsed.critiques : [];

  const critiques: Record<string, unknown>[] = [];
  for (const c of critiquesRaw) {
    if (typeof c !== "object" || c === null) continue;
    const item = c as Record<string, unknown>;
    critiques.push({
      line: typeof item.line === "number" ? item.line : null,
      severity: typeof item.severity === "string" ? item.severity : "info",
      explanation: typeof item.explanation === "string"
        ? item.explanation
        : "No explanation provided.",
      why_it_matters: typeof item.why_it_matters === "string"
        ? item.why_it_matters
        : "Understanding this issue will help you write better code.",
      suggested_improvement: typeof item.suggested_improvement === "string"
        ? item.suggested_improvement
        : "Consider refactoring this section for clarity.",
      engineering_principle: typeof item.engineering_principle === "string"
        ? item.engineering_principle
        : "General best practice.",
    });
  }

  const lrRaw = (typeof parsed.learning_report === "object" && parsed.learning_report !== null
    ? parsed.learning_report
    : {}) as Record<string, unknown>;

  let score = typeof lrRaw.code_quality_score === "number" ? lrRaw.code_quality_score : 0;
  score = Math.max(0, Math.min(100, Math.round(score)));

  const learningReport = {
    code_quality_score: score,
    strengths: Array.isArray(lrRaw.strengths) ? lrRaw.strengths : [],
    improvement_areas: Array.isArray(lrRaw.improvement_areas) ? lrRaw.improvement_areas : [],
    engineering_concepts: Array.isArray(lrRaw.engineering_concepts) ? lrRaw.engineering_concepts : [],
    personalized_recommendation: typeof lrRaw.personalized_recommendation === "string"
      ? lrRaw.personalized_recommendation
      : "Keep practising — code reviews are the best way to improve.",
  };

  const summary = typeof parsed.summary === "object" && parsed.summary !== null
    ? parsed.summary
    : { overall_assessment: "Review completed.", key_takeaway: "Keep learning and improving." };

  const reflection = typeof parsed.reflection === "object" && parsed.reflection !== null
    ? parsed.reflection
    : {
        prompt_1: "What engineering issue do you believe has the greatest impact on your code quality?",
        prompt_2: "Predict one improvement you would personally make before viewing the solution.",
      };

  const sessionSummary = typeof parsed.session_summary === "object" && parsed.session_summary !== null
    ? parsed.session_summary
    : {
        language: request.language,
        persona: request.persona,
        total_issues: critiques.length,
        overall_sentiment: "neutral",
      };

  return {
    summary,
    learning_report: learningReport,
    critiques,
    reflection,
    optimized_solution: typeof parsed.optimized_solution === "string" && parsed.optimized_solution.length > 0
      ? parsed.optimized_solution
      : request.code,
    session_summary: sessionSummary,
  };
}

// ---------------------------------------------------------------------------
// Graceful fallback response — identical to backend/main.py (never exposes
// raw stack traces).
// ---------------------------------------------------------------------------
function fallbackReviewResponse(
  request: ReviewRequest,
  errorDetail: string,
): Record<string, unknown> {
  return {
    summary: {
      overall_assessment: (
        "We were unable to complete the AI review due to a temporary "
        + "service interruption. Please try again shortly."
      ),
      key_takeaway: "The review engine is temporarily unavailable.",
    },
    learning_report: {
      code_quality_score: 0,
      strengths: [],
      improvement_areas: [],
      engineering_concepts: [],
      personalized_recommendation: (
        "Please resubmit your code once the review service is available."
      ),
    },
    critiques: [
      {
        line: null,
        severity: "info",
        explanation: (
          `The AI review service could not process your request: ${errorDetail}`
        ),
        why_it_matters: (
          "Without a review, you may miss opportunities to improve "
          + "your code quality and learn engineering best practices."
        ),
        suggested_improvement: (
          "Check your network connection and try submitting again. "
          + "If the problem persists, contact support."
        ),
        engineering_principle: "Resilience — systems should degrade gracefully.",
      },
    ],
    reflection: {
      prompt_1: "What do you think might be the strongest aspect of your code?",
      prompt_2: "Is there a part of your code you would refactor first if you had more time?",
    },
    optimized_solution: request.code,
    session_summary: {
      language: request.language,
      persona: request.persona,
      total_issues: 1,
      overall_sentiment: "neutral",
      error: true,
    },
  };
}

// ---------------------------------------------------------------------------
// Handler — POST /review (mirrors POST /api/review in main.py)
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

  const validation = validateCodeRequest(body);
  if (!validation.ok) {
    return jsonResponse({ detail: validation.detail }, 422);
  }
  const request = validation.value;

  const systemPrompt = buildSystemPrompt(request.persona);
  const userPrompt = buildUserPrompt(request);

  try {
    const parsed = await callLLM(systemPrompt, userPrompt);
    const result = buildResponse(parsed, request);
    return jsonResponse(result, 200);
  } catch (err) {
    // Both main.py error paths return HTTP 200 with the graceful fallback body.
    const detail = err instanceof LLMFailureError
      ? "The AI review engine is temporarily unavailable."
      : "An unexpected error occurred. Please try again.";
    return jsonResponse(fallbackReviewResponse(request, detail), 200);
  }
});
