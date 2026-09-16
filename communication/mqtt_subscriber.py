"""MQTT subscriber and in-memory state for the agriculture monitor."""

from __future__ import annotations

import json
import threading
from collections import deque
from datetime import datetime
from typing import Any

try:
    import paho.mqtt.client as mqtt
except ImportError:  # The dashboard can still import before dependencies are installed.
    mqtt = None

BROKER_HOST = "broker.hivemq.com"
BROKER_PORT = 1883
TOPIC_SENSOR_DATA = "agrisense/field1/sensors"
TOPIC_STATUS = "agrisense/field1/status"
TOPIC_ALERTS = "agrisense/field1/alerts"
TOPIC_PUMP = "agrisense/field1/pump"

MAX_HISTORY = 50
reading_lock = threading.Lock()

latest_reading: dict[str, Any] = {
    "reading_no": 0,
    "timestamp": "Not connected",
    "scenario": "Waiting for MQTT data",
    "soil": 0.0,
    "temp": 0.0,
    "humidity": 0.0,
    "light": 0.0,
    "water": 0.0,
    "rain": 0.0,
    "pump_on": False,
    "pump_reason": "No message received",
    "alerts": [],
    "mqtt_connected": False,
}

history: dict[str, deque] = {
    "timestamps": deque(maxlen=MAX_HISTORY),
    "soil": deque(maxlen=MAX_HISTORY),
    "temp": deque(maxlen=MAX_HISTORY),
    "humidity": deque(maxlen=MAX_HISTORY),
    "light": deque(maxlen=MAX_HISTORY),
    "water": deque(maxlen=MAX_HISTORY),
    "rain": deque(maxlen=MAX_HISTORY),
    "pump": deque(maxlen=MAX_HISTORY),
}

_mqtt_client = None


def _number(payload: dict[str, Any], key: str) -> float:
    value = payload.get(key, 0)
    return float(value)


def update_reading(payload: dict[str, Any]) -> None:
    """Validate and publish one received sensor payload to dashboard state."""
    timestamp = payload.get("timestamp") or datetime.now().strftime("%H:%M:%S")
    reading = {
        "reading_no": int(payload.get("reading_no", 0)),
        "timestamp": timestamp,
        "scenario": payload.get("scenario", "Live MQTT reading"),
        "soil": _number(payload, "soil_moisture"),
        "temp": _number(payload, "temperature"),
        "humidity": _number(payload, "humidity"),
        "light": _number(payload, "light_intensity"),
        "water": _number(payload, "water_level"),
        "rain": _number(payload, "rain_level"),
        "pump_on": payload.get("pump") == "ON",
        "pump_reason": payload.get("pump_reason", "Received from ESP32"),
        "alerts": list(payload.get("alerts", [])),
        "mqtt_connected": True,
    }

    with reading_lock:
        latest_reading.update(reading)
        history["timestamps"].append(timestamp)
        history["soil"].append(reading["soil"])
        history["temp"].append(reading["temp"])
        history["humidity"].append(reading["humidity"])
        history["light"].append(reading["light"])
        history["water"].append(reading["water"])
        history["rain"].append(reading["rain"])
        history["pump"].append(1 if reading["pump_on"] else 0)


def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        with reading_lock:
            latest_reading["mqtt_connected"] = True
        client.subscribe(TOPIC_SENSOR_DATA)
        client.subscribe(TOPIC_STATUS)
    else:
        with reading_lock:
            latest_reading["mqtt_connected"] = False


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties=None):
    with reading_lock:
        latest_reading["mqtt_connected"] = False


def on_message(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode("utf-8"))
        if message.topic == TOPIC_SENSOR_DATA:
            update_reading(payload)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError):
        return


def start_subscriber() -> None:
    """Start the MQTT network loop in a daemon thread."""
    global _mqtt_client
    if mqtt is None:
        return

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="agrisense-dashboard",
    )
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    try:
        client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
        _mqtt_client = client
        client.loop_start()
    except OSError:
        with reading_lock:
            latest_reading["mqtt_connected"] = False


def snapshot() -> tuple[dict[str, Any], dict[str, list[Any]]]:
    with reading_lock:
        return dict(latest_reading), {key: list(values) for key, values in history.items()}


if __name__ == "__main__":
    start_subscriber()
    print(f"Listening on {BROKER_HOST}:{BROKER_PORT} ({TOPIC_SENSOR_DATA})")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        pass
