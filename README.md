<h1 align="center">⚡ DevSpark</h1>
<h3 align="center">The Educational Review Orchestrator</h3>

<p align="center">
  <em>Review. Reflect. Research. Refactor.</em>
</p>

<p align="center">
  <em>DevSpark believes engineers shouldn't only receive answers—they should also learn how to find trustworthy answers.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Supabase_Edge_Functions-3ECF8E?logo=supabase&logoColor=black" alt="Supabase Edge Functions" />
  <img src="https://img.shields.io/badge/Vite-646CFF?logo=vite&logoColor=fff" alt="Vite" />
  <img src="https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=fff" alt="TypeScript" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-06B6D4?logo=tailwindcss&logoColor=fff" alt="Tailwind CSS" />
  <img src="https://img.shields.io/badge/Deno-70FFAF?logo=deno&logoColor=black" alt="Deno" />
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License" />
</p>

---

## 🎯 The Core Differentiator

> **Most AI coding tools stop at "Upload → Answer".**
>
> **DevSpark enforces "Upload → Analyze → Understand → Reflect → Research → Improve".**

We don't hand you an answer sheet. DevSpark is an *educational review engine*: it reviews your code, prompts you to think critically about the feedback, and only then reveals the optimized solution. The learning happens in the space between the critique and the reveal.

---

## ✨ Key Features

### 🧠 Reflection Gatekeeper
The optimized solution starts **locked behind a blur overlay**. To unlock it, you must:
1. Read through each critique point carefully.
2. Answer two reflection prompts — identifying the most impactful issue and predicting your own improvement.
3. Only then does the solution reveal itself with a rewarding green-flash animation.

This enforces *active recall* — encourages active recall and reflection, learning techniques widely used to improve understanding and retention.

### 🎭 4 Review Persona Modes

| Persona | Style | Best For |
|---------|-------|----------|
| 🔥 **Roast Mode** | Brutally honest with sharp, humorous edge | Getting memorable feedback that sticks |
| 🧑‍🏫 **Mentor Mode** *(default)* | Warm, patient, supportive guide | Beginners and early-stage learning |
| 🎓 **Professor Mode** | Formal academic grading with letter-grade equivalence | Students preparing for exams or assignments |
| ⚙️ **Senior Engineer** | Enterprise-grade production review (scalability, security, architecture) | Experienced devs polishing production code |

### 📊 Learning Report Dashboard
After completing a review session, you receive a structured report including:
- **Code Quality Score** (0–100) with an animated visual meter
- **Strengths & Improvement Areas** — side-by-side comparison
- **Engineering Concepts** tagged as interactive badges (DRY, SOLID, KISS, etc.)
- **Personalized Recommendation** — a single actionable next step

### 🔎 Guided Engineering Research
After completing a review session, students can investigate each critique using grounded web resources.

Rather than generating another AI answer, DevSpark helps students continue learning by surfacing:
- Official documentation
- Framework documentation
- Trusted technical tutorials
- Relevant GitHub issues
- Engineering references

Powered by Bright Data.

### 📁 Drag-and-Drop Upload
Drop a file or paste code directly. Auto-detects language from file extension and pre-selects the corresponding language option.

---

## 🏗️ Tech Stack & Architecture

```
┌──────────────────────────────────────────────────┐
│                   FRONTEND                        │
│  HTML + Vanilla JS + Tailwind CSS (CDN) + Vite   │
│                  :5173                            │
│          │  POST /review  ·  POST /research       │
│          ▼                                        │
├──────────────────────────────────────────────────┤
│        SUPABASE EDGE FUNCTIONS (Deno)             │
│  https://<ref>.supabase.co/functions/v1           │
│  ┌──────────────────────────────┐                 │
│  │  review  (AI code review)    │                 │
│  │  research (guided research)  │                 │
│  └───────┬──────────────┬───────┘                 │
│          │              │                         │
│          ▼              ▼                         │
│  ┌──────────────────┐  ┌───────────────────┐      │
│  │ Persona-Aware    │  │ Bright Data SERP  │      │
│  │ Prompt Builder   │  │ (grounded web     │      │
│  │ + JSON schema    │  │  resources)       │      │
│  │ enforcement      │  └───────────────────┘      │
│  └───────┬──────────┘                             │
│          │                                        │
│          ▼                                        │
│  ┌──────────────────────────────┐                 │
│  │  Featherless (LLM)           │                 │
│  │  primary → fallback chain    │                 │
│  └───────┬──────────────────────┘                 │
│          │                                        │
│          ▼                                        │
│  ┌──────────────────────────────┐                 │
│  │  Canonical ReviewResponse    │                 │
│  │  JSON (validated, no aliases)│                 │
│  └──────────────────────────────┘                 │
└──────────────────────────────────────────────────┘
```

Secrets (`FEATHERLESS_API_KEY`, `BRIGHTDATA_API_KEY`, `BRIGHTDATA_ZONE`, model overrides) live in **Supabase Secret Manager** and are read only inside the Edge Functions via `Deno.env.get()` — never in client code.

### Why This Architecture Matters

This isn't a flimsy AI wrapper. The architecture is built on three layers of engineering rigor:

1. **Strict JSON Contract** — Every Edge Function response is validated against the canonical `ReviewResponse` shape (summary, critiques, learning_report, reflection, optimized_solution, session_summary) before reaching the frontend. If the LLM returns malformed or incomplete JSON, the function catches it and degrades gracefully — never passing raw text to the user.

2. **Supabase Edge Function Orchestration** — The backend doesn't just relay prompts. It:
   - Selects and injects persona-specific system prompts (each with distinct tone, vocabulary, and grading criteria)
   - Appends a shared JSON schema instruction block that enforces structured output via `response_format={"type": "json_object"}`
   - Runs a **primary → fallback model chain** with automatic retry on timeout, API error, or rate limit
   - Returns a **graceful fallback response** (never a stack trace) if both models fail

3. **Behavior Parity** — The Edge Functions were ported 1:1 from the original FastAPI backend (`backend/main.py`): identical prompts, request validation, fallback messages, and canonical response fields. No `message`/`optimized_code` aliases are emitted — the frontend consumes the canonical field names (`explanation`, `optimized_solution`).

---

## 🚀 Local Setup

### Prerequisites

- Node.js 20+
- A Supabase project (Edge Functions are deployed to it)
- A [Featherless](https://featherless.ai) API key (`fl_...`) for AI reviews
- *(Optional)* [Bright Data](https://brightdata.com) SERP zone credentials for guided research

### 1. Install dependencies

```bash
git clone <your-repo-url>
cd devspark

npm install
```

> Note: the backend runs as **Supabase Edge Functions** (`supabase/functions/review` and `supabase/functions/research`), not a local Python server. `backend/main.py` remains in the repo as the reference implementation only.

### 2. Configure secrets (Supabase Secret Manager)

Secrets are stored in **Supabase Secret Manager** and read inside the Edge Functions — never in `.env` or client code.

```bash
# Store the Featherless API key (required for AI reviews)
supabase secrets set FEATHERLESS_API_KEY=fl_your_key_here

# Optional: override models (defaults: Qwen/Qwen2.5-Coder-32B-Instruct primary, Qwen/Qwen3-32B fallback)
supabase secrets set PRIMARY_MODEL=Qwen/Qwen2.5-Coder-32B-Instruct
supabase secrets set FALLBACK_MODEL=Qwen/Qwen3-32B

# Optional: Bright Data credentials (required for the research endpoint)
supabase secrets set BRIGHTDATA_API_KEY=your_key_here
supabase secrets set BRIGHTDATA_ZONE=your_zone_here
```

### 3. Deploy the Edge Functions

```bash
supabase functions deploy review
supabase functions deploy research
```

The functions are now live at `https://<project-ref>.supabase.co/functions/v1/review` and `.../research`.

### 4. Start the frontend

```bash
# From the project root
npm run dev
```

The Vite dev server starts at **http://localhost:5173**. The frontend calls the Edge Functions directly (`API_BASE_URL = https://<project-ref>.supabase.co/functions/v1` in `index.html`) — no local proxy required.

### 🧪 Testing with Different Models

The Edge Functions read model overrides from Supabase secrets:

| Provider | `FEATHERLESS_BASE_URL` secret | Model Example |
|----------|-------------------------------|---------------|
| Featherless (default) | `https://api.featherless.ai/v1` | `Qwen/Qwen2.5-Coder-32B-Instruct` |
| Featherless (fallback) | `https://api.featherless.ai/v1` | `Qwen/Qwen3-32B` |
| OpenAI-compatible (local) | `http://localhost:1234/v1` (LM Studio / Ollama) | `local-model` |

> ⚠️ Featherless serves open-weight models only — OpenAI models like `gpt-4o-mini` are **not** available there. Set `PRIMARY_MODEL` / `FALLBACK_MODEL` secrets to any non-gated model from `https://api.featherless.ai/v1/models`.

---

## 🔌 API Reference

The API is served by Supabase Edge Functions at:

```
Base URL: https://<project-ref>.supabase.co/functions/v1
```

### Submit Code for Review

```
POST /review
Content-Type: application/json
```

**Request body:**

```json
{
  "code": "def hello():\n    print('hello world')",
  "language": "python",
  "persona": "mentor"
}
```

`persona` must be one of `roast`, `mentor`, `professor`, `senior` (defaults to `mentor`).

**Response (canonical ReviewResponse — 200):**

```json
{
  "summary": {
    "overall_assessment": "Good foundational code...",
    "key_takeaway": "Always validate function inputs."
  },
  "critiques": [
    {
      "line": 1,
      "severity": "info",
      "explanation": "Consider adding type hints...",
      "why_it_matters": "Type hints improve readability...",
      "suggested_improvement": "Add type annotations...",
      "engineering_principle": "Defensive Programming"
    }
  ],
  "learning_report": {
    "code_quality_score": 78,
    "strengths": ["Clear function naming"],
    "improvement_areas": ["Missing input validation"],
    "engineering_concepts": ["Defensive Programming", "Type Safety"],
    "personalized_recommendation": "Start by adding type hints..."
  },
  "reflection": {
    "prompt_1": "What engineering issue do you believe has the greatest impact on your code quality?",
    "prompt_2": "Predict one improvement you would personally make before viewing the solution."
  },
  "optimized_solution": "def hello() -> None:\n    print('hello world')",
  "session_summary": {
    "language": "python",
    "persona": "mentor",
    "total_issues": 1,
    "overall_sentiment": "positive"
  }
}
```

If the LLM is unreachable, the function returns HTTP 200 with a **graceful fallback** `ReviewResponse` (`session_summary.error: true`) — never a stack trace.

**Validation errors** (mirror the original Pydantic contract):
- `422` — empty `code`, missing `language`, or invalid `persona` (e.g. `{"detail": "persona must be one of roast, mentor, professor, senior"}`)

### Guided Engineering Research

```
POST /research
Content-Type: application/json
```

**Request body:**

```json
{
  "query": "python async best practices"
}
```

**Response:**

```json
{
  "resources": [
    {
      "title": "asyncio — Asynchronous I/O",
      "url": "https://docs.python.org/3/library/asyncio.html",
      "description": "Official Python documentation...",
      "type": "docs"
    }
  ]
}
```

Returns `503` with a clear message if Bright Data credentials are not configured, and `502` if the provider cannot be reached.

### Persona Values

| Value | Mode |
|-------|------|
| `roast` | 🔥 Roast Mode |
| `mentor` | 🧑‍🏫 Mentor Mode (default) |
| `professor` | 🎓 Professor Mode |
| `senior` | ⚙️ Senior Engineer |

### Language Values

`python`, `java`, `javascript`, `cpp`, `html`, `css`, `plaintext`

---

## 🌐 CORS Configuration

The Edge Functions use a wide-open CORS policy (mirroring the original backend) so the Vite frontend can call them from any origin:

```ts
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};
```

Every function answers `OPTIONS` preflight requests with HTTP 200 + the CORS headers, and includes the same headers on real responses.

**For local testing:**
- Frontend: `http://localhost:5173`
- Functions: `https://<project-ref>.supabase.co/functions/v1`
- The frontend calls the functions directly — no Vite proxy or local CORS setup needed.

**For production deployment:**
1. Tighten `Access-Control-Allow-Origin` from `*` to your actual domain(s) in each function.
2. `verify_jwt` is disabled on both functions because the original public backend had no authentication and the browser sends no JWT. Enable JWT verification and pass a session token if you add authentication later.

---

## 🧪 Running the Build

```bash
# Production build (outputs to dist/)
npm run build

# Preview the production build locally
npm run preview
```

---

## 📁 Project Structure

```
devspark/
├── backend/
│   ├── main.py              # Reference FastAPI implementation (original backend)
│   └── requirements.txt     # Python dependencies (reference only)
├── supabase/
│   └── functions/
│       ├── review/          # Edge Function: POST /review (AI code review)
│       │   ├── index.ts
│       │   └── deno.json
│       └── research/        # Edge Function: POST /research (guided research)
│           ├── index.ts
│           └── deno.json
├── public/
│   └── nativelyai.svg       # Favicon
├── index.html               # Single-page frontend (all HTML + JS + CSS)
├── package.json             # Node dependencies & scripts
├── vite.config.ts           # Vite config (no backend proxy — direct function calls)
├── tsconfig.json            # TypeScript config
├── .env.example             # Legacy backend env template (reference only)
├── .gitignore               # Git ignore rules
└── README.md                # ← You are here
```

---

## 📜 License

Built for learning. MIT License.

---

<p align="center">
  <sub>Built with ❤️ for the hackathon — where code meets pedagogy.</sub>
</p>