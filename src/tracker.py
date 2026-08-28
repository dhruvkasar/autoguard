import supervision as sv


class ByteTrackerWrapper:
    def __init__(self, track_threshold: float = 0.3, match_threshold: float = 0.8):
        # Use supervision defaults for compatibility across versions
        self.tracker = sv.ByteTrack()

    def update(self, detections: sv.Detections) -> sv.Detections:
        return self.tracker.update_with_detections(detections)
