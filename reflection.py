"""
reflection.py — Tobby's Reflection Agent
--------------------------------------------
After each conversation exchange, this agent asks:
"Did this go well? Is there a lasting lesson about HOW to
respond to Drissin, based on how this exchange played out?"

This catches BOTH:
- Corrective signals (Drissin was annoyed, asked for a change)
- Positive signals (Drissin responded well to something specific)

Different from the Memory Agent (memory.py), which stores FACTS.
This agent stores BEHAVIORAL lessons — things that shape Tobby's
future responses, not just what he knows.
"""

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

from memory import save_reflective_memory, recall_relevant_memories

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY_2")
genai.configure(api_key=GEMINI_API_KEY)

reflection_model = genai.GenerativeModel(model_name="gemini-3.5-flash-lite")


def reflect_on_exchange(user_input: str, tobby_reply: str):
    """
    Looks at one conversation exchange and decides if there's a
    lasting BEHAVIORAL lesson worth remembering — either a
    correction to avoid repeating, or a positive pattern worth
    reinforcing.
    """
    existing = recall_relevant_memories(user_input, top_k=3)
    existing_lessons = existing["reflective"] if existing["reflective"] else []

    prompt = f"""
You are Tobby's reflection system. Your job is to look at ONE
conversation exchange and decide if there's a lasting BEHAVIORAL
lesson worth remembering — something about HOW Tobby should respond
to Drissin in the future, not just what facts were discussed.

THE EXCHANGE:
Drissin said: "{user_input}"
Tobby replied: "{tobby_reply}"

EXISTING LESSONS ALREADY REMEMBERED (don't repeat these):
{existing_lessons}

Respond ONLY in this exact JSON format, nothing else, no markdown:

{{
  "lesson_found": true or false,
  "lesson_type": "corrective" or "positive" or "none",
  "lesson": "one short sentence describing the behavioral lesson, or empty string if none",
  "reason": "one short sentence explaining why this is or isn't worth remembering"
}}

Look for TWO kinds of signals:

1. CORRECTIVE signals — Drissin was annoyed, corrected Tobby, asked
   for a different style/length/tone, or reacted negatively to HOW
   Tobby responded.
   Example: "Drissin prefers short answers when discussing deadlines"

2. POSITIVE signals — Drissin responded with clear enthusiasm,
   engagement, gratitude, or explicitly praised something specific
   about HOW Tobby responded (not just the content/facts, but the
   STYLE — e.g. an analogy landed well, a joke worked, a proactive
   offer was appreciated).
   Example: "Drissin engages well when Tobby uses AI/tech analogies
   to explain things"
   Example: "Drissin appreciates when Tobby proactively offers to
   help break tasks into steps"

Rules:
- A lesson should be about Tobby's BEHAVIOR/STYLE, not a fact about
  Drissin's life (that's the Memory Agent's job, not yours).
- Don't invent a lesson from a single neutral exchange — only flag
  genuine, clear signals (either corrective or positive).
- Most normal exchanges have NO signal at all — that's expected and
  fine. Only flag when the reaction is clear, not subtle or assumed.
- If nothing meaningful happened, lesson_found = false and
  lesson_type = "none"
"""

    response = reflection_model.generate_content(prompt)
    raw = response.text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        return {
            "lesson_found": False,
            "lesson_type": "none",
            "lesson": "",
            "reason": "Failed to parse reflection output, skipping to be safe",
        }

    if result.get("lesson_found") and result.get("lesson"):
        save_reflective_memory(result["lesson"])
        lesson_type = result.get("lesson_type", "unknown")
        print(
            f"[Reflection Agent] New {lesson_type} lesson learned: {result['lesson']}")
    else:
        print(f"[Reflection Agent] No lesson: {result.get('reason', '')}")

    return result


if __name__ == "__main__":
    print("Testing Reflection Agent (corrective + positive)...\n")

    # Test 1: Corrective signal (likely already known from past testing)
    print("--- Test 1: Corrective ---")
    test_user_1 = "bro just give me a quick answer next time, that was too long"
    test_reply_1 = (
        "Got it, Sir! I'll keep things shorter and more to the point "
        "from now on."
    )
    reflect_on_exchange(test_user_1, test_reply_1)

    # Test 2: Positive signal (likely already known from past testing)
    print("\n--- Test 2: Positive (analogy) ---")
    test_user_2 = "haha that analogy actually made it click, thanks!"
    test_reply_2 = (
        "Glad that landed, Sir! I'll keep using analogies like that "
        "when explaining tricky concepts."
    )
    reflect_on_exchange(test_user_2, test_reply_2)

    # Test 3: A genuinely NEW positive signal, unrelated to anything
    # tested before — this is the real test of the broadened prompt
    print("\n--- Test 3: Positive (humor, fresh scenario) ---")
    test_user_3 = "lol that joke about semicolons actually got me, you're funnier than I expected"
    test_reply_3 = (
        "Ha, glad I could bring some humor to your coding session, Sir! "
        "I'll keep it light when I can."
    )
    reflect_on_exchange(test_user_3, test_reply_3)
