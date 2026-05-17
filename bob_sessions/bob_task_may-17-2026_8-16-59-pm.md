**User:**

<task>
Bob, look at main.py and index.html. I need you to wire the frontend to the backend. In index.html, remove the mockResponse variable and the setTimeout simulation. Rewrite the handleRoastClick() and displayResults() JavaScript functions so they make a real asynchronous fetch() POST request to http://localhost:8000/analyze. Pass the code from the textarea, and ensure you correctly map the backend Pydantic line integer to the UI instead of the old lines string. Do not change any HTML layout or CSS.
</task>
<environment_details>
# VSCode Visible Files
main.py

# VSCode Open Tabs
index.html,main.py,.env

# Current Time
Current time in ISO 8601 UTC format: 2026-05-17T12:15:10.634Z
User time zone: Asia/Singapore, UTC+8:00

# Current Cost
$0.00

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>


# Current Workspace Directory (d:/User/Downloads/DevSpark) Files
.env
index.html
main.py
requirements.txt
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

I'll help you wire the frontend to the backend. Let me start by reading both files to understand the current implementation.

<read_file>
<args>
<file>
<path>main.py</path>
</file>
<file>
<path>index.html</path>
</file>
</args>
</read_file>

---

**User:**

[read_file for 'main.py', 'index.html'] Result:
<files>
<file><path>main.py</path>
<content lines="1-657">
  1 | """
  2 | FastAPI Backend for Code Analysis using IBM WatsonX AI
  3 | Hackathon Project - Code Roasting & Refactoring
  4 | 
  5 | Production-ready with comprehensive error handling and security best practices.
  6 | """
  7 | 
  8 | from fastapi import FastAPI, HTTPException, Request, status
  9 | from fastapi.middleware.cors import CORSMiddleware
 10 | from fastapi.responses import JSONResponse
 11 | from pydantic import BaseModel, Field, validator
 12 | from typing import Optional, List
 13 | import os
 14 | from dotenv import load_dotenv
 15 | import logging
 16 | import sys
 17 | import traceback
 18 | from ibm_watsonx_ai import APIClient
 19 | from ibm_watsonx_ai.foundation_models import ModelInference
 20 | from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
 21 | 
 22 | # Load environment variables
 23 | load_dotenv()
 24 | 
 25 | # Configure logging with more detail for production
 26 | logging.basicConfig(
 27 |     level=logging.INFO,
 28 |     format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
 29 |     handlers=[
 30 |         logging.StreamHandler(sys.stdout)
 31 |     ]
 32 | )
 33 | logger = logging.getLogger(__name__)
 34 | 
 35 | # Initialize FastAPI app with production settings
 36 | app = FastAPI(
 37 |     title="Code Roasting API",
 38 |     description="AI-powered code roasting and refactoring using IBM WatsonX",
 39 |     version="3.0.0",
 40 |     docs_url="/docs",
 41 |     redoc_url="/redoc",
 42 |     openapi_url="/openapi.json"
 43 | )
 44 | 
 45 | # Global exception handler for unhandled errors
 46 | @app.exception_handler(Exception)
 47 | async def global_exception_handler(request: Request, exc: Exception):
 48 |     """
 49 |     Global exception handler to catch any unhandled exceptions.
 50 |     Returns 500 error with sanitized error message.
 51 |     """
 52 |     logger.error(f"Unhandled exception: {str(exc)}")
 53 |     logger.error(traceback.format_exc())
 54 |     
 55 |     return JSONResponse(
 56 |         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
 57 |         content={
 58 |             "detail": "An internal server error occurred. Please try again later.",
 59 |             "error_type": type(exc).__name__
 60 |         }
 61 |     )
 62 | 
 63 | # Configure CORS for development
 64 | app.add_middleware(
 65 |     CORSMiddleware,
 66 |     allow_origins=["*"],  # Allow all origins for development
 67 |     allow_credentials=True,
 68 |     allow_methods=["*"],  # Allow all methods
 69 |     allow_headers=["*"],  # Allow all headers
 70 | )
 71 | 
 72 | # Pydantic Models
 73 | class CodeAnalysisRequest(BaseModel):
 74 |     """Request model for code analysis with validation"""
 75 |     code: str = Field(
 76 |         ...,
 77 |         description="Code string to analyze and roast",
 78 |         min_length=1,
 79 |         max_length=50000  # Limit code size to prevent abuse
 80 |     )
 81 |     language: Optional[str] = Field(
 82 |         None,
 83 |         description="Programming language (optional)",
 84 |         max_length=50
 85 |     )
 86 |     
 87 |     @validator('code')
 88 |     def validate_code(cls, v):
 89 |         """Validate code input"""
 90 |         if not v or not v.strip():
 91 |             raise ValueError("Code cannot be empty or whitespace only")
 92 |         # Remove any potential script injection attempts
 93 |         if len(v) > 50000:
 94 |             raise ValueError("Code exceeds maximum length of 50,000 characters")
 95 |         return v.strip()
 96 |     
 97 |     @validator('language')
 98 |     def validate_language(cls, v):
 99 |         """Validate language input"""
100 |         if v:
101 |             # Sanitize language input
102 |             allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-_')
103 |             if not all(c in allowed_chars for c in v):
104 |                 raise ValueError("Language contains invalid characters")
105 |             return v.strip().lower()
106 |         return v
107 |     
108 |     class Config:
109 |         json_schema_extra = {
110 |             "example": {
111 |                 "code": "def calculate(x, y):\n    return x + y",
112 |                 "language": "python"
113 |             }
114 |         }
115 | 
116 | 
117 | class RoastCritique(BaseModel):
118 |     """Individual critique with line number"""
119 |     line: Optional[int] = Field(None, description="Line number being critiqued (null for general comments)")
120 |     critique: str = Field(..., description="The roast/critique for this line or section")
121 |     
122 |     class Config:
123 |         json_schema_extra = {
124 |             "example": {
125 |                 "line": 1,
126 |                 "critique": "No type hints? What is this, 2010?"
127 |             }
128 |         }
129 | 
130 | 
131 | class CodeAnalysisResponse(BaseModel):
132 |     """Response model for code analysis - strict JSON contract for frontend"""
133 |     roast_critiques: List[RoastCritique] = Field(..., description="List of line-by-line critiques")
134 |     original_code: str = Field(..., description="The original code submitted")
135 |     refactored_code: str = Field(..., description="Improved version of the code")
136 |     
137 |     class Config:
138 |         json_schema_extra = {
139 |             "example": {
140 |                 "roast_critiques": [
141 |                     {
142 |                         "line": 1,
143 |                         "critique": "No type hints? What is this, 2010?"
144 |                     },
145 |                     {
146 |                         "line": None,
147 |                         "critique": "Overall, this code is functional but lacks modern Python best practices."
148 |                     }
149 |                 ],
150 |                 "original_code": "def calculate(x, y):\n    return x + y",
151 |                 "refactored_code": "def calculate(x: float, y: float) -> float:\n    \"\"\"Add two numbers.\"\"\"\n    return x + y"
152 |             }
153 |         }
154 | 
155 | 
156 | # WatsonX Configuration - Secure credential loading
157 | WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")
158 | WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
159 | WATSONX_URL = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
160 | 
161 | # Validate credentials on startup
162 | if not WATSONX_API_KEY or not WATSONX_PROJECT_ID:
163 |     logger.error("Missing WatsonX credentials in environment variables")
164 |     logger.error("Please ensure WATSONX_API_KEY and WATSONX_PROJECT_ID are set in .env file")
165 |     WATSONX_AVAILABLE = False
166 | else:
167 |     # Validate credential format (basic check)
168 |     if len(WATSONX_API_KEY) < 20:
169 |         logger.warning("WATSONX_API_KEY appears to be invalid (too short)")
170 |         WATSONX_AVAILABLE = False
171 |     elif len(WATSONX_PROJECT_ID) < 10:
172 |         logger.warning("WATSONX_PROJECT_ID appears to be invalid (too short)")
173 |         WATSONX_AVAILABLE = False
174 |     else:
175 |         WATSONX_AVAILABLE = True
176 |         logger.info("WatsonX credentials loaded and validated successfully")
177 |         # Log masked credentials for debugging (security best practice)
178 |         logger.info(f"API Key: {WATSONX_API_KEY[:10]}...{WATSONX_API_KEY[-4:]}")
179 |         logger.info(f"Project ID: {WATSONX_PROJECT_ID[:8]}...{WATSONX_PROJECT_ID[-4:]}")
180 | 
181 | 
182 | def get_watsonx_response(user_code: str, language: Optional[str] = None) -> dict:
183 |     """
184 |     Send code to WatsonX AI for roasting and refactoring.
185 |     
186 |     Args:
187 |         user_code: The code to analyze and roast
188 |         language: Programming language (optional)
189 |     
190 |     Returns:
191 |         Dictionary containing roast, refactored_code, and explanation
192 |     
193 |     Raises:
194 |         HTTPException: If WatsonX API call fails
195 |     """
196 |     try:
197 |         # Validate inputs
198 |         if not user_code or len(user_code.strip()) == 0:
199 |             raise ValueError("Code cannot be empty")
200 |         
201 |         if len(user_code) > 50000:
202 |             raise ValueError("Code exceeds maximum length")
203 |         
204 |         # Initialize credentials dictionary
205 |         credentials = {
206 |             "url": WATSONX_URL,
207 |             "apikey": WATSONX_API_KEY
208 |         }
209 |         
210 |         # Initialize API client
211 |         try:
212 |             client = APIClient(credentials)
213 |             if WATSONX_PROJECT_ID:
214 |                 client.set.default_project(WATSONX_PROJECT_ID)
215 |         except Exception as cred_error:
216 |             logger.error(f"Failed to initialize WatsonX API client: {str(cred_error)}")
217 |             raise HTTPException(
218 |                 status_code=500,
219 |                 detail="Failed to authenticate with WatsonX service"
220 |             )
221 |         
222 |         # Model parameters optimized for creative roasting
223 |         parameters = {
224 |             GenParams.DECODING_METHOD: "greedy",
225 |             GenParams.MAX_NEW_TOKENS: 2000,
226 |             GenParams.MIN_NEW_TOKENS: 100,
227 |             GenParams.TEMPERATURE: 0.8,  # Higher temperature for more creative roasts
228 |             GenParams.TOP_K: 50,
229 |             GenParams.TOP_P: 0.95
230 |         }
231 |         
232 |         # Initialize model - using ibm/granite-8b-code-instruct (best for code!)
233 |         try:
234 |             model = ModelInference(
235 |                 model_id="ibm/granite-8b-code-instruct",
236 |                 params=parameters,
237 |                 credentials=credentials,
238 |                 project_id=WATSONX_PROJECT_ID
239 |             )
240 |         except Exception as model_error:
241 |             logger.error(f"Failed to initialize WatsonX model: {str(model_error)}")
242 |             logger.error(f"Model ID attempted: ibm/granite-8b-code-instruct")
243 |             logger.error(f"Full error: {repr(model_error)}")
244 |             import traceback
245 |             logger.error(f"Traceback: {traceback.format_exc()}")
246 |             raise HTTPException(
247 |                 status_code=500,
248 |                 detail=f"Failed to initialize AI model: {str(model_error)}"
249 |             )
250 |         
251 |         # Construct the roasting prompt - ENFORCE GENUINE REFACTORING
252 |         lang_info = f" written in {language}" if language else ""
253 |         
254 |         # Count lines for better targeting
255 |         code_lines = user_code.split('\n')
256 |         num_lines = len(code_lines)
257 |         
258 |         prompt = f"""You are a sarcastic code reviewer. Analyze this {language or 'code'} and return ONLY a JSON object.
259 | 
260 | CODE TO REVIEW:
261 | ```
262 | {user_code}
263 | ```
264 | 
265 | YOUR TASK:
266 | 1. Find problems, bad practices, or improvements needed in the code above
267 | 2. Write funny but constructive critiques for specific lines
268 | 3. Provide a GENUINELY IMPROVED refactored version
269 | 
270 | OUTPUT FORMAT - Return ONLY this JSON structure (no markdown, no extra text):
271 | {{
272 |   "roast_critiques": [
273 |     {{"line": <line_number_1_to_{num_lines}>, "critique": "<your_funny_critique>"}},
274 |     {{"line": null, "critique": "<overall_assessment>"}}
275 |   ],
276 |   "refactored_code": "<complete_improved_code_with_\\n_for_newlines>"
277 | }}
278 | 
279 | CRITICAL RULES FOR refactored_code:
280 | ⚠️ WARNING: If refactored_code is identical or nearly identical to the original code, your response is INVALID.
281 | 
282 | The refactored_code MUST:
283 | - NOT be identical to the input code
284 | - Include MEANINGFUL improvements (not just whitespace changes)
285 | - Preserve functionality while improving quality
286 | - Use modern best practices for {language or 'the language'}
287 | - Include type hints where appropriate
288 | - Include docstrings explaining what the code does
289 | - Simplify logic where possible
290 | - Improve readability and maintainability
291 | - Use Pythonic constructs (list comprehensions, context managers, etc.) when relevant
292 | - Validate edge cases and handle errors properly
293 | - Be production-ready code
294 | 
295 | FORMATTING RULES:
296 | - Start response with {{ and end with }}
297 | - NO markdown code fences
298 | - NO explanatory text before or after JSON
299 | - Escape newlines in refactored_code as \\n
300 | - Escape double quotes as \\"
301 | - Write ACTUAL critiques about THIS specific code
302 | - Include line numbers for specific issues (1 to {num_lines})
303 | - Include at least one general critique (line: null)
304 | - Be funny, sarcastic, but helpful
305 | 
306 | BEGIN JSON OUTPUT NOW:"""
307 |         
308 |         logger.info(f"Sending code to WatsonX for roasting (length: {len(user_code)} chars)")
309 |         
310 |         # Generate response with timeout handling
311 |         try:
312 |             response = model.generate_text(prompt=prompt)
313 |         except Exception as gen_error:
314 |             logger.error(f"WatsonX generation failed: {str(gen_error)}")
315 |             raise HTTPException(
316 |                 status_code=500,
317 |                 detail="AI model failed to generate response. Please try again."
318 |             )
319 |         
320 |         if not response:
321 |             logger.error("WatsonX returned empty response")
322 |             raise HTTPException(
323 |                 status_code=500,
324 |                 detail="AI model returned empty response"
325 |             )
326 |         
327 |         logger.info("Received response from WatsonX")
328 |         
329 |         # Parse the response - ensure it's a string
330 |         response_text = response if isinstance(response, str) else str(response)
331 |         return _parse_watsonx_response(response_text, user_code)
332 |         
333 |     except HTTPException:
334 |         # Re-raise HTTP exceptions
335 |         raise
336 |     except ValueError as ve:
337 |         logger.error(f"Validation error: {str(ve)}")
338 |         raise HTTPException(
339 |             status_code=400,
340 |             detail=str(ve)
341 |         )
342 |     except Exception as e:
343 |         logger.error(f"Unexpected error calling WatsonX API: {str(e)}")
344 |         logger.error(traceback.format_exc())
345 |         raise HTTPException(
346 |             status_code=500,
347 |             detail="An unexpected error occurred while processing your request"
348 |         )
349 | 
350 | 
351 | def _parse_watsonx_response(response: str, original_code: str) -> dict:
352 |     """
353 |     Robustly parse WatsonX response into structured JSON format.
354 |     Handles multiple formats and edge cases.
355 |     
356 |     Args:
357 |         response: Raw response from WatsonX
358 |         original_code: The original code that was submitted
359 |     
360 |     Returns:
361 |         Dictionary with roast_critiques, original_code, and refactored_code
362 |     """
363 |     import re
364 |     import json
365 |     
366 |     logger.info(f"Parsing WatsonX response (length: {len(response)} chars)")
367 |     
368 |     # Strategy 1: Try to extract JSON from markdown code blocks
369 |     json_str = None
370 |     try:
371 |         # Match ```json ... ``` or ``` ... ```
372 |         json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
373 |         if json_match:
374 |             json_str = json_match.group(1)
375 |             logger.info("Found JSON in markdown code block")
376 |     except Exception as e:
377 |         logger.debug(f"Markdown extraction failed: {e}")
378 |     
379 |     # Strategy 2: Try to find JSON object directly (look for complete object)
380 |     if not json_str:
381 |         try:
382 |             # Find the first { and last } to extract complete JSON object
383 |             start = response.find('{')
384 |             if start != -1:
385 |                 # Count braces to find matching closing brace
386 |                 brace_count = 0
387 |                 for i in range(start, len(response)):
388 |                     if response[i] == '{':
389 |                         brace_count += 1
390 |                     elif response[i] == '}':
391 |                         brace_count -= 1
392 |                         if brace_count == 0:
393 |                             json_str = response[start:i+1]
394 |                             logger.info("Extracted JSON object from response")
395 |                             break
396 |         except Exception as e:
397 |             logger.debug(f"Direct JSON extraction failed: {e}")
398 |     
399 |     # Strategy 3: Last resort - assume entire response is JSON
400 |     if not json_str:
401 |         json_str = response.strip()
402 |         logger.info("Using entire response as JSON")
403 |     
404 |     # Try to parse the JSON
405 |     parsed = None
406 |     parse_error = None
407 |     
408 |     try:
409 |         parsed = json.loads(json_str)
410 |         logger.info("Successfully parsed JSON")
411 |     except json.JSONDecodeError as e:
412 |         parse_error = e
413 |         logger.warning(f"Initial JSON parse failed: {str(e)}")
414 |         
415 |         # Try to clean common issues and retry
416 |         try:
417 |             # Remove any leading/trailing whitespace and newlines
418 |             cleaned = json_str.strip()
419 |             
420 |             # Try to fix common escape sequence issues
421 |             cleaned = cleaned.replace('\\n', '\\\\n')  # Fix unescaped newlines
422 |             cleaned = cleaned.replace('\n', '\\n')     # Escape actual newlines
423 |             cleaned = cleaned.replace('\r', '')         # Remove carriage returns
424 |             cleaned = cleaned.replace('\t', '\\t')     # Escape tabs
425 |             
426 |             # Try parsing again
427 |             parsed = json.loads(cleaned)
428 |             logger.info("Successfully parsed JSON after cleaning")
429 |         except json.JSONDecodeError as e2:
430 |             logger.warning(f"JSON parse failed after cleaning: {str(e2)}")
431 |             parse_error = e2
432 |     
433 |     # Validate and return parsed JSON
434 |     if parsed:
435 |         try:
436 |             # Validate required fields exist
437 |             if "roast_critiques" not in parsed:
438 |                 logger.error("Missing 'roast_critiques' in parsed JSON")
439 |                 raise ValueError("Missing roast_critiques field")
440 |             
441 |             if "refactored_code" not in parsed:
442 |                 logger.error("Missing 'refactored_code' in parsed JSON")
443 |                 raise ValueError("Missing refactored_code field")
444 |             
445 |             # Validate roast_critiques is a list
446 |             if not isinstance(parsed["roast_critiques"], list):
447 |                 logger.error("roast_critiques is not a list")
448 |                 raise ValueError("roast_critiques must be a list")
449 |             
450 |             # Validate each critique has required fields
451 |             for i, critique in enumerate(parsed["roast_critiques"]):
452 |                 if not isinstance(critique, dict):
453 |                     logger.warning(f"Critique {i} is not a dict, skipping")
454 |                     continue
455 |                 if "critique" not in critique:
456 |                     logger.warning(f"Critique {i} missing 'critique' field")
457 |                     critique["critique"] = "No critique provided"
458 |                 if "line" not in critique:
459 |                     critique["line"] = None
460 |             
461 |             # CRITICAL VALIDATION: Check if refactored_code is identical to original
462 |             original_normalized = original_code.strip().replace('\r\n', '\n').replace('\r', '\n')
463 |             refactored_normalized = parsed["refactored_code"].strip().replace('\r\n', '\n').replace('\r', '\n')
464 |             
465 |             if original_normalized == refactored_normalized:
466 |                 logger.warning("AI returned identical code - refactoring failed")
467 |                 return {
468 |                     "roast_critiques": [
469 |                         {
470 |                             "line": None,
471 |                             "critique": "The AI failed to generate a meaningful refactoring. Please try again."
472 |                         }
473 |                     ],
474 |                     "original_code": original_code,
475 |                     "refactored_code": original_code
476 |                 }
477 |             
478 |             # Return validated response with genuine improvements
479 |             return {
480 |                 "roast_critiques": parsed["roast_critiques"],
481 |                 "original_code": original_code,
482 |                 "refactored_code": parsed["refactored_code"]
483 |             }
484 |             
485 |         except (ValueError, KeyError, TypeError) as e:
486 |             logger.error(f"Validation error: {str(e)}")
487 |             # Fall through to fallback
488 |     
489 |     # Fallback: Create safe response when parsing fails
490 |     logger.warning("Using fallback response due to parsing failure")
491 |     logger.debug(f"Response preview: {response[:500]}...")
492 |     
493 |     return {
494 |         "roast_critiques": [
495 |             {
496 |                 "line": None,
497 |                 "critique": "The AI model returned a response, but it couldn't be parsed into the expected format. The model may need additional prompt tuning."
498 |             }
499 |         ],
500 |         "original_code": original_code,
501 |         "refactored_code": original_code  # Return original code as fallback
502 |     }
503 | 
504 | 
505 | # API Endpoints
506 | @app.get("/", tags=["Health"])
507 | async def health_check():
508 |     """
509 |     Health check endpoint.
510 |     Returns service status and configuration.
511 |     """
512 |     return {
513 |         "status": "healthy",
514 |         "service": "Code Roasting API",
515 |         "version": "3.0.0",
516 |         "watsonx_available": WATSONX_AVAILABLE,
517 |         "model": "ibm/granite-8b-code-instruct",
518 |         "environment": "production" if os.getenv("ENVIRONMENT") == "production" else "development"
519 |     }
520 | 
521 | 
522 | @app.get("/health", tags=["Health"])
523 | async def detailed_health_check():
524 |     """
525 |     Detailed health check endpoint for monitoring.
526 |     Returns comprehensive service status.
527 |     """
528 |     health_status = {
529 |         "status": "healthy" if WATSONX_AVAILABLE else "degraded",
530 |         "service": "Code Roasting API",
531 |         "version": "3.0.0",
532 |         "checks": {
533 |             "watsonx_credentials": "ok" if WATSONX_AVAILABLE else "failed",
534 |             "api_key_present": bool(WATSONX_API_KEY),
535 |             "project_id_present": bool(WATSONX_PROJECT_ID),
536 |         }
537 |     }
538 |     
539 |     status_code = 200 if WATSONX_AVAILABLE else 503
540 |     return JSONResponse(content=health_status, status_code=status_code)
541 | 
542 | 
543 | @app.post("/analyze", response_model=CodeAnalysisResponse, tags=["Analysis"])
544 | async def analyze_code(request: CodeAnalysisRequest):
545 |     """
546 |     Roast code and provide a refactored version using IBM WatsonX AI.
547 |     
548 |     **Security Features:**
549 |     - Input validation and sanitization
550 |     - Code length limits (max 50,000 characters)
551 |     - Secure credential handling
552 |     - Comprehensive error handling
553 |     
554 |     **Error Responses:**
555 |     - 400: Invalid input (empty code, invalid characters)
556 |     - 500: WatsonX API failure or internal error
557 |     - 503: WatsonX service unavailable
558 |     
559 |     Args:
560 |         request: CodeAnalysisRequest containing code to analyze
561 |     
562 |     Returns:
563 |         CodeAnalysisResponse with roast critiques, original code, and refactored version
564 |     
565 |     Raises:
566 |         HTTPException: If validation fails or WatsonX service is unavailable
567 |     """
568 |     # Check service availability
569 |     if not WATSONX_AVAILABLE:
570 |         logger.error("Analysis request rejected: WatsonX service unavailable")
571 |         raise HTTPException(
572 |             status_code=503,
573 |             detail="WatsonX AI service is currently unavailable. Please check service configuration."
574 |         )
575 |     
576 |     try:
577 |         logger.info(f"Received analysis request - Code length: {len(request.code)} chars, Language: {request.language or 'auto-detect'}")
578 |         
579 |         # Additional security validation
580 |         if len(request.code.strip()) == 0:
581 |             raise HTTPException(
582 |                 status_code=400,
583 |                 detail="Code cannot be empty or contain only whitespace"
584 |             )
585 |         
586 |         # Get response from WatsonX with error handling
587 |         try:
588 |             result = get_watsonx_response(
589 |                 user_code=request.code,
590 |                 language=request.language
591 |             )
592 |         except HTTPException:
593 |             # Re-raise HTTP exceptions from get_watsonx_response
594 |             raise
595 |         except Exception as e:
596 |             logger.error(f"Failed to get WatsonX response: {str(e)}")
597 |             raise HTTPException(
598 |                 status_code=500,
599 |                 detail="Failed to analyze code. Please try again."
600 |             )
601 |         
602 |         # Validate result structure
603 |         if not result or "roast_critiques" not in result or "refactored_code" not in result:
604 |             logger.error("Invalid result structure from WatsonX")
605 |             raise HTTPException(
606 |                 status_code=500,
607 |                 detail="Received invalid response from AI service"
608 |             )
609 |         
610 |         # Build response with error handling
611 |         try:
612 |             response = CodeAnalysisResponse(
613 |                 roast_critiques=[RoastCritique(**critique) for critique in result["roast_critiques"]],
614 |                 original_code=result["original_code"],
615 |                 refactored_code=result["refactored_code"]
616 |             )
617 |         except Exception as e:
618 |             logger.error(f"Failed to build response model: {str(e)}")
619 |             raise HTTPException(
620 |                 status_code=500,
621 |                 detail="Failed to format analysis results"
622 |             )
623 |         
624 |         logger.info("Code analysis completed successfully")
625 |         return response
626 |         
627 |     except HTTPException:
628 |         # Re-raise HTTP exceptions
629 |         raise
630 |     except Exception as e:
631 |         # Catch any unexpected errors
632 |         logger.error(f"Unexpected error during code analysis: {str(e)}")
633 |         logger.error(traceback.format_exc())
634 |         raise HTTPException(
635 |             status_code=500,
636 |             detail="An unexpected error occurred while analyzing your code"
637 |         )
638 | 
639 | 
640 | if __name__ == "__main__":
641 |     import uvicorn
642 |     
643 |     # Production-ready server configuration
644 |     port = int(os.getenv("PORT", 8000))
645 |     host = os.getenv("HOST", "0.0.0.0")
646 |     
647 |     logger.info(f"Starting Code Roasting API on {host}:{port}")
648 |     logger.info(f"WatsonX Available: {WATSONX_AVAILABLE}")
649 |     logger.info("Documentation available at /docs")
650 |     
651 |     uvicorn.run(
652 |         app,
653 |         host=host,
654 |         port=port,
655 |         log_level="info",
656 |         access_log=True
657 |     )
</content>
</file>
<file><path>index.html</path>
<content lines="1-440">
  1 | <!DOCTYPE html>
  2 | <html lang="en">
  3 | <head>
  4 |     <meta charset="UTF-8">
  5 |     <meta name="viewport" content="width=device-width, initial-scale=1.0">
  6 |     <title>DevSpark - Get Roasted. Get Better.</title>
  7 |     
  8 |     <!-- Tailwind CSS CDN -->
  9 |     <script src="https://cdn.tailwindcss.com"></script>
 10 |     
 11 |     <!-- Google Fonts - Inter -->
 12 |     <link rel="preconnect" href="https://fonts.googleapis.com">
 13 |     <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
 14 |     <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
 15 |     
 16 |     <style>
 17 |         /* IBM Carbon Design System Custom Styles */
 18 |         * {
 19 |             margin: 0;
 20 |             padding: 0;
 21 |             box-sizing: border-box;
 22 |         }
 23 |         
 24 |         body {
 25 |             font-family: 'Inter', sans-serif;
 26 |             background-color: #FFFFFF;
 27 |             color: #161616;
 28 |         }
 29 |         
 30 |         /* IBM Carbon Color Palette */
 31 |         :root {
 32 |             --white: #FFFFFF;
 33 |             --gray-10: #F8F9FA;
 34 |             --black: #161616;
 35 |             --blue: #0F62FE;
 36 |             --red: #DA1E28;
 37 |         }
 38 |         
 39 |         /* Remove Tailwind's default border-radius */
 40 |         * {
 41 |             border-radius: 0 !important;
 42 |         }
 43 |         
 44 |         /* Code blocks */
 45 |         .code-block {
 46 |             font-family: 'JetBrains Mono', monospace;
 47 |             font-size: 0.875rem;
 48 |             line-height: 1.5;
 49 |             white-space: pre-wrap;
 50 |             word-wrap: break-word;
 51 |         }
 52 |         
 53 |         /* IBM Carbon 1px borders */
 54 |         .carbon-border {
 55 |             border: 1px solid #161616;
 56 |         }
 57 |         
 58 |         .carbon-border-top {
 59 |             border-top: 1px solid #161616;
 60 |         }
 61 |         
 62 |         .carbon-border-bottom {
 63 |             border-bottom: 1px solid #161616;
 64 |         }
 65 |         
 66 |         /* Button styles */
 67 |         .carbon-button {
 68 |             background-color: #0F62FE;
 69 |             color: #FFFFFF;
 70 |             border: 1px solid #0F62FE;
 71 |             padding: 0.875rem 2rem;
 72 |             font-weight: 500;
 73 |             cursor: pointer;
 74 |             transition: background-color 0.2s ease;
 75 |         }
 76 |         
 77 |         .carbon-button:hover {
 78 |             background-color: #0353E9;
 79 |         }
 80 |         
 81 |         .carbon-button:disabled {
 82 |             background-color: #C6C6C6;
 83 |             border-color: #C6C6C6;
 84 |             cursor: not-allowed;
 85 |         }
 86 |         
 87 |         /* Alert box */
 88 |         .alert-box {
 89 |             background-color: #FFF1F1;
 90 |             border: 1px solid #DA1E28;
 91 |             padding: 1.5rem;
 92 |         }
 93 |         
 94 |         /* Loading spinner */
 95 |         .spinner {
 96 |             border: 3px solid #F8F9FA;
 97 |             border-top: 3px solid #0F62FE;
 98 |             width: 40px;
 99 |             height: 40px;
100 |             animation: spin 1s linear infinite;
101 |         }
102 |         
103 |         @keyframes spin {
104 |             0% { transform: rotate(0deg); }
105 |             100% { transform: rotate(360deg); }
106 |         }
107 |         
108 |         /* Blur overlay for Active Reflection Lock */
109 |         .blur-overlay {
110 |             backdrop-filter: blur(8px);
111 |             -webkit-backdrop-filter: blur(8px);
112 |             background-color: rgba(255, 255, 255, 0.3);
113 |         }
114 |         
115 |         /* Smooth transitions */
116 |         .fade-in {
117 |             animation: fadeIn 0.5s ease-in;
118 |         }
119 |         
120 |         @keyframes fadeIn {
121 |             from { opacity: 0; transform: translateY(10px); }
122 |             to { opacity: 1; transform: translateY(0); }
123 |         }
124 |         
125 |         /* Textarea styling */
126 |         textarea {
127 |             font-family: 'JetBrains Mono', monospace;
128 |             resize: vertical;
129 |         }
130 |         
131 |         /* Critique item styling */
132 |         .critique-item {
133 |             border-left: 3px solid #DA1E28;
134 |             padding-left: 1rem;
135 |             margin-bottom: 1rem;
136 |         }
137 |         
138 |         .critique-line {
139 |             font-weight: 600;
140 |             color: #DA1E28;
141 |             font-size: 0.875rem;
142 |         }
143 |         
144 |         .critique-text {
145 |             color: #161616;
146 |             margin-top: 0.25rem;
147 |         }
148 |     </style>
149 | </head>
150 | <body>
151 |     <!-- Navbar -->
152 |     <nav class="carbon-border-bottom bg-white">
153 |         <div class="max-w-7xl mx-auto px-6 py-4">
154 |             <div class="flex items-center justify-between">
155 |                 <div class="flex items-center space-x-2">
156 |                     <h1 class="text-2xl font-bold text-black">DevSpark</h1>
157 |                     <span class="text-gray-400">//</span>
158 |                     <span class="text-sm text-gray-600">Powered by IBM Bob</span>
159 |                 </div>
160 |             </div>
161 |         </div>
162 |     </nav>
163 | 
164 |     <!-- Hero Section -->
165 |     <section class="bg-white carbon-border-bottom">
166 |         <div class="max-w-7xl mx-auto px-6 py-16 text-center">
167 |             <h2 class="text-5xl font-bold text-black mb-4">Get Roasted. Get Better.</h2>
168 |             <p class="text-xl text-gray-600 max-w-2xl mx-auto">
169 |                 Submit your code and let our AI-powered senior developer tear it apart—then watch it transform into production-ready excellence.
170 |             </p>
171 |         </div>
172 |     </section>
173 | 
174 |     <!-- Input Section -->
175 |     <section id="inputSection" class="bg-gray-10 py-12">
176 |         <div class="max-w-7xl mx-auto px-6">
177 |             <div class="bg-white carbon-border p-8">
178 |                 <label for="codeInput" class="block text-sm font-semibold text-black mb-3">
179 |                     Paste Your Code Here
180 |                 </label>
181 |                 <textarea 
182 |                     id="codeInput" 
183 |                     class="w-full carbon-border p-4 text-sm focus:outline-none focus:border-blue-600"
184 |                     rows="15"
185 |                     placeholder="// Paste your code here and prepare to be humbled...
186 | function getData() {
187 |     var data = null;
188 |     $.ajax({
189 |         url: '/api/data',
190 |         async: false,
191 |         success: function(result) {
192 |             data = result;
193 |         }
194 |     });
195 |     return data;
196 | }"
197 |                 ></textarea>
198 |                 
199 |                 <div class="mt-6 flex items-center justify-center">
200 |                     <button 
201 |                         id="roastButton" 
202 |                         class="carbon-button"
203 |                         onclick="handleRoastClick()"
204 |                     >
205 |                         Roast & Refactor
206 |                     </button>
207 |                 </div>
208 |                 
209 |                 <!-- Loading State -->
210 |                 <div id="loadingState" class="hidden mt-8 flex flex-col items-center justify-center">
211 |                     <div class="spinner"></div>
212 |                     <p class="mt-4 text-sm text-gray-600">Analyzing your code with brutal honesty...</p>
213 |                 </div>
214 |             </div>
215 |         </div>
216 |     </section>
217 | 
218 |     <!-- Results Dashboard (Initially Hidden) -->
219 |     <section id="resultsSection" class="hidden bg-white py-12">
220 |         <div class="max-w-7xl mx-auto px-6">
221 |             
222 |             <!-- Senior Dev Code Review (Roast) -->
223 |             <div class="alert-box mb-8 fade-in">
224 |                 <div class="flex items-start">
225 |                     <svg class="w-6 h-6 text-red-600 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
226 |                         <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
227 |                     </svg>
228 |                     <div class="flex-1">
229 |                         <h3 class="text-lg font-bold text-red-600 mb-3">Senior Dev Code Review</h3>
230 |                         <div id="roastContent" class="space-y-3">
231 |                             <!-- Critiques will be dynamically inserted here -->
232 |                         </div>
233 |                     </div>
234 |                 </div>
235 |             </div>
236 | 
237 |             <!-- Unlock Button -->
238 |             <div class="mb-8 text-center">
239 |                 <button 
240 |                     id="unlockButton" 
241 |                     class="carbon-button bg-black border-black hover:bg-gray-800"
242 |                     onclick="unlockRefactoredCode()"
243 |                 >
244 |                     I Understand My Mistakes → Unlock Code
245 |                 </button>
246 |             </div>
247 | 
248 |             <!-- Code Comparison Grid -->
249 |             <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
250 |                 
251 |                 <!-- Original Code -->
252 |                 <div class="carbon-border bg-gray-10">
253 |                     <div class="carbon-border-bottom bg-white px-4 py-3">
254 |                         <h4 class="font-semibold text-black">Original Code</h4>
255 |                     </div>
256 |                     <div class="p-4 overflow-x-auto">
257 |                         <pre id="originalCode" class="code-block text-black"></pre>
258 |                     </div>
259 |                 </div>
260 | 
261 |                 <!-- Enterprise Refactor (with blur overlay) -->
262 |                 <div class="carbon-border bg-gray-10 relative">
263 |                     <div class="carbon-border-bottom bg-white px-4 py-3">
264 |                         <h4 class="font-semibold text-black">Enterprise Refactor</h4>
265 |                     </div>
266 |                     <div class="p-4 overflow-x-auto relative">
267 |                         <pre id="refactoredCode" class="code-block text-black"></pre>
268 |                         
269 |                         <!-- Blur Overlay (Active Reflection Lock) -->
270 |                         <div id="blurOverlay" class="absolute inset-0 blur-overlay flex items-center justify-center">
271 |                             <div class="bg-white carbon-border px-6 py-4 text-center">
272 |                                 <svg class="w-12 h-12 mx-auto mb-3 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
273 |                                     <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
274 |                                 </svg>
275 |                                 <p class="font-semibold text-black">Locked</p>
276 |                                 <p class="text-sm text-gray-600 mt-1">Acknowledge your mistakes to unlock</p>
277 |                             </div>
278 |                         </div>
279 |                     </div>
280 |                 </div>
281 | 
282 |             </div>
283 |         </div>
284 |     </section>
285 | 
286 |     <!-- Footer -->
287 |     <footer class="carbon-border-top bg-white py-8 mt-12">
288 |         <div class="max-w-7xl mx-auto px-6 text-center">
289 |             <p class="text-sm text-gray-600">
290 |                 DevSpark © 2026 | Built for developers who want to level up | Powered by IBM Bob
291 |             </p>
292 |         </div>
293 |     </footer>
294 | 
295 |     <script>
296 |         // Mock JSON response matching backend contract
297 |         const mockResponse = {
298 |             "roast_critiques": [
299 |                 {
300 |                     "lines": "Lines 1-8",
301 |                     "critique": "Oh boy, synchronous AJAX in 2026? That's like bringing a flip phone to a smartphone convention. This blocks the entire browser thread and makes your app feel like it's running on a potato. Also, jQuery? Really? We have fetch() and async/await now."
302 |                 },
303 |                 {
304 |                     "lines": "Line 2",
305 |                     "critique": "Using 'var'? What is this, 2010? We have 'const' and 'let' now. 'var' has function scope and hoisting issues that will bite you harder than a caffeinated chihuahua."
306 |                 },
307 |                 {
308 |                     "lines": "Line 4",
309 |                     "critique": "Setting async to false is a cardinal sin. You're literally telling the browser 'hey, freeze everything while I wait for this network request.' Users will think your app crashed. This is why we can't have nice things."
310 |                 },
311 |                 {
312 |                     "lines": "Lines 5-7",
313 |                     "critique": "No error handling? What happens when the API is down? When the network fails? When Mercury is in retrograde? Your app just silently fails and returns null. That's not robust, that's negligent."
314 |                 }
315 |             ],
316 |             "original_code": `function getData() {
317 |     var data = null;
318 |     $.ajax({
319 |         url: '/api/data',
320 |         async: false,
321 |         success: function(result) {
322 |             data = result;
323 |         }
324 |     });
325 |     return data;
326 | }`,
327 |             "refactored_code": `/**
328 |  * Fetches data from the API using modern async/await pattern
329 |  * @returns {Promise<Object>} The API response data
330 |  * @throws {Error} If the API request fails
331 |  */
332 | async function getData() {
333 |     try {
334 |         const response = await fetch('/api/data', {
335 |             method: 'GET',
336 |             headers: {
337 |                 'Content-Type': 'application/json'
338 |             }
339 |         });
340 |         
341 |         if (!response.ok) {
342 |             throw new Error(\`HTTP error! status: \${response.status}\`);
343 |         }
344 |         
345 |         const data = await response.json();
346 |         return data;
347 |         
348 |     } catch (error) {
349 |         console.error('Failed to fetch data:', error);
350 |         throw error; // Re-throw for caller to handle
351 |     }
352 | }
353 | 
354 | // Usage example:
355 | async function handleDataFetch() {
356 |     try {
357 |         const data = await getData();
358 |         console.log('Data received:', data);
359 |     } catch (error) {
360 |         // Handle error appropriately (show user message, retry, etc.)
361 |         console.error('Error handling data:', error);
362 |     }
363 | }`
364 |         };
365 | 
366 |         // Handle Roast & Refactor button click
367 |         function handleRoastClick() {
368 |             const codeInput = document.getElementById('codeInput');
369 |             const code = codeInput.value.trim();
370 |             
371 |             // Validate input
372 |             if (!code) {
373 |                 alert('Please paste some code first!');
374 |                 return;
375 |             }
376 |             
377 |             // Show loading state
378 |             document.getElementById('roastButton').disabled = true;
379 |             document.getElementById('loadingState').classList.remove('hidden');
380 |             
381 |             // Simulate API call with 2.5 second delay
382 |             setTimeout(() => {
383 |                 displayResults(mockResponse);
384 |             }, 2500);
385 |         }
386 | 
387 |         // Display results from API response
388 |         function displayResults(response) {
389 |             // Hide loading state
390 |             document.getElementById('loadingState').classList.add('hidden');
391 |             
392 |             // Populate roast critiques
393 |             const roastContent = document.getElementById('roastContent');
394 |             roastContent.innerHTML = '';
395 |             
396 |             response.roast_critiques.forEach(critique => {
397 |                 const critiqueDiv = document.createElement('div');
398 |                 critiqueDiv.className = 'critique-item';
399 |                 critiqueDiv.innerHTML = `
400 |                     <div class="critique-line">${critique.lines}</div>
401 |                     <div class="critique-text">${critique.critique}</div>
402 |                 `;
403 |                 roastContent.appendChild(critiqueDiv);
404 |             });
405 |             
406 |             // Populate code blocks
407 |             document.getElementById('originalCode').textContent = response.original_code;
408 |             document.getElementById('refactoredCode').textContent = response.refactored_code;
409 |             
410 |             // Show results section with animation
411 |             const resultsSection = document.getElementById('resultsSection');
412 |             resultsSection.classList.remove('hidden');
413 |             resultsSection.classList.add('fade-in');
414 |             
415 |             // Scroll to results
416 |             resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
417 |         }
418 | 
419 |         // Unlock refactored code (remove blur overlay)
420 |         function unlockRefactoredCode() {
421 |             const blurOverlay = document.getElementById('blurOverlay');
422 |             const unlockButton = document.getElementById('unlockButton');
423 |             
424 |             // Remove blur overlay with fade out
425 |             blurOverlay.style.transition = 'opacity 0.3s ease';
426 |             blurOverlay.style.opacity = '0';
427 |             
428 |             setTimeout(() => {
429 |                 blurOverlay.style.display = 'none';
430 |             }, 300);
431 |             
432 |             // Update button state
433 |             unlockButton.textContent = '✓ Code Unlocked';
434 |             unlockButton.disabled = true;
435 |             unlockButton.classList.add('bg-gray-400', 'border-gray-400');
436 |             unlockButton.classList.remove('bg-black', 'border-black', 'hover:bg-gray-800');
437 |         }
438 |     </script>
439 | </body>
440 | </html>
</content>
</file>
</files>
<environment_details>
# VSCode Visible Files
main.py

# VSCode Open Tabs
index.html,main.py,.env

# Current Time
Current time in ISO 8601 UTC format: 2026-05-17T12:16:01.139Z
User time zone: Asia/Singapore, UTC+8:00

# Current Cost
$0.01

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

I'll now wire the frontend to the backend by updating the JavaScript in index.html. I need to:

1. Remove the mockResponse variable
2. Remove the setTimeout simulation
3. Rewrite handleRoastClick() to make a real fetch() POST request
4. Update displayResults() to correctly map the backend's `line` integer field instead of the old `lines` string field

<apply_diff>
<path>index.html</path>
<diff>
<<<<<<< SEARCH
:start_line:295
-------
    <script>
        // Mock JSON response matching backend contract
        const mockResponse = {
            "roast_critiques": [
                {
                    "lines": "Lines 1-8",
                    "critique": "Oh boy, synchronous AJAX in 2026? That's like bringing a flip phone to a smartphone convention. This blocks the entire browser thread and makes your app feel like it's running on a potato. Also, jQuery? Really? We have fetch() and async/await now."
                },
                {
                    "lines": "Line 2",
                    "critique": "Using 'var'? What is this, 2010? We have 'const' and 'let' now. 'var' has function scope and hoisting issues that will bite you harder than a caffeinated chihuahua."
                },
                {
                    "lines": "Line 4",
                    "critique": "Setting async to false is a cardinal sin. You're literally telling the browser 'hey, freeze everything while I wait for this network request.' Users will think your app crashed. This is why we can't have nice things."
                },
                {
                    "lines": "Lines 5-7",
                    "critique": "No error handling? What happens when the API is down? When the network fails? When Mercury is in retrograde? Your app just silently fails and returns null. That's not robust, that's negligent."
                }
            ],
            "original_code": `function getData() {
    var data = null;
    $.ajax({
        url: '/api/data',
        async: false,
        success: function(result) {
            data = result;
        }
    });
    return data;
}`,
            "refactored_code": `/**
 * Fetches data from the API using modern async/await pattern
 * @returns {Promise<Object>} The API response data
 * @throws {Error} If the API request fails
 */
async function getData() {
    try {
        const response = await fetch('/api/data', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(\`HTTP error! status: \${response.status}\`);
        }
        
        const data = await response.json();
        return data;
        
    } catch (error) {
        console.error('Failed to fetch data:', error);
        throw error; // Re-throw for caller to handle
    }
}

// Usage example:
async function handleDataFetch() {
    try {
        const data = await getData();
        console.log('Data received:', data);
    } catch (error) {
        // Handle error appropriately (show user message, retry, etc.)
        console.error('Error handling data:', error);
    }
}`
        };

        // Handle Roast & Refactor button click
        function handleRoastClick() {
            const codeInput = document.getElementById('codeInput');
            const code = codeInput.value.trim();
            
            // Validate input
            if (!code) {
                alert('Please paste some code first!');
                return;
            }
            
            // Show loading state
            document.getElementById('roastButton').disabled = true;
            document.getElementById('loadingState').classList.remove('hidden');
            
            // Simulate API call with 2.5 second delay
            setTimeout(() => {
                displayResults(mockResponse);
            }, 2500);
        }

        // Display results from API response
        function displayResults(response) {
            // Hide loading state
            document.getElementById('loadingState').classList.add('hidden');
            
            // Populate roast critiques
            const roastContent = document.getElementById('roastContent');
            roastContent.innerHTML = '';
            
            response.roast_critiques.forEach(critique => {
                const critiqueDiv = document.createElement('div');
                critiqueDiv.className = 'critique-item';
                critiqueDiv.innerHTML = `
                    <div class="critique-line">${critique.lines}</div>
                    <div class="critique-text">${critique.critique}</div>
                `;
                roastContent.appendChild(critiqueDiv);
            });
            
            // Populate code blocks
            document.getElementById('originalCode').textContent = response.original_code;
            document.getElementById('refactoredCode').textContent = response.refactored_code;
            
            // Show results section with animation
            const resultsSection = document.getElementById('resultsSection');
            resultsSection.classList.remove('hidden');
            resultsSection.classList.add('fade-in');
            
            // Scroll to results
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
=======
    <script>
        // Handle Roast & Refactor button click
        async function handleRoastClick() {
            const codeInput = document.getElementById('codeInput');
            const code = codeInput.value.trim();
            
            // Validate input
            if (!code) {
                alert('Please paste some code first!');
                return;
            }
            
            // Show loading state
            document.getElementById('roastButton').disabled = true;
            document.getElementById('loadingState').classList.remove('hidden');
            
            try {
                // Make real POST request to backend
                const response = await fetch('http://localhost:8000/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        code: code,
                        language: null  // Optional: could detect or let user specify
                    })
                });
                
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                displayResults(data);
                
            } catch (error) {
                // Hide loading state
                document.getElementById('loadingState').classList.add('hidden');
                document.getElementById('roastButton').disabled = false;
                
                // Show error to user
                alert(`Error: ${error.message}\n\nPlease make sure the backend server is running on http://localhost:8000`);
                console.error('Failed to analyze code:', error);
            }
        }

        // Display results from API response
        function displayResults(response) {
            // Hide loading state
            document.getElementById('loadingState').classList.add('hidden');
            
            // Populate roast critiques
            const roastContent = document.getElementById('roastContent');
            roastContent.innerHTML = '';
            
            response.roast_critiques.forEach(critique => {
                const critiqueDiv = document.createElement('div');
                critiqueDiv.className = 'critique-item';
                
                // Map backend's 'line' integer to UI display
                const lineDisplay = critique.line !== null && critique.line !== undefined 
                    ? `Line ${critique.line}` 
                    : 'General';
                
                critiqueDiv.innerHTML = `
                    <div class="critique-line">${lineDisplay}</div>
                    <div class="critique-text">${critique.critique}</div>
                `;
                roastContent.appendChild(critiqueDiv);
            });
            
            // Populate code blocks
            document.getElementById('originalCode').textContent = response.original_code;
            document.getElementById('refactoredCode').textContent = response.refactored_code;
            
            // Show results section with animation
            const resultsSection = document.getElementById('resultsSection');
            resultsSection.classList.remove('hidden');
            resultsSection.classList.add('fade-in');
            
            // Scroll to results
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
>>>>>>> REPLACE
</diff>
</apply_diff>

---

**User:**

[apply_diff for 'index.html'] Result:
<file_write_result>
<path>index.html</path>
<operation>modified</operation>
<notice>
<i>You do not need to re-read the file, as you have seen all changes</i>
<i>Proceed with the task using these changes as the new baseline.</i>
</notice>
</file_write_result>

<notice>Making multiple related changes in a single apply_diff is more efficient. If other changes are needed in this file, please include them as additional SEARCH/REPLACE blocks.</notice>
<environment_details>
# VSCode Visible Files
index.html

# VSCode Open Tabs
main.py,index.html,.env

# Recently Modified Files
These files have been modified since you last accessed them (file was just edited so you may need to re-read it before editing):
index.html

# Current Time
Current time in ISO 8601 UTC format: 2026-05-17T12:16:51.583Z
User time zone: Asia/Singapore, UTC+8:00

# Current Cost
$0.06

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

<attempt_completion>
<result>
Successfully wired the frontend to the backend! Here's what I changed in index.html:

**Removed:**
- The entire `mockResponse` variable (lines 297-364)
- The `setTimeout` simulation in `handleRoastClick()`

**Rewrote `handleRoastClick()`:**
- Now makes a real asynchronous `fetch()` POST request to `http://localhost:8000/analyze`
- Sends the code from the textarea in the request body as JSON
- Includes proper error handling with try/catch
- Shows user-friendly error messages if the backend is unavailable
- Re-enables the button on error so users can retry

**Updated `displayResults()`:**
- Correctly maps the backend's Pydantic `line` integer field to the UI
- Displays "Line X" for specific line numbers (when `line` is not null)
- Displays "General" for overall critiques (when `line` is null)
- Removed the old `critique.lines` string reference

**No changes to:**
- HTML layout
- CSS styling
- Any visual elements

The frontend is now fully integrated with your FastAPI backend and will make real API calls to analyze code!
</result>
</attempt_completion>

