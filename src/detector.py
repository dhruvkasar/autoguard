from typing import Optional
import numpy as np
from ultralytics import YOLO
try:
    import torch
    from ultralytics.nn import tasks as u_tasks
    # Allowlist DetectionModel for torch safe loading on PyTorch>=2.6
    if hasattr(torch, "serialization") and hasattr(torch.serialization, "add_safe_globals"):
        torch.serialization.add_safe_globals([u_tasks.DetectionModel])
except Exception:
    # If add_safe_globals is unavailable or fails, proceed; ultralytics may handle internally.
    pass
import supervision as sv


class YOLODetector:
    def __init__(self, weights: str = "yolov8n.pt", confidence_threshold: float = 0.35, device: str = "auto"):
        self.model = YOLO(weights)
        self.conf_threshold = confidence_threshold
        self.device = "cpu" if str(device).lower() == "auto" else device

    def detect(self, frame: np.ndarray) -> Optional[sv.Detections]:
        results = self.model.predict(frame, conf=self.conf_threshold, device=self.device, verbose=False)
        if not results:
            return None
        dets = sv.Detections.from_ultralytics(results[0])
        # Filter to only person class id 0
        if dets.class_id is not None:
            mask = dets.class_id == 0
            dets = dets[mask]
        return dets
