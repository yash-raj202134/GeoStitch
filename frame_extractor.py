import cv2  # image and video processing
import os   # interact with the file system

# Path to the video file
video_path = r'data\movie.m4v'

# Directory where extracted frames will be saved
output_dir = 'output_frames'
os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist

# Open the video file
cap = cv2.VideoCapture(video_path)

# Check if the video was successfully opened
if not cap.isOpened():
    print("❌ Failed to open video. Please check the path.")
    exit()

# Get the video's frames per second (fps) to control how often we extract frames
fps = cap.get(cv2.CAP_PROP_FPS)
frame_interval = int(fps)  # Save 1 frame per second

frame_count = 0      # Total number of frames processed
saved_count = 0      # Total number of frames saved

# Loop through the video frame by frame
while cap.isOpened():
    ret, frame = cap.read()  # Read one frame
    if not ret:
        break  # Exit the loop if no frame is returned (end of video)

    # Save one frame every second based on fps
    if frame_count % frame_interval == 0:
        # Construct the output filename (e.g., frame_0001.png)
        filename = os.path.join(output_dir, f"frame_{saved_count:04d}.png")
        cv2.imwrite(filename, frame)  # Save the frame as an image
        saved_count += 1  # Increment saved frame count

    frame_count += 1  # Move to the next frame

# Release the video capture object to free resources
cap.release()
print(f"✅ Extracted {saved_count} frames to '{output_dir}'")
