# DevSpark ⚡ // Get Roasted. Get Better.

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)
![IBM watsonx.ai](https://img.shields.io/badge/IBM%20watsonx.ai-0F62FE?style=for-the-badge&logo=ibm&logoColor=white)
![IBM Granite](https://img.shields.io/badge/IBM%20Granite%203-005F9E?style=for-the-badge&logo=ibm&logoColor=white)

> **DevSpark is an automated, brutal AI Tech Lead designed to disrupt the "lazy copy-paste" habit common among modern developers.** > Instead of blindly serving up instant code solutions, DevSpark tears bad code apart with absolute honesty, then safely locks the production-ready refactor behind an interactive code gate. 

**Built for the IBM Bob Hackathon 2026.**

---

## 💡 The Core Innovation: Active Reflection Lock™

Most AI assistants make engineers lazy by providing immediate answers, leading to blind copy-pasting without learning. DevSpark fixes this behavioral loop:

1. 🛑 **The Roast**: Paste messy, outdated, or insecure code. The backend leverages high-capacity foundational models to evaluate it for security flaws, syntax anti-patterns, and architectural issues.
2. 🔒 **The Lock**: The optimized, enterprise-grade refactored code block renders on screen with a strict `backdrop-blur` layer completely obscuring it.
3. 🧠 **The Reflection**: The user is forced to read through the bulleted critiques. Clicking the **"I Understand My Mistakes → Unlock Code"** button is the only way to clear the blur overlay and study the solution.

---

## 📺 Demo & Previews

*(Replace this section with a link to your YouTube demo video or add screenshots of the UI here before final submission)*
* `[Screenshot 1: The Code Roast UI Layout]`
* `[Screenshot 2: The Active Reflection Lock Blur Active]`

---

## 🛠️ Tech Stack & Architecture

* **Frontend**: Single-file semantic HTML5, stylized cleanly using the **IBM Carbon Design System** guidelines (Stark White, Light Gray, True Black, IBM Blue, and Alert Red) with strict flat edges and 1px borders. Responsive utilities powered by Tailwind CSS.
* **Backend**: Python 3.8+ using **FastAPI** as a high-performance, asynchronous proxy gateway to handle secure, server-side data transport.
* **AI Inference Engine**: **IBM watsonx.ai** invoking the official hackathon foundational **ibm/granite-3-8b-instruct** model to process code contexts and enforce strict, type-safe JSON payloads.
* **Development Partner**: Fully designed and developed natively utilizing the **IBM Bob Agentic IDE**.

---

## 📁 Project Structure

```text
devspark-workspace/
├── bob_sessions/        # Mandatory Hackathon Compliance Logs
├── index.html           # Carbon Design System Frontend UI
├── main.py              # FastAPI application & proxy routes
├── .env                 # Environment variables (WatsonX credentials)
├── .gitignore           # Git ignore rules (Crucial for key security)
├── README.md            # This file
└── requirements.txt     # Python dependencies
🚀 Local Setup & Installation
Frontend
No build step required. Simply open the index.html file in any modern web browser to interact with the design system interface.

Backend Gateway
Navigate to your project directory and initialize a virtual environment:

Bash
cd devspark-workspace
python -m venv venv
Activate the virtual environment:

Windows: ```bash
venv\Scripts\activate

macOS/Linux: ```bash
source venv/bin/activate


Install dependencies:
Create a requirements.txt file in the root directory and populate it with:

Plaintext
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-dotenv==1.0.0
ibm-watsonx-ai==0.2.6
pydantic==2.5.3
Then execute the installation command:

Bash
pip install -r requirements.txt
Configure Environment Variables:
Create a secure .env file in the root directory of your project:

Code snippet
WATSONX_API_KEY=your_official_hackathon_api_key_here
WATSONX_PROJECT_ID=your_official_sandbox_project_id_here
WATSONX_URL=[https://us-south.ml.cloud.ibm.com](https://us-south.ml.cloud.ibm.com)
Run the gateway application:
Start the local development proxy using Uvicorn:

Bash
uvicorn main:app --reload
The backend API will fire up and be listening securely at http://localhost:8000.

🔌 API Documentation & Data Contracts
Once the server is initialized and running locally, you can access the interactive documentation directly via:

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

1. Health Verification
Endpoint: GET /

Response Payload Structure:

JSON
{
  "status": "healthy",
  "service": "Code Roasting API",
  "version": "3.0.0",
  "watsonx_available": true,
  "model": "ibm/granite-3-8b-instruct",
  "environment": "development"
}
2. Roast and Refactor Code
Endpoint: POST /analyze

Content-Type: application/json

Request Payload Structure:

JSON
{
  "code": "def calculate(x, y):\n    return x + y",
  "language": "python"
}
Response Payload (Enforced Strict Type-Safe Pydantic Contract):

JSON
{
  "roast_critiques": [
    {
      "line": 1,
      "critique": "No type hints? What is this, 2010? Your function signature is as vague as a politician's promise."
    },
    {
      "line": 1,
      "critique": "Missing docstring! How is anyone supposed to know what this does? Mind reading?"
    },
    {
      "line": null,
      "critique": "Overall, this function is basic but functional. Time to level it up."
    }
  ],
  "original_code": "def calculate(x, y):\n    return x + y",
  "refactored_code": "def calculate(x: float, y: float) -> float:\n    \"\"\"\n    Add two numbers together.\n    \n    Args:\n        x: First number\n        y: Second number\n    \n    Returns:\n        Sum of x and y\n    \"\"\"\n    return x + y"
}
🛡️ Error Handling Boundaries
The API features comprehensive validation boundaries and responds with standardized HTTP status codes:

200: Successful processing, parsing, and data contract generation.

400 / 422: Input validation failure (empty payload, size limits exceeded, or character injection risks).

500: Internal parsing errors or downstream unexpected runtime exceptions.

503: Downstream WatsonX API service unavailable or invalid system credentials.

⚖️ Hackathon Compliance & Integrity
This repository adheres strictly to the competition design protocols. All AI assistant generation session trails, usage reports, and token consumption summaries are fully preserved and auditable.

📁 Session Logs: Located in the /bob_sessions directory.

📝 Contains the exported automated session history markdown (.md) documents.

📊 Includes verifying screenshots of the token allocation analytics dashboard.

🤝 The Team
Jairus Gad Q. Meneses - Frontend Architecture, UI/UX Design, & Tech Lead

Abhishek Ashok Kamthe - FastAPI Backend Architecture & WatsonX Pipeline
