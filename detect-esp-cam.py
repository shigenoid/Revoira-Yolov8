import cv2
import numpy as np
import urllib.request
import serial
import time
from ultralytics import YOLO

# Load the trained YOLOv8 model
model = YOLO("runs/detect/bottle-train/weights/best.pt")  # Path to your trained YOLOv8 model

# ESP32-CAM URL
url = "http://192.168.9.32/cam-hi.jpg"

# Inisialisasi komunikasi serial dengan ESP32-CAM
ser = serial.Serial('COM3', 115200, timeout=1)  # Ganti 'COMX' dengan port ESP32-CAM
time.sleep(2)  # Tunggu koneksi stabil

# Fungsi untuk mengirim perintah ke ESP32-CAM
def send_command(class_name):
    if class_name == "glass-bottle":
        ser.write(b'GLASS\n')  # Kirim perintah untuk glass-bottle
    elif class_name == "can-bottle":
        ser.write(b'CAN\n')  # Kirim perintah untuk can-bottle
    elif class_name == "plastic-bottle":
        ser.write(b'PLASTIC\n')  # Kirim perintah untuk plastic-bottle
    elif class_name == "tetrapak":
        ser.write(b'TETRAPAK\n')  # Kirim perintah untuk tetrapak
    else:
        ser.write(b'NONE\n')  # Kirim perintah NONE jika tidak ada deteksi

# Timer untuk deteksi gambar setiap 1 detik
last_detection_time = time.time()  # Waktu terakhir deteksi gambar dilakukan
detection_interval = 1  # Interval deteksi gambar (dalam detik)

# Timer untuk mengirim perintah setiap 5 detik
last_command_time = time.time()  # Waktu terakhir perintah dikirim
command_interval = 5  # Interval pengiriman perintah (dalam detik)

# Variabel untuk menyimpan hasil deteksi terakhir
last_detected_class = None

while True:
    # Ambil waktu saat ini
    current_time = time.time()

    # Cek apakah sudah waktunya untuk melakukan deteksi gambar
    if current_time - last_detection_time >= detection_interval:
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

        # Reset last_detected_class
        last_detected_class = None

        # Get detected classes
        for result in results:
            boxes = result.boxes  # Get bounding boxes
            for box in boxes:
                class_id = int(box.cls)  # Get class ID
                class_name = model.names[class_id]  # Get class name
                print(f"Detected: {class_name}")

                # Simpan kelas yang terdeteksi
                last_detected_class = class_name

        # Update waktu terakhir deteksi gambar
        last_detection_time = current_time

        # Visualize the results
        annotated_frame = results[0].plot()  # Get the annotated frame

        # Display the annotated frame
        cv2.imshow("YOLOv8 Detection", annotated_frame)

    # Cek apakah sudah waktunya untuk mengirim perintah
    if current_time - last_command_time >= command_interval:
        # Kirim perintah berdasarkan hasil deteksi terakhir
        if last_detected_class:
            send_command(last_detected_class)  # Kirim perintah sesuai kelas yang terdeteksi
        else:
            send_command("NONE")  # Kirim perintah NONE jika tidak ada deteksi

        # Update waktu terakhir pengiriman perintah
        last_command_time = current_time

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Tutup koneksi serial dan window OpenCV
ser.close()
cv2.destroyAllWindows()