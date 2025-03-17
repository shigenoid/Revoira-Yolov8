from ultralytics import YOLO
import torch
import os

def main():
    model = YOLO("runs/detect/revoira-100/weights/last.pt")

    # Train the model
    results = model.train(
        data="data.yaml",  
        epochs=100, 
        warmup_epochs=3,          
        batch=32,           
        imgsz=640,         
        device="0",           
        name="revoira-100",        # Name of the training run
        workers=0,          # Disable multiprocessing (set to 0 for Windows)
        resume=True
    )

if __name__ == "__main__":
    # Fix for multiprocessing on Windows
    torch.multiprocessing.freeze_support()
    main()