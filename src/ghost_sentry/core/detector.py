"""Object detection using YOLOv8."""
from typing import Optional
from pydantic import BaseModel
from ultralytics import YOLO

class Detection(BaseModel):
    """A single detected object."""
    label: str
    confidence: float
    bbox: tuple[int, int, int, int]  # x1, y1, x2, y2
    geo_location: Optional[tuple[float, float]] = None  # lat, lon

class ObjectDetector:
    """YOLOv8-based object detector."""
    
    TACTICAL_CLASSES = {"airplane", "truck", "car", "boat", "bus"}
    
    def __init__(self, model_path: str = "yolov8n.pt"):
        self.model = YOLO(model_path)
    
    def detect(self, image_path: str) -> list[Detection]:
        """Run detection on an image."""
        results = self.model(image_path)
        detections = []
        for result in results:
            for box in result.boxes:
                label = result.names[int(box.cls)]
                if label in self.TACTICAL_CLASSES:
                    detections.append(Detection(
                        label=label,
                        confidence=float(box.conf),
                        bbox=tuple(map(int, box.xyxy[0].tolist())),
                        geo_location=None  # Populated by geo module if available
                    ))
        return detections
