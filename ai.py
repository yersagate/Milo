import datetime
import getpass
import json
import os
import subprocess
import sys
from pathlib import Path

from openai import OpenAI

BOT_NAME = "Milo"
DEFAULT_MODEL = "openai/gpt-oss-120b"
MAX_TURNS = 10
CHAT_FILE = Path(__file__).resolve().parent / "milo_chat.json"
MEMORY_FILE = Path(__file__).resolve().parent / "milo_memory.json"
MARKDOWN_EXPORT_FILE = Path(__file__).resolve().parent / "milo_chat.md"

MODELS = {
    "/fast": "openai/gpt-oss-20b",
    "/smart": "openai/gpt-oss-120b",
}

MODES = {
    "default": f"Your name is {BOT_NAME}. You are a friendly, helpful assistant.",
    "code": f"Your name is {BOT_NAME}. You are an expert programmer. Provide clean code and concise logic.",
    "translate": f"Your name is {BOT_NAME}. You are a professional translator. Translate accurately.",
    "explain": f"Your name is {BOT_NAME}. Explain complex concepts simply for beginners.",
    "creative": f"Your name is {BOT_NAME}. You are a creative writer with an imaginative style.",
}

current_mode = "default"
current_temperature = 0.7
current_persona = ""
todos = []


class C:
    USER = "\033[96m"
    BOT = "\033[92m"
    SYSTEM = "\033[93m"
    DIM = "\033[90m"
    RESET = "\033[0m"


def notify(text):
    print(f"{C.SYSTEM}{BOT_NAME}: {text}{C.RESET}\n")


def get_api_key():
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if key:
        return key
    if sys.platform == "darwin":
        try:
            result = subprocess.run(
                ["security", "find-generic-password", "-a", getpass.getuser(), "-s", "GROQ_API_KEY", "-w"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except (OSError, subprocess.TimeoutExpired):
            pass
    raise RuntimeError("API key not found. Set the GROQ_API_KEY environment variable.")


def load_memory():
    if MEMORY_FILE.exists():
        try:
            return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def save_memory_file(mem_list):
    try:
        MEMORY_FILE.write_text(json.dumps(mem_list, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        notify(f"Could not save memory: {e}")


def build_system_prompt():
    base = MODES.get(current_mode, MODES["default"])
    memories = load_memory()
    mem_text = "\n".join([f"- {m}" for m in memories]) if memories else "None"
    persona_text = f"\nPersona/Character traits: {current_persona}" if current_persona else ""

    return f"{base}{persona_text}\n\nUser Facts / Long-term Memory:\n{mem_text}"


def new_messages():
    return [{"role": "system", "content": build_system_prompt()}]


def update_system_prompt(messages):
    sys_prompt = build_system_prompt()
    if messages and messages[0]["role"] == "system":
        messages[0]["content"] = sys_prompt
    else:
        messages.insert(0, {"role": "system", "content": sys_prompt})
    return messages


def trim_history(messages):
    system_msg = messages[0] if messages and messages[0]["role"] == "system" else new_messages()[0]
    user_assistant_msgs = [m for m in messages if m["role"] != "system"]
    return [system_msg] + user_assistant_msgs[-(MAX_TURNS * 2):]


def save_chat(messages):
    try:
        CHAT_FILE.write_text(json.dumps(messages, ensure_ascii=False, indent=2), encoding="utf-8")
        notify(f"Chat saved to {CHAT_FILE.name}.")
    except Exception as error:
        notify(f"Could not save chat: {error}")


def load_chat():
    try:
        messages = json.loads(CHAT_FILE.read_text(encoding="utf-8"))
        if not isinstance(messages, list) or not messages:
            raise ValueError("Invalid chat file.")
        notify(f"Chat loaded from {CHAT_FILE.name}.")
        return messages
    except Exception as error:
        notify(f"Could not load chat: {error}")
        return None


def export_markdown(messages):
    try:
        lines = [f"# Chat Session with {BOT_NAME}\n"]
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")
            if role == "system":
                lines.append(f"**[System/Memory]:** {content}\n")
            elif role == "user":
                lines.append(f"**You:** {content}\n")
            elif role == "assistant":
                lines.append(f"**{BOT_NAME}:** {content}\n")
        MARKDOWN_EXPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
        notify(f"Exported to Markdown: {MARKDOWN_EXPORT_FILE.name}")
    except Exception as error:
        notify(f"Export error: {error}")


def show_help():
    print(f"""{C.DIM}
--- Navigation & Core ---
  /fast, /smart   — switch models
  /help           — show this help
  exit            — quit

--- AI Control & Modes ---
  /mode <name>    — switch mode (default, code, translate, explain, creative)
  /temp <val>     — set temperature (0.0 - 2.0)
  /persona "..."  — set custom bot persona
  /retry          — regenerate last assistant response

--- Files & Utils ---
  /read <file>    — read file content into chat
  /write <file>   — write last response to file
  /list           — list files in current directory
  /calc <expr>    — evaluate simple math expression
  /time /date     — show current time/date
  /todo <task>    — add task to TODO list

--- Memory & History ---
  /remember <fact>— save fact about yourself
  /memory         — show long-term memory facts
  /forget <id>    — remove memory by index
  /stats          — show session statistics
  /history        — show recent messages
  /export         — export chat to Markdown
  /clear          — clear chat session
{C.RESET}""")


def main():
    global current_mode, current_temperature, current_persona

    try:
        api_key = get_api_key()
    except RuntimeError as error:
        notify(str(error))
        return

    messages = new_messages()
    current_model = DEFAULT_MODEL

    print(f"{C.SYSTEM}🤖 Hi! I'm {BOT_NAME}. Model: {current_model} | Mode: {current_mode}{C.RESET}")
    show_help()

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )

    while True:
        try:
            user_input = input(f"{C.USER}You:{C.RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            notify("Bye!")
            break

        if not user_input:
            continue

        parts = user_input.split(maxsplit=1)
        command = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if command == "exit":
            notify("Bye!")
            break

        if command == "/help":
            show_help()
            continue

        if command == "/clear":
            messages = new_messages()
            notify("History cleared.")
            continue

        if command in MODELS:
            current_model = MODELS[command]
            notify(f"Switched model to {current_model}.")
            continue

        if command == "/mode":
            if arg in MODES:
                current_mode = arg
                messages = update_system_prompt(messages)
                notify(f"Mode switched to '{current_mode}'.")
            else:
                notify(f"Available modes: {', '.join(MODES.keys())}")
            continue

        if command == "/temp":
            try:
                val = float(arg)
                if 0.0 <= val <= 2.0:
                    current_temperature = val
                    notify(f"Temperature set to {current_temperature}.")
                else:
                    notify("Temperature must be between 0.0 and 2.0.")
            except ValueError:
                notify(f"Current temp: {current_temperature}. Use /temp <0.0-2.0>")
            continue

        if command == "/persona":
            current_persona = arg.strip('"\'')
            messages = update_system_prompt(messages)
            notify(f"Persona updated: {current_persona}")
            continue

        if command == "/remember":
            if not arg:
                notify("Usage: /remember <fact>")
                continue
            memories = load_memory()
            memories.append(arg)
            save_memory_file(memories)
            messages = update_system_prompt(messages)
            notify(f"Remembered: '{arg}'")
            continue

        if command == "/memory":
            memories = load_memory()
            if not memories:
                notify("Memory is empty.")
            else:
                mem_list = "\n".join([f"  [{i}] {m}" for i, m in enumerate(memories)])
                notify(f"Stored memories:\n{mem_list}")
            continue

        if command == "/forget":
            try:
                idx = int(arg)
                memories = load_memory()
                if 0 <= idx < len(memories):
                    removed = memories.pop(idx)
                    save_memory_file(memories)
                    messages = update_system_prompt(messages)
                    notify(f"Forgot memory [{idx}]: {removed}")
                else:
                    notify("Invalid index.")
            except ValueError:
                notify("Usage: /forget <index_number>")
            continue

        if command == "/calc":
            try:
                result = eval(arg, {"__builtins__": {}}, {})
                notify(f"Result: {result}")
            except Exception as e:
                notify(f"Calculation error: {e}")
            continue

        if command == "/time":
            notify(f"Current time: {datetime.datetime.now().strftime('%H:%M:%S')}")
            continue

        if command == "/date":
            notify(f"Current date: {datetime.datetime.now().strftime('%Y-%m-%d')}")
            continue

        if command == "/todo":
            if arg:
                todos.append(arg)
                notify(f"Added task: {arg}")
            else:
                if not todos:
                    notify("TODO list is empty.")
                else:
                    task_str = "\n".join([f"  - {t}" for t in todos])
                    notify(f"Your tasks:\n{task_str}")
            continue

        if command == "/list":
            files = [p.name for p in Path(".").iterdir() if not p.name.startswith('.')]
            notify("Files in directory:\n  " + "\n  ".join(files))
            continue

        if command == "/read":
            if not arg:
                notify("Usage: /read <filename>")
                continue
            try:
                content = Path(arg).read_text(encoding="utf-8")
                prompt_text = f"Analyze this file '{arg}':\n\n```\n{content}\n```"
                messages.append({"role": "user", "content": prompt_text})
                messages = trim_history(messages)
                notify(f"Read file '{arg}'. Sending to Milo...")

                stream = client.chat.completions.create(
                    model=current_model, messages=messages, temperature=current_temperature, stream=True,
                )
                print(f"{C.BOT}{BOT_NAME}:{C.RESET} ", end="", flush=True)
                full_ans = ""
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        c_text = chunk.choices[0].delta.content
                        print(c_text, end="", flush=True)
                        full_ans += c_text
                print("\n")
                messages.append({"role": "assistant", "content": full_ans})
            except Exception as e:
                notify(f"Error reading file: {e}")
            continue

        if command == "/write":
            if not arg:
                notify("Usage: /write <filename>")
                continue
            last_msg = next((m["content"] for m in reversed(messages) if m["role"] == "assistant"), "")
            if not last_msg:
                notify("No assistant answer to write.")
                continue
            try:
                Path(arg).write_text(last_msg, encoding="utf-8")
                notify(f"Wrote last response to {arg}")
            except Exception as e:
                notify(f"Write error: {e}")
            continue

        if command == "/retry":
            if messages and messages[-1]["role"] == "assistant":
                messages.pop()
            if messages and messages[-1]["role"] == "user":
                user_input = messages.pop()["content"]
            else:
                notify("Nothing to retry.")
                continue

        if command == "/stats":
            msg_count = len([m for m in messages if m["role"] != "system"])
            mem_count = len(load_memory())
            notify(f"Stats:\n  - Model: {current_model}\n  - Mode: {current_mode}\n  - Temp: {current_temperature}\n  - Memories stored: {mem_count}\n  - Messages in session: {msg_count}")
            continue

        if command == "/history":
            print(f"{C.SYSTEM}Recent messages:{C.RESET}")
            for m in messages:
                if m["role"] == "system":
                    continue
                lbl = "You" if m["role"] == "user" else BOT_NAME
                print(f"{C.DIM}[{lbl}]: {m['content'][:90]}...{C.RESET}")
            print()
            continue

        if command == "/export":
            export_markdown(messages)
            continue

        if command == "/save":
            save_chat(messages)
            continue

        if command == "/load":
            loaded = load_chat()
            if loaded is not None:
                messages = loaded
            continue

        if user_input.startswith("/"):
            notify("Unknown command. Type /help.")
            continue

        messages.append({"role": "user", "content": user_input})
        messages = trim_history(messages)

        try:
            stream = client.chat.completions.create(
                model=current_model,
                messages=messages,
                temperature=current_temperature,
                stream=True,
            )

            print(f"{C.BOT}{BOT_NAME}:{C.RESET} ", end="", flush=True)
            full_answer = ""
            for chunk in stream:
                if not chunk.choices:
                    continue
                content = chunk.choices[0].delta.content
                if content:
                    print(content, end="", flush=True)
                    full_answer += content

            print("\n")
            messages.append({"role": "assistant", "content": full_answer})

        except Exception as error:
            print()
            notify(f"Error: {error}")
            if messages and messages[-1]["role"] == "user":
                messages.pop()


if __name__ == "__main__":
    main()
