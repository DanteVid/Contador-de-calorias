from fastapi import FastAPI, UploadFile, File
from ultralytics import YOLO
from inferences.inference import run_inference
from pathlib import Path
import pandas as pd

app = FastAPI()
model = YOLO("runs/detect/food_detector_v11m/weights/best.pt")

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    contents = await file.read()
    resultado = run_inference(contents, model)
    return {"resultado": resultado}