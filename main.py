import cv2
import numpy as np
import pygame
from datetime import datetime
import threading
import pyttsx3
import time
from scipy.spatial import distance

# === Audio (Beep) Setup ===
pygame.mixer.init()
try:
    DETECTION_SOUND = pygame.mixer.Sound("beep.wav")
except:
    print("⚠️ You must place a 'beep.wav' sound file in this folder.")

# === TTS Engine Setup ===
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)

# === Haar Cascade Setup ===
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# === Webcam Init ===
cap = cv2.VideoCapture(0)  # 0 = default webcam

# === Detection Control Variables ===
last_detection_time = 0
BEEP_COOLDOWN = 3  # seconds between alerts
previous_centroids = []
DISTANCE_THRESHOLD = 50
face_id_counter = 0

# === Beep + Voice Alert Function ===
def play_beep_and_tts():
    global last_detection_time
    now = time.time()
    if now - last_detection_time >= BEEP_COOLDOWN:
        last_detection_time = now
        try:
            DETECTION_SOUND.play()
        except:
            pass
        try:
            current_time = datetime.now().strftime('%H:%M:%S')
            tts_engine.say(f"Face detected at {current_time}")
            tts_engine.runAndWait()
        except:
            pass

# === Check for New Face Using Distance ===
def is_new_face(cx, cy):
    for (px, py) in previous_centroids:
        if distance.euclidean((cx, cy), (px, py)) < DISTANCE_THRESHOLD:
            return False
    previous_centroids.append((cx, cy))
    return True

# === Main Loop ===
while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to grab frame")
        break

    frame = cv2.resize(frame, (640, 480))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.1, 5)
    for (x, y, w, h) in faces:
        cx, cy = x + w // 2, y + h // 2
        face_id_counter += 1
        label = f"ID {face_id_counter}"

        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.circle(frame, (cx, cy), 4, (0, 255, 255), -1)
        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

        if is_new_face(cx, cy):
            threading.Thread(target=play_beep_and_tts, daemon=True).start()

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cv2.putText(frame, f"Time: {timestamp}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    cv2.putText(frame, f"Faces: {len(faces)}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)

    cv2.imshow("🎥 Webcam Face Detector", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()