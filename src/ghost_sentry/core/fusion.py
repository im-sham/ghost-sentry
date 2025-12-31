"""Multi-modal detection fusion engine."""
from typing import List
from ghost_sentry.core.detector import Detection

class FusionEngine:
    """Fuses detections from multiple sensors (e.g., Optical, SAR)."""
    
    def __init__(self, optical_threshold: float = 0.5):
        self.optical_threshold = optical_threshold
    
    def fuse(self, optical_detections: List[Detection], sar_detections: List[Detection]) -> List[Detection]:
        """
        Fuse detections. 
        Current Logic: 
        - If Optical detections reflect high confidence (>= threshold), prioritize them.
        - If Optical confidence is low (e.g., cloudy), they are filtered out, and SAR detections act as primary leads.
        - SAR detections are always included as all-weather/all-day primary leads.
        """
        fused = []
        
        # Add optical detections if they meet the confidence threshold
        for d in optical_detections:
            if d.confidence >= self.optical_threshold:
                d.label = f"{d.label} (Optical)"
                fused.append(d)
            
        # Add SAR detections and mark source
        for d in sar_detections:
            d.label = f"{d.label} (SAR)"
            fused.append(d)
            
        return fused
