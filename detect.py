import cv2
import numpy as np
import time
from ultralytics import YOLO

# Load YOLO model
model = YOLO("runs/detect/bottle-1504/weights/best.pt") 

# Initialize webcam
cap = cv2.VideoCapture(0)  # 0 for default webcam

# Detection interval
last_detection_time = time.time()
detection_interval = 0.1  # More frequent detection (adjust as needed)

while True:
    current_time = time.time()
    
    # Read frame from webcam
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame")
        break

    # Run detection at specified interval
    if current_time - last_detection_time >= detection_interval:
        # Run YOLOv8 inference
        results = model(frame)  

        # Get detected classes
        detected_classes = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                class_id = int(box.cls)
                class_name = model.names[class_id]
                detected_classes.append(class_name)
                print(f"Detected: {class_name}")

        # Visualize results
        annotated_frame = results[0].plot() 
        last_detection_time = current_time

    # Display the frame
    cv2.imshow("Revoira", annotated_frame if 'annotated_frame' in locals() else frame)

    # Exit on 'q' press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()