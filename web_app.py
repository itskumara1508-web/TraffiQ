import os
import secrets
import logging
import json
import time
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from flask import (
    Flask, jsonify, render_template_string, session, request,
    redirect, url_for, send_file, send_from_directory
)
from config import FLASK_PORT
from state import shared_state, state_lock, history_buf, session_stats
from templates import DASHBOARD_HTML, LANDING_HTML, EMERGENCY_HTML

# Modular component imports
from database import (
    get_recent_violations, get_violation_by_id, get_alerts,
    acknowledge_alert, get_audit_logs, log_audit, save_custom_zone,
    get_custom_zones, delete_custom_zone, get_historical_traffic,
    log_emergency_transit, get_emergency_transits, get_emergency_statistics,
    save_user_settings, get_user_settings, run_db_cleanup
)
from violations import ViolationManager, EVIDENCE_DIR
from reports import ReportGenerator
from alerts import active_toasts, AlertDispatcher
from multicam import camera_manager
from auth import require_api_key, audit_action

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(24))

DASH_USER = os.environ.get("DASH_USER", "admin")
DASH_PASS = os.environ.get("DASH_PASS", "admin123")

# Shared violation manager instance
v_manager = ViolationManager()

# ──────────────────────────────────────────────
# CORE ROUTES
# ──────────────────────────────────────────────
@app.route("/")
def home():
    if session.get("authenticated"):
        return redirect(url_for("dashboard"))
    return render_template_string(LANDING_HTML, default_user=DASH_USER, default_pass=DASH_PASS)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        session["authenticated"] = True
        session["user"] = DASH_USER
        session["role"] = "Admin"
        log_audit(DASH_USER, "USER_LOGIN", "One-click auto-login via GET")
        return redirect(url_for("dashboard"))

    username = request.form.get("username", "")
    password = request.form.get("password", "")
    if username == DASH_USER and password == DASH_PASS:
        session["authenticated"] = True
        session["user"] = username
        session["role"] = "Admin"
        log_audit(username, "USER_LOGIN", "Web console login successful")
        return redirect(url_for("dashboard"))
    
    log_audit(username or "unknown", "LOGIN_FAILED", "Invalid credentials provided")
    return redirect(url_for("home") + "?error=1")

@app.route("/logout")
def logout():
    u = session.get("user", "user")
    log_audit(u, "USER_LOGOUT", "User signed out")
    session.clear()
    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    if not session.get("authenticated"):
        return redirect(url_for("home") + "?error=1")
    with state_lock:
        s = dict(shared_state)
    return render_template_string(DASHBOARD_HTML, stats=s)

@app.route("/healthz")
def healthz():
    """Kubernetes / production healthcheck endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "engine": "YOLOv8 + ByteTrack",
        "active_camera": shared_state.get("active_camera", "cam1")
    }), 200

# ──────────────────────────────────────────────
# TELEMETRY API
# ──────────────────────────────────────────────
@app.route("/api/stats")
def api_stats():
    if not session.get("authenticated") and not request.headers.get("X-API-Key"):
        return jsonify({"error": "Unauthorized"}), 401
    with state_lock:
        return jsonify(shared_state)

@app.route("/api/history")
def api_history():
    if not session.get("authenticated") and not request.headers.get("X-API-Key"):
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(list(history_buf))

@app.route("/api/summary")
def api_summary():
    if not session.get("authenticated") and not request.headers.get("X-API-Key"):
        return jsonify({"error": "Unauthorized"}), 401
    start_str = session_stats.session_start
    try:
        start_dt = datetime.fromisoformat(start_str)
        elapsed = int((datetime.now() - start_dt).total_seconds())
        hours, rem = divmod(elapsed, 3600)
        mins, secs = divmod(rem, 60)
        duration = f"{hours:02d}:{mins:02d}:{secs:02d}"
    except Exception:
        duration = "—"
    return jsonify({
        "duration":        duration,
        "total_vehicles":  len(session_stats.all_ids),
        "peak_count":      session_stats.peak_count,
        "peak_time":       session_stats.peak_time,
        "total_incidents": session_stats.total_incidents,
        "speeders":        session_stats.speeders_count,
        "violations":      session_stats.violations_count,
        "wrong_way":       len(session_stats.wrong_way_ids),
        "tailgate_events": session_stats.tailgate_events,
        "session_start":   start_str,
        "session_ended":   session_stats.session_ended,
    })

# ──────────────────────────────────────────────
# PHASE 1 & 2: VIOLATIONS & LICENSE PLATES API
# ──────────────────────────────────────────────
@app.route("/api/violations")
def api_violations():
    if not session.get("authenticated") and not request.headers.get("X-API-Key"):
        return jsonify({"error": "Unauthorized"}), 401
    v_type = request.args.get("type", None)
    limit = int(request.args.get("limit", 50))
    records = get_recent_violations(limit=limit, v_type=v_type)
    return jsonify({"count": len(records), "violations": records})

@app.route("/api/evidence/<path:filename>")
def serve_evidence(filename):
    """Serves snapshot image or video clip from evidence directory."""
    return send_from_directory(EVIDENCE_DIR, filename)

@app.route("/api/violations/<int:v_id>/evidence")
def download_violation_evidence(v_id):
    """Packages evidence snapshot, video clip, and telemetry report as a ZIP."""
    if not session.get("authenticated") and not request.headers.get("X-API-Key"):
        return jsonify({"error": "Unauthorized"}), 401
    zip_path = v_manager.package_evidence_zip(v_id)
    if zip_path and os.path.exists(zip_path):
        return send_file(zip_path, as_attachment=True, download_name=os.path.basename(zip_path))
    return jsonify({"error": "Evidence package not found"}), 404

# ──────────────────────────────────────────────
# PHASE 3: HISTORICAL ANALYTICS & REPORTS API
# ──────────────────────────────────────────────
@app.route("/api/analytics/historical")
def api_historical_analytics():
    if not session.get("authenticated") and not request.headers.get("X-API-Key"):
        return jsonify({"error": "Unauthorized"}), 401
    hours = int(request.args.get("hours", 24))
    lane_id = request.args.get("lane_id", None)
    data = get_historical_traffic(hours=hours, lane_id=lane_id)
    return jsonify({"records": len(data), "data": data})

@app.route("/api/analytics/time-of-day")
def api_time_of_day():
    if not session.get("authenticated") and not request.headers.get("X-API-Key"):
        return jsonify({"error": "Unauthorized"}), 401
    matrix = ReportGenerator.get_time_of_day_matrix()
    return jsonify(matrix)

@app.route("/api/analytics/classes")
def api_vehicle_classes():
    if not session.get("authenticated") and not request.headers.get("X-API-Key"):
        return jsonify({"error": "Unauthorized"}), 401
    with state_lock:
        live_classes = dict(shared_state.get("vehicle_classes", {}))
    # Combine with DB aggregated breakdown
    db_stats = ReportGenerator.get_vehicle_classification_stats()
    combined = {k: live_classes.get(k, 0) + db_stats.get(k, 0) for k in db_stats}
    return jsonify(combined)

@app.route("/api/reports/download/pdf")
def download_pdf_report():
    if not session.get("authenticated") and not request.headers.get("X-API-Key"):
        return jsonify({"error": "Unauthorized"}), 401
    report_file = ReportGenerator.generate_html_pdf_report()
    return send_file(report_file, as_attachment=True, download_name="TraffiQ_Executive_Audit_Report.html")

@app.route("/api/reports/download/excel")
def download_excel_report():
    if not session.get("authenticated") and not request.headers.get("X-API-Key"):
        return jsonify({"error": "Unauthorized"}), 401
    csv_file = ReportGenerator.generate_excel_csv()
    return send_file(csv_file, as_attachment=True, download_name="TraffiQ_Traffic_Logs_Report.csv")

# ──────────────────────────────────────────────
# PHASE 4: ALERTS CENTER & CUSTOM ZONES API
# ──────────────────────────────────────────────
@app.route("/api/alerts")
def api_get_alerts():
    if not session.get("authenticated") and not request.headers.get("X-API-Key"):
        return jsonify({"error": "Unauthorized"}), 401
    cat = request.args.get("category", None)
    history = get_alerts(limit=30, category=cat)
    return jsonify({
        "toasts": list(active_toasts),
        "history": history
    })

@app.route("/api/alerts/ack/<int:a_id>", methods=["POST"])
def api_ack_alert(a_id):
    acknowledge_alert(a_id)
    return jsonify({"status": "acknowledged", "id": a_id})

@app.route("/api/zones", methods=["GET", "POST"])
def api_zones():
    if not session.get("authenticated") and not request.headers.get("X-API-Key"):
        return jsonify({"error": "Unauthorized"}), 401
    
    if request.method == "POST":
        data = request.get_json() or {}
        z_id = data.get("id", f"zone_{int(datetime.now().timestamp())}")
        save_custom_zone(
            zone_id=z_id,
            camera_id=data.get("camera_id", "cam1"),
            name=data.get("name", "Custom Zone"),
            zone_type=data.get("zone_type", "stop_line"),
            coords=data.get("coordinates", [])
        )
        log_audit(session.get("user", "admin"), "ZONE_CREATED", f"Zone {z_id} ({data.get('zone_type')}) created")
        return jsonify({"status": "saved", "zone_id": z_id})

    cam = request.args.get("camera_id", "cam1")
    return jsonify(get_custom_zones(cam))

@app.route("/api/zones/<zone_id>", methods=["DELETE"])
def api_delete_zone(zone_id):
    if not session.get("authenticated") and not request.headers.get("X-API-Key"):
        return jsonify({"error": "Unauthorized"}), 401
    delete_custom_zone(zone_id)
    log_audit(session.get("user", "admin"), "ZONE_DELETED", f"Zone {zone_id} deleted")
    return jsonify({"status": "deleted", "zone_id": zone_id})

# ──────────────────────────────────────────────
# PHASE 5: MULTI-CAMERA & MAP API
# ──────────────────────────────────────────────
@app.route("/api/cameras")
def api_cameras():
    if not session.get("authenticated") and not request.headers.get("X-API-Key"):
        return jsonify({"error": "Unauthorized"}), 401
    with state_lock:
        los = shared_state.get("lane_los", {}).get("1", "B")
    return jsonify({
        "active_camera": camera_manager.active_camera_id,
        "cameras": camera_manager.get_cameras_list(current_los=los)
    })

@app.route("/api/cameras/select", methods=["POST"])
def api_select_camera():
    if not session.get("authenticated") and not request.headers.get("X-API-Key"):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json() or {}
    cid = data.get("camera_id", "cam1")
    if camera_manager.set_active_camera(cid):
        with state_lock:
            shared_state["active_camera"] = cid
        log_audit(session.get("user", "admin"), "CAMERA_SWITCH", f"Active feed switched to {cid}")
        return jsonify({"status": "success", "active_camera": cid})
    return jsonify({"error": "Camera not found"}), 404

# ──────────────────────────────────────────────
# PHASE 6: SIGNALS AI & STRATEGY BENCHMARKING
# ──────────────────────────────────────────────
@app.route("/api/signals/status")
def api_signals_status():
    if not session.get("authenticated") and not request.headers.get("X-API-Key"):
        return jsonify({"error": "Unauthorized"}), 401
    with state_lock:
        sig = dict(shared_state.get("signal_status", {}))
        mode = shared_state.get("signal_mode", "adaptive")
    return jsonify({"mode": mode, "status": sig})

@app.route("/api/signals/strategy", methods=["POST"])
def api_signals_strategy():
    if not session.get("authenticated") and not request.headers.get("X-API-Key"):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json() or {}
    strategy = data.get("strategy", "adaptive").lower()
    with state_lock:
        shared_state["signal_mode"] = strategy
    log_audit(session.get("user", "admin"), "SIGNAL_STRATEGY_CHANGED", f"Signal mode updated to {strategy}")
    return jsonify({"status": "success", "strategy": strategy})

# ──────────────────────────────────────────────
# EMERGENCY VEHICLE PRIORITY CORRIDOR
# ──────────────────────────────────────────────
@app.route("/emergency")
def emergency_page():
    if not session.get("authenticated"):
        return redirect(url_for("home"))
    return render_template_string(EMERGENCY_HTML)

@app.route("/api/emergency/stats")
def api_emergency_stats():
    with state_lock:
        active_p = bool(shared_state.get("emergency_active", False))
        active_lane = shared_state.get("emergency_lane")
        active_veh = shared_state.get("emergency_vehicle_type", "Ambulance")
        sig = dict(shared_state.get("signal_status", {}))
    
    stats = get_emergency_statistics()
    recent = get_emergency_transits(limit=30)
    return jsonify({
        "active_preemption": active_p,
        "active_lane": active_lane,
        "active_vehicle_type": active_veh,
        "signal_status": sig,
        "stats": stats,
        "recent_transits": recent
    })

@app.route("/api/emergency/trigger", methods=["POST"])
def api_emergency_trigger():
    data = request.get_json() or {}
    v_type = data.get("vehicle_type", "Ambulance")
    lane_id = int(data.get("lane_id", 1))
    speed = float(data.get("speed_kmh", 65.0))
    duration = float(data.get("duration_seconds", 35.0))
    
    with state_lock:
        # Determine prior signal state for this lane
        sig = shared_state.get("signal_status", {})
        lane_states = sig.get("lane_states", {})
        prior_state = lane_states.get(lane_id, {}).get("color", "RED")

        # 1. Update shared state
        shared_state["emergency_active"] = True
        shared_state["emergency_lane"] = lane_id
        shared_state["emergency_vehicle_type"] = v_type
        shared_state["emergency_override_until"] = time.time() + duration

        # 2. Preempt signal: override this lane from RED to GREEN!
        new_states = {}
        for l in (1, 2):
            if l == lane_id:
                new_states[l] = {"color": "GREEN", "remaining_s": int(duration)}
            else:
                new_states[l] = {"color": "RED", "remaining_s": int(duration + 15)}
        
        sig["active_green_lane"] = lane_id
        sig["remaining_s"] = int(duration)
        sig["total_duration_s"] = int(duration)
        sig["lane_states"] = new_states
        sig["emergency_corridor"] = True
        shared_state["signal_status"] = sig

    # 3. Log to SQLite
    e_id = log_emergency_transit(
        vehicle_type=v_type,
        lane_id=lane_id,
        speed_kmh=speed,
        prior_signal_state=prior_state,
        new_signal_state="GREEN (Preempted)",
        duration_seconds=duration,
        status="Corridor Cleared"
    )

    # 4. Dispatch Alert Toast
    AlertDispatcher.dispatch(
        severity="critical",
        category="ambulance",
        title=f"🚨 {v_type} Priority Preemption Active",
        message=f"Signal in Lane {lane_id} overridden: {prior_state} ➔ GREEN to give immediate way!"
    )
    log_audit(session.get("user", "admin"), "EMERGENCY_PREEMPTION", f"{v_type} preemption in Lane {lane_id} (Signal: {prior_state} -> GREEN)")

    return jsonify({
        "status": "preempted",
        "id": e_id,
        "vehicle_type": v_type,
        "lane_id": lane_id,
        "prior_signal": prior_state,
        "new_signal": "GREEN"
    })

@app.route("/api/emergency/clear", methods=["POST"])
def api_emergency_clear():
    with state_lock:
        shared_state["emergency_active"] = False
        shared_state["emergency_lane"] = None
        shared_state["emergency_override_until"] = 0
        sig = shared_state.get("signal_status", {})
        sig["emergency_corridor"] = False
        shared_state["signal_status"] = sig
    
    log_audit(session.get("user", "admin"), "EMERGENCY_CLEARED", "Emergency corridor cleared, normal signal cycle resumed.")
    return jsonify({"status": "cleared"})

# ──────────────────────────────────────────────
# PHASE 7: AUDIT LOGS & OPENAPI DOCS
# ──────────────────────────────────────────────
@app.route("/api/audit")
def api_audit():
    if not session.get("authenticated") and not request.headers.get("X-API-Key"):
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(get_audit_logs(limit=40))

@app.route("/api/control/update", methods=["POST"])
def update_controls():
    if not session.get("authenticated") and not request.headers.get("X-API-Key"):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json() or {}
    user = session.get("user", "admin")
    with state_lock:
        if "mode" in data:
            shared_state["mode"] = str(data["mode"])
        if "speed_limit" in data:
            shared_state["speed_limit"] = int(data["speed_limit"])
        if "incident_timeout" in data:
            shared_state["incident_timeout"] = float(data["incident_timeout"])
        if "conf_threshold" in data:
            shared_state["conf_threshold"] = float(data["conf_threshold"])
        if "signal_mode" in data:
            shared_state["signal_mode"] = str(data["signal_mode"])
            
    log_audit(user, "CONFIG_UPDATED", json.dumps(data))
    return jsonify({"status": "success", "settings": data})

@app.route("/api/settings", methods=["GET", "POST"])
def api_settings():
    if not session.get("authenticated") and not request.headers.get("X-API-Key"):
        return jsonify({"error": "Unauthorized"}), 401
    
    username = session.get("user", "admin")
    if request.method == "POST":
        data = request.get_json() or {}
        with state_lock:
            if "conf_threshold" in data:
                shared_state["conf_threshold"] = float(data["conf_threshold"])
            if "speed_limit" in data:
                shared_state["speed_limit"] = int(data["speed_limit"])
            if "incident_timeout" in data:
                shared_state["incident_timeout"] = float(data["incident_timeout"])
            if "signal_mode" in data:
                shared_state["signal_mode"] = str(data["signal_mode"])
            if "mode" in data:
                shared_state["mode"] = str(data["mode"])
        
        save_user_settings(username, data)
        log_audit(username, "SETTINGS_SAVED", "User configuration profile saved")
        return jsonify({"status": "saved", "settings": data})

    saved = get_user_settings(username)
    with state_lock:
        current = {
            "mode": shared_state.get("mode", "lanes"),
            "conf_threshold": shared_state.get("conf_threshold", 0.25),
            "speed_limit": shared_state.get("speed_limit", 50),
            "incident_timeout": shared_state.get("incident_timeout", 5.0),
            "signal_mode": shared_state.get("signal_mode", "adaptive"),
            "fps_target": 25,
            "lane_1_speed_limit": 50,
            "lane_2_speed_limit": 50,
            "telegram_alerts": True,
            "whatsapp_alerts": False,
            "retention_days": 30,
            "api_key": "traffiq_live_secret_key_2026",
            "enforcement_red_light": True,
            "enforcement_wrong_way": True,
            "enforcement_helmet": True,
            "enforcement_parking": True,
            "enforcement_jaywalk": True,
            "enforcement_green_wave": True,
            "enforcement_weather": True
        }
    current.update(saved)
    return jsonify(current)

@app.route("/api/database/cleanup", methods=["POST"])
def api_database_cleanup():
    if not session.get("authenticated") and not request.headers.get("X-API-Key"):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json() or {}
    days = int(data.get("days", 30))
    run_db_cleanup(retention_days=days)
    log_audit(session.get("user", "admin"), "DB_CLEANUP", f"Database pruned (older than {days} days)")
    return jsonify({"status": "cleaned", "retention_days": days})

@app.route("/api/docs")
def swagger_ui():
    """Interactive Swagger/OpenAPI documentation page."""
    html = """<!DOCTYPE html>
<html>
<head>
  <title>TraffiQ REST API &mdash; Swagger Docs</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css" />
</head>
<body style="margin:0;background:#06040c">
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
  <script>
    window.onload = () => {
      SwaggerUIBundle({
        url: '/openapi.json',
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [SwaggerUIBundle.presets.apis],
      });
    };
  </script>
</body>
</html>"""
    return html

@app.route("/openapi.json")
def openapi_spec():
    """OpenAPI 3.0 specification for TraffiQ."""
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "TraffiQ Real-Time Traffic & Enforcement API",
            "version": "2.5.0",
            "description": "Production REST API for automated vehicle detection, violation logs, and adaptive signal coordination."
        },
        "paths": {
            "/api/stats": { "get": { "summary": "Real-time telemetry feed" } },
            "/api/violations": { "get": { "summary": "Query traffic violations with plate linkage" } },
            "/api/alerts": { "get": { "summary": "Active real-time alert notifications" } },
            "/api/analytics/historical": { "get": { "summary": "Historical query density analytics" } },
            "/api/cameras": { "get": { "summary": "Multi-camera registry and GIS status" } },
            "/api/signals/status": { "get": { "summary": "Adaptive traffic light signal timing status" } },
            "/api/control/update": { "post": { "summary": "Live parameter configuration update" } },
            "/api/emergency/stats": { "get": { "summary": "Live emergency corridor statistics and transits" } },
            "/api/emergency/trigger": { "post": { "summary": "Dispatch emergency vehicle and preempt red light to green" } },
            "/api/emergency/clear": { "post": { "summary": "Clear emergency priority corridor" } }
        }
    }
    return jsonify(spec)

def run_flask():
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)
    app.run(host="0.0.0.0", port=FLASK_PORT, debug=False, use_reloader=False)
