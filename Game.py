# Import libraries
import cv2
import torch
import torchvision.transforms as transforms
from gesture_model import HandGestureModel  # Custom PyTorch model
from utils import preprocess_frame, draw_shooting_effect

# Load the trained PyTorch model
model = HandGestureModel()
model.load_state_dict(torch.load('model/hand_gesture_model.pth'))
model.eval()

# Define preprocessing transformation (resize and normalize frame)
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

# Initialize OpenCV video capture
cap = cv2.VideoCapture(0)

# Game variables
player_times = {"Player 1": None, "Player 2": None}
shoot_effect_timer = {"Player 1": 0, "Player 2": 0}
countdown_done = False
countdown_start_time = time.time()

def detect_gesture(frame):
    # Preprocess the frame
    input_tensor = preprocess_frame(frame, transform)
    
    # Pass the preprocessed frame to the model
    with torch.no_grad():
        output = model(input_tensor.unsqueeze(0))  # Add batch dimension
    
    # Interpret the model output
    predicted_gesture = output.argmax(1).item()
    
    # Return the detected gesture (e.g., 0 = no motion, 1 = "shoot")
    return predicted_gesture

def get_player_id(hand_position, frame_width):
    # Determine which player based on x-coordinate of detected hand
    if hand_position < frame_width / 2:
        return "Player 2"
    else:
        return "Player 1"

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)  # Mirror the image
    frame_height, frame_width, _ = frame.shape

    # Countdown phase
    if not countdown_done:
        elapsed_time = time.time() - countdown_start_time
        countdown_done = (elapsed_time >= 3)  # Start game after 3 seconds
        cv2.putText(frame, f"{int(3 - elapsed_time)}", (frame_width // 2 - 50, frame_height // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 5)
        cv2.imshow("Duel Game", frame)
        cv2.waitKey(1)
        continue  # Skip the rest of the loop until countdown is done

    # Detect gesture
    predicted_gesture = detect_gesture(frame)

    if predicted_gesture == 1:  # Gesture recognized as "shoot"
        # Simulate hand position detection (use a model output in the actual game)
        hand_position = frame_width // 2  # Placeholder, replace with actual detection
        player_id = get_player_id(hand_position, frame_width)

        if player_times[player_id] is None:  # Check if player has already shot
            reaction_time = time.time() - countdown_start_time
            player_times[player_id] = reaction_time
            print(f"{player_id} shot in {reaction_time:.2f} seconds!")
            shoot_effect_timer[player_id] = time.time()  # Start effect timer

            # Determine winner if both players have shot
            if player_times["Player 1"] and player_times["Player 2"]:
                winner = "Player 1" if player_times["Player 1"] < player_times["Player 2"] else "Player 2"
                print(f"{winner} wins!")
                break

    # Draw the shooting effect
    for player, timer in shoot_effect_timer.items():
        if timer > 0 and time.time() - timer < 0.5:  # Show effect for 0.5 seconds
            draw_shooting_effect(frame, player)

    # Display player labels
    cv2.putText(frame, "Player 1 (Right)", (frame_width - 300, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, "Player 2 (Left)", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show the game frame
    cv2.imshow("Duel Game", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

