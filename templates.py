# ─────────────────────────────────────────────────────────────
# TraffiQ — Unified Multi-Phase Neural Traffic Intelligence UI
# ─────────────────────────────────────────────────────────────

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>TraffiQ — Neural Traffic Command Console</title>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700;800&display=swap" rel="stylesheet"/>
  
  <!-- Leaflet GIS Map CSS & JS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  
  <!-- Chart.js -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>

  <style>
    :root {
      --bg: #06040c;
      --bg-surface: rgba(16, 12, 28, 0.78);
      --bg-surface-elevated: rgba(26, 18, 44, 0.88);
      --border-subtle: rgba(168, 85, 247, 0.16);
      --border-glow: rgba(168, 85, 247, 0.45);
      --accent: #a855f7;
      --accent-bright: #c084fc;
      --accent-deep: #7c3aed;
      --cyan: #06b6d4;
      --green: #10b981;
      --amber: #f59e0b;
      --red: #ef4444;
      --text: #f1f5f9;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      --shadow-3d: 0 12px 36px -8px rgba(0, 0, 0, 0.65), 0 0 24px -4px rgba(168, 85, 247, 0.15);
    }

    /* Light Theme Overrides */
    body.light-theme {
      --bg: #f8fafc;
      --bg-surface: rgba(255, 255, 255, 0.85);
      --bg-surface-elevated: rgba(241, 245, 249, 0.95);
      --border-subtle: rgba(168, 85, 247, 0.25);
      --border-glow: rgba(168, 85, 247, 0.6);
      --text: #0f172a;
      --text-muted: #475569;
      --text-dim: #64748b;
      --shadow-3d: 0 12px 30px -8px rgba(0, 0, 0, 0.1), 0 0 20px 0 rgba(168, 85, 247, 0.1);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    
    body {
      font-family: 'Plus Jakarta Sans', sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      overflow-x: hidden;
      perspective: 1200px;
      transition: background 0.3s, color 0.3s;
    }

    #bg-canvas {
      position: fixed;
      inset: 0;
      width: 100vw;
      height: 100vh;
      z-index: 0;
      pointer-events: none;
      opacity: 0.85;
    }

    .wrap {
      position: relative;
      z-index: 2;
      max-width: 1480px;
      margin: 0 auto;
      padding: 24px 28px 60px;
    }

    .card-3d {
      position: relative;
      background: var(--bg-surface);
      backdrop-filter: blur(20px) saturate(180%);
      -webkit-backdrop-filter: blur(20px) saturate(180%);
      border: 1px solid var(--border-subtle);
      border-radius: 20px;
      transform-style: preserve-3d;
      transition: transform 0.22s cubic-bezier(0.2, 0.8, 0.2, 1), border-color 0.3s, box-shadow 0.3s;
      box-shadow: var(--shadow-3d);
      overflow: hidden;
    }

    .card-3d:hover {
      border-color: var(--border-glow);
      box-shadow: 0 16px 48px -10px rgba(0, 0, 0, 0.75), 0 0 32px 0 rgba(168, 85, 247, 0.25);
    }

    /* ── HEADER ── */
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 24px;
      padding: 16px 24px;
      border-radius: 22px;
      background: var(--bg-surface);
      backdrop-filter: blur(24px);
      border: 1px solid var(--border-subtle);
      box-shadow: var(--shadow-3d);
      flex-wrap: wrap;
      gap: 16px;
    }

    .brand-group {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .brand-orb {
      width: 50px;
      height: 50px;
      border-radius: 16px;
      background: linear-gradient(135deg, #a855f7, #6366f1);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.6rem;
      box-shadow: 0 0 30px rgba(168, 85, 247, 0.5);
    }

    .brand-titles h1 {
      font-size: 1.55rem;
      font-weight: 900;
      letter-spacing: -0.03em;
      background: linear-gradient(135deg, #ffffff 40%, #c084fc 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    body.light-theme .brand-titles h1 {
      background: linear-gradient(135deg, #4c1d95 30%, #7c3aed 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }

    .live-beacon {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 7px 14px;
      border-radius: 100px;
      background: rgba(16, 185, 129, 0.12);
      border: 1px solid rgba(16, 185, 129, 0.3);
      font-size: 0.72rem;
      font-weight: 800;
      color: var(--green);
      font-family: 'JetBrains Mono', monospace;
    }

    .live-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--green);
      box-shadow: 0 0 10px var(--green);
    }

    .btn-glass {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      padding: 8px 16px;
      border-radius: 12px;
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 0.78rem;
      font-weight: 700;
      cursor: pointer;
      border: 1px solid var(--border-subtle);
      background: var(--bg-surface-elevated);
      color: var(--text);
      backdrop-filter: blur(12px);
      transition: all 0.22s;
      text-decoration: none;
      white-space: nowrap;
    }

    .btn-glass:hover {
      transform: translateY(-2px);
      border-color: var(--border-glow);
      color: var(--accent-bright);
      box-shadow: 0 4px 18px rgba(168, 85, 247, 0.3);
    }

    .btn-glass.active {
      background: linear-gradient(135deg, rgba(168, 85, 247, 0.3), rgba(124, 58, 237, 0.3));
      border-color: var(--accent);
      color: #fff;
    }

    .btn-glass.danger {
      border-color: rgba(239, 68, 68, 0.3);
      color: var(--red);
    }

    /* ── KPI GRID ── */
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: 16px;
      margin-bottom: 22px;
    }

    .kpi-card {
      padding: 20px;
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      min-height: 140px;
    }

    .kpi-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 10px;
    }

    .kpi-label {
      font-size: 0.68rem;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: var(--text-muted);
      font-weight: 700;
    }

    .kpi-val {
      font-family: 'JetBrains Mono', monospace;
      font-size: 2.1rem;
      font-weight: 800;
      line-height: 1;
      letter-spacing: -0.05em;
      margin-bottom: 6px;
      transition: color 0.3s;
    }

    .kpi-val.blue { color: var(--accent-bright); }
    .kpi-val.green { color: var(--green); }
    .kpi-val.red { color: var(--red); }
    .kpi-val.yellow { color: var(--amber); }
    .kpi-val.cyan { color: var(--cyan); }

    .kpi-sub {
      font-size: 0.7rem;
      color: var(--text-dim);
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .kpi-bar {
      position: absolute;
      bottom: 0;
      left: 0;
      height: 3px;
      border-radius: 0 0 20px 20px;
      width: 60%;
    }

    /* ── DUAL CHARTS & DONUT GRID ── */
    .charts-grid {
      display: grid;
      grid-template-columns: 2fr 1.1fr;
      gap: 18px;
      margin-bottom: 22px;
    }

    @media (max-width: 1024px) {
      .charts-grid { grid-template-columns: 1fr; }
    }

    .chart-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;
      flex-wrap: wrap;
      gap: 10px;
    }

    .chart-title {
      font-size: 0.85rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 8px;
    }

    /* ── GIS LEAFLET MAP & SIGNALS ROW ── */
    .gis-signals-grid {
      display: grid;
      grid-template-columns: 1.3fr 1fr;
      gap: 18px;
      margin-bottom: 22px;
    }

    @media (max-width: 960px) {
      .gis-signals-grid { grid-template-columns: 1fr; }
    }

    #city-map {
      height: 320px;
      border-radius: 16px;
      border: 1px solid var(--border-subtle);
      z-index: 1;
    }

    /* ── STRATEGY PERFORMANCE COMPARISON ── */
    .signal-perf-box {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
      margin-top: 14px;
    }

    .perf-tile {
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      border-radius: 12px;
      padding: 12px;
      text-align: center;
    }

    .perf-tile-val {
      font-family: 'JetBrains Mono', monospace;
      font-size: 1.25rem;
      font-weight: 800;
      color: var(--accent-bright);
    }

    .perf-tile-lbl {
      font-size: 0.65rem;
      color: var(--text-dim);
      text-transform: uppercase;
      font-weight: 700;
      margin-top: 4px;
    }

    /* ── TABLE MATRIX ── */
    .table-container {
      margin-bottom: 22px;
      overflow: hidden;
    }

    .table-header-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 18px 22px 12px;
      border-bottom: 1px solid var(--border-subtle);
    }

    .table-scroll {
      width: 100%;
      overflow-x: auto;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
    }

    th {
      padding: 12px 18px;
      font-size: 0.68rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.1em;
      font-weight: 700;
      border-bottom: 1px solid var(--border-subtle);
      background: rgba(16, 12, 28, 0.4);
    }

    td {
      padding: 14px 18px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.03);
      font-size: 0.84rem;
      font-family: 'JetBrains Mono', monospace;
    }

    tbody tr:hover td {
      background: rgba(168, 85, 247, 0.08);
    }

    tbody tr.lane-selected td {
      background: rgba(168, 85, 247, 0.22) !important;
    }

    .los-pill {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 28px;
      height: 28px;
      border-radius: 8px;
      font-size: 0.78rem;
      font-weight: 800;
    }

    .badge-green  { background: rgba(16, 185, 129, 0.18); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.35); }
    .badge-yellow { background: rgba(245, 158, 11, 0.18); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.35); }
    .badge-orange { background: rgba(249, 115, 22, 0.18); color: #fb923c; border: 1px solid rgba(249, 115, 22, 0.35); }
    .badge-red    { background: rgba(239, 68, 68, 0.18);  color: #f87171; border: 1px solid rgba(239, 68, 68, 0.35); }

    /* ── VIOLATION EVIDENCE GALLERY ── */
    .violation-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 16px;
      margin-top: 14px;
    }

    .v-card {
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      border-radius: 14px;
      padding: 14px;
      transition: all 0.25s;
    }

    .v-card:hover {
      border-color: var(--red);
      transform: translateY(-2px);
    }

    .v-thumb {
      width: 100%;
      height: 140px;
      border-radius: 8px;
      object-fit: cover;
      background: #000;
      border: 1px solid var(--border-subtle);
    }

    .v-tag {
      display: inline-block;
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 0.65rem;
      font-weight: 800;
      text-transform: uppercase;
      background: rgba(239, 68, 68, 0.15);
      border: 1px solid rgba(239, 68, 68, 0.35);
      color: #fca5a5;
    }

    /* ── EMERGENCY VEHICLE PREEMPTION BADGES & CONTROLS ── */
    .badge-veh {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 8px;
      font-weight: 700;
      font-size: 0.78rem;
    }
    .badge-amb    { background: rgba(239, 68, 68, 0.2);  color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); }
    .badge-fire   { background: rgba(249, 115, 22, 0.2); color: #fb923c; border: 1px solid rgba(249, 115, 22, 0.4); }
    .badge-police { background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.4); }
    .badge-rescue { background: rgba(234, 179, 8, 0.2);  color: #facc15; border: 1px solid rgba(234, 179, 8, 0.4); }

    .state-pill-emergency {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 14px;
      border-radius: 10px;
      font-size: 0.8rem;
      font-weight: 800;
      width: fit-content;
      transition: all 0.3s;
    }
    .state-pill-emergency.standby {
      background: rgba(148, 163, 184, 0.15);
      border: 1px solid rgba(148, 163, 184, 0.3);
      color: var(--text-muted);
    }
    .state-pill-emergency.active {
      background: linear-gradient(135deg, rgba(239, 68, 68, 0.3), rgba(16, 185, 129, 0.3));
      border: 1px solid #10b981;
      color: #fff;
      box-shadow: 0 0 20px rgba(16, 185, 129, 0.5);
      animation: pulse-preempt-dash 1s infinite alternate;
    }
    @keyframes pulse-preempt-dash {
      from { box-shadow: 0 0 10px rgba(16, 185, 129, 0.4); }
      to { box-shadow: 0 0 25px rgba(16, 185, 129, 0.9); }
    }

    .em-dispatch-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 10px;
      margin-top: 10px;
    }
    .em-dispatch-btn {
      padding: 10px 14px;
      border-radius: 12px;
      border: 1px solid var(--border-subtle);
      background: var(--bg-surface-elevated);
      color: #fff;
      font-family: inherit;
      font-size: 0.8rem;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 10px;
      transition: all 0.25s;
    }
    .em-dispatch-btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(168, 85, 247, 0.3);
    }
    .em-dispatch-btn.amb:hover { border-color: #ef4444; background: rgba(239, 68, 68, 0.2); box-shadow: 0 6px 20px rgba(239, 68, 68, 0.35); }
    .em-dispatch-btn.fire:hover { border-color: #f97316; background: rgba(249, 115, 22, 0.2); box-shadow: 0 6px 20px rgba(249, 115, 22, 0.35); }
    .em-dispatch-btn.police:hover { border-color: #3b82f6; background: rgba(59, 130, 246, 0.2); box-shadow: 0 6px 20px rgba(59, 130, 246, 0.35); }
    .em-dispatch-btn.rescue:hover { border-color: #eab308; background: rgba(234, 179, 8, 0.2); box-shadow: 0 6px 20px rgba(234, 179, 8, 0.35); }
    .em-dispatch-btn.clear:hover { border-color: #94a3b8; background: rgba(148, 163, 184, 0.2); box-shadow: 0 6px 20px rgba(148, 163, 184, 0.35); }

    .em-kpi-row {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-bottom: 14px;
    }
    .em-kpi-chip {
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      border-radius: 10px;
      padding: 8px 12px;
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.76rem;
      font-weight: 700;
    }
    .em-kpi-chip b {
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.9rem;
      color: #fff;
    }

    /* ── REAL-TIME TOAST CONTAINER ── */
    #toast-container {
      position: fixed;
      top: 24px;
      right: 24px;
      z-index: 10000;
      display: flex;
      flex-direction: column;
      gap: 10px;
      pointer-events: none;
    }

    .toast-card {
      pointer-events: auto;
      background: rgba(18, 12, 32, 0.95);
      backdrop-filter: blur(20px);
      border: 1px solid var(--red);
      border-radius: 14px;
      padding: 14px 18px;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 12px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8), 0 0 20px rgba(239, 68, 68, 0.4);
      animation: toast-in 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      min-width: 300px;
    }

    @keyframes toast-in {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }

    /* ── 3D CONTROL SIDEBAR ── */
    .ctrl-trigger {
      position: fixed;
      bottom: 28px;
      right: 28px;
      width: 60px;
      height: 60px;
      border-radius: 20px;
      background: linear-gradient(135deg, #a855f7, #6366f1);
      border: 1px solid rgba(255, 255, 255, 0.3);
      color: #fff;
      font-size: 1.5rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 8px 30px rgba(168, 85, 247, 0.5);
      z-index: 100;
      transition: all 0.3s;
    }

    .ctrl-trigger.open {
      transform: scale(0.9) rotate(-90deg);
      background: #110d22;
      border-color: var(--accent);
    }

    .ctrl-sidebar {
      position: fixed;
      top: 0;
      right: -420px;
      width: 420px;
      height: 100vh;
      background: rgba(14, 10, 24, 0.92);
      backdrop-filter: blur(28px) saturate(200%);
      -webkit-backdrop-filter: blur(28px) saturate(200%);
      border-left: 1px solid var(--border-glow);
      box-shadow: -15px 0 60px rgba(0, 0, 0, 0.8);
      z-index: 99;
      transition: right 0.4s cubic-bezier(0.16, 1, 0.3, 1);
      padding: 36px 28px;
      display: flex;
      flex-direction: column;
      gap: 24px;
      overflow-y: auto;
    }

    .ctrl-sidebar.open { right: 0; }

    .ctrl-segment-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }

    .ctrl-mode-btn {
      padding: 12px 8px;
      border-radius: 12px;
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 0.74rem;
      font-weight: 700;
      cursor: pointer;
      border: 1px solid var(--border-subtle);
      background: rgba(26, 18, 44, 0.6);
      color: var(--text-muted);
      transition: all 0.2s;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 4px;
    }

    .ctrl-mode-btn.active {
      border-color: var(--accent);
      background: linear-gradient(135deg, rgba(168, 85, 247, 0.3), rgba(99, 102, 241, 0.3));
      color: #fff;
    }

    .ctrl-range {
      -webkit-appearance: none;
      width: 100%;
      height: 6px;
      border-radius: 3px;
      background: rgba(255, 255, 255, 0.1);
      outline: none;
    }

    .ctrl-range::-webkit-slider-thumb {
      -webkit-appearance: none;
      width: 18px;
      height: 18px;
      border-radius: 50%;
      background: linear-gradient(135deg, #c084fc, #7c3aed);
      border: 2px solid #fff;
      cursor: pointer;
    }

    .ctrl-toggle-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 14px;
      border-radius: 12px;
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      font-size: 0.8rem;
      font-weight: 600;
    }

    .switch {
      position: relative;
      display: inline-block;
      width: 44px;
      height: 24px;
    }

    .switch input { opacity: 0; width: 0; height: 0; }
    .slider {
      position: absolute;
      cursor: pointer;
      inset: 0;
      background-color: #334155;
      transition: .3s;
      border-radius: 24px;
    }
    .slider:before {
      position: absolute;
      content: "";
      height: 18px;
      width: 18px;
      left: 3px;
      bottom: 3px;
      background-color: white;
      transition: .3s;
      border-radius: 50%;
    }
    input:checked + .slider { background-color: var(--accent); }
    input:checked + .slider:before { transform: translateX(20px); }

    /* ── MODALS ── */
    .modal-overlay {
      display: none;
      position: fixed;
      inset: 0;
      z-index: 1000;
      background: rgba(6, 4, 12, 0.85);
      backdrop-filter: blur(16px);
      align-items: center;
      justify-content: center;
      padding: 20px;
    }

    .modal-overlay.open { display: flex; }

    .modal-3d {
      background: linear-gradient(145deg, #130d22, #1b1233);
      border: 1px solid var(--border-glow);
      border-radius: 26px;
      padding: 36px;
      width: 100%;
      max-width: 600px;
      box-shadow: 0 0 80px rgba(168, 85, 247, 0.35);
      position: relative;
    }

    body.light-theme .modal-3d {
      background: #ffffff;
      color: #0f172a;
    }
  </style>
</head>
<body>

<canvas id="bg-canvas"></canvas>
<div id="toast-container"></div>

<div class="wrap">

  <!-- HUD HEADER -->
  <header class="card-3d">
    <div class="brand-group">
      <div class="brand-orb">🚦</div>
      <div class="brand-titles">
        <h1>TraffiQ <span style="font-size:0.65rem;padding:3px 8px;border-radius:6px;background:rgba(168,85,247,0.25);border:1px solid rgba(168,85,247,0.4);color:var(--accent-bright)">v2.5 Full-Stack</span></h1>
        <p id="sub-hw-info">Hardware: Neural Acceleration Active &bull; Port 5050</p>
      </div>
    </div>
    
    <div class="header-actions">
      <!-- Camera Switcher -->
      <select id="cam-selector" onchange="switchCamera(this.value)" class="btn-glass" style="outline:none">
        <option value="cam1">🎥 Cam 1: North Junction (Main)</option>
        <option value="cam2">🎥 Cam 2: ISBT Interchange</option>
        <option value="cam3">🎥 Cam 3: Ring Road Flyover</option>
        <option value="cam4">🎥 Cam 4: Airport Expressway</option>
      </select>

      <!-- Weather Indicator Badge -->
      <div class="btn-glass" id="weather-badge" style="border-color:var(--cyan);color:var(--cyan)">
        <span id="weather-icon">☀️</span> <span id="weather-txt">Clear Day (100%)</span>
      </div>

      <!-- Live Beacon -->
      <div class="live-beacon" id="live-badge">
        <span class="live-dot" id="live-dot"></span>
        <span id="live-txt">LIVE AI PIPELINE</span>
      </div>

      <!-- Theme Switcher -->
      <button class="btn-glass" onclick="toggleTheme()" id="btn-theme" title="Toggle Dark/Light Theme">🌓 Theme</button>

      <!-- Settings Button in Header -->
      <button class="btn-glass" onclick="toggleSidebar()" id="btn-header-settings" title="System Settings &amp; Controls" style="border-color:var(--accent);color:var(--accent-bright);display:inline-flex;align-items:center;gap:6px">
        <span>⚙️</span> Settings
      </button>

      <!-- Emergency Priority Corridor Link -->
      <a href="/emergency" class="btn-glass" style="border-color:#ef4444;color:#f87171;text-decoration:none;font-weight:700;display:inline-flex;align-items:center;gap:6px;" title="Emergency Vehicle Priority Corridor">
        <span>🚨</span> Emergency Corridor
      </a>
      
      <!-- Pause -->
      <button class="btn-glass" id="btn-pause" onclick="togglePause()">⏸️ Pause</button>

      <!-- Reports Dropdown / Buttons -->
      <button class="btn-glass" onclick="window.open('/api/reports/download/pdf')" title="One-Click PDF Report">📄 PDF Report</button>
      <button class="btn-glass" onclick="window.open('/api/reports/download/excel')" title="One-Click Excel / CSV Logs">📊 Excel Logs</button>
      
      <!-- Summary Modal -->
      <button class="btn-glass" onclick="openSummary()" style="border-color:var(--accent);color:var(--accent-bright)">📈 Summary</button>
      
      <!-- Logout -->
      <a href="/logout" class="btn-glass danger">🚪 Logout</a>
    </div>
  </header>

  <!-- 3D KPI GRID -->
  <div class="kpi-grid">
    <div class="card-3d kpi-card">
      <div class="kpi-header"><span class="kpi-label">Active Flow</span><div style="font-size:1.3rem">🚗</div></div>
      <div class="kpi-val blue" id="k-veh">—</div>
      <div class="kpi-sub">Total Vehicles Monitored</div>
      <div class="kpi-bar" style="background:linear-gradient(90deg,#a855f7,#6366f1);width:75%"></div>
    </div>

    <div class="card-3d kpi-card">
      <div class="kpi-header"><span class="kpi-label">Lanes & LOS</span><div style="font-size:1.3rem">🛣️</div></div>
      <div class="kpi-val green" id="k-lanes">—</div>
      <div class="kpi-sub" id="k-los-summary">Corridor Grade: B</div>
      <div class="kpi-bar" style="background:linear-gradient(90deg,#10b981,#06b6d4);width:85%"></div>
    </div>

    <div class="card-3d kpi-card">
      <div class="kpi-header"><span class="kpi-label">Violations Total</span><div style="font-size:1.3rem">🚨</div></div>
      <div class="kpi-val red" id="k-violations">0</div>
      <div class="kpi-sub">Red light / Wrong way / Helmet</div>
      <div class="kpi-bar" style="background:linear-gradient(90deg,#ef4444,#e11d48);width:40%"></div>
    </div>

    <div class="card-3d kpi-card">
      <div class="kpi-header"><span class="kpi-label">Signal Strategy</span><div style="font-size:1.3rem">⏱️</div></div>
      <div class="kpi-val yellow" id="k-signal-strategy" style="font-size:1.5rem">AI-ADAPTIVE</div>
      <div class="kpi-sub" id="k-signal-timer">Phase: Lane 1 (25s)</div>
      <div class="kpi-bar" style="background:linear-gradient(90deg,#f59e0b,#ec4899);width:60%"></div>
    </div>

    <div class="card-3d kpi-card">
      <div class="kpi-header"><span class="kpi-label">Inference FPS</span><div style="font-size:1.3rem">⚡</div></div>
      <div class="kpi-val cyan" id="k-fps">—</div>
      <div class="kpi-sub" id="k-latency">Latency: ~18ms</div>
      <div class="kpi-bar" style="background:linear-gradient(90deg,#06b6d4,#a855f7);width:80%"></div>
    </div>

    <div class="card-3d kpi-card">
      <div class="kpi-header"><span class="kpi-label">Pedestrians</span><div style="font-size:1.3rem">🚶</div></div>
      <div class="kpi-val blue" id="k-pedestrians">0</div>
      <div class="kpi-sub">Crosswalk Density</div>
      <div class="kpi-bar" style="background:linear-gradient(90deg,#38bdf8,#818cf8);width:50%"></div>
    </div>
  </div>

  <!-- EMERGENCY CASCADE BANNER -->
  <div id="em-banner" style="display:none;margin-bottom:18px">
    <div style="background:linear-gradient(135deg,rgba(239,68,68,0.2),rgba(245,158,11,0.2));border:1px solid var(--red);border-radius:16px;padding:16px 22px;display:flex;align-items:center;gap:14px;box-shadow:0 0 30px rgba(239,68,68,0.35)">
      <span style="font-size:2rem">🚨</span>
      <div>
        <div style="font-size:1.05rem;font-weight:900;color:#fecaca">EMERGENCY VEHICLE DETECTED &mdash; PRIORITY CORRIDOR ACTIVE</div>
        <div id="em-txt" style="font-size:0.85rem;color:#fef08a;margin-top:2px">Lane given green preemption &bull; Adjacent intersections alerted via Green-Wave cascade</div>
      </div>
    </div>
  </div>

  <!-- DUAL CHARTS: 120s FLOW HISTORY + VEHICLE CLASSIFICATION DONUT -->
  <div class="charts-grid">
    <div class="card-3d" style="padding:22px">
      <div class="chart-header">
        <span class="chart-title">📈 Real-Time Lane Traffic Flow History (120s)</span>
        <div style="display:flex;gap:6px">
          <button class="btn-glass active" id="btn-bar" onclick="setChartType('bar')">Bar View</button>
          <button class="btn-glass" id="btn-line" onclick="setChartType('line')">Line View</button>
        </div>
      </div>
      <canvas id="lane-chart" height="95"></canvas>
    </div>

    <div class="card-3d" style="padding:22px">
      <div class="chart-header">
        <span class="chart-title">🚗 Vehicle Classification Breakdown</span>
        <span style="font-size:0.7rem;color:var(--text-dim)">YOLOv8 + Auto/Ped</span>
      </div>
      <div style="position:relative;height:210px;display:flex;align-items:center;justify-content:center">
        <canvas id="donut-chart"></canvas>
      </div>
    </div>
  </div>

  <!-- GIS INTERSECTION MAP & SIGNALS PERFORMANCE BENCHMARK -->
  <div class="gis-signals-grid">
    <div class="card-3d" style="padding:20px">
      <div class="chart-header">
        <span class="chart-title">🗺️ City Arterial Corridor &bull; Live Intersection Congestion</span>
        <span style="font-size:0.72rem;color:var(--text-dim)">Click node to switch camera</span>
      </div>
      <div id="city-map"></div>
    </div>

    <div class="card-3d" style="padding:20px">
      <div class="chart-header">
        <span class="chart-title">🚦 Signal Strategy Comparative Efficiency</span>
        <select id="strategy-select" onchange="changeSignalStrategy(this.value)" class="btn-glass">
          <option value="adaptive">Mode: AI-Adaptive (Optimized)</option>
          <option value="actuated">Mode: Actuated (Vehicle Gap)</option>
          <option value="fixed">Mode: Fixed-Time (30s Cycle)</option>
        </select>
      </div>
      <div class="signal-perf-box">
        <div class="perf-tile">
          <div class="perf-tile-val" id="perf-wait">12.8s</div>
          <div class="perf-tile-lbl">Avg Wait Time</div>
        </div>
        <div class="perf-tile">
          <div class="perf-tile-val" id="perf-throughput" style="color:var(--green)">36.2</div>
          <div class="perf-tile-lbl">Throughput (v/m)</div>
        </div>
        <div class="perf-tile">
          <div class="perf-tile-val" id="perf-delay" style="color:var(--cyan)">-55%</div>
          <div class="perf-tile-lbl">Delay Reduction</div>
        </div>
      </div>

      <div style="margin-top:16px;background:var(--bg-surface-elevated);border:1px solid var(--border-subtle);border-radius:12px;padding:12px">
        <div style="font-size:0.72rem;font-weight:800;text-transform:uppercase;color:var(--text-muted);margin-bottom:8px">Multi-Step Congestion Forecasting</div>
        <div style="display:flex;justify-content:space-between;font-size:0.8rem">
          <div><b style="color:var(--cyan)">T+15m:</b> <span id="fc-15">4 veh (LOS B)</span></div>
          <div><b style="color:var(--accent-bright)">T+30m:</b> <span id="fc-30">7 veh (LOS C)</span></div>
          <div><b style="color:var(--amber)">T+60m:</b> <span id="fc-60">10 veh (LOS C)</span></div>
        </div>
      </div>
    </div>
  </div>

  <!-- LANE TELEMETRY TABLE -->
  <div class="card-3d table-container">
    <div class="table-header-row">
      <div style="font-size:0.88rem;font-weight:800;letter-spacing:0.04em;text-transform:uppercase">🛣️ Lane Telemetry Matrix</div>
      <div id="filter-hint" style="font-size:0.75rem;color:var(--accent-bright);font-style:italic"></div>
    </div>
    <div class="table-scroll">
      <table>
        <thead>
          <tr>
            <th>Lane</th><th>Cars</th><th>Buses</th><th>Trucks</th><th>Bikes</th><th>Pedestrians</th>
            <th>Total</th><th>LOS</th><th>Flow Rate</th><th>Signal State</th><th>Trend</th><th style="color:var(--accent-bright)">Pred 15s</th>
          </tr>
        </thead>
        <tbody id="lane-tbody"></tbody>
      </table>
    </div>
  </div>

  <!-- EMERGENCY VEHICLE TRANSIT & PREEMPTION HISTORY -->
  <div class="card-3d" id="emergency-preemption-section" style="padding:22px;margin-bottom:24px">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;margin-bottom:14px">
      <div style="display:flex;align-items:center;gap:12px">
        <div style="font-size:1.8rem">🚨</div>
        <div>
          <div style="font-size:1.05rem;font-weight:800;letter-spacing:-0.01em;display:flex;align-items:center;gap:8px">
            <span>Emergency Vehicle Transit &amp; Preemption History</span>
            <span style="font-size:0.7rem;padding:3px 8px;border-radius:6px;background:rgba(239,68,68,0.2);color:#fca5a5;font-weight:700">GIVE-WAY SAFETY CORRIDOR</span>
          </div>
          <div style="font-size:0.75rem;color:var(--text-muted);margin-top:2px">
            Automated Red-to-Green preemption overrides &bull; Timestamped audit trail of emergency runs &bull; Priority corridor enforcement
          </div>
        </div>
      </div>
      <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
        <div id="dash-preemption-pill" class="state-pill-emergency standby">
          <span style="font-size:0.6rem">●</span> STANDBY / MONITORING
        </div>
        <button class="btn-glass" onclick="loadDashboardEmergencyHistory()">🔄 Refresh</button>
        <a href="/emergency" class="btn-glass" style="border-color:#ef4444;color:#f87171;text-decoration:none;font-weight:700">
          🚨 Full Corridor Console &rarr;
        </a>
      </div>
    </div>

    <!-- MINI KPI CHIPS -->
    <div class="em-kpi-row">
      <div class="em-kpi-chip" style="border-left:3px solid var(--red)">
        <span>🚨 Total Transits:</span> <b id="em-chip-total">0</b>
      </div>
      <div class="em-kpi-chip" style="border-left:3px solid #f87171">
        <span>🚑 Ambulances:</span> <b id="em-chip-amb">0</b>
      </div>
      <div class="em-kpi-chip" style="border-left:3px solid #fb923c">
        <span>🚒 Fire Engines:</span> <b id="em-chip-fire">0</b>
      </div>
      <div class="em-kpi-chip" style="border-left:3px solid #60a5fa">
        <span>🚓 Police Patrols:</span> <b id="em-chip-police">0</b>
      </div>
      <div class="em-kpi-chip" style="border-left:3px solid #facc15">
        <span>🚜 Rescue Trucks:</span> <b id="em-chip-rescue">0</b>
      </div>
      <div class="em-kpi-chip" style="border-left:3px solid #10b981">
        <span>⚡ Signal Override:</span> <b id="em-chip-override" style="color:#34d399">RED ➔ GREEN</b>
      </div>
    </div>

    <!-- QUICK SIMULATION DISPATCH CONTROLS -->
    <div style="background:rgba(18,12,32,0.6);border:1px solid var(--border-subtle);border-radius:14px;padding:12px 16px;margin-bottom:16px">
      <div style="font-size:0.72rem;font-weight:800;letter-spacing:0.08em;text-transform:uppercase;color:var(--accent-bright);margin-bottom:8px;display:flex;align-items:center;gap:6px">
        <span>⚡ Instant Emergency Preemption Simulator</span>
        <span style="font-size:0.68rem;color:var(--text-muted);font-weight:500">(Click to force RED light to GREEN to clear corridor)</span>
      </div>
      <div class="em-dispatch-grid">
        <button class="em-dispatch-btn amb" onclick="dashDispatchEmergency('Ambulance', 1, 68)">
          <span style="font-size:1.3rem">🚑</span>
          <div style="text-align:left">
            <div>Ambulance (Lane 1)</div>
            <div style="font-size:0.68rem;color:#fca5a5">68 km/h &bull; Red ➔ Green</div>
          </div>
        </button>
        <button class="em-dispatch-btn fire" onclick="dashDispatchEmergency('Fire Engine', 2, 60)">
          <span style="font-size:1.3rem">🚒</span>
          <div style="text-align:left">
            <div>Fire Engine (Lane 2)</div>
            <div style="font-size:0.68rem;color:#fdba74">60 km/h &bull; Red ➔ Green</div>
          </div>
        </button>
        <button class="em-dispatch-btn police" onclick="dashDispatchEmergency('Police Car', 1, 75)">
          <span style="font-size:1.3rem">🚓</span>
          <div style="text-align:left">
            <div>Police Patrol (Lane 1)</div>
            <div style="font-size:0.68rem;color:#93c5fd">75 km/h &bull; Red ➔ Green</div>
          </div>
        </button>
        <button class="em-dispatch-btn rescue" onclick="dashDispatchEmergency('Rescue Truck', 2, 52)">
          <span style="font-size:1.3rem">🚜</span>
          <div style="text-align:left">
            <div>Rescue Truck (Lane 2)</div>
            <div style="font-size:0.68rem;color:#fde047">52 km/h &bull; Red ➔ Green</div>
          </div>
        </button>
        <button class="em-dispatch-btn clear" onclick="dashClearEmergency()">
          <span style="font-size:1.3rem">⏹️</span>
          <div style="text-align:left">
            <div>Clear Corridor</div>
            <div style="font-size:0.68rem;color:var(--text-muted)">Resume Normal Cycle</div>
          </div>
        </button>
      </div>
    </div>

    <!-- PREEMPTION TRANSIT AUDIT HISTORY TABLE -->
    <div style="overflow-x:auto;border-radius:12px;border:1px solid var(--border-subtle)">
      <table>
        <thead>
          <tr>
            <th>Event ID</th>
            <th>Timestamp</th>
            <th>Emergency Vehicle</th>
            <th>Lane</th>
            <th>Approach Velocity</th>
            <th>Signal Transition</th>
            <th>Preemption Duration</th>
            <th>Corridor Status</th>
          </tr>
        </thead>
        <tbody id="dash-emergency-table-body">
          <tr>
            <td colspan="8" style="text-align:center;color:var(--text-muted);padding:24px">
              Loading emergency vehicle transit history...
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- PHASE 1 & 2: VIOLATIONS EVIDENCE GALLERY -->
  <div class="card-3d" style="padding:22px;margin-bottom:24px">
    <div class="chart-header">
      <span class="chart-title">🚨 Recent Violations &bull; Plate Linkage &amp; Evidence Packages</span>
      <div style="display:flex;gap:8px">
        <select id="v-filter" onchange="loadViolations()" class="btn-glass">
          <option value="all">All Violations</option>
          <option value="RED_LIGHT">Red Light</option>
          <option value="WRONG_WAY">Wrong Way</option>
          <option value="NO_HELMET">No Helmet</option>
          <option value="TRIPLE_RIDING">Triple Riding</option>
          <option value="ILLEGAL_PARKING">Illegal Parking</option>
          <option value="JAYWALKING">Jaywalking</option>
        </select>
        <button class="btn-glass" onclick="loadViolations()">🔄 Refresh</button>
      </div>
    </div>
    <div class="violation-grid" id="v-gallery">
      <div style="color:var(--text-dim);font-size:0.85rem">Awaiting violation events from computer vision engine...</div>
    </div>
  </div>

  <!-- KEYBOARD HUD & FOOTER -->
  <div style="margin-bottom:14px">
    <div style="font-size:0.75rem;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;color:var(--text-muted);margin-bottom:10px">⌨️ Direct Keyboard Commands</div>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px">
      <div class="card-3d" style="padding:10px 14px;display:flex;align-items:center;gap:10px"><b style="color:var(--accent-bright)">[ L ]</b><span style="font-size:0.75rem">Lanes Overlay</span></div>
      <div class="card-3d" style="padding:10px 14px;display:flex;align-items:center;gap:10px"><b style="color:var(--accent-bright)">[ H ]</b><span style="font-size:0.75rem">Density Heatmap</span></div>
      <div class="card-3d" style="padding:10px 14px;display:flex;align-items:center;gap:10px"><b style="color:var(--accent-bright)">[ S ]</b><span style="font-size:0.75rem">Speed Radar</span></div>
      <div class="card-3d" style="padding:10px 14px;display:flex;align-items:center;gap:10px"><b style="color:var(--accent-bright)">[ T ]</b><span style="font-size:0.75rem">Adaptive Timer</span></div>
      <div class="card-3d" style="padding:10px 14px;display:flex;align-items:center;gap:10px"><b style="color:var(--red)">[ Q ]</b><span style="font-size:0.75rem">Safe Shutdown</span></div>
    </div>
  </div>

  <div style="text-align:center;font-size:0.75rem;color:var(--text-dim);margin-top:20px">
    TraffiQ Autonomous Traffic Management Platform &bull; <a href="/api/docs" style="color:var(--accent-bright);text-decoration:none">Swagger REST API Docs</a> &bull; <a href="/openapi.json" style="color:var(--cyan);text-decoration:none">OpenAPI 3.0</a>
  </div>

</div>

<!-- 3D CONTROL SIDEBAR -->
<div class="ctrl-overlay" id="ctrl-overlay" onclick="toggleSidebar()" style="display:none;position:fixed;inset:0;background:rgba(6,4,12,0.6);backdrop-filter:blur(6px);z-index:98"></div>

<button class="ctrl-trigger" id="ctrl-toggle-btn" onclick="toggleSidebar()" title="Control Console">⚙️</button>

<div class="ctrl-sidebar" id="ctrl-sidebar">
  <div style="display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--border-subtle);padding-bottom:14px">
    <div style="font-size:1.15rem;font-weight:800;display:flex;align-items:center;gap:10px"><span>⚙️</span>System Settings &amp; Controls</div>
    <button onclick="toggleSidebar()" style="background:none;border:none;color:var(--text-muted);font-size:1.6rem;cursor:pointer">&times;</button>
  </div>

  <!-- PART 1: VISUALIZATION OVERLAYS -->
  <div>
    <div style="font-size:0.7rem;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;color:var(--accent-bright);margin-bottom:8px">Part 1: 🖥️ Visualization Overlay</div>
    <div class="ctrl-segment-grid">
      <button class="ctrl-mode-btn" id="mbtn-lanes" onclick="setMode('lanes')"><span style="font-size:1.3rem">🛣️</span>Lanes</button>
      <button class="ctrl-mode-btn" id="mbtn-heatmap" onclick="setMode('heatmap')"><span style="font-size:1.3rem">🔥</span>Heatmap</button>
      <button class="ctrl-mode-btn" id="mbtn-speed" onclick="setMode('speed')"><span style="font-size:1.3rem">🏎️</span>Speed</button>
      <button class="ctrl-mode-btn" id="mbtn-timer" onclick="setMode('timer')"><span style="font-size:1.3rem">⏱️</span>Timer</button>
    </div>
  </div>

  <!-- PART 2: AI VISION & CONFIDENCE -->
  <div>
    <div style="font-size:0.7rem;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;color:var(--cyan);margin-bottom:8px">Part 2: 👁️ AI Vision &amp; Confidence</div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
      <span style="font-size:0.72rem;font-weight:700;color:var(--text-muted)">YOLO Detection Confidence</span>
      <span id="val-conf-thresh" style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;font-weight:800;color:var(--cyan)">25%</span>
    </div>
    <input type="range" class="ctrl-range" id="slider-conf-thresh" min="0.10" max="0.90" step="0.05" value="0.25" oninput="onSliderInput('conf-thresh', Math.round(this.value*100)+'%', 'conf_threshold')" onchange="onSliderChange('conf_threshold', this.value)">
    
    <div style="margin-top:10px;display:flex;justify-content:space-between;align-items:center">
      <span style="font-size:0.72rem;font-weight:700;color:var(--text-muted)">Target Model</span>
      <select id="select-model" class="btn-glass" style="padding:4px 8px;font-size:0.75rem;outline:none">
        <option value="yolov8n">YOLOv8 Nano (Fastest)</option>
        <option value="yolov8s">YOLOv8 Small (Balanced)</option>
        <option value="yolov8m">YOLOv8 Medium (High Accuracy)</option>
      </select>
    </div>
  </div>

  <!-- PART 3: SPEED & CALIBRATION -->
  <div>
    <div style="font-size:0.7rem;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;color:var(--amber);margin-bottom:8px">Part 3: 🏎️ Speed &amp; Calibration</div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
      <span style="font-size:0.72rem;font-weight:700;color:var(--text-muted)">Speed Camera Trigger</span>
      <span id="val-speed-limit" style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;font-weight:800;color:var(--accent-bright)">50 km/h</span>
    </div>
    <input type="range" class="ctrl-range" id="slider-speed-limit" min="20" max="120" step="5" value="50" oninput="onSliderInput('speed-limit', this.value + ' km/h', 'speed_limit')" onchange="onSliderChange('speed_limit', this.value)">

    <div style="display:flex;justify-content:space-between;align-items:center;margin-top:12px;margin-bottom:8px">
      <span style="font-size:0.72rem;font-weight:700;color:var(--text-muted)">Incident Stalled Vehicle Timeout</span>
      <span id="val-incident-timeout" style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;font-weight:800;color:var(--amber)">5s</span>
    </div>
    <input type="range" class="ctrl-range" id="slider-incident-timeout" min="2" max="30" step="1" value="5" oninput="onSliderInput('incident-timeout', this.value + 's', 'incident_timeout')" onchange="onSliderChange('incident_timeout', this.value)">
    
    <div style="margin-top:8px;font-size:0.7rem;color:var(--text-dim);display:flex;justify-content:space-between">
      <span>Speed Scale Factor:</span>
      <span style="color:var(--accent-bright);font-weight:700">0.05 meters/pixel</span>
    </div>
  </div>

  <!-- PART 4: SIGNAL STRATEGY & EMERGENCY -->
  <div>
    <div style="font-size:0.7rem;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;color:var(--green);margin-bottom:8px">Part 4: 🚦 Signal Strategy &amp; Emergency</div>
    <div style="margin-bottom:10px">
      <label style="font-size:0.72rem;font-weight:700;color:var(--text-muted);display:block;margin-bottom:6px">Control Mode Strategy</label>
      <select id="select-signal-strategy" class="btn-glass" style="width:100%;padding:8px 12px;font-size:0.8rem;outline:none" onchange="onStrategySelect(this.value)">
        <option value="adaptive">AI-Adaptive (Dynamic Queue &amp; Trend)</option>
        <option value="actuated">Actuated (Gap-Out Sensor Logic)</option>
        <option value="fixed">Fixed-Time (Standard 30s Cyclical)</option>
      </select>
    </div>
    <div style="display:flex;flex-direction:column;gap:8px">
      <a href="/emergency" class="btn-glass" style="width:100%;justify-content:center;border-color:#ef4444;color:#f87171;font-size:0.78rem;text-decoration:none">
        <span>🚨</span> Full Priority Console &rarr;
      </a>
      <a href="#emergency-preemption-section" onclick="toggleSidebar()" class="btn-glass" style="width:100%;justify-content:center;border-color:var(--accent);color:var(--accent-bright);font-size:0.78rem;text-decoration:none">
        <span>📋</span> View Transit &amp; Preemption History &darr;
      </a>
    </div>
  </div>

  <!-- PART 5: ENFORCEMENT MODULES -->
  <div>
    <div style="font-size:0.7rem;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;color:var(--text-muted);margin-bottom:8px">Part 5: 🛡️ Enforcement Modules</div>
    <div style="display:flex;flex-direction:column;gap:8px">
      <div class="ctrl-toggle-row">
        <span>🚦 Red-Light Violation Camera</span>
        <label class="switch"><input type="checkbox" id="chk-red-light" checked><span class="slider"></span></label>
      </div>
      <div class="ctrl-toggle-row">
        <span>🔄 Wrong-Way Direction Filter</span>
        <label class="switch"><input type="checkbox" id="chk-wrong-way" checked><span class="slider"></span></label>
      </div>
      <div class="ctrl-toggle-row">
        <span>⛑️ Helmet &amp; Triple-Riding Check</span>
        <label class="switch"><input type="checkbox" id="chk-helmet" checked><span class="slider"></span></label>
      </div>
      <div class="ctrl-toggle-row">
        <span>🅿️ Illegal Parking / Dwell Trap</span>
        <label class="switch"><input type="checkbox" id="chk-parking" checked><span class="slider"></span></label>
      </div>
      <div class="ctrl-toggle-row">
        <span>🚶 Jaywalking Crosswalk Monitor</span>
        <label class="switch"><input type="checkbox" id="chk-jaywalk" checked><span class="slider"></span></label>
      </div>
      <div class="ctrl-toggle-row">
        <span>🌊 Arterial Green-Wave Coordination</span>
        <label class="switch"><input type="checkbox" id="chk-green-wave" checked><span class="slider"></span></label>
      </div>
      <div class="ctrl-toggle-row">
        <span>⛅ Environmental Weather Auto-Tune</span>
        <label class="switch"><input type="checkbox" id="chk-weather" checked><span class="slider"></span></label>
      </div>
    </div>
  </div>

  <!-- PART 6: REMOTE ALERTS & NOTIFICATIONS -->
  <div>
    <div style="font-size:0.7rem;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;color:#c084fc;margin-bottom:8px">Part 6: 🔔 Remote Alert Channels</div>
    <div style="display:flex;flex-direction:column;gap:8px">
      <div class="ctrl-toggle-row">
        <span>💬 Telegram Incident Bot</span>
        <label class="switch"><input type="checkbox" id="chk-telegram" checked><span class="slider"></span></label>
      </div>
      <div class="ctrl-toggle-row">
        <span>📱 WhatsApp Webhook Dispatch</span>
        <label class="switch"><input type="checkbox" id="chk-whatsapp"><span class="slider"></span></label>
      </div>
    </div>
  </div>

  <!-- PART 7: STORAGE & AUTO-CLEANUP POLICY -->
  <div>
    <div style="font-size:0.7rem;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;color:var(--text-muted);margin-bottom:8px">Part 7: 💾 Storage &amp; Database Retention</div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
      <span style="font-size:0.72rem;font-weight:700;color:var(--text-muted)">Auto-Prune Retention</span>
      <select id="select-retention" class="btn-glass" style="padding:4px 8px;font-size:0.75rem;outline:none">
        <option value="7">7 Days</option>
        <option value="15">15 Days</option>
        <option value="30" selected>30 Days (Default)</option>
        <option value="90">90 Days</option>
      </select>
    </div>
    <button class="btn-glass" onclick="pruneDatabaseNow()" style="width:100%;justify-content:center;font-size:0.78rem">
      🧹 Prune Database Records Now
    </button>
  </div>

  <!-- PART 8: SAVE SETTINGS ACTION -->
  <div style="padding-top:10px;border-top:1px solid var(--border-subtle);display:flex;flex-direction:column;gap:10px">
    <button class="btn-glass" onclick="saveAllSettings()" style="width:100%;justify-content:center;background:linear-gradient(135deg,#a855f7,#7c3aed);color:#fff;font-weight:800;padding:12px;border:none">
      💾 Save All Settings to Database
    </button>
    <button class="btn-glass" onclick="resetSettingsDefaults()" style="width:100%;justify-content:center;font-size:0.74rem;color:var(--text-muted)">
      🔄 Reset to Factory Defaults
    </button>
  </div>
</div>

<!-- 3D SUMMARY MODAL -->
<div class="modal-overlay" id="sum-overlay" onclick="if(event.target===this)closeSummary()">
  <div class="modal-3d card-3d">
    <button onclick="closeSummary()" style="position:absolute;top:20px;right:24px;background:none;border:none;color:var(--text-muted);font-size:1.6rem;cursor:pointer">&times;</button>
    <div style="text-align:center;margin-bottom:24px">
      <div style="font-size:2rem;margin-bottom:10px">📊</div>
      <h2 style="font-size:1.4rem;font-weight:900">Session Intelligence Summary</h2>
      <p id="sum-sub" style="font-size:0.8rem;color:var(--text-dim);margin-top:4px">Aggregated corridor runtime audit</p>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:18px">
      <div class="card-3d" style="padding:14px;text-align:center"><div style="font-size:0.68rem;color:var(--text-muted)">Duration</div><div id="sum-duration" style="font-size:1.4rem;font-weight:800;color:var(--accent-bright);margin-top:4px">—</div></div>
      <div class="card-3d" style="padding:14px;text-align:center"><div style="font-size:0.68rem;color:var(--text-muted)">Total Vehicles</div><div id="sum-vehicles" style="font-size:1.4rem;font-weight:800;color:var(--cyan);margin-top:4px">—</div></div>
      <div class="card-3d" style="padding:14px;text-align:center"><div style="font-size:0.68rem;color:var(--text-muted)">Speeders</div><div id="sum-speeders" style="font-size:1.4rem;font-weight:800;color:var(--red);margin-top:4px">—</div></div>
      <div class="card-3d" style="padding:14px;text-align:center"><div style="font-size:0.68rem;color:var(--text-muted)">Incidents</div><div id="sum-incidents" style="font-size:1.4rem;font-weight:800;color:var(--amber);margin-top:4px">—</div></div>
    </div>
    <div style="background:rgba(168,85,247,0.1);border:1px solid rgba(168,85,247,0.3);border-radius:12px;padding:12px;text-align:center;font-size:0.82rem;margin-bottom:18px">
      🏆 Peak Traffic: <b id="sum-peak-count" style="color:var(--accent-bright)">—</b> vehicles at <b id="sum-peak-time" style="color:var(--cyan)">—</b>
    </div>
    <div style="display:flex;gap:10px">
      <button class="btn-glass" onclick="exportSummary()" style="flex:1;justify-content:center">💾 Export JSON</button>
      <button class="btn-glass" onclick="closeSummary()" style="flex:1;justify-content:center;background:linear-gradient(135deg,#a855f7,#7c3aed);color:#fff;border-color:transparent">Close</button>
    </div>
  </div>
</div>

<script>
// ── 3D CANVAS PERSPECTIVE BACKGROUND ──
(function initCanvasBackground() {
  const canvas = document.getElementById('bg-canvas');
  const ctx = canvas.getContext('2d');
  let width, height, particles = [];

  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
    particles = [];
    for (let i = 0; i < 45; i++) {
      particles.push({
        x: (Math.random() - 0.5) * width * 1.5,
        y: Math.random() * height,
        z: Math.random() * 800 + 100,
        speed: Math.random() * 3 + 2,
        color: i % 3 === 0 ? 'rgba(168, 85, 247, ' : i % 3 === 1 ? 'rgba(6, 182, 212, ' : 'rgba(16, 185, 129, '
      });
    }
  }

  window.addEventListener('resize', resize);
  resize();

  function draw() {
    ctx.clearRect(0, 0, width, height);
    const horizonY = height * 0.28;
    const vpX = width / 2;

    ctx.strokeStyle = 'rgba(168, 85, 247, 0.06)';
    ctx.lineWidth = 1;
    for (let i = -7; i <= 7; i++) {
      ctx.beginPath();
      ctx.moveTo(vpX, horizonY);
      ctx.lineTo(width / 2 + i * (width / 14 * 1.6), height);
      ctx.stroke();
    }

    for (let p of particles) {
      p.z -= p.speed;
      if (p.z <= 20) p.z = 800;
      const scale = 400 / p.z;
      const sx = vpX + p.x * scale * 0.003 * p.z;
      const sy = horizonY + (p.y - horizonY) * scale * 0.8;
      const alpha = Math.min(1, Math.max(0, (1 - p.z / 800) * 0.7));

      if (sx >= 0 && sx <= width && sy >= horizonY && sy <= height) {
        ctx.fillStyle = p.color + alpha + ')';
        ctx.beginPath();
        ctx.arc(sx, sy, Math.max(1, 2.5 * scale), 0, Math.PI * 2);
        ctx.fill();
      }
    }
    requestAnimationFrame(draw);
  }
  draw();
})();

// ── LEAFLET GIS MAP INIT ──
let map, markers = {};
function initMap() {
  map = L.map('city-map').setView([28.6315, 77.2167], 12);
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap'
  }).addTo(map);

  fetch('/api/cameras').then(r => r.json()).then(data => {
    data.cameras.forEach(cam => {
      const marker = L.circleMarker([cam.lat, cam.lng], {
        radius: 9,
        fillColor: cam.color || '#10b981',
        color: '#fff',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.85
      }).addTo(map);

      marker.bindPopup(`<b>${cam.name}</b><br>LOS Grade: <b>${cam.los}</b><br><button onclick="switchCamera('${cam.id}')" style="padding:4px 8px;margin-top:6px;cursor:pointer">Switch View</button>`);
      markers[cam.id] = marker;
    });
  }).catch(() => {});
}
document.addEventListener('DOMContentLoaded', initMap);

function switchCamera(camId) {
  fetch('/api/cameras/select', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ camera_id: camId })
  }).then(r => r.json()).then(d => {
    showToast('info', 'Camera Switched', `Active camera feed set to ${camId}`);
  });
}

// ── DONUT CHART INIT ──
let donutChart;
function initDonutChart() {
  const ctx = document.getElementById('donut-chart').getContext('2d');
  donutChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Cars', 'Buses', 'Trucks', 'Motorbikes', 'Autos', 'Pedestrians'],
      datasets: [{
        data: [45, 12, 8, 30, 15, 10],
        backgroundColor: ['#a855f7', '#06b6d4', '#f59e0b', '#10b981', '#ec4899', '#38bdf8'],
        borderWidth: 0,
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'right', labels: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', size: 10, weight: 600 } } }
      },
      cutout: '72%'
    }
  });
}
document.addEventListener('DOMContentLoaded', initDonutChart);

// ── LINE/BAR CHART INIT ──
const ctxLane = document.getElementById('lane-chart').getContext('2d');
let chart = new Chart(ctxLane, {
  type: 'bar',
  data: { labels: [], datasets: [] },
  options: {
    responsive: true,
    animation: { duration: 300 },
    plugins: {
      legend: { labels: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', size: 11, weight: 600 } } }
    },
    scales: {
      x: { ticks: { color: '#64748b', font: { family: 'JetBrains Mono', size: 10 } }, grid: { color: 'rgba(255,255,255,0.03)' } },
      y: { ticks: { color: '#64748b', font: { family: 'JetBrains Mono', size: 10 } }, grid: { color: 'rgba(255,255,255,0.05)' }, beginAtZero: true }
    }
  }
});

let chartType = 'bar';
function setChartType(t) {
  chartType = t;
  document.getElementById('btn-bar').classList.toggle('active', t === 'bar');
  document.getElementById('btn-line').classList.toggle('active', t === 'line');
  chart.config.type = t;
  chart.update();
}

// ── TOAST NOTIFICATIONS ──
function showToast(severity, title, message) {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = 'toast-card';
  const icon = severity === 'critical' ? '🚨' : severity === 'warning' ? '⚠️' : 'ℹ️';
  toast.innerHTML = `<span style="font-size:1.6rem">${icon}</span><div><div style="font-weight:800;font-size:0.88rem">${title}</div><div style="font-size:0.75rem;opacity:0.9">${message}</div></div>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = 'toast-in 0.3s reverse';
    setTimeout(() => toast.remove(), 280);
  }, 4500);
}

// ── VIOLATION EVIDENCE GALLERY ──
function loadViolations() {
  const filter = document.getElementById('v-filter').value;
  fetch('/api/violations?type=' + filter)
    .then(r => r.json())
    .then(data => {
      const container = document.getElementById('v-gallery');
      if (!data.violations || data.violations.length === 0) {
        container.innerHTML = '<div style="color:var(--text-dim);font-size:0.85rem">No violations recorded under current filter.</div>';
        return;
      }
      container.innerHTML = data.violations.slice(0, 8).map(v => `
        <div class="v-card">
          <img src="/api/evidence/${v.evidence_img || ''}" class="v-thumb" onerror="this.src='data:image/svg+xml;utf8,<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'280\\' height=\\'140\\'><rect width=\\'100%\\' height=\\'100%\\' fill=\\'%23161026\\'/><text x=\\'50%\\' y=\\'50%\\' fill=\\'%2394a3b8\\' text-anchor=\\'middle\\' font-family=\\'sans-serif\\'>EVIDENCE SNAPSHOT</text></svg>'"/>
          <div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px">
            <span class="v-tag">${v.type.replace('_', ' ')}</span>
            <span style="font-family:'JetBrains Mono';font-size:0.75rem;color:var(--text-dim)">${v.timestamp}</span>
          </div>
          <div style="font-weight:800;font-size:0.95rem;margin-top:6px">Plate: <span style="color:var(--accent-bright)">${v.plate_number}</span></div>
          <div style="font-size:0.75rem;color:var(--text-dim);margin:4px 0">${v.details} &bull; Speed: ${v.speed_kmh} km/h</div>
          <button class="btn-glass" onclick="window.open('/api/violations/${v.id}/evidence')" style="width:100%;justify-content:center;margin-top:6px;font-size:0.72rem">📥 Download Evidence (ZIP)</button>
        </div>
      `).join('');
    }).catch(() => {});
}

// ── SIGNAL STRATEGY SWITCH ──
function changeSignalStrategy(strategy) {
  fetch('/api/signals/strategy', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ strategy: strategy })
  }).then(r => r.json()).then(d => {
    showToast('info', 'Signal Strategy Updated', `Autonomous controller shifted to ${strategy.toUpperCase()}`);
  });
}

// ── THEME TOGGLE ──
function toggleTheme() {
  document.body.classList.toggle('light-theme');
  const isLight = document.body.classList.contains('light-theme');
  localStorage.setItem('traffiQ_theme', isLight ? 'light' : 'dark');
}
if (localStorage.getItem('traffiQ_theme') === 'light') {
  document.body.classList.add('light-theme');
}

// ── TELEMETRY RENDERING ──
let paused = false, selectedLane = null, lastData = {};

function renderData(s, hist) {
  document.getElementById('k-veh').textContent = s.vehicle_count ?? '—';
  document.getElementById('k-lanes').textContent = Object.keys(s.lane_counts || {}).length;
  document.getElementById('k-fps').textContent = s.fps ?? '—';
  document.getElementById('k-latency').textContent = 'Latency: ' + (s.latency_ms ?? 18) + 'ms';
  document.getElementById('k-violations').textContent = (s.violations || []).length;
  document.getElementById('k-pedestrians').textContent = s.pedestrians_count ?? 0;
  
  // Weather
  if (s.weather_condition) {
    document.getElementById('weather-txt').textContent = s.weather_condition + ' (' + Math.round((s.weather_score || 1) * 100) + '%)';
    document.getElementById('weather-icon').textContent = s.weather_condition.includes('Night') ? '🌙' : s.weather_condition.includes('Rain') ? '🌧️' : s.weather_condition.includes('Fog') ? '🌫️' : '☀️';
  }

  // Signal
  if (s.signal_status) {
    const strat = (s.signal_status.strategy || 'adaptive').toUpperCase();
    document.getElementById('k-signal-strategy').textContent = strat;
    document.getElementById('k-signal-timer').textContent = `Lane ${s.signal_status.active_green_lane} Green (${s.signal_status.remaining_s}s)`;
  }

  // Emergency banner
  const emb = document.getElementById('em-banner');
  if (s.emergency_active || (s.signal_status && s.signal_status.emergency_corridor)) {
    emb.style.display = 'block';
  } else {
    emb.style.display = 'none';
  }

  // Donut chart update
  if (donutChart && s.vehicle_classes) {
    const vc = s.vehicle_classes;
    donutChart.data.datasets[0].data = [vc.car || 0, vc.bus || 0, vc.truck || 0, vc.motorbike || 0, vc.auto || 0, vc.pedestrian || 0];
    donutChart.update('none');
  }

  // Lane Table
  const tb = document.getElementById('lane-tbody');
  tb.innerHTML = '';
  for (const [lid, counts] of Object.entries(s.lane_counts || {})) {
    const total = Object.values(counts).reduce((a, b) => a + b, 0);
    const los = (s.lane_los || {})[lid] || 'B';
    const flow = (s.lane_flow || {})[lid] ?? '—';
    const arrow = (s.lane_trends || {})[lid] || '→';
    const pred = (s.lane_predictions || {})[lid] ?? '—';
    const stateColor = (s.signal_status && s.signal_status.active_green_lane == lid) ? '<b style="color:var(--green)">GREEN</b>' : '<b style="color:var(--red)">RED</b>';

    tb.innerHTML += `
      <tr onclick="selectLane('${lid}')" ${String(selectedLane) === String(lid) ? 'class="lane-selected"' : ''}>
        <td><b style="color:#fff">Lane ${lid}</b></td>
        <td>${counts.car || 0}</td><td>${counts.bus || 0}</td>
        <td>${counts.truck || 0}</td><td>${counts.motorbike || 0}</td>
        <td>${counts.pedestrian || 0}</td>
        <td><b style="color:var(--accent-bright)">${total}</b></td>
        <td><span class="los-pill badge-green">${los}</span></td>
        <td>${typeof flow === 'number' ? flow.toFixed(1) : flow}</td>
        <td>${stateColor}</td>
        <td style="font-weight:800">${arrow}</td>
        <td style="color:var(--accent-bright);font-weight:800">${pred}</td>
      </tr>`;
  }

  // Forecasts
  if (s.forecast_15m && s.forecast_15m['1']) {
    document.getElementById('fc-15').textContent = `${s.forecast_15m['1'].count} veh (LOS ${s.forecast_15m['1'].los})`;
  }
  if (s.forecast_30m && s.forecast_30m['1']) {
    document.getElementById('fc-30').textContent = `${s.forecast_30m['1'].count} veh (LOS ${s.forecast_30m['1'].los})`;
  }
  if (s.forecast_60m && s.forecast_60m['1']) {
    document.getElementById('fc-60').textContent = `${s.forecast_60m['1'].count} veh (LOS ${s.forecast_60m['1'].los})`;
  }

  // Update History Chart
  if (hist && hist.length) {
    chart.data.labels = hist.map(h => h.t);
    const lids = [...new Set(hist.flatMap(h => Object.keys(h.lanes || {})))].sort();
    chart.data.datasets = lids.map((lid, i) => ({
      label: 'Lane ' + lid,
      data: hist.map(h => (h.lanes || {})[lid] ?? 0),
      backgroundColor: i % 2 === 0 ? '#a855f788' : '#06b6d488',
      borderColor: i % 2 === 0 ? '#a855f7' : '#06b6d4',
      borderWidth: chartType === 'bar' ? 0 : 2
    }));
    chart.update('none');
  }

  syncControlUI(s);
}

async function poll() {
  if (paused) return;
  try {
    const [sr, hr, ar] = await Promise.all([fetch('/api/stats'), fetch('/api/history'), fetch('/api/alerts')]);
    if (!sr.ok || !hr.ok) throw new Error();
    lastData = { s: await sr.json(), hist: await hr.json() };
    renderData(lastData.s, lastData.hist);

    // Render new toasts from server
    if (ar.ok) {
      const aData = await ar.json();
      if (aData.toasts && aData.toasts.length) {
        const topToast = aData.toasts[0];
        if (!window._lastToastId || window._lastToastId !== topToast.id) {
          window._lastToastId = topToast.id;
          showToast(topToast.severity, topToast.title, topToast.message);
        }
      }
    }
  } catch (e) {}
}

function selectLane(lid) {
  selectedLane = (String(selectedLane) === String(lid)) ? null : lid;
  if (lastData.s) renderData(lastData.s, lastData.hist);
}

function togglePause() {
  paused = !paused;
  document.getElementById('btn-pause').textContent = paused ? '▶️ Resume' : '⏸️ Pause';
  document.getElementById('btn-pause').classList.toggle('active', paused);
}

// ── SIDEBAR CONTROLS ──
let sidebarOpen = false;
function toggleSidebar() {
  sidebarOpen = !sidebarOpen;
  document.getElementById('ctrl-sidebar').classList.toggle('open', sidebarOpen);
  document.getElementById('ctrl-toggle-btn').classList.toggle('open', sidebarOpen);
  document.getElementById('ctrl-overlay').style.display = sidebarOpen ? 'block' : 'none';
}

function setMode(m) {
  fetch('/api/control/update', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mode: m })
  });
  ['lanes', 'heatmap', 'speed', 'timer'].forEach(mode => {
    document.getElementById('mbtn-' + mode).classList.toggle('active', mode === m);
  });
}

function onSliderInput(id, txt, f) {
  const el = document.getElementById('val-' + id);
  if (el) el.textContent = txt;
}

function onSliderChange(field, val) {
  const obj = {};
  obj[field] = (field === 'speed_limit') ? parseInt(val) : parseFloat(val);
  fetch('/api/control/update', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(obj)
  });
}

function syncControlUI(s) {
  const activeMode = s.mode || 'lanes';
  ['lanes', 'heatmap', 'speed', 'timer'].forEach(m => {
    const btn = document.getElementById('mbtn-' + m);
    if (btn) btn.classList.toggle('active', m === activeMode);
  });
}

// ── SETTINGS SIDEBAR ACTIONS ──
async function saveAllSettings() {
  const confEl = document.getElementById('slider-conf-thresh');
  const spdEl = document.getElementById('slider-speed-limit');
  const incEl = document.getElementById('slider-incident-timeout');
  const stratEl = document.getElementById('select-signal-strategy');
  const retEl = document.getElementById('select-retention');

  const settings = {
    conf_threshold: confEl ? parseFloat(confEl.value) : 0.25,
    speed_limit: spdEl ? parseInt(spdEl.value) : 50,
    incident_timeout: incEl ? parseFloat(incEl.value) : 5.0,
    signal_mode: stratEl ? stratEl.value : 'adaptive',
    retention_days: retEl ? parseInt(retEl.value) : 30,
    enforcement_red_light: document.getElementById('chk-red-light')?.checked ?? true,
    enforcement_wrong_way: document.getElementById('chk-wrong-way')?.checked ?? true,
    enforcement_helmet: document.getElementById('chk-helmet')?.checked ?? true,
    enforcement_parking: document.getElementById('chk-parking')?.checked ?? true,
    enforcement_jaywalk: document.getElementById('chk-jaywalk')?.checked ?? true,
    enforcement_green_wave: document.getElementById('chk-green-wave')?.checked ?? true,
    enforcement_weather: document.getElementById('chk-weather')?.checked ?? true,
    telegram_alerts: document.getElementById('chk-telegram')?.checked ?? true,
    whatsapp_alerts: document.getElementById('chk-whatsapp')?.checked ?? false
  };

  try {
    const res = await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings)
    });
    if (res.ok) {
      if (typeof spawnToast === 'function') {
        spawnToast('Settings Saved', 'System parameters stored in SQLite and applied live.', '💾');
      }
    }
  } catch (err) {
    console.error('Save settings error:', err);
  }
}

async function pruneDatabaseNow() {
  const retEl = document.getElementById('select-retention');
  const days = retEl ? parseInt(retEl.value) : 30;
  try {
    const res = await fetch('/api/database/cleanup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ days: days })
    });
    if (res.ok) {
      if (typeof spawnToast === 'function') {
        spawnToast('Database Pruned', `Historical logs older than ${days} days deleted.`, '🧹');
      }
    }
  } catch (err) {
    console.error('Prune database error:', err);
  }
}

function onStrategySelect(val) {
  fetch('/api/signals/strategy', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ strategy: val })
  });
  if (typeof spawnToast === 'function') {
    spawnToast('Strategy Updated', `Signal mode switched to ${val.toUpperCase()}.`, '🚦');
  }
}

function resetSettingsDefaults() {
  if (document.getElementById('slider-conf-thresh')) {
    document.getElementById('slider-conf-thresh').value = 0.25;
    document.getElementById('val-conf-thresh').textContent = '25%';
  }
  if (document.getElementById('slider-speed-limit')) {
    document.getElementById('slider-speed-limit').value = 50;
    document.getElementById('val-speed-limit').textContent = '50 km/h';
  }
  if (document.getElementById('slider-incident-timeout')) {
    document.getElementById('slider-incident-timeout').value = 5;
    document.getElementById('val-incident-timeout').textContent = '5s';
  }
  if (document.getElementById('select-signal-strategy')) {
    document.getElementById('select-signal-strategy').value = 'adaptive';
  }
  saveAllSettings();
}

async function loadSavedSettings() {
  try {
    const res = await fetch('/api/settings');
    if (!res.ok) return;
    const d = await res.json();
    if (d.conf_threshold != null && document.getElementById('slider-conf-thresh')) {
      document.getElementById('slider-conf-thresh').value = d.conf_threshold;
      document.getElementById('val-conf-thresh').textContent = Math.round(d.conf_threshold * 100) + '%';
    }
    if (d.speed_limit != null && document.getElementById('slider-speed-limit')) {
      document.getElementById('slider-speed-limit').value = d.speed_limit;
      document.getElementById('val-speed-limit').textContent = d.speed_limit + ' km/h';
    }
    if (d.incident_timeout != null && document.getElementById('slider-incident-timeout')) {
      document.getElementById('slider-incident-timeout').value = d.incident_timeout;
      document.getElementById('val-incident-timeout').textContent = d.incident_timeout + 's';
    }
    if (d.signal_mode != null && document.getElementById('select-signal-strategy')) {
      document.getElementById('select-signal-strategy').value = d.signal_mode;
    }
    if (d.retention_days != null && document.getElementById('select-retention')) {
      document.getElementById('select-retention').value = d.retention_days;
    }
  } catch (e) {}
}
loadSavedSettings();

// ── SUMMARY MODAL ──
function openSummary() {
  fetch('/api/summary').then(r => r.json()).then(d => {
    document.getElementById('sum-duration').textContent = d.duration ?? '—';
    document.getElementById('sum-vehicles').textContent = d.total_vehicles ?? '—';
    document.getElementById('sum-speeders').textContent = d.speeders ?? '—';
    document.getElementById('sum-incidents').textContent = d.total_incidents ?? '—';
    document.getElementById('sum-peak-count').textContent = d.peak_count ?? '—';
    document.getElementById('sum-peak-time').textContent = d.peak_time || 'N/A';
    document.getElementById('sum-overlay').classList.add('open');
  });
}
function closeSummary() {
  document.getElementById('sum-overlay').classList.remove('open');
}
function exportSummary() {
  window.open('/api/reports/download/excel');
}

// ── EMERGENCY PREEMPTION HISTORY & DISPATCH (MAIN DASHBOARD) ──
let lastDashPreemptState = false;

async function loadDashboardEmergencyHistory() {
  try {
    const res = await fetch('/api/emergency/stats');
    if (!res.ok) return;
    const data = await res.json();

    // 1. Update mini KPI chips
    const stats = data.stats || {};
    const totalEl = document.getElementById('em-chip-total');
    if (totalEl) totalEl.textContent = stats.total_transits || 0;
    const ambEl = document.getElementById('em-chip-amb');
    if (ambEl) ambEl.textContent = stats.ambulance_count || 0;
    const fireEl = document.getElementById('em-chip-fire');
    if (fireEl) fireEl.textContent = stats.fire_engine_count || 0;
    const polEl = document.getElementById('em-chip-police');
    if (polEl) polEl.textContent = stats.police_count || 0;
    const resEl = document.getElementById('em-chip-rescue');
    if (resEl) resEl.textContent = stats.rescue_count || 0;

    // 2. Preemption Status Pill
    const isPreempted = !!data.active_preemption;
    const activeLane = data.active_lane || 1;
    const activeVeh = data.active_vehicle_type || 'Emergency Vehicle';
    const pill = document.getElementById('dash-preemption-pill');
    if (pill) {
      if (isPreempted) {
        pill.className = 'state-pill-emergency active';
        pill.innerHTML = `<span>🚨</span> PREEMPTION ACTIVE: LANE ${activeLane} (${activeVeh})`;
        if (!lastDashPreemptState) {
          showToast('critical', `Emergency Priority Override!`, `Lane ${activeLane} signal overridden: RED ➔ GREEN to give way for ${activeVeh}.`);
        }
      } else {
        pill.className = 'state-pill-emergency standby';
        pill.innerHTML = `<span style="font-size:0.6rem">●</span> STANDBY / MONITORING`;
      }
    }
    lastDashPreemptState = isPreempted;

    // 3. Populate Table Rows
    const tbody = document.getElementById('dash-emergency-table-body');
    if (!tbody) return;
    const transits = data.recent_transits || [];
    if (transits.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;color:var(--text-muted);padding:24px">No emergency transits recorded yet. Click one of the dispatch buttons above to test preemption!</td></tr>';
    } else {
      tbody.innerHTML = transits.map(t => {
        let badgeCls = 'badge-amb';
        let icon = '🚑';
        if (t.vehicle_type.includes('Fire')) { badgeCls = 'badge-fire'; icon = '🚒'; }
        else if (t.vehicle_type.includes('Police')) { badgeCls = 'badge-police'; icon = '🚓'; }
        else if (t.vehicle_type.includes('Rescue')) { badgeCls = 'badge-rescue'; icon = '🚜'; }

        return `
          <tr>
            <td style="color:var(--text-dim);font-family:'JetBrains Mono'">#${t.id}</td>
            <td style="font-family:'JetBrains Mono'">${t.timestamp.replace('T', ' ')}</td>
            <td><span class="badge-veh ${badgeCls}">${icon} ${t.vehicle_type}</span></td>
            <td><b style="color:#fff">Lane ${t.lane_id}</b></td>
            <td><span style="color:#6ee7b7;font-weight:700;font-family:'JetBrains Mono'">${t.speed_kmh.toFixed(1)} km/h</span></td>
            <td><span style="color:#f87171;font-weight:700">🔴 ${t.prior_signal_state}</span> ➔ <span style="color:#34d399;font-weight:700">🟢 ${t.new_signal_state}</span></td>
            <td><span style="font-family:'JetBrains Mono'">${t.duration_seconds}s</span></td>
            <td><span style="color:#34d399;font-weight:700">✔ ${t.status}</span></td>
          </tr>
        `;
      }).join('');
    }
  } catch (err) {
    console.error('Error fetching dashboard emergency data:', err);
  }
}

async function dashDispatchEmergency(vType, lane, speed) {
  try {
    const res = await fetch('/api/emergency/trigger', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ vehicle_type: vType, lane_id: lane, speed_kmh: speed, duration_seconds: 35 })
    });
    const d = await res.json();
    showToast('critical', `${vType} Priority Corridor Active!`, `Lane ${lane} signal automatically overridden from RED to GREEN.`);
    loadDashboardEmergencyHistory();
  } catch (err) {
    console.error(err);
  }
}

async function dashClearEmergency() {
  try {
    await fetch('/api/emergency/clear', { method: 'POST' });
    showToast('info', 'Corridor Cleared', 'Traffic signals resumed standard autonomous adaptive cycle.');
    loadDashboardEmergencyHistory();
  } catch (err) {
    console.error(err);
  }
}

// Initial polls
poll();
setInterval(poll, 2000);
loadViolations();
setInterval(loadViolations, 8000);
loadDashboardEmergencyHistory();
setInterval(loadDashboardEmergencyHistory, 2000);
</script>
</body>
</html>
"""

LANDING_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>TraffiQ — Neural Traffic Platform</title>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;700;800&display=swap" rel="stylesheet"/>
  <style>
    :root {
      --bg: #06040c;
      --border-subtle: rgba(168, 85, 247, 0.2);
      --border-glow: rgba(168, 85, 247, 0.45);
      --accent: #a855f7;
      --accent-bright: #c084fc;
      --cyan: #06b6d4;
      --text: #f1f5f9;
      --text-muted: #94a3b8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Plus Jakarta Sans', sans-serif; background: var(--bg); color: var(--text); overflow-x: hidden; }
    nav { display: flex; justify-content: space-between; align-items: center; padding: 18px 48px; border-bottom: 1px solid var(--border-subtle); backdrop-filter: blur(20px); }
    .hero { max-width: 1200px; margin: 80px auto; padding: 0 24px; text-align: center; }
    .hero-h1 { font-size: clamp(2.6rem, 5vw, 4.4rem); font-weight: 900; line-height: 1.05; letter-spacing: -0.04em; margin-bottom: 22px; }
    .hero-h1 span { background: linear-gradient(135deg, #ffffff 40%, #c084fc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .btn-main { padding: 15px 36px; border-radius: 12px; background: linear-gradient(135deg, #a855f7, #6366f1); color: #fff; font-weight: 800; border: none; cursor: pointer; box-shadow: 0 8px 30px rgba(168, 85, 247, 0.45); }
    .modal-overlay { display: none; position: fixed; inset: 0; z-index: 1000; background: rgba(6, 4, 12, 0.85); backdrop-filter: blur(16px); align-items: center; justify-content: center; }
    .modal-overlay.open { display: flex; }
    .modal-box { background: #130d24; border: 1px solid var(--border-glow); border-radius: 24px; padding: 40px; width: 100%; max-width: 420px; }
    .form-input { width: 100%; padding: 12px 16px; border-radius: 10px; background: #06040c; border: 1px solid var(--border-subtle); color: #fff; margin-bottom: 16px; outline: none; }
  </style>
</head>
<body>
<nav>
  <div style="display:flex;align-items:center;gap:12px;font-size:1.3rem;font-weight:900">🚦 TraffiQ Platform</div>
  <form method="POST" action="/login" style="margin:0">
    <input type="hidden" name="username" value="{{ default_user or 'admin' }}"/>
    <input type="hidden" name="password" value="{{ default_pass or 'admin123' }}"/>
    <button class="btn-main" type="submit" style="padding:10px 24px;font-size:0.85rem">⚡ Auto Sign In (admin)</button>
  </form>
</nav>

<div class="hero">
  <div style="font-size:0.75rem;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;color:var(--accent-bright);margin-bottom:20px">Phase 1-7 Autonomous Vision System</div>
  <h1 class="hero-h1">Real-Time Traffic Intelligence &amp; <span>Signal Control</span></h1>
  <p style="color:var(--text-muted);font-size:1.1rem;max-width:650px;margin:0 auto 36px;line-height:1.6">YOLOv8 + ByteTrack multi-object tracking, red-light &amp; wrong-way enforcement, plate recognition, multi-step 15m/30m/60m forecasting, and autonomous signal coordination.</p>
  
  <div style="display:flex;justify-content:center;gap:16px;flex-wrap:wrap">
    <form method="POST" action="/login" style="margin:0">
      <input type="hidden" name="username" value="{{ default_user or 'admin' }}"/>
      <input type="hidden" name="password" value="{{ default_pass or 'admin123' }}"/>
      <button class="btn-main" type="submit">🚀 One-Click Auto Login (admin)</button>
    </form>
    <button class="btn-main" onclick="openLogin()" style="background:rgba(255,255,255,0.08);border:1px solid var(--border-subtle);box-shadow:none">🔑 Enter Custom Credentials</button>
  </div>
</div>

<div class="modal-overlay" id="modal-overlay" onclick="if(event.target===this)closeLogin()">
  <div class="modal-box">
    <h2 style="font-size:1.4rem;font-weight:800;margin-bottom:6px;text-align:center">Console Authentication</h2>
    <p style="font-size:0.8rem;color:var(--text-muted);margin-bottom:20px;text-align:center">Sign in with administrator credentials</p>
    <form method="POST" action="/login">
      <div style="margin-bottom:6px;font-size:0.75rem;color:var(--text-muted);font-weight:700">USERNAME</div>
      <input class="form-input" type="text" name="username" id="username" value="{{ default_user or 'admin' }}" placeholder="Username (admin)" required/>
      <div style="margin-bottom:6px;font-size:0.75rem;color:var(--text-muted);font-weight:700">PASSWORD</div>
      <input class="form-input" type="password" name="password" id="password" value="{{ default_pass or 'admin123' }}" placeholder="Password (admin123)" required/>
      <div style="margin-bottom:16px;font-size:0.75rem;color:#c084fc;display:flex;align-items:center;gap:6px">
        <span>✔</span> Username &amp; password automatically filled
      </div>
      <button class="btn-main" style="width:100%" type="submit">Access Command Center</button>
    </form>
  </div>
</div>

<script>
function openLogin() { document.getElementById('modal-overlay').classList.add('open'); }
function closeLogin() { document.getElementById('modal-overlay').classList.remove('open'); }
if (new URLSearchParams(window.location.search).get('error') === '1') openLogin();
</script>
</body>
</html>
"""

# ─────────────────────────────────────────────────────────────
# TraffiQ — Emergency Vehicle Priority Corridor Console UI
# ─────────────────────────────────────────────────────────────

EMERGENCY_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>TraffiQ — Emergency Priority Corridor Console</title>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700;800&display=swap" rel="stylesheet"/>
  
  <style>
    :root {
      --bg: #06040c;
      --bg-surface: rgba(16, 12, 28, 0.78);
      --bg-surface-elevated: rgba(26, 18, 44, 0.88);
      --border-subtle: rgba(168, 85, 247, 0.16);
      --border-glow: rgba(168, 85, 247, 0.45);
      --accent: #a855f7;
      --accent-bright: #c084fc;
      --cyan: #06b6d4;
      --green: #10b981;
      --amber: #f59e0b;
      --red: #ef4444;
      --text: #f1f5f9;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      --shadow-3d: 0 12px 36px -8px rgba(0, 0, 0, 0.65), 0 0 24px -4px rgba(239, 68, 68, 0.2);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Plus Jakarta Sans', sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      overflow-x: hidden;
      background-image: 
        radial-gradient(circle at 15% 15%, rgba(239, 68, 68, 0.12) 0%, transparent 40%),
        radial-gradient(circle at 85% 85%, rgba(168, 85, 247, 0.1) 0%, transparent 40%),
        linear-gradient(rgba(168, 85, 247, 0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(168, 85, 247, 0.02) 1px, transparent 1px);
      background-size: 100% 100%, 100% 100%, 36px 36px, 36px 36px;
    }

    .wrap {
      max-width: 1440px;
      margin: 0 auto;
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }

    /* CARD 3D */
    .card-3d {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 20px;
      padding: 24px;
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      box-shadow: var(--shadow-3d);
      position: relative;
    }

    /* HEADER */
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 16px;
    }

    .brand-group {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .brand-orb {
      width: 52px;
      height: 52px;
      border-radius: 16px;
      background: linear-gradient(135deg, #ef4444, #b91c1c);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.8rem;
      box-shadow: 0 0 25px rgba(239, 68, 68, 0.5);
      animation: pulse-orb 2s infinite ease-in-out;
    }

    @keyframes pulse-orb {
      0%, 100% { transform: scale(1); box-shadow: 0 0 25px rgba(239, 68, 68, 0.5); }
      50% { transform: scale(1.05); box-shadow: 0 0 40px rgba(239, 68, 68, 0.8); }
    }

    .brand-titles h1 {
      font-size: 1.5rem;
      font-weight: 800;
      letter-spacing: -0.02em;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .brand-titles p {
      font-size: 0.8rem;
      color: var(--text-muted);
      margin-top: 3px;
    }

    .btn-glass {
      padding: 10px 18px;
      border-radius: 12px;
      font-family: inherit;
      font-size: 0.82rem;
      font-weight: 700;
      cursor: pointer;
      border: 1px solid var(--border-subtle);
      background: rgba(26, 18, 44, 0.6);
      color: var(--text);
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      text-decoration: none;
    }

    .btn-glass:hover {
      border-color: var(--red);
      background: rgba(239, 68, 68, 0.15);
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(239, 68, 68, 0.3);
    }

    .btn-danger {
      background: linear-gradient(135deg, #ef4444, #dc2626);
      border-color: rgba(255, 255, 255, 0.2);
      color: #fff;
    }

    .btn-danger:hover {
      box-shadow: 0 6px 25px rgba(239, 68, 68, 0.6);
      transform: translateY(-2px);
    }

    .btn-success {
      background: linear-gradient(135deg, #10b981, #059669);
      border-color: rgba(255, 255, 255, 0.2);
      color: #fff;
    }

    /* EMERGENCY HERO BANNER */
    .emergency-banner {
      background: linear-gradient(135deg, rgba(239, 68, 68, 0.25), rgba(185, 28, 28, 0.35));
      border: 2px solid var(--red);
      border-radius: 18px;
      padding: 20px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
      box-shadow: 0 0 35px rgba(239, 68, 68, 0.45);
      animation: banner-glow 1.5s infinite alternate ease-in-out;
    }

    @keyframes banner-glow {
      from { box-shadow: 0 0 20px rgba(239, 68, 68, 0.3); }
      to { box-shadow: 0 0 45px rgba(239, 68, 68, 0.75); }
    }

    .banner-icon {
      font-size: 2.8rem;
      animation: siren-spin 0.8s infinite linear alternate;
    }

    @keyframes siren-spin {
      from { transform: rotate(-15deg) scale(1); }
      to { transform: rotate(15deg) scale(1.15); }
    }

    /* KPI STATS GRID */
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
    }

    .kpi-card {
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      border-radius: 16px;
      padding: 18px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      position: relative;
      overflow: hidden;
    }

    .kpi-card::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 4px;
      height: 100%;
      background: var(--accent);
      border-radius: 4px 0 0 4px;
    }

    .kpi-card.red::before { background: var(--red); }
    .kpi-card.amber::before { background: var(--amber); }
    .kpi-card.cyan::before { background: var(--cyan); }
    .kpi-card.green::before { background: var(--green); }

    .kpi-val {
      font-size: 2rem;
      font-weight: 800;
      font-family: 'JetBrains Mono', monospace;
      color: #fff;
    }

    .kpi-label {
      font-size: 0.74rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 6px;
    }

    /* INTERSECTION LANES & SIGNALS VISUALIZER */
    .lanes-visual-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }

    .lane-box {
      background: rgba(14, 10, 24, 0.8);
      border: 1px solid var(--border-subtle);
      border-radius: 18px;
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 18px;
      position: relative;
    }

    .lane-box.emergency-corridor-active {
      border-color: var(--green);
      box-shadow: 0 0 30px rgba(16, 185, 129, 0.35);
      background: linear-gradient(180deg, rgba(16, 185, 129, 0.08) 0%, rgba(14, 10, 24, 0.9) 100%);
    }

    .lane-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .signal-head-container {
      display: flex;
      align-items: center;
      gap: 24px;
    }

    /* REALISTIC 3-LENS TRAFFIC LIGHT */
    .traffic-light-fixture {
      width: 70px;
      height: 180px;
      background: #111827;
      border: 3px solid #374151;
      border-radius: 20px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: space-around;
      padding: 10px 0;
      box-shadow: inset 0 0 10px #000, 0 10px 25px rgba(0, 0, 0, 0.8);
    }

    .lens {
      width: 44px;
      height: 44px;
      border-radius: 50%;
      background: #1f2937;
      border: 2px solid rgba(255, 255, 255, 0.05);
      transition: all 0.3s;
    }

    .lens.red.lit {
      background: radial-gradient(circle at 35% 35%, #fca5a5, #ef4444);
      box-shadow: 0 0 25px rgba(239, 68, 68, 0.9), inset 0 0 10px rgba(255, 255, 255, 0.6);
    }

    .lens.amber.lit {
      background: radial-gradient(circle at 35% 35%, #fde68a, #f59e0b);
      box-shadow: 0 0 25px rgba(245, 158, 11, 0.9), inset 0 0 10px rgba(255, 255, 255, 0.6);
    }

    .lens.green.lit {
      background: radial-gradient(circle at 35% 35%, #a7f3d0, #10b981);
      box-shadow: 0 0 35px rgba(16, 185, 129, 1), inset 0 0 12px rgba(255, 255, 255, 0.8);
      animation: green-beacon 1.2s infinite alternate;
    }

    @keyframes green-beacon {
      from { transform: scale(1); filter: brightness(1); }
      to { transform: scale(1.08); filter: brightness(1.2); }
    }

    .signal-status-details {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .state-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 14px;
      border-radius: 10px;
      font-size: 0.85rem;
      font-weight: 800;
      width: fit-content;
    }

    .state-pill.red {
      background: rgba(239, 68, 68, 0.2);
      border: 1px solid var(--red);
      color: #fca5a5;
    }

    .state-pill.green {
      background: rgba(16, 185, 129, 0.2);
      border: 1px solid var(--green);
      color: #6ee7b7;
    }

    .state-pill.preempted {
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.3), rgba(6, 182, 212, 0.3));
      border: 1px solid #34d399;
      color: #fff;
      animation: pulse-preempt 1s infinite alternate;
    }

    @keyframes pulse-preempt {
      from { box-shadow: 0 0 10px rgba(16, 185, 129, 0.4); }
      to { box-shadow: 0 0 25px rgba(16, 185, 129, 0.9); }
    }

    /* SIMULATION DISPATCHER */
    .dispatch-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
      margin-top: 14px;
    }

    .dispatch-btn {
      padding: 14px 16px;
      border-radius: 14px;
      border: 1px solid var(--border-subtle);
      background: var(--bg-surface-elevated);
      color: #fff;
      font-family: inherit;
      font-size: 0.85rem;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 12px;
      transition: all 0.25s;
    }

    .dispatch-btn:hover {
      transform: translateY(-3px);
      border-color: var(--accent-bright);
      background: rgba(168, 85, 247, 0.2);
      box-shadow: 0 8px 24px rgba(168, 85, 247, 0.3);
    }

    .dispatch-btn.amb:hover { border-color: #ef4444; background: rgba(239, 68, 68, 0.2); box-shadow: 0 8px 24px rgba(239, 68, 68, 0.35); }
    .dispatch-btn.fire:hover { border-color: #f97316; background: rgba(249, 115, 22, 0.2); box-shadow: 0 8px 24px rgba(249, 115, 22, 0.35); }
    .dispatch-btn.police:hover { border-color: #3b82f6; background: rgba(59, 130, 246, 0.2); box-shadow: 0 8px 24px rgba(59, 130, 246, 0.35); }
    .dispatch-btn.rescue:hover { border-color: #eab308; background: rgba(234, 179, 8, 0.2); box-shadow: 0 8px 24px rgba(234, 179, 8, 0.35); }

    /* TABLE */
    table {
      width: 100%;
      border-collapse: collapse;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.82rem;
    }

    th {
      padding: 12px 16px;
      text-align: left;
      font-size: 0.7rem;
      text-transform: uppercase;
      color: var(--text-muted);
      border-bottom: 1px solid var(--border-subtle);
      background: rgba(16, 12, 28, 0.5);
    }

    td {
      padding: 14px 16px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    }

    tbody tr:hover td {
      background: rgba(239, 68, 68, 0.08);
    }

    .badge-veh {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 8px;
      font-weight: 700;
      font-size: 0.78rem;
    }

    .badge-amb    { background: rgba(239, 68, 68, 0.2);  color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); }
    .badge-fire   { background: rgba(249, 115, 22, 0.2); color: #fb923c; border: 1px solid rgba(249, 115, 22, 0.4); }
    .badge-police { background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.4); }
    .badge-rescue { background: rgba(234, 179, 8, 0.2);  color: #facc15; border: 1px solid rgba(234, 179, 8, 0.4); }

    /* TOAST */
    #toast-container {
      position: fixed;
      top: 24px;
      right: 24px;
      z-index: 9999;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .toast {
      background: rgba(16, 12, 28, 0.95);
      border: 1px solid var(--red);
      border-radius: 14px;
      padding: 16px 20px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8), 0 0 20px rgba(239, 68, 68, 0.4);
      display: flex;
      align-items: center;
      gap: 12px;
      animation: toast-in 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes toast-in {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
  </style>
</head>
<body>

<div id="toast-container"></div>

<div class="wrap">

  <!-- HEADER -->
  <header class="card-3d">
    <div class="brand-group">
      <div class="brand-orb">🚨</div>
      <div class="brand-titles">
        <h1>Emergency Priority Corridor Console</h1>
        <p>Automated Red-to-Green Signal Preemption &bull; Give-Way Safety Enforcement</p>
      </div>
    </div>

    <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">
      <div id="preemption-pill" class="state-pill red">
        <span style="font-size:0.6rem">●</span> STANDBY / MONITORING
      </div>
      <a href="/" class="btn-glass">← Main Traffic Command</a>
    </div>
  </header>

  <!-- LIVE EMERGENCY BANNER (Dynamic) -->
  <div class="emergency-banner" id="active-banner" style="display:none">
    <div style="display:flex;align-items:center;gap:18px">
      <div class="banner-icon" id="banner-icon">🚑</div>
      <div>
        <div style="font-size:1.15rem;font-weight:800;letter-spacing:-0.01em;display:flex;align-items:center;gap:8px">
          <span id="banner-title">EMERGENCY CORRIDOR ACTIVATED</span>
          <span style="font-size:0.75rem;padding:3px 8px;border-radius:6px;background:rgba(255,255,255,0.2);font-weight:700">RED ➔ GREEN OVERRIDE</span>
        </div>
        <p style="font-size:0.85rem;color:#fecaca;margin-top:4px" id="banner-desc">
          Emergency vehicle approaching Lane 1. Signal automatically transitioned to GREEN to give way. Conflicting lanes held at RED.
        </p>
      </div>
    </div>
    <div style="text-align:right">
      <button class="btn-glass btn-danger" onclick="resetCorridor()">⏹️ Reset Corridor</button>
    </div>
  </div>

  <!-- KPI SUMMARY CARDS -->
  <div class="kpi-grid">
    <div class="kpi-card red">
      <div class="kpi-label">🚨 Total Emergency Transits</div>
      <div class="kpi-val" id="kpi-total">0</div>
    </div>
    <div class="kpi-card red">
      <div class="kpi-label">🚑 Ambulances Responded</div>
      <div class="kpi-val" id="kpi-amb">0</div>
    </div>
    <div class="kpi-card amber">
      <div class="kpi-label">🚒 Fire Engines &amp; Trucks</div>
      <div class="kpi-val" id="kpi-fire">0</div>
    </div>
    <div class="kpi-card cyan">
      <div class="kpi-label">🚓 Police Patrols</div>
      <div class="kpi-val" id="kpi-police">0</div>
    </div>
    <div class="kpi-card amber">
      <div class="kpi-label">🚜 Rescue Trucks</div>
      <div class="kpi-val" id="kpi-rescue">0</div>
    </div>
    <div class="kpi-card green">
      <div class="kpi-label">⚡ Preemption Clearance Window</div>
      <div class="kpi-val" id="kpi-duration">30s</div>
    </div>
  </div>

  <!-- INTERSECTION LANES & TRAFFIC LIGHT VISUALIZER -->
  <div class="card-3d">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:18px">
      <div>
        <h2 style="font-size:1.15rem;font-weight:800">🚦 Live Corridor Signal &amp; Preemption Monitor</h2>
        <p style="font-size:0.78rem;color:var(--text-muted);margin-top:3px">Real-time red-to-green phase transition &bull; Automated give-way corridor clearance</p>
      </div>
      <span class="btn-glass" style="font-size:0.75rem;border-color:var(--cyan);color:var(--cyan)">Cycle Mode: AI-Adaptive</span>
    </div>

    <div class="lanes-visual-grid">
      <!-- LANE 1 -->
      <div class="lane-box" id="lane-box-1">
        <div class="lane-header">
          <div style="font-size:1rem;font-weight:800;display:flex;align-items:center;gap:8px">
            <span>Lane 1 (Northbound)</span>
            <span id="lane-1-indicator" style="font-size:0.75rem;color:var(--text-dim)">&bull; Regular Flow</span>
          </div>
          <span id="lane-1-pill" class="state-pill red">🔴 RED</span>
        </div>

        <div class="signal-head-container">
          <div class="traffic-light-fixture">
            <div class="lens red lit" id="l1-red"></div>
            <div class="lens amber" id="l1-amber"></div>
            <div class="lens green" id="l1-green"></div>
          </div>
          <div class="signal-status-details">
            <div style="font-size:0.76rem;color:var(--text-muted);text-transform:uppercase;font-weight:700">Preemption State</div>
            <div id="l1-preemption-msg" style="font-size:0.9rem;font-weight:700;color:var(--text)">Signal running normal cycle</div>
            <div style="margin-top:8px">
              <span style="font-size:0.72rem;color:var(--text-muted)">Remaining Phase Window:</span>
              <span id="l1-timer" style="font-size:1.2rem;font-weight:800;font-family:'JetBrains Mono';color:var(--accent-bright);margin-left:6px">25s</span>
            </div>
            <div id="l1-action-note" style="font-size:0.75rem;color:var(--amber);margin-top:4px;display:none">
              ⚠️ Give way to incoming emergency vehicle!
            </div>
          </div>
        </div>
      </div>

      <!-- LANE 2 -->
      <div class="lane-box" id="lane-box-2">
        <div class="lane-header">
          <div style="font-size:1rem;font-weight:800;display:flex;align-items:center;gap:8px">
            <span>Lane 2 (Southbound)</span>
            <span id="lane-2-indicator" style="font-size:0.75rem;color:var(--text-dim)">&bull; Regular Flow</span>
          </div>
          <span id="lane-2-pill" class="state-pill green">🟢 GREEN</span>
        </div>

        <div class="signal-head-container">
          <div class="traffic-light-fixture">
            <div class="lens red" id="l2-red"></div>
            <div class="lens amber" id="l2-amber"></div>
            <div class="lens green lit" id="l2-green"></div>
          </div>
          <div class="signal-status-details">
            <div style="font-size:0.76rem;color:var(--text-muted);text-transform:uppercase;font-weight:700">Preemption State</div>
            <div id="l2-preemption-msg" style="font-size:0.9rem;font-weight:700;color:var(--text)">Signal running normal cycle</div>
            <div style="margin-top:8px">
              <span style="font-size:0.72rem;color:var(--text-muted)">Remaining Phase Window:</span>
              <span id="l2-timer" style="font-size:1.2rem;font-weight:800;font-family:'JetBrains Mono';color:var(--green);margin-left:6px">25s</span>
            </div>
            <div id="l2-action-note" style="font-size:0.75rem;color:var(--amber);margin-top:4px;display:none">
              ⚠️ Give way to incoming emergency vehicle!
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- EMERGENCY SIMULATION & DISPATCH CONSOLE -->
  <div class="card-3d">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px">
      <div>
        <h2 style="font-size:1.15rem;font-weight:800;display:flex;align-items:center;gap:8px">
          <span>⚡ Emergency Preemption Dispatcher</span>
          <span style="font-size:0.72rem;padding:2px 8px;border-radius:6px;background:rgba(239,68,68,0.2);color:#fca5a5;font-weight:700">Simulation &amp; Manual Override</span>
        </h2>
        <p style="font-size:0.78rem;color:var(--text-muted);margin-top:3px">
          Click below to dispatch an emergency vehicle &mdash; watch the red light instantly switch to <b>GREEN</b> to give way!
        </p>
      </div>
      <button class="btn-glass" onclick="resetCorridor()">⏹️ Reset All Overrides</button>
    </div>

    <!-- QUICK DISPATCH BUTTONS -->
    <div class="dispatch-grid">
      <button class="dispatch-btn amb" onclick="triggerPreemption('Ambulance', 1, 68)">
        <span style="font-size:1.8rem">🚑</span>
        <div style="text-align:left">
          <div style="font-weight:800">Dispatch Ambulance</div>
          <div style="font-size:0.72rem;color:#fca5a5">Lane 1 &bull; 68 km/h &bull; Red ➔ Green</div>
        </div>
      </button>

      <button class="dispatch-btn fire" onclick="triggerPreemption('Fire Engine', 2, 60)">
        <span style="font-size:1.8rem">🚒</span>
        <div style="text-align:left">
          <div style="font-weight:800">Dispatch Fire Engine</div>
          <div style="font-size:0.72rem;color:#fdba74">Lane 2 &bull; 60 km/h &bull; Red ➔ Green</div>
        </div>
      </button>

      <button class="dispatch-btn police" onclick="triggerPreemption('Police Car', 1, 75)">
        <span style="font-size:1.8rem">🚓</span>
        <div style="text-align:left">
          <div style="font-weight:800">Dispatch Police Car</div>
          <div style="font-size:0.72rem;color:#93c5fd">Lane 1 &bull; 75 km/h &bull; Red ➔ Green</div>
        </div>
      </button>

      <button class="dispatch-btn rescue" onclick="triggerPreemption('Rescue Truck', 2, 52)">
        <span style="font-size:1.8rem">🚜</span>
        <div style="text-align:left">
          <div style="font-weight:800">Dispatch Rescue Truck</div>
          <div style="font-size:0.72rem;color:#fde047">Lane 2 &bull; 52 km/h &bull; Red ➔ Green</div>
        </div>
      </button>
    </div>
  </div>

  <!-- EMERGENCY EVENT AUDIT LOG TABLE -->
  <div class="card-3d">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <div>
        <h2 style="font-size:1.15rem;font-weight:800">📋 Emergency Vehicle Transit &amp; Preemption History</h2>
        <p style="font-size:0.78rem;color:var(--text-muted);margin-top:3px">Certified log of all emergency vehicles that passed through the signal corridor</p>
      </div>
      <div style="display:flex;gap:8px">
        <button class="btn-glass" onclick="loadEmergencyData()">🔄 Refresh</button>
      </div>
    </div>

    <div style="overflow-x:auto">
      <table>
        <thead>
          <tr>
            <th>Event ID</th>
            <th>Timestamp</th>
            <th>Vehicle Classification</th>
            <th>Lane</th>
            <th>Approach Velocity</th>
            <th>Signal Transition</th>
            <th>Preemption Duration</th>
            <th>Corridor Status</th>
          </tr>
        </thead>
        <tbody id="emergency-table-body">
          <tr>
            <td colspan="8" style="text-align:center;color:var(--text-muted);padding:24px">
              Loading emergency logs...
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

</div>

<script>
let lastPreemptionActive = false;

function showToast(title, msg) {
  const container = document.getElementById('toast-container');
  const t = document.createElement('div');
  t.className = 'toast';
  t.innerHTML = `
    <span style="font-size:1.5rem">🚨</span>
    <div>
      <div style="font-weight:800;font-size:0.88rem;color:#fff">${title}</div>
      <div style="font-size:0.78rem;color:#fca5a5;margin-top:2px">${msg}</div>
    </div>
  `;
  container.appendChild(t);
  setTimeout(() => t.remove(), 4500);
}

async function triggerPreemption(vType, lane, speed) {
  try {
    const res = await fetch('/api/emergency/trigger', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ vehicle_type: vType, lane_id: lane, speed_kmh: speed, duration_seconds: 35 })
    });
    const d = await res.json();
    showToast(
      `${vType} Priority Triggered!`,
      `Signal in Lane ${lane} overridden: RED ➔ GREEN to give way immediately.`
    );
    loadEmergencyData();
  } catch (err) {
    console.error(err);
  }
}

async function resetCorridor() {
  try {
    await fetch('/api/emergency/clear', { method: 'POST' });
    showToast('Corridor Reset', 'Traffic signals resumed standard autonomous adaptive cycle.');
    loadEmergencyData();
  } catch (err) {
    console.error(err);
  }
}

async function loadEmergencyData() {
  try {
    const res = await fetch('/api/emergency/stats');
    if (!res.ok) return;
    const data = await res.json();

    // 1. Update KPI stats
    const stats = data.stats || {};
    document.getElementById('kpi-total').textContent = stats.total_transits || 0;
    document.getElementById('kpi-amb').textContent = stats.ambulance_count || 0;
    document.getElementById('kpi-fire').textContent = stats.fire_engine_count || 0;
    document.getElementById('kpi-police').textContent = stats.police_count || 0;
    document.getElementById('kpi-rescue').textContent = stats.rescue_count || 0;

    // 2. Preemption Banner & Status Pill
    const isPreempted = !!data.active_preemption;
    const activeLane = data.active_lane || 1;
    const activeVeh = data.active_vehicle_type || 'Emergency Vehicle';

    const pill = document.getElementById('preemption-pill');
    const banner = document.getElementById('active-banner');

    if (isPreempted) {
      pill.className = 'state-pill green';
      pill.innerHTML = `<span>🚨</span> PREEMPTION ACTIVE: LANE ${activeLane}`;
      
      banner.style.display = 'flex';
      const iconMap = {
        'Ambulance': '🚑',
        'Fire Engine': '🚒',
        'Fire Truck': '🚒',
        'Police Car': '🚓',
        'Rescue Truck': '🚜'
      };
      document.getElementById('banner-icon').textContent = iconMap[activeVeh] || '🚨';
      document.getElementById('banner-title').textContent = `${activeVeh.toUpperCase()} CORRIDOR ACTIVE`;
      document.getElementById('banner-desc').textContent = 
        `${activeVeh} approaching on Lane ${activeLane}. The signal was overridden: RED ➔ GREEN to give immediate way.`;

      if (!lastPreemptionActive) {
        showToast(`Corridor Cleared for ${activeVeh}!`, `Signal in Lane ${activeLane} is GREEN. Give way!`);
      }
    } else {
      pill.className = 'state-pill red';
      pill.innerHTML = `<span style="font-size:0.6rem">●</span> STANDBY / MONITORING`;
      banner.style.display = 'none';
    }
    lastPreemptionActive = isPreempted;

    // 3. Update Traffic Light Fixtures for Lane 1 & Lane 2
    const sig = data.signal_status || {};
    const laneStates = sig.lane_states || {};
    
    // Lane 1
    const l1 = laneStates[1] || { color: 'RED', remaining_s: 25 };
    const l1IsGreen = l1.color === 'GREEN';
    document.getElementById('l1-red').className = `lens red ${!l1IsGreen ? 'lit' : ''}`;
    document.getElementById('l1-green').className = `lens green ${l1IsGreen ? 'lit' : ''}`;
    document.getElementById('l1-pill').className = `state-pill ${l1IsGreen ? (isPreempted && activeLane === 1 ? 'preempted' : 'green') : 'red'}`;
    document.getElementById('l1-pill').textContent = l1IsGreen ? (isPreempted && activeLane === 1 ? '🟢 PREEMPTED GREEN' : '🟢 GREEN') : '🔴 RED LIGHT';
    document.getElementById('l1-timer').textContent = `${l1.remaining_s || 25}s`;
    document.getElementById('lane-box-1').className = `lane-box ${isPreempted && activeLane === 1 ? 'emergency-corridor-active' : ''}`;
    document.getElementById('l1-preemption-msg').textContent = (isPreempted && activeLane === 1) ? `🚨 ${activeVeh} Preemption Active (Give Way!)` : 'Regular Traffic Cycle';
    document.getElementById('l1-action-note').style.display = (isPreempted && activeLane === 1) ? 'block' : 'none';

    // Lane 2
    const l2 = laneStates[2] || { color: 'RED', remaining_s: 25 };
    const l2IsGreen = l2.color === 'GREEN';
    document.getElementById('l2-red').className = `lens red ${!l2IsGreen ? 'lit' : ''}`;
    document.getElementById('l2-green').className = `lens green ${l2IsGreen ? 'lit' : ''}`;
    document.getElementById('l2-pill').className = `state-pill ${l2IsGreen ? (isPreempted && activeLane === 2 ? 'preempted' : 'green') : 'red'}`;
    document.getElementById('l2-pill').textContent = l2IsGreen ? (isPreempted && activeLane === 2 ? '🟢 PREEMPTED GREEN' : '🟢 GREEN') : '🔴 RED LIGHT';
    document.getElementById('l2-timer').textContent = `${l2.remaining_s || 25}s`;
    document.getElementById('lane-box-2').className = `lane-box ${isPreempted && activeLane === 2 ? 'emergency-corridor-active' : ''}`;
    document.getElementById('l2-preemption-msg').textContent = (isPreempted && activeLane === 2) ? `🚨 ${activeVeh} Preemption Active (Give Way!)` : 'Regular Traffic Cycle';
    document.getElementById('l2-action-note').style.display = (isPreempted && activeLane === 2) ? 'block' : 'none';

    // 4. Update Emergency Logs Table
    const transits = data.recent_transits || [];
    const tbody = document.getElementById('emergency-table-body');
    if (transits.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;color:var(--text-muted);padding:24px">No emergency transits recorded yet. Click a dispatch button above to simulate!</td></tr>';
    } else {
      tbody.innerHTML = transits.map(t => {
        let badgeCls = 'badge-amb';
        let icon = '🚑';
        if (t.vehicle_type.includes('Fire')) { badgeCls = 'badge-fire'; icon = '🚒'; }
        else if (t.vehicle_type.includes('Police')) { badgeCls = 'badge-police'; icon = '🚓'; }
        else if (t.vehicle_type.includes('Rescue')) { badgeCls = 'badge-rescue'; icon = '🚜'; }

        return `
          <tr>
            <td style="color:var(--text-dim)">#${t.id}</td>
            <td>${t.timestamp.replace('T', ' ')}</td>
            <td><span class="badge-veh ${badgeCls}">${icon} ${t.vehicle_type}</span></td>
            <td><b>Lane ${t.lane_id}</b></td>
            <td><span style="color:#6ee7b7;font-weight:700">${t.speed_kmh.toFixed(1)} km/h</span></td>
            <td><span style="color:#f87171">🔴 ${t.prior_signal_state}</span> ➔ <span style="color:#34d399;font-weight:700">🟢 ${t.new_signal_state}</span></td>
            <td>${t.duration_seconds}s</td>
            <td><span style="color:#34d399;font-weight:700">✔ ${t.status}</span></td>
          </tr>
        `;
      }).join('');
    }

  } catch (err) {
    console.error('Error fetching emergency data:', err);
  }
}

// Initial load & continuous poll
loadEmergencyData();
setInterval(loadEmergencyData, 1000);
</script>

</body>
</html>
"""

