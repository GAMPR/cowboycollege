import cv2
import time

def preprocess_frame(frame, transform):
    # Convert the frame to RGB and apply transformations
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return transform(frame_rgb)

def draw_shooting_effect(frame, player):
    # Placeholder effect (can be enhanced with animations)
    if player == "Player 1":
        x, y = frame.shape[1] - 100, 100
    else:
        x, y = 100, 100
    cv2.circle(frame, (x, y), 50, (0, 0, 255), -1)

