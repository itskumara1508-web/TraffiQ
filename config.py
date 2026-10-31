import os

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _resolve(path: str) -> str:
    if os.path.isabs(path):
        return path
    cand = os.path.join(_BASE_DIR, path)
    return cand if os.path.exists(cand) else path

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────

VIDEO_PATH          = _resolve("Traffic_Video.mp4")
MODEL_NAME          = _resolve("yolov8n.pt")
CONF_THRESHOLD      = 0.25          # detection confidence
TRACK_CLASSES       = {"car", "bus", "truck", "motorbike", "person"}
INCIDENT_TIMEOUT    = 5.0           # seconds a vehicle must stay still → incident
INCIDENT_DIST_PX    = 15            # pixels of movement tolerance
LOG_FILE            = _resolve("traffic_log.csv")
FLASK_PORT          = 5050
PIXEL_TO_METER      = 0.05          # ← change after calibration
SPEED_LIMIT_KMPH    = 50            # vehicles above this are flagged by speed camera
SPEEDER_LOG_FILE    = _resolve("speeders_log.csv")
EMERGENCY_CLASSES   = {"bus", "truck"}  # large vehicle proxy for ambulance/fire truck
EMERGENCY_SPEED_KMH = 40            # fast large vehicle = likely emergency vehicle

# ── ADVANCED ENFORCEMENT & PLATFORM EXTENSIONS ──
DATABASE_PATH                    = _resolve("traffiq.db")
EVIDENCE_DIR                     = os.path.join(_BASE_DIR, "evidence")
RED_LIGHT_ENFORCEMENT            = True
WRONG_WAY_DETECTION              = True
HELMET_DETECTION                 = True
ILLEGAL_PARKING_DETECTION        = True
PARKING_DWELL_TIMEOUT            = 12.0 # seconds
PEDESTRIAN_JAYWALKING_DETECTION  = True
WEATHER_ADAPT_ENABLED            = True
SIGNAL_MODE                      = "adaptive"  # "adaptive", "actuated", "fixed"
API_KEY                          = "traffiq_live_secret_key_2026"
