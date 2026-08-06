<h1 align="center">⚡ DevSpark</h1>
<h3 align="center">The Educational Review Orchestrator</h3>

<p align="center">
  <em>Review. Reflect. Research. Refactor.</em>
</p>

<p align="center">
  <em>DevSpark believes engineers shouldn't only receive answers—they should also learn how to find trustworthy answers.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=fff" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Vite-646CFF?logo=vite&logoColor=fff" alt="Vite" />
  <img src="https://img.shields.io/badge/Pydantic-E92063?logo=pydantic&logoColor=fff" alt="Pydantic" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-06B6D4?logo=tailwindcss&logoColor=fff" alt="Tailwind CSS" />
  <img src="https://img.shields.io/badge/Python_3.12+-3776AB?logo=python&logoColor=fff" alt="Python" />
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
│          │  POST /api/review                      │
│          ▼                                        │
├──────────────────────────────────────────────────┤
│            VITE PROXY (vite.config.ts)            │
│    /api ──────► http://localhost:8000/api         │
│    /health ───► http://localhost:8000/health      │
├──────────────────────────────────────────────────┤
│                   BACKEND                         │
│       FastAPI Orchestration Layer                 │
│                  :8000                            │
│          │                                        │
│          ▼                                        │
│  ┌──────────────────────────────┐                 │
│  │   Pydantic JSON Contract     │                 │
│  │  ────────────────────────── │                 │
│  │  CodeRequest (inbound)      │                 │
│  │  ReviewResponse (outbound)  │                 │
│  │  CritiqueItem               │                 │
│  │  LearningReport             │                 │
│  └──────────┬───────────────────┘                 │
│             │                                     │
│             ▼                                     │
│  ┌──────────────────────────────┐                 │
│  │   Persona-Aware Prompt      │                 │
│  │   Builder                    │                 │
│  │   4 distinct system prompts │                 │
│  │   + JSON schema enforcement │                 │
│  └───────┬──────────────┬───────┘                 │
│          │              │                         │
│          ▼              ▼                         │
│  ┌─────────────┐  ┌─────────────┐                 │
│  │LLM Provider │  │Bright Data   │                 │
│  │(Code Review)│  │(Grounded     │                 │
│  │             │  │ Research)    │                 │
│  └───────┬─────┘  └──────┬──────┘                 │
│          │                                         │
│          ▼                                         │
│  ┌──────────────────────────────┐                 │
│  │  Structured Response         │                 │
│  └──────────────────────────────┘                 │
└──────────────────────────────────────────────────┘
```

### Why This Architecture Matters

This isn't a flimsy AI wrapper. The architecture is built on three layers of engineering rigor:

1. **Strict Pydantic JSON Contract** — Every API response is validated through `ReviewResponse`, `CritiqueItem`, and `LearningReport` Pydantic models before reaching the frontend. If the LLM returns malformed or incomplete JSON, the backend catches it and degrades gracefully — never passing raw text to the user.

2. **FastAPI Orchestration Layer** — The backend doesn't just relay prompts. It:
   - Selects and injects persona-specific system prompts (each with distinct tone, vocabulary, and grading criteria)
   - Appends a shared JSON schema instruction block that enforces structured output via OpenAI's `response_format={"type": "json_object"}`
   - Runs a **primary → fallback model chain** with automatic retry on timeout, API error, or rate limit
   - Returns a **graceful fallback response** (never a stack trace) if both models fail

3. **Frontend Compatibility Layer** — The `_build_response` function adds `message` and `optimized_code` aliases so the frontend can consume either the canonical Pydantic field names or common LLM output variants without breaking.

---

## 🚀 Local Setup

### Prerequisites

- Python 3.12+
- Node.js 20+
- An API key from one of: [ZenMux](https://zenmux.com), [OpenAI](https://platform.openai.com), or [Featherless](https://featherless.ai)

### 1. Clone and install dependencies

```bash
git clone <your-repo-url>
cd devspark

# Frontend dependencies
npm install

# Backend dependencies
cd backend
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set at minimum:

```bash
ZENMUX_API_KEY=zk_your_key_here
# OR
OPENAI_API_KEY=sk_your_key_here
```

> **For Featherless users:** Set `ZENMUX_BASE_URL=https://api.featherless.ai/v1` and provide your Featherless API key via `ZENMUX_API_KEY`.

### 3. Start the backend

```bash
# From the project root
cd backend
python main.py
```

The API starts at **http://localhost:8000**. Verify with:

```bash
curl http://localhost:8000/health
# → {"status": "ok"}
```

### 4. Start the frontend (separate terminal)

```bash
# From the project root
npm run dev
```

The Vite dev server starts at **http://localhost:5173** and proxies `/api/*` requests to the backend automatically.

### 🧪 Testing with Different Models

| Provider | `ZENMUX_BASE_URL` | Model Example |
|----------|-------------------|---------------|
| ZenMux (default) | `https://api.zenmux.com/v1` | `gpt-4o-mini` |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` |
| Featherless | `https://api.featherless.ai/v1` | `meta-llama-3-70b-instruct` |
| Local (LM Studio) | `http://localhost:1234/v1` | `local-model` |

---

## 🔌 API Reference

### Health Check

```
GET /health
```

Response: `{"status": "ok"}`

### Submit Code for Review

```
POST /api/review
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

**Response (validated ReviewResponse):**

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
      "message": "Consider adding type hints...",
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
  "optimized_code": "def hello() -> None:\n    print('hello world')",
  "session_summary": {
    "language": "python",
    "persona": "mentor",
    "total_issues": 1,
    "overall_sentiment": "positive"
  }
}
```

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

The backend is configured with wide-open CORS for hackathon/local testing:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Allow any origin
    allow_credentials=True,
    allow_methods=["*"],       # Allow all HTTP methods
    allow_headers=["*"],       # Allow all headers
)
```

**For local testing:**
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- The Vite dev server proxies `/api/*` and `/health` to the backend, so no direct CORS configuration is needed during development.

**For production deployment:**
1. Change `allow_origins` from `["*"]` to your actual domain(s).
2. Ensure the backend is served behind a reverse proxy (e.g., Nginx, Caddy) with HTTPS.
3. The frontend can call the backend directly (update the API URL) or continue using a proxy.

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
│   ├── main.py              # FastAPI app: routes, prompts, LLM orchestration
│   └── requirements.txt     # Python dependencies
├── public/
│   └── nativelyai.svg       # Favicon
├── index.html               # Single-page frontend (all HTML + JS + CSS)
├── package.json             # Node dependencies & scripts
├── vite.config.ts           # Vite config (dev proxy to backend)
├── tsconfig.json            # TypeScript config
├── .env.example             # Environment variable template
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