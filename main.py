import time
import threading
from wake import detect_whistle
from listener import listen
from voice import speak
from brain import TobbyBrain
from weather import get_weather
from interrupt import monitor_for_interrupt


def speak_interruptible(text):
    stop_event = threading.Event()
    cancel_event = threading.Event()

    monitor_thread = threading.Thread(
        target=monitor_for_interrupt, args=(
            stop_event, cancel_event), daemon=True
    )
    monitor_thread.start()

    speak(text, stop_event=stop_event)

    cancel_event.set()
    monitor_thread.join(timeout=1)

    return stop_event.is_set()


def main():
    tobby = TobbyBrain()
    print("Tobby is starting up...")

    while True:
        detect_whistle()
        speak("Yes Sir?")

        while True:
            user_input = listen()

            if not user_input:
                speak("Sorry, I didn't catch that.")
                continue

            if "sleep" in user_input.lower():
                speak("Going back to sleep. Whistle when you need me.")
                time.sleep(1)
                break

            if "weather" in user_input.lower():
                weather_report = get_weather()
                interrupted = speak_interruptible(weather_report)
                if not interrupted:
                    time.sleep(1)
                continue

            reply = tobby.get_response(user_input)
            interrupted = speak_interruptible(reply)

            if interrupted:
                continue  # skip cooldown, go straight back to listening
            else:
                time.sleep(1)


if __name__ == "__main__":
    main()
