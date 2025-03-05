import cv2
import mediapipe as mp
import time
import math
import socket
import struct
import random

# Set up socket connection to Unity
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('127.0.0.1', 9999))
server_socket.listen(1)
print("Waiting for Unity connection...")
conn, addr = server_socket.accept()
print(f"Connected to Unity at {addr}")

# Set a short timeout for non-blocking socket reads
conn.settimeout(0.01)

# Initialize Mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# OpenCV capture from webcam
cap = cv2.VideoCapture(0)

# Encode frame for streaming
def encode_frame(frame):
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    result, encoded_img = cv2.imencode('.jpg', frame, encode_param)
    return encoded_img

# Distance calculator
def calculate_distance(point1, point2):
    return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

# Detect shooting gesture based on thumb and index finger
def detect_shoot(hand_landmarks, frame_width):
    thumb_tip = hand_landmarks.landmark[4]
    index_tip = hand_landmarks.landmark[8]
    distance = calculate_distance(thumb_tip, index_tip) * frame_width
    return distance > 50  # Adjust as needed

# Determine which player based on screen position
def get_player_id(hand_landmarks, frame_width):
    wrist_x = hand_landmarks.landmark[0].x * frame_width
    return "Player 2" if wrist_x < frame_width / 2 else "Player 1"

# Countdown display
def display_countdown(frame, start_time, countdown_duration):  
    elapsed_time = time.time() - start_time
    count = max(0, int(countdown_duration - elapsed_time))
    #text = f"{count}" if count > 0 else "DRAW!"
    #color = (0, 0, 255) if count == 0 else (255, 255, 255)
    #cv2.putText(frame, text, (frame.shape[1] // 2 - 100, frame.shape[0] // 2), 
     #           cv2.FONT_HERSHEY_SIMPLEX, 5, color, 10)
    return count == 0  # Return True if countdown is complete

# Function to draw the explosive shooting effect
def draw_shooting_effect(frame, x, y, start_time):
    elapsed = time.time() - start_time
    max_duration = 0.5  # Effect lasts 0.5 seconds
    progress = min(1.0, elapsed / max_duration)
    explosion_size = int(20 + 80 * progress)
    color = (0, int(255 * (1 - progress)), int(255 * progress))  # Yellow to Red

    for i in range(3):
        cv2.circle(frame, (x, y), explosion_size - (i * 10), color, 2)
    cv2.circle(frame, (x, y), int(explosion_size / 4), (0, 255, 255), -1)  # Inner core

# Main game logic

def reset_game(msg):
    global player_times, shoot_effect_timer, countdown_start_time, countdown_done, game_start_time, countdown_duration, game_in_progress, winner_msg
    player_times = {"Player 1": None, "Player 2": None}
    shoot_effect_timer = {"Player 1": 0, "Player 2": 0}
    countdown_start_time = time.time()
    countdown_done = False
    winner_msg = ""
    game_start_time = None
    game_in_progress = True
    
    #random.randint(5, 15)  # Generate new random countdown
    if len(msg) == 8 :
        countdown_duration = int(msg[-1])
    elif len(msg) == 9 :
        countdown_duration = int(msg[-2] + msg[-1])
    else :
        countdown_duration = int(msg)
    countdown_duration += 1 # Accounting for desync with Unity

    print("Game reset. Starting new countdown...")

reset_game('5')  # Initialize the game for the first round


game_in_progress = False # At first, the game is not on. It's at the start menu

while True:
    #try:
        while True:
            print(game_in_progress)
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            frame_height, frame_width, _ = frame.shape

            # Check for messages from Unity
            try:
                message = conn.recv(1024).decode('utf-8')
                if message:
                    print(f"Received message from Unity: {message.strip()}")
                    
                    print(message[:-2].strip().lower())
                    if message.strip().lower() == "pause":
                        print("Pausing video capture.")
                        break  # Exiting the game (can be resumed via restart)
                    
                    elif (message[:-2].strip().lower() == "restart") or (message[:-2].strip().lower() == "restart1"):
                        print("Restart signal received from Unity.")
                        reset_game(message.strip().lower())  # Reset game state and start a new round

            except socket.timeout:
                pass  # No message received, continue game loop

            # if winner_msg != "":
            cv2.putText(frame, winner_msg, (50, frame_height // 2), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

            # if winner_msg == "": 
            #     cv2.rectangle(frame, (40, frame_height // 2 - 50), (600, frame_height // 2 + 50), (0, 0, 0), -1)
        
            if game_in_progress:
                # Countdown phase
                if not countdown_done:
                    countdown_done = display_countdown(frame, countdown_start_time, countdown_duration)
                    if countdown_done:
                        print("DRAW!")
                        game_start_time = time.time()

                # Game phase
                if countdown_done:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    result = hands.process(rgb_frame)

                    if result.multi_hand_landmarks:
                        for hand_landmarks in result.multi_hand_landmarks:
                            player_id = get_player_id(hand_landmarks, frame_width)
                            index_tip = hand_landmarks.landmark[8]  # Index finger tip

                            # Check if player has "shot"
                            if detect_shoot(hand_landmarks, frame_width) and player_times[player_id] is None:
                                reaction_time = time.time() - game_start_time
                                player_times[player_id] = reaction_time
                                print(f"{player_id} shot in {reaction_time:.2f} seconds!")
                                shoot_effect_timer[player_id] = time.time()

                                # Determine the winner if both players have shot
                                if player_times["Player 1"] and player_times["Player 2"]:
                                    winner = "Player 1" if player_times["Player 1"] < player_times["Player 2"] else "Player 2"
                                    print(f"{winner} wins!")

                                    winner_msg = f"{winner} wins!"

                                    game_in_progress = False
                            

                            # Draw the shooting effect
                            if shoot_effect_timer[player_id] > 0 and time.time() - shoot_effect_timer[player_id] < 0.5:
                                x, y = int(index_tip.x * frame_width), int(index_tip.y * frame_height)
                                draw_shooting_effect(frame, x, y, shoot_effect_timer[player_id])

                            # Draw landmarks for visualization
                            #mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Display player labels
            # cv2.putText(frame, "Player 1 (Right)", (frame_width - 300, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            # cv2.putText(frame, "Player 2 (Left)", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Encode the frame and send to Unity
            encoded_frame = encode_frame(frame)
            data = encoded_frame.tobytes()
            frame_size = len(data)
            try:
                conn.sendall(struct.pack(">L", frame_size))
                conn.sendall(data)
            except Exception as e:
                print(f"Error during frame transmission: {e}")
                game_in_progress = False  # Optionally reset game state or handle cleanup here

