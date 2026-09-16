"""
============================================================
IoT Smart Agriculture Monitoring System
File   : app.py  (Plotly Dash Real-Time Dashboard)
Author : Anupam Santra
Purpose: Live browser dashboard that shows all 6 sensor
         values, pump status, alert banners, and historical
         trend charts. Auto-refreshes every 2 seconds.

HOW TO RUN:
  cd dashboard
  python app.py
  Open: http://localhost:8050
============================================================
"""

import sys
import os
import csv
import threading
import time
from datetime import datetime
from collections import deque

# Add parent to path so we can import sensor_simulator
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─── IMPORT SIMULATOR LOGIC ──────────────────────────────────
from python_simulation.sensor_simulator import (
    SCENARIOS, THRESHOLDS,
)
from communication.mqtt_subscriber import snapshot, start_subscriber

# ─── SHARED STATE (thread-safe deque for history) ─────────────
MAX_HISTORY = 50

history = {
    "timestamps":  deque(maxlen=MAX_HISTORY),
    "soil":        deque(maxlen=MAX_HISTORY),
    "temp":        deque(maxlen=MAX_HISTORY),
    "humidity":    deque(maxlen=MAX_HISTORY),
    "light":       deque(maxlen=MAX_HISTORY),
    "water":       deque(maxlen=MAX_HISTORY),
    "rain":        deque(maxlen=MAX_HISTORY),
    "pump":        deque(maxlen=MAX_HISTORY),
}

current_reading = {
    "reading_no":  0,
    "scenario":    "Initializing...",
    "soil":        50.0,
    "temp":        25.0,
    "humidity":    60.0,
    "light":       70.0,
    "water":       75.0,
    "rain":        5.0,
    "pump_on":     False,
    "pump_reason": "Starting...",
    "alerts":      [],
}

reading_lock   = threading.Lock()
reading_no_ctr = [0]
scenario_idx   = [0]

# ─── BACKGROUND SENSOR THREAD ────────────────────────────────
def sensor_thread():
    """Start the MQTT receiver used by the dashboard."""
    start_subscriber()

# ─── DASH APP ─────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    title="🌾 Smart Agriculture IoT Dashboard",
    update_title=None,
)

# ─── COLOUR PALETTE ───────────────────────────────────────────
COLORS = {
    "bg":          "#ffffff",
    "card":        "#ffffff",
    "border":      "#000000",
    "green":       "#1b5e20",
    "yellow":      "#8a6500",
    "red":         "#c62828",
    "blue":        "#000000",
    "purple":      "#555555",
    "orange":      "#333333",
    "teal":        "#1b5e20",
    "text":        "#000000",
    "subtext":     "#555555",
    "pump_on":     "#1b5e20",
    "pump_off":    "#555555",
}

SENSOR_COLORS = {
    "soil":     COLORS["orange"],
    "temp":     COLORS["red"],
    "humidity": COLORS["blue"],
    "light":    COLORS["yellow"],
    "water":    COLORS["teal"],
    "rain":     COLORS["purple"],
}

# ─── GAUGE FACTORY ────────────────────────────────────────────
def make_gauge(value, title, color, max_val=100, suffix="%",
               low_thresh=None, high_thresh=None):
    steps = [
        {"range": [0, max_val * 0.3],  "color": "#f1f1f1"},
        {"range": [max_val * 0.3, max_val * 0.7], "color": "#e3e3e3"},
        {"range": [max_val * 0.7, max_val],        "color": "#ffffff"},
    ]
    threshold_dict = None
    if high_thresh:
        threshold_dict = {"line": {"color": COLORS["red"], "width": 3},
                          "thickness": 0.8, "value": high_thresh}
    elif low_thresh:
        threshold_dict = {"line": {"color": COLORS["yellow"], "width": 3},
                          "thickness": 0.8, "value": low_thresh}

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"color": COLORS["text"], "size": 13}},
        number={"suffix": suffix, "font": {"color": color, "size": 22}},
        gauge={
            "axis": {
                "range": [0, max_val],
                "tickcolor": COLORS["subtext"],
                "tickfont":  {"color": COLORS["subtext"], "size": 10},
            },
            "bar":             {"color": color, "thickness": 0.25},
            "bgcolor":         COLORS["card"],
            "borderwidth":     1,
            "bordercolor":     COLORS["border"],
            "steps":           steps,
            "threshold":       threshold_dict,
        },
    ))
    fig.update_layout(
        paper_bgcolor=COLORS["card"],
        plot_bgcolor= COLORS["card"],
        margin=dict(l=20, r=20, t=50, b=20),
        height=200,
        font={"color": COLORS["text"]},
    )
    return fig

# ─── CARD STYLE ───────────────────────────────────────────────
def card_style(extra=None):
    base = {
        "backgroundColor": COLORS["card"],
        "border":          f"1px solid {COLORS['border']}",
        "borderRadius":    "0",
        "padding":         "20px",
        "marginBottom":    "20px",
    }
    if extra:
        base.update(extra)
    return base

# ─── LAYOUT ──────────────────────────────────────────────────
app.layout = html.Div(
        style={"backgroundColor": COLORS["bg"], "minHeight": "100vh",
            "fontFamily": "'JetBrains Mono', 'Courier New', monospace",
            "color": COLORS["text"], "padding": "0 24px 24px"},
    children=[

        # ── Header ──────────────────────────────────────────
        html.Div(style={"borderBottom": "2px solid #000", "padding": "18px 0",
                "display": "flex", "justifyContent": "space-between",
                "alignItems": "center", "gap": "20px"}, children=[
            html.Div([
            html.H1("AGRISENSE / FIELD MONITOR",
                style={"margin": "0", "fontSize": "20px", "letterSpacing": "1px"}),
            html.P("MQTT-ENABLED SMART AGRICULTURE CONTROL NODE",
                   style={"margin": "5px 0 0", "color": COLORS["subtext"],
                      "fontSize": "10px", "fontWeight": "bold"}),
            ]),
            html.Div("STATUS: LIVE TELEMETRY", style={
            "border": "1px solid #000", "padding": "8px 12px",
            "fontSize": "11px", "fontWeight": "bold", "whiteSpace": "nowrap"}),
        ]),

        # ── Interval + Alert Banner ──────────────────────────
        dcc.Interval(id="interval", interval=2000, n_intervals=0),
        html.Div(id="alert-banner"),

        # ── Status Row ──────────────────────────────────────
        html.Div(id="status-row",
                 style={"display": "grid",
                        "gridTemplateColumns": "repeat(4, 1fr)",
                        "gap": "20px", "margin": "20px auto 0",
                        "maxWidth": "1600px"}),

        # ── Gauge Row ───────────────────────────────────────
        html.Div(
            style={"display": "grid",
                   "gridTemplateColumns": "repeat(3, 1fr)",
                   "gap": "20px", "margin": "20px auto",
                   "maxWidth": "1600px"},
            children=[
                html.Div(dcc.Graph(id="gauge-soil",     config={"displayModeBar": False}),
                         style=card_style()),
                html.Div(dcc.Graph(id="gauge-temp",     config={"displayModeBar": False}),
                         style=card_style()),
                html.Div(dcc.Graph(id="gauge-humidity", config={"displayModeBar": False}),
                         style=card_style()),
                html.Div(dcc.Graph(id="gauge-light",    config={"displayModeBar": False}),
                         style=card_style()),
                html.Div(dcc.Graph(id="gauge-water",    config={"displayModeBar": False}),
                         style=card_style()),
                html.Div(dcc.Graph(id="gauge-rain",     config={"displayModeBar": False}),
                         style=card_style()),
            ]
        ),

        # ── History Chart ───────────────────────────────────
        html.Div(style=card_style(), children=[
            html.H3("📈 Live Sensor History",
                    style={"margin": "0 0 12px", "color": COLORS["text"],
                           "fontSize": "16px"}),
            dcc.Graph(id="history-chart", config={"displayModeBar": False},
                      style={"height": "320px"}),
        ]),

        # ── Pump + Scenario Row ──────────────────────────────
        html.Div(
            style={"display": "grid",
                   "gridTemplateColumns": "1fr 2fr",
                   "gap": "20px", "margin": "20px auto",
                   "maxWidth": "1600px"},
            children=[
                html.Div(style=card_style(), children=[
                    html.H3("💦 Pump Status", style={"margin": "0 0 10px",
                                                      "fontSize": "15px"}),
                    html.Div(id="pump-display"),
                ]),
                html.Div(style=card_style(), children=[
                    html.H3("🔄 Current Scenario", style={"margin": "0 0 10px",
                                                           "fontSize": "15px"}),
                    html.Div(id="scenario-display"),
                ]),
            ]
        ),

        # ── Footer ──────────────────────────────────────────
         html.Div(style={"borderTop": "1px solid #000", "color": COLORS["subtext"],
                   "fontSize": "10px", "padding": "14px 0", "maxWidth": "1600px",
                   "margin": "0 auto"},
               children=[
                html.P("AGRISENSE / MQTT TELEMETRY / EDGE IRRIGATION CONTROL"),
                 ]),
    ]
)

# ─── CALLBACKS ───────────────────────────────────────────────
@app.callback(
    [Output("alert-banner",   "children"),
     Output("status-row",     "children"),
     Output("gauge-soil",     "figure"),
     Output("gauge-temp",     "figure"),
     Output("gauge-humidity", "figure"),
     Output("gauge-light",    "figure"),
     Output("gauge-water",    "figure"),
     Output("gauge-rain",     "figure"),
     Output("history-chart",  "figure"),
     Output("pump-display",   "children"),
     Output("scenario-display", "children")],
    Input("interval", "n_intervals"),
)
def update_dashboard(n):
    r, received_history = snapshot()
    ts = received_history["timestamps"]
    hs = received_history["soil"]
    ht = received_history["temp"]
    hh = received_history["humidity"]
    hl = received_history["light"]
    hw = received_history["water"]
    hr = received_history["rain"]
    hp = received_history["pump"]

    # ── Alert Banner ────────────────────────────────────────
    alert_children = []
    if r["alerts"]:
        alert_map = {
            "HIGH_TEMPERATURE": ("🌡️ HIGH TEMPERATURE ALERT",   COLORS["red"]),
            "FROST_RISK":       ("❄️ FROST RISK ALERT",          COLORS["blue"]),
            "LOW_HUMIDITY":     ("💧 LOW HUMIDITY ALERT",        COLORS["yellow"]),
            "LOW_WATER_TANK":   ("🪣 WATER TANK CRITICAL",       COLORS["blue"]),
            "LOW_LIGHT":        ("🌑 LOW LIGHT ALERT",           COLORS["purple"]),
            "DRY_SOIL":         ("🌱 DRY SOIL — PUMP ACTIVATED", COLORS["orange"]),
        }
        for alert in r["alerts"]:
            label, color = alert_map.get(alert, (alert, COLORS["red"]))
            alert_children.append(
                html.Div(label, style={
                    "backgroundColor": color + "22",
                    "border":          f"1px solid {color}",
                    "borderRadius":    "8px",
                    "padding":         "10px 16px",
                    "marginBottom":    "8px",
                    "fontWeight":      "bold",
                    "color":           color,
                    "fontSize":        "14px",
                })
            )
    else:
        alert_children = [
            html.Div("✅ All sensors normal — no active alerts",
                     style={
                         "backgroundColor": COLORS["green"] + "22",
                         "border":          f"1px solid {COLORS['green']}",
                         "borderRadius":    "8px",
                         "padding":         "10px 16px",
                         "marginBottom":    "8px",
                         "color":           COLORS["green"],
                         "fontSize":        "14px",
                     })
        ]

    # ── Status Cards ────────────────────────────────────────
    def stat_card(icon, label, value, color):
        return html.Div(style=card_style({"borderColor": color, "textAlign": "center"}),
                        children=[
                            html.Div(icon, style={"fontSize": "24px"}),
                            html.Div(label, style={"fontSize": "11px",
                                                    "color": COLORS["subtext"],
                                                    "marginTop": "4px"}),
                            html.Div(value, style={"fontSize": "20px",
                                                    "fontWeight": "bold",
                                                    "color": color,
                                                    "marginTop": "4px"}),
                        ])

    status_row = [
        stat_card("📍", "Reading #",    f"#{r['reading_no']:04d}",         COLORS["blue"]),
        stat_card("🕐", "Last received", r["timestamp"], COLORS["subtext"]),
        stat_card("💦", "Pump",         "ON" if r["pump_on"] else "OFF",
                  COLORS["pump_on"] if r["pump_on"] else COLORS["pump_off"]),
        stat_card("⚠️", "Active Alerts", str(len(r["alerts"])),
                  COLORS["red"] if r["alerts"] else COLORS["green"]),
    ]

    # ── Gauges ──────────────────────────────────────────────
    g_soil  = make_gauge(r["soil"],     "🌱 Soil Moisture",   SENSOR_COLORS["soil"],
                         low_thresh=THRESHOLDS["soil_moisture_dry"])
    g_temp  = make_gauge(r["temp"],     "🌡️ Temperature",      SENSOR_COLORS["temp"],
                         max_val=50, suffix="°C",
                         high_thresh=THRESHOLDS["temp_high"])
    g_humid = make_gauge(r["humidity"], "💧 Humidity",         SENSOR_COLORS["humidity"],
                         low_thresh=THRESHOLDS["humidity_low"])
    g_light = make_gauge(r["light"],    "☀️ Light Intensity",  SENSOR_COLORS["light"],
                         low_thresh=THRESHOLDS["light_low"])
    g_water = make_gauge(r["water"],    "🪣 Water Level",      SENSOR_COLORS["water"],
                         low_thresh=THRESHOLDS["water_level_low"])
    g_rain  = make_gauge(r["rain"],     "🌧️ Rain Level",       SENSOR_COLORS["rain"],
                         high_thresh=THRESHOLDS["rain_active"])

    # ── History Chart ───────────────────────────────────────
    layout_history = go.Layout(
        paper_bgcolor=COLORS["card"],
        plot_bgcolor= COLORS["card"],
        margin=dict(l=40, r=20, t=20, b=40),
        legend=dict(orientation="h", y=1.1,
                    font={"color": COLORS["text"], "size": 11}),
        xaxis=dict(tickfont={"color": COLORS["subtext"], "size": 10},
                   gridcolor=COLORS["border"]),
        yaxis=dict(tickfont={"color": COLORS["subtext"], "size": 10},
                   gridcolor=COLORS["border"], range=[0, 105]),
        hovermode="x unified",
    )

    traces = [
        go.Scatter(x=ts, y=hs, name="Soil %",    line=dict(color=SENSOR_COLORS["soil"],     width=2)),
        go.Scatter(x=ts, y=ht, name="Temp °C",   line=dict(color=SENSOR_COLORS["temp"],     width=2)),
        go.Scatter(x=ts, y=hh, name="Humidity%", line=dict(color=SENSOR_COLORS["humidity"], width=2)),
        go.Scatter(x=ts, y=hl, name="Light %",   line=dict(color=SENSOR_COLORS["light"],    width=2)),
        go.Scatter(x=ts, y=hw, name="Water %",   line=dict(color=SENSOR_COLORS["water"],    width=2)),
        go.Scatter(x=ts, y=hr, name="Rain %",    line=dict(color=SENSOR_COLORS["rain"],     width=2)),
    ]
    history_fig = go.Figure(data=traces, layout=layout_history)

    # ── Pump Display ─────────────────────────────────────────
    pump_color = COLORS["pump_on"] if r["pump_on"] else COLORS["pump_off"]
    pump_icon  = "🟢" if r["pump_on"] else "⚫"
    pump_label = "ACTIVE — Irrigating" if r["pump_on"] else "IDLE"
    pump_display = html.Div([
        html.Div(f"{pump_icon} {pump_label}",
                 style={"fontSize": "20px", "fontWeight": "bold",
                        "color": pump_color}),
        html.Div(r["pump_reason"],
                 style={"fontSize": "12px", "color": COLORS["subtext"],
                        "marginTop": "6px"}),
        html.Div(
            style={"marginTop": "12px", "display": "flex", "gap": "8px"},
            children=[
                html.Div(f"Pump ON: {hp.count(1)}", style={
                    "backgroundColor": COLORS["pump_on"] + "22",
                    "border": f"1px solid {COLORS['pump_on']}",
                    "borderRadius": "6px", "padding": "4px 10px",
                    "fontSize": "12px", "color": COLORS["pump_on"],
                }),
                html.Div(f"Pump OFF: {hp.count(0)}", style={
                    "backgroundColor": COLORS["border"],
                    "borderRadius": "6px", "padding": "4px 10px",
                    "fontSize": "12px", "color": COLORS["subtext"],
                }),
            ]
        ),
    ])

    # ── Scenario Display ─────────────────────────────────────
    scenario_display = html.Div([
        html.Div(f"📍 {r['scenario']}",
                 style={"fontSize": "18px", "fontWeight": "bold",
                        "color": COLORS["blue"]}),
         html.Div(
               f"MQTT: {'CONNECTED' if r['mqtt_connected'] else 'WAITING FOR ESP32 DATA'}",
               style={"fontSize": "12px",
                   "color": (COLORS["green"] if r["mqtt_connected"]
                          else COLORS["yellow"]),
                   "margin": "8px 0 6px"}),
         html.Div("Scenario and sensor values are received from the ESP32:",
                 style={"fontSize": "12px", "color": COLORS["subtext"],
                        "margin": "8px 0 6px"}),
        html.Div(
            style={"display": "flex", "flexWrap": "wrap", "gap": "6px"},
            children=[
                html.Span(sc["name"], style={
                    "backgroundColor": (COLORS["green"] + "33"
                                        if sc["name"] == r["scenario"]
                                        else COLORS["border"]),
                    "border":          (f"1px solid {COLORS['green']}"
                                        if sc["name"] == r["scenario"]
                                        else f"1px solid {COLORS['border']}"),
                    "borderRadius":    "20px",
                    "padding":         "3px 10px",
                    "fontSize":        "11px",
                    "color":           (COLORS["green"]
                                        if sc["name"] == r["scenario"]
                                        else COLORS["subtext"]),
                })
                for sc in SCENARIOS
            ]
        ),
    ])

    return (
        alert_children, status_row,
        g_soil, g_temp, g_humid, g_light, g_water, g_rain,
        history_fig, pump_display, scenario_display
    )

# ─── ENTRY POINT ─────────────────────────────────────────────
if __name__ == "__main__":
    # Start background sensor thread
    t = threading.Thread(target=sensor_thread, daemon=True)
    t.start()

    print("\n" + "="*52)
    print("  IoT Smart Agriculture Dashboard Starting...")
    print("  Open your browser: http://localhost:8050")
    print("="*52 + "\n")

    app.run(debug=False, host="0.0.0.0", port=8050)
