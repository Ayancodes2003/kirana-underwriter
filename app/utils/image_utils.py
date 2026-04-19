from __future__ import annotations

import cv2
import numpy as np


def decode_image_bytes(content: bytes):
    array = np.frombuffer(content, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Unsupported or corrupted image file.")
    return image
