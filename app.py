import os
import PyPDF2
from flask import Flask, request, jsonify, render_template_string
import google.generativeai as genai
import io
import webbrowser
import threading
import time
import json
import csv

# --- Gemini AI Toolkit Class (from your original code) ---
class GeminiAIToolkit:
    def __init__(self, api_key):
        genai.configure(api_key="AIzaSyAH8J7JMWl8lrj9nI_d5OZQ2JfxZ3kUU9E")
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.chat = self.model.start_chat(history=[])

    def chat_response(self, message):
        response = self.chat.send_message(message)
        return response.text

    def extract_text_from_pdf(self, pdf_file):
        """Extract text from a PDF file stream"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            return f"Error reading PDF: {str(e)}"

    def summarize_text(self, text, summary_type="detailed", max_length=8000):
        """Advanced text summarization with multiple options"""
        summary_prompts = {
            "brief": "Create a very brief 1-2 sentence summary highlighting only the main point:",
            "key_points": "Extract 5-7 key bullet points from this text. Focus on main ideas and important details:",
            "detailed": "Create a comprehensive summary (about 1 paragraph) covering all main points:",
            "academic": "Create an academic-style summary with thesis, main arguments, and conclusion:",
            "executive": "Create an executive summary suitable for business professionals (3-4 sentences):"
        }
        
        prompt = f"{summary_prompts.get(summary_type, summary_prompts['detailed'])}\n\n{text[:max_length]}"
        return self.generate_content(prompt)

    def explain_code(self, code, explanation_type="simple", language="general"):
        """Advanced code explanation with multiple levels and language context"""
        explanation_prompts = {
            "simple": f"Explain this {language} code in simple terms for beginners:\n\n",
            "technical": f"Provide a technical explanation of this {language} code including algorithms and patterns:\n\n",
            "line_by_line": f"Explain this {language} code line by line with detailed comments:\n\n",
            "optimization": f"Analyze this {language} code and suggest optimizations or improvements:\n\n"
        }
        
        prompt = f"{explanation_prompts.get(explanation_type, explanation_prompts['simple'])}{code}"
        return self.generate_content(prompt)

    def generate_content(self, prompt):
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"
    
    def analyze_document_structure(self, text):
        """Analyze document to provide better context for summarization"""
        analysis_prompt = f"""Analyze this document and identify:
        1. Document type (research paper, article, report, etc.)
        2. Main topic/subject
        3. Key sections/headings
        4. Primary arguments or findings
        
        Document excerpt: {text[:2000]}
        """
        
        return self.generate_content(analysis_prompt)

# --- Flask Web Application ---
app = Flask(__name__)

# Get API key from environment variable
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")

# Initialize the toolkit
toolkit = GeminiAIToolkit(API_KEY)

# --- HTML Content with microphone functionality ---
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemini AI Toolkit</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        body {
            font-family: 'Inter', sans-serif;
            background: #0d0d1a;
            color: #c0c0d0;
            overflow-x: hidden;
        }

        /* Animated background with deep, subtle gradients */
        .animated-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            background: radial-gradient(circle at top right, #1a1a2e 0%, #0d0d1a 70%);
            animation: background-pulse 20s infinite alternate ease-in-out;
        }

        @keyframes background-pulse {
            0% { transform: scale(1); opacity: 0.8; }
            100% { transform: scale(1.1); opacity: 1; }
        }

        .container {
            max-width: 960px;
            margin: 0 auto;
            padding: 2rem;
        }

        /* Enhanced Glassmorphism Effect */
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 1.5rem;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 2.5rem;
            transition: all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        }

        .glass-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 16px 64px 0 rgba(0, 0, 0, 0.6);
        }

        /* Nav button floating effect and glass transition */
        .nav-btn {
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.4s ease-in-out;
            animation: floating 3s ease-in-out infinite;
        }
        
        @keyframes floating {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }

        .nav-btn:hover {
            background: rgba(255, 255, 255, 0.1);
            box-shadow: 0 0 15px rgba(255, 255, 255, 0.2);
            transform: translateY(-5px) scale(1.05);
        }

        /* Active tool button glass effect */
        .nav-btn.active {
            background: rgba(255, 255, 255, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 0 20px rgba(255, 91, 91, 0.5);
            animation: none; /* Stop floating when active */
        }
        
        .btn {
            padding: 0.75rem 1.5rem;
            border-radius: 9999px;
            font-weight: 600;
            transition: background-color 0.2s, transform 0.1s;
        }

        /* Darker colors for input and select fields */
        .input-field, .select-field {
            width: 100%;
            background: #1e1e2d;
            border: 1px solid #3b3b5b;
            border-radius: 0.75rem;
            padding: 0.75rem;
            color: #c0c0d0;
            transition: all 0.3s ease;
        }

        .input-field:focus, .select-field:focus {
            outline: none;
            border-color: #ff5b5b;
            box-shadow: 0 0 0 3px rgba(255, 91, 91, 0.5);
        }

        .textarea-field {
            min-height: 200px;
            resize: vertical;
        }

        .spinner {
            border: 4px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top: 4px solid #ff5b5b;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* Microphone button styles */
        .mic-btn {
            background: #4a5568;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }

        .mic-btn:hover {
            background: #718096;
            transform: scale(1.1);
        }

        .mic-btn.recording {
            background: #e53e3e;
            animation: pulse 1.5s infinite;
        }

        .mic-btn.recording:hover {
            background: #c53030;
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }

        .voice-status {
            font-size: 0.875rem;
            color: #a0aec0;
            margin-left: 0.5rem;
        }

        .voice-status.recording {
            color: #e53e3e;
            font-weight: 600;
        }

        .voice-status.processing {
            color: #4299e1;
            font-weight: 600;
        }

        /* Input container with microphone */
        .input-container {
            position: relative;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
    </style>
</head>
<body class="bg-gray-900 text-gray-200">
<div class="animated-bg"></div>

<div class="container min-h-screen flex flex-col items-center justify-center p-4 relative z-10">

    <header class="text-center mb-12">
        <h1 class="text-4xl sm:text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-pink-600 mb-2">Gemini AI Toolkit</h1>
        <p class="text-lg text-gray-400">Your all-in-one AI command center with voice input.</p>
    </header>

    <nav class="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4 mb-8">
        <button id="chat-btn" class="nav-btn btn bg-blue-600 hover:bg-blue-700">💬 Chat with AI</button>
        <button id="summarizer-btn" class="nav-btn btn bg-purple-600 hover:bg-purple-700">📊 Summarizer</button>
        <button id="explainer-btn" class="nav-btn btn bg-green-600 hover:bg-green-700 active">👨‍💻 Code Explainer</button>
    </nav>

    <main class="w-full">
        <div id="chat-container" class="glass-card hidden">
            <h2 class="text-2xl font-semibold mb-4">💬 AI Chat</h2>
            <div id="chat-history" class="bg-gray-800 p-4 rounded-lg mb-4 h-96 overflow-y-auto flex flex-col-reverse">
                <div id="chat-placeholder" class="text-gray-500 italic text-center">Start a conversation with the AI...</div>
            </div>
            <div class="input-container">
                <input id="chat-input" type="text" placeholder="Type your message or use voice..." class="input-field flex-grow">
                <button id="chat-mic-btn" class="mic-btn" title="Voice input">🎤</button>
                <button id="chat-send-btn" class="btn bg-blue-600 hover:bg-blue-700">Send</button>
            </div>
            <div id="chat-voice-status" class="voice-status mt-2"></div>
        </div>

        <div id="summarizer-container" class="glass-card hidden">
            <h2 class="text-2xl font-semibold mb-4">📊 Advanced Summarizer</h2>
            <p class="text-sm text-gray-400 mb-4">Paste text, upload a file, or use voice input below.</p>

            <div class="input-container mb-4">
                <textarea id="summarizer-input" placeholder="Paste text here or use voice input..." class="textarea-field input-field flex-grow"></textarea>
                <button id="summarizer-mic-btn" class="mic-btn" title="Voice input">🎤</button>
            </div>
            <div id="summarizer-voice-status" class="voice-status mb-4"></div>
            
            <div class="flex flex-col sm:flex-row items-center space-y-4 sm:space-y-0 sm:space-x-4 mb-4">
                <select id="summary-type" class="select-field">
                    <option value="brief">Brief (1-2 sentences)</option>
                    <option value="key_points">Key Points (bullet list)</option>
                    <option value="detailed" selected>Detailed (1 paragraph)</option>
                    <option value="academic">Academic style</option>
                    <option value="executive">Executive summary</option>
                </select>
                <select id="file-type" class="select-field">
                    <option value="">Select File Type</option>
                    <option value="pdf">PDF</option>
                    <option value="txt">TXT</option>
                    <option value="json">JSON</option>
                    <option value="xml">XML</option>
                    <option value="csv">CSV</option>
                    <option value="unsupported">RAR, ZIP, etc.</option>
                </select>
                <input type="file" id="file-upload" class="file-input text-sm text-gray-400 flex-grow" />
                <button id="summarize-btn" class="btn bg-purple-600 hover:bg-purple-700 w-full sm:w-auto">Summarize</button>
            </div>

            <div id="summarizer-results" class="bg-gray-800 p-4 rounded-lg hidden">
                <h3 class="text-lg font-medium text-gray-300 mb-2">Summary:</h3>
                <pre class="whitespace-pre-wrap font-mono text-gray-200" id="summarizer-output"></pre>
            </div>
        </div>

        <div id="explainer-container" class="glass-card">
            <h2 class="text-2xl font-semibold mb-4">👨‍💻 Advanced Code Explainer</h2>
            <p class="text-sm text-gray-400 mb-4">Paste code and choose an explanation depth.</p>

            <textarea id="explainer-input" placeholder="Paste your code here..." class="textarea-field input-field mb-4"></textarea>

            <div class="flex flex-col sm:flex-row items-center space-y-4 sm:space-y-0 sm:space-x-4 mb-4">
                <select id="explanation-type" class="select-field">
                    <option value="simple">Simple (for beginners)</option>
                    <option value="technical">Technical (algorithms & patterns)</option>
                    <option value="line_by_line">Line-by-line</option>
                    <option value="optimization">Optimization suggestions</option>
                </select>
                <select id="code-language" class="select-field">
                    <option value="general">General Code</option>
                    <option value="python">Python</option>
                    <option value="html">HTML</option>
                    <option value="css">CSS</option>
                    <option value="javascript">JavaScript</option>
                    <option value="java">Java</option>
                </select>
                <button id="explain-btn" class="btn bg-green-600 hover:bg-green-700 w-full sm:w-auto">Explain Code</button>
            </div>

            <div id="explainer-results" class="bg-gray-800 p-4 rounded-lg hidden">
                <h3 class="text-lg font-medium text-gray-300 mb-2">Explanation:</h3>
                <pre class="whitespace-pre-wrap font-mono text-gray-200" id="explainer-output"></pre>
            </div>
        </div>
    </main>

    <div id="loading-overlay" class="fixed inset-0 bg-gray-900 bg-opacity-75 flex items-center justify-center hidden">
        <div class="flex flex-col items-center">
            <div class="spinner"></div>
            <p class="mt-4 text-xl">Thinking...</p>
        </div>
    </div>
</div>

<script>
    // --- UI Elements ---
    const chatBtn = document.getElementById('chat-btn');
    const summarizerBtn = document.getElementById('summarizer-btn');
    const explainerBtn = document.getElementById('explainer-btn');

    const chatContainer = document.getElementById('chat-container');
    const summarizerContainer = document.getElementById('summarizer-container');
    const explainerContainer = document.getElementById('explainer-container');

    const chatInput = document.getElementById('chat-input');
    const chatSendBtn = document.getElementById('chat-send-btn');
    const chatHistory = document.getElementById('chat-history');
    const chatPlaceholder = document.getElementById('chat-placeholder');
    const chatMicBtn = document.getElementById('chat-mic-btn');
    const chatVoiceStatus = document.getElementById('chat-voice-status');

    const summarizerInput = document.getElementById('summarizer-input');
    const summarizeBtn = document.getElementById('summarize-btn');
    const summaryType = document.getElementById('summary-type');
    const fileType = document.getElementById('file-type');
    const fileUpload = document.getElementById('file-upload');
    const summarizerResults = document.getElementById('summarizer-results');
    const summarizerOutput = document.getElementById('summarizer-output');
    const summarizerMicBtn = document.getElementById('summarizer-mic-btn');
    const summarizerVoiceStatus = document.getElementById('summarizer-voice-status');

    const explainerInput = document.getElementById('explainer-input');
    const explainBtn = document.getElementById('explain-btn');
    const explanationType = document.getElementById('explanation-type');
    const codeLanguage = document.getElementById('code-language');
    const explainerResults = document.getElementById('explainer-results');
    const explainerOutput = document.getElementById('explainer-output');

    const loadingOverlay = document.getElementById('loading-overlay');

    const containers = [chatContainer, summarizerContainer, explainerContainer];
    const navButtons = [chatBtn, summarizerBtn, explainerBtn];

    // --- State & Utility Functions ---
    let isLoading = false;
    let recognition = null;
    let isRecording = false;

    // Initialize Speech Recognition
    const initSpeechRecognition = () => {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            return true;
        }
        return false;
    };

    // Start voice recording
    const startVoiceRecording = (inputElement, micButton, statusElement) => {
        if (!recognition) {
            if (!initSpeechRecognition()) {
                statusElement.textContent = 'Speech recognition not supported in this browser';
                statusElement.className = 'voice-status';
                return;
            }
        }

        if (isRecording) {
            stopVoiceRecording();
            return;
        }

        isRecording = true;
        micButton.classList.add('recording');
        statusElement.textContent = 'Listening... Click mic again to stop';
        statusElement.className = 'voice-status recording';

        recognition.onresult = (event) => {
            let finalTranscript = '';
            let interimTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            if (finalTranscript) {
                inputElement.value += finalTranscript;
                statusElement.textContent = 'Voice input completed';
                statusElement.className = 'voice-status';
            } else if (interimTranscript) {
                statusElement.textContent = `Listening: "${interimTranscript}"`;
                statusElement.className = 'voice-status recording';
            }
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            statusElement.textContent = `Error: ${event.error}`;
            statusElement.className = 'voice-status';
            stopVoiceRecording();
        };

        recognition.onend = () => {
            stopVoiceRecording();
        };

        recognition.start();
    };

    // Stop voice recording
    const stopVoiceRecording = () => {
        if (recognition && isRecording) {
            recognition.stop();
        }
        isRecording = false;
        
        // Remove recording class from all mic buttons
        document.querySelectorAll('.mic-btn').forEach(btn => {
            btn.classList.remove('recording');
        });
        
        // Clear all status messages
        document.querySelectorAll('.voice-status').forEach(status => {
            if (status.textContent.includes('Listening')) {
                status.textContent = '';
                status.className = 'voice-status';
            }
        });
    };

    const showLoading = () => {
        isLoading = true;
        loadingOverlay.classList.remove('hidden');
    };

    const hideLoading = () => {
        isLoading = false;
        loadingOverlay.classList.add('hidden');
    };

    const setActiveView = (containerId) => {
        containers.forEach(container => container.classList.add('hidden'));
        document.getElementById(containerId).classList.remove('hidden');

        navButtons.forEach(btn => btn.classList.remove('active'));
        document.getElementById(containerId.replace('-container', '-btn')).classList.add('active');
    };

    // --- API Request Functions ---
    const handleChat = async () => {
        if (isLoading) return;
        const message = chatInput.value.trim();
        if (!message) return;

        chatPlaceholder.classList.add('hidden');
        
        // Add user message
        const userMessageDiv = document.createElement('div');
        userMessageDiv.className = 'text-right my-2';
        userMessageDiv.innerHTML = `<span class="bg-blue-600 text-white rounded-lg p-3 inline-block max-w-[80%] break-words">${message}</span>`;
        chatHistory.prepend(userMessageDiv);

        chatInput.value = '';
        showLoading();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });
            const data = await response.json();
            
            // Add AI response
            const aiMessageDiv = document.createElement('div');
            aiMessageDiv.className = 'text-left my-2';
            aiMessageDiv.innerHTML = `<span class="bg-gray-700 rounded-lg p-3 inline-block max-w-[80%] break-words">${data.response}</span>`;
            chatHistory.prepend(aiMessageDiv);

        } catch (error) {
            console.error('Error:', error);
            const errorMessageDiv = document.createElement('div');
            errorMessageDiv.className = 'text-left my-2';
            errorMessageDiv.innerHTML = `<span class="bg-red-500 rounded-lg p-3 inline-block max-w-[80%] break-words">Error: Failed to get response from server.</span>`;
            chatHistory.prepend(errorMessageDiv);
        } finally {
            hideLoading();
        }
    };

    const handleSummarize = async () => {
        if (isLoading) return;
        
        const text = summarizerInput.value.trim();
        const file = fileUpload.files[0];
        const type = summaryType.value;
        const selectedFileType = fileType.value;

        if (!text && !file) {
            summarizerOutput.textContent = "Please provide text or a file to summarize.";
            summarizerResults.classList.remove('hidden');
            return;
        }

        if (file && !selectedFileType) {
             summarizerOutput.textContent = "Please select the file type from the dropdown.";
             summarizerResults.classList.remove('hidden');
             return;
        }
        
        showLoading();

        try {
            const formData = new FormData();
            formData.append('summary_type', type);
            if (file) {
                formData.append('file', file);
                formData.append('file_type', selectedFileType);
            } else {
                formData.append('text', text);
            }

            const response = await fetch('/summarize', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            summarizerOutput.textContent = data.summary;

        } catch (error) {
            console.error('Error:', error);
            summarizerOutput.textContent = "Error: Failed to get summary from server.";
        } finally {
            hideLoading();
            summarizerResults.classList.remove('hidden');
        }
    };

    const handleExplain = async () => {
        if (isLoading) return;
        const codeText = explainerInput.value.trim();
        const type = explanationType.value;
        const language = codeLanguage.value;
        if (!codeText) {
            explainerOutput.textContent = "Please provide code to explain.";
            explainerResults.classList.remove('hidden');
            return;
        }

        showLoading();

        try {
            const response = await fetch('/explain', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: codeText, explanation_type: type, language: language })
            });
            const data = await response.json();
            explainerOutput.textContent = data.explanation;
        } catch (error) {
            console.error('Error:', error);
            explainerOutput.textContent = "Error: Failed to get explanation from server.";
        } finally {
            hideLoading();
            explainerResults.classList.remove('hidden');
        }
    };

    // --- Event Listeners ---
    chatBtn.addEventListener('click', () => setActiveView('chat-container'));
    summarizerBtn.addEventListener('click', () => setActiveView('summarizer-container'));
    explainerBtn.addEventListener('click', () => setActiveView('explainer-container'));
    
    chatSendBtn.addEventListener('click', handleChat);
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            handleChat();
        }
    });

    // Voice input event listeners
    chatMicBtn.addEventListener('click', () => {
        startVoiceRecording(chatInput, chatMicBtn, chatVoiceStatus);
    });

    summarizerMicBtn.addEventListener('click', () => {
        startVoiceRecording(summarizerInput, summarizerMicBtn, summarizerVoiceStatus);
    });

    summarizeBtn.addEventListener('click', handleSummarize);
    explainBtn.addEventListener('click', handleExplain);

    // Initialize speech recognition on page load
    initSpeechRecognition();

    // Initial state: show the Code Explainer
    setActiveView('explainer-container');
</script>

</body>
</html>
"""

# --- Flask Routes ---
@app.route("/")
def index():
    return render_template_string(HTML_CONTENT)

@app.route("/chat", methods=["POST"])
def chat_endpoint():
    data = request.json
    message = data.get("message", "")
    response_text = toolkit.chat_response(message)
    return jsonify({"response": response_text})

@app.route("/summarize", methods=["POST"])
def summarize_endpoint():
    file = request.files.get("file")
    file_type = request.form.get("file_type")
    text_content = request.form.get("text", "")

    if file:
        if file_type == "pdf":
            text_content = toolkit.extract_text_from_pdf(io.BytesIO(file.read()))
        elif file_type in ["txt", "json", "xml", "csv"]:
            try:
                # Decode as UTF-8 for general text files
                text_content = file.read().decode('utf-8')
                # For CSV, read and convert to string for summarization
                if file_type == "csv":
                    reader = csv.DictReader(io.StringIO(text_content))
                    text_content = json.dumps([row for row in reader], indent=2)
            except Exception as e:
                text_content = f"Error reading {file_type} file: {str(e)}"
        else:
            text_content = "Unsupported file type selected."

    if not text_content:
        summary_text = "No content provided to summarize."
    else:
        summary_type = request.form.get("summary_type", "detailed")
        summary_text = toolkit.summarize_text(text_content, summary_type)
        
    return jsonify({"summary": summary_text})

@app.route("/explain", methods=["POST"])
def explain_endpoint():
    data = request.json
    code = data.get("code", "")
    explanation_type = data.get("explanation_type", "simple")
    language = data.get("language", "general")
    explanation_text = toolkit.explain_code(code, explanation_type, language)
    return jsonify({"explanation": explanation_text})

if __name__ == "__main__":
    # --- Code to automatically open browser ---
    def open_browser():
        time.sleep(1) # Give the server a moment to start
        webbrowser.open("http://127.0.0.1:5000")
        
    threading.Thread(target=open_browser).start()
    # --- End of automatic open code ---
    app.run(debug=True)