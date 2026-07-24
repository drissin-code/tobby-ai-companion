"""
screen_perception.py — Tobby's Screen Perception (Phase 7)
----------------------------------------------------------------
Lets Tobby take a screenshot and answer questions about what's
currently on Drissin's screen, using Gemini's native image
understanding (multimodal input).
"""

import os
import mss
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY_2")
genai.configure(api_key=GEMINI_API_KEY)

vision_model = genai.GenerativeModel(model_name="gemini-3.5-flash-lite")


def capture_screenshot() -> Image.Image:
    """
    Captures the current screen (primary monitor) and returns it
    as a PIL Image, ready to send to Gemini.
    """
    with mss.MSS() as sct:
        # monitor index 1 = primary monitor (0 = all monitors combined)
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)

        # Convert raw screenshot data into a PIL Image
        img = Image.frombytes(
            "RGB", screenshot.size, screenshot.bgra, "raw", "BGRX"
        )
        return img


def ask_about_screen(question: str) -> str:
    """
    Takes a screenshot and asks Gemini to answer a question about
    what's currently visible on screen.
    """
    try:
        screenshot = capture_screenshot()

        prompt = f"""
You are Tobby, looking at Drissin's screen right now. He asked:
"{question}"

Describe only what's relevant to answering his question. Keep your
answer short and spoken-friendly (this will be read aloud), and
call him "Sir" naturally. If the screen doesn't show anything
relevant to his question, say so honestly instead of guessing.
"""

        response = vision_model.generate_content([prompt, screenshot])
        return response.text.strip()

    except Exception as e:
        print(f"[Screen Perception] Error: {e}")
        return (
            "Sorry Sir, I ran into an issue trying to look at your "
            "screen just now."
        )


if __name__ == "__main__":
    print("Testing Screen Perception...\n")
    print("Taking a screenshot of your current screen in 3 seconds...")
    import time
    time.sleep(3)

    answer = ask_about_screen("What am I currently looking at?")
    print(f"\nTobby: {answer}")
