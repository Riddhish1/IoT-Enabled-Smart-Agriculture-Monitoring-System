/*
 * Digital Assignment 2: MQTT-enabled smart agriculture node.
 * The ESP32 reads sensors, makes irrigation decisions locally,
 * and publishes one JSON reading to the MQTT broker.
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

#define DEMO_MODE false

const int SOIL_MOISTURE_PIN = 34;
const int LDR_PIN = 35;
const int WATER_LEVEL_PIN = 32;
const int RAIN_SENSOR_PIN = 33;
const int DHT_PIN = 15;
const int PUMP_PIN = 26;
const int ALERT_LED_PIN = 27;

const float TEMP_HIGH_THRESHOLD = 35.0;
const float TEMP_LOW_THRESHOLD = 5.0;
const float HUMIDITY_LOW_THRESHOLD = 30.0;
const int SOIL_DRY_THRESHOLD = 30;
const int SOIL_WET_THRESHOLD = 70;
const int WATER_LEVEL_LOW = 20;
const int LIGHT_LOW_THRESHOLD = 20;
const int RAIN_THRESHOLD = 60;

const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASSWORD = "";
const char* MQTT_HOST = "broker.hivemq.com";
const int MQTT_PORT = 1883;
const char* SENSOR_TOPIC = "agrisense/field1/sensors";
const char* STATUS_TOPIC = "agrisense/field1/status";

DHT dht(DHT_PIN, DHT22);
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
int readingCount = 0;

int toPercent(int rawValue) {
  return map(rawValue, 0, 4095, 0, 100);
}

void connectWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  Serial.println();
  Serial.println(WiFi.status() == WL_CONNECTED ? "WiFi connected" : "WiFi unavailable");
}

void connectMqtt() {
  while (!mqttClient.connected()) {
    String clientId = "agrisense-esp32-" + String((uint32_t)ESP.getEfuseMac(), HEX);
    Serial.print("Connecting to MQTT...");
    if (mqttClient.connect(clientId.c_str())) {
      Serial.println("connected");
      mqttClient.publish(STATUS_TOPIC, "ESP32 online");
    } else {
      Serial.print("failed, state=");
      Serial.println(mqttClient.state());
      delay(3000);
    }
  }
}

String alertsJson(float temperature, float humidity, int soil, int light, int water) {
  String alerts = "[";
  bool hasAlert = false;
  if (temperature > TEMP_HIGH_THRESHOLD) { alerts += "\"HIGH_TEMPERATURE\""; hasAlert = true; }
  if (temperature < TEMP_LOW_THRESHOLD) { if (hasAlert) alerts += ","; alerts += "\"FROST_RISK\""; hasAlert = true; }
  if (humidity < HUMIDITY_LOW_THRESHOLD) { if (hasAlert) alerts += ","; alerts += "\"LOW_HUMIDITY\""; hasAlert = true; }
  if (water < WATER_LEVEL_LOW) { if (hasAlert) alerts += ","; alerts += "\"LOW_WATER_TANK\""; hasAlert = true; }
  if (light < LIGHT_LOW_THRESHOLD) { if (hasAlert) alerts += ","; alerts += "\"LOW_LIGHT\""; hasAlert = true; }
  if (soil < SOIL_DRY_THRESHOLD) { if (hasAlert) alerts += ","; alerts += "\"DRY_SOIL\""; }
  alerts += "]";
  return alerts;
}

void publishReading(int soil, float temperature, float humidity, int light,
                    int water, int rain, bool pumpOn, String pumpReason) {
  String payload = "{";
  payload += "\"reading_no\":" + String(readingCount) + ",";
  payload += "\"timestamp\":\"" + String(millis() / 1000) + "s\",";
  payload += "\"scenario\":\"Live Wokwi Sensors\",";
  payload += "\"soil_moisture\":" + String(soil) + ",";
  payload += "\"temperature\":" + String(temperature, 1) + ",";
  payload += "\"humidity\":" + String(humidity, 1) + ",";
  payload += "\"light_intensity\":" + String(light) + ",";
  payload += "\"water_level\":" + String(water) + ",";
  payload += "\"rain_level\":" + String(rain) + ",";
  payload += "\"pump\":\"" + String(pumpOn ? "ON" : "OFF") + "\",";
  payload += "\"pump_reason\":\"" + pumpReason + "\",";
  payload += "\"alerts\":" + alertsJson(temperature, humidity, soil, light, water);
  payload += "}";
  mqttClient.publish(SENSOR_TOPIC, payload.c_str());
  Serial.println("MQTT published: " + payload);
}

void setup() {
  Serial.begin(115200);
  pinMode(PUMP_PIN, OUTPUT);
  pinMode(ALERT_LED_PIN, OUTPUT);
  digitalWrite(PUMP_PIN, LOW);
  digitalWrite(ALERT_LED_PIN, LOW);
  dht.begin();
  mqttClient.setServer(MQTT_HOST, MQTT_PORT);
  connectWiFi();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) connectWiFi();
  if (!mqttClient.connected()) connectMqtt();
  mqttClient.loop();
  readingCount++;

  int soil = toPercent(analogRead(SOIL_MOISTURE_PIN));
  int light = toPercent(analogRead(LDR_PIN));
  int water = toPercent(analogRead(WATER_LEVEL_PIN));
  int rain = toPercent(analogRead(RAIN_SENSOR_PIN));
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("DHT22 read failed; skipping this message");
    delay(2000);
    return;
  }

  bool pumpOn = false;
  String pumpReason = "Soil moisture in acceptable range";
  if (rain > RAIN_THRESHOLD) {
    pumpReason = "Rain detected - irrigation skipped";
  } else if (water < WATER_LEVEL_LOW) {
    pumpReason = "Water tank critically low - pump disabled";
  } else if (soil < SOIL_DRY_THRESHOLD) {
    pumpOn = true;
    pumpReason = "Soil is dry - pump activated";
  } else if (soil >= SOIL_WET_THRESHOLD) {
    pumpReason = "Soil sufficiently moist - pump idle";
  }

  bool alertOn = temperature > TEMP_HIGH_THRESHOLD || temperature < TEMP_LOW_THRESHOLD
                 || humidity < HUMIDITY_LOW_THRESHOLD || water < WATER_LEVEL_LOW
                 || light < LIGHT_LOW_THRESHOLD || soil < SOIL_DRY_THRESHOLD;
  digitalWrite(PUMP_PIN, pumpOn ? HIGH : LOW);
  digitalWrite(ALERT_LED_PIN, alertOn ? HIGH : LOW);
  publishReading(soil, temperature, humidity, light, water, rain, pumpOn, pumpReason);
  delay(5000);
}
