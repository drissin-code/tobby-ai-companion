import speech_recognition as sr
import threading

recognizer = sr.Recognizer()
recognizer.pause_threshold = 0.6
# Raised energy_threshold from 300 -> 500 so it's less sensitive to
# faint background noise, reducing false Whisper hallucinations.
recognizer.energy_threshold = 500
recognizer.dynamic_energy_threshold = True

TRIGGER_PHRASES = ["hey listen", "listen wait",
                   "wait listen", "hey wait", "hold on", "hey tobby wait"]

# Common Whisper hallucination phrases on silence/noise — if the
# recognized text matches one of these closely, we ignore it instead
# of treating it as real speech.
HALLUCINATION_PATTERNS = [
    "thanks for watching", "thank you for watching", "subscribe",
    "bye bye", "you", ".", "", "the end", "thank you",
]


def is_likely_hallucination(text: str) -> bool:
    """Filters out common Whisper hallucinations on silence/noise."""
    cleaned = text.lower().strip().strip(".")
    if len(cleaned) < 3:
        return True
    if cleaned in HALLUCINATION_PATTERNS:
        return True
    return False


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

                # Skip likely hallucinated/junk text instead of acting on it
                if is_likely_hallucination(text_lower):
                    continue

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
