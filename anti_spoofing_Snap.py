import cv2
import mediapipe as mp
import numpy as np
import time

from face_auth import check_face

# Initializing Mediapipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

# Video Capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Defined landmark indexes
NOSE_TIP = 1
FOREHEAD_TOP = 10  

# Liveness Challenges
CHALLENGES = ["Move head LEFT", "Move head RIGHT", "Raise eyebrows"]
TIME_LIMIT = 3  # Time limit in seconds for each challenge

# Variables for tracking
success_count = 0
best_image = None
best_sharpness = 0
challenge_index = 0

def is_front_facing(landmarks, frame_width):
    """Check if face is front-facing"""
    left_eye_x = landmarks[33].x * frame_width  
    right_eye_x = landmarks[263].x * frame_width  
    nose_x = landmarks[1].x * frame_width  
    eye_center = (left_eye_x + right_eye_x) / 2
    return abs(eye_center - nose_x) < (frame_width * 0.03)  

def calculate_sharpness(frame):
    """Calculate the sharpness of an image"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

def enhance_image(frame):
    """Apply sharpening and contrast enhancement"""
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.equalizeHist(l)
    enhanced = cv2.merge((l, a, b))
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    return cv2.filter2D(enhanced, -1, kernel)

while cap.isOpened() and challenge_index < len(CHALLENGES):
    current_challenge = CHALLENGES[challenge_index]
    start_time = time.time()
    
    nose_start_x = None
    forehead_start_y = None
    challenge_completed = False

    while time.time() - start_time < TIME_LIMIT:
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(frame_rgb)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                h, w, _ = frame.shape
                landmarks = [(int(l.x * w), int(l.y * h)) for l in face_landmarks.landmark]

                # Extracting Nose and Forehead positions
                nose_x = landmarks[NOSE_TIP][0]
                forehead_y = landmarks[FOREHEAD_TOP][1]

                if nose_start_x is None:
                    nose_start_x = nose_x  
                if forehead_start_y is None:
                    forehead_start_y = forehead_y  

                # Head movement detection
                face_width = abs(landmarks[127][0] - landmarks[356][0])  
                movement_threshold = face_width * 0.15

                if current_challenge == "Move head LEFT" and (nose_x - nose_start_x) > movement_threshold:
                    challenge_completed = True
                    break
                elif current_challenge == "Move head RIGHT" and (nose_x - nose_start_x) < -movement_threshold:
                    challenge_completed = True
                    break
                elif current_challenge == "Raise eyebrows" and (forehead_start_y - forehead_y) > 5:
                    challenge_completed = True
                    break

                # Capturing the best image while liveness is active
                if is_front_facing(face_landmarks.landmark, w):
                    sharpness = calculate_sharpness(frame)
                    if sharpness > best_sharpness:
                        best_sharpness = sharpness
                        best_image = frame.copy()
                        print(f"📸 Updated best image (Sharpness: {sharpness:.2f})")

        cv2.putText(frame, f"🔹 Perform: {current_challenge}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        cv2.imshow("Liveness Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            cap.release()
            cv2.destroyAllWindows()
            exit()

    if not challenge_completed: 
        print("⛔ Liveness failed due to timeout.")
        cv2.putText(frame, "⛔ Liveness failed!", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow("Liveness Detection", frame)
        cv2.waitKey(3000)  # Wait 3 seconds before showing failure message
        best_image = None  # Discards any saved image
        break
    
    print(f"✅ Challenge {success_count+1}/3 Passed!")
    success_count += 1
    challenge_index += 1

cap.release()
cv2.destroyAllWindows()

# Saved the best image after all challenges
if success_count == len(CHALLENGES) and best_image is not None:
    best_image = enhance_image(best_image)
    # cv2.imwrite("best_quality_face.png", best_image)
    print(f"✅ Liveness completed! Best quality face saved (Sharpness: {best_sharpness:.2f})")
    check_face(best_image)
    
else:
    print("⚠ Liveness verification failed. No image saved.")
