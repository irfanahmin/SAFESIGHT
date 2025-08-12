import cv2
import time
import numpy as np
import mediapipe as mp
import requests
import webbrowser
import time
# Flask API URL
FLASK_SERVER_URL = "http://127.0.0.1:5000/send_alert"

# Initialize MediaPipe Hand Tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils

# Gesture Tracking Variables
gesture_detected = False
last_gesture_time = 0

def send_sos_alert():
    """Trigger SOS alert by opening the webpage that runs JavaScript to send location."""
    try:
        print("🚨 Opening SOS alert page in the browser...")
        
        # Open the Flask front-end webpage in the default browser
        webbrowser.open("http://127.0.0.1:5000", new=2)  # new=2 opens in a new tab

        # Give some time for the JavaScript to execute
        time.sleep(5)  # Wait 5 seconds (adjust if needed)
        
        print("✅ SOS alert triggered successfully!")
    except Exception as e:
        print("❌ Error triggering SOS:", str(e))

def detect_open_close_fingers(landmarks):
    """
    Detect if the user opens and closes their fingers.
    If detected, send an SOS alert.
    """
    global gesture_detected, last_gesture_time

    if landmarks:
        # Extract y-coordinates of fingers
        thumb_tip = landmarks[4].y
        index_tip = landmarks[8].y
        middle_tip = landmarks[12].y
        ring_tip = landmarks[16].y
        pinky_tip = landmarks[20].y

        # Extract base (MCP) y-coordinates
        index_base = landmarks[5].y
        middle_base = landmarks[9].y
        ring_base = landmarks[13].y
        pinky_base = landmarks[17].y

        # Check if fingers are *open* (above the base)
        fingers_open = (
            index_tip < index_base and
            middle_tip < middle_base and
            ring_tip < ring_base and
            pinky_tip < pinky_base
        )

        # Check if fingers are *closed* (below the base)
        fingers_closed = (
            index_tip > index_base and
            middle_tip > middle_base and
            ring_tip > ring_base and
            pinky_tip > pinky_base
        )

        # Enforce 5-second cooldown to prevent multiple alerts
        current_time = time.time()
        if current_time - last_gesture_time < 5:
            return  # Ignore repeated alerts

        if fingers_open:
            gesture_detected = True  # Mark that the hand was opened

        if fingers_closed and gesture_detected:
            send_sos_alert()  # Call frontend function to get correct location
            last_gesture_time = current_time  # Update last alert time
            gesture_detected = False  # Reset for next detection

def main():
    """Main function to capture video and detect gestures."""
    cap = cv2.VideoCapture(0)  # Open camera

    if not cap.isOpened():
        print("❌ Camera failed to open!")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to capture frame!")
            break

        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process frame with MediaPipe Hands
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                detect_open_close_fingers(hand_landmarks.landmark)

        cv2.imshow("Gesture Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):  # Press 'q' to exit
            break

    cap.release()
    cv2.destroyAllWindows()

if _name_ == "_main_":
    main()