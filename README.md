# Milo AI Assistant

Milo is a modular terminal and web AI assistant powered by Groq, featuring advanced memory, RAG document search, autonomous multi-agent loops, and a voice interface.

## Features

- **Core UX & Modes**: Dynamic role switching (`/mode code`, `/mode translate`, etc.), temperature tuning, and history export.
- **Long-term Memory**: JSON-based factual memory (`/remember`, `/memory`).
- **File Management & Tools**: Direct file analysis, code generation, built-in calculator, and task lists.
- **RAG Engine**: Semantic and keyword search across PDF, TXT, and Markdown documents.
- **Voice Interface**: Whisper STT and local TTS integration.
- **Autonomous Agents**: Multi-step planning, coding, and review loops.
- **Web GUI**: Streamlit-based interactive browser interface.

## Project Structure

- `ai.py` - Main terminal interface with commands, modes, memory, and built-in tools.
- `app.py` - Streamlit web interface for browser usage.
- `milo_rag.py` - RAG module for local document indexing and search.
- `milo_voice.py` - Voice interface module using Groq Whisper and local TTS.
- `milo_agent.py` - Multi-agent autonomous task execution loop.

## Getting Started (macOS Guide)

### 1. System Requirements & PortAudio
Ensure you have Python (version 3.10 or higher) and Homebrew installed. For voice capabilities (`sounddevice`), install PortAudio:
```bash
brew install portaudio
```

### 2. Virtual Environment & Dependencies
Navigate to your project directory, create a virtual environment, and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install openai pypdf sounddevice scipy pyttsx3 streamlit
```

### 3. API Key Configuration
Set your Groq API key as an environment variable in your terminal:
```bash
export GROQ_API_KEY="your_groq_api_key_here"
```

### 4. Running the Terminal Interface
To launch the main console assistant:
```bash
python3 ai.py
```

### 5. Running the Web Interface
To launch the Streamlit web GUI in your browser:
```bash
streamlit run app.py
```