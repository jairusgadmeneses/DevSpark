# DevSpark ⚡ // Get Roasted. Get Better.

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)
![IBM watsonx.ai](https://img.shields.io/badge/IBM%20watsonx.ai-0F62FE?style=for-the-badge&logo=ibm&logoColor=white)
![IBM Granite Code](https://img.shields.io/badge/IBM%20Granite%20Code-005F9E?style=for-the-badge&logo=ibm&logoColor=white)

> **DevSpark is an automated, brutal AI Tech Lead designed to disrupt the "lazy copy-paste" habit common among modern developers.** > Instead of blindly serving up instant code solutions, DevSpark tears bad code apart with absolute honesty, then safely locks the production-ready refactor behind an interactive code gate. 

**Built for the IBM Bob Hackathon 2026.**

---

## 💡 The Core Innovation: Active Reflection Lock™

Most AI assistants make engineers lazy by providing immediate answers, leading to blind copy-pasting without learning. DevSpark fixes this behavioral loop:

1. 🛑 **The Roast**: Paste messy, outdated, or insecure code. The backend leverages high-capacity foundational code models to evaluate it for security flaws, syntax anti-patterns, and architectural issues.
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
* **AI Inference Engine**: **IBM watsonx.ai** invoking the specialized **ibm/granite-8b-code-instruct** model to process code contexts, handle structural logic, and enforce strict, type-safe JSON payloads.
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
