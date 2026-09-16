"""
============================================================
IoT Smart Agriculture Monitoring System
File   : main.py  (Single Entry Point)
Author : Anupam Santra

USAGE:
  python main.py            → Launches live dashboard + simulation
  python main.py --sim-only → Terminal-only simulation, no browser
  python main.py --help     → Show help
============================================================
"""

import sys
import os
import subprocess
import threading
import time
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

BANNER = """
╔══════════════════════════════════════════════════════╗
║   IoT-Enabled Smart Agriculture Monitoring System   ║
║   Author : Anupam Santra                            ║
║   GitHub : IoT-Enabled-Smart-Agriculture-Monitoring ║
╚══════════════════════════════════════════════════════╝
"""

def run_sim_only():
    """Run terminal simulation only (no dashboard)."""
    print(BANNER)
    print("Running terminal simulation only...\n")
    from python_simulation.sensor_simulator import run_simulation
    for _ in run_simulation(interval_seconds=2):
        pass

def run_dashboard():
    """Run full dashboard mode (simulation runs inside dashboard thread)."""
    print(BANNER)
    print("Starting IoT Smart Agriculture Dashboard...")
    print("📊 Opening: http://localhost:8050")
    print("🛑 Press Ctrl+C to stop\n")

    # Import here so path is set
    from dashboard.app import app, sensor_thread
    from python_simulation.sensor_simulator import init_csv, ALERT_FILE
    from datetime import datetime

    # Start sensor background thread
    t = threading.Thread(target=sensor_thread, daemon=True)
    t.start()

    # Give sensor thread 1 second to produce first reading
    time.sleep(1)

    # Start Dash server
    try:
        app.run(debug=False, host="0.0.0.0", port=8050, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\nDashboard stopped.")
        print(f"✅ Data saved to: {os.path.join(BASE_DIR, 'data', 'sensor_log.csv')}")
        print(f"✅ Alerts saved to: {os.path.join(BASE_DIR, 'outputs', 'alert_log.txt')}")

def main():
    parser = argparse.ArgumentParser(
        description="IoT Smart Agriculture Monitoring System by Anupam Santra"
    )
    parser.add_argument(
        "--sim-only",
        action="store_true",
        help="Run terminal simulation only (no browser dashboard)"
    )
    args = parser.parse_args()

    if args.sim_only:
        run_sim_only()
    else:
        run_dashboard()

if __name__ == "__main__":
    main()
