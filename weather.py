"""
Weather & Environmental Visibility Analyzer for TraffiQ
=======================================================
Phase 3 Implementation:
Analyzes camera frames for rain, fog, low light, and night conditions.
Automatically calculates a visibility index and adjusts YOLO confidence
and image preprocessing filters in real time.
"""

import cv2
import numpy as np
from config import CONF_THRESHOLD

class WeatherAnalyzer:
    """Evaluates environmental visibility and lighting dynamics."""
    def __init__(self):
        self.condition = "Clear"
        self.visibility_score = 1.0  # 0.0 to 1.0
        self.last_adjusted_conf = CONF_THRESHOLD
        self.frame_counter = 0

    def analyze_frame(self, frame: np.ndarray) -> dict:
        """Analyzes frame brightness, contrast, and blur/fog index."""
        self.frame_counter += 1
        if self.frame_counter % 15 != 0:
            return {
                "condition": self.condition,
                "visibility_score": self.visibility_score,
                "recommended_conf": self.last_adjusted_conf
            }

        # Downsample for ultra-fast environmental analysis
        small = cv2.resize(frame, (160, 90))
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        
        # 1. Mean brightness & contrast
        mean_brightness = np.mean(gray)
        std_contrast = np.std(gray)
        
        # 2. Laplacian variance (Sharpness / Fog detector)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Determine condition
        if mean_brightness < 45:
            self.condition = "Night"
            # At night, vehicle headlights cause contrast spikes; lower conf to catch dim silhouettes
            self.visibility_score = round(mean_brightness / 100.0, 2)
            self.last_adjusted_conf = max(0.18, CONF_THRESHOLD - 0.08)
        elif laplacian_var < 80 and std_contrast < 38:
            self.condition = "Fog / Haze"
            self.visibility_score = round(laplacian_var / 120.0, 2)
            self.last_adjusted_conf = max(0.20, CONF_THRESHOLD - 0.05)
        elif std_contrast < 30:
            self.condition = "Rain / Overcast"
            self.visibility_score = 0.65
            self.last_adjusted_conf = max(0.20, CONF_THRESHOLD - 0.04)
        else:
            self.condition = "Clear Day"
            self.visibility_score = 0.98
            self.last_adjusted_conf = CONF_THRESHOLD

        return {
            "condition": self.condition,
            "visibility_score": self.visibility_score,
            "recommended_conf": self.last_adjusted_conf
        }

