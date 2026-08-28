import hashlib
from typing import Tuple
import cv2


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def box_center(xyxy) -> Tuple[int, int]:
    x1, y1, x2, y2 = map(int, xyxy)
    return (int((x1 + x2) / 2), int((y1 + y2) / 2))


def draw_id(frame, xyxy, track_id: int, color=(0, 255, 0)):
    x1, y1, x2, y2 = map(int, xyxy)
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    cv2.putText(frame, f"ID {track_id}", (x1, max(0, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
