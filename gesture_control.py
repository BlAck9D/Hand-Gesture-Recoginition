import cv2
import mediapipe as mp
import pyautogui
import subprocess
import os
import time
import sys
import pygetwindow as gw
import math

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Webcam
cap = cv2.VideoCapture(0)

# Gesture tracking
last_gesture = None
gesture_cooldown = 1.5  # seconds
last_gesture_time = time.time()


def count_fingers(hand_landmarks):
    fingers = []
    tip_ids = [4, 8, 12, 16, 20]

    # Thumb
    if hand_landmarks.landmark[tip_ids[0]].x < hand_landmarks.landmark[tip_ids[0] - 1].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other fingers
    for i in range(1, 5):
        if hand_landmarks.landmark[tip_ids[i]].y < hand_landmarks.landmark[tip_ids[i] - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers


def detect_gesture(fingers, hand_landmarks):
    total_fingers = sum(fingers)

    # 👍 Thumbs Up → End Gesture Recognition
    if fingers == [1, 0, 0, 0, 0]:
        return "thumbs_up"

    # ✌️ Two Fingers → Play/Pause Media
    if fingers == [0, 1, 1, 0, 0]:
        return "two_fingers"

    # ✊ Fist → Close Window
    if total_fingers == 0:
        return "fist"

    # 🤟 Three Fingers → Switch Tabs
    if fingers == [0, 1, 1, 1, 0]:
        return "three_fingers"

    # 🖖 Four Fingers → Minimize Window
    if fingers == [0, 1, 1, 1, 1]:
        return "four_fingers"

    # 🖐 Five Fingers → Maximize Window
    if total_fingers == 5:
        return "five_fingers"

    # 🤘 Rock Sign → Mute/Unmute Volume
    if fingers == [0, 1, 0, 0, 1]:
        return "rock"

    # 🤞 Screenshot
    if fingers == [0, 1, 1, 0, 0]:
        return "screenshot"

    # 👉 Open Notepad → Index Finger Only
    if fingers == [0, 1, 0, 0, 0]:
        return "notepad"

    # 👌 OK Sign → Open File Explorer
    thumb_tip = hand_landmarks.landmark[4]
    index_tip = hand_landmarks.landmark[8]
    distance = math.hypot(
        index_tip.x - thumb_tip.x,
        index_tip.y - thumb_tip.y
    )
    if distance < 0.05:
        return "ok"

    return None


def perform_action(gesture):
    if gesture == "thumbs_up":
        print("Ending Gesture Recognition...")
        cap.release()
        cv2.destroyAllWindows()
        sys.exit()

    elif gesture == "two_fingers":
        pyautogui.press("playpause")

    elif gesture == "fist":
        pyautogui.hotkey("alt", "f4")

    elif gesture == "three_fingers":
        pyautogui.hotkey("ctrl", "tab")

    elif gesture == "four_fingers":
        pyautogui.hotkey("win", "down")

    elif gesture == "five_fingers":
        pyautogui.hotkey("win", "up")

    elif gesture == "rock":
        pyautogui.press("volumemute")

    elif gesture == "screenshot":
        screenshot = pyautogui.screenshot()
        screenshot.save(os.path.join(os.path.expanduser("~/Desktop"), "screenshot.png"))

    elif gesture == "notepad":
        subprocess.Popen(["notepad.exe"])

    elif gesture == "ok":
        subprocess.Popen("explorer")


# Main Loop
with mp_hands.Hands(min_detection_confidence=0.7,
                    min_tracking_confidence=0.7,
                    max_num_hands=1) as hands:

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue

        # Flip frame
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process
        results = hands.process(rgb_frame)

        # Detect hands
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                fingers = count_fingers(hand_landmarks)
                gesture = detect_gesture(fingers, hand_landmarks)

                if gesture and (gesture != last_gesture or (time.time() - last_gesture_time) > gesture_cooldown):
                    perform_action(gesture)
                    last_gesture = gesture
                    last_gesture_time = time.time()

                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        cv2.imshow("Hand Gesture Recognition", frame)

        if cv2.waitKey(10) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
