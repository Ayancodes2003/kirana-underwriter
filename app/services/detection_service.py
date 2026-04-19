from functools import lru_cache

from ultralytics import YOLO


@lru_cache(maxsize=1)
def get_model() -> YOLO:
    return YOLO("yolov8n.pt")


def detect_products(image) -> list[dict]:
    model = get_model()
    results = model.predict(source=image, verbose=False)
    if not results:
        return []

    result = results[0]
    names = result.names or model.names
    detections: list[dict] = []

    if result.boxes is None:
        return detections

    for box in result.boxes:
        x1, y1, x2, y2 = [float(value) for value in box.xyxy[0].tolist()]
        class_id = int(box.cls[0].item())
        confidence = float(box.conf[0].item())
        detections.append(
            {
                "label": names.get(class_id, str(class_id)),
                "class_id": class_id,
                "confidence": round(confidence, 4),
                "bbox": [round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)],
                "area": round(max(0.0, (x2 - x1) * (y2 - y1)), 2),
            }
        )

    return detections
