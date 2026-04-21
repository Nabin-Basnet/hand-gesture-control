import cv2
import mediapipe as mp
import pyautogui
import time

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# prevent key spam / flicker control
last_action = ""
cooldown_time = 0.2
last_time = 0

# NEW: jump/extra action cooldown
extra_cooldown = 0.6
last_extra_time = 0

def fingers_up(hand_landmarks):
    tips = [8, 12, 16, 20]
    fingers = []

    # Thumb
    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other fingers
    for tip in tips:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers


while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    result = hands.process(rgb)

    current_time = time.time()

    action = "NONE"

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

            fingers = fingers_up(handLms)

            # ✊ FIST
            if fingers == [0, 0, 0, 0, 0]:
                action = "BRAKE"

            # ✋ OPEN HAND
            elif fingers == [1, 1, 1, 1, 1]:
                action = "MOVE"

            # ☝️ ONE FINGER (UP)
            elif fingers == [0, 1, 0, 0, 0]:
                action = "UP"

            # ✌️ TWO FINGERS (DOWN)
            elif fingers == [0, 1, 1, 0, 0]:
                action = "DOWN"

    # 🧠 Apply actions with stability (original logic unchanged)
    if current_time - last_time > cooldown_time:

        if action != last_action:

            if action == "BRAKE":
                pyautogui.keyDown("left")
                pyautogui.keyUp("right")

            elif action == "MOVE":
                pyautogui.keyDown("right")
                pyautogui.keyUp("left")

            elif action == "NONE":
                pyautogui.keyUp("left")
                pyautogui.keyUp("right")

            # NEW: UP (single press)
            elif action == "UP":
                if current_time - last_extra_time > extra_cooldown:
                    pyautogui.press("up")
                    last_extra_time = current_time

            # NEW: DOWN (single press)
            elif action == "DOWN":
                if current_time - last_extra_time > extra_cooldown:
                    pyautogui.press("down")
                    last_extra_time = current_time

            last_action = action
            last_time = current_time

    # UI text
    cv2.putText(img, f"Action: {action}", (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    # NEW: instruction display (for demo)
    cv2.putText(img, "✋ Move  ✊ Brake  ☝️ Up  ✌️ Down", (50, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow("Gesture Game Control", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pyautogui.keyUp("left")
pyautogui.keyUp("right")