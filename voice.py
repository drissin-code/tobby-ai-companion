import os
import edge_tts
import asyncio
import pygame
import tempfile
import time
from dotenv import load_dotenv

load_dotenv()

# en-US-AvaNeural: polished, expressive American female voice —
# sits closer to a "premium concierge" tone than older voices like
# Aria or Jenny. Good alternatives if this isn't quite right:
#   "en-US-EmmaNeural"  - warm, professional, slightly softer
#   "en-US-AriaNeural"  - classic, clear, a bit more neutral
VOICE = "en-US-AvaNeural"

# Slightly slower, calmer rate feels more composed/elegant than fast,
# energetic speech. Tune to taste.
RATE = "-2%"
PITCH = "+0Hz"


async def speak_async(text, stop_event=None):
    pygame.mixer.init()
    communicate = edge_tts.Communicate(
        text, voice=VOICE, rate=RATE, pitch=PITCH)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        temp_path = f.name
    await communicate.save(temp_path)
    pygame.mixer.music.load(temp_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        if stop_event is not None and stop_event.is_set():
            pygame.mixer.music.stop()
            break
        pygame.time.Clock().tick(10)
    pygame.mixer.music.stop()
    time.sleep(0.2)
    try:
        os.unlink(temp_path)
    except:
        pass


def speak(text, stop_event=None):
    print(f"Tobby: {text}")
    asyncio.run(speak_async(text, stop_event))


# ---------------------------------------------------------
# Manual test block — run "python voice.py" directly to hear
# how the current voice/rate/pitch settings sound.
# ---------------------------------------------------------
if __name__ == "__main__":
    print("Testing voice.py...\n")
    speak(
        "Good evening, Drissin Sir. Everything is exactly as you "
        "left it. How may I assist you this evening?"
    )
