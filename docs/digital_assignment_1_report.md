# DIGITAL ASSIGNMENT - 1

## CPS Problem Identification and Simulation

# IoT-Enabled Smart Agriculture Monitoring and Irrigation Control System

## Team Details

| Team Member Name | Register Number |
|---|---|
| [Enter Name 1] | [Register No. 1] |
| [Enter Name 2] | [Register No. 2] |
| [Enter Name 3] | [Register No. 3] |

## 1. Problem Statement

Agricultural fields require regular monitoring of soil moisture, temperature, humidity, sunlight, water availability, and rainfall. Manual inspection is time-consuming and can result in delayed irrigation, water wastage, crop stress, and damage caused by extreme weather conditions.

This project develops a Cyber-Physical System that senses field conditions, processes the readings on an ESP32 controller, automatically controls a simulated water pump, and activates an alert indicator in the Wokwi simulator.

## 2. Objectives

To develop a Cyber-Physical System that:

- Measures soil moisture, temperature, humidity, light intensity, water level, and rain level.
- Processes sensor data using threshold-based decision logic.
- Automatically turns the irrigation pump on when soil is dry and water is available.
- Prevents irrigation during rain or when the water tank is critically low.
- Activates an alert LED when unsafe agricultural conditions are detected.
- Demonstrates real-time sensor input, processing, and actuation in Wokwi.
- Tests multiple agricultural conditions using automatic scenario profiles and manual controls.

## 3. CPS Architecture and Design

### 3.1 Block Diagram

```text
Physical Farm Environment
        |
        v
+-----------------------------+
| Sensor Layer                |
| Soil, DHT22, LDR, Water,   |
| Rain sensors                |
+-------------+---------------+
              | Sensor readings
              v
+-----------------------------+
| ESP32 Controller            |
| Read, convert, validate,    |
| apply thresholds            |
+-------------+---------------+
              | Control decisions
              +------------------+
              |                  |
              v                  v
+-------------------+  +----------------------+
| Actuator Layer    |  | Alert and Output Layer |
| Pump LED / Relay  |  | Alert LED, Serial    |
|                   |  | Monitor output       |
+-------------------+  +----------+-----------+
```

**Screenshot required:** Capture the complete Wokwi circuit and use it below the diagram in the submitted document.

### 3.2 System Components

| Component | Type | Quantity | Purpose |
|---|---|---:|---|
| ESP32 DevKit V1 | Controller | 1 | Reads sensors and controls outputs |
| DHT22 | Digital sensor | 1 | Measures temperature and humidity |
| Potentiometer | Analog sensor simulator | 3 | Simulates soil moisture, water level, and rain |
| Photoresistor/LDR | Analog sensor | 1 | Measures light intensity |
| Blue LED | Actuator indicator | 1 | Simulates water pump operation |
| Red LED | Alert actuator | 1 | Indicates an active alert |
| 220 ohm resistor | Current limiting component | 2 | Protects the LEDs |
| Serial Monitor | Communication/debugging | 1 | Displays readings and decisions |

## 4. Simulator and Tools

**Simulator used:** Wokwi ESP32 Simulator

**Software tools used:**

- Arduino C++ firmware
- ESP32 DevKit V1
- DHT22, photoresistor, potentiometers, LEDs, and resistors
- Visual Studio Code

**Reason for using Wokwi:** Wokwi is browser-based, free for basic simulation, supports ESP32 components, and allows sensor controls and Serial Monitor output without physical hardware.

## 5. Implementation

### 5.1 Circuit Design

The Wokwi circuit contains six simulated sensors connected to the ESP32. The DHT22 provides temperature and humidity. Potentiometers simulate soil moisture, water level, and rain. The photoresistor simulates light intensity. A blue LED represents the pump and a red LED represents the alert output.

**Wokwi files used:**

- `arduino_code/diagram.json`
- `arduino_code/smart_agriculture.ino`

**Screenshot required:** Capture the full circuit with every component, label, wire, and ESP32 pin visible.

### 5.2 Pin Configuration

| Sensor or actuator | ESP32 pin | Signal or purpose |
|---|---:|---|
| DHT22 data | GPIO 15 | Temperature and humidity |
| Soil moisture potentiometer | GPIO 34 | Analog soil moisture |
| Water level potentiometer | GPIO 32 | Analog tank level |
| Rain sensor potentiometer | GPIO 33 | Analog rain level |
| LDR analog output | GPIO 35 | Analog light intensity |
| Pump LED | GPIO 26 | Pump ON/OFF indicator |
| Alert LED | GPIO 27 | Alert indicator |
| Sensor power | 3V3 | VCC |
| Sensor ground | GND | Ground reference |

### 5.3 Threshold and Control Logic

| Reading | Threshold | System action |
|---|---|---|
| Soil moisture | Below 30% | Turn pump ON if water is available and rain is not active |
| Soil moisture | 70% or higher | Turn pump OFF because soil is sufficiently wet |
| Temperature | Above 35 C | Activate high-temperature alert |
| Temperature | Below 5 C | Activate frost-risk alert |
| Humidity | Below 30% | Activate low-humidity alert |
| Water level | Below 20% | Activate tank alert and disable the pump |
| Light intensity | Below 20% | Activate low-light alert |
| Rain level | Above 60% | Override irrigation and turn pump OFF |

### 5.4 Operating Modes

The firmware supports two Wokwi modes:

- **Automatic scenario demo:** `#define DEMO_MODE true` cycles through 11 predefined farm conditions. Each scenario remains active for 8 readings.
- **Manual sensor mode:** `#define DEMO_MODE false` reads the potentiometer, LDR, and DHT22 controls directly.

### 5.5 Program Code Summary

The main firmware functions are:

- `setup()` initializes Serial communication, pins, the DHT22, and random scenario generation.
- `loop()` reads or generates sensor values and runs the control cycle.
- `toPercent()` converts ESP32 analog readings from 0-4095 to 0-100 percent.
- The scenario profile table generates realistic sensor ranges in automatic demo mode.
- Threshold checks identify unsafe conditions.
- Pump logic permits irrigation only when soil is dry, water is available, and rain is not active.

**Screenshot required:** Capture the Arduino sketch showing `setup()`, `loop()`, sensor reading, threshold, and pump-control sections.

## 6. Testing and Test Cases

### 6.1 Test Case 1: Dry Soil with Available Water

| Test parameter | Expected output | Actual output |
|---|---|---|
| Soil moisture | Below 30% | Fill after running |
| Water level | At least 20% | Fill after running |
| Rain level | Below 60% | Fill after running |
| Pump | Blue LED ON | Fill after running |
| Alert | DRY_SOIL may be shown | Fill after running |
| Result | PASS | [PASS / FAIL] |

**Wokwi action:** In manual mode, move the soil potentiometer left, keep the water potentiometer above 20%, and keep the rain potentiometer below 60%.

### 6.2 Test Case 2: Rain Override

| Test parameter | Expected output | Actual output |
|---|---|---|
| Rain level | Above 60% | Fill after running |
| Soil moisture | Dry or moderate | Fill after running |
| Pump | Blue LED OFF | Fill after running |
| Serial message | Rain detected. Pump override OFF. | Fill after running |
| Result | PASS | [PASS / FAIL] |

**Wokwi action:** In manual mode, move the rain potentiometer right above 60%. The pump must remain OFF even if the soil is dry.

### 6.3 Test Case 3: Low Water Tank Protection

| Test parameter | Expected output | Actual output |
|---|---|---|
| Water level | Below 20% | Fill after running |
| Soil moisture | Below 30% | Fill after running |
| Pump | Blue LED OFF | Fill after running |
| Alert LED | Red LED ON | Fill after running |
| Serial message | Water tank critical and pump disabled | Fill after running |
| Result | PASS | [PASS / FAIL] |

**Wokwi action:** In manual mode, move the water-level potentiometer left below 20% and the soil potentiometer left below 30%.

### 6.4 Test Case 4: High Temperature and Low Humidity

| Test parameter | Expected output | Actual output |
|---|---|---|
| Temperature | Above 35 C | Fill after running |
| Humidity | Below 30% | Fill after running |
| Alert LED | Red LED ON | Fill after running |
| Serial output | High-temperature and low-humidity alerts | Fill after running |
| Result | PASS | [PASS / FAIL] |

**Wokwi action:** In manual mode, set the DHT22 temperature above 35 C and humidity below 30, then wait for the next reading.

### 6.5 Test Case 5: Automatic Scenario Cycle

| Test parameter | Expected output | Actual output |
|---|---|---|
| Firmware mode | `DEMO_MODE true` | Fill after running |
| Scenario count | 11 profiles | Fill after running |
| Scenario transition | Changes every 8 readings | Fill after running |
| Frost scenario | Frost-risk alert below 5 C | Fill after running |
| Heatwave scenario | Heat, dry soil, and humidity alerts | Fill after running |
| Result | PASS | [PASS / FAIL] |

**Wokwi action:** Run the firmware in automatic scenario mode and capture the Serial Monitor while `Heatwave Drought`, `Storm Incoming`, or `Frost Risk` is displayed.

## 7. Results and Observations

The system demonstrates the complete CPS loop:

- Sensors or simulated profiles provide environmental readings.
- The ESP32 processes readings locally using threshold rules.
- The pump indicator responds to soil, rain, and tank conditions.
- The alert LED responds to unsafe environmental conditions.
- The Serial Monitor provides real-time diagnostic output.
- The Serial Monitor provides real-time readings, alerts, scenario names, and pump decisions.

**Observed results to record:**

- Dry soil with sufficient water activates the pump.
- Rain overrides irrigation and keeps the pump OFF.
- A critically low tank disables the pump for protection.
- High temperature, low humidity, low light, and frost conditions activate alerts.
- Automatic demo mode cycles through 11 agricultural scenarios.

## 8. Required Screenshots

Take these screenshots from Wokwi. Crop them only enough to remove unrelated browser content; keep labels and outputs readable.

| Screenshot | What must be visible | Suggested file name |
|---|---|---|
| Complete circuit | ESP32, all six sensors, LEDs, resistors, and wiring | `wokwi_complete_circuit.png` |
| Firmware code | `setup()`, `loop()`, thresholds, and pump logic | `arduino_firmware_code.png` |
| Normal operation | Serial Monitor with normal readings and pump OFF | `wokwi_normal_reading.png` |
| Dry soil response | Soil below 30%, pump message, blue LED ON | `wokwi_dry_soil_pump_on.png` |
| Rain override | Rain above 60%, override message, blue LED OFF | `wokwi_rain_override.png` |
| Low tank protection | Water below 20%, critical alert, pump disabled | `wokwi_low_water_alert.png` |
| Heatwave response | High temperature and low humidity alerts | `wokwi_heatwave_alert.png` |
| Frost response | Scenario `Frost Risk`, temperature below 5 C, red LED ON | `wokwi_frost_alert.png` |
| Automatic scenario mode | Scenario name and multiple Serial readings | `wokwi_scenario_cycle.png` |

### Screenshot procedure in Wokwi

1. Open a new ESP32 project at `https://wokwi.com/esp32`.
2. Paste `arduino_code/smart_agriculture.ino` into the code editor.
3. Paste `arduino_code/diagram.json` into the diagram editor.
4. Confirm the DHT library dependency is available.
5. Click Play and open the Serial Monitor.
6. For automatic screenshots, keep `DEMO_MODE true`.
7. For manual screenshots, change `DEMO_MODE` to `false`, restart the simulation, and adjust the controls.
8. Wait for a complete reading to appear before taking each screenshot.
9. Save screenshots in the repository `images/` folder using the names in the table.

## 9. Conclusion

The IoT-Enabled Smart Agriculture Monitoring and Irrigation Control System successfully demonstrates a Cyber-Physical System for agricultural monitoring.

**Sensing:** The ESP32 receives data from soil, temperature, humidity, light, water-level, and rain inputs.

**Processing:** Threshold logic evaluates field conditions and determines whether irrigation is safe and necessary.

**Actuation:** The blue pump LED and red alert LED provide visible responses to controller decisions.

**Monitoring:** The Serial Monitor provides real-time sensor readings, scenario names, alert messages, and pump status.

The system can reduce unnecessary irrigation, protect the pump when the tank is low, respond to rain, and identify environmental risks such as heat, frost, low humidity, and low light. Future work can add MQTT communication, real sensors, cloud storage, mobile notifications, and crop-specific thresholds.

## 10. Appendix

### 10.1 Wokwi Project Link

[Open the Smart Agriculture Wokwi project](https://wokwi.com/projects/473246028714505217)

### 10.2 Repository Files

- `arduino_code/smart_agriculture.ino` - ESP32 firmware
- `arduino_code/diagram.json` - Wokwi circuit
- `docs/digital_assignment_1_report.md` - Assignment report

### 10.3 Technical Summary

- Controller: ESP32 DevKit V1
- Number of monitored values: 6
- Automatic scenario profiles: 11
- Analog conversion range: 0-4095 to 0-100 percent
- Pump output: GPIO 26
- Alert output: GPIO 27
- Serial baud rate: 115200
- Automatic scenario duration: 8 readings
- Default reading interval: 3 seconds
