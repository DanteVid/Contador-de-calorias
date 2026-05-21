from ultralytics import YOLO

if __name__ == '__main__':

    #model = YOLO("runs/detect/food_detector_v26m/weights/best.pt")
    model = YOLO("runs/detect/food_detector_v11m/weights/best.pt")
    #model = YOLO("runs/detect/food_detector/weights/best.pt")

    metrics = model.val(
        data="dataset/LVIS_Fruits_And_Vegetables/data.yaml",
        split="test"
    )

    # Ver resultados
    print(f"Precision:  {metrics.box.mp:.4f}")
    print(f"Recall:     {metrics.box.mr:.4f}")
    print(f"mAP50:      {metrics.box.map50:.4f}")
    print(f"mAP50-95:   {metrics.box.map:.4f}")