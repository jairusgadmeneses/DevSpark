"""
DevSpark — AI-Powered Code Review Backend

A FastAPI orchestration layer that:
  - Accepts code submissions with language and persona selection
  - Builds persona-aware system prompts
  - Calls an OpenAI-compatible LLM (ZenMux / OpenAI) with JSON-enforced output
  - Falls back to a secondary model on failure
  - Returns strictly validated ReviewResponse JSON — never raw text
"""

import asyncio
import os
import json
import logging
from typing import Optional

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from openai import AsyncOpenAI, APIError, APITimeoutError, RateLimitError

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("devspark")

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

ZENMUX_API_KEY = os.getenv("ZENMUX_API_KEY") or os.getenv("OPENAI_API_KEY", "")
ZENMUX_BASE_URL = os.getenv(
    "ZENMUX_BASE_URL", "https://api.zenmux.com/v1"
)
PRIMARY_MODEL = os.getenv("PRIMARY_MODEL", "gpt-4o-mini")
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "gpt-4o-mini")

BRIGHTDATA_API_KEY = os.getenv("BRIGHTDATA_API_KEY", "")
BRIGHTDATA_ZONE = os.getenv("BRIGHTDATA_ZONE", "")

APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="DevSpark API",
    version="1.0.0",
    description="AI-powered code review orchestration layer",
)

# Allow any origin so the Vite frontend (localhost:5173) can reach us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# OpenAI-compatible client
# ---------------------------------------------------------------------------

client = AsyncOpenAI(
    api_key=ZENMUX_API_KEY,
    base_url=ZENMUX_BASE_URL,
)

# ---------------------------------------------------------------------------
# Pydantic request / response models
# ---------------------------------------------------------------------------


class CodeRequest(BaseModel):
    """Inbound payload from the frontend."""

    code: str
    language: str
    persona: str = "mentor"

    @field_validator("persona")
    @classmethod
    def _valid_persona(cls, v: str) -> str:
        allowed = {"roast", "mentor", "professor", "senior"}
        if v.lower() not in allowed:
            raise ValueError(f"persona must be one of {allowed}")
        return v.lower()

    @field_validator("code")
    @classmethod
    def _code_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("code must not be empty")
        return stripped


class CritiqueItem(BaseModel):
    """Single critique point returned by the LLM."""

    line: Optional[int] = None
    severity: str  # "error" | "warning" | "info"
    explanation: str
    why_it_matters: str
    suggested_improvement: str
    engineering_principle: str


class LearningReport(BaseModel):
    """Aggregated learning report / code quality summary."""

    code_quality_score: int = Field(..., ge=0, le=100)
    strengths: list[str]
    improvement_areas: list[str]
    engineering_concepts: list[str]
    personalized_recommendation: str


class ReviewResponse(BaseModel):
    """Top-level response contract — every endpoint returns this shape."""

    summary: dict
    learning_report: LearningReport
    critiques: list[CritiqueItem]
    reflection: dict
    optimized_solution: str
    session_summary: dict


# ---------------------------------------------------------------------------
# Persona-aware system prompts
# ---------------------------------------------------------------------------

SYSTEM_PROMPTS: dict[str, str] = {
    "roast": (
        "You are a brutally honest senior engineer with a sharp, humorous edge. "
        "Your reviews are direct, memorable, and pull no punches — but always "
        "constructive underneath the attitude. Use sarcasm and wit to make the "
        "point stick. Never be mean without a reason; every jab must teach something.\n\n"
        "You MUST respond with a single JSON object only. Do NOT include any text "
        "outside the JSON. Follow the exact schema described below."
    ),
    "mentor": (
        "You are a warm, patient, and supportive coding mentor. Your feedback "
        "encourages growth and builds confidence. Explain concepts simply, celebrate "
        "what the developer did well, and gently guide them toward improvement. "
        "Assume the developer is still learning.\n\n"
        "You MUST respond with a single JSON object only. Do NOT include any text "
        "outside the JSON. Follow the exact schema described below."
    ),
    "professor": (
        "You are a computer science professor providing a formal, academic code "
        "review. Structure your feedback like a graded assignment: state the "
        "evaluation criteria, assess each criterion, and provide a final letter-grade "
        "equivalent alongside the numeric score. Use precise engineering terminology. "
        "Reference established principles (DRY, SOLID, KISS, YAGNI, etc.) where "
        "applicable.\n\n"
        "You MUST respond with a single JSON object only. Do NOT include any text "
        "outside the JSON. Follow the exact schema described below."
    ),
    "senior": (
        "You are a senior staff engineer conducting an enterprise-grade code review "
        "for a production system. Focus on: maintainability, scalability, testability, "
        "security, performance, and clean architecture. Evaluate code as if it will "
        "be read and maintained by a team of 10+ engineers over multiple years. "
        "Reference specific design patterns and architectural principles.\n\n"
        "You MUST respond with a single JSON object only. Do NOT include any text "
        "outside the JSON. Follow the exact schema described below."
    ),
}

# Shared instructions appended to every persona prompt
JSON_SCHEMA_INSTRUCTIONS = (
    "\n\n"
    "Return a single JSON object with exactly these top-level keys:\n"
    "  - \"summary\": object with keys \"overall_assessment\" (string) and "
    "\"key_takeaway\" (string).\n"
    "  - \"critiques\": array of objects, each with:\n"
    "      - \"line\": integer or null (the line number, or null if not applicable)\n"
    "      - \"severity\": string — one of \"error\", \"warning\", \"info\"\n"
    "      - \"explanation\": string — what the issue is\n"
    "      - \"why_it_matters\": string — why this issue impacts code quality\n"
    "      - \"suggested_improvement\": string — how to fix it\n"
    "      - \"engineering_principle\": string — the relevant principle (e.g. DRY, SOLID, "
    "KISS, single-responsibility)\n"
    "  - \"learning_report\": object with:\n"
    "      - \"code_quality_score\": integer (0–100)\n"
    "      - \"strengths\": array of strings\n"
    "      - \"improvement_areas\": array of strings\n"
    "      - \"engineering_concepts\": array of strings (e.g. \"Separation of Concerns\", "
    "\"Error Handling Patterns\")\n"
    "      - \"personalized_recommendation\": string (a single actionable next step)\n"
    "  - \"reflection\": object with keys:\n"
    "      - \"prompt_1\": string — a question prompting the developer to identify "
    "the most impactful issue\n"
    "      - \"prompt_2\": string — a question asking them what they would improve "
    "before seeing the solution\n"
    "  - \"optimized_solution\": string — the full corrected/optimised version of "
    "the submitted code. Include complete code, not just diffs. Use proper escaping "
    "for newlines.\n"
    "  - \"session_summary\": object with keys:\n"
    "      - \"language\": string (the programming language reviewed)\n"
    "      - \"persona\": string (the reviewer persona used)\n"
    "      - \"total_issues\": integer (number of critiques)\n"
    "      - \"overall_sentiment\": string — one of \"positive\", \"neutral\", \"critical\"\n"
    "\n"
    "Ensure the JSON is valid and contains every key listed above. "
    "Do not include any explanatory text before or after the JSON."
)


def _build_system_prompt(persona: str) -> str:
    """Combine the persona prompt with the shared JSON schema instructions."""
    base = SYSTEM_PROMPTS.get(persona, SYSTEM_PROMPTS["mentor"])
    return base + JSON_SCHEMA_INSTRUCTIONS


def _build_user_prompt(request: CodeRequest) -> str:
    """Build the user message containing the code to review."""
    return (
        f"Review the following {request.language} code as a {request.persona} reviewer.\n\n"
        f"```{request.language}\n{request.code}\n```"
    )


# ---------------------------------------------------------------------------
# LLM call with fallback
# ---------------------------------------------------------------------------


async def _call_llm(
    system_prompt: str,
    user_prompt: str,
) -> dict:
    """
    Call the primary model; if it fails, try the fallback model once.
    Returns the parsed JSON dict.
    Raises RuntimeError if both calls fail.
    """
    models = [
        (PRIMARY_MODEL, "primary"),
        (FALLBACK_MODEL, "fallback"),
    ]

    last_error: Optional[Exception] = None

    for model_name, label in models:
        if label == "fallback" and model_name == models[0][0]:
            # If fallback is the same model as primary, skip redundant attempt
            continue
        try:
            logger.info("Calling %s model=%s", label, model_name)
            response = await client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.4,
                max_tokens=4096,
                timeout=60,
            )

            raw = response.choices[0].message.content
            if not raw:
                raise RuntimeError("LLM returned empty content")

            parsed = json.loads(raw)
            logger.info(
                "%s model succeeded (input tokens=%d, output tokens=%d)",
                label.capitalize(),
                response.usage.prompt_tokens if response.usage else 0,
                response.usage.completion_tokens if response.usage else 0,
            )
            return parsed

        except (APITimeoutError, APIError, RateLimitError, json.JSONDecodeError, RuntimeError) as exc:
            last_error = exc
            logger.warning("%s model failed: %s — %s", label.capitalize(), type(exc).__name__, exc)
            # Small delay before fallback
            await asyncio.sleep(0.5)

    raise RuntimeError(
        f"Both primary and fallback models failed. Last error: {last_error}"
    )


# ---------------------------------------------------------------------------
# Fallback response (when LLM is completely unavailable)
# ---------------------------------------------------------------------------

def _fallback_review_response(request: CodeRequest, error_detail: str) -> dict:
    """
    Return a gracefully degraded ReviewResponse when the LLM cannot be reached.
    Never exposes raw stack traces.
    """
    return {
        "summary": {
            "overall_assessment": (
                "We were unable to complete the AI review due to a temporary "
                "service interruption. Please try again shortly."
            ),
            "key_takeaway": "The review engine is temporarily unavailable.",
        },
        "learning_report": {
            "code_quality_score": 0,
            "strengths": [],
            "improvement_areas": [],
            "engineering_concepts": [],
            "personalized_recommendation": (
                "Please resubmit your code once the review service is available."
            ),
        },
        "critiques": [
            {
                "line": None,
                "severity": "info",
                "explanation": (
                    f"The AI review service could not process your request: "
                    f"{error_detail}"
                ),
                "why_it_matters": (
                    "Without a review, you may miss opportunities to improve "
                    "your code quality and learn engineering best practices."
                ),
                "suggested_improvement": (
                    "Check your network connection and try submitting again. "
                    "If the problem persists, contact support."
                ),
                "engineering_principle": "Resilience — systems should degrade gracefully.",
            }
        ],
        "reflection": {
            "prompt_1": "What do you think might be the strongest aspect of your code?",
            "prompt_2": "Is there a part of your code you would refactor first if you had more time?",
        },
        "optimized_solution": request.code,
        "session_summary": {
            "language": request.language,
            "persona": request.persona,
            "total_issues": 1,
            "overall_sentiment": "neutral",
            "error": True,
        },
    }


# ---------------------------------------------------------------------------
# Response builder — validates LLM output against the canonical schema
# ---------------------------------------------------------------------------

def _build_response(parsed: dict, request: CodeRequest) -> dict:
    """
    Validate parsed LLM output through the canonical ReviewResponse schema.
    Returns a dict matching ReviewResponse exactly; no duplicate or aliased fields.
    """
    # Ensure expected keys exist with safe defaults
    critiques_raw = parsed.get("critiques", [])
    learning_report_raw = parsed.get(
        "learning_report",
        {
            "code_quality_score": 0,
            "strengths": [],
            "improvement_areas": [],
            "engineering_concepts": [],
            "personalized_recommendation": "Complete a code review to receive a recommendation.",
        },
    )

    # Build CritiqueItem list — add `message` alias from `explanation`
    critiques: list[dict] = []
    for c in critiques_raw:
        if not isinstance(c, dict):
            continue
        item = CritiqueItem(
            line=c.get("line"),
            severity=c.get("severity", "info"),
            explanation=c.get("explanation", "No explanation provided."),
            why_it_matters=c.get(
                "why_it_matters",
                "Understanding this issue will help you write better code.",
            ),
            suggested_improvement=c.get(
                "suggested_improvement",
                "Consider refactoring this section for clarity.",
            ),
            engineering_principle=c.get(
                "engineering_principle",
                "General best practice.",
            ),
        )
        critiques.append(item.model_dump())

    # Build LearningReport
    lr = LearningReport(
        code_quality_score=learning_report_raw.get("code_quality_score", 0),
        strengths=learning_report_raw.get("strengths", []),
        improvement_areas=learning_report_raw.get("improvement_areas", []),
        engineering_concepts=learning_report_raw.get("engineering_concepts", []),
        personalized_recommendation=learning_report_raw.get(
            "personalized_recommendation",
            "Keep practising — code reviews are the best way to improve.",
        ),
    )

    # Assemble the full ReviewResponse for validation
    response = ReviewResponse(
        summary=parsed.get(
            "summary",
            {
                "overall_assessment": "Review completed.",
                "key_takeaway": "Keep learning and improving.",
            },
        ),
        learning_report=lr,
        critiques=[CritiqueItem(**c) for c in critiques],
        reflection=parsed.get(
            "reflection",
            {
                "prompt_1": "What engineering issue do you believe has the greatest impact on your code quality?",
                "prompt_2": "Predict one improvement you would personally make before viewing the solution.",
            },
        ),
        optimized_solution=parsed.get(
            "optimized_solution",
            request.code,
        ),
        session_summary=parsed.get(
            "session_summary",
            {
                "language": request.language,
                "persona": request.persona,
                "total_issues": len(critiques),
                "overall_sentiment": "neutral",
            },
        ),
    )

    # Build validated ReviewResponse dict, preserving the exact model schema.
    result = response.model_dump()
    result["critiques"] = critiques

    return result


# ---------------------------------------------------------------------------
# API endpoint
# ---------------------------------------------------------------------------

@app.post("/api/review", response_model=None)
async def review_code(request: CodeRequest) -> dict:
    """
    Accept code submission, orchestrate the LLM call with persona-aware
    prompts, enforce JSON output, and return a strictly validated
    ReviewResponse.
    """
    logger.info(
        "Review request: persona=%s language=%s code_length=%d",
        request.persona,
        request.language,
        len(request.code),
    )

    system_prompt = _build_system_prompt(request.persona)
    user_prompt = _build_user_prompt(request)

    try:
        parsed = await _call_llm(system_prompt, user_prompt)
        result = _build_response(parsed, request)
        logger.info(
            "Review complete: %d critiques, score=%d",
            len(result["critiques"]),
            result["learning_report"]["code_quality_score"],
        )
        return result

    except RuntimeError as exc:
        logger.error("LLM call failed after all retries: %s", exc)
        return _fallback_review_response(
            request, "The AI review engine is temporarily unavailable."
        )

    except Exception as exc:
        logger.exception("Unexpected error in review_code")
        return _fallback_review_response(
            request,
            "An unexpected error occurred. Please try again.",
        )


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/health")
async def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logger.info("Starting DevSpark API on %s:%s", APP_HOST, APP_PORT)
    uvicorn.run(
        "main:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=False,
        log_level="info",
    )