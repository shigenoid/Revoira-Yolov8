from ultralytics import YOLO
import torch
import os

def main():
    model = YOLO("yolov8n.pt")

    # Train the model
    results = model.train(
        data="data.yaml",  # Path to your dataset configuration file
        epochs=150, 
        warmup_epochs=3,           # Number of training epochs
        batch=32,             # Batch size
        imgsz=640,            # Image size
        device="0",           # Use GPU (set to "cpu" if you don't have a GPU)
        name="revoira-150",        # Name of the training run
        workers=0,          # Disable multiprocessing (set to 0 for Windows)
        resume=False
    )

if __name__ == "__main__":
    # Fix for multiprocessing on Windows
    torch.multiprocessing.freeze_support()
    main()