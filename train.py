from ultralytics import YOLO
import torch
import os

def main():
    model = YOLO("runs/detect/revoira-150/weights/last.pt")

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
        resume=True,
        lr0=0.001,
        weight_decay=0.001,  # Added regularization
        cos_lr=True,  # Enable cosine schedule
        patience=20,  # Early stopping
        freeze=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    )

if __name__ == "__main__":
    # Fix for multiprocessing on Windows
    torch.multiprocessing.freeze_support()
    main()