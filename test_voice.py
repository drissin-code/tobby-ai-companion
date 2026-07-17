import asyncio
import edge_tts
import pygame
import tempfile
import os
import time

pygame.mixer.init()


async def test():
    communicate = edge_tts.Communicate(
        "At your service Drissin Sir! Tobby is online and ready.",
        voice="en-US-GuyNeural"
    )
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        temp_path = f.name
    await communicate.save(temp_path)
    pygame.mixer.music.load(temp_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.music.stop()
    pygame.mixer.quit()
    time.sleep(0.5)
    os.unlink(temp_path)

asyncio.run(test())
