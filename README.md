# Milo AI Assistant

Milo is a modular terminal and web AI assistant powered by Groq. It includes long-term memory, RAG-based document search, autonomous multi-agent workflows, file tools, and a voice interface.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-brightgreen)

## Features

- **Core UX & Modes:** Dynamic role switching (`/mode code`, `/mode translate`, etc.), temperature tuning, and chat history export.
- **Long-term Memory:** JSON-based factual memory with `/remember` and `/memory`.
- **File Management & Tools:** File analysis, code generation, built-in calculator, and task lists.
- **RAG Engine:** Semantic and keyword search across PDF, TXT, and Markdown documents.
- **Voice Interface:** Speech-to-text with Groq Whisper and local text-to-speech.
- **Autonomous Agents:** Multi-step planning, coding, and review loops.
- **Web GUI:** Streamlit-based browser interface.

## Project Structure

| File | Purpose |
|---|---|
| `ai.py` | Main terminal interface: commands, modes, memory, and built-in tools |
| `app.py` | Streamlit web interface |
| `milo_rag.py` | Local document indexing and RAG search |
| `milo_voice.py` | Voice interface using Groq Whisper and local TTS |
| `milo_agent.py` | Autonomous multi-agent task execution loop |

## Requirements

- Python **3.10 or newer**
- A Groq API key
- Internet connection for Groq API requests
- Optional: PortAudio, required for microphone input with `sounddevice`

## Installation

### 1. Clone the repository

```bash
git clone [https://github.com/yersagate/Milo.git](https://github.com/yersagate/Milo.git)
cd Milo
```

### 2. Create a virtual environment

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows — Command Prompt:**

```bat
python -m venv venv
venv\Scripts\activate
```

**Windows — PowerShell:**

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install openai pypdf sounddevice scipy pyttsx3 streamlit
```

> On Linux, if `sounddevice` fails to install, install PortAudio first:
>
> **Debian / Ubuntu:**
> ```bash
> sudo apt update
> sudo apt install portaudio19-dev
> ```
>
> **Fedora:**
> ```bash
> sudo dnf install portaudio-devel
> ```
>
> **Arch Linux:**
> ```bash
> sudo pacman -S portaudio
> ```
>
> Then run the `pip install` command again.

### 4. Configure your Groq API key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Alternatively, set it as an environment variable.

**macOS / Linux:**

```bash
export GROQ_API_KEY="your_groq_api_key_here"
```

**Windows — Command Prompt:**

```bat
set GROQ_API_KEY=your_groq_api_key_here
```

**Windows — PowerShell:**

```powershell
$env:GROQ_API_KEY = "your_groq_api_key_here"
```

## Usage

### Terminal interface

```bash
python ai.py
```

### Web interface

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

## Voice Support

Voice features require a working microphone and audio output device.

- **macOS:** Install PortAudio with Homebrew:
  ```bash
  brew install portaudio
  ```
- **Windows:** PortAudio is usually installed automatically with `sounddevice`; if microphone access fails, check Windows microphone permissions.
- **Linux:** Install PortAudio through your package manager, as shown above.

## Troubleshooting

- **`GROQ_API_KEY` not found:** Make sure the `.env` file exists or the environment variable is set in the same terminal session.
- **`sounddevice` installation error:** Install PortAudio for your operating system, then reinstall dependencies.
- **Microphone not detected:** Check system microphone permissions and ensure no other application is using the device.
- **Streamlit does not open:** Run `streamlit run app.py` from the project root and use the URL printed in the terminal.

## License

This project is licensed under the [MIT License](LICENSE).
