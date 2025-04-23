from ultralytics import YOLO
import cv2
import paho.mqtt.client as mqtt
import time
import os
import requests  # Added for API requests
from dotenv import load_dotenv

load_dotenv()

# MQTT setup
mqttc = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=os.getenv("CLIENT_ID")
)
mqttc.connect(os.getenv("MQTT_SERVER"), int(os.getenv("MQTT_PORT")))
mqttc.loop_start()

# YOLOv8 Model
model = YOLO('models/model-1.pt')

# ESP32-CAM Setup
cam = cv2.VideoCapture(os.getenv("ESP32_CAM_URL"))

if not cam.isOpened():
    print("Failed to connect to ESP32-CAM stream")
    exit()

# Throttling Variables
last_publish_time = 0
PUBLISH_INTERVAL = 5  # Seconds
last_detected_classes = set()  # Track previous detection

# API Check Variables
API_CHECK_INTERVAL = 1  # Check API every 1 second
last_api_check_time = 0
detection_enabled = False  # Start with detection off

while True:
    current_time = time.time()
    
    # Check API for detection toggle status
    if current_time - last_api_check_time >= API_CHECK_INTERVAL:
        try:
            response = requests.get("https://revoira.vercel.app/session-status")
            if response.status_code == 200:
                data = response.json()
                detection_enabled = data.get("turnOn", False)
            else:
                print(f"API Error: Status {response.status_code}")
                detection_enabled = False
        except Exception as e:
            print(f"API Request Failed: {e}")
            detection_enabled = False
        last_api_check_time = current_time

    # Frame retrieval
    ret, frame = cam.read()
    if not ret:
        print("Frame retrieval error, trying to reconnect...")
        cam.release()
        time.sleep(2)
        cam = cv2.VideoCapture(os.getenv("ESP32_CAM_URL"))
        continue

    detected_classes = set()
    annotated_frame = frame  # Default to raw frame if detection is off

    # Only process detection if enabled
    if detection_enabled:
        # YOLOv8 Inference
        results = model.predict(frame, conf=0.6)
        
        # Process Results
        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls.item())
                detected_classes.add(model.names[cls_id])
        
        # Prepare annotated frame
        annotated_frame = results[0].plot()

        # Throttled MQTT Publishing (only if classes changed)
        if current_time - last_publish_time >= PUBLISH_INTERVAL:
            if detected_classes != last_detected_classes:
                msg = ",".join(detected_classes) if detected_classes else "NONE"
                mqttc.publish(os.getenv("MQTT_TOPIC"), msg)
                last_detected_classes = detected_classes.copy()
                last_publish_time = current_time
            else:
                # Reset timer to maintain throttle interval
                last_publish_time = current_time

    # Display frame (annotated if detection is on)
    cv2.imshow('ESP32-CAM Feed', annotated_frame)
    if cv2.waitKey(1) == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()