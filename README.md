# DevSpark ⚡ // Get Roasted. Get Better.

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)
![IBM watsonx.ai](https://img.shields.io/badge/IBM%20watsonx.ai-0F62FE?style=for-the-badge&logo=ibm&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

> **DevSpark is an automated, brutal Tech Lead designed to combat the "lazy copy-paste" habit common among modern developers.** > 
> Instead of blindly serving up instant code solutions, DevSpark tears bad code apart with absolute honesty, then safely locks the production-ready refactor behind an interactive code gate. 

**Built for the IBM Bob Hackathon 2026.**

---

## 💡 The Core Innovation: Active Reflection Lock

Most AI assistants make engineers lazy by providing immediate answers, leading to blind copy-pasting without learning. DevSpark fixes this behavioral loop:

1. 🛑 **The Roast**: Paste messy, outdated, or insecure code. The AI brutally reviews it for security flaws, syntax anti-patterns, and architectural issues.
2. 🔒 **The Lock**: The optimized, enterprise-grade refactored code block renders on screen with a strict `backdrop-blur` layer completely obscuring it.
3. 🧠 **The Reflection**: The user is forced to read through the bulleted critiques. Clicking the **"I Understand My Mistakes → Unlock Code"** button is the only way to clear the blur overlay and study the solution.

---

## 📺 Demo & Previews

*(Replace this section with a link to your YouTube demo video or add screenshots of the UI here before final submission)*
* `[Screenshot 1: The Code Roast UI]`
* `[Screenshot 2: The Active Reflection Lock in Action]`

---

## 🛠️ Tech Stack & Architecture

* **Frontend**: Single-file semantic HTML5, stylized cleanly using the **IBM Carbon Design System** guidelines (Stark White, Light Gray, True Black, IBM Blue, and Alert Red) with strict flat edges and 1px borders. Responsive utilities powered by Tailwind CSS.
* **Backend**: Python 3.x using **FastAPI** as a fast, asynchronous proxy to handle secure, server-side data transport.
* **AI Inference Engine**: **IBM watsonx.ai** parsing inputs using state-of-the-art Granite foundational models (`granite-3-8b-instruct`) to return strict JSON data payloads.
* **Development Partner**: Fully designed and developed natively utilizing the **IBM Bob Agentic IDE**.

---

## ⚖️ Hackathon Compliance & Integrity

This repository adheres strictly to the competition design protocols. All AI assistant generation session trails, usage reports, and token consumption summaries are fully preserved and auditable.

* 📁 **Session Logs**: Located in the `/bob_sessions` directory.
* 📝 Contains the exported automated session history markdown (`.md`) documents.
* 📊 Includes verifying screenshots of the token allocation analytics dashboard.

---

## 🚀 Local Setup & Installation

### Frontend
No build step required. Simply open the `index.html` file in any modern web browser to interact with the design system interface and review the built-in static demonstration contracts.

### Backend
1. Navigate to your project directory and install the required dependencies:
   ```bash
   pip install fastapi uvicorn pydantic requests python-dotenv ibm-watsonx-ai
