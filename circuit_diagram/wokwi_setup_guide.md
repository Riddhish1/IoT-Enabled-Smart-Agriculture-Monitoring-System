# Wokwi ESP32 Simulation Setup Guide
**IoT Smart Agriculture Monitoring System**  
Author: Anupam Santra

---

## What is Wokwi?
Wokwi (https://wokwi.com) is a free online IoT simulator that runs ESP32, Arduino, and other
microcontrollers in your browser — no physical hardware needed.

---

## Step-by-Step: Load the Project on Wokwi

### Step 1 — Open Wokwi ESP32
1. Go to: **https://wokwi.com/esp32**
2. You will see a new empty ESP32 project with two tabs:
   - `sketch.ino` — the code editor
   - `diagram.json` — the circuit diagram

---

### Step 2 — Paste the Arduino Code
1. Click the **`sketch.ino`** tab
2. Select all existing text (Ctrl+A)
3. Delete it
4. Open the file: `arduino_code/smart_agriculture.ino`
5. Copy all the code and paste it into Wokwi

---

### Step 3 — Paste the Circuit Diagram
1. Click the **`diagram.json`** tab
2. Select all existing text (Ctrl+A)
3. Delete it
4. Open the file: `arduino_code/diagram.json`
5. Copy all the content and paste it into Wokwi

After pasting, you will see the following components appear automatically:

| Component | Label | What it simulates |
|-----------|-------|-------------------|
| ESP32 DevKit V1 | esp | Main microcontroller |
| DHT22 Sensor | dht1 | Temperature + Humidity |
| Potentiometer | pot1 | Soil Moisture Sensor |
| Potentiometer | pot2 | Water Level Sensor |
| Potentiometer | pot3 | Rain Sensor |
| LDR (Photoresistor) | ldr1 | Light Intensity Sensor |
| Blue LED | led1 | Water Pump (ON/OFF indicator) |
| Red LED | led2 | Alert Indicator |

---

### Step 4 — Run the Simulation
1. Click the green **▶ Play** button (top left)
2. Wait 2–3 seconds for the simulation to boot
3. Click **Serial Monitor** (bottom panel) to see sensor readings

By default, the firmware runs in **automatic scenario demo mode**. It cycles through all 11
profiles every 8 readings, so the LEDs and Serial Monitor demonstrate the system without manual
changes. To use the Wokwi controls instead, change `#define DEMO_MODE true` to `false` and run
the simulation again.

---

### Step 5 — Interact with the Simulation

#### Automatic scenario demo:
- Watch the `Scenario` line in Serial Monitor change after every 8 readings.
- `Heatwave Drought` demonstrates multiple simultaneous alerts and pump activation.
- `Storm Incoming` demonstrates rain approaching the irrigation override threshold.
- `Frost Risk` demonstrates the new temperature-below-5°C alert.
- `Irrigation Recovery` demonstrates moderate soil moisture with a limited water reserve.

#### Manual sensor mode (`DEMO_MODE false`):

#### Simulate Dry Soil (Pump should turn ON):
- Drag **pot1 (Soil Moisture)** slider to the LEFT (low value, ~20%)
- Watch the Blue LED turn ON (pump activated)
- Serial Monitor shows: `[PUMP] Water pump turned ON → Soil is DRY`

#### Simulate High Temperature Alert:
- Click on the **DHT22 sensor**
- Change the `temperature` attribute to `40`
- Serial Monitor shows: `[ALERT] HIGH TEMPERATURE DETECTED!`
- Red LED turns ON

#### Simulate Rainy Day (Pump Override OFF):
- Drag **pot3 (Rain Sensor)** slider to the RIGHT (high value, ~80%)
- Pump turns OFF even if soil is dry
- Serial Monitor shows: `[INFO] Rain detected. Pump override OFF.`

#### Simulate Low Water Tank:
- Drag **pot2 (Water Level)** slider to the LEFT (low value, ~10%)
- Serial Monitor shows: `[ALERT] WATER TANK LEVEL CRITICAL!`
- Pump is disabled even if soil is dry

#### Simulate Low Light (Night):
- Click on **LDR sensor**
- Set lux value to `10`
- Serial Monitor shows: `[ALERT] LOW LIGHT INTENSITY!`

---

### Step 6 — Take Screenshots for GitHub

Capture these screenshots and save them in the `images/` folder:

| Screenshot | File name to use |
|------------|-----------------|
| Full Wokwi circuit with all components | `wokwi_circuit.png` |
| Serial Monitor showing normal readings | `serial_normal.png` |
| Serial Monitor showing DRY SOIL + pump ON | `serial_dry_soil.png` |
| Serial Monitor showing HIGH TEMP alert | `serial_high_temp.png` |
| Serial Monitor showing LOW WATER alert | `serial_low_water.png` |
| Serial Monitor showing RAIN override | `serial_rain.png` |
| Dashboard in browser (from Python) | `dashboard.png` |

---

## Circuit Pin Reference

| ESP32 Pin | Connected To | Signal |
|-----------|-------------|--------|
| GPIO 15 | DHT22 DATA | Temperature + Humidity |
| GPIO 34 | Pot1 SIG | Soil Moisture (Analog) |
| GPIO 32 | Pot2 SIG | Water Level (Analog) |
| GPIO 33 | Pot3 SIG | Rain Sensor (Analog) |
| GPIO 35 | LDR AO | Light Intensity (Analog) |
| GPIO 26 | Blue LED (via 220Ω) | Water Pump |
| GPIO 27 | Red LED (via 220Ω) | Alert Indicator |
| 3.3V | All VCC pins | Power |
| GND | All GND pins | Ground |

---

## Troubleshooting

**DHT22 reads NaN?**
→ Wait 2–3 seconds after pressing Play. DHT22 needs warmup time.

**LEDs not lighting?**
→ Check that diagram.json was pasted correctly and simulation is running.

**Serial Monitor blank?**
→ Click the Serial Monitor tab at the bottom of Wokwi.

**Potentiometer not changing values?**
→ Click the potentiometer knob and drag left/right.

---

## Wokwi Project Link
After creating your project, copy the URL from your browser (e.g. `https://wokwi.com/projects/XXXXXXXXXX`) and paste it in your README.md under the "Live Simulation" section.
