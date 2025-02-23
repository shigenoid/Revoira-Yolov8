import cv2
import numpy as np
import urllib.request
from ultralytics import YOLO

# Load the trained YOLOv8 model
model = YOLO("runs/detect/bottle-train/weights/best.pt")  # Path to your trained YOLOv8 model

# ESP32-CAM URL
url = "http://192.168.18.81/cam-hi.jpg"

while True:
    # Fetch image from ESP32-CAM
    try:
        img_resp = urllib.request.urlopen(url)
        img_array = np.array(bytearray(img_resp.read()), dtype=np.uint8)
        frame = cv2.imdecode(img_array, -1)
    except Exception as e:
        print(f"Failed to fetch frame: {e}. Retrying...")
        continue

    # Run YOLOv8 inference
    results = model(frame)  # Perform inference on the frame

    # Visualize the results
    annotated_frame = results[0].plot()  # Get the annotated frame

    # Display the annotated frame
    cv2.imshow("YOLOv8 Detection", annotated_frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()