"""
Multi-Camera & City GIS Map Manager for TraffiQ
==============================================
Phase 5 Implementation:
- Multi-stream camera registry (RTSP, Video files, Webcams)
- Active camera switcher and 2x2 grid view metadata
- GPS coordinate mapping for Leaflet.js interactive intersection map
"""

import os
from datetime import datetime

class CameraManager:
    """Manages multi-intersection camera sources and geographical locations."""
    def __init__(self):
        self.cameras = {
            "cam1": {
                "id": "cam1",
                "name": "Connaught Place Junction (North)",
                "source": "Traffic_Video.mp4",
                "type": "video_file",
                "status": "online",
                "fps": 30.0,
                "lat": 28.6315,
                "lng": 77.2167,
                "lanes": 2,
                "los": "B"
            },
            "cam2": {
                "id": "cam2",
                "name": "Kashmere Gate ISBT Interchange",
                "source": "simulated_cam2",
                "type": "synthetic_loop",
                "status": "online",
                "fps": 25.0,
                "lat": 28.6675,
                "lng": 77.2285,
                "lanes": 3,
                "los": "C"
            },
            "cam3": {
                "id": "cam3",
                "name": "Ring Road Flyover Corridor",
                "source": "simulated_cam3",
                "type": "synthetic_loop",
                "status": "online",
                "fps": 30.0,
                "lat": 28.5823,
                "lng": 77.2341,
                "lanes": 4,
                "los": "A"
            },
            "cam4": {
                "id": "cam4",
                "name": "IGI Airport Expressway Gate 3",
                "source": "simulated_cam4",
                "type": "synthetic_loop",
                "status": "online",
                "fps": 28.0,
                "lat": 28.5562,
                "lng": 77.1000,
                "lanes": 3,
                "los": "B"
            }
        }
        self.active_camera_id = "cam1"

    def get_cameras_list(self, current_los: str = "B"):
        """Returns camera roster with dynamically updated congestion colors."""
        cam_list = []
        for cid, cam in self.cameras.items():
            c = dict(cam)
            if cid == self.active_camera_id:
                c["los"] = current_los
            c["color"] = self._get_los_color(c["los"])
            cam_list.append(c)
        return cam_list

    def set_active_camera(self, camera_id: str):
        if camera_id in self.cameras:
            self.active_camera_id = camera_id
            return True
        return False

    def add_camera(self, cam_id: str, name: str, source: str, lat: float, lng: float):
        self.cameras[cam_id] = {
            "id": cam_id,
            "name": name,
            "source": source,
            "type": "rtsp" if source.startswith("rtsp://") else "video",
            "status": "online",
            "fps": 30.0,
            "lat": lat,
            "lng": lng,
            "lanes": 2,
            "los": "A"
        }

    @staticmethod
    def _get_los_color(los: str) -> str:
        colors = {
            "A": "#10b981", # Emerald
            "B": "#34d399", # Green
            "C": "#fbbf24", # Amber
            "D": "#fb923c", # Orange
            "E": "#f87171", # Red
            "F": "#ef4444"  # Dark Red
        }
        return colors.get(los, "#10b981")

camera_manager = CameraManager()

