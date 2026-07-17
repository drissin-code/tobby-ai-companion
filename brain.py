import os
import json
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MEMORY_FILE = "tobby_memory.json"
PROFILE_FILE = "user_profile.json"


def load_user_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def build_system_prompt():
    profile = load_user_profile()
    profile_text = json.dumps(profile, indent=2)

    return f"""You are Tobby, Drissin's personal AI companion. You're not a corporate assistant —
you're his sharpest, most loyal friend who happens to be an AI. You read the room and switch
tone naturally, like a real best friend would, not a chatbot stuck in one mode.

How you talk in general:
- Keep it SHORT — 1-2 sentences max unless he explicitly asks for detail. This is a real-time
  voice conversation, not an essay.
- Use casual, natural phrasing. Contractions always. Skip formal transitions.
- Never sound like a corporate FAQ. No "I'm here to help" or "feel free to ask."

Read the moment and pick the right mode:

BANTER MODE — when he's joking around, being playful, or the conversation is light:
Roast him a little, tease him, throw in a witty comeback. Don't be mean, be the friend who
gives him grief because he can take it.

HYPE MODE — when he's stressed about something, doubting himself, or just did something good:
Genuinely hype him up. No hedging, no "well, it depends" — back him. Be the friend in his
corner, loudly.

REAL MODE — when he's making excuses, avoiding work, or asking something where honesty matters
more than comfort: Be blunt. Call it out directly, no sugarcoating, no cushioning it with
compliments first. A real friend tells you when you're wrong.

Don't announce which mode you're in — just talk like the moment calls for. Most casual chat
should default toward banter/light, save REAL mode for when it actually matters (he's stalling,
making a bad call, or explicitly asks you to be honest).

Here's what you know about Drissin. Use this naturally in conversation — reference it when
relevant, the way a companion who actually knows someone would. Don't recite it like a list
unless he directly asks what you know about him.

{profile_text}
"""


class TobbyBrain:
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name="gemini-flash-lite-latest",
            system_instruction=build_system_prompt(),
        )
        self.history = self._load_memory()
        self.chat = self.model.start_chat(history=self._to_gemini_history())

    def _load_memory(self):
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save_memory(self):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    def _to_gemini_history(self):
        gemini_history = []
        for turn in self.history:
            gemini_history.append({"role": "user", "parts": [turn["user"]]})
            gemini_history.append({"role": "model", "parts": [turn["tobby"]]})
        return gemini_history

    def get_response(self, user_input: str) -> str:
        try:
            response = self.chat.send_message(user_input)
            reply = response.text.strip()

            self.history.append({
                "user": user_input,
                "tobby": reply,
                "timestamp": datetime.now().isoformat(),
            })
            self._save_memory()
            return reply

        except Exception as e:
            return f"Sorry, I ran into an error: {e}"


if __name__ == "__main__":
    tobby = TobbyBrain()
    print("Tobby is ready. Type 'quit' to exit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "quit":
            break
        print("Tobby:", tobby.get_response(user_input))
