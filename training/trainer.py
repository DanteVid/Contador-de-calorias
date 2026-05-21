from ultralytics import YOLO


if __name__ == '__main__':
    # Load a pretrained model 
    model = YOLO('yolo11m.pt') 

    # Fine tuning the model on custom dataset
    results = model.train(data='dataset/LVIS_Fruits_And_Vegetables/data.yaml', epochs=50, imgsz=1024, device=0, batch=4, name='food_detector_v11m_NewBiggerSize')

    print(results)