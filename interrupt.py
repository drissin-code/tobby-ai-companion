import speech_recognition as sr
import threading

recognizer = sr.Recognizer()
recognizer.pause_threshold = 0.6
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True

TRIGGER_PHRASES = ["hey listen", "listen wait",
                   "wait listen", "hey wait", "hold on", "hey tobby wait"]


def monitor_for_interrupt(stop_event, cancel_event):
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)

        while not cancel_event.is_set():
            try:
                audio = recognizer.listen(
                    source, timeout=1, phrase_time_limit=3)
                text = recognizer.recognize_whisper(
                    audio, model="small", language="english")
                text_lower = text.lower().strip()

                print(f"[interrupt check]: {text_lower}")

                if any(phrase in text_lower for phrase in TRIGGER_PHRASES):
                    stop_event.set()
                    break

            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except Exception:
                continue
