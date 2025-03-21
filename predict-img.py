from ultralytics import YOLO
import cv2
import paho.mqtt.client as mqtt
import os
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
model = YOLO('runs/detect/revoira-100/weights/best.pt')

# Load image (replace with your image path)
image_path = "test-img/tetrapak/1.jpg"
image = cv2.imread(image_path)
if image is None:
    print("Error loading image")
    exit()

# Perform inference
results = model.predict(image, conf=0.6)

# Process results
detected_classes = set()  # Using set to automatically avoid duplicates
for result in results:
    for box in result.boxes:
        cls_id = int(box.cls.item())
        cls_name = model.names[cls_id]
        detected_classes.add(cls_name)

# Prepare MQTT message
msg = ",".join(detected_classes) if detected_classes else "NONE"

mqttc.publish(os.getenv("MQTT_TOPIC"), msg)

# Save results
output_dir = "predict-results"
os.makedirs(output_dir, exist_ok=True)

# Save annotated image
annotated_image = results[0].plot()
output_path = os.path.join(output_dir, "predicted-image.jpg")
cv2.imwrite(output_path, annotated_image)

# Cleanup
mqttc.loop_stop()
mqttc.disconnect()