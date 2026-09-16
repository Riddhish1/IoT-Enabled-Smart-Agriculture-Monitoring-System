# IoT-Enabled Smart Agriculture Monitoring System
## Complete Project Explanation
**Author: Anupam Santra**

---

## 1. Simple Explanation

Imagine a farmer who has to walk to his field every few hours to check if the soil is dry, if the
temperature is too hot for crops, or if the water tank is running low. This is time-consuming,
inefficient, and often inaccurate.

A **Smart Agriculture Monitoring System** uses small electronic sensors placed in the farm to do
this automatically. These sensors measure:

- How wet or dry the soil is
- How hot or cold the temperature is
- How humid the air is
- How bright the sunlight is
- How full the water tank is
- Whether it is raining

All this data is sent to a computer (or phone), displayed on a dashboard, and acted upon
automatically — for example, turning on a water pump when the soil gets too dry.

---

## 2. Technical Explanation

The system uses:
- **Microcontroller**: ESP32 — a WiFi-enabled chip that reads all sensor values
- **Sensors**: DHT22, Soil Moisture, LDR, Water Level, Rain Sensor
- **Threshold Logic**: Comparisons determine when to act (e.g., soil < 30% → pump ON)
- **Actuator**: Water Pump / Relay — turns on/off based on decisions
- **Dashboard**: Plotly Dash web app showing real-time readings
- **Data Logging**: All readings saved to CSV, alerts saved to TXT

---

## 3. Problem Statement

Traditional farming relies on manual inspection and guesswork for irrigation decisions.
This leads to:
- **Over-irrigation**: Wasting water, root damage
- **Under-irrigation**: Crop failure, yield loss
- **Delayed responses**: Farmer not present when conditions change
- **No historical data**: Cannot analyze patterns over time

Smart agriculture solves all of these.

---

## 4. How Different Users Benefit

| User | Benefit |
|------|---------|
| Small farmer | Automated irrigation, save water |
| Greenhouse owner | Precise humidity and temperature control |
| Agriculture company | Monitor multiple farms remotely |
| Irrigation team | Data-driven pump scheduling |
| Smart farming startup | Platform for precision agriculture |

---

## 5. Sensor Data Flow

```
Physical World
      │
      ▼
┌─────────────────────────────────────────────┐
│            SENSOR LAYER                     │
│  Soil │ DHT22 │ LDR │ Water │ Rain          │
└─────────────┬───────────────────────────────┘
              │  analog/digital readings
              ▼
┌─────────────────────────────────────────────┐
│         MICROCONTROLLER (ESP32)             │
│  - Reads all sensor values                  │
│  - Converts analog to percentage            │
│  - Applies threshold comparison             │
└─────────────┬───────────────────────────────┘
              │  decisions + values
              ▼
┌─────────────────────────────────────────────┐
│           PROCESSING LAYER                  │
│  - Irrigation decision logic                │
│  - Alert generation                         │
│  - Data formatting                          │
└──────────┬──────────────┬───────────────────┘
           │              │
           ▼              ▼
┌─────────────┐   ┌───────────────┐
│  ACTUATOR   │   │  DATA LAYER   │
│  Pump ON/OFF│   │  CSV logging  │
│  Alert LED  │   │  Alert log    │
└─────────────┘   └───────┬───────┘
                          │
                          ▼
               ┌────────────────────┐
               │   DASHBOARD LAYER  │
               │  Real-time gauges  │
               │  Alert banners     │
               │  Historical charts │
               └────────────────────┘
```

---

## 6. IoT Concepts Demonstrated

| Concept | Where Used |
|---------|-----------|
| Sensor integration | DHT22, soil moisture, LDR, water level, rain |
| Actuator control | Water pump ON/OFF relay simulation |
| Threshold-based automation | Pump logic, alert generation |
| Real-time monitoring | Plotly Dash auto-refresh every 2 seconds |
| Data logging | CSV file, alert log file |
| Edge computing | Threshold logic runs on ESP32 itself |
| Alert system | Both dashboard banners + terminal output |
| Simulation | Wokwi (hardware) + Python (software) |

---

## 7. Threshold Reference Table

| Sensor | Threshold | Action |
|--------|-----------|--------|
| Soil Moisture | < 30% | Pump ON |
| Soil Moisture | ≥ 70% | Pump OFF |
| Temperature | > 35°C | Alert: HIGH TEMPERATURE |
| Temperature | < 5°C | Alert: FROST RISK |
| Humidity | < 30% | Alert: LOW HUMIDITY |
| Water Level | < 20% | Alert + Disable Pump |
| Light Intensity | < 20% | Alert: LOW LIGHT |
| Rain Level | > 60% | Pump Override OFF |

---

## 8. Simulation Scenarios

The Python simulation and Wokwi demo cycle through 11 realistic farm scenarios:

1. **Normal Day** — All values within acceptable range
2. **Dry Soil — Pump Needed** — Low moisture triggers pump
3. **High Temperature Alert** — Heat stress condition
4. **Rainy Day** — Rain detected, pump override
5. **Low Water Tank** — Tank critically low, pump disabled
6. **Night / Low Light** — Low light intensity alert
7. **Seedling Care** — Gentle conditions for young plants
8. **Heatwave Drought** — Combined heat, dry soil, and low humidity
9. **Storm Incoming** — Rising rain with reduced light
10. **Frost Risk** — Temperature below 5°C
11. **Irrigation Recovery** — Soil recovering with a limited water reserve

---

## 9. Architecture Diagram

```
┌──────────────────────────────────────────────────────┐
│                   WOKWI SIMULATION                   │
│                                                      │
│  [DHT22]──┐                                          │
│  [Soil] ──┤                                          │
│  [LDR]  ──┼──→ [ESP32] ──→ [Pump LED] (GPIO 26)     │
│  [Water]──┤         └────→ [Alert LED] (GPIO 27)     │
│  [Rain] ──┘                                          │
└──────────────────────────────────────────────────────┘
                          ↕ (mirrors logic)
┌──────────────────────────────────────────────────────┐
│                 PYTHON SIMULATION                    │
│                                                      │
│  sensor_simulator.py                                 │
│    → 6 sensor values generated                       │
│    → threshold logic applied                         │
│    → pump ON/OFF decided                             │
│    → alerts generated                                │
│    → data/sensor_log.csv updated                     │
│    → outputs/alert_log.txt updated                   │
└──────────────────────────────────────────────────────┘
                          ↕
┌──────────────────────────────────────────────────────┐
│               PLOTLY DASH DASHBOARD                  │
│                   localhost:8050                      │
│                                                      │
│  [Alert Banners]  [Status Cards]                     │
│  [6 Gauge Charts]                                    │
│  [Live History Chart]                                │
│  [Pump Status]  [Scenario Display]                   │
└──────────────────────────────────────────────────────┘
```

---

## 10. Learning Outcomes

After completing this project, you will understand:

- How IoT sensors work and how to simulate them
- How microcontrollers (ESP32/Arduino) read sensor data
- How to write threshold-based automation logic
- How to build real-time dashboards with Python
- How to log and store IoT data in structured formats
- How to simulate hardware using Wokwi
- How to structure and publish an IoT project on GitHub
- Industry-standard practices: alerts, logging, modular code
