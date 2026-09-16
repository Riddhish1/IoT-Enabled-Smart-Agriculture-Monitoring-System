"""
============================================================
IoT Smart Agriculture Monitoring System
File   : sensor_simulator.py
Author : Anupam Santra
Purpose: Simulates 6 agricultural sensors across realistic
         scenarios, threshold logic, pump control,
         alert generation, and CSV data logging.
============================================================
"""

import random
import time
import csv
import os
from datetime import datetime

# ─── PATHS ────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR    = os.path.join(BASE_DIR, "data")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
CSV_FILE    = os.path.join(DATA_DIR, "sensor_log.csv")
ALERT_FILE  = os.path.join(OUTPUTS_DIR, "alert_log.txt")

os.makedirs(DATA_DIR,    exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# ─── THRESHOLDS ────────────────────────────────────────────────
THRESHOLDS = {
    "soil_moisture_dry":   30,    # % — below this: pump ON
    "soil_moisture_wet":   70,    # % — above this: pump OFF
    "temp_high":           35.0,  # °C — above this: alert
    "temp_low":             5.0,  # °C — below this: frost-risk alert
    "humidity_low":        30.0,  # % — below this: alert
    "water_level_low":     20,    # % — below this: alert + disable pump
    "light_low":           20,    # % — below this: low light alert
    "rain_active":         60,    # % — above this: skip irrigation
}

# ─── SIMULATION SCENARIOS ──────────────────────────────────────
# Each scenario represents a realistic farm condition.
# The simulator cycles through these automatically.
SCENARIOS = [
    {
        "name":         "Normal Day",
        "soil":         (45, 65),   "temp":    (24.0, 30.0),
        "humidity":     (50, 70),   "light":   (60, 90),
        "water_level":  (60, 90),   "rain":    (0, 10),
    },
    {
        "name":         "Dry Soil — Pump Needed",
        "soil":         (5, 25),    "temp":    (26.0, 32.0),
        "humidity":     (35, 55),   "light":   (55, 80),
        "water_level":  (50, 80),   "rain":    (0, 5),
    },
    {
        "name":         "High Temperature Alert",
        "soil":         (20, 40),   "temp":    (36.0, 42.0),
        "humidity":     (20, 35),   "light":   (80, 100),
        "water_level":  (40, 70),   "rain":    (0, 5),
    },
    {
        "name":         "Rainy Day — Pump Override",
        "soil":         (70, 95),   "temp":    (18.0, 24.0),
        "humidity":     (80, 98),   "light":   (10, 30),
        "water_level":  (80, 100),  "rain":    (65, 95),
    },
    {
        "name":         "Low Water Tank",
        "soil":         (10, 30),   "temp":    (25.0, 31.0),
        "humidity":     (40, 60),   "light":   (50, 75),
        "water_level":  (5, 18),   "rain":    (0, 5),
    },
    {
        "name":         "Night / Low Light",
        "soil":         (40, 60),   "temp":    (16.0, 22.0),
        "humidity":     (55, 75),   "light":   (0, 15),
        "water_level":  (50, 80),   "rain":    (0, 10),
    },
    {
        "name":         "Seedling Care",
        "soil":         (55, 70),    "temp":    (20.0, 26.0),
        "humidity":     (60, 80),    "light":   (45, 70),
        "water_level":  (70, 95),    "rain":    (0, 5),
    },
    {
        "name":         "Heatwave Drought",
        "soil":         (5, 20),     "temp":    (38.0, 45.0),
        "humidity":     (15, 28),    "light":   (85, 100),
        "water_level":  (35, 65),    "rain":    (0, 5),
    },
    {
        "name":         "Storm Incoming",
        "soil":         (25, 45),    "temp":    (22.0, 29.0),
        "humidity":     (70, 90),    "light":   (15, 40),
        "water_level":  (45, 75),    "rain":    (55, 75),
    },
    {
        "name":         "Frost Risk",
        "soil":         (45, 65),    "temp":    (0.0, 4.5),
        "humidity":     (55, 75),    "light":   (20, 50),
        "water_level":  (60, 90),    "rain":    (0, 10),
    },
    {
        "name":         "Irrigation Recovery",
        "soil":         (30, 45),    "temp":    (24.0, 32.0),
        "humidity":     (35, 55),    "light":   (55, 85),
        "water_level":  (25, 45),    "rain":    (0, 8),
    },
]

# ─── CSV HEADER ───────────────────────────────────────────────
CSV_COLUMNS = [
    "timestamp", "reading_no", "scenario",
    "soil_moisture_%", "temperature_C", "humidity_%",
    "light_intensity_%", "water_level_%", "rain_level_%",
    "pump_status", "alerts"
]

# ─── ALERT ENGINE ─────────────────────────────────────────────
def check_alerts(soil, temp, humidity, light, water, rain):
    """
    Evaluate sensor values against thresholds.
    Returns list of active alert strings.
    """
    alerts = []
    if temp     > THRESHOLDS["temp_high"]:      alerts.append("HIGH_TEMPERATURE")
    if temp     < THRESHOLDS["temp_low"]:       alerts.append("FROST_RISK")
    if humidity < THRESHOLDS["humidity_low"]:   alerts.append("LOW_HUMIDITY")
    if water    < THRESHOLDS["water_level_low"]:alerts.append("LOW_WATER_TANK")
    if light    < THRESHOLDS["light_low"]:      alerts.append("LOW_LIGHT")
    if soil     < THRESHOLDS["soil_moisture_dry"]:alerts.append("DRY_SOIL")
    return alerts

# ─── PUMP DECISION LOGIC ──────────────────────────────────────
def decide_pump(soil, water, rain):
    """
    Decides whether the water pump should be ON or OFF.
    Rules:
      - If raining → OFF (rain override)
      - If water tank critically low → OFF (protect pump)
      - If soil dry + water available → ON
      - If soil sufficiently wet → OFF
    Returns: (bool pump_on, str reason)
    """
    if rain > THRESHOLDS["rain_active"]:
        return False, "Rain detected — irrigation skipped"
    if water < THRESHOLDS["water_level_low"]:
        return False, "Water tank critically low — pump disabled"
    if soil < THRESHOLDS["soil_moisture_dry"]:
        return True,  "Soil is DRY — pump activated"
    if soil >= THRESHOLDS["soil_moisture_wet"]:
        return False, "Soil sufficiently moist — pump idle"
    return False, "Soil moisture in acceptable range"

# ─── TERMINAL ALERT PRINTER ───────────────────────────────────
ALERT_COLORS = {
    "HIGH_TEMPERATURE": "\033[91m",   # Red
    "LOW_HUMIDITY":     "\033[93m",   # Yellow
    "LOW_WATER_TANK":   "\033[94m",   # Blue
    "LOW_LIGHT":        "\033[95m",   # Magenta
    "DRY_SOIL":         "\033[33m",   # Orange
}
RESET = "\033[0m"
GREEN = "\033[92m"
CYAN  = "\033[96m"
BOLD  = "\033[1m"

def print_reading(reading_no, scenario, soil, temp, humid,
                  light, water, rain, pump_on, pump_reason, alerts):
    print(f"\n{BOLD}{CYAN}{'='*52}{RESET}")
    print(f"{BOLD}  Reading #{reading_no:04d}  |  Scenario: {scenario}{RESET}")
    print(f"{CYAN}{'='*52}{RESET}")
    print(f"  🌱 Soil Moisture   : {soil:5.1f} %")
    print(f"  🌡️  Temperature     : {temp:5.1f} °C")
    print(f"  💧 Humidity        : {humid:5.1f} %")
    print(f"  ☀️  Light Intensity : {light:5.1f} %")
    print(f"  🪣 Water Level     : {water:5.1f} %")
    print(f"  🌧️  Rain Level      : {rain:5.1f} %")
    print(f"  {'-'*48}")

    pump_icon = "🟢 ON  [ACTIVE]" if pump_on else "⚫ OFF [IDLE]"
    pump_color = GREEN if pump_on else "\033[90m"
    print(f"  💦 Pump Status     : {pump_color}{pump_icon}{RESET}")
    print(f"     Reason          : {pump_reason}")

    if alerts:
        print(f"  {'-'*48}")
        for alert in alerts:
            color = ALERT_COLORS.get(alert, "")
            print(f"  {color}⚠️  ALERT: {alert}{RESET}")
    else:
        print(f"  {GREEN}✅ All sensors normal — no alerts{RESET}")

def log_alert(reading_no, scenario, alerts, pump_on, pump_reason):
    """Append alert entry to alert_log.txt"""
    if not alerts and not pump_on:
        return
    with open(ALERT_FILE, "a", encoding="utf-8") as f:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"\n[{ts}] Reading #{reading_no:04d} | Scenario: {scenario}\n")
        for alert in alerts:
            f.write(f"  ALERT : {alert}\n")
        if pump_on:
            f.write(f"  PUMP  : ON — {pump_reason}\n")
        f.write(f"  {'─'*40}\n")

# ─── CSV LOGGER ───────────────────────────────────────────────
def init_csv():
    """Create CSV with header if it doesn't exist."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()

def log_csv(reading_no, scenario, soil, temp, humid,
            light, water, rain, pump_on, alerts):
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writerow({
            "timestamp":         datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "reading_no":        reading_no,
            "scenario":          scenario,
            "soil_moisture_%":   round(soil, 1),
            "temperature_C":     round(temp, 1),
            "humidity_%":        round(humid, 1),
            "light_intensity_%": round(light, 1),
            "water_level_%":     round(water, 1),
            "rain_level_%":      round(rain, 1),
            "pump_status":       "ON" if pump_on else "OFF",
            "alerts":            "|".join(alerts) if alerts else "None",
        })

# ─── SIMULATE ONE READING ─────────────────────────────────────
def generate_reading(scenario_data):
    """Generate sensor values and decisions from a scenario range."""
    def rval(lo, hi):
        return round(random.uniform(lo, hi), 1)

    soil  = rval(*scenario_data["soil"])
    temp  = rval(*scenario_data["temp"])
    humid = rval(*scenario_data["humidity"])
    light = rval(*scenario_data["light"])
    water = rval(*scenario_data["water_level"])
    rain  = rval(*scenario_data["rain"])

    alerts               = check_alerts(soil, temp, humid, light, water, rain)
    pump_on, pump_reason = decide_pump(soil, water, rain)

    return {
        "soil": soil,
        "temp": temp,
        "humidity": humid,
        "light": light,
        "water": water,
        "rain": rain,
        "pump_on": pump_on,
        "pump_reason": pump_reason,
        "alerts": alerts,
    }

def simulate_reading(reading_no, scenario_data):
    """Generate, display, and persist one sensor reading."""
    reading = generate_reading(scenario_data)
    soil = reading["soil"]
    temp = reading["temp"]
    humid = reading["humidity"]
    light = reading["light"]
    water = reading["water"]
    rain = reading["rain"]
    pump_on = reading["pump_on"]
    pump_reason = reading["pump_reason"]
    alerts = reading["alerts"]

    print_reading(
        reading_no, scenario_data["name"],
        soil, temp, humid, light, water, rain,
        pump_on, pump_reason, alerts
    )
    log_csv(reading_no, scenario_data["name"],
            soil, temp, humid, light, water, rain, pump_on, alerts)
    log_alert(reading_no, scenario_data["name"], alerts, pump_on, pump_reason)

    return {
        "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "reading_no":  reading_no,
        "scenario":    scenario_data["name"],
        "soil":        soil,
        "temp":        temp,
        "humidity":    humid,
        "light":       light,
        "water":       water,
        "rain":        rain,
        "pump_on":     pump_on,
        "pump_reason": pump_reason,
        "alerts":      alerts,
    }

# ─── MAIN SIMULATION LOOP ─────────────────────────────────────
def run_simulation(interval_seconds=3, total_readings=None):
    """
    Run the simulation loop.
    Args:
        interval_seconds: pause between readings (default 3s)
        total_readings  : None = infinite loop, int = stop after N readings
    Returns:
        Generator that yields each reading dict (used by dashboard)
    """
    init_csv()

    # Write alert log header
    with open(ALERT_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"Session Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*50}\n")

    print(f"\n{BOLD}{'='*52}")
    print("   IoT Smart Agriculture Monitoring System")
    print("   Author: Anupam Santra")
    print(f"{'='*52}{RESET}")
    print(f"  Logging to  : {CSV_FILE}")
    print(f"  Alerts log  : {ALERT_FILE}")
    print(f"  Interval    : {interval_seconds}s per reading")
    print(f"  Press Ctrl+C to stop\n")

    reading_no     = 1
    scenario_index = 0

    try:
        while True:
            if total_readings and reading_no > total_readings:
                break

            # Cycle through scenarios every 8 readings
            if reading_no % 8 == 1:
                scenario_index = (scenario_index + 1) % len(SCENARIOS)

            scenario = SCENARIOS[scenario_index]
            data     = simulate_reading(reading_no, scenario)
            yield data

            reading_no += 1
            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        print(f"\n{GREEN}Simulation stopped by user.{RESET}")
        print(f"Data saved to: {CSV_FILE}")
        print(f"Alerts saved to: {ALERT_FILE}")

# ─── ENTRY POINT (standalone run) ─────────────────────────────
if __name__ == "__main__":
    for _ in run_simulation(interval_seconds=2):
        pass  # printing happens inside simulate_reading
