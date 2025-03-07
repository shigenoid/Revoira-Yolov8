from ultralytics import YOLO
import torch
import os

def main():
<<<<<<< HEAD
    model = YOLO("runs/detect/bottle-1504/weights/last.pt")
=======
    model = YOLO("yolov8n.pt")
>>>>>>> 0590b66211be66ede4c8970e20dfcf4508561c56

    # Train the model
    results = model.train(
        data="data.yaml",  
        epochs=150,
        warmup_epochs=3,            
        batch=32,            
        imgsz=640,          
        device="0",           # Use GPU (set to "cpu" if you don't have a GPU)
<<<<<<< HEAD
        name="bottle-1504",        # Name of the training run
=======
        name="bottle-150",        # Name of the training run
>>>>>>> 0590b66211be66ede4c8970e20dfcf4508561c56
        workers=0,          # Disable multiprocessing (set to 0 for Windows)
        #resume=True
    )

if __name__ == "__main__":
    torch.multiprocessing.freeze_support()
    main()