# DIGITAL ASSIGNMENT - 2

## CPS Communication, Data Acquisition and Monitoring

# AgriSense: MQTT-Enabled Smart Agriculture Monitoring System

## Team Details

| Team Member Name | Register Number |
|---|---|
| [Enter Name 1] | [Register No. 1] |
| [Enter Name 2] | [Register No. 2] |
| [Enter Name 3] | [Register No. 3] |

## 1. Objective

Digital Assignment 2 extends the Digital Assignment 1 agriculture CPS by adding real-time data acquisition, MQTT communication, a Python MQTT receiver, and live monitoring. The ESP32 remains responsible for edge processing and safe pump decisions.

## 2. DA1 to DA2 Progression

| DA1 | DA2 Extension |
|---|---|
| ESP32 reads or simulates sensors | ESP32 publishes live readings through MQTT |
| Local Serial Monitor | Serial Monitor plus MQTT receiver output |
| Local pump and alert decisions | Decisions remain at the edge and are transmitted |
| Wokwi circuit | Wokwi circuit with Wi-Fi and MQTT connectivity |
| Scenario-based testing | Communication, monitoring, and failure testing |

## 3. Enhanced CPS Architecture

```text
+----------------------+
| Wokwi Sensors        |
| Soil, DHT22, LDR,    |
| Water, Rain          |
+----------+-----------+
           | sensor readings
           v
+----------------------+
| ESP32 Edge Controller|
| Read sensors         |
| Apply thresholds     |
| Control pump/alert   |
| Create JSON payload  |
+----------+-----------+
           | MQTT publish
           v
+----------------------+
| MQTT Broker          |
| broker.hivemq.com    |
+----------+-----------+
           | MQTT subscribe
           v
+----------------------+       +----------------------+
| Python MQTT Receiver | ----> | Plotly Dash Monitor  |
| Validate JSON        |       | Gauges and history   |
| Keep recent readings |       | Pump and alerts     |
+----------------------+       +----------------------+
```

## 4. Added Components and Tools

| Component | Purpose |
|---|---|
| ESP32 Wi-Fi | Connects the CPS node to the network |
| MQTT broker | Transfers sensor data between the ESP32 and receiver |
| PubSubClient | MQTT library used by the ESP32 |
| Paho MQTT | MQTT library used by Python |
| MQTT subscriber | Receives and validates ESP32 JSON data |
| Plotly Dash | Displays received sensor data and status |

## 5. Communication Protocol

MQTT was selected because it is lightweight, fast, suitable for IoT devices, and supports publish/subscribe communication. The ESP32 is the publisher, HiveMQ is the broker, and the Python receiver is the subscriber.

| Topic | Publisher | Subscriber | Data |
|---|---|---|---|
| `agrisense/field1/sensors` | ESP32 | Python receiver | Sensor values, pump, alerts |
| `agrisense/field1/status` | ESP32 | Python receiver | Online status |
| `agrisense/field1/alerts` | Reserved | Future extension | Alert events |
| `agrisense/field1/pump` | Reserved | Future extension | Actuator events |

Example sensor payload:

```json
{
  "reading_no": 12,
  "timestamp": "60s",
  "scenario": "Live Wokwi Sensors",
  "soil_moisture": 18,
  "temperature": 38.2,
  "humidity": 27.0,
  "light_intensity": 84,
  "water_level": 55,
  "rain_level": 2,
  "pump": "ON",
  "pump_reason": "Soil is dry - pump activated",
  "alerts": ["HIGH_TEMPERATURE", "LOW_HUMIDITY", "DRY_SOIL"]
}
```

## 6. Data Acquisition and Edge Processing

The ESP32 acquires data from GPIO 34, 35, 32, 33, and the DHT22 on GPIO 15. Analog readings are converted from the ESP32 range 0-4095 into percentages.

The ESP32 applies these rules before publishing:

- Rain above 60% disables irrigation.
- Water below 20% disables the pump.
- Soil below 30% activates the pump when irrigation is safe.
- Soil at least 70% keeps the pump idle.
- Temperature above 35 C creates a high-temperature alert.
- Temperature below 5 C creates a frost-risk alert.
- Humidity below 30% creates a low-humidity alert.
- Light below 20% creates a low-light alert.

This is edge processing because the actuator decision is made locally even if the MQTT receiver or dashboard is unavailable.

## 7. Implementation Files

- `arduino_code/arduino_code.ino`: ESP32 Wi-Fi, sensor, edge-control, and MQTT publisher.
- `arduino_code/diagram.json`: Wokwi circuit and GPIO connections.
- `arduino_code/libraries.txt`: Wokwi library declarations.
- `communication/mqtt_subscriber.py`: Python MQTT receiver and recent-reading state.
- `dashboard/app.py`: Dashboard that consumes MQTT snapshots.
- `requirements.txt`: Includes `paho-mqtt`.

## 8. How to Run

### ESP32 and Wokwi

1. Open the Wokwi project: https://wokwi.com/projects/473246028714505217
2. Open the Code tab.
3. Replace the sketch with `arduino_code/arduino_code.ino`.
4. Add the libraries from `arduino_code/libraries.txt` if Wokwi does not install them automatically.
5. Confirm the circuit uses GPIO 26 for the blue pump LED and GPIO 27 for the red alert LED.
6. Start the simulation and open the Serial Monitor.

### Python receiver and dashboard

Install the dependencies:

```powershell
pip install -r requirements.txt
```

Start the dashboard:

```powershell
python main.py
```

The dashboard opens at `http://localhost:8050` and waits for MQTT data from the ESP32.

To run only the receiver:

```powershell
python -m communication.mqtt_subscriber
```

## 9. Experiments and Test Cases

### Test Case 1: MQTT Connection

**Input:** Start Wokwi with Wi-Fi available.

**Expected:** Serial Monitor shows `WiFi connected`, then `Connecting to MQTT...connected`.

**Evidence:** Wokwi Serial Monitor screenshot.

### Test Case 2: Sensor Publishing

**Input:** Allow one complete sensor cycle.

**Expected:** Serial Monitor shows `MQTT published:` followed by JSON, and the Python dashboard updates.

**Evidence:** Serial Monitor and dashboard screenshots.

### Test Case 3: Dry Soil Pump Activation

**Input:** Set soil potentiometer below 30%, water above 20%, and rain below 60%.

**Expected:** Blue LED turns ON, pump is `ON`, and the MQTT JSON contains `"pump":"ON"` and `DRY_SOIL`.

### Test Case 4: Rain Override

**Input:** Set rain potentiometer above 60% while soil is dry.

**Expected:** Pump remains OFF and the message contains `Rain detected - irrigation skipped`.

### Test Case 5: Low Water Protection

**Input:** Set water level below 20% and soil below 30%.

**Expected:** Pump remains OFF, red alert LED turns ON, and `LOW_WATER_TANK` is published.

### Test Case 6: Multiple Alerts

**Input:** Set temperature above 35 C and humidity below 30%.

**Expected:** Red alert LED turns ON and the JSON contains both alert names.

### Test Case 7: Communication Failure

**Input:** Stop the Python receiver or disconnect the network after the ESP32 is running.

**Expected:** ESP32 continues local threshold processing and attempts MQTT reconnection. The pump safety decision does not depend on the dashboard.

## 10. Required Screenshots

| Screenshot | What must be visible | File name |
|---|---|---|
| Enhanced circuit | ESP32, six sensors, LEDs, resistors, all wires | `da2_wokwi_circuit.png` |
| Firmware | Wi-Fi, MQTT topics, sensor acquisition, edge logic | `da2_firmware.png` |
| Wi-Fi connection | Serial Monitor shows `WiFi connected` | `da2_wifi_connected.png` |
| MQTT connection | Serial Monitor shows MQTT connected | `da2_mqtt_connected.png` |
| Published JSON | Serial Monitor shows `MQTT published` payload | `da2_mqtt_payload.png` |
| Dashboard connected | Dashboard shows MQTT CONNECTED and live gauges | `da2_dashboard_connected.png` |
| Dry soil | Blue LED ON and pump JSON status ON | `da2_dry_soil.png` |
| Rain override | Rain above threshold and pump OFF | `da2_rain_override.png` |
| Low water | Red LED ON and pump disabled | `da2_low_water.png` |
| Multiple alerts | Several alerts in Serial Monitor or dashboard | `da2_multiple_alerts.png` |
| Failure test | Reconnection message or dashboard waiting state | `da2_connection_failure.png` |

## 11. Screenshot Procedure

1. Open the Wokwi project and replace the sketch with the DA2 firmware.
2. Open the Serial Monitor.
3. Start the Python receiver with `python -m communication.mqtt_subscriber`.
4. Start the dashboard with `python main.py`.
5. Capture the circuit when all components and wires are visible.
6. Capture Wi-Fi and MQTT connection messages from the Serial Monitor.
7. Capture a complete `MQTT published` JSON message.
8. Open `http://localhost:8050` and wait until it shows `MQTT: CONNECTED`.
9. Adjust the Wokwi potentiometers for dry soil, rain, and low water tests.
10. For each test, capture the Serial Monitor and visible LED state together.
11. Stop the receiver to perform the communication-failure test, then capture the dashboard waiting state or ESP32 reconnection output.
12. Save screenshots in the repository `images/` folder using the names above.

On Windows, use `Win + Shift + S`, select the relevant Wokwi or dashboard area, and save the image with the required filename.

## 12. Results and Analysis

Record whether each message reached the broker, whether the Python receiver decoded the JSON, whether the dashboard updated, and whether the ESP32 actuator decision remained correct.

| Test | Expected result | Actual result | Status |
|---|---|---|---|
| MQTT connection | Broker connection succeeds | [Fill] | [PASS/FAIL] |
| Sensor publishing | JSON is received | [Fill] | [PASS/FAIL] |
| Dry soil | Pump ON | [Fill] | [PASS/FAIL] |
| Rain override | Pump OFF | [Fill] | [PASS/FAIL] |
| Low water | Pump disabled | [Fill] | [PASS/FAIL] |
| Communication failure | Local safety continues | [Fill] | [PASS/FAIL] |

## 13. Conclusion

The DA2 system extends the original agriculture CPS with real-time communication and monitoring. Sensor data is acquired by the ESP32, processed at the edge, published through MQTT, received by Python, and displayed through the dashboard. The actuator safety logic remains local, so irrigation is not dependent on the dashboard being online.

## 14. Future Improvements

- Use a private authenticated MQTT broker.
- Add TLS encryption.
- Add MQTT commands for a manual override.
- Store received data in a database.
- Add a mobile notification service.
- Add crop-specific thresholds and multiple field nodes.
