import cv2
import numpy as np
from ultralytics import YOLO
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array

# Load YOLOv8 model for person detection
yolo_model = YOLO("yolov8n.pt")  # Ensure this model exists

# Load trained gender classification model
gender_model = load_model(r"C:\Users\Dell\OneDrive\Desktop\safesight models\gender.h5")  # Update path

# Define labels for gender classification
labels = ["Man", "Woman"]

# Image path
image_path = r"C:\Users\Dell\OneDrive\Desktop\safesight models\women.jpeg"  # Change this to your image path

# Load the image
image = cv2.imread(image_path)
if image is None:
    print("Error: Cannot load image. Check the file path.")
    exit()

# Run YOLO detection
results = yolo_model(image)[0]

for result in results.boxes:
    x1, y1, x2, y2 = map(int, result.xyxy[0])  # Get bounding box coordinates
    class_id = int(result.cls[0])  # Class ID

    # Ensure detection is for 'person' (class ID 0)
    if class_id == 0:
        # Crop the detected person
        person_crop = image[y1:y2, x1:x2]

        # Preprocess for gender classification
        try:
            person_crop_resized = cv2.resize(person_crop, (100, 100))  # Resize
            person_crop_array = img_to_array(person_crop_resized) / 255.0  # Normalize
            person_crop_array = np.expand_dims(person_crop_array, axis=0)  # Expand dims for model

            # Predict gender
            conf = gender_model.predict(person_crop_array)[0]
            gender_label = labels[np.argmax(conf)]  # "Man" or "Woman"

            # Draw bounding box and label
            color = (255, 0, 0) if gender_label == "Man" else (0, 0, 255)  # Blue for Man, Red for Woman
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            cv2.putText(image, gender_label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        except Exception as e:
            print(f"Error processing gender classification: {e}")

# Display result (without saving)
cv2.imshow("YOLOv8 Detection with Gender", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
