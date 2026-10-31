import threading
from collections import deque
from datetime import datetime
from config import SPEED_LIMIT_KMPH, INCIDENT_TIMEOUT, CONF_THRESHOLD, SIGNAL_MODE

# ──────────────────────────────────────────────
# SHARED STATE  (Flask ↔ OpenCV thread-safe)
# ──────────────────────────────────────────────
shared_state = {
    "lane_counts": {},          # {lane_id: {class: count}}
    "vehicle_count": 0,
    "incidents": [],            # list of active incident dicts
    "mode": "lanes",
    "fps": 0.0,
    "latency_ms": 18.0,
    "frame_id": 0,
    "speed_data": {},           # {track_id: speed_kmh}
    "speeders": [],             # recent speeding events
    "emergency_active": False,
    "emergency_lane": None,
    "lane_trends":   {},   # {lane_id_str: "↑"/"↓"/"→"}
    "lane_los":      {},   # {lane_id_str: "A".."F"}
    "lane_flow":     {},   # {lane_id_str: veh/min}
    "lane_queue":    {},   # {lane_id_str: stopped count at RED}
    "wrong_way":     [],   # list of track_ids flagged this frame
    "tailgating":    [],   # list of {id_a, id_b, lane} this frame
    "lane_predictions": {},  # {lane_id_str: predicted_count_in_15s}
    "ml_ready":      False,  # True once RF model has trained
    "speed_limit":   SPEED_LIMIT_KMPH,   # expose config for dashboard
    "incident_timeout": INCIDENT_TIMEOUT,
    "conf_threshold": CONF_THRESHOLD,
    
    # ── PHASE 1-7 EXTENSIONS ──
    "violations": [],           # list of recent violation objects
    "vehicle_classes": {        # live class distribution for donut chart
        "car": 0, "bus": 0, "truck": 0, "motorbike": 0, "auto": 0, "pedestrian": 0
    },
    "pedestrians_count": 0,
    "weather_condition": "Clear Day",
    "weather_score": 0.98,
    "signal_mode": SIGNAL_MODE, # "adaptive", "actuated", "fixed"
    "signal_status": {
        "active_green_lane": 1,
        "remaining_s": 25,
        "total_duration_s": 35,
        "strategy": "adaptive",
        "emergency_corridor": False,
        "green_wave": True
    },
    "forecast_15m": {},
    "forecast_30m": {},
    "forecast_60m": {},
    "active_camera": "cam1",
    "hardware_info": {
        "device": "CPU / Neural Engine",
        "acceleration": "Active",
        "model": "YOLOv8 Nano"
    }
}
state_lock = threading.Lock()

history_buf = deque(maxlen=60)

# ──────────────────────────────────────────────
# SESSION STATS  (for summary on quit)
# ──────────────────────────────────────────────
_ss_all_ids:       set  = set()
_ss_peak_count:    int  = 0
_ss_peak_time:     str  = ""
_ss_total_inc:     int  = 0
_ss_wrong_ids:     set  = set()
_ss_tailgate:      int  = 0
_ss_start:         str  = datetime.now().isoformat(timespec="seconds")
_ss_speeders:      int  = 0
_ss_violations:    int  = 0
_ss_ended:         bool = False

# Convenience namespace so callers use session_stats["key"] syntax
class _SessionStats:
    @property
    def all_ids(self):         return _ss_all_ids
    @property
    def peak_count(self):      return _ss_peak_count
    @peak_count.setter
    def peak_count(self, v):   global _ss_peak_count; _ss_peak_count = v
    @property
    def peak_time(self):       return _ss_peak_time
    @peak_time.setter
    def peak_time(self, v):    global _ss_peak_time; _ss_peak_time = v
    @property
    def total_incidents(self): return _ss_total_inc
    @total_incidents.setter
    def total_incidents(self, v): global _ss_total_inc; _ss_total_inc = v
    @property
    def wrong_way_ids(self):   return _ss_wrong_ids
    @property
    def tailgate_events(self): return _ss_tailgate
    @tailgate_events.setter
    def tailgate_events(self, v): global _ss_tailgate; _ss_tailgate = v
    @property
    def session_start(self):   return _ss_start
    @property
    def speeders_count(self):  return _ss_speeders
    @speeders_count.setter
    def speeders_count(self, v): global _ss_speeders; _ss_speeders = v
    @property
    def violations_count(self): return _ss_violations
    @violations_count.setter
    def violations_count(self, v): global _ss_violations; _ss_violations = v
    @property
    def session_ended(self):   return _ss_ended
    @session_ended.setter
    def session_ended(self, v): global _ss_ended; _ss_ended = v
    def __getitem__(self, k):  return getattr(self, k)
    def __setitem__(self, k, v): setattr(self, k, v)

session_stats = _SessionStats()
