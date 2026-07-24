"""
file_agent.py — Tobby's File Access Agent (Phase 7b)
----------------------------------------------------------------
Lets Tobby read files, list folders, and create/append simple
notes — all restricted to a safe working folder (tobby_files/)
rather than the whole filesystem, for safety.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY_2")
genai.configure(api_key=GEMINI_API_KEY)

file_model = genai.GenerativeModel(model_name="gemini-3.5-flash-lite")

# ---------------------------------------------------------
# Safety boundary: Tobby can only access files inside this folder.
# This gets created automatically if it doesn't exist.
# ---------------------------------------------------------
SAFE_FOLDER = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "tobby_files")
os.makedirs(SAFE_FOLDER, exist_ok=True)


def _safe_path(filename: str) -> str:
    """
    Resolves a filename to a path INSIDE the safe folder only.
    Prevents things like '../../secrets.txt' from escaping the
    safe folder.
    """
    filename = os.path.basename(filename)  # strips any path traversal
    return os.path.join(SAFE_FOLDER, filename)


def list_files() -> str:
    """Lists all files currently in Tobby's safe folder."""
    files = os.listdir(SAFE_FOLDER)
    if not files:
        return "There's nothing in your files folder yet, Sir."
    return "Here's what's in your files folder: " + ", ".join(files)


def read_file(filename: str, question: str = "") -> str:
    """
    Reads a file and either summarizes it or answers a specific
    question about its contents.
    """
    path = _safe_path(filename)

    if not os.path.exists(path):
        return f"I couldn't find a file called '{filename}' in your files folder, Sir."

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        return f"Sorry Sir, I ran into trouble reading that file: {e}"

    if not content.strip():
        return f"'{filename}' looks empty, Sir."

    prompt = f"""
You are Tobby. Drissin asked about a file called '{filename}'.
His question: "{question if question else 'Summarize this file for me'}"

FILE CONTENTS:
{content[:8000]}

Answer clearly and concisely, spoken-friendly (this may be read aloud).
Call him "Sir" naturally.
"""
    response = file_model.generate_content(prompt)
    return response.text.strip()


def write_note(text: str, filename: str = "notes.txt") -> str:
    """
    Appends a note to a simple text file (default: notes.txt).
    Creates the file if it doesn't exist yet.
    """
    path = _safe_path(filename)

    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(text.strip() + "\n")
        return f"Got it, Sir — added that to {filename}."
    except Exception as e:
        return f"Sorry Sir, I couldn't save that note: {e}"


if __name__ == "__main__":
    print("Testing File Agent...\n")

    print("--- Listing files (should be empty first time) ---")
    print(list_files())

    print("\n--- Writing a note ---")
    print(write_note("Remember to submit AI/ML assignment by Friday"))

    print("\n--- Listing files again ---")
    print(list_files())

    print("\n--- Reading the note back ---")
    print(read_file("notes.txt", "What does this note say?"))
