import pyaudio
import numpy as np
import asyncio
import edge_tts
import pygame
import tempfile
import os
import time

CHUNK = 2048
RATE = 44100
THRESHOLD = 3000
WHISTLE_LOW = 1000
WHISTLE_HIGH = 4000
PURITY_THRESHOLD = 0.3
CONSECUTIVE_FRAMES_NEEDED = 3
BAND_WIDTH_HZ = 150

pygame.mixer.init()


async def speak_async(text):
    pygame.mixer.init()
    communicate = edge_tts.Communicate(text, voice="en-US-GuyNeural")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        temp_path = f.name
    await communicate.save(temp_path)
    pygame.mixer.music.load(temp_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.music.stop()
    time.sleep(0.3)
    try:
        os.unlink(temp_path)
    except:
        pass


def speak(text):
    asyncio.run(speak_async(text))


def detect_whistle():
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=RATE,
        input=True,
        input_device_index=1,
        frames_per_buffer=CHUNK
    )
    print("Tobby is sleeping... whistle to wake me Sir!")

    consecutive_hits = 0

    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        samples = np.frombuffer(data, dtype=np.int16).astype(np.float32)

        windowed = samples * np.hanning(len(samples))

        volume = np.max(np.abs(samples))

        if volume < THRESHOLD:
            consecutive_hits = 0
            continue

        fft = np.fft.rfft(windowed)
        freqs = np.fft.rfftfreq(len(windowed), 1.0/RATE)
        magnitude = np.abs(fft)

        peak_index = np.argmax(magnitude)
        peak_freq = freqs[peak_index]

        band_mask = np.abs(freqs - peak_freq) <= BAND_WIDTH_HZ
        band_energy = np.sum(magnitude[band_mask])
        total_energy = np.sum(magnitude) + 1e-6

        purity = band_energy / total_energy

        in_range = WHISTLE_LOW <= peak_freq <= WHISTLE_HIGH
        is_pure = purity >= PURITY_THRESHOLD

        if in_range and is_pure:
            consecutive_hits += 1
        else:
            consecutive_hits = 0

        if consecutive_hits >= CONSECUTIVE_FRAMES_NEEDED:
            print("Whistle detected! Waking up...")
            stream.stop_stream()
            stream.close()
            audio.terminate()
            time.sleep(1)
            return True


if __name__ == "__main__":
    detect_whistle()
