from ultralytics import YOLO
import cv2
import paho.mqtt.client as mqtt
import time
import os
import urllib.request
import numpy as np
from dotenv import load_dotenv

load_dotenv()  # .env file must exist in the same folder

# MQTT setup
mqttc = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=os.getenv("CLIENT_ID")  # Client ID from .env
)
mqttc.connect(os.getenv("MQTT_SERVER"), int(os.getenv("MQTT_PORT")))
mqttc.loop_start()

# YOLOv8 Model
model = YOLO('runs/detect/bottle-train/weights/best.pt')  # Replace with your trained model

# ESP32-CAM Streaming URL
ESP_CAM_URL = os.getenv("ESP_CAM_URL")  # Example: http://192.168.x.x/cam-hi.jpg

# Throttling Variables
last_publish_time = 0
PUBLISH_INTERVAL = 3  # Seconds

while True:
    try:
        # Capture frame from ESP32-CAM
        img_resp = urllib.request.urlopen(ESP_CAM_URL)
        img_array = np.array(bytearray(img_resp.read()), dtype=np.uint8)
        frame = cv2.imdecode(img_array, -1)

        # YOLOv8 Inference
        results = model.predict(frame, conf=0.6)
        detected_classes = set()

        # Process Results
        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls.item())
                detected_classes.add(model.names[cls_id])

        # Throttled MQTT Publishing
        current_time = time.time()
        if current_time - last_publish_time >= PUBLISH_INTERVAL:
            msg = ",".join(detected_classes) if detected_classes else "NONE"
            mqttc.publish(os.getenv("MQTT_TOPIC"), msg)
            last_publish_time = current_time

        # Display Annotated Frame
        cv2.imshow('ESP32-CAM Stream', results[0].plot())
        if cv2.waitKey(1) == ord('q'):
            break

    except Exception as e:
        print(f"Error: {e}. Retrying...")

cv2.destroyAllWindows()