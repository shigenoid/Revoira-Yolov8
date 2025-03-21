from ultralytics import YOLO
import cv2
import paho.mqtt.client as mqtt
import time
import os
from dotenv import load_dotenv

load_dotenv()  # .env file must exist in same folder

# MQTT setup
mqttc = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=os.getenv("CLIENT_ID")  # Client ID from .env
)
mqttc.connect(os.getenv("MQTT_SERVER"), int(os.getenv("MQTT_PORT")))
mqttc.loop_start()

# YOLOv8 Model
model = YOLO('runs/detect/revoira-100/weights/best.pt')  # Replace with your trained model

#esp32
url = "http://192.168.84.187/cam-hi.jpg"

# Webcam Setup
cam = cv2.VideoCapture(0)
if not cam.isOpened():
    print("Cannot open camera")
    exit()

# Throttling Variables
last_publish_time = 0
PUBLISH_INTERVAL = 3  # Seconds

while True:
    ret, frame = cam.read()
    if not ret:
        print("Can't receive frame. Exiting...")
        break

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
        if detected_classes:
            msg = ",".join(detected_classes)
        else:
            msg = "NONE"
        
        mqttc.publish(os.getenv("MQTT_TOPIC"), msg)
        last_publish_time = current_time

    # Display Annotated Frame
    cv2.imshow('frame', results[0].plot())
    if cv2.waitKey(1) == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()