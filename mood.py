import cv2
from deepface import DeepFace
import base64
import numpy as np

def detect_mood_from_frame(base64_str):
    try:
        # Decode base64 image
        encoded_data = base64_str.split(',')[1]
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Analyze using DeepFace
        results = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
        dominant_emotion = results[0]['dominant_emotion']
        return dominant_emotion
    except Exception as e:
        print(f"Mood Error: {e}")
        return "neutral"