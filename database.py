"""
Database Module for TraffiQ
===========================
Production-ready SQLite persistence for violations, traffic logs, alerts,
audit trails, and customizable camera zones with auto-cleanup policies.
"""

import sqlite3
import json
import os
import time
from datetime import datetime, timedelta
import threading

DB_FILE = os.environ.get("TRAFFIQ_DB", "traffiq.db")
_db_lock = threading.Lock()

def get_db_connection():
    db_path = os.environ.get("TRAFFIQ_DB", DB_FILE)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    with _db_lock:
        conn = get_db_connection()
        c = conn.cursor()
        
        # 1. Violations Table
        c.execute("""
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            type TEXT NOT NULL,
            track_id INTEGER,
            lane_id INTEGER,
            speed_kmh REAL,
            plate_number TEXT,
            details TEXT,
            evidence_img TEXT,
            evidence_clip TEXT,
            status TEXT DEFAULT 'unreviewed'
        );
        """)
        
        # 2. Traffic Log Table
        c.execute("""
        CREATE TABLE IF NOT EXISTS traffic_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            frame_id INTEGER,
            lane_id INTEGER,
            cars INTEGER DEFAULT 0,
            buses INTEGER DEFAULT 0,
            trucks INTEGER DEFAULT 0,
            motorbikes INTEGER DEFAULT 0,
            pedestrians INTEGER DEFAULT 0,
            total INTEGER DEFAULT 0,
            los TEXT,
            flow_rate REAL,
            incident INTEGER DEFAULT 0
        );
        """)
        
        # 3. Alerts Center Table
        c.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            severity TEXT NOT NULL, -- critical, warning, info
            category TEXT NOT NULL, -- incident, violation, ambulance, congestion
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            acknowledged INTEGER DEFAULT 0
        );
        """)
        
        # 4. User Settings Table
        c.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            username TEXT PRIMARY KEY,
            settings_json TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """)
        
        # 5. Audit Log Table
        c.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            username TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT
        );
        """)
        
        # 6. User Custom Zones Table
        c.execute("""
        CREATE TABLE IF NOT EXISTS custom_zones (
            id TEXT PRIMARY KEY,
            camera_id TEXT NOT NULL,
            name TEXT NOT NULL,
            zone_type TEXT NOT NULL, -- stop_line, no_parking, crosswalk, speed_trap
            coordinates_json TEXT NOT NULL,
            active INTEGER DEFAULT 1
        );
        """)

        # 7. Emergency Corridor Preemption Table
        c.execute("""
        CREATE TABLE IF NOT EXISTS emergency_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            vehicle_type TEXT NOT NULL, -- Ambulance, Fire Engine, Police Car, Rescue Truck
            lane_id INTEGER NOT NULL,
            speed_kmh REAL DEFAULT 0.0,
            prior_signal_state TEXT DEFAULT 'RED',
            new_signal_state TEXT DEFAULT 'GREEN',
            duration_seconds REAL DEFAULT 30.0,
            status TEXT DEFAULT 'Completed'
        );
        """)
        
        conn.commit()
        conn.close()

# ──────────────────────────────────────────────
# VIOLATIONS CRUD
# ──────────────────────────────────────────────
def insert_violation(v_type: str, track_id: int, lane_id: int, speed_kmh: float,
                     plate_number: str = "UNKNOWN", details: str = "",
                     evidence_img: str = "", evidence_clip: str = "") -> int:
    with _db_lock:
        conn = get_db_connection()
        ts = datetime.now().isoformat(timespec="seconds")
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO violations (timestamp, type, track_id, lane_id, speed_kmh, plate_number, details, evidence_img, evidence_clip)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (ts, v_type, track_id, lane_id, speed_kmh, plate_number, details, evidence_img, evidence_clip))
        v_id = cur.lastrowid
        conn.commit()
        conn.close()
        return v_id

def get_recent_violations(limit: int = 50, v_type: str = None):
    with _db_lock:
        conn = get_db_connection()
        cur = conn.cursor()
        if v_type and v_type != "all":
            cur.execute("SELECT * FROM violations WHERE type = ? ORDER BY id DESC LIMIT ?", (v_type, limit))
        else:
            cur.execute("SELECT * FROM violations ORDER BY id DESC LIMIT ?", (limit,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

def get_violation_by_id(v_id: int):
    with _db_lock:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM violations WHERE id = ?", (v_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None

# ──────────────────────────────────────────────
# ALERTS CRUD
# ──────────────────────────────────────────────
def insert_alert(severity: str, category: str, title: str, message: str) -> int:
    with _db_lock:
        conn = get_db_connection()
        ts = datetime.now().isoformat(timespec="seconds")
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO alerts (timestamp, severity, category, title, message)
            VALUES (?, ?, ?, ?, ?)
        """, (ts, severity, category, title, message))
        a_id = cur.lastrowid
        conn.commit()
        conn.close()
        return a_id

def get_alerts(limit: int = 40, category: str = None):
    with _db_lock:
        conn = get_db_connection()
        cur = conn.cursor()
        if category and category != "all":
            cur.execute("SELECT * FROM alerts WHERE category = ? ORDER BY id DESC LIMIT ?", (category, limit))
        else:
            cur.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT ?", (limit,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

def acknowledge_alert(a_id: int):
    with _db_lock:
        conn = get_db_connection()
        conn.execute("UPDATE alerts SET acknowledged = 1 WHERE id = ?", (a_id,))
        conn.commit()
        conn.close()

# ──────────────────────────────────────────────
# AUDIT LOG
# ──────────────────────────────────────────────
def log_audit(username: str, action: str, details: str = ""):
    with _db_lock:
        conn = get_db_connection()
        ts = datetime.now().isoformat(timespec="seconds")
        conn.execute("INSERT INTO audit_logs (timestamp, username, action, details) VALUES (?, ?, ?, ?)",
                     (ts, username, action, details))
        conn.commit()
        conn.close()

def get_audit_logs(limit: int = 50):
    with _db_lock:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

# ──────────────────────────────────────────────
# CUSTOM ZONES
# ──────────────────────────────────────────────
def save_custom_zone(zone_id: str, camera_id: str, name: str, zone_type: str, coords: list):
    with _db_lock:
        conn = get_db_connection()
        coords_json = json.dumps(coords)
        conn.execute("""
            INSERT OR REPLACE INTO custom_zones (id, camera_id, name, zone_type, coordinates_json, active)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (zone_id, camera_id, name, zone_type, coords_json))
        conn.commit()
        conn.close()

def get_custom_zones(camera_id: str = "cam1"):
    with _db_lock:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM custom_zones WHERE camera_id = ? AND active = 1", (camera_id,))
        rows = []
        for r in cur.fetchall():
            d = dict(r)
            d["coordinates"] = json.loads(d["coordinates_json"])
            rows.append(d)
        conn.close()
        return rows

def delete_custom_zone(zone_id: str):
    with _db_lock:
        conn = get_db_connection()
        conn.execute("DELETE FROM custom_zones WHERE id = ?", (zone_id,))
        conn.commit()
        conn.close()

# ──────────────────────────────────────────────
# USER SETTINGS PERSISTENCE
# ──────────────────────────────────────────────
def save_user_settings(username: str, settings: dict):
    with _db_lock:
        conn = get_db_connection()
        ts = datetime.now().isoformat(timespec="seconds")
        settings_str = json.dumps(settings)
        conn.execute("""
            INSERT OR REPLACE INTO user_settings (username, settings_json, updated_at)
            VALUES (?, ?, ?)
        """, (username, settings_str, ts))
        conn.commit()
        conn.close()

def get_user_settings(username: str) -> dict:
    with _db_lock:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT settings_json FROM user_settings WHERE username = ?", (username,))
        row = cur.fetchone()
        conn.close()
        if row and row["settings_json"]:
            try:
                return json.loads(row["settings_json"])
            except Exception:
                pass
        return {}

# ──────────────────────────────────────────────
# HISTORICAL ANALYTICS QUERY
# ──────────────────────────────────────────────
def get_historical_traffic(hours: int = 24, lane_id: str = None):
    with _db_lock:
        conn = get_db_connection()
        cur = conn.cursor()
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat(timespec="seconds")
        
        query = "SELECT timestamp, lane_id, cars, buses, trucks, motorbikes, pedestrians, total, los, flow_rate FROM traffic_logs WHERE timestamp >= ?"
        params = [cutoff]
        if lane_id and lane_id != "all":
            query += " AND lane_id = ?"
            params.append(lane_id)
        query += " ORDER BY id ASC"
        
        cur.execute(query, params)
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

def log_traffic_frame(frame_id: int, lane_counts: dict, incidents: list, los_dict: dict, flow_dict: dict):
    with _db_lock:
        conn = get_db_connection()
        ts = datetime.now().isoformat(timespec="seconds")
        incident_lanes = {inc["lane"] for inc in incidents}
        cur = conn.cursor()
        for lid, counts in lane_counts.items():
            tot = sum(counts.values())
            los = los_dict.get(str(lid), "A")
            flow = flow_dict.get(str(lid), 0.0)
            inc = 1 if lid in incident_lanes else 0
            cur.execute("""
                INSERT INTO traffic_logs (timestamp, frame_id, lane_id, cars, buses, trucks, motorbikes, pedestrians, total, los, flow_rate, incident)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (ts, frame_id, lid, counts.get("car", 0), counts.get("bus", 0), counts.get("truck", 0),
                  counts.get("motorbike", 0), counts.get("pedestrian", 0), tot, los, flow, inc))
        conn.commit()
        conn.close()

# ──────────────────────────────────────────────
# EMERGENCY CORRIDOR PREEMPTION CRUD
# ──────────────────────────────────────────────
def log_emergency_transit(vehicle_type: str, lane_id: int, speed_kmh: float = 0.0,
                          prior_signal_state: str = "RED", new_signal_state: str = "GREEN",
                          duration_seconds: float = 30.0, status: str = "Corridor Cleared") -> int:
    with _db_lock:
        conn = get_db_connection()
        cur = conn.cursor()
        ts = datetime.now().isoformat(timespec="seconds")
        cur.execute("""
            INSERT INTO emergency_logs (timestamp, vehicle_type, lane_id, speed_kmh,
                                        prior_signal_state, new_signal_state, duration_seconds, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (ts, vehicle_type, lane_id, speed_kmh, prior_signal_state, new_signal_state, duration_seconds, status))
        e_id = cur.lastrowid
        conn.commit()
        conn.close()
        return e_id

def get_emergency_transits(limit: int = 50) -> list:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM emergency_logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_emergency_statistics() -> dict:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as total FROM emergency_logs")
    tot = cur.fetchone()["total"]
    
    cur.execute("""
        SELECT vehicle_type, COUNT(*) as cnt
        FROM emergency_logs
        GROUP BY vehicle_type
    """)
    breakdown = {r["vehicle_type"]: r["cnt"] for r in cur.fetchall()}
    
    cur.execute("SELECT AVG(speed_kmh) as avg_spd, AVG(duration_seconds) as avg_dur FROM emergency_logs")
    stats = cur.fetchone()
    avg_speed = round(stats["avg_spd"] or 0.0, 1)
    avg_duration = round(stats["avg_dur"] or 0.0, 1)

    cur.execute("SELECT * FROM emergency_logs ORDER BY id DESC LIMIT 1")
    last_row = cur.fetchone()
    last_event = dict(last_row) if last_row else None
    conn.close()

    return {
        "total_transits": tot,
        "ambulance_count": breakdown.get("Ambulance", 0),
        "fire_engine_count": breakdown.get("Fire Engine", 0) + breakdown.get("Fire Truck", 0),
        "police_count": breakdown.get("Police Car", 0),
        "rescue_count": breakdown.get("Rescue Truck", 0),
        "breakdown": breakdown,
        "avg_speed_kmh": avg_speed,
        "avg_duration_s": avg_duration,
        "last_transit": last_event
    }

# ──────────────────────────────────────────────
# RETENTION POLICY / AUTO-CLEANUP
# ──────────────────────────────────────────────
def run_db_cleanup(retention_days: int = 30):
    with _db_lock:
        conn = get_db_connection()
        cutoff = (datetime.now() - timedelta(days=retention_days)).isoformat(timespec="seconds")
        conn.execute("DELETE FROM traffic_logs WHERE timestamp < ?", (cutoff,))
        conn.execute("DELETE FROM alerts WHERE timestamp < ? AND acknowledged = 1", (cutoff,))
        conn.execute("DELETE FROM audit_logs WHERE timestamp < ?", (cutoff,))
        conn.commit()
        conn.close()

# Initialize tables immediately
init_db()
