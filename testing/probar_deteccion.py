from ultralytics import YOLO

model = YOLO("runs/detect/food_detector_v11m/weights/best.pt")

results = model.predict(source="comida2.jpg", conf=0.5)

for r in results:
    print(r.boxes)
    r.show()
    r.save(filename="resultado.jpg")