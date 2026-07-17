import os
import edge_tts
import asyncio
import pygame
import tempfile
import time
from dotenv import load_dotenv

load_dotenv()


async def speak_async(text, stop_event=None):
    pygame.mixer.init()
    communicate = edge_tts.Communicate(
        text, voice="en-US-AndrewNeural", rate="+8%")
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
