"""
TraffiQ — Neural Traffic Analysis & Autonomous Signal Control Platform
======================================================================
Complete Implementation of Phases 1 to 7:
  1. ByteTrack multi-object tracking (MOT)
  2. Red-light, wrong-way, no-helmet, triple-riding, illegal parking, & jaywalking enforcement
  3. Automatic license plate recognition (LPR) & evidence clipping
  4. Environmental visibility / weather analysis & adaptive confidence adjustment
  5. Vehicle classification breakdown (Cars, Buses, Trucks, Bikes, Autos, Pedestrians)
  6. Actuated & AI-adaptive traffic signal control with arterial green-wave & emergency cascade
  7. Multi-step 15m/30m/60m congestion forecasting
  8. SQLite database audit logs & telemetry persistence
  9. Real-time Flask dashboard with 3D glassmorphic control center
"""

import os
os.environ.setdefault("YOLO_CONFIG_DIR", "/tmp/ultralytics")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
import cv2
import numpy as np
import time
from datetime import datetime
from collections import defaultdict, deque
import threading
import webbrowser
from math import hypot

import torch
from ultralytics import YOLO
import supervision as sv

# Imports from modular architecture
from config import (
    VIDEO_PATH, MODEL_NAME, CONF_THRESHOLD, TRACK_CLASSES,
    PIXEL_TO_METER, SPEED_LIMIT_KMPH, SPEEDER_LOG_FILE,
    EMERGENCY_CLASSES, EMERGENCY_SPEED_KMH, LOG_FILE, FLASK_PORT,
    RED_LIGHT_ENFORCEMENT, WRONG_WAY_DETECTION, HELMET_DETECTION,
    ILLEGAL_PARKING_DETECTION, PEDESTRIAN_JAYWALKING_DETECTION,
    WEATHER_ADAPT_ENABLED, SIGNAL_MODE
)
from state import shared_state, state_lock, history_buf, session_stats
from loggers import CSVLogger, SpeedCameraLogger
from analytics import (
    IncidentDetector, LaneTrendTracker, TrafficPredictor,
    FlowRateTracker, los_grade, _SKLEARN_OK
)
from database import log_traffic_frame, log_emergency_transit
from violations import ViolationManager
from weather import WeatherAnalyzer
from signals_ai import SignalController, CongestionForecaster
from web_app import run_flask

# ──────────────────────────────────────────────
# ROI SELECTOR
# ──────────────────────────────────────────────
lanes = []
drawing, ix, iy = False, -1, -1
selecting = True
frame = None

def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing, lanes, frame
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing, ix, iy = True, x, y
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        lanes.append((min(ix, x), min(iy, y), max(ix, x), max(iy, y)))
        print(f"Lane {len(lanes)} set: {lanes[-1]}")

def detect_hardware():
    """Detects neural hardware acceleration."""
    if torch.cuda.is_available():
        return {"device": "NVIDIA CUDA GPU", "acceleration": "Active", "model": "YOLOv8 Nano"}
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return {"device": "Apple Silicon Neural Engine (MPS)", "acceleration": "Active", "model": "YOLOv8 Nano"}
    return {"device": "Multi-core CPU", "acceleration": "Standard", "model": "YOLOv8 Nano"}

def main():
    global lanes, drawing, ix, iy, selecting, frame
    
    cap = cv2.VideoCapture(VIDEO_PATH)
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read video. Make sure Traffic_Video.mp4 exists.")
        cap.release()
        exit()

    try:
        cv2.namedWindow("ROI Selector")
        cv2.setMouseCallback("ROI Selector", draw_rectangle)
        print("Draw lane boxes with the mouse. Press ENTER when done (or wait 3s for auto-lanes).")
        start_wait = time.time()
        while selecting:
            display = frame.copy()
            for i, (x1, y1, x2, y2) in enumerate(lanes, 1):
                cv2.rectangle(display, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(display, f"Lane {i}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            cv2.imshow("ROI Selector", display)
            k = cv2.waitKey(100) & 0xFF
            if k == 13: selecting = False
            elif k == ord("q"): cap.release(); exit()
            if time.time() - start_wait > 3.0 and len(lanes) == 0:
                print("[INFO] Auto-proceeding with default lanes...")
                selecting = False
        cv2.destroyWindow("ROI Selector")
    except Exception as e:
        print(f"[INFO] GUI unavailable or auto-skipped ({e}). Using default lanes.")
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    if not lanes:
        h, w = frame.shape[:2]
        lanes = [
            (0, 0, w // 2, h),
            (w // 2, 0, w, h)
        ]
        print(f"[INFO] No custom lanes drawn. Auto-configured 2-lane default layout: {lanes}")

    # Instantiate ML predictor & intelligence engines
    num_lanes = len(lanes)
    predictor = TrafficPredictor(lane_ids=list(range(1, num_lanes + 1)))
    v_manager = ViolationManager()
    v_manager.update_stop_lines(lanes)
    weather_analyzer = WeatherAnalyzer()
    signal_controller = SignalController(num_lanes=num_lanes)
    forecaster = CongestionForecaster()
    hw_info = detect_hardware()

    with state_lock:
        shared_state["hardware_info"] = hw_info

    # ──────────────────────────────────────────────
    # INIT TRACKING + TOOLS
    # ──────────────────────────────────────────────
    model = YOLO(MODEL_NAME)
    tracker = sv.ByteTrack()

    incident_detector = IncidentDetector()
    trend_tracker = LaneTrendTracker()
    logger = CSVLogger(LOG_FILE)
    speeder_logger = SpeedCameraLogger(SPEEDER_LOG_FILE)

    speed_history = defaultdict(lambda: deque(maxlen=8))
    heatmap = np.zeros((int(cap.get(4)), int(cap.get(3))), dtype=np.float32)
    flow_tracker = FlowRateTracker()
    vehicle_last_lane: dict = {}
    
    mode = "lanes"
    frame_id = 0
    fps_timer = time.time()

    # ──────────────────────────────────────────────
    # START FLASK IN BACKGROUND
    # ──────────────────────────────────────────────
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print(f"📊 Live dashboard → http://localhost:{FLASK_PORT}")
    def _open_browser():
        try:
            webbrowser.open(f"http://localhost:{FLASK_PORT}")
        except Exception:
            pass
    threading.Timer(1.5, _open_browser).start()

    # ──────────────────────────────────────────────
    # HELPER: lane for a centroid
    # ──────────────────────────────────────────────
    def get_lane(cx, cy):
        for i, (lx1, ly1, lx2, ly2) in enumerate(lanes, 1):
            if lx1 <= cx <= lx2 and ly1 <= cy <= ly2:
                return i
        return None

    # ──────────────────────────────────────────────
    # MAIN PIPELINE LOOP
    # ──────────────────────────────────────────────
    while True:
        ret, frame = cap.read()
        if not ret:
            # End of video — seamlessly loop back to start
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()
            if not ret:
                cap.release()
                cap = cv2.VideoCapture(VIDEO_PATH)
                ret, frame = cap.read()
                if not ret:
                    print("[DEBUG] Could not re-read video frame after loop reset. Exiting.")
                    break
        frame_id += 1
        t_frame_start = time.time()

        # ── FPS & Latency ──
        now = time.time()
        fps = 1.0 / max(now - fps_timer, 1e-9)
        fps_timer = now

        # Maintain rolling evidence buffer
        v_manager.push_frame(frame)

        # ── WEATHER & ENVIRONMENTAL ADAPTATION ──
        weather_info = weather_analyzer.analyze_frame(frame)

        # ── LOAD DYNAMIC CONTROLS FROM SHARED STATE ──
        with state_lock:
            mode = shared_state["mode"]
            speed_limit = shared_state["speed_limit"]
            incident_timeout = shared_state["incident_timeout"]
            conf_threshold = shared_state["conf_threshold"]
            current_signal_strategy = shared_state.get("signal_mode", "adaptive")
            signal_controller.set_strategy(current_signal_strategy)

        # Auto-adjust threshold if weather compensation is enabled
        effective_conf = weather_info["recommended_conf"] if WEATHER_ADAPT_ENABLED else conf_threshold

        # ── YOLO DETECT (Includes Vehicles + Pedestrians) ──
        t_infer_start = time.time()
        results = model(frame, conf=effective_conf, verbose=False)[0]
        inference_latency_ms = round((time.time() - t_infer_start) * 1000, 1)

        # Filter to tracked classes
        vehicle_mask = np.array([
            model.names[int(c)] in TRACK_CLASSES
            for c in results.boxes.cls
        ], dtype=bool)

        if vehicle_mask.any():
            filtered = results.boxes[vehicle_mask]
            sv_dets = sv.Detections(
                xyxy=filtered.xyxy.cpu().numpy(),
                confidence=filtered.conf.cpu().numpy(),
                class_id=filtered.cls.cpu().numpy().astype(int),
            )
        else:
            sv_dets = sv.Detections.empty()

        # ── BYTETRACK ──
        tracked = tracker.update_with_detections(sv_dets)

        # ── PER-FRAME ACCUMULATORS ──
        lane_counts = {i + 1: {"car": 0, "bus": 0, "truck": 0, "motorbike": 0, "pedestrian": 0} for i in range(num_lanes)}
        active_ids = set()
        active_incidents = []
        frame_speeders = []
        frame_wrong_way = set()
        current_centroids = {}
        all_box_tuples = []
        emergency_lane_this_frame = None

        # Live Vehicle Class Breakdown
        class_breakdown = {"car": 0, "bus": 0, "truck": 0, "motorbike": 0, "auto": 0, "pedestrian": 0}

        # ── FIRST PASS: COLLECT BOUNDING BOXES & CENTROIDS ──
        for i in range(len(tracked)):
            x1, y1, x2, y2 = map(int, tracked.xyxy[i])
            track_id = int(tracked.tracker_id[i])
            cls_id = int(tracked.class_id[i])
            label = model.names[cls_id]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            current_centroids[track_id] = (cx, cy)
            all_box_tuples.append(((x1, y1, x2, y2), label))
            active_ids.add(track_id)

            # Class breakdown tally
            if label == "person":
                class_breakdown["pedestrian"] += 1
            elif label in class_breakdown:
                class_breakdown[label] += 1
            else:
                class_breakdown["car"] += 1

        # ── EMERGENCY CORRIDOR CHECK (Vision or Web Console) ──
        with state_lock:
            state_em_lane = shared_state.get("emergency_lane")
            override_until = shared_state.get("emergency_override_until", 0)
        
        effective_em_lane = None
        if state_em_lane and (override_until == 0 or time.time() < override_until):
            effective_em_lane = state_em_lane
        elif emergency_lane_this_frame is not None:
            effective_em_lane = emergency_lane_this_frame

        # ── COMPUTE SIGNALS AI CYCLE ──
        predicted_lane_counts = {i: predictor.predict(i) for i in range(1, num_lanes + 1)}
        signal_status = signal_controller.compute_cycle(
            lane_counts=lane_counts,
            predicted_counts=predicted_lane_counts,
            emergency_lane=effective_em_lane,
            current_time=now
        )

        # ── SECOND PASS: SPEED, TRACKING, AND VIOLATIONS ──
        for i in range(len(tracked)):
            x1, y1, x2, y2 = map(int, tracked.xyxy[i])
            track_id = int(tracked.tracker_id[i])
            cls_id = int(tracked.class_id[i])
            label = model.names[cls_id]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            bbox = (x1, y1, x2, y2)

            lane_id = get_lane(cx, cy)
            if lane_id:
                vehicle_last_lane[track_id] = lane_id
            else:
                lane_id = vehicle_last_lane.get(track_id)

            # Lane counts
            if lane_id:
                if label == "person":
                    lane_counts[lane_id]["pedestrian"] += 1
                elif label in lane_counts[lane_id]:
                    lane_counts[lane_id][label] += 1

            # Speed calculation (pixels/sec → km/h)
            speed_history[track_id].append((cx, cy, time.time()))
            speed_kmh = 0.0
            if len(speed_history[track_id]) >= 2:
                p1 = speed_history[track_id][0]
                p2 = speed_history[track_id][-1]
                dt = p2[2] - p1[2]
                if dt > 0:
                    dist_px = hypot(p2[0] - p1[0], p2[1] - p1[1])
                    speed_kmh = (dist_px * PIXEL_TO_METER / dt) * 3.6

            # Emergency vehicle trigger from live camera feed
            if label in EMERGENCY_CLASSES and speed_kmh > EMERGENCY_SPEED_KMH and lane_id:
                emergency_lane_this_frame = lane_id
                if not shared_state.get("emergency_active"):
                    with state_lock:
                        shared_state["emergency_active"] = True
                        shared_state["emergency_lane"] = lane_id
                        shared_state["emergency_vehicle_type"] = "Ambulance" if label == "bus" else "Fire Truck"
                        shared_state["emergency_override_until"] = time.time() + 25.0
                    try:
                        log_emergency_transit(
                            vehicle_type="Ambulance" if label == "bus" else "Fire Truck",
                            lane_id=lane_id,
                            speed_kmh=round(speed_kmh, 1),
                            prior_signal_state="RED",
                            new_signal_state="GREEN (Preempted)",
                            duration_seconds=25.0,
                            status="Corridor Cleared"
                        )
                    except Exception:
                        pass

            # Signal color for this lane
            lane_state = signal_status["lane_states"].get(lane_id, {})
            is_lane_red = lane_state.get("color") == "RED"
            is_lane_green = lane_state.get("color") == "GREEN"

            # ── PHASE 1 & 2: VIOLATION CHECKS ──
            if label != "person":
                # 1. Red Light Violation
                if RED_LIGHT_ENFORCEMENT and lane_id:
                    v_manager.check_red_light(
                        track_id, cx, cy, lane_id, is_lane_red,
                        frame, bbox, speed_kmh, label
                    )

                # 2. Wrong Way Driving
                if WRONG_WAY_DETECTION and lane_id:
                    v_ww = v_manager.check_wrong_way(
                        track_id, cx, cy, lane_id,
                        frame, bbox, speed_kmh, label
                    )
                    if v_ww:
                        frame_wrong_way.add(track_id)

                # 3. Helmet & Triple Riding
                if HELMET_DETECTION:
                    v_manager.check_two_wheeler_violations(
                        track_id, frame, bbox, lane_id, speed_kmh, label,
                        all_boxes=all_box_tuples
                    )

                # 4. Illegal Parking / Lane Blocking
                if ILLEGAL_PARKING_DETECTION:
                    v_manager.check_illegal_parking(
                        track_id, cx, cy, lane_id, speed_kmh, frame, bbox,
                        label, is_lane_green=is_lane_green
                    )

            else:
                # 5. Pedestrian Jaywalking
                if PEDESTRIAN_JAYWALKING_DETECTION and lane_id:
                    v_manager.check_jaywalking(
                        track_id, cx, cy, lane_id, frame, bbox,
                        is_veh_green=is_lane_green
                    )

            # ── SPEED CAMERA ──
            if speed_kmh > speed_limit and label != "person":
                event = speeder_logger.log(frame_id, track_id, lane_id, speed_kmh, label)
                if event:
                    frame_speeders.append(event)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 220), 3)
                cv2.rectangle(frame, (x1, max(0, y1 - 28)), (x1 + 220, max(0, y1)), (0, 0, 220), -1)
                cv2.putText(frame, f"SPEEDING {int(speed_kmh)} km/h", (x1 + 4, max(0, y1 - 8)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.58, (255, 255, 255), 2)

            # Incident detection (Stopped vehicle)
            is_incident = lane_id and label != "person" and incident_detector.update(track_id, cx, cy, lane_id, timeout=incident_timeout)
            if is_incident:
                still_since = incident_detector.history[track_id]["still_since"]
                duration = round(time.time() - still_since, 1)
                active_incidents.append({
                    "track_id": track_id, "lane": lane_id,
                    "cx": cx, "cy": cy, "duration": duration
                })
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                cv2.putText(frame, f"INCIDENT! {duration}s", (x1, max(0, y1 - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            elif speed_kmh <= speed_limit:
                color = (0, 255, 0) if label != "person" else (255, 200, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                txt = f"ID{track_id} {int(speed_kmh)}km/h" if speed_kmh > 2 else f"ID{track_id} {label}"
                cv2.putText(frame, txt, (x1, max(0, y1 - 8)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.52, color, 2)

            # Flow rate recording
            if lane_id and label != "person":
                flow_tracker.record(lane_id, track_id)

            # Heatmap update
            cv2.circle(heatmap, (cx, cy), 12, 1, -1)

            # Lane label on vehicle
            if lane_id:
                cv2.putText(frame, f"L{lane_id}", (cx, cy),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Store centroid history for velocity and heading calculations
        v_manager.post_frame_update(current_centroids)
        incident_detector.cleanup(active_ids)
        total_vehicles = sum(sum(c.values()) for c in lane_counts.values())

        # ── CONGESTION FORECASTING RECORD ──
        forecaster.record_volume({i: sum(c.values()) for i, c in lane_counts.items()})

        # ── SESSION STATS & SNAPSHOTS ──
        session_stats["all_ids"].update(active_ids)
        session_stats.violations_count = len(v_manager.recent_violations)
        if total_vehicles > session_stats["peak_count"]:
            session_stats["peak_count"] = total_vehicles
            session_stats["peak_time"] = datetime.now().strftime("%H:%M:%S")

        # Snapshot every ~3 seconds (90 frames)
        if frame_id % 90 == 0:
            history_buf.append({
                "t": datetime.now().strftime("%H:%M:%S"),
                "lanes": {str(k): sum(v.values()) for k, v in lane_counts.items()}
            })
            for _lid, _cnts in lane_counts.items():
                predictor.update(_lid, sum(_cnts.values()))

        lane_los_out = {str(k): los_grade(sum(v.values()))[0] for k, v in lane_counts.items()}
        lane_flow_out = {str(k): flow_tracker.rate(k) for k in lane_counts}

        # Trend tracker
        for lane_id, counts in lane_counts.items():
            trend_tracker.update(lane_id, sum(counts.values()))

        # ── MODES OVERLAYS ──
        if mode == "lanes":
            for i, (lx1, ly1, lx2, ly2) in enumerate(lanes, 1):
                total = sum(lane_counts[i].values())
                color = (0, 255, 0) if total < 5 else (0, 255, 255) if total < 15 else (0, 0, 255)
                cv2.rectangle(frame, (lx1, ly1), (lx2, ly2), color, 2)
                cv2.putText(frame, f"Lane {i} ({total})", (lx1 + 5, ly1 + 22),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2)

                # Draw Stop Line on Lane
                if i in v_manager.stop_lines:
                    stop_y = v_manager.stop_lines[i]
                    cv2.line(frame, (lx1, stop_y), (lx2, stop_y), (0, 0, 255), 2)
                    cv2.putText(frame, "STOP LINE", (lx1 + 5, stop_y - 6),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1)

        elif mode == "heatmap":
            blur = cv2.GaussianBlur(heatmap, (0, 0), 25)
            norm = cv2.normalize(blur, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            colored = cv2.applyColorMap(norm, cv2.COLORMAP_JET)
            frame = cv2.addWeighted(frame, 0.55, colored, 0.45, 0)

        elif mode == "speed":
            for i in range(len(tracked)):
                track_id = int(tracked.tracker_id[i])
                x1, y1, x2, y2 = map(int, tracked.xyxy[i])
                history = speed_history[track_id]
                if len(history) >= 2:
                    p1, p2 = history[0], history[-1]
                    dt = p2[2] - p1[2]
                    if dt > 0:
                        speed = (hypot(p2[0] - p1[0], p2[1] - p1[1]) * PIXEL_TO_METER / dt) * 3.6
                        color = (0, 255, 0) if speed < 40 else (0, 165, 255) if speed < 80 else (0, 0, 255)
                        cv2.putText(frame, f"{int(speed)} km/h", (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        elif mode == "timer":
            # Signal visual overlay
            active_green = signal_status["active_green_lane"]
            rem_s = signal_status["remaining_s"]
            for i, (lx1, ly1, lx2, ly2) in enumerate(lanes, 1):
                lane_total = sum(lane_counts[i].values())
                trend_arrow = trend_tracker.label_ascii(i)
                if i == active_green:
                    cv2.rectangle(frame, (lx1, ly1), (lx2, ly2), (0, 255, 0), 4)
                    cv2.putText(frame, f"GO ({rem_s}s) [{lane_total}v] {trend_arrow}",
                                (lx1 + 10, ly1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                else:
                    cv2.rectangle(frame, (lx1, ly1), (lx2, ly2), (0, 0, 220), 2)
                    cv2.putText(frame, f"RED (~{rem_s + 15}s) [{lane_total}v] {trend_arrow}",
                                (lx1 + 10, ly1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 220), 2)

        # ── INCIDENT OVERLAYS ──
        for inc in active_incidents:
            cv2.putText(frame, f"[!] INCIDENT L{inc['lane']}", (20, frame.shape[0] - 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # ── TOP HUD BAR ──
        dash_url = f"http://localhost:{FLASK_PORT}"
        if effective_em_lane:
            em_veh = shared_state.get("emergency_vehicle_type", "EMERGENCY VEHICLE")
            hud_text = f"*** {em_veh.upper()} DETECTED - PREEMPTION ACTIVE: LANE {effective_em_lane} OVERRIDDEN TO GREEN ***"
            hud_bar = np.zeros((46, frame.shape[1], 3), dtype=np.uint8)
            hud_bar[:] = (20, 20, 160)  # High-contrast red bar
            cv2.putText(hud_bar, hud_text, (14, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.56, (255, 255, 255), 2)
        else:
            hud_text = f"MODE: {mode.upper()} | Strategy: {signal_status['strategy'].upper()} | Weather: {weather_info['condition']} | FPS: {fps:.1f} | Latency: {inference_latency_ms}ms"
            hud_bar = np.zeros((46, frame.shape[1], 3), dtype=np.uint8)
            cv2.putText(hud_bar, hud_text, (14, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 1)
        frame = np.vstack((hud_bar, frame))

        # ── MULTI-STEP CONGESTION FORECASTS ──
        f15 = {str(i): forecaster.forecast(i)["15m"] for i in range(1, num_lanes + 1)}
        f30 = {str(i): forecaster.forecast(i)["30m"] for i in range(1, num_lanes + 1)}
        f60 = {str(i): forecaster.forecast(i)["60m"] for i in range(1, num_lanes + 1)}

        # ── UPDATE THREAD-SAFE SHARED STATE ──
        with state_lock:
            shared_state["lane_counts"] = {str(k): dict(v) for k, v in lane_counts.items()}
            shared_state["vehicle_count"] = total_vehicles
            shared_state["incidents"] = active_incidents
            shared_state["fps"] = round(fps, 1)
            shared_state["latency_ms"] = inference_latency_ms
            shared_state["frame_id"] = frame_id
            shared_state["emergency_active"] = emergency_lane_this_frame is not None
            shared_state["emergency_lane"] = emergency_lane_this_frame
            shared_state["lane_trends"] = {str(k): trend_tracker.label(k) for k in lane_counts}
            shared_state["lane_los"] = lane_los_out
            shared_state["lane_flow"] = lane_flow_out
            shared_state["lane_predictions"] = {str(k): round(predictor.predict(k), 1) for k in lane_counts}
            shared_state["ml_ready"] = predictor.is_ready()
            shared_state["violations"] = list(v_manager.recent_violations)
            shared_state["vehicle_classes"] = class_breakdown
            shared_state["pedestrians_count"] = class_breakdown["pedestrian"]
            shared_state["weather_condition"] = weather_info["condition"]
            shared_state["weather_score"] = weather_info["visibility_score"]
            shared_state["signal_status"] = signal_status
            shared_state["forecast_15m"] = f15
            shared_state["forecast_30m"] = f30
            shared_state["forecast_60m"] = f60

            if frame_speeders:
                shared_state["speeders"] = (shared_state["speeders"] + frame_speeders)[-10:]
                session_stats.speeders_count += len(frame_speeders)

        # ── LOG TO CSV & SQLITE EVERY 30 FRAMES ──
        if frame_id % 30 == 0:
            logger.log(frame_id, lane_counts, active_incidents)
            log_traffic_frame(frame_id, lane_counts, active_incidents, lane_los_out, lane_flow_out)

        # ── DISPLAY ──
        try:
            cv2.imshow("Traffic Analysis [L/H/S/T] Q=quit", frame)
            key = cv2.waitKey(30) & 0xFF
            if key == ord("l"):
                with state_lock: shared_state["mode"] = "lanes"
            elif key == ord("h"):
                with state_lock: shared_state["mode"] = "heatmap"
            elif key == ord("s"):
                with state_lock: shared_state["mode"] = "speed"
            elif key == ord("t"):
                with state_lock: shared_state["mode"] = "timer"
            elif key in (ord("q"), ord("Q"), 27):
                print(f"[DEBUG] Quit key detected: {key}. Exiting loop.")
                break
        except cv2.error:
            time.sleep(0.03)

    cap.release()
    cv2.destroyAllWindows()

    heatmap_norm = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    cv2.imwrite("heatmap_export.png", cv2.applyColorMap(heatmap_norm, cv2.COLORMAP_JET))

    # ──────────────────────────────────────────────
    # SESSION SUMMARY
    # ──────────────────────────────────────────────
    duration_s = (datetime.now() - datetime.fromisoformat(session_stats["session_start"])).seconds
    print()
    print("═" * 58)
    print("  🚦  TRAFFIC PLATFORM SESSION SUMMARY")
    print("═" * 58)
    print(f"  Started         : {session_stats['session_start']}")
    print(f"  Duration        : {duration_s // 60}m {duration_s % 60}s")
    print(f"  Total vehicles  : {len(session_stats['all_ids'])} unique IDs")
    print(f"  Peak traffic    : {session_stats['peak_count']} vehicles at {session_stats['peak_time']}")
    print(f"  Incidents       : {session_stats['total_incidents']}")
    print(f"  Violations      : {session_stats.violations_count}")
    print(f"  Speeders        : {session_stats.speeders_count}")
    print(f"  Database        : traffiq.db")
    print(f"  Heatmap         : heatmap_export.png")
    print("═" * 58)
    print()

    session_stats.session_ended = True

if __name__ == "__main__":
    main()
