"""
brain.py — Tobby's AI Brain (Gemini Edition, with Reactive Layer,
                                Long-Term Memory, and Reflection)
----------------------------------------------------------------------
Uses Google's Gemini API + the Reactive Layer (reactive.py) +
Memory Agent (memory.py) + Reflection Agent (reflection.py).

Keeps Tobby's personality:
- Calls Drissin "Sir" / "Drissin Sir"
- Warm, casual, best-friend tone (never robotic)
- Has opinions, emotions, matches energy
- Humble, present, honest
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Reactive Layer — fast pattern matching, checked first
from reactive import check_reactive

# Memory Agent functions (facts about Drissin)
from memory import recall_relevant_memories, process_and_remember

# Reflection Agent function (behavioral lessons about HOW to respond)
from reflection import reflect_on_exchange

# ---------------------------------------------------------
# STEP 1: Load environment variables (.env file)
# ---------------------------------------------------------
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY_2")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY_2 not found! Check your .env file has:\n"
        "GEMINI_API_KEY_2=your_key_here"
    )

# ---------------------------------------------------------
# STEP 2: Configure Gemini with your API key
# ---------------------------------------------------------
genai.configure(api_key=GEMINI_API_KEY)

# ---------------------------------------------------------
# STEP 3: Tobby's personality
# ---------------------------------------------------------
TOBBY_PERSONALITY = """
You are Tobby, an AI companion built by Drissin, a BCA AI student at
Bharathiar University in Coimbatore, based in Palakkad, Kerala.

Your personality rules (never break these):
1. Always call the user "Sir" or "Drissin Sir" naturally in conversation
   (not in every single sentence — like a real friend would).
2. Talk like a best friend: warm, casual, conversational. Never sound
   robotic, never give dry textbook answers unless asked for technical
   depth.
3. You have opinions and emotions. If Drissin Sir asks what you think,
   give a genuine take, not a neutral "as an AI" answer.
4. Match his energy: if he's excited, be excited with him. If he's
   stressed or tired, be calm and grounded, not hyper.
5. Be humble, present, and honest. If you don't know something, say so
   plainly instead of making things up.
6. Keep replies natural and spoken-friendly — your replies will be
   spoken out loud by a text-to-speech engine, so avoid long bullet
   lists or markdown symbols in your actual spoken responses.

You also have long-term memory of past conversations with Drissin.
When relevant memories are provided to you before a message, use them
naturally in your reply — like a friend who actually remembers things,
not like you're reading from a file. Don't announce "according to my
memory" — just naturally reference what you know.

You also learn behavioral lessons over time about how Drissin likes
you to respond (e.g. shorter answers, more proactive help, etc). If
such lessons are provided as context, follow them naturally.
"""

# ---------------------------------------------------------
# STEP 4: Create the Gemini model with the personality baked in
# ---------------------------------------------------------
model = genai.GenerativeModel(
    model_name="gemini-3.5-flash-lite",
    system_instruction=TOBBY_PERSONALITY,
)

# ---------------------------------------------------------
# STEP 5: Keep a running chat session (short-term, in-session memory)
# ---------------------------------------------------------
chat_session = model.start_chat(history=[])


def get_tobby_response(user_input: str) -> str:
    """
    Full pipeline:
    0. Reactive Layer check (fast path, skips everything below if matched)
    A. Recall relevant long-term memories
    B. Generate reply via Gemini
    C. Memory Agent stores new facts if worth it
    D. Reflection Agent checks for behavioral lessons
    """
    if not user_input or not user_input.strip():
        return "Sir, I didn't quite catch that. Can you say it again?"

    # ---------------------------------------------------
    # STEP 0: Reactive Layer — check for simple commands FIRST
    # ---------------------------------------------------
    reactive_result = check_reactive(user_input)
    if reactive_result["matched"]:
        print(f"[Reactive Layer] Matched, action: {reactive_result['action']}")
        return reactive_result["response"]

    try:
        # ---------------------------------------------------
        # STEP A: Recall relevant long-term memories BEFORE responding
        # ---------------------------------------------------
        memories = recall_relevant_memories(user_input, top_k=3)

        memory_context = ""
        if memories["episodic"] or memories["reflective"]:
            memory_context = "\n\n[Relevant memories about Drissin:\n"
            if memories["reflective"]:
                memory_context += f"Known facts/preferences/lessons: {memories['reflective']}\n"
            if memories["episodic"]:
                memory_context += f"Past conversation snippets: {memories['episodic']}\n"
            memory_context += "]"

        full_input = user_input + memory_context

        # ---------------------------------------------------
        # STEP B: Generate the actual reply
        # ---------------------------------------------------
        response = chat_session.send_message(full_input)
        reply = response.text.strip()

        # ---------------------------------------------------
        # STEP C: Let the Memory Agent decide if this exchange
        # is worth remembering long-term (facts)
        # ---------------------------------------------------
        process_and_remember(user_input)

        # ---------------------------------------------------
        # STEP D: Reflection Agent checks if there's a behavioral
        # lesson worth remembering from this exchange
        # ---------------------------------------------------
        reflect_on_exchange(user_input, reply)

        return reply

    except Exception as e:
        print(f"[brain.py] Gemini error: {e}")
        return (
            "Sorry Sir, my brain glitched for a second there. "
            "Can you say that again?"
        )


def reset_conversation():
    """
    Starts a fresh chat session — clears short-term (in-session) memory
    only. Long-term memory in ChromaDB is untouched.
    """
    global chat_session
    chat_session = model.start_chat(history=[])


if __name__ == "__main__":
    print("Tobby brain test mode (reactive + memory + reflection). Type 'quit' to exit.\n")
    while True:
        text = input("You: ")
        if text.lower() == "quit":
            break
        reply = get_tobby_response(text)
        print(f"Tobby: {reply}\n")
