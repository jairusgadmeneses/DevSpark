"""P0 fixes verification — runs without any API key."""

import os
import sys

# Make sure we can import main.py from the backend directory.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# The backend imports openai, so set a dummy key to avoid import-time errors.
os.environ.setdefault("ZENMUX_API_KEY", "dummy-key-for-testing")

from main import _build_response, CodeRequest, ReviewResponse


def test_canonical_response_schema():
    """Backend must return the canonical ReviewResponse schema without aliases."""
    parsed = {
        "summary": {
            "overall_assessment": "Good start, room to grow.",
            "key_takeaway": "Focus on readability and error handling.",
        },
        "critiques": [
            {
                "line": 3,
                "severity": "warning",
                "explanation": "The variable name is unclear.",
                "why_it_matters": "Naming affects maintainability.",
                "suggested_improvement": "Use a descriptive name like `user_count`.",
                "engineering_principle": "Readability",
            }
        ],
        "learning_report": {
            "code_quality_score": 78,
            "strengths": ["Clear structure"],
            "improvement_areas": ["Naming", "Error handling"],
            "engineering_concepts": ["Readability", "Defensive Programming"],
            "personalized_recommendation": "Refactor variable names before adding features.",
        },
        "reflection": {
            "prompt_1": "What issue matters most?",
            "prompt_2": "What would you improve first?",
        },
        "optimized_solution": "# Optimized code\nuser_count = 0\n",
        "session_summary": {
            "language": "python",
            "persona": "mentor",
            "total_issues": 1,
            "overall_sentiment": "neutral",
        },
    }

    request = CodeRequest(code="x = 0", language="python", persona="mentor")
    result = _build_response(parsed, request)

    # Validate the returned shape against the canonical schema
    validated = ReviewResponse(**result)

    # No duplicate aliases
    assert "optimized_code" not in result, "optimized_code alias must not be present"
    assert "message" not in result["critiques"][0], "critique message alias must not be present"

    # Learning report uses canonical keys
    lr = result["learning_report"]
    assert lr["code_quality_score"] == 78
    assert lr["improvement_areas"] == ["Naming", "Error handling"]
    assert lr["engineering_concepts"] == ["Readability", "Defensive Programming"]
    assert lr["personalized_recommendation"].startswith("Refactor")

    # Optimized solution present under canonical key
    assert result["optimized_solution"] == "# Optimized code\nuser_count = 0\n"

    # Critiques use canonical explanation
    assert result["critiques"][0]["explanation"] == "The variable name is unclear."

    print("test_canonical_response_schema: PASSED")


def test_fallback_response_schema():
    """Fallback response must also conform to the canonical schema."""
    from main import _fallback_review_response

    request = CodeRequest(code="x = 0", language="python", persona="mentor")
    result = _fallback_review_response(request, "service unavailable")

    ReviewResponse(**result)
    assert result["learning_report"]["code_quality_score"] == 0
    assert "optimized_code" not in result
    assert result["optimized_solution"] == request.code

    print("test_fallback_response_schema: PASSED")


if __name__ == "__main__":
    test_canonical_response_schema()
    test_fallback_response_schema()
    print("\nAll backend P0 verification tests passed.")
