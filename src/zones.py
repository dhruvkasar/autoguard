from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import cv2

Point = Tuple[int, int]
Rect = Tuple[int, int, int, int]  # x1, y1, x2, y2
LineSeg = Tuple[Point, Point]


@dataclass
class Zone:
    name: str
    rect: Rect
    color: Tuple[int, int, int] = (0, 255, 255)

    def contains(self, p: Point) -> bool:
        x1, y1, x2, y2 = self.rect
        x, y = p
        return x1 <= x <= x2 and y1 <= y <= y2

    def draw(self, frame, thickness: int = 2):
        x1, y1, x2, y2 = self.rect
        cv2.rectangle(frame, (x1, y1), (x2, y2), self.color, thickness)
        cv2.putText(frame, self.name, (x1 + 5, y1 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.color, 2)


class ZoneManager:
    def __init__(self, zones: List[Zone]):
        self.zones = zones
        self.zone_map: Dict[str, Zone] = {z.name: z for z in zones}

    def locate(self, p: Point) -> Optional[str]:
        for z in self.zones:
            if z.contains(p):
                return z.name
        return None

    def draw_all(self, frame):
        for z in self.zones:
            z.draw(frame)


@dataclass
class Line:
    p1: Point
    p2: Point
    color: Tuple[int, int, int] = (0, 0, 255)
    thickness: int = 2

    def draw(self, frame):
        cv2.line(frame, self.p1, self.p2, self.color, self.thickness)


def _ccw(a: Point, b: Point, c: Point) -> int:
    return (c[1] - a[1]) * (b[0] - a[0]) - (b[1] - a[1]) * (c[0] - a[0])


def segments_intersect(p: Point, p2: Point, q: Point, q2: Point) -> bool:
    d1 = _ccw(p, p2, q)
    d2 = _ccw(p, p2, q2)
    d3 = _ccw(q, q2, p)
    d4 = _ccw(q, q2, p2)

    if (d1 == 0 and min(p[0], p2[0]) <= q[0] <= max(p[0], p2[0]) and min(p[1], p2[1]) <= q[1] <= max(p[1], p2[1])):
        return True
    if (d2 == 0 and min(p[0], p2[0]) <= q2[0] <= max(p[0], p2[0]) and min(p[1], p2[1]) <= q2[1] <= max(p[1], p2[1])):
        return True
    if (d3 == 0 and min(q[0], q2[0]) <= p[0] <= max(q[0], q2[0]) and min(q[1], q2[1]) <= p[1] <= max(q[1], q2[1])):
        return True
    if (d4 == 0 and min(q[0], q2[0]) <= p2[0] <= max(q[0], q2[0]) and min(q[1], q2[1]) <= p2[1] <= max(q[1], q2[1])):
        return True
    return (d1 > 0) != (d2 > 0) and (d3 > 0) != (d4 > 0)
