# 🌾 IoT-Enabled Smart Agriculture Monitoring System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![ESP32](https://img.shields.io/badge/ESP32-Wokwi_Simulation-green?style=for-the-badge&logo=espressif)
![Plotly Dash](https://img.shields.io/badge/Dashboard-Plotly_Dash-orange?style=for-the-badge&logo=plotly)
![IoT](https://img.shields.io/badge/Domain-IoT_Agriculture-brightgreen?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**A real-time IoT simulation system that monitors agricultural field conditions using 6 virtual sensors, intelligent pump automation, and a live Plotly Dash browser dashboard.**

</div>

---

## 📌 Project Overview

This project simulates a complete **IoT-based smart agriculture monitoring system** built for farmers, greenhouse operators, and precision agriculture researchers. It demonstrates end-to-end IoT engineering: sensor data collection → threshold-based decision logic → actuator control → real-time dashboard → data logging.

The project runs in **two parallel modes**:
1. **Hardware Simulation**: ESP32 on [Wokwi](https://wokwi.com) with DHT22, potentiometers (soil/water/rain), and LDR
2. **Software Simulation**: Python simulation engine + live Plotly Dash dashboard at `localhost:8050`

---

## 🚨 Problem Statement

Traditional farming relies on manual inspection for irrigation decisions, leading to:
- 💧 **Over-irrigation** — water waste and root damage
- 🌵 **Under-irrigation** — crop failure and yield loss
- ⏱️ **Delayed response** — farmer absent when conditions change
- 📊 **No historical data** — unable to analyze patterns over time

This system solves all of the above through real-time automated monitoring.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🌱 **6 Sensor Simulation** | Soil Moisture, Temperature, Humidity, Light Intensity, Water Level, Rain |
| 💦 **Auto Pump Control** | Pump turns ON/OFF based on soil moisture + rain + water tank logic |
| ⚠️ **Dual Alert System** | On-dashboard banners + terminal output + alert log file |
| 📈 **Live Dashboard** | Real-time Plotly Dash at `localhost:8050`, refreshes every 2 seconds |
| 🔄 **11 Scenarios** | Covers normal growth, drought, storms, frost, heatwave, tank protection, and recovery |
| 📁 **CSV Logging** | All readings auto-saved to `data/sensor_log.csv` |
| 🔌 **Wokwi Circuit** | Full ESP32 circuit with `diagram.json` — paste and run instantly |
| 🧩 **Modular Code** | Separate modules for simulation, dashboard, and Arduino |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Microcontroller | ESP32 DevKit V1 (via Wokwi simulation) |
| Hardware Simulation | [Wokwi.com](https://wokwi.com/esp32) |
| Firmware Language | Arduino C++ (`.ino`) |
| Software Language | Python 3.8+ |
| Dashboard | Plotly Dash 2.17 |
| Charts | Plotly 5.22 |
| Data Storage | CSV (pandas) |
| Sensors (Wokwi) | DHT22, Potentiometer x3, LDR/Photoresistor |
| Actuators (Wokwi) | Blue LED (Pump), Red LED (Alert) |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────┐
│                   WOKWI SIMULATION                   │
│  DHT22 ──┐                                           │
│  Soil  ──┤                                           │
│  LDR   ──┼──→ ESP32 ──→ Pump LED (GPIO 26)           │
│  Water ──┤        └───→ Alert LED (GPIO 27)          │
│  Rain  ──┘                                           │
└──────────────────────────────────────────────────────┘
                      ↕ (mirrors logic)
┌──────────────────────────────────────────────────────┐
│                PYTHON SIMULATION                     │
│  sensor_simulator.py                                 │
│  → 6 sensor values → threshold check                 │
│  → pump decision → alerts → CSV log                  │
└──────────────────────────────────────────────────────┘
                      ↕
┌──────────────────────────────────────────────────────┐
│            PLOTLY DASH DASHBOARD                     │
│               localhost:8050                         │
│  [Alert Banners] [Status Cards]                      │
│  [6 Gauge Charts] [Live History Chart]               │
│  [Pump Status]  [Scenario Selector]                  │
└──────────────────────────────────────────────────────┘
```

---

## 📂 Folder Structure

```
IoT-Enabled-Smart-Agriculture-Monitoring-System/
│
├── arduino_code/
│   ├── smart_agriculture.ino     ← ESP32 firmware (paste into Wokwi)
│   └── diagram.json              ← Wokwi circuit (paste into Wokwi diagram tab)
│
├── python_simulation/
│   └── sensor_simulator.py       ← Scenario engine + CSV logger
│
├── dashboard/
│   └── app.py                    ← Real-time Plotly Dash dashboard
│
├── data/
│   └── sensor_log.csv            ← Auto-generated sensor readings
│
├── outputs/
│   └── alert_log.txt             ← All alerts logged with timestamps
│
├── docs/
│   ├── project_explanation.md    ← Full technical + simple explanation
│   ├── digital_assignment_1_report.md ← CPS assignment report template
│   ├── digital_assignment_2_report.md ← MQTT communication assignment report
│   └── github_upload_guide.md    ← Day-wise proof strategy + commit guide
│
├── circuit_diagram/
│   └── wokwi_setup_guide.md      ← How to load and run on Wokwi
│
├── images/                       ← Screenshots for GitHub proof
├── main.py                       ← Single entry point (run this!)
├── communication/                ← MQTT receiver for DA2
│   ├── __init__.py
│   └── mqtt_subscriber.py
├── requirements.txt
├── .gitignore
├── .env.example
└── README.md
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager
- A modern web browser (Chrome / Firefox)
- Wokwi account (free): https://wokwi.com

### Step 1: Clone the Repository
```bash
git clone https://github.com/Anupam-Santra/IoT-Enabled-Smart-Agriculture-Monitoring-System.git
cd IoT-Enabled-Smart-Agriculture-Monitoring-System
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Dashboard
```bash
python main.py
```
Then open your browser at: **http://localhost:8050**

### Step 4: Terminal-Only Mode (no browser)
```bash
python main.py --sim-only
```

---

## 🔌 Wokwi Hardware Simulation

### Quick Start
1. Go to **https://wokwi.com/esp32**
2. In the **code editor** tab → paste contents of `arduino_code/smart_agriculture.ino`
3. In the **diagram.json** tab → paste contents of `arduino_code/diagram.json`
4. Click ▶ **Play**
5. Open **Serial Monitor** to see live sensor readings

### Components Auto-Placed by diagram.json

| Component | Simulates |
|-----------|-----------|
| ESP32 DevKit V1 | Main microcontroller |
| DHT22 | Temperature + Humidity |
| Potentiometer (pot1) | Soil Moisture Sensor |
| Potentiometer (pot2) | Water Level Sensor |
| Potentiometer (pot3) | Rain Sensor |
| LDR / Photoresistor | Light Intensity |
| Blue LED | Water Pump indicator |
| Red LED | Alert indicator |

### Interaction Guide
| Action | How to do it on Wokwi |
|--------|----------------------|
| Simulate dry soil | Drag pot1 slider LEFT |
| Simulate full water tank | Drag pot2 slider RIGHT |
| Simulate rain | Drag pot3 slider RIGHT (>60%) |
| Simulate high temperature | Click DHT22 → change temperature to 40 |
| Simulate dark/night | Click LDR → set lux to 10 |

---

## 🌡️ Sensor Thresholds

| Sensor | Threshold | Action Triggered |
|--------|-----------|-----------------|
| Soil Moisture | < 30% | 🟢 Pump ON |
| Soil Moisture | ≥ 70% | ⚫ Pump OFF |
| Temperature | > 35°C | ⚠️ HIGH TEMPERATURE alert |
| Temperature | < 5°C | ⚠️ FROST RISK alert |
| Humidity | < 30% | ⚠️ LOW HUMIDITY alert |
| Water Level | < 20% | ⚠️ WATER TANK CRITICAL + pump disabled |
| Light Intensity | < 20% | ⚠️ LOW LIGHT alert |
| Rain Level | > 60% | 🌧️ Pump override OFF |

---

## 🔄 Simulation Scenarios

The system automatically cycles through 11 realistic farm conditions every 8 readings:

| # | Scenario | Condition |
|---|----------|-----------|
| 1 | Normal Day | All values healthy, no alerts |
| 2 | Dry Soil | Low soil moisture → pump activated |
| 3 | High Temperature | Heat stress → temperature alert |
| 4 | Rainy Day | Rain detected → pump override OFF |
| 5 | Low Water Tank | Critical tank level → pump disabled |
| 6 | Night / Low Light | Low light intensity → light alert |
| 7 | Seedling Care | Mild conditions for young plants |
| 8 | Heatwave Drought | Heat, low humidity, and dry-soil stress |
| 9 | Storm Incoming | Rising rain with reduced light |
| 10 | Frost Risk | Temperature below 5°C → frost alert |
| 11 | Irrigation Recovery | Dry-to-moderate soil with limited water reserve |

---

## 📊 Sample Output

### Terminal Output
```
====================================================
  Reading #0012  |  Scenario: Dry Soil — Pump Needed
====================================================
  🌱 Soil Moisture   :  18.3 %
  🌡️  Temperature     :  29.4 °C
  💧 Humidity        :  47.2 %
  ☀️  Light Intensity :  68.1 %
  🪣 Water Level     :  64.5 %
  🌧️  Rain Level      :   2.1 %
  ------------------------------------------------
  💦 Pump Status     : 🟢 ON  [ACTIVE]
     Reason          : Soil is DRY — pump activated
  ------------------------------------------------
  ⚠️  ALERT: DRY_SOIL
```

### sensor_log.csv Sample
```csv
timestamp,reading_no,scenario,soil_moisture_%,temperature_C,humidity_%,light_intensity_%,water_level_%,rain_level_%,pump_status,alerts
2024-07-15 10:23:01,1,Normal Day,52.3,27.1,61.4,74.2,68.9,3.2,OFF,None
2024-07-15 10:23:03,2,Normal Day,49.8,26.8,59.7,72.1,70.1,4.5,OFF,None
2024-07-15 10:23:05,3,Dry Soil — Pump Needed,18.3,29.4,47.2,68.1,64.5,2.1,ON,DRY_SOIL
2024-07-15 10:23:07,4,High Temperature Alert,25.1,38.7,22.4,88.3,55.2,1.8,OFF,HIGH_TEMPERATURE|LOW_HUMIDITY
```
---

# 📸 Project Outputs

<p align="center">
  <img src="images/IoT-Enabled-Smart-Agriculture-Monitoring-System.png" width="900">
</p>

<p align="center">
  <b>Main Smart Agriculture Dashboard</b>
</p>

---

## Dashboard Screens

<p align="center">
  <img src="images/Screenshot%202026-06-14%20174710.png" width="45%">
  <img src="images/Screenshot%202026-06-14%20174726.png" width="45%">
</p>

<p align="center">
  <b>Real-Time Monitoring & Analytics Views</b>
</p>

---

### Dashboard Features Demonstrated

- 🌱 Soil Moisture Monitoring
- 🌡️ Temperature Tracking
- 💧 Humidity Analysis
- ☀️ Light Intensity Detection
- 🪣 Water Tank Monitoring
- 🌧️ Rain Detection
- 💦 Automatic Pump Control
- ⚠️ Intelligent Alert System
- 📊 Live Data Visualization
- 📁 Historical Data Logging

---

## 📋 IoT Concepts Demonstrated

- ✅ Sensor Integration (6 sensor types)
- ✅ Actuator Control (pump ON/OFF relay simulation)
- ✅ Threshold-based Automation
- ✅ Real-time Monitoring Dashboard
- ✅ Data Logging (CSV + text)
- ✅ Edge Computing (logic runs on ESP32)
- ✅ Alert System (dual: UI + terminal)
- ✅ Hardware Simulation (Wokwi ESP32)
- ✅ Software Simulation (Python)
- ✅ Modular Code Architecture

---

## 🎓 Learning Outcomes

After studying this project, you will be able to:
- Explain how IoT sensors work in agriculture
- Understand ESP32 analog/digital pin mapping
- Write threshold-based automation logic
- Build real-time dashboards with Python
- Simulate hardware without physical components
- Structure and document a complete IoT project
- Apply version control and GitHub best practices

---

## 👨‍💻 Author

**Anupam Santra**  
B.Tech Computer Science | ML/IoT Engineer  
🔗 GitHub: [github.com/Anupam-Santra](https://github.com/Anupam-Santra)  
🔗 LinkedIn: [linkedin.com/in/anupam-santra](https://linkedin.com/in/anupam-santra)

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">
⭐ If this project helped you, please star the repository!
</div>
