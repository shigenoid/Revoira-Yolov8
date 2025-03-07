import cv2
import numpy as np
import urllib.request
import serial
import time
from ultralytics import YOLO

model = YOLO("runs/detect/bottle-train/weights/best.pt") 

# ESP32-CAM URL
url = "http://192.168.8.78/cam-hi.jpg"

# ESP32 Serial Communication
ser = serial.Serial('COM4', 115200, timeout=1) 
time.sleep(2)  

# ESP32 Commands
def send_command(class_name):
    if class_name == "glass-bottle":
        ser.write(b'GLASS\n')  
    elif class_name == "can-bottle":
        ser.write(b'CAN\n') 
    elif class_name == "plastic-bottle":
        ser.write(b'PLASTIC\n') 
    elif class_name == "tetrapak":
        ser.write(b'TETRAPAK\n') 
    else:
        ser.write(b'NONE\n')  

# Detection Intervals
last_detection_time = time.time()  
detection_interval = 1 

# Command Intervals
last_command_time = time.time() 
command_interval = 5 

last_detected_class = None

while True:
    current_time = time.time()

    # Is it the time to detect image
    if current_time - last_detection_time >= detection_interval:
        try:
            img_resp = urllib.request.urlopen(url)
            img_array = np.array(bytearray(img_resp.read()), dtype=np.uint8)
            frame = cv2.imdecode(img_array, -1)
        except Exception as e:
            print(f"Failed to fetch frame: {e}. Retrying...")
            continue

        # Run YOLOv8 inference
        results = model(frame)  

        # Reset last_detected_class
        last_detected_class = None

        # Get detected classes
        for result in results:
            boxes = result.boxes  # Get bounding boxes
            for box in boxes:
                class_id = int(box.cls)  # Get class ID
                class_name = model.names[class_id]  # Get class name
                print(f"Detected: {class_name}")

                last_detected_class = class_name

        last_detection_time = current_time

        # Visualize the results
        annotated_frame = results[0].plot() 

        # Display the annotated frame
        cv2.imshow("YOLOv8 Detection", annotated_frame)

    # Is it the time to send command
    if current_time - last_command_time >= command_interval:
        if last_detected_class:
            send_command(last_detected_class) 
        else:
            send_command("NONE") 

        last_command_time = current_time

    # Exit Command
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

ser.close()
cv2.destroyAllWindows()