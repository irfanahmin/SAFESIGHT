import cv2
import torch
from ultralytics import YOLO

# Load YOLOv8 model (Ensure you have 'yolov8n.pt' in your directory)
model = YOLO("yolov8n.pt")

# Input video path (Change the filename accordingly)
input_video_path = r"C:\Users\Dell\OneDrive\Desktop\safesight models\istockphoto-1500551874-640_adpp_is (1).mp4"
output_video_path = r"C:\Users\Dell\OneDrive\Desktop\safesight models\processed_video.mp4"

# Open video file
cap = cv2.VideoCapture(input_video_path)
if not cap.isOpened():
    print("Error: Cannot open video file")
    exit()

# Get video properties
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Video codec for output

# Create VideoWriter object
out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

# Process each frame
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break  # End of video

    # Run YOLO detection
    results = model(frame)[0]

    person_count = 0  # Reset count for each frame

    # Draw bounding boxes
    for result in results.boxes:
        x1, y1, x2, y2 = map(int, result.xyxy[0])  # Get bounding box coordinates
        class_id = int(result.cls[0])  # Class ID

        # Ensure detection is for 'person' (class ID 0)
        if class_id == 0:
            person_count += 1  # Increase person count

            # Draw bounding box and label
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green box for person
            label = f"Person {person_count}"  # Unique label
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Display total person count on screen
    cv2.putText(frame, f"Total Persons: {person_count}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Write processed frame
    out.write(frame)

    # Display frame (Optional)
    cv2.imshow("YOLOv8 Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
out.release()
cv2.destroyAllWindows()

print(f"Processed video saved at: {output_video_path}")
