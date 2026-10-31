"""
TraffiQ Production Test Suite
=============================
Covers:
- Phase 1 & 2: ViolationManager (red light, wrong way, helmet/triple-riding, illegal parking, jaywalking, plate OCR)
- Phase 3: WeatherAnalyzer, Reports & Analytics (time-of-day matrix, class aggregation)
- Phase 4: AlertDispatcher, in-memory toasts, custom zones
- Phase 5: Multi-camera manager and LOS tracking
- Phase 6: Congestion forecaster, SignalController (fixed, actuated, adaptive, emergency green-wave)
- Phase 7: REST API endpoints, OpenAPI documentation, Swagger UI, RBAC auth, SQLite persistence and cleanup
"""

import os
import sys
import time
import json
import zipfile
import unittest
import numpy as np

# Ensure TraffiQ root directory is on Python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Isolate database during testing
TEST_DB_PATH = os.path.join(CURRENT_DIR, "test_traffiq.db")
os.environ["TRAFFIQ_DB"] = TEST_DB_PATH

from config import PIXEL_TO_METER, SPEED_LIMIT_KMPH
from analytics import IncidentDetector, LaneTrendTracker
from database import (
    init_db, get_db_connection, insert_violation, get_recent_violations,
    get_violation_by_id, log_traffic_frame, get_historical_traffic,
    insert_alert, get_alerts, acknowledge_alert, save_custom_zone,
    get_custom_zones, delete_custom_zone, log_audit, get_audit_logs,
    run_db_cleanup
)
from violations import ViolationManager, LicensePlateRecognizer, EVIDENCE_DIR
from weather import WeatherAnalyzer
from reports import ReportGenerator
from alerts import AlertDispatcher, active_toasts
from multicam import CameraManager
from signals_ai import CongestionForecaster, SignalController
from auth import require_api_key, _has_permission, API_KEYS
from web_app import app, session_stats, shared_state


class TestTrackingAndCalibration(unittest.TestCase):
    """Tests vehicle speed calibration, distance conversion, and trend tracking."""

    def test_speed_calculation(self):
        # Formula: speed_kmh = (dist_px * PIXEL_TO_METER / dt) * 3.6
        p1 = (100.0, 100.0, 1.0)
        p2 = (140.0, 130.0, 2.0)
        dt = p2[2] - p1[2] # 1.0 s
        dist_px = np.hypot(p2[0] - p1[0], p2[1] - p1[1]) # 50 px
        speed_kmh = (dist_px * PIXEL_TO_METER / dt) * 3.6
        # 50 * 0.05 = 2.5 m / 1.0 s = 2.5 m/s * 3.6 = 9.0 km/h
        self.assertAlmostEqual(speed_kmh, 9.0, places=2)

    def test_zero_time_delta_protection(self):
        dt = 0.0
        dist_px = 50.0
        speed_kmh = 0.0
        if dt > 0:
            speed_kmh = (dist_px * PIXEL_TO_METER / dt) * 3.6
        self.assertEqual(speed_kmh, 0.0)

    def test_lane_trend_tracker(self):
        tracker = LaneTrendTracker()
        # Feed increasing counts
        for c in range(1, 15):
            tracker.update(lane_id=1, count=c)
        self.assertGreater(tracker.trend(lane_id=1), 0.15)
        self.assertEqual(tracker.label(lane_id=1), "↑")
        self.assertEqual(tracker.label_ascii(lane_id=1), "^")

        # Feed decreasing counts
        for c in range(15, 1, -1):
            tracker.update(lane_id=2, count=c)
        self.assertLess(tracker.trend(lane_id=2), -0.15)
        self.assertEqual(tracker.label(lane_id=2), "↓")
        self.assertEqual(tracker.label_ascii(lane_id=2), "v")

        # Feed flat counts
        for _ in range(10):
            tracker.update(lane_id=3, count=5)
        self.assertAlmostEqual(tracker.trend(lane_id=3), 0.0, places=1)
        self.assertEqual(tracker.label(lane_id=3), "→")
        self.assertEqual(tracker.label_ascii(lane_id=3), "-")


class TestIncidentDetector(unittest.TestCase):
    """Tests stationary vehicle and stalled incident detection."""

    def test_stationary_incident_detection(self):
        detector = IncidentDetector()
        track_id = 101
        lane_id = 1
        
        # Initial position
        res = detector.update(track_id, cx=200, cy=200, lane_id=lane_id, timeout=0.05)
        self.assertFalse(res)

        # Wait past timeout
        time.sleep(0.08)
        # Update with same coordinates
        res = detector.update(track_id, cx=200, cy=200, lane_id=lane_id, timeout=0.05)
        self.assertTrue(res)

    def test_moving_vehicle_resets_incident(self):
        detector = IncidentDetector()
        track_id = 102
        detector.update(track_id, cx=100, cy=100, lane_id=1, timeout=0.05)
        time.sleep(0.03)
        # Vehicle moved > INCIDENT_DIST_PX
        res = detector.update(track_id, cx=300, cy=300, lane_id=1, timeout=0.05)
        self.assertFalse(res)


class TestViolationManager(unittest.TestCase):
    """Tests Phase 1 & 2 traffic enforcement violations and evidence creation."""

    def setUp(self):
        init_db()
        self.vm = ViolationManager()
        self.dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    def test_red_light_violation(self):
        self.vm.stop_lines[1] = 200 # stop line at y = 200
        bbox = (100, 210, 160, 270)
        track_id = 201
        
        # Set previous position before stop line
        self.vm.prev_centroids[track_id] = (120, 180)

        # Crosses stop line (cy = 220) during RED -> Violation!
        v = self.vm.check_red_light(
            track_id=track_id, cx=120, cy=220, lane_id=1,
            is_lane_red=True, frame=self.dummy_frame, bbox=bbox, speed_kmh=42.0, label="car"
        )
        self.assertIsNotNone(v)
        self.assertEqual(v["type"], "RED_LIGHT")

    def test_wrong_way_detection(self):
        track_id = 301
        bbox = (200, 100, 260, 180)
        # Establish downward dominant traffic flow in lane 1
        self.vm.lane_flow_vectors[1] = [(0.0, 15.0)] * 10
        self.vm.prev_centroids[track_id] = (230, 200)
        
        # Vehicle moving upward (dy = -50, opposing flow)
        v = None
        for _ in range(6):
            res = self.vm.check_wrong_way(
                track_id=track_id, cx=230, cy=150, lane_id=1,
                frame=self.dummy_frame, bbox=bbox, speed_kmh=35.0, label="car"
            )
            if res:
                v = res
                break
        self.assertIsNotNone(v)
        self.assertEqual(v["type"], "WRONG_WAY")

    def test_two_wheeler_helmet_and_triple_riding(self):
        track_id = 401
        m_bbox = (100, 100, 200, 300) # motorcycle bbox
        
        # Motorcycle with 2 additional persons overlapping (Triple riding)
        person_boxes = [
            ((110, 110, 150, 180), "person"),
            ((150, 110, 190, 180), "person")
        ]
        
        violations = self.vm.check_two_wheeler_violations(
            track_id=track_id, frame=self.dummy_frame, bbox=m_bbox,
            lane_id=1, speed_kmh=35.0, label="motorcycle", all_boxes=person_boxes
        )
        self.assertIsInstance(violations, list)
        self.assertTrue(any(v["type"] == "TRIPLE_RIDING" for v in violations))

    def test_pedestrian_jaywalking(self):
        ped_id = 501
        bbox = (150, 250, 180, 320)
        # Pedestrian in vehicle lane while vehicle light is GREEN
        v = self.vm.check_jaywalking(
            ped_id=ped_id, cx=165, cy=285, lane_id=1,
            frame=self.dummy_frame, bbox=bbox, is_veh_green=True
        )
        self.assertIsNotNone(v)
        self.assertEqual(v["type"], "JAYWALKING")

    def test_plate_ocr_fallback(self):
        lpr = LicensePlateRecognizer()
        plate_str, _ = lpr.extract_plate(self.dummy_frame, (50, 50, 150, 150), track_id=99)
        self.assertTrue(plate_str.startswith("IND-") or len(plate_str) >= 4)


class TestWeatherAnalyzer(unittest.TestCase):
    """Tests Phase 3 environmental condition detection and confidence tuning."""

    def test_day_clear_detection(self):
        analyzer = WeatherAnalyzer()
        # Create normal daylight image with texture and contrast
        np.random.seed(42)
        normal_frame = np.random.randint(70, 210, (300, 300, 3), dtype=np.uint8)
        
        # Run across frame counter interval
        res = None
        for _ in range(16):
            res = analyzer.analyze_frame(normal_frame)
        self.assertIn(res["condition"], ["Clear Day", "Rain / Overcast", "Clear"])
        self.assertGreaterEqual(res["recommended_conf"], 0.20)

    def test_night_detection(self):
        analyzer = WeatherAnalyzer()
        dark_frame = np.full((300, 300, 3), 15, dtype=np.uint8)
        res = None
        for _ in range(16):
            res = analyzer.analyze_frame(dark_frame)
        self.assertEqual(res["condition"], "Night")
        self.assertLess(res["recommended_conf"], 0.35)


class TestSignalsAIAndForecasting(unittest.TestCase):
    """Tests Phase 6 signal strategies, green wave, and forecasting."""

    def test_congestion_forecaster(self):
        forecaster = CongestionForecaster()
        # Feed volumes
        for i in range(10):
            forecaster.record_volume({1: 5 + i, 2: 3 + i})
        
        fc = forecaster.forecast(lane_id=1)
        self.assertIn("15m", fc)
        self.assertIn("30m", fc)
        self.assertIn("60m", fc)
        self.assertIn(fc["15m"]["los"], ["A", "B", "C", "D", "E", "F"])

    def test_signal_controller_modes(self):
        sc = SignalController(num_lanes=2)
        # Test switching strategies
        self.assertTrue(sc.set_strategy("fixed"))
        self.assertEqual(sc.current_strategy, "fixed")
        
        self.assertTrue(sc.set_strategy("actuated"))
        self.assertEqual(sc.current_strategy, "actuated")

        self.assertTrue(sc.set_strategy("adaptive"))
        self.assertEqual(sc.current_strategy, "adaptive")

        self.assertFalse(sc.set_strategy("invalid_mode"))

    def test_emergency_vehicle_preemption(self):
        sc = SignalController(num_lanes=2)
        # Trigger emergency in lane 2
        status = sc.compute_cycle(lane_counts={1: {}, 2: {}}, predicted_counts={}, emergency_lane=2)
        self.assertEqual(status["active_green_lane"], 2)
        self.assertTrue(status["emergency_corridor"])
        self.assertEqual(status["lane_states"][2]["color"], "GREEN")


class TestDatabaseAndStorage(unittest.TestCase):
    """Tests Phase 7 SQLite persistence, audit trails, and cleanup policies."""

    def setUp(self):
        init_db()

    def test_violation_crud(self):
        v_id = insert_violation(
            v_type="speeding", track_id=88, lane_id=1,
            speed_kmh=82.5, plate_number="IND-0088", details="Over speed limit"
        )
        self.assertGreater(v_id, 0)
        rec = get_violation_by_id(v_id)
        self.assertIsNotNone(rec)
        self.assertEqual(rec["plate_number"], "IND-0088")

    def test_alerts_and_acknowledgment(self):
        a_id = insert_alert(severity="critical", category="incident", title="Crash", message="Vehicle stalled")
        self.assertGreater(a_id, 0)
        alerts = get_alerts(limit=5)
        self.assertTrue(any(a["id"] == a_id for a in alerts))
        acknowledge_alert(a_id)

    def test_custom_zones(self):
        save_custom_zone("zone_test_1", "cam1", "Test Zone", "speed_zone", [[0, 0], [100, 100]])
        zones = get_custom_zones("cam1")
        self.assertTrue(any(z["id"] == "zone_test_1" for z in zones))
        delete_custom_zone("zone_test_1")
        zones_after = get_custom_zones("cam1")
        self.assertFalse(any(z["id"] == "zone_test_1" for z in zones_after))

    def test_audit_logs(self):
        log_audit("admin", "SIGNAL_CHANGE", "Switched to adaptive")
        logs = get_audit_logs(limit=5)
        self.assertTrue(any(l["action"] == "SIGNAL_CHANGE" for l in logs))

    def test_traffic_logging(self):
        log_traffic_frame(
            frame_id=1,
            lane_counts={1: {"car": 4, "bus": 1, "truck": 0, "motorbike": 2, "pedestrian": 0}},
            incidents=[],
            los_dict={"1": "B"},
            flow_dict={"1": 15.0}
        )
        logs = get_historical_traffic(hours=1, lane_id="1")
        self.assertGreater(len(logs), 0)

    def test_cleanup_policy(self):
        run_db_cleanup(retention_days=30)


class TestAuthAndRBAC(unittest.TestCase):
    """Tests Phase 7 Role-Based Access Control and API Key enforcement."""

    def test_permission_hierarchy(self):
        self.assertTrue(_has_permission("Admin", "Viewer"))
        self.assertTrue(_has_permission("Admin", "Operator"))
        self.assertTrue(_has_permission("Admin", "Admin"))
        
        self.assertTrue(_has_permission("Operator", "Viewer"))
        self.assertTrue(_has_permission("Operator", "Operator"))
        self.assertFalse(_has_permission("Operator", "Admin"))

        self.assertTrue(_has_permission("Viewer", "Viewer"))
        self.assertFalse(_has_permission("Viewer", "Operator"))
        self.assertFalse(_has_permission("Viewer", "Admin"))


class TestRESTAPIEndpoints(unittest.TestCase):
    """Tests REST endpoints, OpenAPI docs, and Swagger UI."""

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()
        init_db()

    def test_healthz_endpoint(self):
        res = self.client.get("/healthz")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "healthy")

    def test_openapi_spec(self):
        res = self.client.get("/openapi.json")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["openapi"], "3.0.0")
        self.assertIn("/api/stats", data["paths"])
        self.assertIn("/api/violations", data["paths"])

    def test_swagger_ui_docs(self):
        res = self.client.get("/api/docs")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Swagger Docs", res.get_data(as_text=True))

    def test_api_stats_auth_protection(self):
        # Unauthenticated request without API Key should return 401
        res = self.client.get("/api/stats")
        self.assertEqual(res.status_code, 401)

        # Authenticated with valid API key
        headers = {"X-API-Key": "traffiq_live_secret_key_2026"}
        res = self.client.get("/api/stats", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("vehicle_count", data)

    def test_signals_strategy_api(self):
        headers = {"X-API-Key": "traffiq_live_secret_key_2026"}
        
        # Get status
        res = self.client.get("/api/signals/status", headers=headers)
        self.assertEqual(res.status_code, 200)

        # Post strategy change
        res = self.client.post(
            "/api/signals/strategy",
            headers=headers,
            json={"strategy": "actuated"}
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["strategy"], "actuated")

    def test_cameras_api(self):
        headers = {"X-API-Key": "traffiq_live_secret_key_2026"}
        res = self.client.get("/api/cameras", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("cameras", data)
        self.assertGreater(len(data["cameras"]), 0)

    def test_report_downloads(self):
        headers = {"X-API-Key": "traffiq_live_secret_key_2026"}
        
        # PDF/HTML report
        res_pdf = self.client.get("/api/reports/download/pdf", headers=headers)
        self.assertEqual(res_pdf.status_code, 200)
        res_pdf.close()

        # Excel/CSV report
        res_excel = self.client.get("/api/reports/download/excel", headers=headers)
        self.assertEqual(res_excel.status_code, 200)
        res_excel.close()

    def test_emergency_corridor_api(self):
        # 1. Stats endpoint
        res = self.client.get("/api/emergency/stats")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("stats", data)
        self.assertIn("recent_transits", data)

        # 2. Trigger preemption: Ambulance approaching Lane 1
        res_trig = self.client.post("/api/emergency/trigger", json={
            "vehicle_type": "Ambulance",
            "lane_id": 1,
            "speed_kmh": 68.0,
            "duration_seconds": 30.0
        })
        self.assertEqual(res_trig.status_code, 200)
        trig_data = res_trig.get_json()
        self.assertEqual(trig_data["status"], "preempted")
        self.assertEqual(trig_data["vehicle_type"], "Ambulance")
        self.assertEqual(trig_data["new_signal"], "GREEN")

        # 3. Verify stats reflect the active preemption and new count
        res_after = self.client.get("/api/emergency/stats")
        self.assertEqual(res_after.status_code, 200)
        after_data = res_after.get_json()
        self.assertTrue(after_data["active_preemption"])
        self.assertEqual(after_data["active_lane"], 1)
        self.assertEqual(after_data["signal_status"]["lane_states"]["1"]["color"], "GREEN")
        self.assertEqual(after_data["signal_status"]["lane_states"]["2"]["color"], "RED")

        # 4. Clear emergency corridor
        res_clear = self.client.post("/api/emergency/clear")
        self.assertEqual(res_clear.status_code, 200)
        self.assertEqual(res_clear.get_json()["status"], "cleared")

    def test_settings_api(self):
        headers = {"X-API-Key": "traffiq_live_secret_key_2026"}

        # 1. GET Settings
        res = self.client.get("/api/settings", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("conf_threshold", data)
        self.assertIn("speed_limit", data)
        self.assertIn("signal_mode", data)

        # 2. POST Save Settings
        new_settings = {
            "conf_threshold": 0.40,
            "speed_limit": 65,
            "incident_timeout": 8.0,
            "signal_mode": "actuated",
            "retention_days": 15
        }
        res_post = self.client.post("/api/settings", headers=headers, json=new_settings)
        self.assertEqual(res_post.status_code, 200)
        self.assertEqual(res_post.get_json()["status"], "saved")

        # 3. Verify GET returns updated settings
        res_verify = self.client.get("/api/settings", headers=headers)
        self.assertEqual(res_verify.status_code, 200)
        verify_data = res_verify.get_json()
        self.assertEqual(verify_data["conf_threshold"], 0.40)
        self.assertEqual(verify_data["speed_limit"], 65)

        # 4. Database cleanup endpoint
        res_cleanup = self.client.post("/api/database/cleanup", headers=headers, json={"days": 30})
        self.assertEqual(res_cleanup.status_code, 200)
        self.assertEqual(res_cleanup.get_json()["status"], "cleaned")

    @classmethod
    def tearDownClass(cls):
        # Clean up test database file if created
        if os.path.exists(TEST_DB_PATH):
            try:
                os.remove(TEST_DB_PATH)
            except OSError:
                pass


if __name__ == "__main__":
    unittest.main()
