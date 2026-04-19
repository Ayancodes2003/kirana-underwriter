from __future__ import annotations


def compute_store_features(shelf_images: list[dict], detections: list[dict]) -> dict:
    shelf_density_values: list[float] = []
    unique_labels: set[str] = set()

    detection_lookup = {entry["filename"]: entry["detections"] for entry in detections}

    for payload in shelf_images:
        image = payload["image"]
        height, width = image.shape[:2]
        image_area = float(height * width) if height and width else 1.0
        image_detections = detection_lookup.get(payload["filename"], [])

        occupied_area = sum(float(detection["area"]) for detection in image_detections)
        shelf_density_values.append(min(1.0, occupied_area / image_area))

        for detection in image_detections:
            unique_labels.add(detection["label"])

    shelf_density = round(sum(shelf_density_values) / len(shelf_density_values), 4) if shelf_density_values else 0.0
    sku_diversity = len(unique_labels)

    return {
        "shelf_density": shelf_density,
        "sku_diversity": sku_diversity,
    }
