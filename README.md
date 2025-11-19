📘 Gemini AI Toolkit – README
🚀 Overview

Gemini AI Toolkit is a full-stack AI-powered web application built using Flask + Gemini 2.5 Flash + TailwindCSS + JavaScript.
It provides an interactive interface for:

AI Chat (like ChatGPT)

Text & File Summarization

Code Explanation

Voice Input (Speech → Text)

This project showcases modern UI design, powerful AI integrations, and robust backend engineering—making it suitable for portfolios, learning, and real-world applications.

✨ Features
🧠 1. AI Chat

Interact with Gemini 2.5 Flash through a chat interface using:

Text input

Voice input

Persistent chat session

📄 2. Advanced Summarizer

Summarize text or uploaded files using 5 summary modes:

Brief (1–2 sentences)

Key Points

Detailed

Academic

Executive Summary

Supported File Formats:

PDF

TXT

JSON

XML

CSV

Files are automatically processed and summarized by the AI.

👨‍💻 3. Code Explainer

Paste any code and choose explanation style:

Simple (Beginner-level)

Technical (Algorithms, patterns)

Line-by-line

Optimization suggestions

Supports: Python, HTML, CSS, JavaScript, Java, and General Code

🎤 4. Voice Recognition

Built-in Web Speech API enabling:

Voice-to-text input for Chat & Summarizer

Live transcription

Visual listening indicators

🏗 Architecture
Backend (Flask)

Exposes 3 REST API routes:

/chat — AI conversation

/summarize — Text/file summarization

/explain — Code explanation

Uses GeminiAIToolkit class for AI logic

Handles PDF, text, CSV, JSON, XML parsing

Automatically opens browser when running locally

Frontend

TailwindCSS-based modern UI

Animated glassmorphism design

Dynamic switching between tool components

JavaScript handles:

API calls

Loading overlays

Voice input logic

DOM updates

🧰 Technology Stack
Layer	Tools
Frontend	HTML, TailwindCSS, JavaScript, Web Speech API
Backend	Python, Flask
AI	Gemini 2.5 Flash (google-generativeai)
File Handling	PyPDF2, CSV, JSON parsing
📁 Project Structure
app.py
templates/
    (optional) index.html
static/
    (optional) css/js files
README.md


Note: In your version, HTML is directly embedded inside app.py.

⚙ How It Works
🔹 1. AI Engine – GeminiAIToolkit

Handles:

Chat responses

Summaries

Code explanations

PDF text extraction

🔹 2. File Processing

PDF → Extract pages using PyPDF2

Text/JSON/XML → UTF-8 decode

CSV → Convert rows to JSON string for summarization

🔹 3. Speech Recognition

Implemented fully in JavaScript:

Uses browser’s SpeechRecognition API

Real-time transcript

“Listening” → “Completed” indicators

🌟 Strengths

✔ Full-stack AI system
✔ Beautiful modern UI with animations
✔ Multi-file summarization
✔ Voice-based input
✔ Multi-style code explanation
✔ Modular backend code structure
✔ Suitable for real deployment

⚠ Known Issues / Improvements Needed
Issue	Impact	Fix
Hard-coded Gemini API key	Security risk	Replace with environment variable
Large HTML block inside Python	Hard to maintain	Move to templates folder
Limited CSV parsing	Large CSV becomes huge	Use pandas or chunking
No rate limit handling	API may fail on high use	Add error retries
No auth	Others can misuse API	Add login/token protection
🛠 Future Enhancements

Add database for saving chat history

User authentication (JWT or OAuth)

Dark/Light mode toggle

Deployment via Docker / Render / Railway

Add image summarization support

Convert to a Chrome/desktop application

▶ Running the Project Locally
1. Install Dependencies
pip install -r requirements.txt

2. Set Gemini API Key
export GEMINI_API_KEY="your_api_key_here"

3. Start the App
python app.py


The browser will automatically open at:

http://127.0.0.1:5000

📌 Summary

This project is a professional AI toolkit combining:

Advanced AI features

Full-stack development

Real-time voice processing

File handling

Beautiful UI

Perfect for showcasing your skills in AI, web development, and UI/UX.
# 🚀 Live Project Link
You can access the live deployed version here:
👉 https://gemini-toolkit.onrender.com


