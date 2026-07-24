"""
reactive.py — Tobby's Reactive Layer
----------------------------------------
Fast pattern-matching for simple, common commands that don't need
full LLM reasoning. Runs BEFORE the main brain pipeline — if
something matches here, we skip memory recall, Gemini, and
reflection entirely for speed.
"""

REACTIVE_PATTERNS = [
    {
        "triggers": ["tobby stop", "stop tobby", "stop"],
        "response": "Okay Sir, going quiet now.",
        "action": "stop",
    },
    {
        "triggers": ["go to sleep", "sleep now", "goodnight tobby"],
        "response": "Alright Sir, catch you later.",
        "action": "sleep",
    },
    {
        "triggers": ["are you there", "you there", "tobby you there"],
        "response": "Yeah, I'm right here Sir.",
        "action": None,
    },
    {
        "triggers": ["what time is it", "current time"],
        "response": None,  # handled dynamically below
        "action": "get_time",
    },
]


def check_reactive(user_input: str):
    """
    Checks if the user's input matches a known reactive pattern.
    Returns {"matched": bool, "response": str, "action": str}
    or {"matched": False} if nothing matched.
    """
    text = user_input.lower().strip()

    for pattern in REACTIVE_PATTERNS:
        for trigger in pattern["triggers"]:
            if trigger in text:
                response = pattern["response"]

                if pattern["action"] == "get_time":
                    from datetime import datetime
                    now = datetime.now().strftime("%I:%M %p")
                    response = f"It's {now}, Sir."

                return {
                    "matched": True,
                    "response": response,
                    "action": pattern["action"],
                }

    return {"matched": False}


if __name__ == "__main__":
    print("Testing Reactive Layer...\n")

    test_inputs = [
        "tobby stop",
        "hey are you there",
        "what time is it",
        "tell me a joke",
    ]

    for text in test_inputs:
        result = check_reactive(text)
        print(f"Input: {text}")
        print(f"Result: {result}\n")
