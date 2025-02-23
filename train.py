from ultralytics import YOLO
import torch
import os

def main():
    # Load a pre-trained YOLOv8 model
    model = YOLO("runs/detect/bottle-train/weights/last.pt")

    # Train the model
    results = model.train(
        data="data.yaml",  # Path to your dataset configuration file
        epochs=50,            # Number of training epochs
        batch=16,             # Batch size
        imgsz=320,            # Image size
        device="0",           # Use GPU (set to "cpu" if you don't have a GPU)
        name="bottle-train-2",        # Name of the training run
        workers=0,          # Disable multiprocessing (set to 0 for Windows)
        resume=True
    )

if __name__ == "__main__":
    # Fix for multiprocessing on Windows
    torch.multiprocessing.freeze_support()
    main()