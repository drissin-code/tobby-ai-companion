import speech_recognition as sr
import torch

recognizer = sr.Recognizer()
recognizer.pause_threshold = 1.0
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"CUDA available: {torch.cuda.is_available()} (device: {DEVICE})")


def listen():
    with sr.Microphone() as source:
        print("Listening Sir...")
        recognizer.adjust_for_ambient_noise(source, duration=0.8)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=20)
            text = recognizer.recognize_whisper(
                audio,
                model="medium",
                language="english",
                initial_prompt="Tobby, AMD, NVIDIA, Gemini, AI, ML, Drissin, whistle, Bharathiar, Coimbatore, Palakkad"
            )
            print(f"You said: {text}")
            return text
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            print("Whisper recognition failed")
            return None
