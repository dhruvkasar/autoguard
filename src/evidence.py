import os
import json
import time
from typing import Tuple
import cv2
from .utils import sha256_file
import tempfile
import zipfile


def save_evidence(frame, xyxy: Tuple[int, int, int, int], person_id: int, rule_name: str, 
                  evidence_dir: str, camera_id: str, logger, description: str = "", priority: str = "standard") -> str:
    """
    Save evidence snapshot with metadata including AI-generated description.
    
    Args:
        frame: OpenCV frame (BGR)
        xyxy: Bounding box coordinates [x1, y1, x2, y2]
        person_id: Track ID
        rule_name: Name of triggered rule
        evidence_dir: Directory to save evidence
        camera_id: Camera identifier
        logger: Logger instance
        description: AI-generated natural language description (optional)
        priority: Alert priority level ('high' or 'standard')
    
    Returns:
        Path to saved image file
    """
    os.makedirs(evidence_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    base = f"evidence_{camera_id}_id{person_id}_{rule_name.replace(' ', '_')}_{ts}"
    image_path = os.path.join(evidence_dir, base + ".jpg")
    meta_path = os.path.join(evidence_dir, base + ".json")

    x1, y1, x2, y2 = map(int, xyxy)
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
    cv2.putText(frame, f"{rule_name} | ID {person_id}", (x1, max(0, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.putText(frame, time.strftime("%Y-%m-%d %H:%M:%S"), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # Save image
    cv2.imwrite(image_path, frame)
    digest = sha256_file(image_path)

    metadata = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "person_id": person_id,
        "rule": rule_name,
        "camera_id": camera_id,
        "image_path": image_path,
        "sha256": digest,
        "description": description,  # AI-generated description
        "priority": priority,  # 'high' or 'standard'
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"Evidence captured: {image_path} | Priority: {priority} | SHA256={digest}")
    return image_path


def prune_old_evidence(evidence_dir: str, retention_days: int, logger) -> int:
    if retention_days <= 0:
        return 0
    now = time.time()
    cutoff = now - (retention_days * 86400)
    removed = 0
    for fname in list(os.listdir(evidence_dir)):
        if not (fname.endswith('.jpg') or fname.endswith('.json')):
            continue
        fpath = os.path.join(evidence_dir, fname)
        try:
            if os.path.getmtime(fpath) < cutoff:
                os.remove(fpath)
                removed += 1
        except Exception:
            continue
    if removed:
        logger.info(f"Pruned {removed} old evidence files older than {retention_days}d")
    return removed


def build_evidence_zip(evidence_dir: str) -> str:
    files = [os.path.join(evidence_dir, f) for f in os.listdir(evidence_dir) if f.endswith('.jpg') or f.endswith('.json')]
    tmp_fd, tmp_path = tempfile.mkstemp(suffix='.zip')
    os.close(tmp_fd)
    with zipfile.ZipFile(tmp_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.write(f, arcname=os.path.basename(f))
    return tmp_path


def ensure_thumbnail(image_path: str, thumb_dir: str, width: int = 320) -> str:
    os.makedirs(thumb_dir, exist_ok=True)
    base = os.path.basename(image_path)
    name, _ = os.path.splitext(base)
    thumb_path = os.path.join(thumb_dir, f"{name}_thumb.jpg")
    if os.path.exists(thumb_path):
        return thumb_path
    img = cv2.imread(image_path)
    if img is None:
        return thumb_path
    h, w = img.shape[:2]
    scale = width / float(w) if w > 0 else 1.0
    new_size = (width, int(h * scale))
    resized = cv2.resize(img, new_size)
    cv2.imwrite(thumb_path, resized)
    return thumb_path
