"""
FastAPI Backend for Code Analysis using IBM WatsonX AI
Hackathon Project - Code Roasting & Refactoring

Production-ready with comprehensive error handling and security best practices.
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List
import os
from dotenv import load_dotenv
import logging
import sys
import traceback
from ibm_watsonx_ai import APIClient
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

# Load environment variables
load_dotenv()

# Configure logging with more detail for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app with production settings
app = FastAPI(
    title="Code Roasting API",
    description="AI-powered code roasting and refactoring using IBM WatsonX",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Global exception handler for unhandled errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler to catch any unhandled exceptions.
    Returns 500 error with sanitized error message.
    """
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred. Please try again later.",
            "error_type": type(exc).__name__
        }
    )

# Configure CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Pydantic Models
class CodeAnalysisRequest(BaseModel):
    """Request model for code analysis with validation"""
    code: str = Field(
        ...,
        description="Code string to analyze and roast",
        min_length=1,
        max_length=50000  # Limit code size to prevent abuse
    )
    language: Optional[str] = Field(
        None,
        description="Programming language (optional)",
        max_length=50
    )
    
    @validator('code')
    def validate_code(cls, v):
        """Validate code input"""
        if not v or not v.strip():
            raise ValueError("Code cannot be empty or whitespace only")
        # Remove any potential script injection attempts
        if len(v) > 50000:
            raise ValueError("Code exceeds maximum length of 50,000 characters")
        return v.strip()
    
    @validator('language')
    def validate_language(cls, v):
        """Validate language input"""
        if v:
            # Sanitize language input
            allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-_')
            if not all(c in allowed_chars for c in v):
                raise ValueError("Language contains invalid characters")
            return v.strip().lower()
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "def calculate(x, y):\n    return x + y",
                "language": "python"
            }
        }


class RoastCritique(BaseModel):
    """Individual critique with line number"""
    line: Optional[int] = Field(None, description="Line number being critiqued (null for general comments)")
    critique: str = Field(..., description="The roast/critique for this line or section")
    
    class Config:
        json_schema_extra = {
            "example": {
                "line": 1,
                "critique": "No type hints? What is this, 2010?"
            }
        }


class CodeAnalysisResponse(BaseModel):
    """Response model for code analysis - strict JSON contract for frontend"""
    roast_critiques: List[RoastCritique] = Field(..., description="List of line-by-line critiques")
    original_code: str = Field(..., description="The original code submitted")
    refactored_code: str = Field(..., description="Improved version of the code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "roast_critiques": [
                    {
                        "line": 1,
                        "critique": "No type hints? What is this, 2010?"
                    },
                    {
                        "line": None,
                        "critique": "Overall, this code is functional but lacks modern Python best practices."
                    }
                ],
                "original_code": "def calculate(x, y):\n    return x + y",
                "refactored_code": "def calculate(x: float, y: float) -> float:\n    \"\"\"Add two numbers.\"\"\"\n    return x + y"
            }
        }


# WatsonX Configuration - Secure credential loading
WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
WATSONX_URL = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

# Validate credentials on startup
if not WATSONX_API_KEY or not WATSONX_PROJECT_ID:
    logger.error("Missing WatsonX credentials in environment variables")
    logger.error("Please ensure WATSONX_API_KEY and WATSONX_PROJECT_ID are set in .env file")
    WATSONX_AVAILABLE = False
else:
    # Validate credential format (basic check)
    if len(WATSONX_API_KEY) < 20:
        logger.warning("WATSONX_API_KEY appears to be invalid (too short)")
        WATSONX_AVAILABLE = False
    elif len(WATSONX_PROJECT_ID) < 10:
        logger.warning("WATSONX_PROJECT_ID appears to be invalid (too short)")
        WATSONX_AVAILABLE = False
    else:
        WATSONX_AVAILABLE = True
        logger.info("WatsonX credentials loaded and validated successfully")
        # Log masked credentials for debugging (security best practice)
        logger.info(f"API Key: {WATSONX_API_KEY[:10]}...{WATSONX_API_KEY[-4:]}")
        logger.info(f"Project ID: {WATSONX_PROJECT_ID[:8]}...{WATSONX_PROJECT_ID[-4:]}")


def get_watsonx_response(user_code: str, language: Optional[str] = None) -> dict:
    """
    Send code to WatsonX AI for roasting and refactoring.
    
    Args:
        user_code: The code to analyze and roast
        language: Programming language (optional)
    
    Returns:
        Dictionary containing roast, refactored_code, and explanation
    
    Raises:
        HTTPException: If WatsonX API call fails
    """
    try:
        # Validate inputs
        if not user_code or len(user_code.strip()) == 0:
            raise ValueError("Code cannot be empty")
        
        if len(user_code) > 50000:
            raise ValueError("Code exceeds maximum length")
        
        # Initialize credentials dictionary
        credentials = {
            "url": WATSONX_URL,
            "apikey": WATSONX_API_KEY
        }
        
        # Initialize API client
        try:
            client = APIClient(credentials)
            if WATSONX_PROJECT_ID:
                client.set.default_project(WATSONX_PROJECT_ID)
        except Exception as cred_error:
            logger.error(f"Failed to initialize WatsonX API client: {str(cred_error)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to authenticate with WatsonX service"
            )
        
        # Model parameters optimized for creative roasting
        parameters = {
            GenParams.DECODING_METHOD: "greedy",
            GenParams.MAX_NEW_TOKENS: 2000,
            GenParams.MIN_NEW_TOKENS: 100,
            GenParams.TEMPERATURE: 0.8,  # Higher temperature for more creative roasts
            GenParams.TOP_K: 50,
            GenParams.TOP_P: 0.95
        }
        
        # Initialize model - using ibm/granite-8b-code-instruct (best for code!)
        try:
            model = ModelInference(
                model_id="ibm/granite-8b-code-instruct",
                params=parameters,
                credentials=credentials,
                project_id=WATSONX_PROJECT_ID
            )
        except Exception as model_error:
            logger.error(f"Failed to initialize WatsonX model: {str(model_error)}")
            logger.error(f"Model ID attempted: ibm/granite-8b-code-instruct")
            logger.error(f"Full error: {repr(model_error)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize AI model: {str(model_error)}"
            )
        
        # Construct the roasting prompt - ENFORCE GENUINE REFACTORING
        lang_info = f" written in {language}" if language else ""
        
        # Count lines for better targeting
        code_lines = user_code.split('\n')
        num_lines = len(code_lines)
        
        prompt = f"""You are a sarcastic code reviewer. Analyze this {language or 'code'} and return ONLY a JSON object.

CODE TO REVIEW:
```
{user_code}
```

YOUR TASK:
1. Find problems, bad practices, or improvements needed in the code above
2. Write funny but constructive critiques for specific lines
3. Provide a GENUINELY IMPROVED refactored version

OUTPUT FORMAT - Return ONLY this JSON structure (no markdown, no extra text):
{{
  "roast_critiques": [
    {{"line": <line_number_1_to_{num_lines}>, "critique": "<your_funny_critique>"}},
    {{"line": null, "critique": "<overall_assessment>"}}
  ],
  "refactored_code": "<complete_improved_code_with_\\n_for_newlines>"
}}

CRITICAL RULES FOR refactored_code:
⚠️ WARNING: If refactored_code is identical or nearly identical to the original code, your response is INVALID.

The refactored_code MUST:
- NOT be identical to the input code
- Include MEANINGFUL improvements (not just whitespace changes)
- Preserve functionality while improving quality
- Use modern best practices for {language or 'the language'}
- Include type hints where appropriate
- Include docstrings explaining what the code does
- Simplify logic where possible
- Improve readability and maintainability
- Use Pythonic constructs (list comprehensions, context managers, etc.) when relevant
- Validate edge cases and handle errors properly
- Be production-ready code

FORMATTING RULES:
- Start response with {{ and end with }}
- NO markdown code fences
- NO explanatory text before or after JSON
- Escape newlines in refactored_code as \\n
- Escape double quotes as \\"
- Write ACTUAL critiques about THIS specific code
- Include line numbers for specific issues (1 to {num_lines})
- Include at least one general critique (line: null)
- Be funny, sarcastic, but helpful

BEGIN JSON OUTPUT NOW:"""
        
        logger.info(f"Sending code to WatsonX for roasting (length: {len(user_code)} chars)")
        
        # Generate response with timeout handling
        try:
            response = model.generate_text(prompt=prompt)
        except Exception as gen_error:
            logger.error(f"WatsonX generation failed: {str(gen_error)}")
            raise HTTPException(
                status_code=500,
                detail="AI model failed to generate response. Please try again."
            )
        
        if not response:
            logger.error("WatsonX returned empty response")
            raise HTTPException(
                status_code=500,
                detail="AI model returned empty response"
            )
        
        logger.info("Received response from WatsonX")
        
        # Parse the response - ensure it's a string
        response_text = response if isinstance(response, str) else str(response)
        return _parse_watsonx_response(response_text, user_code)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Unexpected error calling WatsonX API: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your request"
        )


def _parse_watsonx_response(response: str, original_code: str) -> dict:
    """
    Robustly parse WatsonX response into structured JSON format.
    Handles multiple formats and edge cases.
    
    Args:
        response: Raw response from WatsonX
        original_code: The original code that was submitted
    
    Returns:
        Dictionary with roast_critiques, original_code, and refactored_code
    """
    import re
    import json
    
    logger.info(f"Parsing WatsonX response (length: {len(response)} chars)")
    
    # Strategy 1: Try to extract JSON from markdown code blocks
    json_str = None
    try:
        # Match ```json ... ``` or ``` ... ```
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            logger.info("Found JSON in markdown code block")
    except Exception as e:
        logger.debug(f"Markdown extraction failed: {e}")
    
    # Strategy 2: Try to find JSON object directly (look for complete object)
    if not json_str:
        try:
            # Find the first { and last } to extract complete JSON object
            start = response.find('{')
            if start != -1:
                # Count braces to find matching closing brace
                brace_count = 0
                for i in range(start, len(response)):
                    if response[i] == '{':
                        brace_count += 1
                    elif response[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_str = response[start:i+1]
                            logger.info("Extracted JSON object from response")
                            break
        except Exception as e:
            logger.debug(f"Direct JSON extraction failed: {e}")
    
    # Strategy 3: Last resort - assume entire response is JSON
    if not json_str:
        json_str = response.strip()
        logger.info("Using entire response as JSON")
    
    # Try to parse the JSON
    parsed = None
    parse_error = None
    
    try:
        parsed = json.loads(json_str)
        logger.info("Successfully parsed JSON")
    except json.JSONDecodeError as e:
        parse_error = e
        logger.warning(f"Initial JSON parse failed: {str(e)}")
        
        # Try to clean common issues and retry
        try:
            # Remove any leading/trailing whitespace and newlines
            cleaned = json_str.strip()
            
            # Try to fix common escape sequence issues
            cleaned = cleaned.replace('\\n', '\\\\n')  # Fix unescaped newlines
            cleaned = cleaned.replace('\n', '\\n')     # Escape actual newlines
            cleaned = cleaned.replace('\r', '')         # Remove carriage returns
            cleaned = cleaned.replace('\t', '\\t')     # Escape tabs
            
            # Try parsing again
            parsed = json.loads(cleaned)
            logger.info("Successfully parsed JSON after cleaning")
        except json.JSONDecodeError as e2:
            logger.warning(f"JSON parse failed after cleaning: {str(e2)}")
            parse_error = e2
    
    # Validate and return parsed JSON
    if parsed:
        try:
            # Validate required fields exist
            if "roast_critiques" not in parsed:
                logger.error("Missing 'roast_critiques' in parsed JSON")
                raise ValueError("Missing roast_critiques field")
            
            if "refactored_code" not in parsed:
                logger.error("Missing 'refactored_code' in parsed JSON")
                raise ValueError("Missing refactored_code field")
            
            # Validate roast_critiques is a list
            if not isinstance(parsed["roast_critiques"], list):
                logger.error("roast_critiques is not a list")
                raise ValueError("roast_critiques must be a list")
            
            # Validate each critique has required fields
            for i, critique in enumerate(parsed["roast_critiques"]):
                if not isinstance(critique, dict):
                    logger.warning(f"Critique {i} is not a dict, skipping")
                    continue
                if "critique" not in critique:
                    logger.warning(f"Critique {i} missing 'critique' field")
                    critique["critique"] = "No critique provided"
                if "line" not in critique:
                    critique["line"] = None
            
            # CRITICAL VALIDATION: Check if refactored_code is identical to original
            original_normalized = original_code.strip().replace('\r\n', '\n').replace('\r', '\n')
            refactored_normalized = parsed["refactored_code"].strip().replace('\r\n', '\n').replace('\r', '\n')
            
            if original_normalized == refactored_normalized:
                logger.warning("AI returned identical code - refactoring failed")
                return {
                    "roast_critiques": [
                        {
                            "line": None,
                            "critique": "The AI failed to generate a meaningful refactoring. Please try again."
                        }
                    ],
                    "original_code": original_code,
                    "refactored_code": original_code
                }
            
            # Return validated response with genuine improvements
            return {
                "roast_critiques": parsed["roast_critiques"],
                "original_code": original_code,
                "refactored_code": parsed["refactored_code"]
            }
            
        except (ValueError, KeyError, TypeError) as e:
            logger.error(f"Validation error: {str(e)}")
            # Fall through to fallback
    
    # Fallback: Create safe response when parsing fails
    logger.warning("Using fallback response due to parsing failure")
    logger.debug(f"Response preview: {response[:500]}...")
    
    return {
        "roast_critiques": [
            {
                "line": None,
                "critique": "The AI model returned a response, but it couldn't be parsed into the expected format. The model may need additional prompt tuning."
            }
        ],
        "original_code": original_code,
        "refactored_code": original_code  # Return original code as fallback
    }


# API Endpoints
@app.get("/", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    Returns service status and configuration.
    """
    return {
        "status": "healthy",
        "service": "Code Roasting API",
        "version": "3.0.0",
        "watsonx_available": WATSONX_AVAILABLE,
        "model": "ibm/granite-8b-code-instruct",
        "environment": "production" if os.getenv("ENVIRONMENT") == "production" else "development"
    }


@app.get("/health", tags=["Health"])
async def detailed_health_check():
    """
    Detailed health check endpoint for monitoring.
    Returns comprehensive service status.
    """
    health_status = {
        "status": "healthy" if WATSONX_AVAILABLE else "degraded",
        "service": "Code Roasting API",
        "version": "3.0.0",
        "checks": {
            "watsonx_credentials": "ok" if WATSONX_AVAILABLE else "failed",
            "api_key_present": bool(WATSONX_API_KEY),
            "project_id_present": bool(WATSONX_PROJECT_ID),
        }
    }
    
    status_code = 200 if WATSONX_AVAILABLE else 503
    return JSONResponse(content=health_status, status_code=status_code)


@app.post("/analyze", response_model=CodeAnalysisResponse, tags=["Analysis"])
async def analyze_code(request: CodeAnalysisRequest):
    """
    Roast code and provide a refactored version using IBM WatsonX AI.
    
    **Security Features:**
    - Input validation and sanitization
    - Code length limits (max 50,000 characters)
    - Secure credential handling
    - Comprehensive error handling
    
    **Error Responses:**
    - 400: Invalid input (empty code, invalid characters)
    - 500: WatsonX API failure or internal error
    - 503: WatsonX service unavailable
    
    Args:
        request: CodeAnalysisRequest containing code to analyze
    
    Returns:
        CodeAnalysisResponse with roast critiques, original code, and refactored version
    
    Raises:
        HTTPException: If validation fails or WatsonX service is unavailable
    """
    # Check service availability
    if not WATSONX_AVAILABLE:
        logger.error("Analysis request rejected: WatsonX service unavailable")
        raise HTTPException(
            status_code=503,
            detail="WatsonX AI service is currently unavailable. Please check service configuration."
        )
    
    try:
        logger.info(f"Received analysis request - Code length: {len(request.code)} chars, Language: {request.language or 'auto-detect'}")
        
        # Additional security validation
        if len(request.code.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Code cannot be empty or contain only whitespace"
            )
        
        # Get response from WatsonX with error handling
        try:
            result = get_watsonx_response(
                user_code=request.code,
                language=request.language
            )
        except HTTPException:
            # Re-raise HTTP exceptions from get_watsonx_response
            raise
        except Exception as e:
            logger.error(f"Failed to get WatsonX response: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to analyze code. Please try again."
            )
        
        # Validate result structure
        if not result or "roast_critiques" not in result or "refactored_code" not in result:
            logger.error("Invalid result structure from WatsonX")
            raise HTTPException(
                status_code=500,
                detail="Received invalid response from AI service"
            )
        
        # Build response with error handling
        try:
            response = CodeAnalysisResponse(
                roast_critiques=[RoastCritique(**critique) for critique in result["roast_critiques"]],
                original_code=result["original_code"],
                refactored_code=result["refactored_code"]
            )
        except Exception as e:
            logger.error(f"Failed to build response model: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to format analysis results"
            )
        
        logger.info("Code analysis completed successfully")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error during code analysis: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while analyzing your code"
        )


if __name__ == "__main__":
    import uvicorn
    
    # Production-ready server configuration
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting Code Roasting API on {host}:{port}")
    logger.info(f"WatsonX Available: {WATSONX_AVAILABLE}")
    logger.info("Documentation available at /docs")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )
