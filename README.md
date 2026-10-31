# 🚦 TraffiQ — AI-Powered Autonomous Traffic Intelligence & Signal Control

A production-grade, real-time traffic analytics and actuated signal-control dashboard built with **YOLOv8**, **ByteTrack**, **OpenCV**, and **Flask**. Detects and tracks vehicles across lanes, enforces traffic violations with evidence snapshot/video generation, coordinates traffic signals (Fixed, Actuated, AI-Adaptive, and Green-Wave), forecasts congestion, maps multi-camera intersections on GIS Leaflet, and provides an enterprise REST API with OpenAPI/Swagger documentation.

Featuring a dark theme with neon-purple glow glassmorphism, collapsible control sidebar, and real-time telemetry.

---

## 🌟 Comprehensive 7-Phase Architecture

### Phase 1: Violation Enforcement & Evidence Archival
- **Red-Light Violation Enforcement:** Detects stop-line crossings during RED signal phases, automatically capturing high-resolution watermarked snapshots and a 75-frame rolling video clip.
- **Wrong-Way Driving Detection:** Learns dominant lane directional flow vectors online; flags vehicles travelling counter-flow via cosine vector similarity.
- **Two-Wheeler Safety & Triple-Riding:** Identifies motorcycle riders without helmets and flags triple-riding through spatial person-to-vehicle overlap heuristics.
- **Illegal Parking & Stalling:** Configurable dwell timer flags vehicles stopping or idling inside active traffic lanes.
- **Jaywalking & Pedestrian Counting:** Detects pedestrians crossing vehicle roadways during active green vehicular phases.
- **Violation Gallery & Evidence Download:** Interactive gallery displaying plate, speed, timestamp, and a one-click ZIP download packaging annotated image + MP4 clip + JSON telemetry.

### Phase 2: License Plate Recognition (LPR) & Linkage
- Localizes vehicle plate ROIs and extracts alphanumeric plates with EasyOCR / heuristic fallback (`IND-XXXX`).
- Links recognized plates across violations, speed camera logs, and database records.
- Included in CSV/Excel exports, REST API, and visual evidence watermarks.

### Phase 3: Historical Analytics & Environmental Intelligence
- **Vehicle Classification:** Live breakdown (Cars, Buses, Trucks, Motorcycles, Pedestrians) with interactive Chart.js Donut chart.
- **Historical Analytics & Heatmap Matrix:** 24-hour time-of-day volume distribution matrix, peak hour identification, and lane-by-lane comparison.
- **One-Click Executive Reports:** Instant generation of executive HTML/PDF audit reports and structured Excel/CSV data dumps.
- **Weather & Environmental Analyzer:** Dynamic sharpness variance (Laplacian) and contrast/brightness profiling to detect Day/Clear, Fog/Haze, Rain, and Night, dynamically auto-tuning YOLO confidence.

### Phase 4: Dynamic Alerts Center & Custom Zones
- **Alerts Center:** Real-time glassmorphic toast notifications and persistent history log filtered by category (Incident, Violation, Ambulance, Congestion).
- **Theme Toggle & Responsive UI:** Instant Dark / Light theme switching, mobile-responsive layout, and PWA manifest.
- **Interactive Zone Tool:** Draw custom polygons directly on the video feed to define virtual counting gates, no-parking zones, or speed zones.
- **Remote Dispatch:** Automated notification webhooks for Telegram, WhatsApp, and generic incident endpoints.

### Phase 5: Multi-Camera GIS Grid & Live Mapping
- **Multi-Camera Management:** Camera switcher and 2x2 grid view supporting RTSP, IP cameras, webcams, and video files.
- **Interactive Leaflet.js Map:** Real-time GIS map displaying intersection nodes with dynamic color-coded Level of Service (LOS A–F) indicators.

### Phase 6: AI Predictive Signals & Arterial Coordination
- **Congestion Forecasting:** Multi-step time-series forecasting (15, 30, and 60 minutes ahead) with predicted vehicle count and LOS grades.
- **Triple Signal Strategy Controller:**
  - `Fixed`: Predictable 30s cyclical phase timing.
  - `Actuated`: Gap-out vehicle presence extensions (min 12s, max 60s).
  - `AI-Adaptive`: Dynamic phase durations (15s–75s) derived from queue volume, trend slopes, and starvation prevention.
- **Arterial Green-Wave Coordination:** Progresses green signals downstream with travel-time offsets.
- **Emergency Priority Corridor & Preemption History (Main Dashboard + `/emergency`):**
  - **Embedded Main Dashboard Card**: Live "Emergency Vehicle Transit & Preemption History" table directly visible on `/dashboard` and `/` without leaving the main command center.
  - Automated **Red ➔ Green Signal Override**: when an ambulance 🚑, fire truck/engine 🚒, rescue truck 🚜, or police car 🚓 approaches, its lane's red light instantly transitions to green to give immediate way, while conflicting lanes are locked to red.
  - Live preemption status beacon (Standby vs. Active Override with pulsing glow) and instant corridor toast notifications.
  - Real-time counters and breakdown for Ambulances 🚑, Fire Engines 🚒, Police Interceptors 🚓, and Rescue Trucks 🚜.
  - Embedded one-click simulation dispatcher right in the dashboard for testing emergency vehicle preemption on-demand.
  - Complete certified historical transit audit log (`Event ID`, `Timestamp`, `Vehicle Classification`, `Lane`, `Approach Velocity`, `Signal Transition RED ➔ GREEN`, `Preemption Duration`, `Corridor Status`).
  - Dedicated full-screen console available at `/emergency` with 3-lens realistic glowing signal fixtures.
- **Live Efficiency Comparison:** Side-by-side wait time and throughput benchmarking between Fixed, Actuated, and AI-Adaptive modes.

### Phase 7: Production Readiness, Security & Docker
- **Enterprise REST API:** Full OpenAPI 3.0 specification (`/openapi.json`) and interactive Swagger UI documentation at `/api/docs`.
- **Role-Based Access Control (RBAC):** Hierarchical permissions (`Admin`, `Operator`, `Viewer`) with audit trail logging for all configuration changes.
- **SQLite WAL Storage:** Persistent database (`traffiq.db`) with automatic 30-day data retention and cleanup policies.
- **Hardware Acceleration:** Auto-detects Apple Silicon MPS, NVIDIA CUDA, and CPU execution with live FPS, frame-skipping, and latency monitoring.
- **Containerization:** Production Dockerfile and `docker-compose.yml` with health checks (`/healthz`).
- **Comprehensive Test Suite:** 29 automated unit tests verifying tracking, calibration, signals, and REST endpoints.

---

## 🚀 Quick Start

### 1. Prerequisites & Virtual Environment
```bash
git clone https://github.com/Varn1t/Traffic-Intelligence.git
cd "Traffic Intelligence"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Credentials
```bash
cp .env.example .env
```
Default credentials in `.env`:
```
DASH_USER=admin
DASH_PASS=admin123
API_KEY=trq-prod-live-secret-key-2026
FLASK_PORT=5050
```

### 3. Run with Docker (Recommended)
```bash
docker compose up --build
```
Open **http://localhost:5050** in your browser.

### 4. Run Locally
```bash
python main.py
```
- A video window opens.
- The web dashboard will be available at **http://localhost:5050**.
- Log in with `admin` / `admin123`.

---

## 🧪 Running Unit Tests

Run the complete 29-test automated test suite:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## 📡 REST API & Swagger UI

Interactive Swagger documentation is available at:
👉 **http://localhost:5050/api/docs**

OpenAPI specification:
👉 **http://localhost:5050/openapi.json**

### Key Endpoints:
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/healthz` | System health check (Kubernetes ready) |
| `GET` | `/api/stats` | Real-time telemetry (counts, LOS, speeds, signals) |
| `GET` | `/api/violations` | Filterable violation logs |
| `GET` | `/api/violations/<id>/evidence` | Download complete evidence ZIP package |
| `GET` | `/api/alerts` | Real-time toast alerts and historic notifications |
| `POST` | `/api/alerts/ack/<id>` | Acknowledge an alert |
| `GET` | `/api/analytics/historical` | Query historical vehicle flows by hour/lane |
| `GET` | `/api/analytics/time-of-day` | 24-hour traffic volume matrix |
| `GET` | `/api/analytics/classes` | Breakdown across vehicle types |
| `GET` | `/api/reports/download/pdf` | Download official executive HTML/PDF report |
| `GET` | `/api/reports/download/excel` | Download structured traffic CSV report |
| `GET` | `/api/cameras` | List connected camera streams and GPS coordinates |
| `GET` | `/api/signals/status` | Active signal phase, remaining countdown, and strategy |
| `POST` | `/api/signals/strategy` | Change signal mode (`fixed`, `actuated`, `ai_adaptive`) |
| `GET` | `/emergency` | Dedicated Emergency Priority Corridor dashboard |
| `GET` | `/api/emergency/stats` | Emergency transit statistics and active preemption status |
| `POST` | `/api/emergency/trigger` | Dispatch emergency vehicle & trigger RED ➔ GREEN preemption |
| `POST` | `/api/emergency/clear` | Reset emergency preemption corridor |
| `GET` | `/api/audit` | View RBAC audit trails |

Authentication is supported via session login or `X-API-Key: trq-prod-live-secret-key-2026` header.

---

## ⌨️ Keyboard Shortcuts (OpenCV Window)
- **`L`** — Toggle Lane Overlay
- **`H`** — Toggle Density Heatmap Overlay
- **`S`** — Toggle Speed Camera Bounding Boxes
- **`T`** — Toggle Signal Countdown Timers
- **`Q`** or **`Esc`** — Safe Shutdown

---

## 📄 License
TraffiQ Autonomous Traffic Management Intelligence Engine &bull; All rights reserved.
