import cv2
import os

# Safe and correct path format (use raw string or double backslashes)
video_path = r'data\movie.m4v'

# Output directory for frames
output_dir = 'output_frames'
os.makedirs(output_dir, exist_ok=True)

# Open video file
cap = cv2.VideoCapture(video_path)

# Check if video opened successfully
if not cap.isOpened():
    print("❌ Failed to open video. Please check the path.")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)
frame_interval = int(fps)  # extract 1 frame per second

frame_count = 0
saved_count = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    if frame_count % frame_interval == 0:
        filename = os.path.join(output_dir, f"frame_{saved_count:04d}.png")
        cv2.imwrite(filename, frame)
        saved_count += 1

    frame_count += 1

cap.release()
print(f"✅ Extracted {saved_count} frames to '{output_dir}'")
